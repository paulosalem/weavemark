import { h } from "./dom.js";

export function renderRecoveryState({ title, message, actionLabel = "Try again", onAction }) {
  return h("main", { className: "recovery-view", attrs: { id: "app-main", role: "alert" } }, [
    h("p", { className: "eyebrow", text: "Recovery" }),
    h("h1", { text: title }),
    h("p", { text: message }),
    h("button", { className: "primary-button", text: actionLabel, attrs: { type: "button" }, on: { click: onAction } })
  ]);
}
