// static/js/script.js
document.addEventListener("DOMContentLoaded", () => {
  const toggleThemeBtn = document.getElementById("toggle-theme");
  if (toggleThemeBtn) {
    toggleThemeBtn.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
      if (document.body.classList.contains("dark-mode")) {
        toggleThemeBtn.textContent = "Modalità Chiara";
      } else {
        toggleThemeBtn.textContent = "Modalità Notte";
      }
    });
  }
});
