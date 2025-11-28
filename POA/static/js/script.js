document.addEventListener("DOMContentLoaded", function () {
  console.log("JS carregado — sidebar funcionando!");

  const sidebar = document.getElementById("sidebar");
  const toggle = document.getElementById("sidebar-toggle");

  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
  });
});
