import { loadBootstrapFiles } from "./bootstrap.js";
import {
  acquireWorkspaceLock,
  acquireDirectoryCreationLock,
  clearRecentHandle,
  downloadArchive,
  FolderWorkspace,
  nativeFileSystemSupported,
  PortableWorkspace,
  queryHandlePermission,
  recentHandle,
  reconnectRecent,
  WorkspaceConflictError,
} from "./file-workspace.js";
import {
  CoordinationService,
  agentStateLabel,
  isAgentGrantCandidate,
} from "./coordination.js";
import { renderMarkdown, escapeHtml } from "./markdown.js";
import { latestSuccessfulOutput } from "./output-selection.js";
import {
  createHandoffPacket,
  validateResponsePacket,
} from "./packets.js";
import { AIProviderAdapter } from "./provider-adapter.js";
import { BoardRepository } from "./repository.js";
import { SerializedSaveQueue } from "./save-queue.js";
import { shellQuote } from "./shell-quote.js";
import { renderSurface } from "./surfaces.js";
import { MAX_WORKSPACE_BYTES } from "./constants.js";

const repository = new BoardRepository();
const providerAdapter = new AIProviderAdapter();
const broadcast = "BroadcastChannel" in window
  ? new BroadcastChannel("ai-kanban-workspaces")
  : null;

const state = {
  workspace: null,
  snapshot: null,
  selectedCard: null,
  selectedTab: "overview",
  dirty: false,
  saving: false,
  readOnly: false,
  detachedForAgent: false,
  loading: false,
  lock: null,
  coordination: null,
  readRepository: null,
  agent: null,
  conflict: null,
  pendingImport: null,
  handoffFormat: "json",
  directPreview: null,
  directReview: null,
  credentialVersion: 0,
  genericAction: null,
  filters: {
    query: "",
    priority: "",
    assignee: "",
    columnId: "",
    kind: "",
    turnStatus: "",
    attention: "",
    origin: "",
    blocked: false,
    archived: false,
  },
};

const saveQueue = new SerializedSaveQueue(persistWorkspace);

const elements = Object.fromEntries(
  [
    "welcome", "application", "welcomeOpenButton", "welcomeCreateButton",
    "demoButton", "browserSupportNote", "recentButton", "recentName",
    "workspaceName", "saveStatus", "connectionDot", "saveButton",
    "newCardButton", "agentButton", "agentStatusDot", "globalHandoffButton",
    "workspaceMenuButton", "workspaceMenu", "exportArchiveButton",
    "repairBootstrapButton", "archivedCardsButton", "aboutWorkspaceButton",
    "closeWorkspaceButton", "workspaceAlert", "searchInput", "filtersButton",
    "quickFilters", "activeFilterCount", "visibleCardCount", "boardSummary",
    "needsYouCount", "aiWorkingCount", "aiUpdatedCount", "emptyBoardState",
    "board", "archiveInput", "packetFileInput", "cardComposerDialog",
    "cardComposerForm", "composerTitle", "composerColumn", "cardDetailDialog",
    "detailBreadcrumb", "detailTitle", "detailMeta", "detailTabs", "detailBody",
    "archiveCardButton", "publishResultButton", "cancelTurnButton",
    "readyForAgentButton", "filtersDialog", "filtersForm", "filterColumn",
    "clearFiltersButton", "agentDialog", "agentConnectionState",
    "agentFallbackText", "agentDiagnostics", "copyAgentInstructionsButton",
    "repairFromAgentButton", "retryAgentButton", "agentControlAction",
    "handoffDialog", "handoffCardSelect", "handoffExportPanel",
    "handoffImportPanel", "handoffDirectPanel", "handoffExportText",
    "handoffImportText", "copyHandoffButton", "downloadHandoffButton",
    "choosePacketButton", "previewImportButton", "handoffPreview",
    "applyImportButton", "providerName", "providerModel", "providerEndpoint",
    "providerCredential", "providerPurpose", "previewDirectButton",
    "directPreview", "sendDirectButton", "genericDialog", "genericForm",
    "genericEyebrow", "genericTitle", "genericFields", "genericSubmit",
    "conflictDialog", "conflictDetails", "reloadConflictButton",
    "exportDraftButton", "recoverConflictButton", "aboutDialog",
    "workspaceDetails", "loadingOverlay", "loadingText", "toastRegion",
  ].map((id) => [id, document.getElementById(id)]),
);

initialize();

async function initialize() {
  bindEvents();
  elements.browserSupportNote.textContent = nativeFileSystemSupported
    ? "Your browser can connect directly to a Board Workspace folder."
    : "Connected folders are unavailable here. Open and save explicitly labeled portable archives instead.";
  if (!nativeFileSystemSupported) {
    elements.welcomeOpenButton.innerHTML = '<span aria-hidden="true">↥</span> Import Board Archive';
    elements.welcomeCreateButton.innerHTML = '<span aria-hidden="true">＋</span> Create Download-only Board';
  } else {
    const handle = await recentHandle().catch(() => null);
    if (handle) {
      elements.recentName.textContent = handle.name;
      elements.recentButton.hidden = false;
      const permission = await queryHandlePermission(handle).catch(() => "prompt");
      elements.recentButton.dataset.permission = permission;
    }

  }
  updateChrome();
}

function bindEvents() {
  elements.welcomeOpenButton.addEventListener("click", openWorkspace);
  elements.welcomeCreateButton.addEventListener("click", createWorkspace);
  elements.demoButton.addEventListener("click", openDemo);
  elements.recentButton.addEventListener("click", reconnectWorkspace);
  elements.saveButton.addEventListener("click", () => saveNow());
  elements.newCardButton.addEventListener("click", () => openCardComposer());
  document.querySelector("[data-action='new-card']").addEventListener("click", () => openCardComposer());
  elements.agentButton.addEventListener("click", openAgentDialog);
  elements.globalHandoffButton.addEventListener("click", () => openHandoff());
  elements.workspaceMenuButton.addEventListener("click", toggleWorkspaceMenu);
  elements.exportArchiveButton.addEventListener("click", exportWorkspaceArchive);
  elements.repairBootstrapButton.addEventListener("click", showBootstrapRepair);
  elements.archivedCardsButton.addEventListener("click", showArchivedCards);
  elements.aboutWorkspaceButton.addEventListener("click", showWorkspaceDetails);
  elements.closeWorkspaceButton.addEventListener("click", closeWorkspace);
  elements.archiveInput.addEventListener("change", importArchive);
  elements.packetFileInput.addEventListener("change", importPacketFile);
  elements.searchInput.addEventListener("input", (event) => {
    state.filters.query = event.target.value.trim().toLowerCase();
    renderBoard();
  });
  elements.filtersButton.addEventListener("click", openFilters);
  elements.filtersForm.addEventListener("submit", applyFilters);
  elements.clearFiltersButton.addEventListener("click", clearFilters);
  elements.quickFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-priority]");
    if (!button) return;
    state.filters.priority = button.dataset.priority;
    elements.quickFilters.querySelectorAll("[data-priority]").forEach((candidate) => {
      candidate.setAttribute("aria-pressed", String(candidate === button));
    });
    updateFilterCount();
    renderBoard();
  });
  document.querySelectorAll("[data-attention-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.filters.attention = state.filters.attention === button.dataset.attentionFilter
        ? ""
        : button.dataset.attentionFilter;
      updateFilterCount();
      renderBoard();
    });
  });
  elements.cardComposerForm.addEventListener("submit", createCard);
  elements.cardComposerForm.elements.recurring.addEventListener("change", (event) => {
    elements.cardComposerForm.querySelectorAll(".recurring-field").forEach((field) => {
      field.hidden = !event.target.checked;
    });
  });
  elements.detailTabs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-tab]");
    if (button) selectDetailTab(button.dataset.tab);
  });
  elements.detailTabs.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    const tabs = [...elements.detailTabs.querySelectorAll("[data-tab]")]
      .filter((tab) => !tab.hidden);
    const current = tabs.indexOf(event.target.closest("[data-tab]"));
    if (current < 0) return;
    event.preventDefault();
    const next = event.key === "Home"
      ? 0
      : event.key === "End"
        ? tabs.length - 1
        : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    selectDetailTab(tabs[next].dataset.tab);
    tabs[next].focus();
  });
  elements.archiveCardButton.addEventListener("click", archiveCard);
  elements.publishResultButton.addEventListener("click", publishResult);
  elements.readyForAgentButton.addEventListener("click", readyForAgent);
  elements.cancelTurnButton.addEventListener("click", cancelActiveTurn);
  elements.copyAgentInstructionsButton.addEventListener("click", copyAgentInstructions);
  elements.repairFromAgentButton.addEventListener("click", showBootstrapRepair);
  elements.retryAgentButton.addEventListener("click", () => state.coordination?.poll());
  elements.agentControlAction.addEventListener("click", handleAgentControl);
  elements.handoffCardSelect.addEventListener("change", () => {
    invalidateDirectSend();
    refreshHandoff();
  });
  document.querySelectorAll("[data-handoff-tab]").forEach((button) => {
    button.addEventListener("click", () => switchHandoffTab(button.dataset.handoffTab));
  });
  document.querySelectorAll("[data-format]").forEach((button) => {
    button.addEventListener("click", () => {
      state.handoffFormat = button.dataset.format;
      document.querySelectorAll("[data-format]").forEach((candidate) => {
        candidate.setAttribute("aria-pressed", String(candidate === button));
      });
      refreshHandoff();
    });
  });
  elements.copyHandoffButton.addEventListener("click", copyHandoff);
  elements.downloadHandoffButton.addEventListener("click", downloadHandoff);
  elements.choosePacketButton.addEventListener("click", () => elements.packetFileInput.click());
  elements.previewImportButton.addEventListener("click", previewImport);
  elements.applyImportButton.addEventListener("click", applyImport);
  elements.previewDirectButton.addEventListener("click", previewDirectSend);
  elements.sendDirectButton.addEventListener("click", sendDirect);
  for (const input of [
    elements.providerName,
    elements.providerModel,
    elements.providerEndpoint,
    elements.providerPurpose,
    elements.providerCredential,
  ]) {
    input.addEventListener("input", () => {
      state.credentialVersion += 1;
      invalidateDirectSend();
    });
  }
  elements.handoffDialog.addEventListener("close", () => {
    invalidateDirectSend({ clearCredential: true });
  });
  elements.genericForm.addEventListener("submit", submitGenericDialog);
  elements.reloadConflictButton.addEventListener("click", reloadAfterConflict);
  elements.exportDraftButton.addEventListener("click", exportDraft);
  elements.recoverConflictButton.addEventListener("click", recoverConflict);
  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog")?.close());
  });
  document.addEventListener("click", (event) => {
    if (
      !elements.workspaceMenu.hidden &&
      !elements.workspaceMenu.contains(event.target) &&
      event.target !== elements.workspaceMenuButton
    ) {
      hideWorkspaceMenu();
    }
  });
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k" && state.snapshot) {
      event.preventDefault();
      elements.searchInput.focus();
    }
    if (event.key === "Escape" && !elements.workspaceMenu.hidden) hideWorkspaceMenu();
  });
  window.addEventListener("beforeunload", (event) => {
    if (!state.dirty && !state.saving && !saveQueue.pending) return;
    event.preventDefault();
    event.returnValue = "";
  });
  broadcast?.addEventListener("message", ({ data }) => {
    if (
      state.workspace?.mode === "connected" &&
      data?.workspaceId === state.snapshot?.meta?.workspace_id &&
      data.type === "saved"
    ) {
      state.readOnly = true;
      state.lock?.release();
      state.lock = null;
      state.workspace.setWriterLock?.(null);
      if (state.dirty) {
        showConflict(new WorkspaceConflictError({
          loaded: {
            revision: Number(state.snapshot.meta.revision),
            fingerprint: state.workspace.loadedSignature?.fingerprint,
          },
          disk: {
            revision: Number(data.revision),
            fingerprint: data.fingerprint || null,
          },
        }));
        updateChrome();
        return;
      }
      setWorkspaceAlert(
        "Another tab saved this workspace. This tab is now read-only until you reload.",
        "warning",
        [["Reload", reloadWorkspace]],
      );
      updateChrome();
    }
  });
}

async function openWorkspace() {
  if (!(await prepareWorkspaceSwitch())) return;
  if (!nativeFileSystemSupported) {
    elements.archiveInput.click();
    return;
  }
  try {
    const workspace = await FolderWorkspace.openNative();
    await activateWorkspace(workspace, { create: false });
  } catch (error) {
    handleActionError(error);
  }
}

async function createWorkspace() {
  if (!(await prepareWorkspaceSwitch())) return;
  let creationLock = null;
  try {
    const workspace = nativeFileSystemSupported
      ? await FolderWorkspace.createNative()
      : new PortableWorkspace({ name: "New Board Workspace" });
    let bootstrapFiles = null;
    let confirmedBootstrapReplacements = [];
    if (workspace instanceof FolderWorkspace) {
      creationLock = await acquireDirectoryCreationLock(workspace.handle);
      if (!creationLock.acquired) {
        throw typedError(
          "CREATION_LOCK_UNAVAILABLE",
          "Another tab is creating a workspace in a folder with this directory identity.",
        );
      }
      await workspace.assertCreatable();
      bootstrapFiles = await loadBootstrapFiles();
      const status = await workspace.bootstrapStatus(bootstrapFiles);
      const conflicts = status.filter((item) => item.state === "path-conflict");
      if (conflicts.length) {
        throw typedError(
          "BOOTSTRAP_PATH_CONFLICT",
          `A bootstrap path is occupied by a directory: ${conflicts.map((item) => item.path).join(", ")}`,
        );
      }
      const modified = status.filter((item) => item.state === "modified");
      if (
        modified.length &&
        !window.confirm(
          `This folder contains ${modified.length} existing agent instruction file${modified.length === 1 ? "" : "s"}:\n\n` +
          `${modified.map((item) => `• ${item.path}`).join("\n")}\n\n` +
          "Replace these files with the generated AI Kanban versions? Cancel preserves the folder unchanged.",
        )
      ) {
        creationLock.release();
        creationLock = null;
        return;
      }
      confirmedBootstrapReplacements = modified.map(
        ({ path, actualContent }) => ({ path, actualContent }),
      );
    }
    await activateWorkspace(workspace, {
      create: true,
      bootstrapFiles,
      confirmedBootstrapReplacements,
      creationLock,
    });
    creationLock = null;
  } catch (error) {
    handleActionError(error);
  } finally {
    creationLock?.release();
  }
}

