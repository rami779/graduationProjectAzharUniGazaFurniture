(function () {
  "use strict";

  function setError(field, message) {
    var input = field.querySelector(".field__input");
    var error = field.querySelector(".field__error");
    error.querySelector(".field__error-text").textContent = message;
    error.hidden = false;
    field.classList.add("field--invalid");
    if (input) input.setAttribute("aria-invalid", "true");
  }

  function clearError(field) {
    var input = field.querySelector(".field__input");
    var error = field.querySelector(".field__error");
    error.hidden = true;
    error.querySelector(".field__error-text").textContent = "";
    field.classList.remove("field--invalid");
    if (input) input.removeAttribute("aria-invalid");
  }

  function clearOnInput(field, eventName) {
    var input = field.querySelector("input");
    input.addEventListener(eventName || "input", function () { clearError(field); });
  }

  /* Eye button */
  function initPasswordToggle(button, input) {
    button.addEventListener("click", function () {
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      button.setAttribute("aria-pressed", String(show));
      button.setAttribute("aria-label", show ? "Hide password" : "Show password");
      input.focus();
    });
  }

  function setBusy(form, submitButton, busy) {
    submitButton.setAttribute("aria-busy", String(busy));
    form.querySelectorAll("button, input").forEach(function (el) {
      if (el.type === "checkbox" || el.tagName === "BUTTON") {
        el.disabled = busy;
      } else {
        el.readOnly = busy;
      }
    });
  }

  window.Nestro.AuthForm = {
    setError: setError,
    clearError: clearError,
    clearOnInput: clearOnInput,
    initPasswordToggle: initPasswordToggle,
    setBusy: setBusy
  };
})();
