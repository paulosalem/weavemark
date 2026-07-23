import { renderActionBar } from "./actionBar.js";
import { renderKnowledgeCard } from "./cardRenderer.js";
import { h } from "./dom.js";

let cleanupPageNavigation = () => {};
let lastActiveCardKey = null;

export function renderFeedShell({
  pack,
  cards,
  order,
  activeIndex,
  sourceRefs,
  states,
  notes,
  progress,
  preferences,
  sessionMinutes,
  shouldStop,
  onBack,
  onNavigate,
  onAction,
  onNote,
  onShare,
  onUnderstand,
  onPanel,
  onContinue
}) {
  const activeCard = cards.get(order[activeIndex]);
  const progressPercent = Math.round(((activeIndex + 1) / order.length) * 100);
  const visibleIndices = [
    activeIndex,
    Math.min(order.length - 1, activeIndex + 1)
  ].filter((value, index, values) => values.indexOf(value) === index);
  const activeCardKey = `${pack.id}:${order[activeIndex]}`;
  const resetPagePosition = activeCardKey !== lastActiveCardKey;
  lastActiveCardKey = activeCardKey;
  const feed = h("section", {
    className: "snap-feed",
    attrs: { "aria-label": "Knowledge card feed" }
  }, visibleIndices.map((index) => {
    const cardId = order[index];
    const card = cards.get(cardId);
    const state = states.get(cardId) ?? {};
    const note = notes.get(cardId);
    return h("section", {
      className: index === activeIndex ? "snap-panel is-active" : "snap-panel",
      attrs: { tabindex: "0", "aria-label": `Card ${index + 1} of ${order.length}: ${card.title}` },
      dataset: { cardId, cardIndex: String(index) }
    }, [
      renderKnowledgeCard({
        card,
        sourceRefs,
        state,
        note,
        revisitReason: state.revisitRequested
          ? "Revisit requested: use the prompt below to deepen or check recall."
          : null
      }),
      renderActionBar({
        card,
        state,
        onToggle: (key) => onAction(card, key),
        onNote: () => onNote(card),
        onShare: () => onShare(card),
        onUnderstand: (value) => onUnderstand(card, value)
      })
    ]);
  }));
  window.setTimeout(() => {
    if (!feed.isConnected) return;
    cleanupPageNavigation();
    cleanupPageNavigation = enablePageNavigation(
      feed,
      activeIndex,
      onNavigate,
      resetPagePosition
    );
  }, 0);
  return h("main", { className: "feed-view", attrs: { id: "app-main", style: `--pack-accent: ${pack.accent_color}` } }, [
    h("header", { className: "feed-header" }, [
      h("button", { className: "ghost-button", text: "Library", attrs: { type: "button" }, on: { click: onBack } }),
      h("h1", { text: pack.title }),
      h("button", { className: "ghost-button", text: "Menu", attrs: { type: "button" }, on: { click: () => onPanel("settings") } })
    ]),
    h("div", { className: "session-meter", attrs: { "aria-label": `${progressPercent}% through current order` } }, [
      h("span", { attrs: { style: `inline-size: ${progressPercent}%` } })
    ]),
    shouldStop
      ? h("aside", { className: "stopping-point", attrs: { role: "status" } }, [
          h("strong", { text: "A good stopping point." }),
          h("span", { text: ` You have viewed ${progress.viewed_count} cards in ${sessionMinutes} minutes. Save the map you built today, or consciously continue.` }),
          h("button", { className: "secondary-button", text: "Continue", attrs: { type: "button" }, on: { click: onContinue } })
        ])
      : null,
    feed,
    h("footer", { className: "feed-controls" }, [
      h("button", {
        className: "secondary-button",
        text: "Previous",
        attrs: { type: "button", disabled: activeIndex <= 0 },
        on: { click: () => onNavigate(Math.max(0, activeIndex - 1)) }
      }),
      h("span", { className: "small-copy", text: `${activeIndex + 1} / ${order.length} · ${sessionMinutes} min` }),
      h("button", {
        className: "primary-button",
        text: activeIndex >= order.length - 1 ? "Finish" : "Next",
        attrs: { type: "button" },
        on: { click: () => onNavigate(Math.min(order.length - 1, activeIndex + 1)) }
      })
    ])
  ]);
}

function enablePageNavigation(feed, activeIndex, onNavigate, resetPagePosition) {
  if (resetPagePosition) window.scrollTo({ top: 0, behavior: "auto" });
  const next = feed.querySelector(`[data-card-index="${activeIndex + 1}"]`);
  if (!next) return () => {};
  let activated = false;
  const activateIfReady = () => {
    if (!feed.isConnected) return;
    if (!activated && next.getBoundingClientRect().top <= stickyChromeHeight() + 24) {
      activated = true;
      onNavigate(activeIndex + 1);
    }
  };
  window.addEventListener("scroll", activateIfReady, { passive: true });
  const fallback = window.setInterval(activateIfReady, 250);
  return () => {
    window.removeEventListener("scroll", activateIfReady);
    window.clearInterval(fallback);
  };
}

function stickyChromeHeight() {
  const header = document.querySelector(".feed-header");
  const meter = document.querySelector(".session-meter");
  return (header?.offsetHeight ?? 0) + (meter?.offsetHeight ?? 0) + 12;
}
