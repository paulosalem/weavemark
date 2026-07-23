(() => {
  if (window.location.protocol !== "file:") return;

  const localDocsUrl = new URL("http://127.0.0.1:4173/docs/");
  document.querySelectorAll("[data-live-demo]").forEach((element) => {
    for (const attribute of ["href", "data-href"]) {
      const value = element.getAttribute(attribute);
      if (value?.startsWith("../outputs/implementations/")) {
        element.setAttribute(attribute, new URL(value, localDocsUrl).href);
      }
    }
  });
})();