async function openDemo() {
  if (!(await prepareWorkspaceSwitch())) return;
  await activateWorkspace(PortableWorkspace.demo(), { create: true, demo: true });
}

async function reconnectWorkspace() {
  if (!(await prepareWorkspaceSwitch())) return;
  const handle = await recentHandle().catch(() => null);
  if (!handle) {
    elements.recentButton.hidden = true;
    return;
  }
  try {
    const workspace = await reconnectRecent(handle);
    await activateWorkspace(workspace, { create: false });
  } catch (error) {
    if (error.code === "PERMISSION_DENIED") await clearRecentHandle();
    handleActionError(error);
  }
}

async function importArchive(event) {
  const [file] = event.target.files;
  event.target.value = "";
  if (!file) return;
  try {
    const workspace = await PortableWorkspace.fromArchiveFile(file);
    await activateWorkspace(workspace, { create: false });
  } catch (error) {
    handleActionError(error);
  }
}

async function activateWorkspace(
  workspace,
  {
    create,
    demo = false,
    bootstrapFiles = null,
    confirmedBootstrapReplacements = [],
    creationLock = null,
  },
) {
  await releaseWorkspace();
  setLoading(true, create ? "Creating your workspace…" : "Opening your workspace…");
  let preAcquiredLock = null;
  try {
    let snapshot;
    let openedStateBytes = null;
    if (create) {
      if (workspace instanceof FolderWorkspace) {
        await workspace.assertCreatable();
        preAcquiredLock = await acquireWorkspaceLock(
          workspace.manifest.workspace_id,
        );
        if (!preAcquiredLock.acquired) {
          throw typedError(
            "WORKSPACE_LOCK_UNAVAILABLE",
            "Another tab acquired this workspace before creation completed.",
          );
        }
        workspace.setWriterLock(preAcquiredLock);
      }
      snapshot = await repository.create({
        demo,
        workspaceId: workspace.manifest.workspace_id,
      });
      const bytes = await repository.exportBytes();
      if (workspace instanceof FolderWorkspace) {
        const bootstrap = bootstrapFiles || await loadBootstrapFiles();
        await workspace.initialize(bytes, bootstrap, {
          confirmedReplacements: confirmedBootstrapReplacements,
        });
        workspace.manifest.revision = Number(snapshot.meta.revision);
      } else {
        workspace.stateBytes = bytes;
        workspace.manifest.revision = Number(snapshot.meta.revision);
      }
    } else {
      const bytes = await workspace.readState();
      openedStateBytes = bytes;
      snapshot = await openVerifiedWorkspaceBytes(
        bytes,
        workspace,
        workspace.manifest.workspace_id,
        false,
        true,
      );
    }
    state.workspace = workspace;
    state.snapshot = snapshot;
    const unpublishedGrant =
      snapshot.meta.control_state === "granting_agent" &&
      snapshot.meta.control_holder === "human";
    const schemaUpgraded =
      Number(workspace.manifest.schema_version) !==
      Number(snapshot.meta.schema_version);
    if (schemaUpgraded) {
      workspace.manifest.schema_version = Number(snapshot.meta.schema_version);
    }
    state.dirty = schemaUpgraded;
    state.readOnly = unpublishedGrant;
    state.detachedForAgent = snapshot.meta.control_state === "agent";
    if (state.detachedForAgent) {
      state.readRepository = new BoardRepository();
      await state.readRepository.open(openedStateBytes);
      await repository.close();
      state.readOnly = true;
    }
    state.lock = preAcquiredLock || await acquireWorkspaceLock(snapshot.meta.workspace_id);
    workspace.setWriterLock?.(state.lock);
    creationLock?.release();
    creationLock = null;
    preAcquiredLock = null;
    if (!state.lock.acquired) {
      state.readOnly = true;
      setWorkspaceAlert(
        "Another tab owns the workspace lock. This tab is read-only.",
        "warning",
      );
    } else {
      clearWorkspaceAlert();
    }
    if (workspace.mode === "connected") {
      setupCoordination();
      await inspectBootstrap();
    } else if (workspace.mode === "memory-only") {
      setWorkspaceAlert(
        "Demo workspace · memory only. Use Save to download a portable archive before closing.",
        "warning",
      );
    } else {
      setWorkspaceAlert(
        "Archive mode · changes stay in memory until Save downloads an updated archive.",
        "warning",
      );
    }
    if (unpublishedGrant) {
      setWorkspaceAlert(
        "A previous browser stopped during an unpublished agent grant. Editing stays disabled until the human-owned grant is safely rolled back.",
        "warning",
        [["Roll back unpublished grant", rollbackUnpublishedGrant]],
      );
    }
    resetFilters();
    elements.welcome.hidden = true;
    elements.application.hidden = false;
    populateColumnSelects();
    renderBoard();
    updateChrome();
    if (schemaUpgraded && workspace.mode === "connected" && !state.readOnly) {
      saveQueue.schedule(0);
    }
  } catch (error) {
    state.coordination?.stop();
    state.coordination = null;
    state.lock?.release();
    state.lock = null;
    workspace.setWriterLock?.(null);
    preAcquiredLock?.release();
    creationLock?.release();
    await repository.close().catch(() => {});
    await closeReadRepository();
    state.workspace = null;
    state.snapshot = null;
    elements.application.hidden = true;
    elements.welcome.hidden = false;
    handleActionError(error);
  } finally {
    setLoading(false);
  }
}

async function prepareWorkspaceSwitch() {
  if (
    !state.snapshot ||
    (!state.dirty && !state.saving && !saveQueue.pending)
  ) return true;
  try {
    await saveNow();
    return !state.dirty;
  } catch {
    return window.confirm("Saving did not finish. Discard the in-memory draft and switch workspaces?");
  }
}

async function releaseWorkspace() {
  await saveQueue.reset();
  state.coordination?.stop();
  state.coordination = null;
  state.lock?.release();
  state.lock = null;
  if (!state.detachedForAgent) await repository.close().catch(() => {});
  await closeReadRepository();
  state.workspace = null;
  state.snapshot = null;
  state.selectedCard = null;
  state.dirty = false;
  state.saving = false;
  state.readOnly = false;
  state.detachedForAgent = false;
  state.agent = null;
  invalidateDirectSend({ clearCredential: true });
}

async function closeWorkspace() {
  hideWorkspaceMenu();
  if (!(await prepareWorkspaceSwitch())) return;
  await releaseWorkspace();
  elements.application.hidden = true;
  elements.welcome.hidden = false;
  updateChrome();
}

async function persistWorkspace(
  { force = false, recovery = false } = {},
  saveContext = { isCurrent: () => true },
) {
  if (!state.workspace || state.readOnly || state.detachedForAgent) return;
  const workspace = state.workspace;
  state.saving = true;
  updateChrome();
  try {
    const bytes = await repository.exportBytes();
    const savedRevision = Number(state.snapshot.meta.revision);
    await workspace.saveState(bytes, {
      force,
      recovery,
      revision: savedRevision,
    });
    if (workspace !== state.workspace) return;
    const saveIsCurrent =
      saveContext.isCurrent() &&
      Number(state.snapshot.meta.revision) === savedRevision;
    if (saveIsCurrent) {
      state.dirty = false;
      clearWorkspaceAlert();
      if (workspace.mode === "connected") {
        broadcast?.postMessage({
          type: "saved",
          workspaceId: state.snapshot.meta.workspace_id,
          revision: savedRevision,
          fingerprint: workspace.loadedSignature?.fingerprint || null,
        });
      }
      showToast(
        workspace.mode === "connected"
          ? "Workspace saved to its folder."
          : "Portable workspace archive downloaded.",
        "success",
      );
    }
  } catch (error) {
    state.dirty = true;
    if (error instanceof WorkspaceConflictError) showConflict(error);
    else handleActionError(error);
    throw error;
  } finally {
    state.saving = false;
    updateChrome();
  }
}

function saveNow(options = {}) {
  if (!state.workspace || state.readOnly) return Promise.resolve();
  return saveQueue.flush({ runIfClean: true, saveOptions: options });
}

function markDirty() {
  state.dirty = true;
  if (state.workspace?.mode === "connected" && !state.readOnly) saveQueue.schedule(700);
  updateChrome();
}

async function runMutation(operation, parameters = {}, { refreshDetail = false, context = {} } = {}) {
  if (state.readOnly || state.detachedForAgent) {
    showToast("Reclaim the writer baton before editing this workspace.", "warning");
    return null;
  }
  try {
    const result = await repository.mutate(operation, parameters, context);
    state.snapshot = result.snapshot;
    markDirty();
    await renderBoard();
    if (refreshDetail && state.selectedCard) await refreshSelectedCard();
    return result;
  } catch (error) {
    const message = userMessage(error);
    setWorkspaceAlert(message, "error");
    showToast(message, "error");
    return null;
  }
}

async function renderBoard() {
  if (!state.snapshot) return;
  if (state.filters.archived) {
    await renderArchivedBoard();
    return;
  }
  const cards = state.snapshot.cards.filter(cardMatchesFilters);
  elements.visibleCardCount.textContent = `${cards.length} ${cards.length === 1 ? "card" : "cards"}`;
  elements.boardSummary.textContent = activeFilterCount()
    ? `Filtered from ${state.snapshot.cards.length}`
    : "All active work";
  elements.needsYouCount.textContent = state.snapshot.counts.needsYou;
  elements.aiWorkingCount.textContent = state.snapshot.counts.aiWorking;
  elements.aiUpdatedCount.textContent = state.snapshot.counts.aiUpdated;
  elements.emptyBoardState.hidden = state.snapshot.cards.length !== 0;
  elements.board.hidden = state.snapshot.cards.length === 0;
  elements.board.replaceChildren(
    ...state.snapshot.columns.map((column, columnIndex) => {
      const columnCards = cards.filter((card) => card.columnId === column.id);
      const section = document.createElement("section");
      section.className = "board-column";
      section.dataset.columnId = column.id;
      section.style.setProperty("--column-color", column.color);
      section.innerHTML = `
        <header class="column-header">
          <div><span class="column-dot" aria-hidden="true"></span><h2>${escapeHtml(column.title)}</h2></div>
          <span class="column-count">${columnCards.length}</span>
        </header>
        <div class="column-cards" role="list" aria-label="${escapeHtml(column.title)} cards"></div>
        <button class="add-card-button" type="button">＋ Add card</button>
      `;
      const list = section.querySelector(".column-cards");
      list.append(...columnCards.map((card) => renderCard(card, columnIndex)));
      if (!columnCards.length) {
        const empty = document.createElement("div");
        empty.className = "column-empty";
        empty.textContent = activeFilterCount()
          ? "No matching cards"
          : column.id === "inbox"
            ? "New ideas and questions arrive here"
            : `No work in ${column.title}`;
        list.append(empty);
      }
      section.querySelector(".add-card-button").disabled = state.readOnly;
      section.querySelector(".add-card-button").addEventListener("click", () => openCardComposer(column.id));
      list.addEventListener("dragover", (event) => {
        if (state.readOnly) return;
        event.preventDefault();
        list.classList.add("is-drop-target");
      });
      list.addEventListener("dragleave", (event) => {
        if (!list.contains(event.relatedTarget)) list.classList.remove("is-drop-target");
      });
      list.addEventListener("drop", async (event) => {
        event.preventDefault();
        list.classList.remove("is-drop-target");
        const cardId = event.dataTransfer.getData("text/ai-kanban-card");
        if (cardId) await moveCard(cardId, column.id);
      });
      return section;
    }),
  );
}

async function renderArchivedBoard() {
  const cards = await queryRepository().archivedCards();
  elements.visibleCardCount.textContent = `${cards.length} archived`;
  elements.boardSummary.textContent = "Archived work";
  elements.emptyBoardState.hidden = true;
  elements.board.hidden = false;
  const section = document.createElement("section");
  section.className = "board-column";
  section.style.setProperty("--column-color", "#64757a");
  section.innerHTML = `
    <header class="column-header"><div><span class="column-dot"></span><h2>Archived</h2></div><span class="column-count">${cards.length}</span></header>
    <div class="column-cards" role="list"></div>`;
  const list = section.querySelector(".column-cards");
  if (!cards.length) list.append(emptyMessage("No archived cards."));
  for (const card of cards) {
    const article = document.createElement("article");
    article.className = "kanban-card";
    article.innerHTML = `
      <div class="card-topline"><span class="priority" data-priority="${attribute(card.priority)}">${escapeHtml(card.priority)}</span><span class="kind-badge">${escapeHtml(card.kind)}</span></div>
      <h3>${escapeHtml(card.title)}</h3>
      <button class="card-primary-action" type="button">Restore to Inbox</button>`;
    article.querySelector("button").addEventListener("click", async () => {
      await runMutation("restoreCard", { cardId: card.id });
    });
    list.append(article);
  }
  elements.board.replaceChildren(section);
}

function cardMatchesFilters(card) {
  const filters = state.filters;
  const searchText = `${card.title} ${card.description} ${card.assignee}`.toLowerCase();
  return (
    (!filters.query || searchText.includes(filters.query)) &&
    (!filters.priority || card.priority === filters.priority) &&
    (!filters.assignee || card.assignee.toLowerCase().includes(filters.assignee.toLowerCase())) &&
    (!filters.columnId || card.columnId === filters.columnId) &&
    (!filters.kind || card.kind === filters.kind) &&
    (!filters.turnStatus || card.turnStatus === filters.turnStatus) &&
    (!filters.attention || card.attention === filters.attention) &&
    (!filters.origin || JSON.stringify(card.provenance).includes(filters.origin)) &&
    (!filters.blocked || card.columnId === "blocked")
  );
}

