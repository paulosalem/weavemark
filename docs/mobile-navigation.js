(() => {
  const mobileQuery = window.matchMedia("(max-width: 920px)");
  const disclosures = [];
  let sequence = 0;

  const normalizedText = (element) =>
    element?.textContent?.replace(/\s+/g, " ").trim() || "";

  const activeLink = (container) =>
    container.querySelector('a[aria-current="page"], a.active') ||
    container.querySelector("a");

  const wrapDirectLinks = (container, modifier) => {
    const existing = container.querySelector(`:scope > .${modifier}`);
    if (existing) return existing;
    const panel = document.createElement("div");
    panel.className = `mobile-nav-panel ${modifier}`;
    container.querySelectorAll(":scope > a").forEach((link) => panel.append(link));
    container.append(panel);
    return panel;
  };

  const close = (item, { restoreFocus = false } = {}) => {
    item.container.removeAttribute("data-mobile-open");
    item.button.setAttribute("aria-expanded", "false");
    item.button.setAttribute("aria-label", `Open ${item.label.toLowerCase()}`);
    if (restoreFocus) item.button.focus();
  };

  const closeOthers = (current) => {
    disclosures.forEach((item) => {
      if (item !== current) close(item);
    });
  };

  const enhance = (container, options) => {
    if (!container || container.dataset.mobileNavigationReady === "true") return;
    container.dataset.mobileNavigationReady = "true";

    const panel = options.panel(container);
    if (!panel) return;
    const panelId = panel.id || `mobile-navigation-panel-${++sequence}`;
    panel.id = panelId;

    const button = document.createElement("button");
    button.type = "button";
    button.className = `mobile-nav-toggle mobile-nav-toggle--${options.kind}`;
    button.setAttribute("aria-controls", panelId);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-label", `Open ${options.label.toLowerCase()}`);
    button.innerHTML = `
      <span class="mobile-nav-toggle-copy">
        <strong>${options.label}</strong>
        <small></small>
      </span>
      <span class="mobile-nav-toggle-icon" aria-hidden="true">
        <i></i><i></i><i></i>
      </span>
    `;

    options.insert(container, button);
    const subtitle = button.querySelector("small");
    const updateSubtitle = () => {
      subtitle.textContent = normalizedText(activeLink(panel)) || options.fallback;
    };
    updateSubtitle();

    const item = { button, container, label: options.label, panel };
    disclosures.push(item);

    button.addEventListener("click", () => {
      const opening = !container.hasAttribute("data-mobile-open");
      closeOthers(item);
      if (opening) {
        container.setAttribute("data-mobile-open", "");
        button.setAttribute("aria-expanded", "true");
        button.setAttribute("aria-label", `Close ${options.label.toLowerCase()}`);
      } else {
        close(item);
      }
    });

    panel.addEventListener("click", (event) => {
      if (event.target.closest("a")) close(item);
    });

    new MutationObserver(updateSubtitle).observe(panel, {
      attributeFilter: ["aria-current", "class"],
      attributes: true,
      subtree: true,
    });
  };

  enhance(document.querySelector(".site-nav"), {
    fallback: "Site pages",
    insert: (container, button) =>
      container.querySelector(".site-nav-inner")?.insertBefore(
        button,
        container.querySelector(".nav-links"),
      ),
    kind: "site",
    label: "Menu",
    panel: (container) => container.querySelector(".nav-links"),
  });

  enhance(document.querySelector(".tutorial-nav"), {
    fallback: "Tutorial track",
    insert: (container, button) => container.prepend(button),
    kind: "tutorials",
    label: "Tutorials",
    panel: (container) =>
      wrapDirectLinks(container, "mobile-nav-panel--tutorials"),
  });

  enhance(document.querySelector(".sidebar"), {
    fallback: "Page sections",
    insert: (container, button) => container.prepend(button),
    kind: "sections",
    label: "On this page",
    panel: (container) =>
      wrapDirectLinks(container, "mobile-nav-panel--sections"),
  });

  document.documentElement.classList.add("mobile-nav-enhanced");

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const open = disclosures.find((item) =>
      item.container.hasAttribute("data-mobile-open"),
    );
    if (open) close(open, { restoreFocus: true });
  });

  document.addEventListener("click", (event) => {
    disclosures.forEach((item) => {
      if (
        item.container.hasAttribute("data-mobile-open") &&
        !item.container.contains(event.target)
      ) {
        close(item);
      }
    });
  });

  mobileQuery.addEventListener("change", (event) => {
    if (!event.matches) disclosures.forEach((item) => close(item));
  });
})();
