import { SQLiteClient } from "./sqlite-client.js";
import {
  FileWorkspace,
  WorkspaceConflictError,
  acquireWorkspaceLock,
  clearRecentHandle,
  nativeFileSystemSupported,
  queryHandlePermission,
  recentHandle,
} from "./file-workspace.js";
import {
  createHandoffPacket,
  validateResponsePacket,
} from "./packets.js";

const client = new SQLiteClient();
const channel = "BroadcastChannel" in window
  ? new BroadcastChannel("ai-kanban-workspaces")
  : null;

const state = {
  workspace: null,
  snapshot: null,
  selectedCard: null,
  dirty: false,
  saving: false,
  readOnly: false,
  priority: "all",
  query: "",
  saveTimer: null,
  saveChain: Promise.resolve(),
  lock: null,
  pendingImport: null,
  textAction: null,
};

const elements = Object.fromEntries(
  [
    "welcome", "workspace", "board", "workspaceAlert", "connectionDot",
    "workspaceName", "saveStatus", "saveButton", "newCardButton",
    "openBoardButton", "createBoardButton", "welcomeOpenButton",
    "welcomeCreateButton", "demoButton", "browserSupportNote", "recentButton",
    "recentName", "fallbackFileInput", "searchInput", "visibleCardCount",
    "boardSummary", "moreButton", "workspaceMenu", "saveAsButton",
    "aboutWorkspaceButton", "closeWorkspaceButton", "cardDialog", "cardForm",
    "cardDialogEyebrow", "cardDialogTitle", "cardTitleInput", "cardColumnInput",
    "cardPriorityInput", "cardAssigneeInput", "cardDescriptionInput",
    "cardWorkspaceSections", "archiveCardButton", "planList", "outputList",
    "activityList", "addPlanButton", "addOutputButton", "handoffButton",
    "textDialog", "textDialogForm", "textDialogEyebrow", "textDialogTitle",
    "textDialogFields", "textDialogSubmit", "handoffDialog",
    "handoffExportPanel", "handoffImportPanel", "handoffExportText",
    "handoffImportText", "copyHandoffButton", "downloadHandoffButton",
    "previewImportButton", "handoffPreview", "applyImportButton",
    "aboutDialog", "workspaceDetails", "toastRegion",
  ].map((id) => [id, document.getElementById(id)]),
);

initialize();

async function initialize() {
  bindGlobalEvents();
  elements.browserSupportNote.textContent = nativeFileSystemSupported
    ? "Connected file saving is available in this browser."
    : "This browser uses import/download mode. Chrome or Edge desktop can save directly to a chosen file.";
  if (!nativeFileSystemSupported) {
    const steps = document.querySelectorAll(".welcome-diagram article");
    steps[0].querySelector("strong").textContent = "Import";
    steps[0].querySelector("small").textContent = "Choose a SQLite file.";
    steps[2].querySelector("strong").textContent = "Download";
    steps[2].querySelector("small").textContent = "Save an updated copy.";
  }
  const handle = nativeFileSystemSupported ? await recentHandle() : null;
  if (handle) {
    elements.recentName.textContent = handle.name;
    elements.recentButton.hidden = false;
    elements.recentButton.addEventListener("click", () => reconnect(handle));
  }
  updateChrome();
}