function renderCard(card, columnIndex) {
  const article = document.createElement("article");
  article.className = "kanban-card";
  article.dataset.cardId = card.id;
  article.dataset.attention = card.attention;
  article.draggable = !state.readOnly;
  article.tabIndex = 0;
  article.setAttribute("role", "listitem");
  const action = cardAction(card);
  article.innerHTML = `
    <div class="card-topline">
      <div class="card-badges">
        <span class="priority" data-priority="${attribute(card.priority)}">${escapeHtml(card.priority)}</span>
        <span class="kind-badge">${escapeHtml(card.kind)}</span>
        ${card.recurring ? '<span class="recurring-badge" title="Recurring topic monitor">↻</span>' : ""}
      </div>
      <span class="card-assignee">${escapeHtml(card.assignee || "Unassigned")}</span>
    </div>
    <h3>${escapeHtml(card.title)}</h3>
    <p class="card-description">${escapeHtml(excerpt(card.description, 142) || "Add intent and context.")}</p>
    ${card.latestOutputPreview ? `<div class="latest-preview"><strong>Latest result</strong>${escapeHtml(excerpt(card.latestOutputPreview, 130))}</div>` : ""}
    ${attentionCue(card)}
    <div class="card-progress" aria-label="${card.planDone} of ${card.planCount} plan steps complete">
      <i style="width:${card.planCount ? Math.round((card.planDone / card.planCount) * 100) : 0}%"></i>
    </div>
    <footer class="card-footer">
      <span>☷ ${card.planCount ? `${card.planDone}/${card.planCount} steps` : "No plan"}</span>
      <span>${card.dependencyCount ? `⌁ ${card.dependencyCount}` : ""}</span>
      <span>${card.outputCount ? `▧ ${card.outputCount}` : "No outputs"}</span>
    </footer>
    <button class="card-primary-action" type="button">${escapeHtml(action.label)}</button>
    <div class="card-move-actions" aria-label="Move card with buttons">
      <button type="button" data-direction="-1" ${columnIndex === 0 ? "disabled" : ""} aria-label="Move ${escapeHtml(card.title)} left">←</button>
      <button type="button" data-direction="1" ${columnIndex === state.snapshot.columns.length - 1 ? "disabled" : ""} aria-label="Move ${escapeHtml(card.title)} right">→</button>
    </div>
  `;
  article.addEventListener("click", (event) => {
    if (event.target.closest(".card-move-actions")) return;
    const tab = event.target.closest(".card-primary-action") ? action.tab : "overview";
    openCardDetail(card.id, tab);
  });
  article.addEventListener("keydown", async (event) => {
    if (event.target.closest("button")) return;
    if ((event.key === "Enter" || event.key === " ") && !event.altKey) {
      event.preventDefault();
      openCardDetail(card.id, "overview");
    }
    if (event.altKey && ["ArrowLeft", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
      await moveAdjacent(card.id, event.key === "ArrowRight" ? 1 : -1);
      requestAnimationFrame(() => elements.board.querySelector(`[data-card-id="${CSS.escape(card.id)}"]`)?.focus());
    }
    if (event.altKey && ["ArrowUp", "ArrowDown"].includes(event.key)) {
      event.preventDefault();
      await reorderCard(card, event.key === "ArrowDown" ? 1 : -1);
    }
  });
  article.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/ai-kanban-card", card.id);
    event.dataTransfer.effectAllowed = "move";
    article.classList.add("is-dragging");
  });
  article.addEventListener("dragend", () => {
    article.classList.remove("is-dragging");
    elements.board.querySelectorAll(".is-drop-target").forEach((target) => target.classList.remove("is-drop-target"));
  });
  article.addEventListener("dragover", (event) => {
    if (!state.readOnly) event.preventDefault();
  });
  article.addEventListener("drop", async (event) => {
    event.preventDefault();
    event.stopPropagation();
    const cardId = event.dataTransfer.getData("text/ai-kanban-card");
    if (cardId && cardId !== card.id) {
      await moveCard(cardId, card.columnId, card.id);
    }
  });
  article.querySelectorAll("[data-direction]").forEach((button) => {
    button.addEventListener("click", async () => moveAdjacent(card.id, Number(button.dataset.direction)));
  });
  return article;
}

function attentionCue(card) {
  const values = {
    needs_you: ["!", "Needs you"],
    ai_working: ["◌", card.turnStatus ? `AI ${card.turnStatus.replace("_", " ")}` : "AI working"],
    ai_updated: ["✦", "AI updated"],
  };
  if (!values[card.attention]) return "";
  return `<div class="attention-cue" data-attention="${attribute(card.attention)}"><span aria-hidden="true">${escapeHtml(values[card.attention][0])}</span>${escapeHtml(values[card.attention][1])}</div>`;
}

function cardAction(card) {
  if (card.turnStatus === "needs_input") return { label: "Answer agent", tab: "turns" };
  if (card.attention === "ai_updated") return { label: "Review update", tab: "outputs" };
  if (card.turnStatus) return { label: "View active turn", tab: "turns" };
  if (card.decisionPhase === "needs_feedback") return { label: "Review options", tab: "decision" };
  return { label: "Open workspace", tab: "overview" };
}

async function moveAdjacent(cardId, direction) {
  const card = state.snapshot.cards.find((item) => item.id === cardId);
  const index = state.snapshot.columns.findIndex((column) => column.id === card?.columnId);
  const target = state.snapshot.columns[index + direction];
  if (target) await moveCard(cardId, target.id);
}

async function reorderCard(card, direction) {
  const siblings = state.snapshot.cards.filter((item) => item.columnId === card.columnId);
  const index = siblings.findIndex((item) => item.id === card.id);
  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= siblings.length) return;
  const beforeCardId = direction < 0
    ? siblings[targetIndex].id
    : siblings[targetIndex + 1]?.id || null;
  await runMutation("moveCard", { cardId: card.id, columnId: card.columnId, beforeCardId });
}

async function moveCard(cardId, columnId, beforeCardId = null) {
  const card = state.snapshot.cards.find((item) => item.id === cardId);
  const parameters = { cardId, columnId, beforeCardId };
  if (card?.columnId === "done" && columnId === "inbox") {
    if (!window.confirm("Run this card again? A fresh queued turn will be linked to its last successful turn.")) return;
    parameters.confirmRunAgain = true;
  }
  await runMutation("moveCard", parameters);
}

function openCardComposer(columnId = "inbox") {
  if (state.readOnly) return;
  elements.cardComposerForm.reset();
  elements.composerColumn.value = columnId;
  elements.cardComposerForm.querySelectorAll(".recurring-field").forEach((field) => {
    field.hidden = true;
  });
  elements.cardComposerDialog.showModal();
  elements.cardComposerForm.elements.title.focus();
}

async function createCard(event) {
  event.preventDefault();
  if (!elements.cardComposerForm.reportValidity()) return;
  const form = new FormData(elements.cardComposerForm);
  const result = await runMutation("createCard", {
    title: form.get("title"),
    description: form.get("description"),
    kind: form.get("kind"),
    columnId: form.get("columnId"),
    priority: form.get("priority"),
    assignee: form.get("assignee"),
    recurring: form.get("recurring") === "on",
    cadence: form.get("cadence"),
    lookbackWindow: form.get("lookbackWindow"),
    decision: form.get("decision") === "on",
    origin: "human",
  });
  if (result) {
    elements.cardComposerDialog.close();
    await openCardDetail(result.cardId, "overview");
  }
}

async function openCardDetail(cardId, tab = "overview") {
  setLoading(true, "Opening card workspace…");
  try {
    state.selectedCard = await queryRepository().card(cardId);
    state.selectedTab = validTabForCard(tab);
    renderCardDetail();
    elements.cardDetailDialog.showModal();
  } catch (error) {
    handleActionError(error);
  } finally {
    setLoading(false);
  }
}

async function refreshSelectedCard() {
  if (!state.selectedCard) return;
  state.selectedCard = await queryRepository().card(state.selectedCard.id);
  state.selectedTab = validTabForCard(state.selectedTab);
  renderCardDetail();
}

function validTabForCard(tab) {
  if (tab === "decision" && !state.selectedCard?.decision) return "overview";
  if (tab === "memory" && !state.selectedCard?.recurring) return "overview";
  return tab;
}

function renderCardDetail() {
  const card = state.selectedCard;
  elements.detailBreadcrumb.innerHTML = `
    <span>${escapeHtml(card.columnTitle)}</span><span aria-hidden="true">›</span><span>${escapeHtml(card.kind)}</span>`;
  elements.detailTitle.textContent = card.title;
  elements.detailMeta.innerHTML = `
    <span class="priority" data-priority="${attribute(card.priority)}">${escapeHtml(card.priority)}</span>
    <span class="meta-pill">◎ ${escapeHtml(card.assignee || "Unassigned")}</span>
    ${card.recurring ? `<span class="meta-pill">↻ ${escapeHtml(card.cadence || "Recurring")}</span>` : ""}
    <span class="meta-pill">Updated ${escapeHtml(relativeTime(card.updatedAt))}</span>`;
  elements.detailTabs.querySelectorAll("[data-tab]").forEach((button) => {
    const hidden = (button.dataset.tab === "decision" && !card.decision) ||
      (button.dataset.tab === "memory" && !card.recurring);
    button.hidden = hidden;
    button.setAttribute("aria-selected", String(button.dataset.tab === state.selectedTab));
    button.tabIndex = button.dataset.tab === state.selectedTab ? 0 : -1;
  });
  renderSelectedTab();
  const active = card.turns.find((turn) => ["queued", "claimed", "running", "needs_input", "review"].includes(turn.status));
  elements.readyForAgentButton.hidden = Boolean(active) || state.readOnly;
  elements.readyForAgentButton.textContent = card.turns.some((turn) => ["complete", "failed", "cancelled"].includes(turn.status))
    ? "Run again"
    : "Ready for agent";
  elements.cancelTurnButton.hidden = !active || state.readOnly;
  elements.archiveCardButton.disabled = state.readOnly;
  elements.publishResultButton.disabled =
    state.readOnly || !latestSuccessfulOutput(card);
}

