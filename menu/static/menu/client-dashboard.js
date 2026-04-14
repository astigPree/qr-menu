const menuToggle = document.querySelector(".mobile-menu-toggle");
const closeButtons = document.querySelectorAll("[data-close-client-sidebar]");

function setClientSidebar(open) {
    document.body.classList.toggle("client-sidebar-open", open);
    if (menuToggle) {
        menuToggle.setAttribute("aria-expanded", String(open));
    }
}

if (menuToggle) {
    menuToggle.addEventListener("click", () => {
        setClientSidebar(!document.body.classList.contains("client-sidebar-open"));
    });
}

closeButtons.forEach((button) => {
    button.addEventListener("click", () => setClientSidebar(false));
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        setClientSidebar(false);
    }
});
