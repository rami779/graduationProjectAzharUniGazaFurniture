(function () {
  "use strict";

  var N = window.Nestro;
  var F = N.AuthForm;
  var form = document.getElementById("register-form");
  var nameInput = document.getElementById("name");
  var emailInput = document.getElementById("email");
  var passwordInput = document.getElementById("password");
  var termsInput = document.getElementById("terms");
  var nameField = document.getElementById("field-name");
  var emailField = document.getElementById("field-email");
  var passwordField = document.getElementById("field-password");
  var termsField = document.getElementById("field-terms");
  var submitButton = document.getElementById("register-submit");
  var googleButton = document.getElementById("google-signup");

  var MIN_NAME_LETTERS = 4;      // "more than 3 letters"
  var MIN_PASSWORD_LENGTH = 8;   // "At least 8 characters"

  var MESSAGES = {
    nameEmpty: "Please enter your full name",
    nameInvalid: "Please enter valid name characters",
    nameShort: "Please enter more than 3 letters",
    emailEmpty: "Please enter your email address",
    emailInvalid: "Please enter a valid email address",
    emailExists: "This email address is existed",
    passwordEmpty: "Please enter a password",
    passwordShort: "Please enter a valid password.",
    termsRequired: "Please accept the terms of the platform to continue"
  };

  var NAME_PATTERN = /^[\p{L}\p{M}\s'.-]+$/u;

  var isSubmitting = false;

  F.clearOnInput(nameField);
  F.clearOnInput(emailField);
  F.clearOnInput(passwordField);
  F.clearOnInput(termsField, "change");
  F.initPasswordToggle(document.getElementById("toggle-password"), passwordInput);

  function nameError(value) {
    if (!value) return MESSAGES.nameEmpty;
    if (!NAME_PATTERN.test(value)) return MESSAGES.nameInvalid;
    var letters = value.replace(/[^\p{L}]/gu, "").length;
    if (letters < MIN_NAME_LETTERS) return MESSAGES.nameShort;
    return null;
  }

  function emailError(value) {
    if (!value) return MESSAGES.emailEmpty;
    if (!N.isValidEmail(value)) return MESSAGES.emailInvalid;
    return null;
  }

  function passwordError(value) {
    if (!value) return MESSAGES.passwordEmpty;
    if (value.length < MIN_PASSWORD_LENGTH) return MESSAGES.passwordShort;
    return null;
  }

  function validate() {
    var checks = [
      [nameField, nameInput, nameError(nameInput.value.trim())],
      [emailField, emailInput, emailError(emailInput.value.trim())],
      [passwordField, passwordInput, passwordError(passwordInput.value)],
      [termsField, termsInput, termsInput.checked ? null : MESSAGES.termsRequired]
    ];
    var firstInvalid = null;

    checks.forEach(function (check) {
      if (check[2]) {
        F.setError(check[0], check[2]);
        firstInvalid = firstInvalid || check[1];
      } else {
        F.clearError(check[0]);
      }
    });

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
    N.MockAuth.register({
      name: nameInput.value,
      email: emailInput.value,
      password: passwordInput.value
    }).then(function (result) {
      if (result.ok) {
        
        window.location.href = N.ROUTES.login + "?email=" + encodeURIComponent(result.email);
        return;
      }

      setLoading(false);

      if (result.reason === "exists") {
        F.setError(emailField, MESSAGES.emailExists);
        emailInput.focus();
      } else {
        N.showToast("toast-register-failure");
      }
    }).catch(function () {
      setLoading(false);
      N.showToast("toast-register-failure");
    });
  });

  /* Google sign-up is not connected*/
  googleButton.setAttribute("data-opens-toast", "");
  submitButton.setAttribute("data-opens-toast", "");
  googleButton.addEventListener("click", function () {
    if (isSubmitting) return;
    googleButton.disabled = true;
    N.MockAuth.signUpWithGoogle().then(function () {
      googleButton.disabled = false;
      N.showToast("toast-google-signup-error");
    });
  });
})();