function selectDetailTab(tab) {
  state.selectedTab = validTabForCard(tab);
  elements.detailTabs.querySelectorAll("[data-tab]").forEach((button) => {
    const selected = button.dataset.tab === state.selectedTab;
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  renderSelectedTab();
}

function renderSelectedTab() {
  const renderers = {
    overview: renderOverview,
    plan: renderPlan,
    decision: renderDecision,
    turns: renderTurns,
    outputs: renderOutputs,
    memory: renderMemory,
    activity: renderActivity,
  };
  elements.detailBody.replaceChildren(renderers[state.selectedTab]());
  elements.detailBody.scrollTop = 0;
}

function renderOverview() {
  const card = state.selectedCard;
  const wrapper = div("detail-grid");
  const main = div("");
  const description = sectionElement("Intent and context", "The durable instruction for this workspace.");
  const markdown = div("markdown");
  markdown.innerHTML = renderMarkdown(card.description || "No description yet.");
  description.append(markdown);
  const descriptionActions = div("section-actions");
  descriptionActions.append(actionButton("Edit card", editSelectedCard, "button-quiet"));
  description.append(descriptionActions);
  main.append(description);
  const latestOutput = latestSuccessfulOutput(card);
  if (latestOutput) {
    const latest = sectionElement("Latest successful result", "Featured output; complete history stays in Outputs.");
    latest.append(renderSurface(latestOutput, { compact: true }));
    main.append(latest);
  }
  const side = div("");
  const facts = sectionElement("Workspace facts", "Current snapshot");
  facts.append(definitionList({
    "Column": card.columnTitle,
    "Kind": capitalize(card.kind),
    "Priority": card.priority,
    "Assignee": card.assignee || "Unassigned",
    "Plan": `${card.plan.filter((item) => item.state === "done").length}/${card.plan.length} complete`,
    "Turns": String(card.turns.length),
    "Outputs": String(card.outputs.length),
    "Last actor": card.lastChangeActor,
  }));
  side.append(facts);
  const dependencies = sectionElement("Dependencies", "Done is blocked until dependencies are complete.");
  const dependencyList = div("");
  if (card.dependencies.length) {
    const list = document.createElement("ul");
    for (const item of card.dependencies) {
      const row = document.createElement("li");
      row.append(document.createTextNode(
        `${item.title} · ${item.columnId.replace("_", " ")}`,
      ));
      if (!state.readOnly) {
        row.append(actionButton(
          "Remove",
          () => removeDependency(item),
          "button-quiet",
        ));
      }
      list.append(row);
    }
    dependencyList.append(list);
  } else {
    dependencyList.append(emptyMessage("No dependencies."));
  }
  dependencies.append(dependencyList);
  if (!state.readOnly) {
    const dependencyActions = div("section-actions");
    dependencyActions.append(actionButton("Add dependency", addDependency, "button-quiet"));
    dependencies.append(dependencyActions);
  }
  side.append(dependencies);
  const provenance = sectionElement("Provenance", "Where this card came from.");
  provenance.append(definitionList({
    "Origin": card.provenance.origin || "Unknown",
    "Source": card.provenance.source || "Workspace",
    "Created": formatDate(card.createdAt),
    "Updated": formatDate(card.updatedAt),
  }));
  side.append(provenance);
  const handoff = sectionElement("AI handoff", "Use any provider without uploading workspace bytes automatically.");
  const handoffActions = div("section-actions");
  handoffActions.append(actionButton("Export context", () => openHandoff(card.id), "button-quiet"));
  handoff.append(handoffActions);
  side.append(handoff);
  wrapper.append(main, side);
  return wrapper;
}

function renderPlan() {
  const card = state.selectedCard;
  const section = sectionElement("Plan", "Explicit steps preserve progress independently of agent turns.");
  section.querySelector(".detail-section-header").append(actionButton("＋ Add step", addPlanItem, "button-quiet"));
  const list = div("plan-list");
  if (!card.plan.length) list.append(emptyMessage("No plan yet. Add the first concrete step."));
  for (const item of card.plan) {
    const row = div("plan-row");
    const select = document.createElement("select");
    select.setAttribute("aria-label", `Status for ${item.text}`);
    for (const status of ["pending", "active", "done", "skipped", "blocked", "failed"]) {
      const option = document.createElement("option");
      option.value = status;
      option.textContent = status.replace("_", " ");
      option.selected = item.state === status;
      select.append(option);
    }
    select.disabled = state.readOnly;
    select.addEventListener("change", async () => {
      await runMutation("updatePlanItem", {
        cardId: card.id,
        planItemId: item.id,
        text: item.text,
        state: select.value,
      }, { refreshDetail: true });
    });
    const text = document.createElement("span");
    text.textContent = item.text;
    const updated = document.createElement("small");
    updated.className = "plan-state";
    updated.textContent = relativeTime(item.updatedAt);
    row.append(select, text, updated);
    list.append(row);
  }
  section.append(list);
  return section;
}

function renderDecision() {
  const decision = state.selectedCard.decision;
  const wrapper = div("");
  const phaseSection = sectionElement("Decision loop", "Explore broadly, ask what matters, commit once, then do deep work.");
  const phases = ["briefing", "exploring", "needs_feedback", "committed", "deep_work", "review", "accepted"];
  const track = div("phase-track");
  for (const phase of phases) {
    const item = document.createElement("span");
    item.textContent = phase.replace("_", " ");
    item.classList.toggle("is-current", decision.phase === phase);
    track.append(item);
  }
  phaseSection.append(track);
  const briefingHeader = div("detail-section-header");
  briefingHeader.innerHTML = "<div><h3>Briefing</h3><p>Goals, constraints, preferences, and unknowns stay editable.</p></div>";
  briefingHeader.append(actionButton("Edit briefing", editBriefing, "button-quiet"));
  phaseSection.append(briefingHeader);
  const briefingGrid = div("briefing-grid");
  for (const [key, value] of Object.entries(decision.briefing)) {
    const item = div("briefing-item");
    item.innerHTML = `<strong>${escapeHtml(capitalize(key))}</strong><p>${escapeHtml(value || "Not specified")}</p>`;
    briefingGrid.append(item);
  }
  phaseSection.append(briefingGrid);
  if (decision.phase === "briefing") {
    const actions = div("section-actions");
    actions.append(actionButton("Mark briefing ready for agent", () => changeDecisionPhase("exploring"), "button-primary"));
    phaseSection.append(actions);
  }
  if (decision.phase === "review") {
    const actions = div("section-actions");
    actions.append(
      actionButton("Accept proposal", () => changeDecisionPhase("accepted"), "button-primary"),
      actionButton("Request revision", requestDecisionRevision, "button-quiet"),
    );
    phaseSection.append(actions);
  }
  if (decision.phase === "accepted") {
    const accepted = document.createElement("p");
    accepted.className = "status-surface";
    accepted.textContent = "Accepted. The complete decision and turn history remains available.";
    phaseSection.append(accepted);
  }
  wrapper.append(phaseSection);

  const optionsSection = sectionElement("Options and feedback", "Alternatives remain visible with evidence, fit, tradeoffs, uncertainty, and practical constraints.");
  optionsSection.querySelector(".detail-section-header").append(actionButton("＋ Add option", addDecisionOption, "button-quiet"));
  const list = div("option-list");
  if (!decision.options.length) list.append(emptyMessage("No options yet. Exploration should test credible alternatives."));
  for (const option of decision.options) {
    const article = document.createElement("article");
    article.className = "option-card";
    article.dataset.status = option.status;
    article.innerHTML = `
      <header><h4>${escapeHtml(option.title)}</h4><span class="status-label">${escapeHtml(option.status)}</span></header>
      <p>${escapeHtml(option.summary)}</p>
      <div class="option-criteria">
        <div><strong>Evidence</strong><span>${escapeHtml(option.evidence || "Not recorded")}</span></div>
        <div><strong>Fit</strong><span>${escapeHtml(option.fit || "Not recorded")}</span></div>
        <div><strong>Tradeoffs</strong><span>${escapeHtml(option.tradeoffs || "Not recorded")}</span></div>
        <div><strong>Uncertainty</strong><span>${escapeHtml(option.uncertainty || "Not recorded")}</span></div>
      </div>`;
    const actions = div("section-actions");
    if (option.status === "rejected") {
      actions.append(actionButton("Restore", () => feedbackOption(option, "restore"), "button-quiet"));
    } else {
      actions.append(
        actionButton("Shortlist", () => feedbackOption(option, "shortlist"), "button-quiet"),
        actionButton("Add note", () => feedbackOption(option, "note"), "button-quiet"),
        actionButton("Reject", () => feedbackOption(option, "reject"), "danger-button"),
        actionButton(
          decision.selectedOptionId === option.id ? "Selected" : "Select for deep work",
          () => selectDecisionGate(option),
          decision.selectedOptionId === option.id ? "button-quiet" : "button-primary",
        ),
      );
    }
    article.append(actions);
    list.append(article);
  }
  optionsSection.append(list);
  wrapper.append(optionsSection);
  if (decision.feedback.length) {
    const feedback = sectionElement("Feedback history", "Append-only ranking, shortlist, rejection, restoration, and notes.");
    const activity = document.createElement("ol");
    activity.className = "activity-list";
    for (const item of [...decision.feedback].reverse()) {
      const option = decision.options.find((candidate) => candidate.id === item.optionId);
      activity.append(activityRow({
        actor: item.actor,
        summary: `${capitalize(item.action)} · ${option?.title || "Decision"}`,
        createdAt: item.createdAt,
      }));
    }
    feedback.append(activity);
    wrapper.append(feedback);
  }
  return wrapper;
}

function renderTurns() {
  const card = state.selectedCard;
  const section = sectionElement("Execution turns", "Each bounded attempt has an immutable instruction snapshot and lifecycle.");
  const list = div("turn-list");
  if (!card.turns.length) list.append(emptyMessage("No turns yet. Initial placement never runs work automatically."));
  for (const turn of card.turns) {
    const article = document.createElement("article");
    article.className = "turn-card";
    article.innerHTML = `
      <header><h4>Turn ${escapeHtml(turn.displayNumber)} · ${escapeHtml(turn.trigger.replaceAll("_", " "))}</h4><span class="status-label" data-status="${attribute(turn.status)}">${escapeHtml(turn.status.replace("_", " "))}</span></header>
      <p>${escapeHtml(turn.instructionSnapshot)}</p>
      <p><strong>Actor:</strong> ${escapeHtml(turn.actor || "Unclaimed")} · <strong>Queued:</strong> ${escapeHtml(formatDate(turn.queuedAt))}</p>
      ${turn.result ? `<div class="markdown">${renderMarkdown(turn.result)}</div>` : ""}
      ${turn.error ? `<p class="unsafe-content">${escapeHtml(turn.error)}</p>` : ""}
      ${turn.cancellationReason ? `<p class="unsafe-content">${escapeHtml(turn.cancellationReason)}</p>` : ""}`;
    if (turn.checkpoints.length) {
      const list = document.createElement("ul");
      list.className = "checkpoint-list";
      for (const checkpoint of turn.checkpoints) {
        const item = document.createElement("li");
        item.textContent = `${checkpoint.summary}${checkpoint.progress != null ? ` · ${checkpoint.progress}%` : ""}`;
        list.append(item);
      }
      article.append(list);
    }
    for (const question of turn.questions) {
      const questionCard = div("question-card");
      questionCard.innerHTML = `<strong>${escapeHtml(question.question)}</strong><span>${escapeHtml(question.answer || question.context || "Awaiting your answer")}</span>`;
      if (question.status === "open" && !state.readOnly) {
        questionCard.append(actionButton("Answer", () => answerQuestion(question), "button-quiet"));
      }
      article.append(questionCard);
    }
    list.append(article);
  }
  section.append(list);
  return section;
}

function renderOutputs() {
  const card = state.selectedCard;
  const section = sectionElement("Outputs and history", "Typed surfaces render safely; complete versions remain ordered and inspectable.");
  section.querySelector(".detail-section-header").append(actionButton("＋ Add output", addOutput, "button-quiet"));
  const list = div("output-list");
  if (!card.outputs.length) list.append(emptyMessage("No outputs yet. Capture a result, status, link, program, table, diff, image, or file."));
  for (const output of card.outputs) {
    const surface = renderSurface(output);
    const versions = card.outputVersions[output.id] || [];
    if (versions.length > 1) {
      const details = document.createElement("details");
      details.className = "advanced-details";
      details.innerHTML = `<summary>${versions.length} dated versions</summary>`;
      for (const version of versions) {
        const item = document.createElement("p");
        item.textContent = `v${version.version} · ${formatDate(version.createdAt)} · ${version.status}`;
        details.append(item);
      }
      surface.append(details);
    }
    if (output.type === "diff" && output.status !== "approved" && !state.readOnly) {
      surface.querySelector(".surface-actions")?.append(
        actionButton("Approve diff", () => approveOutput(output), "button-primary"),
      );
    }
    list.append(surface);
  }
  section.append(list);
  return section;
}

function renderMemory() {
  const card = state.selectedCard;
  const wrapper = div("");
  const cycles = sectionElement("Research cycles", `${card.cadence || "Recurring"} · lookback ${card.lookbackWindow || "not set"}`);
  if (!card.cycles.length) cycles.append(emptyMessage("No completed research cycle yet."));
  for (const cycle of card.cycles) {
    const article = document.createElement("article");
    article.className = "cycle-card";
    article.innerHTML = `
      <h4>Cycle ${escapeHtml(cycle.cycleNumber)} · ${escapeHtml(cycle.topic)}</h4>
      <dl>
        <div><dt>Coverage</dt><dd>${escapeHtml(cycle.coverage)}</dd></div>
        <div><dt>Gaps</dt><dd>${escapeHtml(cycle.gaps || "None recorded")}</dd></div>
        <div><dt>New findings</dt><dd>${escapeHtml(cycle.newFindings)}</dd></div>
        <div><dt>Retained context</dt><dd>${escapeHtml(cycle.retainedContext)}</dd></div>
      </dl>`;
    cycles.append(article);
  }
  wrapper.append(cycles);
  const memory = sectionElement("Durable research memory", "Inspectable evidence memory; corrections never rewrite historical reports.");
  const list = div("memory-list");
  if (!card.memory.length) list.append(emptyMessage("No retained memory yet."));
  for (const item of card.memory) {
    const article = document.createElement("article");
    article.className = "memory-card";
    const content = div("");
    if (item.state === "forgotten") {
      content.innerHTML = `
        <span class="memory-state">Forgotten</span>
        <h4>Forgotten memory</h4>
        <p>Payload and provenance were removed. Minimal audit timing remains.</p>
        <div class="memory-meta"><span>Forgotten ${escapeHtml(relativeTime(item.lastSeen))}</span></div>`;
    } else {
      content.innerHTML = `
        <span class="memory-state">${item.pinned ? "Pinned · " : ""}${escapeHtml(item.state.replaceAll("_", " "))}</span>
        <h4>${escapeHtml(item.subject)}</h4>
        <p>${escapeHtml(item.summary)}</p>
        <div class="memory-meta"><span>${escapeHtml(item.publisher)}</span><span>Evidence ${escapeHtml(item.evidenceDate)}</span><span>Seen ${escapeHtml(relativeTime(item.lastSeen))}</span></div>`;
    }
    const actions = div("memory-actions");
    if (!state.readOnly && item.state !== "forgotten") {
      actions.append(
        actionButton(item.pinned ? "Pinned" : "Pin", () => memoryAction(item, "pin"), "button-quiet"),
        actionButton("Correct", () => correctMemory(item), "button-quiet"),
        actionButton("Dismiss", () => memoryAction(item, "dismiss"), "button-quiet"),
        actionButton("Forget", () => forgetMemory(item), "danger-button"),
      );
    }
    article.append(content, actions);
    list.append(article);
  }
  memory.append(list);
  wrapper.append(memory);
  return wrapper;
}

function renderActivity() {
  const section = sectionElement("Activity", "Append-only audit history stays separate from current snapshots.");
  const list = document.createElement("ol");
  list.className = "activity-list";
  if (!state.selectedCard.activity.length) list.append(emptyMessage("Activity will appear as the workspace changes.", "li"));
  for (const event of state.selectedCard.activity) list.append(activityRow(event));
  section.append(list);
  return section;
}

function activityRow(event) {
  const item = document.createElement("li");
  item.className = "activity-row";
  item.dataset.actorKind = /agent|ai/i.test(event.actor || "") ? "ai" : "human";
  item.innerHTML = `
    <i aria-hidden="true"></i>
    <div><strong>${escapeHtml(event.summary)}</strong><span>${escapeHtml(event.actor || "System")} · ${escapeHtml(event.type || "activity")}</span></div>
    <time datetime="${escapeHtml(event.createdAt)}">${escapeHtml(relativeTime(event.createdAt))}</time>`;
  return item;
}

async function archiveCard() {
  if (!state.selectedCard || !window.confirm("Archive this card? Its history remains durable and restorable.")) return;
  const result = await runMutation("archiveCard", { cardId: state.selectedCard.id });
  if (result) {
    elements.cardDetailDialog.close();
    state.selectedCard = null;
  }
}

async function publishResult() {
  const card = state.selectedCard;
  const latest = latestSuccessfulOutput(card);
  if (!latest) return;
  const result = await runMutation("createCard", {
    title: `${card.title} · published result`,
    description: latest.content,
    priority: card.priority,
    assignee: card.assignee,
    kind: "result",
    columnId: "done",
    origin: "published-result",
    source: card.id,
  });
  if (result) showToast("A result card was published to Done.", "success");
}

async function readyForAgent() {
  const card = state.selectedCard;
  const terminal = card.turns.find((turn) => ["complete", "failed", "cancelled"].includes(turn.status));
  const result = await runMutation("queueTurn", {
    cardId: card.id,
    instruction: card.description || card.title,
    trigger: terminal ? "run_again" : "ready_for_agent",
    linkedTurnId: terminal?.id || null,
    idempotencyKey: crypto.randomUUID(),
  }, { refreshDetail: true });
  if (result) selectDetailTab("turns");
}

async function cancelActiveTurn() {
  const turn = state.selectedCard.turns.find((item) => ["queued", "claimed", "running", "needs_input", "review"].includes(item.status));
  if (!turn) return;
  openGenericDialog({
    eyebrow: "Retain partial work",
    title: `Cancel turn ${turn.displayNumber}?`,
    submit: "Cancel turn",
    fields: `<label class="field field-wide"><span>Reason</span><textarea name="reason" required rows="4"></textarea></label>`,
    action: async (form) => Boolean(await runMutation("transitionTurn", {
      turnId: turn.id,
      status: "cancelled",
      reason: form.get("reason"),
    }, { refreshDetail: true })),
  });
}

function editSelectedCard() {
  const card = state.selectedCard;
  openGenericDialog({
    eyebrow: "Current snapshot",
    title: "Edit card",
    submit: "Save changes",
    fields: `
      <label class="field field-wide"><span>Title</span><input name="title" required maxlength="160" value="${attribute(card.title)}"></label>
      <label class="field"><span>Priority</span><select name="priority">${options(["P0", "P1", "P2", "P3"], card.priority)}</select></label>
      <label class="field"><span>Kind</span><select name="kind">${options(["task", "question", "result"], card.kind)}</select></label>
      <label class="field field-wide"><span>Assignee</span><input name="assignee" maxlength="100" value="${attribute(card.assignee)}"></label>
      <label class="field field-wide"><span>Intent and context</span><textarea name="description" rows="8" maxlength="50000">${escapeHtml(card.description)}</textarea></label>
      <label class="check-field"><input name="recurring" type="checkbox" ${card.recurring ? "checked" : ""}> <span>Recurring topic monitor</span></label>
      <label class="field"><span>Cadence</span><input name="cadence" value="${attribute(card.cadence)}"></label>
      <label class="field"><span>Lookback</span><input name="lookbackWindow" value="${attribute(card.lookbackWindow)}"></label>`,
    action: async (form) => Boolean(await runMutation("updateCard", {
      cardId: card.id,
      title: form.get("title"),
      description: form.get("description"),
      priority: form.get("priority"),
      kind: form.get("kind"),
      assignee: form.get("assignee"),
      recurring: form.get("recurring") === "on",
      cadence: form.get("cadence"),
      lookbackWindow: form.get("lookbackWindow"),
      attention: card.attention,
    }, { refreshDetail: true })),
  });
}

function addPlanItem() {
  openGenericDialog({
    eyebrow: "Concrete next step",
    title: "Add plan item",
    submit: "Add step",
    fields: `
      <label class="field field-wide"><span>Step</span><input name="text" required maxlength="500"></label>
      <label class="field"><span>State</span><select name="state">${options(["pending", "active", "done", "skipped", "blocked", "failed"], "pending")}</select></label>`,
    action: async (form) => Boolean(await runMutation("addPlanItem", {
      cardId: state.selectedCard.id,
      text: form.get("text"),
      state: form.get("state"),
    }, { refreshDetail: true })),
  });
}

function addDependency() {
  const available = state.snapshot.cards.filter(
    (card) =>
      card.id !== state.selectedCard.id &&
      !state.selectedCard.dependencies.some((dependency) => dependency.id === card.id),
  );
  if (!available.length) {
    showToast("No additional active cards are available as dependencies.", "info");
    return;
  }
  openGenericDialog({
    eyebrow: "Readiness gate",
    title: "Add a dependency",
    submit: "Add dependency",
    fields: `
      <label class="field field-wide"><span>Depends on</span>
        <select name="dependsOnId">${available.map(
          (card) => `<option value="${attribute(card.id)}">${escapeHtml(card.title)} · ${escapeHtml(card.columnId.replace("_", " "))}</option>`,
        ).join("")}</select>
      </label>`,
    action: async (form) => Boolean(await runMutation("addDependency", {
      cardId: state.selectedCard.id,
      dependsOnId: form.get("dependsOnId"),
    }, { refreshDetail: true })),
  });
}

async function removeDependency(dependency) {
  await runMutation("removeDependency", {
    cardId: state.selectedCard.id,
    dependsOnId: dependency.id,
  }, { refreshDetail: true });
}

function editBriefing() {
  const briefing = state.selectedCard.decision.briefing;
  openGenericDialog({
    eyebrow: "Decision briefing",
    title: "What should exploration optimize for?",
    submit: "Save briefing",
    fields: Object.keys({
      goals: "", suggestions: "", constraints: "", preferences: "",
      exclusions: "", bounds: "", criteria: "", unknowns: "",
    }).map((key) => `
      <label class="field ${["goals", "constraints", "criteria"].includes(key) ? "field-wide" : ""}">
        <span>${escapeHtml(capitalize(key))}</span>
        <textarea name="${key}" rows="3">${escapeHtml(briefing[key] || "")}</textarea>
      </label>`).join(""),
    action: async (form) => {
      const value = Object.fromEntries([...form.entries()]);
      return Boolean(await runMutation("saveDecisionBriefing", {
        cardId: state.selectedCard.id,
        briefing: value,
      }, { refreshDetail: true }));
    },
  });
}

function addDecisionOption() {
  openGenericDialog({
    eyebrow: "Credible alternative",
    title: "Add an option",
    submit: "Add option",
    fields: `
      <label class="field field-wide"><span>Option</span><input name="title" required maxlength="200"></label>
      <label class="field field-wide"><span>Summary</span><textarea name="summary" rows="3"></textarea></label>
      <label class="field field-wide"><span>Evidence</span><textarea name="evidence" rows="3"></textarea></label>
      <label class="field"><span>Fit</span><textarea name="fit" rows="3"></textarea></label>
      <label class="field"><span>Tradeoffs</span><textarea name="tradeoffs" rows="3"></textarea></label>
      <label class="field"><span>Uncertainty</span><textarea name="uncertainty" rows="3"></textarea></label>
      <label class="field"><span>Practical constraints</span><textarea name="practicalConstraints" rows="3"></textarea></label>`,
    action: async (form) => Boolean(await runMutation("addDecisionOption", {
      cardId: state.selectedCard.id,
      ...Object.fromEntries([...form.entries()]),
    }, { refreshDetail: true })),
  });
}

function feedbackOption(option, action) {
  if (action === "reject" && !window.confirm(`Reject ${option.title}? It remains restorable in history.`)) return;
  if (action === "restore") {
    runMutation("feedbackDecisionOption", {
      cardId: state.selectedCard.id,
      optionId: option.id,
      action,
    }, { refreshDetail: true });
    return;
  }
  openGenericDialog({
    eyebrow: "Append-only feedback",
    title: `${capitalize(action)} · ${option.title}`,
    submit: "Record feedback",
    fields: `
      ${action === "rank" ? '<label class="field"><span>Rank</span><input name="value" type="number" min="1"></label>' : ""}
      <label class="field field-wide"><span>Note</span><textarea name="note" rows="4" ${action === "note" ? "required" : ""}></textarea></label>`,
    action: async (form) => Boolean(await runMutation("feedbackDecisionOption", {
      cardId: state.selectedCard.id,
      optionId: option.id,
      action,
      value: form.get("value"),
      note: form.get("note"),
    }, { refreshDetail: true })),
  });
}

function selectDecisionGate(option) {
  openGenericDialog({
    eyebrow: "Explicit deep-work gate",
    title: `Commit to ${option.title}`,
    submit: "Confirm selection",
    fields: `
      <div class="caution-note field-wide"><strong>Exploration ends at this gate.</strong><span>Deep work snapshots this option, evidence, feedback, constraints, and unresolved questions.</span></div>
      <label class="field field-wide"><span>Current constraints</span><textarea name="constraints" required rows="4">${escapeHtml(state.selectedCard.decision.briefing.constraints || "")}</textarea></label>
      <label class="field field-wide"><span>Evidence snapshot</span><textarea name="evidence" rows="4">${escapeHtml(option.evidence || "")}</textarea></label>
      <label class="field field-wide"><span>Unresolved questions</span><textarea name="unresolvedQuestions" rows="3">${escapeHtml(state.selectedCard.decision.briefing.unknowns || "")}</textarea></label>`,
    action: async (form) => Boolean(await runMutation("setDecisionGate", {
      cardId: state.selectedCard.id,
      optionId: option.id,
      constraints: form.get("constraints"),
      evidence: form.get("evidence"),
      unresolvedQuestions: form.get("unresolvedQuestions"),
    }, { refreshDetail: true })),
  });
}

function changeDecisionPhase(phase) {
  runMutation("setDecisionPhase", {
    cardId: state.selectedCard.id,
    phase,
  }, { refreshDetail: true });
}

function requestDecisionRevision() {
  openGenericDialog({
    eyebrow: "Preserve review history",
    title: "Request a revision",
    submit: "Queue revision",
    fields: `<label class="field field-wide"><span>Revision instruction</span><textarea name="instruction" required rows="5"></textarea></label>`,
    action: async (form) => {
      const revision = await runMutation("requestDecisionRevision", {
        cardId: state.selectedCard.id,
        instruction: form.get("instruction"),
        idempotencyKey: crypto.randomUUID(),
      }, { refreshDetail: true });
      if (revision) selectDetailTab("turns");
      return Boolean(revision);
    },
  });
}

function answerQuestion(question) {
  openGenericDialog({
    eyebrow: "Resume this turn",
    title: question.question,
    submit: "Answer and resume",
    fields: `<label class="field field-wide"><span>Your answer</span><textarea name="answer" required rows="5"></textarea></label>`,
    action: async (form) => Boolean(await runMutation("answerQuestion", {
      questionId: question.id,
      answer: form.get("answer"),
    }, { refreshDetail: true })),
  });
}

function addOutput() {
  openGenericDialog({
    eyebrow: "Typed output surface",
    title: "Capture an output",
    submit: "Add output",
    fields: `
      <label class="field"><span>Type</span><select name="type">${options(["text", "status", "link", "program", "table", "diff", "image", "file"], "text")}</select></label>
      <label class="field"><span>Status</span><select name="status">${options(["draft", "complete", "failed", "stale", "approved"], "complete")}</select></label>
      <label class="field field-wide"><span>Title</span><input name="title" required maxlength="200"></label>
      <label class="field field-wide"><span>Payload or reference</span><textarea name="content" rows="9" placeholder="Text, code, URL, JSON rows, diff, or safe file metadata"></textarea></label>
      <label class="field field-wide"><span>Alt text (images)</span><input name="altText" maxlength="500"></label>`,
    action: async (form) => Boolean(await runMutation("addOutput", {
      cardId: state.selectedCard.id,
      ...Object.fromEntries([...form.entries()]),
      source: "human",
    }, { refreshDetail: true })),
  });
}

function approveOutput(output) {
  runMutation("approveOutput", {
    outputId: output.id,
  }, { refreshDetail: true });
}

function memoryAction(item, action, extra = {}) {
  return runMutation("memoryAction", {
    cardId: state.selectedCard.id,
    memoryId: item.id,
    action,
    ...extra,
  }, { refreshDetail: true });
}

function correctMemory(item) {
  openGenericDialog({
    eyebrow: "Correction with lineage",
    title: item.subject,
    submit: "Save correction",
    fields: `<label class="field field-wide"><span>Corrected summary</span><textarea name="summary" required rows="6">${escapeHtml(item.summary)}</textarea></label>`,
    action: async (form) => Boolean(await memoryAction(item, "correct", {
      summary: form.get("summary"),
    })),
  });
}

function forgetMemory(item) {
  if (!window.confirm("Forget this retained memory? Historical reports remain unchanged.")) return;
  memoryAction(item, "forget");
}

function openFilters() {
  for (const [key, value] of Object.entries(state.filters)) {
    if (key === "query" || key === "priority") continue;
    const field = elements.filtersForm.elements[key];
    if (!field) continue;
    if (field.type === "checkbox") field.checked = Boolean(value);
    else field.value = value;
  }
  elements.filtersDialog.showModal();
}

function applyFilters(event) {
  event.preventDefault();
  const form = new FormData(elements.filtersForm);
  for (const key of ["assignee", "columnId", "kind", "turnStatus", "attention", "origin"]) {
    state.filters[key] = form.get(key) || "";
  }
  state.filters.blocked = form.get("blocked") === "on";
  state.filters.archived = form.get("archived") === "on";
  updateFilterCount();
  elements.filtersDialog.close();
  renderBoard();
}

function clearFilters() {
  const query = state.filters.query;
  resetFilters();
  state.filters.query = query;
  elements.searchInput.value = query;
  elements.filtersForm.reset();
  updateFilterCount();
  elements.filtersDialog.close();
  renderBoard();
}

function resetFilters() {
  Object.assign(state.filters, {
    query: "", priority: "", assignee: "", columnId: "", kind: "",
    turnStatus: "", attention: "", origin: "", blocked: false, archived: false,
  });
  if (elements.searchInput) elements.searchInput.value = "";
  elements.quickFilters?.querySelectorAll("[data-priority]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.priority === ""));
  });
  updateFilterCount();
}

function activeFilterCount() {
  return Object.entries(state.filters).filter(([key, value]) => key !== "query" && Boolean(value)).length;
}

function updateFilterCount() {
  const count = activeFilterCount();
  elements.activeFilterCount.textContent = count;
  elements.activeFilterCount.hidden = count === 0;
}

function populateColumnSelects() {
  for (const select of [elements.composerColumn, elements.filterColumn]) {
    const initial = select === elements.filterColumn
      ? [new Option("Any column", "")]
      : [];
    select.replaceChildren(
      ...initial,
      ...state.snapshot.columns.map((column) => new Option(column.title, column.id)),
    );
  }
}

function setupCoordination() {
  state.coordination?.stop();
  state.coordination = new CoordinationService(state.workspace, state.snapshot.meta.workspace_id);
  state.coordination.addEventListener("status", ({ detail }) => {
    state.agent = detail.agents.sort(
      (left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp),
    )[0] || null;
    updateAgentStatus();
    if (state.agent?.status === "manifest_publication_failed") {
      const command =
        `python .agents/skills/ai-kanban/ai_kanban.py reconcile-manifest ` +
        `--actor ${shellQuote(state.agent.actor_id)} ` +
        `--run-id ${shellQuote(state.agent.run_id)}`;
      setWorkspaceAlert(
        "SQLite committed, but manifest publication failed. Verify the recovery marker, then reconcile the manifest before reloading.",
        "error",
        [["Copy reconciliation command", async () => {
          await navigator.clipboard.writeText(command);
          showToast("Reconciliation command copied.", "success");
        }]],
      );
    } else if (state.detachedForAgent && isYieldAcknowledgement(state.agent)) {
      setWorkspaceAlert(
        "The agent yielded a final durable revision. Verify it before accepting returned control.",
        "warning",
        [["Accept returned control", () => acceptYieldedControl(state.agent)]],
      );
    } else if (
      state.detachedForAgent &&
      state.agent &&
      Number(state.agent.observed_revision) > Number(state.snapshot.meta.revision)
    ) {
      setWorkspaceAlert(
        "The agent published a newer durable revision. Reload after it yields the writer baton.",
        "warning",
        [["Reload agent changes", reloadAgentChanges]],
      );
    }
  });
  state.coordination.addEventListener("error", ({ detail }) => {
    elements.agentDiagnostics.textContent = `Coordination read failed: ${detail.message}`;
  });
  state.coordination.start();
}

async function inspectBootstrap() {
  const expected = await loadBootstrapFiles();
  const status = await state.workspace.bootstrapStatus(expected);
  const attention = status.filter((item) => item.state !== "current");
  if (!attention.length) return;
  setWorkspaceAlert(
    `${attention.length} agent bootstrap file${attention.length === 1 ? " needs" : "s need"} review. User-edited files will not be overwritten automatically.`,
    "warning",
    [["Compare", showBootstrapRepair]],
  );
}

async function showBootstrapRepair() {
  hideWorkspaceMenu();
  if (state.workspace?.mode !== "connected") {
    showToast("Agent bootstrap files exist only in connected folder workspaces.", "info");
    return;
  }
  if (state.readOnly || !ownsWorkspaceLock()) {
    showToast("Bootstrap repair requires this tab's writable workspace lock.", "warning");
    return;
  }
  const expected = await loadBootstrapFiles();
  const status = await state.workspace.bootstrapStatus(expected);
  openGenericDialog({
    eyebrow: "Integrity without silent overwrite",
    title: "Agent bootstrap files",
    submit: "Apply selected repairs",
    fields: status.map((item) => `
      <label class="check-field field-wide">
        <input type="checkbox" name="path" value="${attribute(item.path)}" ${item.state === "current" ? "disabled" : ""}>
        <span><strong>${escapeHtml(item.path)}</strong> · ${escapeHtml(item.state)}</span>
      </label>
      ${item.state === "modified" ? `<details class="advanced-details field-wide"><summary>Compare ${escapeHtml(item.path)}</summary><p><strong>Existing</strong></p><pre>${escapeHtml(excerpt(item.actualContent, 1200))}</pre><p><strong>Generated ${escapeHtml(item.expectedContent.includes("Version:") ? "update" : "version")}</strong></p><pre>${escapeHtml(excerpt(item.expectedContent, 1200))}</pre></details>` : ""}`,
    ).join(""),
    action: async (form) => {
      const selected = new Set(form.getAll("path"));
      const repairs = status.map((item) => ({
        ...item,
        state: selected.has(item.path)
          ? item.state === "missing" ? "missing" : "confirmed-replace"
          : item.state,
      }));
      if (state.readOnly || !ownsWorkspaceLock()) {
        throw typedError(
          "WORKSPACE_LOCK_REQUIRED",
          "This tab no longer owns the writable workspace lock.",
        );
      }
      await saveQueue.run(() => state.workspace.repairBootstrap(repairs));
      showToast("Selected agent files repaired.", "success");
      return true;
    },
  });
}

function ownsWorkspaceLock() {
  return Boolean(
    state.workspace?.mode === "connected" &&
    state.lock?.acquired,
  );
}

function queryRepository() {
  return state.readRepository || repository;
}

async function closeReadRepository() {
  if (!state.readRepository) return;
  const current = state.readRepository;
  state.readRepository = null;
  await current.close().catch(() => {});
  current.terminate();
}

function openAgentDialog() {
  renderAgentDialog();
  elements.agentDialog.showModal();
}

function renderAgentDialog() {
  const agent = state.agent;
  const meta = state.snapshot.meta;
  const label = state.workspace.mode !== "connected"
    ? "Connected agents require a folder workspace"
    : agentStateLabel(agent);
  const detail = agent
    ? `${agent.actor_id} · revision ${agent.observed_revision} · ${relativeTime(agent.timestamp)}`
    : "A valid workspace-matched heartbeat has not arrived yet.";
  elements.agentConnectionState.innerHTML = `
    <span class="agent-state-icon" aria-hidden="true">${agent ? "✦" : "◌"}</span>
    <div><strong>${escapeHtml(label)}</strong><span>${escapeHtml(detail)}</span></div>`;
  elements.agentDiagnostics.textContent = JSON.stringify({
    workspaceId: meta.workspace_id,
    protocolVersion: meta.protocol_version,
    revision: Number(meta.revision),
    control: {
      state: meta.control_state,
      holder: meta.control_holder,
      generation: Number(meta.control_generation),
    },
    heartbeat: agent || "waiting",
  }, null, 2);
  const controlState = meta.control_state;
  const ownsLock = ownsWorkspaceLock();
  if (controlState === "human") {
    const grantCandidate = isAgentGrantCandidate(agent, meta);
    elements.agentControlAction.textContent = grantCandidate
      ? "Grant agent control"
      : agent
        ? "Waiting for control request"
        : "Waiting for agent";
    elements.agentControlAction.disabled =
      !grantCandidate || !ownsLock || state.readOnly;
  } else {
    elements.agentControlAction.textContent = isYieldAcknowledgement(agent)
      ? "Accept returned control"
      : "Request control back";
    elements.agentControlAction.disabled = !ownsLock;
  }
  elements.repairFromAgentButton.disabled = !ownsLock || state.readOnly;
}

function updateAgentStatus() {
  const label = agentStateLabel(state.agent);
  elements.agentStatusDot.dataset.state = !state.agent
    ? "waiting"
    : state.agent.stale
      ? "stale"
      : state.agent.current_turn_id
        ? "working"
        : "connected";
  elements.agentButton.title = label;
  if (elements.agentDialog.open) renderAgentDialog();
}

async function handleAgentControl() {
  if (!ownsWorkspaceLock()) {
    showToast("Agent control requires this tab's workspace lock.", "warning");
    return;
  }
  const controlState = state.snapshot.meta.control_state;
  if (controlState === "human") await grantAgentControl();
  else await requestControlBack();
}

async function grantAgentControl() {
  if (!ownsWorkspaceLock() || state.readOnly) {
    showToast("This tab cannot grant control without the writable workspace lock.", "warning");
    return;
  }
  const agent = state.agent;
  if (!isAgentGrantCandidate(agent, state.snapshot.meta)) return;
  if (!window.confirm(`Save, close the browser writer, and grant control to ${agent.actor_id}?`)) return;
  setLoading(true, "Transferring the writer baton…");
  let publicationStarted = false;
  let transferMutationStarted = false;
  try {
    if (state.dirty || saveQueue.pending) await saveNow();
    transferMutationStarted = true;
    let result = await repository.mutate("setControl", {
      state: "granting_agent",
      holderId: "human",
      ownerId: "human",
      incrementGeneration: true,
      leaseUntil: new Date(Date.now() + 90_000).toISOString(),
    });
    state.snapshot = result.snapshot;
    markDirty();
    await saveQueue.flush();
    result = await repository.mutate("setControl", {
      state: "agent",
      holderId: agent.actor_id,
      ownerId: "human",
      incrementGeneration: false,
      leaseUntil: new Date(Date.now() + 90_000).toISOString(),
    });
    state.snapshot = result.snapshot;
    markDirty();
    await saveQueue.flush();
    const grant = {
      generation: Number(state.snapshot.meta.control_generation),
      revision: Number(state.snapshot.meta.revision),
    };
    const readBytes = await repository.exportBytes();
    await closeReadRepository();
    state.readRepository = new BoardRepository();
    await state.readRepository.open(readBytes);
    await repository.close();
    state.detachedForAgent = true;
    state.readOnly = true;
    publicationStarted = true;
    await state.coordination.publishHuman({
      holderId: agent.actor_id,
      generation: grant.generation,
      revision: grant.revision,
      requestedState: "agent",
      note: "Browser writer closed after durable grant.",
    });
    elements.agentDialog.close();
    setWorkspaceAlert(
      `${agent.actor_id} has the writer baton. The browser is read-only until control returns.`,
      "warning",
    );
    updateChrome();
  } catch (error) {
    if (elements.agentDialog.open) elements.agentDialog.close();
    if (!publicationStarted && transferMutationStarted) {
      try {
        await rollbackUnpublishedGrant();
        setWorkspaceAlert(
          "Agent transfer failed before publication. Control was safely rolled back to the human owner.",
          "warning",
        );
      } catch (rollbackError) {
        state.readOnly = true;
        setWorkspaceAlert(
          "Agent transfer and automatic rollback both failed. Keep this tab open and retry the safe rollback; do not start an agent.",
          "error",
          [["Retry safe rollback", rollbackUnpublishedGrant]],
        );
        showToast(userMessage(rollbackError), "error");
      }
    } else if (publicationStarted) {
      state.detachedForAgent = true;
      state.readOnly = true;
      setWorkspaceAlert(
        "The agent grant may already be visible. The browser will not overwrite it. Request control back and wait for a verified final yield.",
        "error",
        [["Request control back", requestControlBack]],
      );
    }
    showToast(userMessage(error), "error");
  } finally {
    setLoading(false);
    updateChrome();
  }
}

async function rollbackUnpublishedGrant() {
  if (!ownsWorkspaceLock()) {
    throw typedError(
      "WORKSPACE_LOCK_REQUIRED",
      "Safe grant rollback requires this tab's workspace lock.",
    );
  }
  if (state.detachedForAgent || !repository.snapshotValue) {
    await closeReadRepository();
    const expectedWorkspaceId = state.snapshot.meta.workspace_id;
    await state.workspace.reloadManifest();
    const bytes = await state.workspace.readState();
    state.snapshot = await openVerifiedWorkspaceBytes(
      bytes,
      state.workspace,
      expectedWorkspaceId,
      true,
    );
    state.detachedForAgent = false;
  }
  const metadata = state.snapshot.meta;
  if (
    metadata.control_state !== "human" ||
    metadata.control_holder !== "human"
  ) {
    const result = await repository.mutate(
      "setControl",
      {
        state: "human",
        holderId: "human",
        ownerId: "human",
        incrementGeneration: true,
        leaseUntil: "",
      },
      { holderId: metadata.control_holder },
    );
    state.snapshot = result.snapshot;
    state.readOnly = false;
    markDirty();
    await saveQueue.flush();
  }
  state.readOnly = !state.lock?.acquired;
  state.dirty = false;
  await state.coordination.publishHuman({
    holderId: "human",
    generation: Number(state.snapshot.meta.control_generation),
    revision: Number(state.snapshot.meta.revision),
    requestedState: "human",
    note: "Unpublished agent grant rolled back safely.",
  });
  updateChrome();
}

async function requestControlBack() {
  if (!ownsWorkspaceLock()) {
    showToast("This tab cannot publish reclamation without the workspace lock.", "warning");
    return;
  }
  const agent = state.agent;
  if (isYieldAcknowledgement(agent)) {
    await acceptYieldedControl(agent);
    return;
  }
  await state.coordination.publishHuman({
    holderId: state.snapshot.meta.control_holder,
    generation: Number(state.snapshot.meta.control_generation),
    revision: Number(state.snapshot.meta.revision),
    requestedState: "reclaim_requested",
    note: "Human reclamation has priority. Commit or roll back, close, publish final revision, and acknowledge.",
  });
  showToast(
    agent?.stale
      ? "The heartbeat is stale, but no overwrite is permitted. Waiting for an acknowledged final yield marker."
      : "Control return requested. Waiting for the agent to commit or roll back, close its writer, and yield.",
    "info",
  );
}

function isYieldAcknowledgement(agent) {
  const metadata = state.snapshot?.meta;
  return Boolean(
    agent &&
    agent.requested_state === "human" &&
    agent.status === "stopped" &&
    agent.holder_id === "human" &&
    !agent.current_turn_id &&
    Number(agent.control_generation) > Number(metadata?.control_generation) &&
    Number(agent.observed_revision) >= Number(metadata?.revision),
  );
}

async function acceptYieldedControl(agent) {
  if (!ownsWorkspaceLock()) {
    showToast("This tab cannot accept returned control without the workspace lock.", "warning");
    return;
  }
  setLoading(true, "Verifying the agent's final revision…");
  try {
    if (!isYieldAcknowledgement(agent)) {
      throw typedError(
        "YIELD_ACKNOWLEDGEMENT_REQUIRED",
        "A valid final yield marker is required before accepting returned control.",
      );
    }
    await waitForJournalStabilization();
    await closeReadRepository();
    const expectedWorkspaceId = state.snapshot.meta.workspace_id;
    await state.workspace.reloadManifest();
    const bytes = await state.workspace.readState();
    const snapshot = await openVerifiedWorkspaceBytes(
      bytes,
      state.workspace,
      expectedWorkspaceId,
      true,
    );
    const health = await repository.health();
    if (!health.ok) {
      throw typedError("INTEGRITY_FAILURE", "The agent's final database failed integrity checks.");
    }
    if (
      snapshot.meta.control_state !== "human" ||
      snapshot.meta.control_holder !== "human" ||
      Number(snapshot.meta.control_generation) !== Number(agent.control_generation) ||
      Number(snapshot.meta.revision) !== Number(agent.observed_revision)
    ) {
      throw typedError(
        "FINAL_MARKER_MISMATCH",
        "The final yield marker does not match durable SQLite control state.",
      );
    }
    state.snapshot = snapshot;
    state.detachedForAgent = false;
    state.readOnly = !state.lock?.acquired;
    state.dirty = false;
    await state.coordination.publishHuman({
      holderId: "human",
      generation: Number(state.snapshot.meta.control_generation),
      revision: Number(state.snapshot.meta.revision),
      requestedState: "human",
      note: "Agent final revision verified; human control accepted.",
    });
    elements.agentDialog.close();
    renderBoard();
  } catch (error) {
    handleActionError(error);
  } finally {
    setLoading(false);
    updateChrome();
  }
}

async function reloadAgentChanges() {
  if (!state.workspace) return;
  setLoading(true, "Stabilizing and checking agent changes…");
  try {
    await waitForJournalStabilization();
    const expectedWorkspaceId = state.snapshot.meta.workspace_id;
    await closeReadRepository();
    await state.workspace.reloadManifest();
    const bytes = await state.workspace.readState();
    const snapshot = await openVerifiedWorkspaceBytes(
      bytes,
      state.workspace,
      expectedWorkspaceId,
      true,
    );
    const health = await repository.health();
    if (!health.ok) throw typedError("INTEGRITY_FAILURE", "Agent changes failed the integrity check.");
    if (snapshot.meta.control_state === "human") {
      if (
        !isYieldAcknowledgement(state.agent) ||
        state.agent.holder_id !== "human" ||
        Number(snapshot.meta.control_generation) !== Number(state.agent.control_generation) ||
        Number(snapshot.meta.revision) !== Number(state.agent.observed_revision)
      ) {
        await repository.close();
        throw typedError(
          "YIELD_ACKNOWLEDGEMENT_REQUIRED",
          "Durable state claims human control without a matching final yield marker.",
        );
      }
    }
    state.snapshot = snapshot;
    state.detachedForAgent = snapshot.meta.control_state === "agent";
    state.readOnly = state.detachedForAgent || !state.lock?.acquired;
    if (state.detachedForAgent) {
      await repository.close();
      state.readRepository = new BoardRepository();
      await state.readRepository.open(bytes);
    }
    else {
      await state.workspace.captureLoadedSignature();
      await state.coordination.publishHuman({
        holderId: "human",
        generation: Number(snapshot.meta.control_generation),
        revision: Number(snapshot.meta.revision),
        requestedState: "human",
        note: "Agent final revision verified; human control accepted.",
      });
    }
    renderBoard();
    updateChrome();
  } catch (error) {
    handleActionError(error);
  } finally {
    setLoading(false);
  }
}

async function waitForJournalStabilization() {
  let prior = null;
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const sidecars = await state.workspace.journalState?.() || [];
    const bytes = await (
      state.workspace.readStateForStabilization?.() ??
      state.workspace.readState()
    );
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const signature = [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
    if (!sidecars.length && signature === prior) return;
    prior = signature;
    await new Promise((resolve) => setTimeout(resolve, 250 * (attempt + 1)));
  }
  throw typedError("JOURNAL_DELAY", "Database bytes did not stabilize. Retry after the agent closes SQLite.");
}

async function copyAgentInstructions() {
  await navigator.clipboard.writeText(elements.agentFallbackText.textContent);
  showToast("Fallback instructions copied.", "success");
}

async function openHandoff(cardId = null) {
  if (!state.snapshot.cards.length) {
    showToast("Create a card before exporting a handoff.", "info");
    return;
  }
  elements.handoffCardSelect.replaceChildren(
    ...state.snapshot.cards.map((card) => new Option(card.title, card.id)),
  );
  elements.handoffCardSelect.value = cardId || state.selectedCard?.id || state.snapshot.cards[0].id;
  elements.handoffImportText.value = "";
  state.pendingImport = null;
  elements.handoffPreview.hidden = true;
  elements.applyImportButton.hidden = true;
  switchHandoffTab("export");
  await refreshHandoff();
  elements.handoffDialog.showModal();
}

async function refreshHandoff() {
  const cardId = elements.handoffCardSelect.value;
  if (!cardId) return;
  try {
    invalidateDirectSend();
    const card = await queryRepository().card(cardId);
    const packet = createHandoffPacket(card);
    elements.handoffExportText.value = state.handoffFormat === "json"
      ? JSON.stringify(packet, null, 2)
      : handoffAsMarkdown(packet);
  } catch (error) {
    handleActionError(error);
  }
}

function switchHandoffTab(tab) {
  document.querySelectorAll("[data-handoff-tab]").forEach((button) => {
    button.setAttribute("aria-selected", String(button.dataset.handoffTab === tab));
  });
  elements.handoffExportPanel.hidden = tab !== "export";
  elements.handoffImportPanel.hidden = tab !== "import";
  elements.handoffDirectPanel.hidden = tab !== "direct";
}

async function copyHandoff() {
  await navigator.clipboard.writeText(elements.handoffExportText.value);
  showToast("Handoff packet copied.", "success");
}

function downloadHandoff() {
  const card = state.snapshot.cards.find((item) => item.id === elements.handoffCardSelect.value);
  downloadText(
    elements.handoffExportText.value,
    `${slug(card?.title)}-handoff.${state.handoffFormat === "json" ? "json" : "md"}`,
    state.handoffFormat === "json" ? "application/json" : "text/markdown",
  );
}

function handoffAsMarkdown(packet) {
  const card = packet.card;
  return [
    `# ${card.title}`,
    "",
    `- Card: \`${card.id}\``,
    `- Priority: ${card.priority}`,
    `- Assignee: ${card.assignee || "Unassigned"}`,
    `- Column: ${card.column}`,
    "",
    "## Intent and context",
    card.description || "No description.",
    "",
    "## Plan",
    ...(card.plan.length ? card.plan.map((item) => `- [${item.status === "done" ? "x" : " "}] ${item.text} (${item.status})`) : ["No plan."]),
    "",
    "## Recent activity",
    ...(card.recentActivity.length ? card.recentActivity.map((item) => `- ${item.createdAt}: ${item.summary} — ${item.actor}`) : ["No recent activity."]),
    "",
    "## Requested response",
    card.requestedResponseShape,
    "",
    `Return a JSON packet with schema \`${packet.requestedResponse.schema}\` and cardId \`${card.id}\`.`,
  ].join("\n");
}

function importPacketFile(event) {
  const [file] = event.target.files;
  event.target.value = "";
  if (!file) return;
  if (!Number.isSafeInteger(file.size) || file.size < 0) {
    handleActionError(typedError("INVALID_IMPORT", "The selected response has no trustworthy size."));
    return;
  }
  if (file.size > MAX_WORKSPACE_BYTES) {
    handleActionError(
      typedError("IMPORT_SIZE_LIMIT", "The encoded response exceeds the 250 MB import limit."),
    );
    return;
  }
  file.text().then((text) => {
    if (new TextEncoder().encode(text).byteLength > MAX_WORKSPACE_BYTES) {
      throw typedError(
        "IMPORT_SIZE_LIMIT",
        "The encoded response exceeds the 250 MB import limit.",
      );
    }
    elements.handoffImportText.value = text;
    previewImport();
  }).catch(handleActionError);
}

function previewImport() {
  try {
    const parsed = JSON.parse(elements.handoffImportText.value);
    const validation = validateResponsePacket(parsed, elements.handoffCardSelect.value);
    if (!validation.ok) {
      elements.handoffPreview.innerHTML = `
        <strong>Cannot apply this packet</strong>
        <ul>${validation.errors.map((error) => `<li>${escapeHtml(error)}</li>`).join("")}</ul>`;
      elements.handoffPreview.dataset.tone = "error";
      elements.handoffPreview.hidden = false;
      elements.applyImportButton.hidden = true;
      return;
    }
    state.pendingImport = validation.packet;
    elements.handoffPreview.innerHTML = `
      <strong>Review proposed changes</strong>
      <p>${escapeHtml(validation.packet.summary || "No summary supplied.")}</p>
      <dl>
        <div><dt>Plan steps</dt><dd>${validation.packet.plan.length}</dd></div>
        <div><dt>Outputs</dt><dd>${validation.packet.outputs.length}</dd></div>
        <div><dt>Activity entries</dt><dd>${validation.packet.activity.length}</dd></div>
      </dl>`;
    elements.handoffPreview.dataset.tone = "ready";
    elements.handoffPreview.hidden = false;
    elements.applyImportButton.hidden = false;
  } catch {
    elements.handoffPreview.textContent = "The response is not valid JSON.";
    elements.handoffPreview.dataset.tone = "error";
    elements.handoffPreview.hidden = false;
    elements.applyImportButton.hidden = true;
  }
}

async function applyImport() {
  if (!state.pendingImport) return;
  const result = await runMutation("applyResponse", {
    cardId: elements.handoffCardSelect.value,
    packet: state.pendingImport,
  });
  if (!result) return;
  if (state.selectedCard?.id === elements.handoffCardSelect.value) await refreshSelectedCard();
  elements.handoffDialog.close();
  showToast("Approved response applied with provenance.", "success");
}

function previewDirectSend() {
  try {
    providerAdapter.setCredential(elements.providerCredential.value);
    state.directPreview = providerAdapter.preview({
      provider: elements.providerName.value,
      endpoint: elements.providerEndpoint.value,
      model: elements.providerModel.value,
      content: elements.handoffExportText.value,
      purpose: elements.providerPurpose.value,
    });
    state.directReview = currentDirectReview();
    elements.directPreview.innerHTML = `
      <strong>Exact request preview</strong>
      <dl>
        <div><dt>Provider</dt><dd>${escapeHtml(state.directPreview.provider)}</dd></div>
        <div><dt>Model</dt><dd>${escapeHtml(state.directPreview.model)}</dd></div>
        <div><dt>Purpose</dt><dd>${escapeHtml(state.directPreview.purpose)}</dd></div>
      </dl>
      <p><strong>Endpoint</strong><br>${escapeHtml(state.directPreview.endpoint)}</p>
      <details><summary>Exact content</summary><pre>${escapeHtml(state.directPreview.content)}</pre></details>`;
    elements.directPreview.dataset.tone = "ready";
    elements.directPreview.hidden = false;
    elements.sendDirectButton.hidden = false;
  } catch (error) {
    elements.directPreview.textContent = error.message;
    elements.directPreview.dataset.tone = "error";
    elements.directPreview.hidden = false;
    elements.sendDirectButton.hidden = true;
  }
}

async function sendDirect() {
  if (
    !state.directPreview ||
    !state.directReview ||
    JSON.stringify(state.directReview) !== JSON.stringify(currentDirectReview())
  ) {
    invalidateDirectSend();
    showToast("The reviewed direct request changed. Preview it again before sending.", "warning");
    return;
  }
  if (!window.confirm("Send exactly the reviewed content to this provider endpoint?")) return;
  elements.sendDirectButton.disabled = true;
  try {
    const response = await providerAdapter.send(state.directPreview);
    elements.handoffImportText.value = JSON.stringify(response, null, 2);
    switchHandoffTab("import");
    previewImport();
    showToast("Provider response received. Review it before applying.", "success");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    providerAdapter.clearCredential();
    elements.providerCredential.value = "";
    elements.sendDirectButton.disabled = false;
  }
}

function currentDirectReview() {
  return {
    credentialVersion: state.credentialVersion,
    cardId: elements.handoffCardSelect.value,
    content: elements.handoffExportText.value,
    provider: elements.providerName.value,
    endpoint: elements.providerEndpoint.value,
    model: elements.providerModel.value,
    purpose: elements.providerPurpose.value,
  };
}

function invalidateDirectSend({ clearCredential = false } = {}) {
  providerAdapter.clearCredential();
  state.directPreview = null;
  state.directReview = null;
  if (elements.directPreview) {
    elements.directPreview.hidden = true;
    elements.directPreview.replaceChildren();
  }
  if (elements.sendDirectButton) elements.sendDirectButton.hidden = true;
  if (clearCredential && elements.providerCredential) {
    elements.providerCredential.value = "";
    state.credentialVersion += 1;
  }
}

async function exportWorkspaceArchive() {
  hideWorkspaceMenu();
  try {
    if (state.detachedForAgent) await state.workspace.reloadManifest();
    const bytes = state.detachedForAgent
      ? await state.workspace.readState()
      : await repository.exportBytes();
    const revision = state.detachedForAgent
      ? Number(state.workspace.manifest.revision)
      : Number(state.snapshot.meta.revision);
    const references = state.workspace instanceof FolderWorkspace
      ? await archiveReferencesFor(bytes)
      : [];
    const archive = await state.workspace.exportArchive(
      bytes,
      references,
      revision,
    );
    downloadArchive(archive, state.workspace.name);
    showToast("Portable workspace archive downloaded.", "success");
  } catch (error) {
    handleActionError(error);
  }

  async function archiveReferencesFor(bytes) {
    if (!state.detachedForAgent) return repository.archiveReferences();
    const reader = new BoardRepository();
    try {
      await reader.open(bytes);
      return await reader.archiveReferences();
    } finally {
      await reader.close().catch(() => {});
      reader.terminate();
    }
  }
}

async function showArchivedCards() {
  hideWorkspaceMenu();
  state.filters.archived = true;
  updateFilterCount();
  await renderBoard();
}

function showWorkspaceDetails() {
  hideWorkspaceMenu();
  const details = state.workspace?.details() || {};
  elements.workspaceDetails.replaceChildren(
    ...Object.entries(details).map(([key, value]) => {
      const row = document.createElement("div");
      row.innerHTML = `<dt>${escapeHtml(label(key))}</dt><dd>${escapeHtml(String(value))}</dd>`;
      return row;
    }),
  );
  elements.aboutDialog.showModal();
}

function showConflict(error) {
  state.conflict = error;
  const details = error.details || {};
  elements.conflictDetails.innerHTML = `
    <div><dt>Loaded revision</dt><dd>${escapeHtml(details.loaded?.revision ?? "Unknown")}</dd></div>
    <div><dt>Folder revision</dt><dd>${escapeHtml(details.disk?.revision ?? "Unknown")}</dd></div>
    <div><dt>Loaded fingerprint</dt><dd>${escapeHtml(shortFingerprint(details.loaded?.fingerprint))}</dd></div>
    <div><dt>Folder fingerprint</dt><dd>${escapeHtml(shortFingerprint(details.disk?.fingerprint))}</dd></div>`;
  elements.conflictDialog.showModal();
}

async function reloadAfterConflict() {
  elements.conflictDialog.close();
  await reloadWorkspace();
}

async function reloadWorkspace() {
  if (!state.workspace) return;
  setLoading(true, "Reloading durable workspace…");
  try {
    const expectedWorkspaceId = state.snapshot.meta.workspace_id;
    if (
      state.workspace.mode === "connected" &&
      !state.detachedForAgent &&
      !state.lock?.acquired
    ) {
      state.lock = await acquireWorkspaceLock(expectedWorkspaceId);
      state.workspace.setWriterLock?.(state.lock.acquired ? state.lock : null);
    }
    await state.workspace.reloadManifest?.();
    const bytes = await state.workspace.readState();
    state.snapshot = await openVerifiedWorkspaceBytes(
      bytes,
      state.workspace,
      expectedWorkspaceId,
      true,
    );
    state.dirty = false;
    state.conflict = null;
    state.readOnly = state.detachedForAgent || (
      state.workspace.mode === "connected" && !state.lock?.acquired
    );
    if (state.readOnly && state.workspace.mode === "connected") {
      setWorkspaceAlert(
        "Latest changes loaded. Another tab still owns the workspace lock, so this tab remains read-only.",
        "warning",
        [["Retry writable access", reloadWorkspace]],
      );
    } else {
      clearWorkspaceAlert();
    }
    await renderBoard();
    if (state.selectedCard) {
      state.selectedCard = await queryRepository().card(state.selectedCard.id).catch(() => null);
      if (state.selectedCard) renderCardDetail();
      else elements.cardDetailDialog.close();
    }
    updateChrome();
  } catch (error) {
    handleActionError(error);
  } finally {
    setLoading(false);
  }
}

async function exportDraft() {
  try {
    const bytes = await repository.exportBytes();
    const references = state.workspace instanceof FolderWorkspace
      ? await repository.archiveReferences()
      : [];
    const archive = await state.workspace.exportArchive(
      bytes,
      references,
      Number(state.snapshot.meta.revision),
    );
    downloadArchive(archive, `${state.workspace.name}-draft`);
    showToast("In-memory draft exported without overwriting the folder.", "success");
  } catch (error) {
    handleActionError(error);
  }
}

async function recoverConflict() {
  if (!window.confirm("Use the in-memory draft as the durable workspace? This explicit recovery replaces the externally changed board.sqlite.")) return;
  let acquiredHere = false;
  try {
    if (!state.lock?.acquired) {
      const lock = await acquireWorkspaceLock(state.snapshot.meta.workspace_id);
      if (!lock.acquired) {
        throw typedError(
          "RECOVERY_LOCK_UNAVAILABLE",
          "Use my draft requires an exclusive workspace lock. Close the other writer and retry.",
        );
      }
      state.lock = lock;
      state.workspace.setWriterLock?.(lock);
      acquiredHere = true;
    }
    await saveQueue.recover(async () => {
      const bytes = await repository.exportBytes();
      await state.workspace.recoverState(bytes, {
        revision: Number(state.snapshot.meta.revision),
      });
      state.dirty = false;
      state.readOnly = false;
      clearWorkspaceAlert();
      broadcast?.postMessage({
        type: "saved",
        workspaceId: state.snapshot.meta.workspace_id,
        revision: Number(state.snapshot.meta.revision),
        fingerprint: state.workspace.loadedSignature?.fingerprint || null,
      });
    });
    elements.conflictDialog.close();
    state.conflict = null;
    updateChrome();
    showToast("Draft recovered through an explicit locked write.", "success");
  } catch (error) {
    if (acquiredHere) {
      state.lock?.release();
      state.lock = null;
      state.workspace.setWriterLock?.(null);
    }
    handleActionError(error);
  }
}

function toggleWorkspaceMenu() {
  const open = elements.workspaceMenu.hidden;
  elements.workspaceMenu.hidden = !open;
  elements.workspaceMenuButton.setAttribute("aria-expanded", String(open));
}

function hideWorkspaceMenu() {
  elements.workspaceMenu.hidden = true;
  elements.workspaceMenuButton.setAttribute("aria-expanded", "false");
}

function updateChrome() {
  const open = Boolean(state.workspace && state.snapshot);
  if (!open) return;
  elements.workspaceName.textContent = state.workspace.name;
  let status;
  let dot;
  if (state.detachedForAgent) {
    status = `Read-only · ${state.snapshot.meta.control_holder} has control`;
    dot = "warning";
  } else if (state.readOnly) {
    status = state.dirty
      ? "Conflict · unsaved draft preserved"
      : "Read-only";
    dot = "warning";
  } else if (state.saving) {
    status = "Saving durable state…";
    dot = "saving";
  } else if (state.dirty) {
    status = state.workspace.mode === "connected"
      ? "Unsaved changes · autosave pending"
      : state.workspace.mode === "memory-only"
        ? "Memory-only · Save downloads an archive"
        : "Unsaved changes · Save downloads an archive";
    dot = "dirty";
  } else if (state.workspace.mode === "connected") {
    status = state.workspace.lastSavedAt
      ? `Saved · read/write granted · ${relativeTime(state.workspace.lastSavedAt)}`
      : `Connected · read/write granted · revision ${state.snapshot.meta.revision}`;
    dot = "saved";
  } else {
    status = state.workspace.mode === "memory-only" ? "Demo · memory only" : "Archive mode";
    dot = state.workspace.mode === "memory-only" ? "warning" : "saved";
  }
  elements.saveStatus.textContent = status;
  elements.connectionDot.dataset.state = dot;
  elements.saveButton.disabled = state.readOnly || state.saving;
  elements.newCardButton.disabled = state.readOnly;
  elements.globalHandoffButton.disabled = state.detachedForAgent;
  elements.repairBootstrapButton.disabled =
    state.readOnly || !ownsWorkspaceLock();
  updateAgentStatus();
}

function openGenericDialog({ eyebrow, title, submit, fields, action }) {
  elements.genericEyebrow.textContent = eyebrow;
  elements.genericTitle.textContent = title;
  elements.genericSubmit.textContent = submit;
  elements.genericFields.innerHTML = fields;
  state.genericAction = action;
  elements.genericDialog.showModal();
  elements.genericDialog.querySelector("input,textarea,select")?.focus();
}

async function submitGenericDialog(event) {
  event.preventDefault();
  if (!elements.genericForm.reportValidity()) return;
  elements.genericSubmit.disabled = true;
  try {
    const success = await state.genericAction?.(new FormData(elements.genericForm));
    if (success) elements.genericDialog.close();
  } catch (error) {
    handleActionError(error);
  } finally {
    elements.genericSubmit.disabled = false;
  }
}

function setWorkspaceAlert(message, tone = "info", actions = []) {
  elements.workspaceAlert.hidden = false;
  elements.workspaceAlert.dataset.tone = tone;
  elements.workspaceAlert.replaceChildren(document.createTextNode(message));
  if (actions.length) {
    const group = div("alert-actions");
    for (const [text, handler] of actions) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = text;
      button.addEventListener("click", handler);
      group.append(button);
    }
    elements.workspaceAlert.append(group);
  }
}

