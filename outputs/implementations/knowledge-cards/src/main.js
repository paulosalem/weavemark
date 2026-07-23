import { DEFAULT_SESSION_SEED, STORE_NAMES } from "./config.js";
import { createExport, previewImport, applyImport } from "./domain/importExport.js";
import { loadPack, loadPackIndex } from "./domain/packLoader.js";
import { chooseRevisitCard, planSessionOrder } from "./domain/feedOrdering.js";
import {
  createProgress,
  recordCardCompleted,
  recordCardViewed,
  shouldOfferStoppingPoint
} from "./domain/progress.js";
import { createRepository } from "./domain/repositories.js";
import { entityId, sessionOrderId } from "./domain/storageSchema.js";
import { minutesBetween, nowIso } from "./domain/time.js";
import { packUrl, panelUrl, parseRoute } from "./domain/url.js";
import { parseImportInWorker } from "./domain/workers.js";
import { renderFeedShell } from "./ui/feed.js?v=1.1.5";
import { renderPackLibrary } from "./ui/library.js";
import { renderNoteEditor } from "./ui/noteEditor.js";
import { renderPanel } from "./ui/panels.js";
import { renderRecoveryState } from "./ui/recovery.js";

const app = document.querySelector("#app");
const state = {
  repo: null,
  packIndex: null,
  activePack: null,
  activeOrder: [],
  activeIndex: 0,
  activeStates: new Map(),
  activeNotes: new Map(),
  noteCard: null,
  importPayload: null,
  importPreview: null,
  preferences: null,
  mutationChain: Promise.resolve(),
  sessionTimer: null
};

boot();

async function boot() {
  try {
    state.repo = await createRepository();
    state.preferences = await state.repo.getPreferences();
    applyPreferenceClasses();
    state.packIndex = await loadPackIndex();
    window.addEventListener("hashchange", route);
    window.addEventListener("keydown", handleKeys);
    window.addEventListener("online", () => announce("Back online."));
    window.addEventListener("offline", () => announce("Offline. Loaded packs and local state remain available."));
    await registerServiceWorker();
    await route();
  } catch (error) {
    app.replaceChildren(renderRecoveryState({
      title: "The library could not load",
      message: error.message,
      onAction: () => location.reload()
    }));
  }
}

async function route() {
  const routeState = parseRoute();
  if (routeState.view === "pack") {
    await openPack(routeState.packId, routeState.cardId);
  } else if (routeState.view === "panel") {
    await openPanel(routeState.panel);
  } else {
    await renderLibrary();
  }
}

async function renderLibrary() {
  clearSessionTimer();
  state.activePack = null;
  const progress = await state.repo.getAll(STORE_NAMES.progress);
  const progressByPack = new Map(progress.map((item) => [item.packId, item]));
  app.replaceChildren(renderPackLibrary({
    packs: state.packIndex.packs,
    progressByPack,
    preferences: state.preferences,
    repoWarning: state.repo.warning,
    onOpen: (packId, cardId) => {
      location.hash = packUrl(packId, cardId);
    },
    onPanel: (panel) => {
      location.hash = panelUrl(panel);
    },
    onDismissOnboarding: async () => {
      state.preferences = { ...state.preferences, onboardingDismissed: true };
      await state.repo.savePreferences(state.preferences);
      await renderLibrary();
    }
  }));
}

