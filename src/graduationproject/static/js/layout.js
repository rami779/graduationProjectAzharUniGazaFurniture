/* Nestro Home — layout.js (one file)

   Works in two ways:
   1. Now (plain HTML files): uses the .html links below.
   2. In Django: base.html writes window.NESTRO_CONFIG before this file,
      and the links / user role / cart number / static folder come from it.
      Nothing in this file needs to change. */

(function () {
  "use strict";

  /* Info from Django (empty when the pages are plain HTML files) */
  var CFG = window.NESTRO_CONFIG || {};
  var STATIC = CFG.staticUrl || "../";   /* "../" now, "/static/" in Django */

  var LINKS = {
    home: {                       
      visitor: "home.html",
      customer: "home.html",
      designer: "home.html"
    },
    shop: "shop.html",
    consultation: "consultation.html",
    designers: "designers.html",
    login: "login.html",
    register: "register.html",
    cart: "cart.html",
    contact: "contact.html",
    about: "about.html",
    becomeDesigner: "become-designer.html",
    profile: "profile.html",
    orders: "orders.html",
    consultations: "my-consultations.html",
    addresses: "addresses.html",
    messages: "messages.html",
    workspace: "design-workspace.html",
    earnings: "earnings.html",
    logout: "home.html"
  };

  /* Django links replace the .html links (only the ones it sends) */
  if (CFG.links) {
    Object.keys(CFG.links).forEach(function (key) {
      if (!CFG.links[key]) return;
      if (key === "home") LINKS.home = { visitor: CFG.links.home, customer: CFG.links.home, designer: CFG.links.home };
      else LINKS[key] = CFG.links[key];
    });
  }

  /* Badge numbers
     cart: counted from the cart saved by shop.js ("nestroCart")
     messages: replace with the real value from your backend later */
  var CART_KEY = "nestroCart";
  var serverCart = typeof CFG.cartCount === "number" ? CFG.cartCount : null; /* from Django */
  function cartCount() {
    if (serverCart !== null) return serverCart;
    try {
      var cart = JSON.parse(localStorage.getItem(CART_KEY)) || [];
      return cart.reduce(function (n, item) { return n + (Number(item.qty) || 1); }, 0);
    } catch (e) { return 0; }
  }
  var COUNTS = {
    cart: cartCount(),
    messages: typeof CFG.messagesCount === "number" ? CFG.messagesCount : 2
  };

  /*  2. ICONS (inline SVG, white on the dark header)  */
  var ICONS = {
    sofa:
      '<svg viewBox="0 0 31 26" width="31" height="26" fill="none" aria-hidden="true">' +
        '<path d="M5 11V4.5A3.5 3.5 0 0 1 8.5 1h14A3.5 3.5 0 0 1 26 4.5V11" stroke="currentColor" stroke-width="2.4"/>' +
        '<path d="M2.5 11h4.5v5h17v-5h4.5v9.5h-26z" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>' +
        '<path d="M5 20.5V25M26 20.5V25" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>' +
      "</svg>",
    search:
      '<svg viewBox="0 0 36 36" width="36" height="36" fill="none" aria-hidden="true">' +
        '<circle cx="15" cy="15" r="12" stroke="currentColor" stroke-width="2.2"/>' +
        '<path d="M24 24l10 10" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>' +
      "</svg>",
    cart:
      '<svg viewBox="0 0 34 30" width="34" height="30" fill="currentColor" aria-hidden="true">' +
        '<path d="M0 2.2C0 1 .9 0 2 0h3.2c1 0 1.8.7 2 1.6L7.7 4H32c1.3 0 2.2 1.2 1.9 2.4l-2.6 10.4c-.2.9-1 1.6-2 1.6H10.6l.6 2.6H29c1.1 0 2 .9 2 2s-.9 2-2 2H9.6c-1 0-1.8-.7-2-1.6L3.6 4.4H2c-1.1 0-2-.9-2-2.2z"/>' +
        '<circle cx="12" cy="27" r="3"/><circle cx="27" cy="27" r="3"/>' +
      "</svg>",
    user:
      '<svg viewBox="0 0 40 40" width="40" height="40" aria-hidden="true">' +
        '<circle cx="20" cy="20" r="20" fill="currentColor"/>' +
        '<circle cx="20" cy="15" r="6.5" fill="var(--icon-cut, #4a3b2e)"/>' +
        '<path d="M8 32.5c2.4-5.2 7-7.5 12-7.5s9.6 2.3 12 7.5A16.9 16.9 0 0 1 20 37a16.9 16.9 0 0 1-12-4.5z" fill="var(--icon-cut, #4a3b2e)"/>' +
      "</svg>",
       messages:
      '<svg viewBox="0 0 24 26" width="26" height="28" fill="currentColor" aria-hidden="true">' +
        '<path d="M12 0a1.6 1.6 0 0 0-1.6 1.6v.9A8 8 0 0 0 4 10.4v5.4L1.6 19.4A1.2 1.2 0 0 0 2.6 21h18.8a1.2 1.2 0 0 0 1-1.6L20 15.8v-5.4a8 8 0 0 0-6.4-7.9v-.9A1.6 1.6 0 0 0 12 0z"/>' +
        '<path d="M8.6 22.4h6.8a3.4 3.4 0 0 1-6.8 0z"/>' +
      "</svg>",
    arrowRight:
      '<svg viewBox="0 0 20 20" width="20" height="20" fill="none" aria-hidden="true">' +
        '<path d="M3 10h14M11 4l6 6-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>' +
      "</svg>"
  };

  /* Account-menu icons (profile dropdow) */
  var MENU_ICONS = {
    profile:
      '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">' +
        '<circle cx="12" cy="7.5" r="4"/><path d="M4 21c.8-4.2 4-6.5 8-6.5s7.2 2.3 8 6.5" stroke-linecap="round"/></svg>',
    orders:
      '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true">' +
        '<path d="M12 2.5l9 4.5v10l-9 4.5-9-4.5V7z"/><path d="M3 7l9 4.5L21 7M12 11.5v10M7.5 4.8l9 4.5v3.7"/></svg>',
    consultations:
      '<svg viewBox="0 0 26 24" width="26" height="24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true">' +
        '<path d="M2 2h14v10H7l-5 4z"/><path d="M19 7h5v11h-3v4l-4.5-4H9v-3"/>' +
        '<path d="M6 6.5h6M6 9h4" stroke-linecap="round"/></svg>',
    addresses:
      '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">' +
        '<path d="M12 21.5s-7-6.6-7-12a7 7 0 0 1 14 0c0 5.4-7 12-7 12z" stroke-linejoin="round"/><circle cx="12" cy="9.5" r="2.6"/></svg>',
    become:
      '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
        '<path d="M3 21L15.5 8.5l2 2L5 23z"/><path d="M15 3v3M13.5 4.5h3M20 8v2.5M18.8 9.2h2.5M9 4v2M8 5h2"/></svg>',
    logout:
      '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
        '<path d="M14 4V2.5H3v19h11V20"/><path d="M9 12h12M17 8l4 4-4 4"/></svg>'
  };

  /*  SOCIAL (footer)  */
  var SOCIAL = [
    { label: "Facebook", href: "#",
      icon: '<svg viewBox="0 0 32 32" width="32" height="32" fill="none" aria-hidden="true"><rect x="1" y="1" width="30" height="30" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M20.5 31V19h3.6l.5-4h-4.1v-2.6c0-1.2.4-2 2.1-2h2.2V6.9c-.4 0-1.7-.2-3.2-.2-3.2 0-5.4 1.9-5.4 5.5V15H13v4h3.2v12" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>' },
    { label: "Instagram", href: "#",
      icon: '<svg viewBox="0 0 32 32" width="31" height="31" fill="none" aria-hidden="true"><rect x="2" y="2" width="28" height="28" rx="8" stroke="currentColor" stroke-width="2.6"/><circle cx="16" cy="16" r="6.5" stroke="currentColor" stroke-width="2.6"/><circle cx="24" cy="8" r="1.8" fill="currentColor"/></svg>' },
    { label: "X", href: "#",
      icon: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" aria-hidden="true"><path d="M2 2h6.2l13.8 20h-6.2zM3.5 22l7.8-8.8M20.5 2l-7.3 8.2" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>' },
    { label: "WhatsApp", href: "#",
      icon: '<svg viewBox="0 0 28 28" width="27" height="27" fill="none" aria-hidden="true"><path d="M14 2.2A11.8 11.8 0 0 0 3.9 20l-1.6 5.8 6-1.6A11.8 11.8 0 1 0 14 2.2z" stroke="currentColor" stroke-width="2.1" stroke-linejoin="round"/><path d="M10.2 8.3c-.4 0-.9.1-1.2.6-.4.5-1.2 1.4-1.2 3.3s1.3 3.8 1.5 4c.2.3 2.6 4.1 6.4 5.6 3.2 1.2 3.8 1 4.5.9.7-.1 2.2-.9 2.5-1.8.3-.9.3-1.6.2-1.8-.1-.2-.3-.3-.7-.5l-2.4-1.2c-.3-.1-.6-.2-.8.2l-1.1 1.4c-.2.2-.4.3-.8.1-.4-.2-1.5-.6-2.9-1.8-1.1-1-1.8-2.1-2-2.5-.2-.4 0-.6.2-.8l.6-.7c.2-.2.3-.4.4-.7.1-.3 0-.5 0-.7l-1.1-2.6c-.3-.7-.6-.7-.8-.7z" fill="currentColor"/></svg>' },
    { label: "LinkedIn", href: "#",
      icon: '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true"><rect x="1" y="8" width="4.6" height="14"/><circle cx="3.3" cy="3.6" r="2.6"/><path d="M8.6 8h4.4v2c.7-1.3 2.4-2.4 4.7-2.4 4.6 0 5.3 3 5.3 6.8V22h-4.6v-6.8c0-1.7 0-3.8-2.3-3.8s-2.7 1.8-2.7 3.7V22H8.6z"/></svg>' }
  ];

  /* - Small helpers */
  function homeLink(type) {
    return LINKS.home[type] || LINKS.home.visitor;
  }

  function navLink(key, label, active, type) {
    var href = key === "home" ? homeLink(type) : LINKS[key];
    var isActive = key === active;
    return '<a class="site-nav__link' + (isActive ? " is-active" : "") + '" href="' + href + '"' +
      (isActive ? ' aria-current="page"' : "") + ">" + label + "</a>";
  }

  function badge(n, mod) {
    return n ? '<span class="icon-badge' + (mod ? " icon-badge--" + mod : "") + '">' + n + "</span>" : "";
  }

  function logo(type, cls) {
    return '<a class="' + cls + '" href="' + homeLink(type) + '" aria-label="Nestro Home — home page">' +
      ICONS.sofa + '<span class="brand">Nestro Home</span></a>';
  }

  /*  Header parts  */
  function searchBlock() {
    return '<div class="header-search">' +
      '<button class="icon-btn header-search__toggle" type="button" aria-label="Search" aria-expanded="false" aria-controls="header-search-bar">' +
        ICONS.search +
      "</button>" +
      '<form class="header-search__bar" id="header-search-bar" role="search" action="' + LINKS.shop + '" hidden>' +
        '<label class="visually-hidden" for="header-search-input">Search products</label>' +
        '<input class="header-search__input" id="header-search-input" name="search" type="search" placeholder="Search furniture, rooms, designers…" autocomplete="off">' +
        '<button class="header-search__submit" type="submit">Search</button>' +
      "</form>" +
    "</div>";
  }

  function cartLink() {
    var n = cartCount();
    return '<a class="icon-btn header-cart" href="' + LINKS.cart + '" aria-label="Cart, ' + n + ' items">' +
      ICONS.cart +
      '<span class="icon-badge" data-cart-count' + (n ? "" : " hidden") + ">" + (n > 99 ? "99+" : n) + "</span>" +
    "</a>";
  }

  /* Update the cart number on the page (after Add to Cart, or from another tab) */
  function refreshCart(count) {
    if (typeof count !== "number") count = cartCount();
    else if (serverCart !== null) serverCart = count;
    COUNTS.cart = count;
    document.querySelectorAll("[data-cart-count]").forEach(function (el) {
      el.textContent = count > 99 ? "99+" : count;
      el.hidden = count === 0;
      var link = el.closest(".header-cart");
      if (link) link.setAttribute("aria-label", "Cart, " + count + " items");
    });
  }
  document.addEventListener("nestro:cart-updated", function (e) {
    refreshCart(e.detail && typeof e.detail.count === "number" ? e.detail.count : undefined);
  });
  window.addEventListener("storage", function (e) { if (e.key === CART_KEY) refreshCart(); });
  window.addEventListener("pageshow", function () { refreshCart(); }); // back button

  function messagesLink() {
    return '<a class="icon-btn header-messages" href="' + LINKS.messages + '" aria-label="Notifications, ' + COUNTS.messages + ' unread">' +
      ICONS.messages + badge(COUNTS.messages, "red") + "</a>";
  }

  /* Account menu  */
  function accountMenu(type) {
    var items = [
      { key: "profile", label: "My Profile", href: LINKS.profile, icon: MENU_ICONS.profile },
      { key: "orders", label: "My Orders", href: LINKS.orders, icon: MENU_ICONS.orders },
      { key: "consultations", label: "My Consultations", href: LINKS.consultations, icon: MENU_ICONS.consultations },
      { key: "addresses", label: "My Addresses", href: LINKS.addresses, icon: MENU_ICONS.addresses }
    ];
    if (type === "customer") {
      items.push({ key: "become", label: "Become a designer", href: LINKS.becomeDesigner, icon: MENU_ICONS.become, small: true });
    }
    items.push({ key: "logout", label: "Log out", href: LINKS.logout, icon: MENU_ICONS.logout, danger: true });

    return '<div class="account">' +
      '<button class="icon-btn account__toggle" type="button" aria-label="My account" aria-haspopup="true" aria-expanded="false" aria-controls="account-menu">' +
        ICONS.user +
      "</button>" +
      '<ul class="account__menu" id="account-menu" hidden>' +
        items.map(function (it) {
          /* Django: log out must be a POST form with the CSRF token */
          if (it.key === "logout" && CFG.csrfToken) {
            return '<li><form method="post" action="' + it.href + '" style="margin:0">' +
              '<input type="hidden" name="csrfmiddlewaretoken" value="' + CFG.csrfToken + '">' +
              '<button type="submit" class="account__item account__item--danger" data-logout ' +
                'style="width:100%;background:none;border:0;font:inherit;text-align:left;cursor:pointer">' +
                it.icon + "<span>" + it.label + "</span></button></form></li>";
          }
          return '<li><a class="account__item' + (it.danger ? " account__item--danger" : "") +
            (it.small ? " account__item--small" : "") + '" href="' + it.href + '"' +
            (it.key === "logout" ? ' data-logout' : "") + ">" +
            it.icon + "<span>" + it.label + "</span></a></li>";
        }).join("") +
      "</ul>" +
    "</div>";
  }

  /*  Header */
  function headerActions(type, opts) {
    var search = opts.search ? searchBlock() : "";

    if (type === "customer") {
      return search + accountMenu("customer") + cartLink();
    }
    if (type === "designer") {
      return messagesLink() +
        '<a class="pill-btn pill-btn--workspace" href="' + LINKS.workspace + '">Design Workspace</a>' +
        search + accountMenu("designer") + cartLink();
    }
    /* visitor */
    return search +
      '<a class="pill-btn pill-btn--login" href="' + LINKS.login + '">Login</a>' +
      '<a class="pill-btn pill-btn--signup" href="' + LINKS.register + '">Sign up</a>' +
      cartLink();
  }

  function renderHeader(type, opts) {
    return '<header class="site-header site-header--' + type + (opts.overlay ? " site-header--overlay" : "") + '">' +
      '<div class="site-header__inner">' +
        '<div class="site-header__brand">' + logo(type, "site-header__logo") + "</div>" +
        '<nav class="site-nav" aria-label="Main">' +
          navLink("home", "Home", opts.active, type) +
          navLink("shop", "Shop", opts.active, type) +
          navLink("consultation", "Get Consultation", opts.active, type) +
          navLink("designers", "Designers", opts.active, type) +
        "</nav>" +
        '<div class="site-header__actions">' + headerActions(type, opts) + "</div>" +
      "</div>" +
    "</header>";
  }

  /*  Footer: same design, the link lists change per user  */
  var FOOTER_LINKS = {
    visitor: [
     [["Home", "home"], ["Shop", LINKS.shop], ["Get Consultation", LINKS.consultation], ["Designers", LINKS.designers], ["Become a Designer", LINKS.login + "?next=" + LINKS.becomeDesigner]],
      [["Register/Login", LINKS.login], ["My Cart", LINKS.cart], ["Contact Us", LINKS.contact], ["About Us", LINKS.about]]
    ],
    customer: [
      [["Home", "home"], ["Shop", LINKS.shop], ["Get Consultation", LINKS.consultation], ["Designers", LINKS.designers], ["Become a Designer", LINKS.becomeDesigner]],
      [["My Orders", LINKS.orders], ["My Cart", LINKS.cart], ["Contact Us", LINKS.contact], ["About Us", LINKS.about]]
    ],
    designer: [
      [["Home", "home"], ["Shop", LINKS.shop], ["Get Consultation", LINKS.consultation], ["Designers", LINKS.designers], ["Earnings and Payouts", LINKS.earnings]],
      [["My Cart", LINKS.cart], ["My Orders", LINKS.orders], ["Design Workspace", LINKS.workspace], ["Contact Us", LINKS.contact], ["About Us", LINKS.about]]
    ]
  };

  function renderFooter(type) {
    var cols = FOOTER_LINKS[type] || FOOTER_LINKS.visitor;
    return '<footer class="site-footer">' +
      '<div class="site-footer__inner">' +
        logo(type, "site-footer__logo") +
        '<nav class="site-footer__links" aria-label="Footer">' +
          cols.map(function (col) {
            return '<ul class="site-footer__col">' +
              col.map(function (l) {
                var href = l[1] === "home" ? homeLink(type) : l[1];
                return '<li><a href="' + href + '">' + l[0] + "</a></li>";
              }).join("") +
            "</ul>";
          }).join("") +
        "</nav>" +
        '<p class="site-footer__copy">Copyright © 2026 Nestro.com. All rights reserved.</p>' +
        '<div class="site-footer__social">' +
          '<p class="site-footer__social-title">Follow Our Social Media Pages</p>' +
          '<ul class="site-footer__icons">' +
            SOCIAL.map(function (s) {
              return '<li><a href="' + s.href + '" aria-label="' + s.label + '">' + s.icon + "</a></li>";
            }).join("") +
          "</ul>" +
          '<img class="site-footer__img" src="' + STATIC + 'assets/images/home/footer-chairs.jpg" width="384" height="288" alt="">' +
        "</div>" +
      "</div>" +
    "</footer>";
  }

  
  function setupAccountMenu(root) {
    var toggle = root.querySelector(".account__toggle");
    var menu = root.querySelector(".account__menu");
    if (!toggle || !menu) return;

    function open() {
      menu.hidden = false;
      toggle.setAttribute("aria-expanded", "true");
    }
    function close() {
      menu.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      if (menu.hidden) open(); else close();
    });
    document.addEventListener("click", function (e) {
      if (!menu.hidden && !root.querySelector(".account").contains(e.target)) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !menu.hidden) {
        close();
        toggle.focus();
      }
    });
  }

  function setupSearch(root) {
    var toggle = root.querySelector(".header-search__toggle");
    var bar = root.querySelector(".header-search__bar");
    if (!toggle || !bar) return;
    var input = bar.querySelector("input");

    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      var willOpen = bar.hidden;
      bar.hidden = !willOpen;
      toggle.setAttribute("aria-expanded", String(willOpen));
      if (willOpen) input.focus();
    });
    document.addEventListener("click", function (e) {
      if (!bar.hidden && !root.querySelector(".header-search").contains(e.target)) {
        bar.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !bar.hidden) {
        bar.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  var ROLES = ["visitor", "customer", "designer"];
  var STORAGE_KEY = "nestroRole";

  function cleanRole(r) {
    r = String(r || "").toLowerCase();
    return ROLES.indexOf(r) > -1 ? r : "";
  }

  function saveRole(r) {
    try {
      if (r === "visitor") localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, r);
    } catch (e) { /* storage blocked: role lasts for this page only */ }
  }

  function getRole() {
    /* Django tells who is logged in */
    if (cleanRole(CFG.role)) return cleanRole(CFG.role);
    var fromUrl = cleanRole(new URLSearchParams(location.search).get("role"));
    if (fromUrl) {
      saveRole(fromUrl);
      return fromUrl;
    }
    try {
      return cleanRole(localStorage.getItem(STORAGE_KEY)) || "visitor";
    } catch (e) {
      return "visitor";
    }
  }

  var ROLE = getRole();
  document.documentElement.setAttribute("data-role", ROLE);

   function applyRoleVisibility() {
    document.querySelectorAll("[data-hide-for]").forEach(function (el) {
      el.hidden = el.getAttribute("data-hide-for").split(/\s+/).indexOf(ROLE) > -1;
    });
    document.querySelectorAll("[data-only-for]").forEach(function (el) {
      el.hidden = el.getAttribute("data-only-for").split(/\s+/).indexOf(ROLE) === -1;
    });

    document.querySelectorAll("a[data-needs-login]").forEach(function (a) {
      if (!a.dataset.target) a.dataset.target = a.getAttribute("href");
      a.setAttribute("href", ROLE === "visitor"
        ? LINKS.login + "?next=" + encodeURIComponent(a.dataset.target)
        : a.dataset.target);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyRoleVisibility);
  } else {
    applyRoleVisibility();
  }

  /* Log out → back to visitor (also ends the login session of common.js) */
  document.addEventListener("click", function (e) {
    if (e.target.closest && e.target.closest("[data-logout]")) {
      saveRole("visitor");
      try { localStorage.removeItem("nestro.mockSession"); } catch (err) { /* ignore */ }
    }
  });

  /* type="visitor|customer|designer" forces a type; no type = current user */
  function typeOf(el) {
    return cleanRole(el.getAttribute("type")) || ROLE;
  }

  if (!customElements.get("site-header")) {
    customElements.define("site-header", class extends HTMLElement {
      connectedCallback() {
        if (this._done) return;
        this._done = true;
        this.innerHTML = renderHeader(typeOf(this), {
          active: this.getAttribute("active") || "",
          overlay: this.hasAttribute("overlay"),
          search: this.hasAttribute("search")
        });
        setupAccountMenu(this);
        setupSearch(this);
      }
    });
  }

  if (!customElements.get("site-footer")) {
    customElements.define("site-footer", class extends HTMLElement {
      connectedCallback() {
        if (this._done) return;
        this._done = true;
        this.innerHTML = renderFooter(typeOf(this));
      }
    });
  }

  /* Other scripts can use the same arrow icon / links */
  window.NestroLayout = {
    LINKS: LINKS,
    ICONS: ICONS,
    homeLink: homeLink,
    role: ROLE,
    /* NestroLayout.refreshCart() → re-reads the cart and updates the number */
    refreshCart: refreshCart,
    cartCount: cartCount,
    /* call after a successful login, e.g. NestroLayout.setRole("designer") */
    setRole: function (r) {
      r = cleanRole(r);
      if (r) saveRole(r);
    }
  };
})();

(function () {
  "use strict";

  var MAX_RESULTS = 6;
  var DELAY = 250;
  var CFG = window.NESTRO_CONFIG || {};
  var LINKS = CFG.links || {};
  var SHOP = LINKS.shop || "shop.html";
  var PRODUCT = LINKS.product || "product.html";

  /*  styles for the results list  */
  var css =
    ".header-search__bar{width:440px}" +
    ".header-search__results{max-height:420px;margin:8px 0 0;padding:0;list-style:none;overflow-y:auto;flex-basis:100%}" +
    ".header-search__bar{flex-wrap:wrap}" +
    ".header-search__result{display:flex;align-items:center;gap:12px;padding:8px;border-radius:8px;color:#000;text-decoration:none}" +
    ".header-search__result img{flex:none;width:48px;height:48px;border-radius:6px;object-fit:cover}" +
    ".header-search__results .is-active .header-search__result,.header-search__result:hover{background:#f4e6db}" +
    ".header-search__text{display:flex;flex-direction:column;min-width:0}" +
    ".header-search__title{color:#604025;font:500 15px/22px Poppins,sans-serif}" +
    ".header-search__title mark{background:none;color:inherit;font-weight:700}" +
    ".header-search__sub{color:#5e5e5e;font:13px/19px Poppins,sans-serif}" +
    ".header-search__empty{padding:14px 8px;color:#5e5e5e;font:14px Poppins,sans-serif}" +
    ".header-search__all a{display:block;margin-top:4px;padding:10px 8px 4px;border-top:1px solid #eee;color:#604025;font:500 14px Poppins,sans-serif}" +
    ".header-search__all a:hover{text-decoration:underline}";
  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  /*  helpers */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* lower case + Arabic letter forms unified */
  function norm(s) {
    return (" " + String(s || "").toLowerCase() + " ")
      .replace(/[\u064B-\u0652\u0640]/g, "")
      .replace(/[\u0623\u0625\u0622]/g, "\u0627").replace(/\u0629/g, "\u0647").replace(/\u0649/g, "\u064A")
      .replace(/\s\u0627\u0644/g, " ")
      .replace(/&/g, "and").replace(/\s+/g, " ").trim();
  }

  function highlight(text, q) {
    var safe = esc(text);
    var w = esc(String(q).trim().split(/\s+/)[0].toLowerCase());
    var i = w ? safe.toLowerCase().indexOf(w) : -1;
    if (i < 0) return safe;
    return safe.slice(0, i) + "<mark>" + safe.slice(i, i + w.length) + "</mark>" + safe.slice(i + w.length);
  }

  function resultLink(r) {
    if (r.href) return r.href;
    if (r.type === "category") return SHOP + "?room=" + encodeURIComponent(r.slug || r.id);
    return productLink(r.id);
  }

  /* "product.html?id=5" now, or Django "/product/{id}/" → "/product/5/" */
  function productLink(id) {
    return PRODUCT.indexOf("{id}") > -1
      ? PRODUCT.replace("{id}", encodeURIComponent(id))
      : PRODUCT + "?id=" + encodeURIComponent(id);
  }

  /* Without api.js: search the cards that are on the page */
  var ARABIC = {
    chair: "كرسي كراسي", bed: "سرير تخت نوم", sofa: "كنب كنبه", light: "اضاءه اناره ثريا",
    rug: "سجاد سجاده", outdoor: "حديقه خارجي", living: "معيشه صالون", dining: "سفره طعام",
    kitchen: "مطبخ", office: "مكتب", bedroom: "غرفه نوم"
  };

  function arabicWords(text) {
    var t = norm(text), extra = "";
    Object.keys(ARABIC).forEach(function (k) { if (t.indexOf(k) > -1) extra += " " + ARABIC[k]; });
    return extra;
  }

  function pageItems() {
    var items = [];
    document.querySelectorAll(".product-card").forEach(function (card) {
      var title = (card.querySelector(".product-card__title") || {}).textContent || "";
      var cat = (card.querySelector(".product-card__category") || {}).textContent || "";
      var price = (card.querySelector(".product-card__price ins") || {}).textContent || "";
      var img = card.querySelector("img");
      var btn = card.querySelector(".product-card__btn");
      items.push({ title: title, subtitle: cat + (price ? " · " + price : ""),
                   image: img ? img.getAttribute("src") : "", href: btn ? btn.getAttribute("href") : "",
                   words: title + " " + cat + arabicWords(title + " " + cat) });
    });
    document.querySelectorAll(".room-card").forEach(function (card) {
      var name = (card.querySelector(".room-card__name") || {}).textContent || "";
      var img = card.querySelector("img");
      items.push({ title: name, subtitle: "Room category", image: img ? img.getAttribute("src") : "",
                   href: card.getAttribute("href"), words: name + " room غرفه" + arabicWords(name) });
    });
    return items;
  }

  function searchPage(q) {
    var words = norm(q).split(" ").filter(Boolean);
    var found = pageItems().filter(function (it) {
      var hay = norm(it.words + " " + it.subtitle);
      return words.every(function (w) { return hay.indexOf(w) > -1; });
    });
    found.sort(function (a, b) {
      var ia = norm(a.title).indexOf(words[0]), ib = norm(b.title).indexOf(words[0]);
      return (ia === 0 ? 0 : ia > 0 ? 1 : 2) - (ib === 0 ? 0 : ib > 0 ? 1 : 2);
    });
    return Promise.resolve(found.slice(0, MAX_RESULTS));
  }

  function doSearch(q, signal) {
    if (window.NestroAPI && NestroAPI.search) return NestroAPI.search(q, MAX_RESULTS, signal);
    return searchPage(q);
  }

  /*  attach to the header search box  */
  function setup(bar) {
    if (bar.dataset.liveSearch) return;           /* only once */
    bar.dataset.liveSearch = "1";

    var input = bar.querySelector("input");
    if (!input) return;

    var list = document.createElement("ul");
    list.className = "header-search__results";
    list.id = "header-search-results";
    list.setAttribute("role", "listbox");
    list.hidden = true;
    bar.appendChild(list);

    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-expanded", "false");
    input.setAttribute("aria-controls", list.id);

    var matches = [], active = -1, timer = null, controller = null, last = "";

    function hide() {
      list.hidden = true;
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
      active = -1;
    }

    function show(q, results) {
      matches = results;
      active = -1;
      if (!results.length) {
        list.innerHTML = '<li class="header-search__empty">No results for “' + esc(q) + "”</li>";
      } else {
        list.innerHTML = results.map(function (r, i) {
          return '<li role="option" id="search-opt-' + i + '" aria-selected="false">' +
            '<a class="header-search__result" href="' + esc(resultLink(r)) + '" tabindex="-1">' +
              (r.image ? '<img src="' + esc(r.image) + '" alt="">' : "") +
              '<span class="header-search__text">' +
                '<span class="header-search__title">' + highlight(r.title, q) + "</span>" +
                (r.subtitle ? '<span class="header-search__sub">' + esc(r.subtitle) + "</span>" : "") +
              "</span></a></li>";
        }).join("") +
        '<li class="header-search__all"><a href="' + SHOP + "?q=" + encodeURIComponent(q) +
          '" tabindex="-1">See all results for “' + esc(q) + "”</a></li>";
      }
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
    }

    function run(q) {
      if (controller) controller.abort();
      controller = window.AbortController ? new AbortController() : null;
      last = q;
      doSearch(q, controller && controller.signal).then(function (res) {
        if (q === last) show(q, Array.isArray(res) ? res : []);
      }).catch(function (err) {
        if (err && err.name === "AbortError") return;
        if (q === last) show(q, []);
      });
    }

    function move(step) {
      if (!matches.length) return;
      active = (active + step + matches.length) % matches.length;
      list.querySelectorAll('[role="option"]').forEach(function (li, i) {
        li.setAttribute("aria-selected", String(i === active));
        li.classList.toggle("is-active", i === active);
      });
      input.setAttribute("aria-activedescendant", "search-opt-" + active);
    }

    input.addEventListener("input", function () {
      var q = input.value.trim();
      clearTimeout(timer);
      if (!q) { hide(); return; }
      timer = setTimeout(function () { run(q); }, DELAY);
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter" && active > -1 && matches[active]) {
        e.preventDefault();
        location.href = resultLink(matches[active]);
      }
    });

  
    bar.addEventListener("submit", function (e) {
      e.preventDefault();
      var q = input.value.trim();
      if (!q) return;
      clearTimeout(timer);
      location.href = SHOP + "?q=" + encodeURIComponent(q);
    }, true);
  }

  /* the header is drawn by layout.js → wait until it is there */
  function init() {
    document.querySelectorAll(".header-search__bar").forEach(setup);
  }
  init();
  new MutationObserver(init).observe(document.documentElement, { childList: true, subtree: true });
})();