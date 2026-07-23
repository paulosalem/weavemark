import { h, iconButton } from "./dom.js";

export function renderActionBar({ card, state = {}, onToggle, onNote, onShare, onUnderstand }) {
  return h("nav", { className: "action-bar", attrs: { "aria-label": `Actions for ${card.title}` } }, [
    iconButton("Like this card", "Like", () => onToggle("liked"), Boolean(state.liked)),
    iconButton("Save this card", "Save", () => onToggle("saved"), Boolean(state.saved)),
    iconButton("Request a revisit", "Revisit", () => onToggle("revisitRequested"), Boolean(state.revisitRequested)),
    h("button", {
      className: "icon-button",
      text: "Note",
      attrs: { type: "button", "aria-label": `Add or edit note for ${card.title}` },
      on: { click: onNote }
    }),
    h("button", {
      className: "icon-button",
      text: "Copy",
      attrs: { type: "button", "aria-label": `Copy link to ${card.title}` },
      on: { click: onShare }
    }),
    h("button", {
      className: state.understanding === "understood" ? "understand-button is-selected" : "understand-button",
      text: "Understood",
      attrs: {
        type: "button",
        "aria-label": `I understand ${card.title}`,
        "aria-pressed": state.understanding === "understood" ? "true" : "false"
      },
      on: { click: () => onUnderstand(state.understanding === "understood" ? null : "understood") }
    })
  ]);
}
