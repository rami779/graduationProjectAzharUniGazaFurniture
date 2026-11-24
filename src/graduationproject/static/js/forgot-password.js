(function () {
  "use strict";
  var N = window.Nestro;
  var href = N.supportMailto("Password reset request");
  document.getElementById("support-email").href = href;
  document.getElementById("contact-support").href = href;
})();