function bindGlobalEvents() {
  elements.openBoardButton.addEventListener("click", openExisting);
  elements.welcomeOpenButton.addEventListener("click", openExisting);
  elements.createBoardButton.addEventListener("click", createBoard);
  elements.welcomeCreateButton.addEventListener("click", createBoard);
  elements.demoButton.addEventListener("click", openDemo);
  elements.saveButton.addEventListener("click", () => saveNow());
  elements.saveAsButton.addEventListener("click", saveAs);
  elements.newCardButton.addEventListener("click", () => openCardEditor());
  elements.moreButton.addEventListener("click", toggleWorkspaceMenu);
  elements.aboutWorkspaceButton.addEventListener("click", showWorkspaceDetails);
  elements.closeWorkspaceButton.addEventListener("click", closeWorkspace);
  elements.fallbackFileInput.addEventListener("change", importFallbackFile);
  elements.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value.trim().toLowerCase();
    renderBoard();
  });
  document.querySelectorAll("[data-priority]").forEach((button) => {
    button.addEventListener("click", () => {
      state.priority = button.dataset.priority;
      document.querySelectorAll("[data-priority]").forEach((candidate) => {
        const active = candidate === button;
        candidate.classList.toggle("is-active", active);
        candidate.setAttribute("aria-pressed", String(active));
      });
      renderBoard();
    });
  });
  elements.cardForm.addEventListener("submit", saveCardFromDialog);
  elements.archiveCardButton.addEventListener("click", archiveSelectedCard);
  elements.addPlanButton.addEventListener("click", openPlanEditor);
  elements.addOutputButton.addEventListener("click", openOutputEditor);
  elements.handoffButton.addEventListener("click", openHandoff);
  elements.textDialogForm.addEventListener("submit", submitTextDialog);
  document.querySelectorAll("[data-handoff-tab]").forEach((button) => {
    button.addEventListener("click", () => switchHandoffTab(button.dataset.handoffTab));
  });
  elements.copyHandoffButton.addEventListener("click", copyHandoff);
  elements.downloadHandoffButton.addEventListener("click", downloadHandoff);
  elements.previewImportButton.addEventListener("click", previewImport);
  elements.applyImportButton.addEventListener("click", applyImport);
  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog")?.close());
  });
  window.addEventListener("beforeunload", (event) => {
    if (!state.dirty) return;
    event.preventDefault();
    event.returnValue = "";
  });
  document.addEventListener("click", (event) => {
    if (
      !elements.workspaceMenu.hidden &&
      !elements.workspaceMenu.contains(event.target) &&
      event.target !== elements.moreButton
    ) {
      hideWorkspaceMenu();
    }
  });
  channel?.addEventListener("message", ({ data }) => {
    if (data?.workspaceId === state.snapshot?.meta?.workspace_id && data.type === "saved") {
      setWorkspaceAlert("Another tab saved this workspace. Reload before making further changes.", "warning");
    }
  });
}

async function openExisting() {
  if (!confirmWorkspaceSwitch()) return;
  if (!nativeFileSystemSupported) {
    elements.fallbackFileInput.click();
    return;
  }
  try {
    const workspace = await FileWorkspace.openNative();
    await activateWorkspace(workspace, { create: false });
  } catch (error) {
    handleFileActionError(error);
  }
}

async function createBoard() {
  if (!confirmWorkspaceSwitch()) return;
  if (!nativeFileSystemSupported) {
    await activateWorkspace(
      new FileWorkspace({
        name: "new-board.aikanban.sqlite",
        mode: "import/download",
      }),
      { create: true },
    );
    return;
  }
  try {
    const workspace = await FileWorkspace.createNative();
    await activateWorkspace(workspace, { create: true });
    await saveNow({ force: true });
  } catch (error) {
    handleFileActionError(error);
  }
}

async function openDemo() {
  if (!confirmWorkspaceSwitch()) return;
  await activateWorkspace(FileWorkspace.memoryDemo(), { create: true, seed: true });
}

async function reconnect(handle) {
  if (!confirmWorkspaceSwitch()) return;
  try {
    const permission = await queryHandlePermission(handle);
    if (permission !== "granted") {
      showToast("Confirm file access to reconnect your recent board.", "info");
    }
    const workspace = await FileWorkspace.fromHandle(handle);
    await activateWorkspace(workspace, { create: false });
  } catch (error) {
    if (error.code === "PERMISSION_DENIED") await clearRecentHandle();
    handleFileActionError(error);
  }
}

async function importFallbackFile(event) {
  const [file] = event.target.files;
  event.target.value = "";
  if (!file) return;
  try {
    const workspace = await FileWorkspace.fromImportedFile(file);
    await activateWorkspace(workspace, { create: false });
  } catch (error) {
    handleFileActionError(error);
  }
}

