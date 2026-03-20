// thoda style fix karne js

// 5 sec baad flash hatado
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach((el) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });

  // active nav item dikhane ke liye
  // jinja ka fallback
  const currentPath = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach((link) => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });

  // file ka naam label mein dalo
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach((input) => {
    input.addEventListener("change", () => {
      const label = input.nextElementSibling;
      if (label && label.classList.contains("form-text")) {
        const name = input.files[0]?.name || "";
        if (name) {
          label.textContent = "Selected: " + name;
        }
      }
    });
  });
});