function clearWorkspaceAlert() {
  elements.workspaceAlert.hidden = true;
  elements.workspaceAlert.replaceChildren();
}

function setLoading(loading, text = "") {
  state.loading = loading;
  elements.loadingText.textContent = text;
  elements.loadingOverlay.hidden = !loading;
}

function showToast(message, tone = "info") {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.dataset.tone = tone;
  toast.textContent = message;
  elements.toastRegion.append(toast);
  setTimeout(() => toast.remove(), 4800);
}

function handleActionError(error) {
  if (error?.name === "AbortError") return;
  const message = userMessage(error);
  showToast(message, "error");
  if (state.snapshot) setWorkspaceAlert(message, "error");
}

function userMessage(error) {
  const messages = {
    MISSING_MANIFEST: "This folder has no AI Kanban manifest. Choose Create for an empty folder.",
    INVALID_MANIFEST: "manifest.json is invalid. Repair it from a trusted archive before reopening.",
    FUTURE_SCHEMA: "This workspace was created by a newer AI Kanban version. Open it with that version.",
    CORRUPT_DATABASE: "board.sqlite failed validation. Preserve the folder and restore from an archive.",
    MIGRATION_FAILED: "Migration rolled back. Original database bytes were preserved; export them before recovery.",
    PERMISSION_DENIED: "Read/write folder permission was not granted.",
    PERMISSION_PROMPT_REQUIRED: "Use Reconnect to grant folder permission.",
    WORKSPACE_NOT_EMPTY: "That folder already contains AI Kanban state. Open it or choose an empty folder.",
    CREATION_LOCK_UNAVAILABLE: "Another tab is creating this folder workspace. Wait for it to finish, then open the resulting workspace.",
    WORKSPACE_LOCK_UNAVAILABLE: "Another tab acquired this workspace while creation was starting.",
    WORKSPACE_LOCK_REQUIRED: "This tab does not own the writable workspace lock.",
    WORKSPACE_TOO_LARGE: "This workspace exceeds the documented 250 MB whole-file limit.",
    WORKSPACE_ID_MISMATCH: "The manifest and database belong to different workspaces.",
    WORKSPACE_PROTOCOL_MISMATCH: "Manifest and SQLite format, schema, or protocol do not agree.",
    STATE_FINGERPRINT_MISSING: "The manifest does not bind the canonical SQLite bytes. Restore or reconcile a trusted manifest.",
    STATE_FINGERPRINT_MISMATCH: "The SQLite bytes do not match the manifest fingerprint. The workspace may have been swapped or incompletely published.",
    REVISION_MISMATCH: "The workspace revision changed. Reload or export your draft before continuing.",
    STALE_GENERATION: "The writer baton changed generation. Reload control state.",
    CONTROL_NOT_HELD: "Another approved actor owns the writer baton.",
    AGENT_HAS_CONTROL: "The agent holds the writer baton. Request control back before editing.",
    DEPENDENCIES_INCOMPLETE: "This card still has incomplete dependencies.",
    DEPENDENCY_CYCLE: "That link would create a dependency cycle. Remove or reverse an existing dependency first.",
    DEPENDENCY_NOT_FOUND: "That dependency was already removed. Refresh the card workspace.",
    DECISION_GATE_REQUIRED: "Select an option and confirm the deep-work gate first.",
    ACTIVE_TURN_EXISTS: "This card already has an active turn.",
    ACTIVE_TURN_BLOCKS_DONE: "Finish or cancel claimed/running work before moving this card to Done.",
    RUN_AGAIN_CONFIRMATION_REQUIRED: "Confirm Run again before moving Done work to Inbox.",
    JOURNAL_DELAY: "Agent writes are still stabilizing. Retry after the agent closes SQLite.",
    COMMIT_MARKER_MISMATCH: "The manifest commit marker does not match board.sqlite. Preserve both files; if an agent published a recovery marker, run the skill's reconcile-manifest command before reopening.",
    BOOTSTRAP_CONFIRMATION_REQUIRED: "Existing agent instruction files require explicit replacement confirmation.",
    BOOTSTRAP_PATH_CONFLICT: "An agent bootstrap path is occupied by a directory and cannot be replaced.",
    BOOTSTRAP_CONFLICT: "An agent bootstrap file changed after comparison. Review the new content before approving replacement.",
    YIELD_ACKNOWLEDGEMENT_REQUIRED: "Wait for the agent to close its writer and publish a final yield marker.",
    FINAL_MARKER_MISMATCH: "The agent's final marker does not match durable SQLite state. Preserve the workspace and inspect diagnostics.",
  };
  return messages[error?.code] || error?.message || "Something went wrong. No durable state was replaced.";
}