async function activateWorkspace(workspace, { create, seed = false }) {
  await releaseCurrentWorkspace();
  setLoading(true, create ? "Creating workspace…" : "Opening workspace…");
  try {
    const bytes = create ? null : await workspace.readBytes();
    state.snapshot = await client.open(bytes, { seed });
    state.workspace = workspace;
    state.dirty = create;
    state.readOnly = false;
    state.lock = await acquireWorkspaceLock(state.snapshot.meta.workspace_id);
    if (!state.lock.acquired) {
      state.readOnly = true;
      setWorkspaceAlert(
        "Another tab owns this workspace. This tab is read-only until the other tab closes it.",
        "warning",
      );
    } else {
      clearWorkspaceAlert();
    }
    elements.welcome.hidden = true;
    elements.workspace.hidden = false;
    elements.searchInput.value = "";
    state.query = "";
    renderBoard();
    updateChrome();
    if (create && workspace.mode === "import/download") {
      showToast("New board created. Use Save to download its SQLite file.", "info");
    }
  } catch (error) {
    await client.close().catch(() => {});
    state.workspace = null;
    state.snapshot = null;
    showToast(userMessage(error), "error");
  } finally {
    setLoading(false);
    updateChrome();
  }
}

async function releaseCurrentWorkspace() {
  clearTimeout(state.saveTimer);
  state.lock?.release();
  state.lock = null;
  if (state.snapshot) await client.close().catch(() => {});
  state.selectedCard = null;
  state.snapshot = null;
  state.workspace = null;
  state.dirty = false;
  state.readOnly = false;
}

async function closeWorkspace() {
  if (state.saving) {
    showToast("Wait for the current save to finish before closing.", "info");
    return;
  }
  if (state.dirty) {
    const confirmed = window.confirm("Close with unsaved changes?");
    if (!confirmed) return;
  }
  await releaseCurrentWorkspace();
  hideWorkspaceMenu();
  elements.workspace.hidden = true;
  elements.welcome.hidden = false;
  updateChrome();
}

function confirmWorkspaceSwitch() {
  if (state.saving) {
    showToast("Wait for the current save to finish before switching workspaces.", "info");
    return false;
  }
  return (
    !state.snapshot ||
    !state.dirty ||
    window.confirm("Discard unsaved changes and switch workspaces?")
  );
}

async function saveNow({ force = false } = {}) {
  if (!state.workspace || state.readOnly) return;
  const workspace = state.workspace;
  state.saveChain = state.saveChain.then(async () => {
    if (state.workspace !== workspace) return;
    state.saving = true;
    updateChrome();
    try {
      const bytes = await client.exportBytes();
      await workspace.save(bytes, { force });
      if (state.workspace !== workspace) return;
      state.dirty = false;
      clearWorkspaceAlert();
      channel?.postMessage({
        type: "saved",
        workspaceId: state.snapshot.meta.workspace_id,
      });
      showToast(
        workspace.mode === "import/download"
          ? "Updated workspace downloaded."
          : "Workspace saved.",
        "success",
      );
    } catch (error) {
      if (error instanceof WorkspaceConflictError) showConflict(error);
      else showToast(userMessage(error), "error");
    } finally {
      state.saving = false;
      updateChrome();
    }
  });
  return state.saveChain;
}

async function saveAs() {
  if (!state.workspace || state.readOnly) return;
  try {
    const bytes = await client.exportBytes();
    await state.workspace.saveAs(bytes);
    state.dirty = false;
    clearWorkspaceAlert();
    updateChrome();
    showToast("Workspace saved to the selected file.", "success");
  } catch (error) {
    handleFileActionError(error);
  }
}

function scheduleSave() {
  state.dirty = true;
  updateChrome();
  clearTimeout(state.saveTimer);
  if (state.workspace?.mode === "connected" && !state.readOnly) {
    state.saveTimer = setTimeout(() => saveNow(), 650);
  }
}

