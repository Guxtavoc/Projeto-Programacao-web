document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ DOM carregado - JS puro funcionando!");

  // Atualizar data e hora
  function updateDateTime() {
    const now = new Date();
    const options = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    };

    const datetimeElement = document.getElementById("datetime");
    if (datetimeElement) {
      datetimeElement.textContent = now.toLocaleDateString("pt-BR", options);
    }
  }

  // Alternar barra lateral - SEM ALERTS
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebar = document.getElementById("sidebar");
  const content = document.querySelector(".content");

  if (sidebarToggle && sidebar && content) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("collapsed");

      if (sidebar.classList.contains("collapsed")) {
        content.style.marginLeft = "60px";
      } else {
        content.style.marginLeft = "0";
      }
    });
  }

  // Menu items
  const menuItems = document.querySelectorAll(".menu-item");
  menuItems.forEach((item) => {
    item.addEventListener("click", function () {
      menuItems.forEach((i) => i.classList.remove("active"));
      this.classList.add("active");
    });
  });

  // Iniciar
  updateDateTime();
  setInterval(updateDateTime, 60000);
});
