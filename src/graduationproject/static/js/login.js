(function () {
  "use strict";

  var N = window.Nestro;
  var F = N.AuthForm;
  var form = document.getElementById("login-form");
  var emailInput = document.getElementById("email");
  var passwordInput = document.getElementById("password");
  var emailField = document.getElementById("field-email");
  var passwordField = document.getElementById("field-password");
  var submitButton = document.getElementById("login-submit");
  var googleButton = document.getElementById("google-login");

  var MESSAGES = {
    emailEmpty: "Please enter your email address",
    emailInvalid: "Please enter a valid email address",
    passwordEmpty: "Please enter a password",
    passwordWrong: "This password is incorrect"
  };

  var isSubmitting = false;
  var prefill = new URLSearchParams(window.location.search).get("email");
  if (prefill) {
    emailInput.value = prefill;
  }

  F.clearOnInput(emailField);
  F.clearOnInput(passwordField);
  F.initPasswordToggle(document.getElementById("toggle-password"), passwordInput);

  function validate() {
    var email = emailInput.value.trim();
    var password = passwordInput.value;
    var firstInvalid = null;

    if (!email) {
      F.setError(emailField, MESSAGES.emailEmpty);
      firstInvalid = emailInput;
    }

    if (!password) {
      F.setError(passwordField, MESSAGES.passwordEmpty);
      firstInvalid = firstInvalid || passwordInput;
    } else {
      F.clearError(passwordField);
    }

    if (firstInvalid) firstInvalid.focus();
    return !firstInvalid;
  }

  function setLoading(loading) {
    isSubmitting = loading;
    F.setBusy(form, submitButton, loading);
    googleButton.disabled = loading;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (isSubmitting) return;
    N.hideToast();
    if (!validate()) return;

    setLoading(true);
    N.MockAuth.login(emailInput.value, passwordInput.value).then(function (result) {
      if (result.ok) {
        /* Save who logged in (customer / designer) */
        try {
          localStorage.setItem("nestroRole", result.user.role);
        } catch (e) { /* storage blocked */ }

        /* came from a page that needs login (login.html?next=become-designer.html)?
           go back there; otherwise go Home */
        var next = new URLSearchParams(window.location.search).get("next") || "";
        /* only pages of this site: "about.html" or "/about/" (never another website) */
        var home = (window.NESTRO_CONFIG && NESTRO_CONFIG.links && NESTRO_CONFIG.links.home) || "home.html";
        var safeNext = /^[\w-]+\.html$/.test(next) || /^\/(?!\/)[\w\-\/]*$/.test(next) ? next : home;
        window.location.href = safeNext + "?role=" + encodeURIComponent(result.user.role);
        return;
      }

      setLoading(false);

      if (result.reason === "credentials") {
        F.setError(passwordField, MESSAGES.passwordWrong);
        passwordInput.focus();
        passwordInput.select();
      } else if (result.reason === "suspended") {
        window.location.href = N.ROUTES.accountSuspended;
      } else {
        N.showToast("toast-login-failure");
      }
    }).catch(function () {
      setLoading(false);
      N.showToast("toast-login-failure");
    });
  });

  googleButton.setAttribute("data-opens-toast", "");
  submitButton.setAttribute("data-opens-toast", "");
  googleButton.addEventListener("click", function () {
    if (isSubmitting) return;
    googleButton.disabled = true;
    N.MockAuth.loginWithGoogle().then(function () {
      googleButton.disabled = false;
      N.showToast("toast-google-error");
    });
  });
})();