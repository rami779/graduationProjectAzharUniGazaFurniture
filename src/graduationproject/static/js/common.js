(function () {
  "use strict";
  /* Links: from Django (window.NESTRO_CONFIG) or the .html files */
  var NC = window.NESTRO_CONFIG || {};
  function page(key, file) { return (NC.links && NC.links[key]) || file; }
  var ROUTES = {
    login: page("login", "login.html"),
    register: page("register", "register.html"),
    forgotPassword: page("forgotPassword", "forgot-password.html"),
    accountSuspended: page("accountSuspended", "account-suspended.html"),
    outsideFlow: page("home", "home.html"),
    afterLogin: {              /* after login → Home (header follows the role) */
      customer: page("home", "home.html"),
      designer: page("home", "home.html")
    }
  };

  var SUPPORT_EMAIL = "NestroHome.Help@gmail.com";

  var storage = {
    get: function (key) {
      try {
        var raw = window.localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    },
    set: function (key, value) {
      try {
        window.localStorage.setItem(key, JSON.stringify(value));
      } catch (e) {  }
    },
    remove: function (key) {
      try {
        window.localStorage.removeItem(key);
      } catch (e) {  }
    }
  };

  var DESKTOP_MIN = 1024;
  var STAGE_HEIGHTS = { login: 787, register: 888 }; // Figma frame heights of the auth screens

  function fitStage() {
    var stage = document.querySelector("[data-stage]");
    if (!stage) return;
    var vw = document.documentElement.clientWidth;
    var vh = window.innerHeight;
    var scale = 1;

    if (vw >= DESKTOP_MIN) {
      var frameHeight = STAGE_HEIGHTS[stage.getAttribute("data-stage")];
      if (frameHeight) {
        scale = Math.min(vw / 1440, Math.max(vh / frameHeight, 0.6));
      } else {
        scale = vw / 1440;
      }
    }
    document.documentElement.style.setProperty("--stage-scale", scale.toFixed(4));
  }

  window.addEventListener("resize", fitStage);
  document.addEventListener("DOMContentLoaded", fitStage);
  fitStage();

  /*  Toasts*/
  var openToast = null;

  function hideToast() {
    if (openToast) {
      openToast.hidden = true;
      openToast = null;
    }
  }

  function showToast(id) {
    hideToast();
    var toast = document.getElementById(id);
    if (!toast) return;
    toast.hidden = false;
    openToast = toast;
  }

  document.addEventListener("click", function (event) {
    if (openToast && !openToast.contains(event.target) && !event.target.closest("[data-opens-toast]")) {
      hideToast();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") hideToast();
  });

  /*  Mock authentication  */
  var SESSION_KEY = "nestro.mockSession";
  var NETWORK_DELAY_MS = 900;

  var MOCK_USERS = [
    
    { email: "sarah345@gmail.com", password: "sarah$account123", role: "customer", name: "Sarah", status: "active" },
    
    { email: "designer@nestro.com", password: "Designer$123", role: "designer", name: "Designer", status: "active" },
    { email: "suspended@nestro.com", password: "Suspended$123", role: "customer", name: "Suspended user", status: "suspended",
      suspensionReason: "Your account was suspended after repeated violations of the Nestro terms of use." }
  ];

  var SIMULATE_FAILURE_EMAIL = "error@nestro.com";
  var REGISTERED_KEY = "nestro.mockRegisteredUsers";

  function allUsers() {
    return MOCK_USERS.concat(storage.get(REGISTERED_KEY) || []);
  }

  function delay(ms) {
    return new Promise(function (resolve) { setTimeout(resolve, ms); });
  }

  var MockAuth = {
    login: function (email, password) {
      var normalized = String(email).trim().toLowerCase();
      return delay(NETWORK_DELAY_MS).then(function () {
        if (normalized === SIMULATE_FAILURE_EMAIL) {
          return { ok: false, reason: "server" };
        }
        var user = allUsers().find(function (u) { return u.email === normalized; });
        if (!user || user.password !== password) {
          return { ok: false, reason: "credentials" };
        }
        if (user.status === "suspended") {
          storage.set("nestro.suspension", { email: user.email, reason: user.suspensionReason });
          return { ok: false, reason: "suspended" };
        }
        var session = { email: user.email, name: user.name, role: user.role, loggedInAt: new Date().toISOString(), mock: true };
        storage.set(SESSION_KEY, session);
        /* tell the shared header who is logged in (layout.js reads "nestroRole") */
        try { window.localStorage.setItem("nestroRole", user.role); } catch (e) {  }
        return { ok: true, user: session };
      });
    },
    register: function (data) {
      var normalized = String(data.email).trim().toLowerCase();
      return delay(NETWORK_DELAY_MS).then(function () {
        if (normalized === SIMULATE_FAILURE_EMAIL) {
          return { ok: false, reason: "server" };
        }
        if (allUsers().some(function (u) { return u.email === normalized; })) {
          return { ok: false, reason: "exists" };
        }
        var registered = storage.get(REGISTERED_KEY) || [];
        registered.push({ email: normalized, password: data.password, role: "customer", name: data.name.trim(), status: "active" });
        storage.set(REGISTERED_KEY, registered);
        return { ok: true, email: normalized };
      });
    },
    signUpWithGoogle: function () {
      // Google sign-up is not connected in this front-end build.
      return delay(400).then(function () { return { ok: false, reason: "google-unavailable" }; });
    },
    getRegisteredUsers: function () {
      return storage.get(REGISTERED_KEY) || [];
    },
    clearRegisteredUsers: function () {
      storage.remove(REGISTERED_KEY);
    },
    loginWithGoogle: function () {
      // Google sign-in is not connected in this front-end build.
      return delay(400).then(function () { return { ok: false, reason: "google-unavailable" }; });
    },
    getSession: function () {
      return storage.get(SESSION_KEY);
    },
    logout: function () {
      storage.remove(SESSION_KEY);
      try { window.localStorage.removeItem("nestroRole"); } catch (e) {  }
    },
    getSuspension: function () {
      return storage.get("nestro.suspension");
    },
    demoAccounts: MOCK_USERS.map(function (u) {
      return { email: u.email, password: u.password, role: u.role, status: u.status };
    }),
    simulateFailureEmail: SIMULATE_FAILURE_EMAIL
  };

  /*  Validation helpers  */
  var EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function isValidEmail(value) {
    return EMAIL_PATTERN.test(String(value).trim());
  }

  /* Support mail links  */
  function supportMailto(subject) {
    return "mailto:" + SUPPORT_EMAIL + "?subject=" + encodeURIComponent(subject);
  }

  window.Nestro = {
    ROUTES: ROUTES,
    SUPPORT_EMAIL: SUPPORT_EMAIL,
    MockAuth: MockAuth,
    isValidEmail: isValidEmail,
    showToast: showToast,
    hideToast: hideToast,
    supportMailto: supportMailto,
    fitStage: fitStage
  };
})();