async function openPack(packId, requestedCardId = null) {
  const entry = state.packIndex.packs.find((pack) => pack.id === packId);
  if (!entry) throw new Error(`Unknown pack ${packId}`);
  state.activePack = await loadPack(entry);
  let progress = (await state.repo.get(STORE_NAMES.progress, packId)) ?? createProgress(packId);
  const sessionId = progress.last_session_started_at.replace(/[^0-9]/g, "");
  const sessionKey = sessionOrderId(packId, sessionId);
  let session = await state.repo.get(STORE_NAMES.sessionOrders, sessionKey);
  if (!session) {
    const cardStates = (await state.repo.getAll(STORE_NAMES.cardStates)).filter(
      (item) => item.packId === packId
    );
    const completed = cardStates.filter((item) => item.completed).map((item) => item.cardId);
    const cardStateMap = new Map(cardStates.map((item) => [item.cardId, item]));
    const cardIds = planSessionOrder(state.activePack.cards, {
      completedCardIds: completed,
      mode: state.preferences.orderedMode,
      seed: DEFAULT_SESSION_SEED
    });
    const revisit = chooseRevisitCard(
      state.activePack.cards,
      cardStateMap,
      progress.interactions_since_revisit
    );
    if (revisit && !cardIds.includes(revisit.id)) {
      cardIds.splice(Math.min(4, cardIds.length), 0, revisit.id);
      progress = {
        ...progress,
        interactions_since_revisit: 0,
        last_revisit_at: nowIso()
      };
      await state.repo.put(STORE_NAMES.progress, progress);
    }
    session = {
      id: sessionKey,
      packId,
      sessionId,
      seed: DEFAULT_SESSION_SEED,
      mode: state.preferences.orderedMode,
      card_ids: cardIds,
      created_at: nowIso()
    };
    await state.repo.put(STORE_NAMES.sessionOrders, session);
  }
  state.activeOrder = [...session.card_ids];
  if (
    requestedCardId &&
    state.activePack.byId.has(requestedCardId) &&
    !state.activeOrder.includes(requestedCardId)
  ) {
    state.activeOrder.unshift(requestedCardId);
  }
  state.activeIndex = Math.max(
    0,
    requestedCardId
      ? state.activeOrder.indexOf(requestedCardId)
      : state.activeOrder.indexOf(progress.active_card_id)
  );
  if (state.activeIndex < 0) state.activeIndex = 0;
  await hydrateActiveState();
  await renderFeed(progress);
}

async function hydrateActiveState() {
  const packId = state.activePack.manifest.id;
  const [cardStates, notes] = await Promise.all([
    state.repo.getAll(STORE_NAMES.cardStates),
    state.repo.getAll(STORE_NAMES.notes)
  ]);
  state.activeStates = new Map(cardStates.filter((item) => item.packId === packId).map((item) => [item.cardId, item]));
  state.activeNotes = new Map(notes.filter((item) => item.packId === packId).map((item) => [item.cardId, item]));
}

async function renderFeed(progress) {
  const packId = state.activePack.manifest.id;
  const activeCardId = state.activeOrder[state.activeIndex];
  const isNewView = !(progress.session_viewed_card_ids ?? []).includes(activeCardId);
  const nextProgress = recordCardViewed(progress, activeCardId);
  await state.repo.put(STORE_NAMES.progress, nextProgress);
  if (isNewView) {
    await state.repo.addHistory({
      packId,
      cardId: activeCardId,
      label: `Viewed ${state.activePack.byId.get(activeCardId).title}`
    });
  }
  const sessionMinutes = minutesBetween(nextProgress.last_session_started_at);
  const shouldStop = shouldOfferStoppingPoint(nextProgress, state.preferences);
  app.replaceChildren(renderFeedShell({
    pack: state.activePack.entry,
    cards: state.activePack.byId,
    order: state.activeOrder,
    activeIndex: state.activeIndex,
    sourceRefs: state.activePack.sourceRefs,
    states: state.activeStates,
    notes: state.activeNotes,
    progress: nextProgress,
    preferences: state.preferences,
    sessionMinutes,
    shouldStop,
    onBack: () => {
      location.hash = "#/";
    },
    onNavigate: (index) => navigateToCard(index),
    onAction: toggleAction,
    onNote: openNoteSheet,
    onShare: copyCardLink,
    onUnderstand: setUnderstanding,
    onPanel: (panel) => {
      location.hash = panelUrl(panel);
    },
    onContinue: async () => {
      await state.repo.put(STORE_NAMES.progress, {
        ...nextProgress,
        viewed_count: 0,
        session_viewed_card_ids: [],
        last_session_started_at: nowIso()
      });
      await openPack(packId, activeCardId);
    }
  }));
  scheduleSessionTimer(nextProgress);
}

async function navigateToCard(index) {
  state.activeIndex = index;
  const cardId = state.activeOrder[index];
  history.replaceState(null, "", packUrl(state.activePack.manifest.id, cardId));
  const progress = (await state.repo.get(STORE_NAMES.progress, state.activePack.manifest.id)) ?? createProgress(state.activePack.manifest.id);
  await renderFeed(progress);
}

