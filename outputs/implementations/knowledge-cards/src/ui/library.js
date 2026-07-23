import { h } from "./dom.js";

export function renderPackLibrary({
  packs,
  progressByPack = new Map(),
  preferences,
  repoWarning = null,
  onOpen,
  onPanel,
  onDismissOnboarding
}) {
  return h("main", { className: "library-view", attrs: { id: "app-main" } }, [
    h("section", { className: "hero-card" }, [
      h("p", { className: "eyebrow", text: "Knowledge Cards" }),
      h("h1", { text: "A calm one-card feed for cumulative learning." }),
      h("p", {
        className: "hero-copy",
        text: "Choose a coherent pack, read one concept at a time, keep notes locally, and stop without shame when you have learned enough for today."
      }),
      repoWarning ? h("p", { className: "status-message status-message--warning", text: repoWarning, attrs: { role: "status" } }) : null,
      h("div", { className: "hero-actions" }, [
        h("button", { className: "secondary-button", text: "Saved", attrs: { type: "button" }, on: { click: () => onPanel("saved") } }),
        h("button", { className: "secondary-button", text: "Notes", attrs: { type: "button" }, on: { click: () => onPanel("notes") } }),
        h("button", { className: "secondary-button", text: "History", attrs: { type: "button" }, on: { click: () => onPanel("history") } }),
        h("button", { className: "secondary-button", text: "Settings", attrs: { type: "button" }, on: { click: () => onPanel("settings") } }),
        h("button", { className: "secondary-button", text: "Import / Export", attrs: { type: "button" }, on: { click: () => onPanel("import-export") } })
      ])
    ]),
    !preferences.onboardingDismissed
      ? h("section", { className: "onboarding-card", attrs: { "aria-labelledby": "onboarding-title" } }, [
          h("div", {}, [
            h("p", { className: "eyebrow", text: "How this works" }),
            h("h2", { text: "Scroll with a purpose.", attrs: { id: "onboarding-title" } }),
            h("p", { text: "Each pack is a reviewed concept map. Move one card at a time, keep private notes, and stop after a short learning session." })
          ]),
          h("ul", {}, [
            h("li", { text: "Your progress and notes stay in this browser." }),
            h("li", { text: "Likes shape your library, not the learning order." }),
            h("li", { text: "A stopping point appears after 10 cards or 10 minutes." })
          ]),
          h("button", {
            className: "primary-button",
            text: "Got it",
            attrs: { type: "button" },
            on: { click: onDismissOnboarding }
          })
        ])
      : null,
    h("section", { className: "pack-grid", attrs: { "aria-label": "Available topic packs" } }, packs.map((pack) => {
      const progress = progressByPack.get(pack.id);
      const completed = progress?.completed_count ?? 0;
      const percent = Math.round((completed / pack.card_count) * 100);
      return h("article", { className: "pack-card", attrs: { style: `--pack-accent: ${pack.accent_color}` } }, [
        h("p", { className: "eyebrow", text: `${pack.level} - ${pack.card_count} cards` }),
        h("h2", { text: pack.title }),
        h("p", { text: pack.description }),
        h("p", { className: "small-copy", text: `${pack.audience}. ${pack.purpose}` }),
        h("div", { className: "progress-track", attrs: { "aria-label": `${percent}% complete` } }, [
          h("span", { attrs: { style: `inline-size: ${percent}%` } })
        ]),
        h("button", {
          className: "primary-button",
          text: completed > 0 ? "Resume pack" : "Start pack",
          attrs: { type: "button" },
          on: { click: () => onOpen(pack.id, progress?.active_card_id ?? null) }
        })
      ]);
    }))
  ]);
}
