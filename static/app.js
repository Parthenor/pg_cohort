// Small client-side enhancement for the PG Cohort demo.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"]');
      if (button && button.dataset.loading !== "true") {
        button.dataset.loading = "true";
        button.style.opacity = "0.8";
      }
    });
  });
});
