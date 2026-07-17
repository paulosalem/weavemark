// WeaveMark — Webview form panel
//
// Renders an interactive form for filling in spec variables,
// with live preview and run capabilities.

const vscode = require("vscode");
const path = require("path");
const crypto = require("crypto");
const {
  buildCliArguments,
  launchCliTerminal,
  requireTrustedWorkspace,
  resolvePrompletPath,
  scanPromplet,
} = require("./cli");

// ── State ───────────────────────────────────────────────────────

let _panel = null;
let _specPath = null;
let _metadata = null;

// ── Panel creation ──────────────────────────────────────────────

/**
 * Open the WeaveMark form panel for the given promplet file.
 */
async function openFormPanel(uri) {
  if (!requireTrustedWorkspace("scanning or running promplets")) return;
  const specPath = await resolvePrompletPath(uri);
  if (!specPath) return;

  let metadata;
  try {
    metadata = await scanPromplet(specPath);
  } catch (err) {
    vscode.window.showErrorMessage(
      `WeaveMark: Failed to scan spec — ${err.message}`
    );
    return;
  }

  // Create or reuse panel
  if (_panel) {
    _panel.reveal(vscode.ViewColumn.Beside);
  } else {
    _panel = vscode.window.createWebviewPanel(
      "weavemarkForm",
      `⚡ ${metadata.title || "WeaveMark"}`,
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
        enableCommandUris: false,
        localResourceRoots: [],
        retainContextWhenHidden: false,
      }
    );
    _panel.onDidDispose(() => {
      _panel = null;
      _specPath = null;
      _metadata = null;
    });
    _panel.webview.onDidReceiveMessage(handleWebviewMessage);
  }

  _specPath = specPath;
  _metadata = metadata;
  _panel.title = `⚡ ${metadata.title || "WeaveMark"}`;
  _panel.webview.html = buildFormHtml(_panel.webview, metadata, specPath);
}

async function handleWebviewMessage(message) {
  if (!_panel || !_specPath || !_metadata || !isMessage(message)) {
    return;
  }
  if (!requireTrustedWorkspace("running promplets")) return;

  if (message.command === "refresh") {
    try {
      _metadata = await scanPromplet(_specPath);
      _panel.title = `⚡ ${_metadata.title || "WeaveMark"}`;
      _panel.webview.html = buildFormHtml(
        _panel.webview,
        _metadata,
        _specPath
      );
    } catch (error) {
      vscode.window.showErrorMessage(`WeaveMark: ${error.message}`);
    }
    return;
  }

  const values = validateFormValues(message.values, _metadata.inputs || []);
  if (!values) {
    vscode.window.showErrorMessage(
      "WeaveMark: The form submitted invalid or unexpected values."
    );
    return;
  }
  const modes = {
    compose: { args: [], name: "WeaveMark Compose" },
    run: { args: ["--run", "--verbose"], name: "WeaveMark Run" },
    openTUI: { args: ["--ui"], name: "WeaveMark TUI" },
  };
  const mode = modes[message.command];
  if (!mode) return;

  try {
    launchCliTerminal(
      buildCliArguments(_specPath, mode.args, values),
      path.dirname(_specPath),
      mode.name
    );
  } catch (error) {
    vscode.window.showErrorMessage(`WeaveMark: ${error.message}`);
  }
}

// ── HTML generation ─────────────────────────────────────────────