async function runMutation(method, payload) {
  if (state.readOnly) {
    showToast("This workspace is open read-only in this tab.", "warning");
    return null;
  }
  try {
    const result = await client[method](payload);
    state.snapshot = result.snapshot;
    scheduleSave();
    renderBoard();
    return result;
  } catch (error) {
    showToast(userMessage(error), "error");
    return null;
  }
}

function renderBoard() {
  if (!state.snapshot) return;
  const query = state.query;
  const visible = state.snapshot.cards.filter((card) => {
    const priorityMatch = state.priority === "all" || card.priority === state.priority;
    const text = `${card.title} ${card.description} ${card.assignee}`.toLowerCase();
    return priorityMatch && (!query || text.includes(query));
  });
  elements.visibleCardCount.textContent = `${visible.length} ${visible.length === 1 ? "card" : "cards"}`;
  elements.boardSummary.textContent = state.query || state.priority !== "all"
    ? `Filtered from ${state.snapshot.cards.length}`
    : "All work visible";

  elements.board.replaceChildren(
    ...state.snapshot.columns.map((column, columnIndex) => {
      const cards = visible.filter((card) => card.columnId === column.id);
      const section = document.createElement("section");
      section.className = "board-column";
      section.dataset.columnId = column.id;
      section.style.setProperty("--column-color", column.color);
      section.innerHTML = `
        <header class="column-header">
          <div><span class="column-dot"></span><h2>${escapeHtml(column.title)}</h2></div>
          <span>${cards.length}</span>
        </header>
        <div class="column-cards" role="list"></div>
        <button class="add-card-button" type="button">+ Add card</button>
      `;
      const list = section.querySelector(".column-cards");
      list.append(...cards.map((card) => renderCard(card, columnIndex)));
      if (!cards.length) {
        const empty = document.createElement("div");
        empty.className = "column-empty";
        empty.textContent = query || state.priority !== "all"
          ? "No matching cards"
          : `No work in ${column.title}`;
        list.append(empty);
      }
      section.querySelector(".add-card-button").addEventListener("click", () => {
        openCardEditor(null, column.id);
      });
      section.addEventListener("dragover", (event) => event.preventDefault());
      section.addEventListener("drop", (event) => {
        event.preventDefault();
        const cardId = event.dataTransfer.getData("text/ai-kanban-card");
        if (cardId) runMutation("moveCard", { cardId, columnId: column.id });
      });
      return section;
    }),
  );
}

function renderCard(card, columnIndex) {
  const article = document.createElement("article");
  article.className = "kanban-card";
  article.draggable = !state.readOnly;
  article.tabIndex = 0;
  article.dataset.cardId = card.id;
  article.setAttribute("role", "listitem");
  article.innerHTML = `
    <div class="card-topline">
      <span class="priority" data-priority="${card.priority}">${card.priority}</span>
      <span class="assignee">${escapeHtml(card.assignee || "Unassigned")}</span>
    </div>
    <h3>${escapeHtml(card.title)}</h3>
    <p>${escapeHtml(excerpt(card.description, 150) || "No description yet.")}</p>
    <div class="card-progress" aria-label="${card.planDone} of ${card.planCount} plan steps complete">
      <i style="width:${card.planCount ? Math.round((card.planDone / card.planCount) * 100) : 0}%"></i>
    </div>
    <footer>
      <span>${card.planCount ? `${card.planDone}/${card.planCount} steps` : "No plan"}</span>
      <span>${card.outputCount ? `${card.outputCount} outputs` : "No outputs"}</span>
    </footer>
    <div class="card-move-actions" aria-label="Move card">
      <button type="button" data-direction="-1" ${columnIndex === 0 ? "disabled" : ""} aria-label="Move left">←</button>
      <button type="button" data-direction="1" ${columnIndex === state.snapshot.columns.length - 1 ? "disabled" : ""} aria-label="Move right">→</button>
    </div>
  `;
  article.addEventListener("click", (event) => {
    if (!event.target.closest(".card-move-actions")) openCardEditor(card.id);
  });
  article.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openCardEditor(card.id);
    }
    if (event.altKey && ["ArrowLeft", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
      moveAdjacent(card.id, event.key === "ArrowRight" ? 1 : -1);
    }
  });
  article.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/ai-kanban-card", card.id);
    event.dataTransfer.effectAllowed = "move";
    article.classList.add("is-dragging");
  });
  article.addEventListener("dragend", () => article.classList.remove("is-dragging"));
  article.addEventListener("dragover", (event) => event.preventDefault());
  article.addEventListener("drop", (event) => {
    event.preventDefault();
    event.stopPropagation();
    const movedCardId = event.dataTransfer.getData("text/ai-kanban-card");
    if (movedCardId && movedCardId !== card.id) {
      runMutation("moveCard", {
        cardId: movedCardId,
        columnId: card.columnId,
        beforeCardId: card.id,
      });
    }
  });
  article.querySelectorAll("[data-direction]").forEach((button) => {
    button.addEventListener("click", () => moveAdjacent(card.id, Number(button.dataset.direction)));
  });
  return article;
}

