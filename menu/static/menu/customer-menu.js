const categoryLinks = Array.from(document.querySelectorAll(".category-nav a"));
const categorySections = Array.from(document.querySelectorAll(".category-section"));

if ("IntersectionObserver" in window && categoryLinks.length && categorySections.length) {
    const linkById = new Map(
        categoryLinks.map((link) => [link.getAttribute("href").replace("#", ""), link])
    );

    const observer = new IntersectionObserver(
        (entries) => {
            const visible = entries
                .filter((entry) => entry.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

            if (!visible) {
                return;
            }

            categoryLinks.forEach((link) => link.classList.remove("active"));
            const activeLink = linkById.get(visible.target.id);
            if (activeLink) {
                activeLink.classList.add("active");
            }
        },
        {
            rootMargin: "-120px 0px -55% 0px",
            threshold: [0.2, 0.45, 0.7],
        }
    );

    categorySections.forEach((section) => observer.observe(section));
}
