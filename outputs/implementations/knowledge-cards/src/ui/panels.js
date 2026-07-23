import { fieldLabel, h, statusMessage } from "./dom.js";

export function renderPanel({ panel, data, handlers }) {
  const title = panelTitle(panel);
  const body = panelBody(panel, data, handlers);
  return h("main", { className: "panel-view", attrs: { id: "app-main" } }, [
    h("header", { className: "panel-header" }, [
      h("button", { className: "ghost-button", text: "Back", attrs: { type: "button" }, on: { click: handlers.onBack } }),
      h("div", {}, [
        h("p", { className: "eyebrow", text: "Knowledge Cards" }),
        h("h1", { text: title })
      ])
    ]),
    body
  ]);
}

function panelBody(panel, data, handlers) {
  if (panel === "settings") return renderSettings(data.preferences, handlers);
  if (panel === "import-export") return renderImportExport(data.importPreview, handlers);
  if (panel === "notes") return renderList("Notes", data.notes, "body", handlers);
  if (panel === "saved") return renderList("Saved cards", data.savedCards, "cardTitle", handlers);
  if (panel === "history") return renderList("History", data.history, "label", handlers);
  return h("section", { className: "empty-state" }, [
    h("h2", { text: "Help and privacy" }),
    h("p", { text: "Knowledge Cards is a static app. Packs are bundled content; notes, saves, progress, and preferences stay in this browser's IndexedDB." }),
    h("p", { text: "There are no accounts, analytics profiles, ads, remote sync, notification prompts, or runtime LLM calls." })
  ]);
}

function renderSettings(preferences, handlers) {
  const textSize = h("select", {
    attrs: { name: "textSize" },
    on: { change: (event) => handlers.onPreference({ textSize: event.currentTarget.value }) }
  }, ["compact", "regular", "large"].map((value) => h("option", {
    text: value,
    attrs: { value, selected: preferences.textSize === value }
  })));
  const orderMode = h("select", {
    attrs: { name: "orderedMode" },
    on: { change: (event) => handlers.onPreference({ orderedMode: event.currentTarget.value }) }
  }, ["adaptive", "ordered", "shuffled"].map((value) => h("option", {
    text: value,
    attrs: { value, selected: preferences.orderedMode === value }
  })));
  return h("section", { className: "settings-card" }, [
    h("h2", { text: "Reading preferences" }),
    fieldLabel("Text size", textSize),
    fieldLabel("Session order", orderMode),
    fieldLabel("Cards before a stopping point", h("input", {
      attrs: { type: "number", min: "1", max: "50", value: preferences.sessionCardLimit },
      on: { change: (event) => handlers.onPreference({
        sessionCardLimit: clampNumber(event.currentTarget.value, 1, 50)
      }) }
    })),
    fieldLabel("Minutes before a stopping point", h("input", {
      attrs: { type: "number", min: "1", max: "60", value: preferences.sessionMinuteLimit },
      on: { change: (event) => handlers.onPreference({
        sessionMinuteLimit: clampNumber(event.currentTarget.value, 1, 60)
      }) }
    })),
    fieldLabel("Reduce motion", h("input", {
      attrs: { type: "checkbox", checked: preferences.reducedMotion },
      on: { change: (event) => handlers.onPreference({ reducedMotion: event.currentTarget.checked }) }
    })),
    h("button", {
      className: "danger-button",
      text: "Reset onboarding explanation",
      attrs: { type: "button" },
      on: { click: () => handlers.onPreference({ onboardingDismissed: false }) }
    })
  ]);
}

function renderImportExport(importPreview, handlers) {
  return h("section", { className: "settings-card" }, [
    h("h2", { text: "Import and export local state" }),
    h("p", { text: "Exports contain user-owned local state only. Bundled pack content is not duplicated." }),
    h("button", { className: "primary-button", text: "Download export", attrs: { type: "button" }, on: { click: handlers.onExport } }),
    fieldLabel("Import JSON", h("input", {
      attrs: { type: "file", accept: "application/json" },
      on: { change: handlers.onImportFile }
    })),
    importPreview
      ? h("section", { className: "import-preview" }, [
          h("h3", { text: importPreview.valid ? "Import preview" : "Import rejected" }),
          importPreview.valid
            ? h("p", { text: `${importPreview.conflicts.length} conflicts detected. Merge keeps existing compatible records unless IDs match.` })
            : statusMessage(importPreview.errors.join(" "), "error"),
          importPreview.valid
            ? h("button", { className: "primary-button", text: "Merge import", attrs: { type: "button" }, on: { click: handlers.onApplyImport } })
            : null
        ])
      : null
  ]);
}

function renderList(title, items, field, handlers) {
  return h("section", { className: "settings-card" }, [
    h("h2", { text: title }),
    items.length === 0
      ? h("p", { text: "Nothing here yet." })
      : h("ul", { className: "plain-list" }, items.map((item) => h("li", {}, [
          h("span", { text: item[field] ?? item.cardId ?? item.id }),
          item.packId && item.cardId
            ? h("button", {
                className: "ghost-button",
                text: "Open card",
                attrs: { type: "button" },
                on: { click: () => handlers.onOpenCard(item.packId, item.cardId) }
              })
            : null
        ])))
  ]);
}

function clampNumber(value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, Number(value) || minimum));
}

function panelTitle(panel) {
  return ({
    settings: "Settings",
    "import-export": "Import / Export",
    notes: "Notes",
    saved: "Saved cards",
    history: "History",
    help: "Help"
  })[panel] ?? "Help";
}