function moveAdjacent(cardId, direction) {
  const card = state.snapshot.cards.find((item) => item.id === cardId);
  if (!card) return;
  const index = state.snapshot.columns.findIndex((column) => column.id === card.columnId);
  const target = state.snapshot.columns[index + direction];
  if (target) runMutation("moveCard", { cardId, columnId: target.id });
}

async function openCardEditor(cardId = null, columnId = "inbox") {
  state.selectedCard = cardId ? await client.card(cardId) : null;
  elements.cardDialogEyebrow.textContent = cardId ? state.selectedCard.columnTitle : "New workspace card";
  elements.cardDialogTitle.textContent = cardId ? "Card workspace" : "Create card";
  elements.cardTitleInput.value = state.selectedCard?.title || "";
  elements.cardColumnInput.replaceChildren(
    ...state.snapshot.columns.map((column) => {
      const option = document.createElement("option");
      option.value = column.id;
      option.textContent = column.title;
      return option;
    }),
  );
  elements.cardColumnInput.value = state.selectedCard?.columnId || columnId;
  elements.cardPriorityInput.value = state.selectedCard?.priority || "P2";
  elements.cardAssigneeInput.value = state.selectedCard?.assignee || "";
  elements.cardDescriptionInput.value = state.selectedCard?.description || "";
  elements.cardWorkspaceSections.hidden = !cardId;
  elements.archiveCardButton.hidden = !cardId;
  if (cardId) renderCardWorkspace();
  elements.cardDialog.showModal();
  elements.cardTitleInput.focus();
}

async function saveCardFromDialog(event) {
  event.preventDefault();
  if (!elements.cardForm.reportValidity()) return;
  const payload = {
    title: elements.cardTitleInput.value,
    description: elements.cardDescriptionInput.value,
    priority: elements.cardPriorityInput.value,
    assignee: elements.cardAssigneeInput.value,
  };
  const targetColumnId = elements.cardColumnInput.value;
  let result = state.selectedCard
    ? await runMutation("updateCard", { cardId: state.selectedCard.id, ...payload })
    : await runMutation("createCard", {
        columnId: targetColumnId,
        ...payload,
      });
  if (
    result &&
    state.selectedCard &&
    targetColumnId !== state.selectedCard.columnId
  ) {
    result = await runMutation("moveCard", {
      cardId: state.selectedCard.id,
      columnId: targetColumnId,
    });
  }
  if (result) elements.cardDialog.close();
}

async function archiveSelectedCard() {
  if (!state.selectedCard || !window.confirm("Archive this card?")) return;
  const result = await runMutation("archiveCard", state.selectedCard.id);
  if (result) elements.cardDialog.close();
}