function sectionElement(title, subtitle) {
  const section = document.createElement("section");
  section.className = "detail-section";
  section.innerHTML = `<header class="detail-section-header"><div><h3>${escapeHtml(title)}</h3><p>${escapeHtml(subtitle)}</p></div></header>`;
  return section;
}

function definitionList(entries) {
  const list = document.createElement("dl");
  list.className = "fact-list";
  for (const [key, value] of Object.entries(entries)) {
    const row = document.createElement("div");
    row.innerHTML = `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd>`;
    list.append(row);
  }
  return list;
}

function actionButton(text, handler, variant = "button-quiet") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${variant}`;
  button.textContent = text;
  button.disabled = state.readOnly && !["Export context"].includes(text);
  button.addEventListener("click", handler);
  return button;
}

function emptyMessage(text, tag = "div") {
  const element = document.createElement(tag);
  element.className = "empty-message";
  element.textContent = text;
  return element;
}

function div(className) {
  const element = document.createElement("div");
  element.className = className;
  return element;
}

function options(values, selected) {
  return values.map((value) => `<option value="${attribute(value)}" ${value === selected ? "selected" : ""}>${escapeHtml(value.replaceAll("_", " "))}</option>`).join("");
}

function attribute(value) {
  return escapeHtml(value).replaceAll("`", "&#96;");
}

