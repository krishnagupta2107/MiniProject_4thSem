// main.js – small UI enhancements

// auto-dismiss flash alerts after 5 seconds
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach((el) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });

  // highlight nav link based on current page
  // (already handled by Jinja, but this is a fallback)
  const currentPath = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach((link) => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });

  // file input - show filename in label
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