function renderCardWorkspace() {
  const card = state.selectedCard;
  elements.planList.replaceChildren(
    ...(card.plan.length
      ? card.plan.map(renderPlanItem)
      : [emptyMessage("No plan yet. Add the first concrete step.")]),
  );
  elements.outputList.replaceChildren(
    ...(card.outputs.length
      ? card.outputs.map(renderOutput)
      : [emptyMessage("No outputs yet. Capture a result or status.")]),
  );
  elements.activityList.replaceChildren(
    ...(card.activity.length
      ? card.activity.map(renderActivity)
      : [emptyMessage("Activity will appear as the workspace changes.", "li")]),
  );
}

function renderPlanItem(item) {
  const row = document.createElement("div");
  row.className = "plan-item";
  row.innerHTML = `
    <select aria-label="Plan status">
      ${["pending", "running", "done", "failed"].map(
        (status) => `<option value="${status}" ${item.status === status ? "selected" : ""}>${status}</option>`,
      ).join("")}
    </select>
    <span>${escapeHtml(item.text)}</span>
  `;
  row.querySelector("select").addEventListener("change", async (event) => {
    const result = await runMutation("updatePlanItem", {
      cardId: state.selectedCard.id,
      planItemId: item.id,
      text: item.text,
      status: event.target.value,
    });
    if (result) {
      state.selectedCard = await client.card(state.selectedCard.id);
      renderCardWorkspace();
    }
  });
  return row;
}

function renderOutput(output) {
  const article = document.createElement("article");
  article.className = "output-card";
  const content = output.type === "link"
    ? safeLink(output.content)
    : `<pre>${escapeHtml(output.content)}</pre>`;
  article.innerHTML = `
    <header><span>${escapeHtml(output.type)}</span><small>${escapeHtml(output.status)}</small></header>
    <h4>${escapeHtml(output.title)}</h4>
    ${content}
  `;
  return article;
}

function renderActivity(event) {
  const item = document.createElement("li");
  item.dataset.type = event.type;
  item.innerHTML = `
    <i aria-hidden="true"></i>
    <div><strong>${escapeHtml(event.summary)}</strong><span>${escapeHtml(event.actor)} · ${formatTime(event.createdAt)}</span></div>
  `;
  return item;
}

function openPlanEditor() {
  openTextDialog({
    eyebrow: "Plan",
    title: "Add a concrete step",
    submit: "Add step",
    fields: `
      <label class="field"><span>Step</span><input name="text" required maxlength="240"></label>
      <label class="field"><span>Status</span>
        <select name="status"><option>pending</option><option>running</option><option>done</option><option>failed</option></select>
      </label>
    `,
    action: async (form) => {
      const result = await runMutation("addPlanItem", {
        cardId: state.selectedCard.id,
        text: form.get("text"),
        status: form.get("status"),
      });
      if (result) refreshSelectedCard();
      return Boolean(result);
    },
  });
}

function openOutputEditor() {
  openTextDialog({
    eyebrow: "Output surface",
    title: "Capture an output",
    submit: "Add output",
    fields: `
      <div class="card-form-grid">
        <label class="field"><span>Type</span>
          <select name="type"><option>text</option><option>status</option><option>link</option><option>program</option><option>table</option></select>
        </label>
        <label class="field"><span>Status</span>
          <select name="status"><option>complete</option><option>draft</option><option>streaming</option><option>failed</option><option>stale</option></select>
        </label>
        <label class="field field-wide"><span>Title</span><input name="title" required maxlength="160"></label>
        <label class="field field-wide"><span>Content</span><textarea name="content" rows="7"></textarea></label>
      </div>
    `,
    action: async (form) => {
      const result = await runMutation("addOutput", {
        cardId: state.selectedCard.id,
        type: form.get("type"),
        status: form.get("status"),
        title: form.get("title"),
        content: form.get("content"),
      });
      if (result) refreshSelectedCard();
      return Boolean(result);
    },
  });
}

