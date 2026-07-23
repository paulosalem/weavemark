import { h } from "./dom.js";

export function renderNoteEditor({ card, draft = "", note = "", onDraft, onSave, onClose }) {
  const textarea = h("textarea", {
    className: "note-textarea",
    text: draft || note || "",
    attrs: {
      rows: "8",
      maxlength: "4000",
      "aria-label": `Note for ${card.title}`
    },
    on: { input: (event) => onDraft(event.currentTarget.value) }
  });
  return h("section", { className: "note-sheet", attrs: { role: "dialog", "aria-modal": "true", "aria-labelledby": "note-sheet-title" } }, [
    h("div", { className: "sheet-handle", attrs: { "aria-hidden": "true" } }),
    h("h2", { text: "Local note", attrs: { id: "note-sheet-title" } }),
    h("p", { className: "small-copy", text: card.title }),
    textarea,
    h("div", { className: "sheet-actions" }, [
      h("button", { className: "secondary-button", text: "Close", attrs: { type: "button" }, on: { click: onClose } }),
      h("button", {
        className: "primary-button",
        text: "Save note",
        attrs: { type: "button" },
        on: { click: () => onSave(textarea.value) }
      })
    ])
  ]);
}