function excerpt(value, length = 160) {
  const normalized = String(value || "").replace(/\s+/g, " ").trim();
  return normalized.length > length ? `${normalized.slice(0, length - 1)}…` : normalized;
}

function formatDate(value) {
  if (!value) return "Not yet";
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function relativeTime(value) {
  if (!value) return "not yet";
  const difference = Date.now() - Date.parse(value);
  if (!Number.isFinite(difference)) return "unknown";
  const minutes = Math.round(difference / 60_000);
  if (Math.abs(minutes) < 1) return "just now";
  if (Math.abs(minutes) < 60) return `${Math.abs(minutes)}m ${minutes > 0 ? "ago" : "from now"}`;
  const hours = Math.round(minutes / 60);
  if (Math.abs(hours) < 24) return `${Math.abs(hours)}h ${hours > 0 ? "ago" : "from now"}`;
  const days = Math.round(hours / 24);
  return `${Math.abs(days)}d ${days > 0 ? "ago" : "from now"}`;
}

function capitalize(value) {
  return String(value || "").replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function label(value) {
  return capitalize(value.replace(/([A-Z])/g, " $1"));
}

function slug(value) {
  return String(value || "card").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "card";
}


function shortFingerprint(value) {
  return value ? `${String(value).slice(0, 14)}…` : "Unknown";
}

function downloadText(text, name, type) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([text], { type }));
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 0);
}