function toggleAction(card, key) {
  const mutation = state.mutationChain.then(() => commitToggleAction(card, key));
  state.mutationChain = mutation.catch((error) => {
    announce(`Could not update this card: ${error.message}`);
  });
  return mutation;
}

async function commitToggleAction(card, key) {
  const packId = state.activePack.manifest.id;
  const previous = (await state.repo.getCardState(packId, card.id)) ?? {};
  const nextValue = !previous[key];
  const patch = { ...previous, [key]: nextValue, completed: true };
  if (key === "saved") {
    const saved = { id: entityId(packId, card.id), packId, cardId: card.id, cardTitle: card.title, created_at: nowIso() };
    if (nextValue) await state.repo.put(STORE_NAMES.savedCards, saved);
    else await state.repo.delete(STORE_NAMES.savedCards, saved.id);
  }
  await state.repo.saveCardState(packId, card.id, patch);
  const progress = recordCardCompleted(
    (await state.repo.get(STORE_NAMES.progress, packId)) ?? createProgress(packId),
    card.id,
    Boolean(previous.completed)
  );
  await state.repo.put(STORE_NAMES.progress, progress);
  const label = {
    liked: "Like",
    saved: "Save",
    revisitRequested: "Revisit"
  }[key] ?? "Card action";
  announce(
    nextValue
      ? `${label} stored locally.`
      : `${label} cleared. Undo by pressing the button again.`
  );
  await hydrateActiveState();
  await renderFeed(progress);
}

function setUnderstanding(card, value) {
  const mutation = state.mutationChain.then(() => commitUnderstanding(card, value));
  state.mutationChain = mutation.catch((error) => {
    announce(`Could not save understanding: ${error.message}`);
  });
  return mutation;
}

async function commitUnderstanding(card, value) {
  const packId = state.activePack.manifest.id;
  const previous = (await state.repo.getCardState(packId, card.id)) ?? {};
  await state.repo.saveCardState(packId, card.id, {
    ...previous,
    understanding: value,
    completed: true
  });
  const progress = recordCardCompleted(
    (await state.repo.get(STORE_NAMES.progress, packId)) ?? createProgress(packId),
    card.id,
    Boolean(previous.completed)
  );
  await state.repo.put(STORE_NAMES.progress, progress);
  announce(value ? "Understanding signal saved. It is not treated as proof of mastery." : "Understanding signal cleared.");
  await hydrateActiveState();
  await renderFeed(progress);
}

async function openNoteSheet(card) {
  state.noteCard = card;
  const packId = state.activePack.manifest.id;
  const [draft, note] = await Promise.all([
    state.repo.get(STORE_NAMES.noteDrafts, entityId(packId, card.id)),
    state.repo.get(STORE_NAMES.notes, entityId(packId, card.id))
  ]);
  const sheet = renderNoteEditor({
    card,
    draft: draft?.body ?? "",
    note: note?.body ?? "",
    onDraft: async (body) => {
      await state.repo.put(STORE_NAMES.noteDrafts, {
        id: entityId(packId, card.id),
        packId,
        cardId: card.id,
        body,
        updated_at: nowIso()
      });
    },
    onSave: async (body) => {
      await state.repo.put(STORE_NAMES.notes, {
        id: entityId(packId, card.id),
        packId,
        cardId: card.id,
        body,
        updated_at: nowIso()
      });
      await state.repo.delete(STORE_NAMES.noteDrafts, entityId(packId, card.id));
      const previous = (await state.repo.getCardState(packId, card.id)) ?? {};
      await state.repo.saveCardState(packId, card.id, { ...previous, completed: true });
      const progress = recordCardCompleted(
        (await state.repo.get(STORE_NAMES.progress, packId)) ?? createProgress(packId),
        card.id,
        Boolean(previous.completed)
      );
      await state.repo.put(STORE_NAMES.progress, progress);
      announce("Note saved locally.");
      await hydrateActiveState();
      await renderFeed(progress);
    },
    onClose: async () => {
      await renderFeed((await state.repo.get(STORE_NAMES.progress, packId)) ?? createProgress(packId));
    }
  });
  app.append(sheet);
  sheet.querySelector("textarea")?.focus();
}

