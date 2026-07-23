export function h(tag, options = {}, children = []) {
  const node = document.createElement(tag);
  const {
    className,
    text,
    attrs = {},
    dataset = {},
    on = {},
    hidden = false
  } = options;
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  if (hidden) node.hidden = true;
  for (const [key, value] of Object.entries(attrs)) {
    if (value === false || value == null) continue;
    if (value === true) node.setAttribute(key, "");
    else node.setAttribute(key, String(value));
  }
  for (const [key, value] of Object.entries(dataset)) node.dataset[key] = String(value);
  for (const [event, handler] of Object.entries(on)) node.addEventListener(event, handler);
  for (const child of Array.isArray(children) ? children : [children]) {
    if (child == null) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

export function replaceChildren(node, children) {
  node.replaceChildren(...children.filter(Boolean));
}

export function iconButton(label, text, onClick, selected = false) {
  return h("button", {
    className: selected ? "icon-button is-selected" : "icon-button",
    text,
    attrs: {
      type: "button",
      "aria-label": label,
      "aria-pressed": selected ? "true" : "false"
    },
    on: { click: onClick }
  });
}

export function statusMessage(message, tone = "neutral") {
  return h("p", {
    className: `status-message status-message--${tone}`,
    text: message,
    attrs: { role: tone === "error" ? "alert" : "status" }
  });
}

export function fieldLabel(text, control) {
  return h("label", { className: "field-label" }, [h("span", { text }), control]);
}