function openTextDialog({ eyebrow, title, submit, fields, action }) {
  elements.textDialogEyebrow.textContent = eyebrow;
  elements.textDialogTitle.textContent = title;
  elements.textDialogSubmit.textContent = submit;
  elements.textDialogFields.innerHTML = fields;
  state.textAction = action;
  elements.textDialog.showModal();
  elements.textDialog.querySelector("input,textarea,select")?.focus();
}

async function submitTextDialog(event) {
  event.preventDefault();
  if (!elements.textDialogForm.reportValidity()) return;
  const success = await state.textAction?.(new FormData(elements.textDialogForm));
  if (success) elements.textDialog.close();
}

async function refreshSelectedCard() {
  state.selectedCard = await client.card(state.selectedCard.id);
  renderCardWorkspace();
}

function openHandoff() {
  const packet = createHandoffPacket(state.selectedCard);
  elements.handoffExportText.value = JSON.stringify(packet, null, 2);
  elements.handoffImportText.value = "";
  state.pendingImport = null;
  elements.handoffPreview.hidden = true;
  elements.applyImportButton.hidden = true;
  switchHandoffTab("export");
  elements.handoffDialog.showModal();
}

function switchHandoffTab(tab) {
  document.querySelectorAll("[data-handoff-tab]").forEach((button) => {
    const active = button.dataset.handoffTab === tab;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
  elements.handoffExportPanel.hidden = tab !== "export";
  elements.handoffImportPanel.hidden = tab !== "import";
}

async function copyHandoff() {
  await navigator.clipboard.writeText(elements.handoffExportText.value);
  showToast("Handoff packet copied.", "success");
}

function downloadHandoff() {
  downloadText(
    elements.handoffExportText.value,
    `${slug(state.selectedCard.title)}-handoff.json`,
    "application/json",
  );
}

function previewImport() {
  try {
    const parsed = JSON.parse(elements.handoffImportText.value);
    const validation = validateResponsePacket(parsed, state.selectedCard.id);
    if (!validation.ok) {
      elements.handoffPreview.innerHTML = `<strong>Cannot apply this packet</strong><ul>${validation.errors.map(
        (error) => `<li>${escapeHtml(error)}</li>`,
      ).join("")}</ul>`;
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
      </dl>
    `;
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
    cardId: state.selectedCard.id,
    packet: state.pendingImport,
  });
  if (!result) return;
  await refreshSelectedCard();
  elements.handoffDialog.close();
  showToast("Approved AI response applied.", "success");
}

function toggleWorkspaceMenu() {
  const open = elements.workspaceMenu.hidden;
  elements.workspaceMenu.hidden = !open;
  elements.moreButton.setAttribute("aria-expanded", String(open));
}

function hideWorkspaceMenu() {
  elements.workspaceMenu.hidden = true;
  elements.moreButton.setAttribute("aria-expanded", "false");
}

function showWorkspaceDetails() {
  hideWorkspaceMenu();
  const details = state.workspace?.details() || {};
  elements.workspaceDetails.innerHTML = Object.entries(details)
    .map(([key, value]) => `<div><dt>${escapeHtml(label(key))}</dt><dd>${escapeHtml(String(value))}</dd></div>`)
    .join("");
  elements.aboutDialog.showModal();
}

function updateChrome() {
  const open = Boolean(state.workspace && state.snapshot);
  document.body.classList.toggle("has-workspace", open);
  elements.workspaceName.textContent = open ? state.workspace.name : "No board open";
  let status = "Choose or create a local workspace";
  let dot = "closed";
  if (open) {
    dot = state.readOnly ? "warning" : state.dirty ? "dirty" : "saved";
    if (state.readOnly) status = "Read-only · another tab owns this file";
    else if (state.saving) status = "Saving to local file…";
    else if (state.dirty) {
      status = state.workspace.mode === "connected"
        ? "Unsaved changes · autosave pending"
        : state.workspace.mode === "memory-only"
          ? "Memory-only · use Save As"
          : "Unsaved changes · Save downloads a new file";
    } else {
      status = state.workspace.mode === "connected"
        ? `Saved locally${state.workspace.lastSavedAt ? ` · ${formatTime(state.workspace.lastSavedAt)}` : ""}`
        : state.workspace.mode;
    }
  }
  elements.connectionDot.dataset.state = dot;
  elements.saveStatus.textContent = status;
  elements.saveButton.disabled = !open || state.readOnly || state.saving;
  elements.newCardButton.disabled = !open || state.readOnly;
  elements.moreButton.disabled = !open;
  elements.saveAsButton.disabled = !open || state.readOnly;
  elements.closeWorkspaceButton.disabled = !open;
}

function setLoading(loading, message = "") {
  document.body.classList.toggle("is-loading", loading);
  if (loading) elements.saveStatus.textContent = message;
}

function showConflict(error) {
  setWorkspaceAlert(
    `${error.message} Reload the file, save your version elsewhere, or explicitly overwrite it.`,
    "error",
    [
      ["Reload", () => reloadWorkspace()],
      ["Save as", saveAs],
      ["Overwrite", () => saveNow({ force: true })],
    ],
  );
}

async function reloadWorkspace() {
  if (!state.workspace) return;
  try {
    const bytes = await state.workspace.readBytes();
    state.snapshot = await client.open(bytes);
    state.dirty = false;
    clearWorkspaceAlert();
    renderBoard();
    updateChrome();
  } catch (error) {
    showToast(userMessage(error), "error");
  }
}

function setWorkspaceAlert(message, tone, actions = []) {
  elements.workspaceAlert.hidden = false;
  elements.workspaceAlert.dataset.tone = tone;
  elements.workspaceAlert.replaceChildren(document.createTextNode(message));
  if (actions.length) {
    const group = document.createElement("div");
    group.className = "alert-actions";
    for (const [labelText, action] of actions) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = labelText;
      button.addEventListener("click", action);
      group.append(button);
    }
    elements.workspaceAlert.append(group);
  }
}

function clearWorkspaceAlert() {
  elements.workspaceAlert.hidden = true;
  elements.workspaceAlert.replaceChildren();
}

function handleFileActionError(error) {
  if (error?.name === "AbortError") return;
  showToast(userMessage(error), "error");
}

function userMessage(error) {
  const messages = {
    INVALID_SCHEMA: "That file is not an AI Kanban workspace.",
    FUTURE_SCHEMA: "This board was created by a newer AI Kanban version.",
    UNSUPPORTED_SCHEMA: "This board needs a supported migration before it can open.",
    PERMISSION_DENIED: "File permission was not granted.",
    EXTERNAL_FILE_CONFLICT: "The workspace changed outside AI Kanban.",
    NO_FILE_HANDLE: "Choose Save As to connect this workspace to a file.",
    SQLITE_ERROR: "This file is unreadable or is not a valid SQLite database.",
  };
  return messages[error?.code] || error?.message || "Something went wrong.";
}

function showToast(message, tone = "info") {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.dataset.tone = tone;
  toast.textContent = message;
  elements.toastRegion.append(toast);
  setTimeout(() => toast.remove(), 4200);
}

function emptyMessage(text, tag = "div") {
  const element = document.createElement(tag);
  element.className = "empty-message";
  element.textContent = text;
  return element;
}

function safeLink(value) {
  try {
    const url = new URL(value);
    if (!["http:", "https:"].includes(url.protocol)) throw new Error();
    return `<a href="${escapeHtml(url.href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(url.href)}</a>`;
  } catch {
    return `<pre>${escapeHtml(value)}</pre>`;
  }
}

function downloadText(text, name, type) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([text], { type }));
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 0);
}

function escapeHtml(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (character) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    })[character],
  );
}

function excerpt(value, length) {
  const normalized = String(value || "").replace(/\s+/g, " ").trim();
  return normalized.length > length ? `${normalized.slice(0, length - 1)}…` : normalized;
}

function formatTime(value) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function slug(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "card";
}

function label(value) {
  return value.replace(/([A-Z])/g, " $1").replace(/^./, (character) => character.toUpperCase());
}