function typedError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

function assertManifestRevision(snapshot, workspace) {
  if (
    Number(snapshot.meta.revision) !== Number(workspace.manifest.revision)
  ) {
    throw typedError(
      "COMMIT_MARKER_MISMATCH",
      "manifest.json and board.sqlite disagree on the committed revision.",
    );
  }
}

async function openVerifiedWorkspaceBytes(
  bytes,
  workspace,
  expectedWorkspaceId,
  invalidateOnMismatch,
  allowSchemaUpgrade = false,
) {
  try {
    if (workspace.manifest.workspace_id !== expectedWorkspaceId) {
      throw typedError(
        "WORKSPACE_ID_MISMATCH",
        "manifest.json changed to a different workspace.",
      );
    }
    const snapshot = await repository.openVerified(bytes, (candidate) => {
      if (
        candidate.meta.workspace_id !== workspace.manifest.workspace_id ||
        candidate.meta.workspace_id !== expectedWorkspaceId
      ) {
        throw typedError(
          "WORKSPACE_ID_MISMATCH",
          "manifest.json and board.sqlite identify a different workspace.",
        );
      }
      if (
        candidate.meta.workspace_format !== workspace.manifest.format ||
        Number(candidate.meta.format_version) !==
          Number(workspace.manifest.format_version) ||
        Number(candidate.meta.protocol_version) !==
          Number(workspace.manifest.protocol_version) ||
        (
          Number(candidate.meta.schema_version) !==
            Number(workspace.manifest.schema_version) &&
          !(
            allowSchemaUpgrade &&
            Number(candidate.meta.schema_version) >
              Number(workspace.manifest.schema_version)
          )
        )
      ) {
        throw typedError(
          "WORKSPACE_PROTOCOL_MISMATCH",
          "Manifest and SQLite format, schema, or protocol do not agree.",
        );
      }
      assertManifestRevision(candidate, workspace);
    });
    return snapshot;
  } catch (error) {
    if (
      ["WORKSPACE_ID_MISMATCH", "WORKSPACE_PROTOCOL_MISMATCH"].includes(error.code) &&
      invalidateOnMismatch
    ) {
      await repository.close().catch(() => {});
      state.coordination?.stop();
      state.coordination = null;
      state.lock?.release();
      state.lock = null;
      state.readOnly = true;
      state.detachedForAgent = true;
      updateChrome();
      setWorkspaceAlert(
        "Workspace identity changed on disk. The old lock and coordination session were released; reopen the intended folder explicitly.",
        "error",
      );
    }
    throw error;
  }
}
