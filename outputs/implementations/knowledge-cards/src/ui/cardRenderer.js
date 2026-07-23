import { h } from "./dom.js";

export function renderKnowledgeCard({ card, sourceRefs = [], state = {}, note = null, revisitReason = null }) {
  const sourcesById = new Map(sourceRefs.map((source) => [source.id, source]));
  const sourceList = h("ul", { className: "source-list" }, card.source_refs.map((id) => {
    const source = sourcesById.get(id);
    return h("li", {}, [
      h("a", {
        text: source?.title ?? id,
        attrs: {
          href: source?.url ?? "#",
          target: "_blank",
          rel: "noopener noreferrer"
        }
      }),
      h("span", { text: source ? ` — ${source.publisher}. ${source.claim_scope}` : " — source unavailable." })
    ]);
  }));
  const reviewPrompt = card.review_prompts[0];
  return h("article", {
    className: "knowledge-card",
    attrs: {
      "aria-labelledby": `${card.id}-title`,
      tabindex: "-1"
    },
    dataset: { cardId: card.id }
  }, [
    h("div", { className: "card-topline" }, [
      h("span", { className: "category-pill", text: labelForCategory(card.category) }),
      h("span", { className: "difficulty-pill", text: `Difficulty ${card.difficulty}/5` })
    ]),
    revisitReason ? h("p", { className: "revisit-reason", text: revisitReason }) : null,
    h("h2", { text: card.title, attrs: { id: `${card.id}-title` } }),
    h("div", { className: "core-idea" }, card.core_idea.map((paragraph) => h("p", { text: paragraph }))),
    h("section", { className: "example-box", attrs: { "aria-label": "Example" } }, [
      h("h3", { text: "Example" }),
      h("p", { text: card.example })
    ]),
    h("p", { className: "takeaway", text: card.key_takeaway }),
    h("details", { className: "detail-stack" }, [
      h("summary", { text: "Connections, review, and sources" }),
      h("div", { className: "connection-grid" }, [
        h("section", {}, [
          h("h3", { text: "Connections" }),
          card.connections.length
            ? h("ul", {}, card.connections.map((connection) => h("li", { text: connection.label })))
            : h("p", { text: "This card is a foundation for later ideas." })
        ]),
        h("section", {}, [
          h("h3", { text: "Deliberate revisit" }),
          h("p", { text: reviewPrompt.prompt }),
          h("p", { className: "hint", text: `Hint: ${reviewPrompt.answer_hint}` })
        ])
      ]),
      h("section", {}, [
        h("h3", { text: "Boundary and sources" }),
        h("p", { className: "boundary-note", text: card.boundary_note }),
        sourceList
      ])
    ]),
    note?.body ? h("p", { className: "note-preview", text: `Your note: ${note.body}` }) : null,
    state.saved ? h("span", { className: "saved-badge", text: "Saved locally" }) : null
  ]);
}

function labelForCategory(category) {
  return category.split("-").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}