async function copyCardLink(card) {
  const url = new URL(packUrl(state.activePack.manifest.id, card.id), location.href).toString();
  await navigator.clipboard?.writeText(url);
  announce("Card link copied. Opening it never shares your notes or progress.");
}

async function openPanel(panel) {
  clearSessionTimer();
  const data = {
    preferences: state.preferences,
    importPreview: state.importPreview,
    notes: await state.repo.getAll(STORE_NAMES.notes),
    savedCards: await state.repo.getAll(STORE_NAMES.savedCards),
    history: (await state.repo.getAll(STORE_NAMES.history)).slice(-50).reverse()
  };
  app.replaceChildren(renderPanel({
    panel,
    data,
    handlers: {
      onBack: () => {
        location.hash = "#/";
      },
      onOpenCard: (packId, cardId) => {
        location.hash = packUrl(packId, cardId);
      },
      onPreference: async (patch) => {
        state.preferences = { ...state.preferences, ...patch };
        await state.repo.savePreferences(state.preferences);
        applyPreferenceClasses();
        await openPanel(panel);
      },
      onExport: exportLocalState,
      onImportFile: importFile,
      onApplyImport: async () => {
        await applyImport(state.repo, state.importPayload, { mode: "merge" });
        state.importPayload = null;
        state.importPreview = null;
        announce("Import merged with rollback protection.");
        await openPanel(panel);
      }
    }
  }));
}

async function exportLocalState() {
  const payload = await createExport(state.repo);
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `knowledge-cards-export-${new Date().toISOString().slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
}

async function importFile(event) {
  const file = event.currentTarget.files?.[0];
  if (!file) return;
  try {
    state.importPayload = await parseImportInWorker(await file.text());
    state.importPreview = await previewImport(state.repo, state.importPayload);
  } catch (error) {
    state.importPayload = null;
    state.importPreview = { valid: false, errors: [`Could not parse import: ${error.message}`], conflicts: [], counts: {} };
  }
  await openPanel("import-export");
}

function handleKeys(event) {
  const editable = event.target.closest?.("input, textarea, select, [contenteditable='true']");
  if (
    !state.activePack ||
    parseRoute().view !== "pack" ||
    editable ||
    event.altKey ||
    event.metaKey ||
    event.ctrlKey
  ) return;
  if (event.key === "ArrowRight" || event.key === "PageDown") {
    event.preventDefault();
    navigateToCard(Math.min(state.activeOrder.length - 1, state.activeIndex + 1));
  }
  if (event.key === "ArrowLeft" || event.key === "PageUp") {
    event.preventDefault();
    navigateToCard(Math.max(0, state.activeIndex - 1));
  }
}

function scheduleSessionTimer(progress) {
  clearSessionTimer();
  const limit = state.preferences.sessionMinuteLimit ?? 10;
  const remaining =
    Date.parse(progress.last_session_started_at) + limit * 60_000 - Date.now();
  if (remaining <= 0) return;
  state.sessionTimer = window.setTimeout(async () => {
    const latest = await state.repo.get(STORE_NAMES.progress, progress.packId);
    if (latest && parseRoute().view === "pack") await renderFeed(latest);
  }, remaining + 100);
}

function clearSessionTimer() {
  if (state.sessionTimer !== null) {
    window.clearTimeout(state.sessionTimer);
    state.sessionTimer = null;
  }
}

function applyPreferenceClasses() {
  document.documentElement.dataset.textSize = state.preferences?.textSize ?? "regular";
  document.documentElement.dataset.reducedMotion = state.preferences?.reducedMotion ? "true" : "false";
}

function announce(message) {
  let region = document.querySelector("#status-region");
  if (!region) {
    region = document.createElement("div");
    region.id = "status-region";
    region.className = "sr-only";
    region.setAttribute("aria-live", "polite");
    document.body.append(region);
  }
  region.textContent = message;
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator) || location.protocol === "file:") return;
  try {
    const registration = await navigator.serviceWorker.register(new URL("../sw.js", import.meta.url), { scope: "./" });
    if (registration.active) {
      registration.addEventListener("updatefound", () =>
        announce("Update detected. Reload when you are ready.")
      );
    }
  } catch (error) {
    console.warn("Service worker registration failed; app still runs online.", error);
  }
}