function buildFormHtml(webview, metadata, specPath) {
  const nonce = crypto.randomBytes(18).toString("base64");
  const title = escapeHtml(metadata.title || "Untitled Promplet");
  const desc = escapeHtml(metadata.description || "");
  const filename = escapeHtml(path.basename(specPath));

  const inputsHtml = (metadata.inputs || []).map(buildInputHtml).join("\n");

  const hasExecution = metadata.execution && metadata.execution.type;
  const strategyBadge = hasExecution
    ? `<span class="badge strategy">${escapeHtml(metadata.execution.type)}</span>`
    : "";

  const toolBadges = (metadata.tool_names || [])
    .map((t) => `<span class="badge tool">🔧 ${escapeHtml(t)}</span>`)
    .join(" ");

  const promptBadges = (metadata.prompt_names || [])
    .map((p) => `<span class="badge prompt">💬 ${escapeHtml(p)}</span>`)
    .join(" ");

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src ${webview.cspSource} 'nonce-${nonce}'; script-src 'nonce-${nonce}';">
<style nonce="${nonce}">
  :root {
    --gold: #FFD700;
    --gold-dim: #B8960F;
    --bg: var(--vscode-editor-background);
    --fg: var(--vscode-editor-foreground);
    --input-bg: var(--vscode-input-background);
    --input-fg: var(--vscode-input-foreground);
    --input-border: var(--vscode-input-border, #444);
    --btn-bg: var(--vscode-button-background);
    --btn-fg: var(--vscode-button-foreground);
    --btn-hover: var(--vscode-button-hoverBackground);
    --focus: var(--vscode-focusBorder);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: var(--vscode-font-family, system-ui, sans-serif);
    font-size: var(--vscode-font-size, 13px);
    color: var(--fg);
    background: var(--bg);
    padding: 16px 20px;
    line-height: 1.5;
  }

  /* Header */
  .header {
    border-bottom: 2px solid var(--gold);
    padding-bottom: 12px;
    margin-bottom: 20px;
  }
  .header h1 {
    font-size: 1.4em;
    color: var(--gold);
    margin-bottom: 4px;
  }
  .header .filename {
    font-size: 0.85em;
    opacity: 0.6;
  }
  .header .desc {
    margin-top: 6px;
    opacity: 0.8;
  }
  .badges {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.8em;
    font-weight: 600;
  }
  .badge.strategy { background: rgba(255, 165, 0, 0.2); color: #FFA500; }
  .badge.tool { background: rgba(0, 206, 209, 0.15); color: #00CED1; }
  .badge.prompt { background: rgba(0, 191, 255, 0.15); color: #00BFFF; }

  /* Form */
  .form-section {
    margin-bottom: 24px;
  }
  .form-section h2 {
    font-size: 1.05em;
    color: var(--gold-dim);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .field {
    margin-bottom: 16px;
  }
  .field label {
    display: block;
    margin-bottom: 4px;
    font-weight: 600;
  }
  .field label .directive-tag {
    font-weight: normal;
    font-size: 0.85em;
    opacity: 0.5;
    margin-left: 6px;
  }
  .field .hint {
    font-size: 0.85em;
    opacity: 0.6;
    margin-bottom: 4px;
  }

  input[type="text"],
  textarea,
  select {
    width: 100%;
    padding: 6px 10px;
    background: var(--input-bg);
    color: var(--input-fg);
    border: 1px solid var(--input-border);
    border-radius: 4px;
    font-family: inherit;
    font-size: inherit;
    outline: none;
  }
  input:focus, textarea:focus, select:focus {
    border-color: var(--focus);
  }
  textarea {
    min-height: 80px;
    resize: vertical;
  }
  select {
    cursor: pointer;
  }

  /* Toggle switch for booleans */
  .toggle-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .toggle {
    position: relative;
    width: 40px;
    height: 22px;
    cursor: pointer;
  }
  .toggle input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  .toggle .slider {
    position: absolute;
    inset: 0;
    background: var(--input-border);
    border-radius: 11px;
    transition: background 0.2s;
  }
  .toggle .slider::before {
    content: "";
    position: absolute;
    width: 16px;
    height: 16px;
    left: 3px;
    top: 3px;
    background: white;
    border-radius: 50%;
    transition: transform 0.2s;
  }
  .toggle input:checked + .slider {
    background: var(--gold);
  }
  .toggle input:checked + .slider::before {
    transform: translateX(18px);
  }

  /* Buttons */
  .actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    padding-top: 16px;
    border-top: 1px solid var(--input-border);
  }
  button {
    padding: 8px 18px;
    border: none;
    border-radius: 4px;
    font-family: inherit;
    font-size: inherit;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  button:hover { opacity: 0.85; }
  button:active { opacity: 0.7; }

  .btn-compose {
    background: var(--btn-bg);
    color: var(--btn-fg);
  }
  .btn-run {
    background: var(--gold);
    color: #1a1a1a;
  }
  .btn-tui {
    background: rgba(0, 191, 255, 0.2);
    color: #00BFFF;
    border: 1px solid rgba(0, 191, 255, 0.4);
  }
  .btn-refresh {
    margin-left: auto;
    background: transparent;
    color: var(--fg);
    opacity: 0.6;
    border: 1px solid var(--input-border);
  }

  /* Empty state */
  .empty {
    text-align: center;
    padding: 40px 20px;
    opacity: 0.5;
  }
  .empty .icon { font-size: 2em; margin-bottom: 8px; }
</style>
</head>
<body>

<div class="header">
  <h1>⚡ ${title}</h1>
  <div class="filename">${filename}</div>
  ${desc ? `<div class="desc">${desc}</div>` : ""}
  <div class="badges">
    ${strategyBadge}
    ${toolBadges}
    ${promptBadges}
  </div>
</div>

${
  (metadata.inputs || []).length === 0
    ? `<div class="empty">
        <div class="icon">✨</div>
        <p>This spec has no variables to fill in.<br>You can run it directly.</p>
      </div>`
    : `<div class="form-section">
        <h2>Variables</h2>
        ${inputsHtml}
      </div>`
}

<div class="actions">
  <button id="compose" class="btn-compose" title="Compile the spec">▶ Compose</button>
  <button id="run" class="btn-run" title="Compile and execute via LLM">🚀 Run</button>
  <button id="openTUI" class="btn-tui" title="Open in interactive TUI">🖥 TUI</button>
  <button id="refresh" class="btn-refresh" title="Re-scan the promplet file">↻ Refresh</button>
</div>

<script nonce="${nonce}">
  const vscode = acquireVsCodeApi();

  function getValues() {
    const values = {};
    document.querySelectorAll('[data-field]').forEach(el => {
      const name = el.dataset.field;
      if (el.type === 'checkbox') {
        values[name] = el.checked ? 'true' : 'false';
      } else {
        values[name] = el.value;
      }
    });
    return values;
  }

  for (const command of ['compose', 'run', 'openTUI']) {
    document.getElementById(command).addEventListener('click', () => {
      vscode.postMessage({ command, values: getValues() });
    });
  }
  document.getElementById('refresh').addEventListener('click', () => {
    vscode.postMessage({ command: 'refresh' });
  });
  document.querySelectorAll('input[type="checkbox"][data-field]').forEach(input => {
    input.addEventListener('change', () => {
      const label = input.closest('.toggle-row').querySelector('.toggle-label');
      label.textContent = input.checked ? 'Enabled' : 'Disabled';
    });
  });
</script>

</body>
</html>`;
}

function buildInputHtml(input) {
  const name = escapeHtml(input.name);
  const fieldId = `field-${name}`;
  const label = escapeHtml(formatLabel(input.name));
  const directive = input.source_directive
    ? `<span class="directive-tag">(${escapeHtml(input.source_directive)})</span>`
    : "";
  const hint = input.description
    ? `<div class="hint">${escapeHtml(input.description)}</div>`
    : "";
  const defaultVal = input.default ?? "";

  switch (input.input_type) {
    case "select": {
      const opts = (input.options || [])
        .map(
          (o) =>
            `<option value="${escapeHtml(o)}"${
              o === defaultVal ? " selected" : ""
            }>${escapeHtml(o)}</option>`
        )
        .join("\n");
      return `<div class="field">
        <label for="${fieldId}">${label} ${directive}</label>
        ${hint}
        <select id="${fieldId}" data-field="${name}">
          <option value="">— select —</option>
          ${opts}
        </select>
      </div>`;
    }

    case "boolean":
      return `<div class="field">
        <label>${label} ${directive}</label>
        ${hint}
        <div class="toggle-row">
          <label class="toggle">
            <input id="${fieldId}" type="checkbox" data-field="${name}" ${
        defaultVal === "true" ? "checked" : ""
      }>
            <span class="slider"></span>
          </label>
          <span class="toggle-label">${
            defaultVal === "true" ? "Enabled" : "Disabled"
          }</span>
        </div>
      </div>`;

    case "multiline":
      return `<div class="field">
        <label for="${fieldId}">${label} ${directive}</label>
        ${hint}
        <textarea id="${fieldId}" data-field="${name}" placeholder="Enter ${label.toLowerCase()}…" rows="4">${escapeHtml(
        defaultVal
      )}</textarea>
      </div>`;

    case "file":
      return `<div class="field">
        <label for="${fieldId}">${label} ${directive}</label>
        ${hint}
        <input id="${fieldId}" type="text" data-field="${name}" placeholder="${
        escapeHtml(input.file_hint || "Path to file…")
      }" value="${escapeHtml(defaultVal)}">
      </div>`;

    default:
      // text
      return `<div class="field">
        <label for="${fieldId}">${label} ${directive}</label>
        ${hint}
        <input id="${fieldId}" type="text" data-field="${name}" placeholder="Enter ${label.toLowerCase()}…" value="${escapeHtml(
        defaultVal
      )}">
      </div>`;
  }
}

function formatLabel(name) {
  return name
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function isMessage(message) {
  return (
    message !== null &&
    typeof message === "object" &&
    !Array.isArray(message) &&
    ["compose", "run", "openTUI", "refresh"].includes(message.command)
  );
}

function validateFormValues(values, inputs) {
  if (!values || typeof values !== "object" || Array.isArray(values)) {
    return null;
  }
  const allowed = new Set(
    inputs
      .map((input) => input?.name)
      .filter((name) => typeof name === "string" && /^[A-Za-z_][\w.-]*$/.test(name))
  );
  const entries = Object.entries(values);
  if (entries.length > allowed.size) return null;

  let totalLength = 0;
  const validated = Object.create(null);
  for (const [name, value] of entries) {
    if (!allowed.has(name) || typeof value !== "string") return null;
    totalLength += value.length;
    if (value.length > 100_000 || totalLength > 1_000_000) return null;
    validated[name] = value;
  }
  return validated;
}

// ── Registration ────────────────────────────────────────────────

function registerFormPanel(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("weavemark.fillForm", openFormPanel)
  );
}

module.exports = {
  buildFormHtml,
  registerFormPanel,
  validateFormValues,
};
