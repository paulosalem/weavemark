// WeaveMark — VS Code extension
//
// Features:
//   • Visual decorations (borders, backgrounds, variable pills)
//   • Completions for directives, parameters, variables, file paths
//   • Hover documentation for directives, variables, strategies
//   • Diagnostics (unknown directives, unclosed @{, missing files)
//   • Go-to-definition for @refine file references
//   • Document symbols (Outline view & breadcrumbs)
//   • Smart folding for directive blocks

const vscode = require("vscode");
const { WeaveMarkCompletionProvider, TRIGGER_CHARACTERS } = require("./completions");
const { WeaveMarkHoverProvider } = require("./hovers");
const { createDiagnosticsProvider } = require("./diagnostics");
const { WeaveMarkDefinitionProvider } = require("./definitions");
const { WeaveMarkDocumentSymbolProvider } = require("./symbols");
const { WeaveMarkFoldingRangeProvider } = require("./folding");
const { registerRunCommands } = require("./run");
const { registerFormPanel } = require("./form");
const { analyzeSource } = require("./language");

// ── Decoration types ────────────────────────────────────────────

function createDecorations() {
  const execute = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "#FFD700",
    backgroundColor: "rgba(255, 215, 0, 0.07)",
    overviewRulerColor: "#FFD700",
    overviewRulerLane: vscode.OverviewRulerLane.Left,
    before: {
      contentText: " ",
      width: "6px",
    },
  });

  const executeParam = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "rgba(255, 215, 0, 0.3)",
    backgroundColor: "rgba(255, 215, 0, 0.03)",
    before: {
      contentText: " ",
      width: "6px",
    },
  });

  const prompt = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "#00BFFF",
    backgroundColor: "rgba(0, 191, 255, 0.07)",
    overviewRulerColor: "#00BFFF",
    overviewRulerLane: vscode.OverviewRulerLane.Left,
    before: {
      contentText: " ",
      width: "6px",
    },
  });

  const tool = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "#00CED1",
    backgroundColor: "rgba(0, 206, 209, 0.05)",
    before: { contentText: " ", width: "6px" },
  });

  const definition = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "#50FA7B",
    backgroundColor: "rgba(80, 250, 123, 0.05)",
    before: { contentText: " ", width: "6px" },
  });

  const moduleImport = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "#8BE9FD",
    backgroundColor: "rgba(139, 233, 253, 0.05)",
    before: { contentText: " ", width: "6px" },
  });

  const bind = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "#FFB86C",
    backgroundColor: "rgba(255, 184, 108, 0.05)",
    before: { contentText: " ", width: "6px" },
  });

  const emitInput = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 3px",
    borderStyle: "solid",
    borderColor: "#DA70D6",
    backgroundColor: "rgba(218, 112, 214, 0.05)",
    before: { contentText: " ", width: "6px" },
  });

  const controlFlow = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 2px",
    borderStyle: "solid",
    borderColor: "#FF79C6",
    before: { contentText: " ", width: "6px" },
  });

  const matchCase = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 2px",
    borderStyle: "solid",
    borderColor: "#B34040",
    backgroundColor: "rgba(179, 64, 64, 0.04)",
    before: { contentText: " ", width: "6px" },
  });

  const noteBlock = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 1px",
    borderStyle: "dotted",
    borderColor: "#6272A4",
    backgroundColor: "rgba(98, 114, 164, 0.06)",
    opacity: "0.7",
    before: { contentText: " ", width: "6px" },
  });

  const variable = vscode.window.createTextEditorDecorationType({
    backgroundColor: "rgba(255, 184, 108, 0.12)",
    borderRadius: "3px",
  });

  const surface = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    borderWidth: "0 0 0 2px",
    borderStyle: "solid",
    borderColor: "#BD93F9",
    backgroundColor: "rgba(189, 147, 249, 0.04)",
    before: { contentText: " ", width: "6px" },
  });

  return {
    execute,
    executeParam,
    prompt,
    tool,
    definition,
    moduleImport,
    bind,
    emitInput,
    controlFlow,
    matchCase,
    noteBlock,
    variable,
    surface,
  };
}

// ── Regex patterns ──────────────────────────────────────────────

const RE_EXECUTE = /^\s*@execute\b/;
const RE_EXECUTE_PARAM = /^\s{2,}\w+:\s*.+/; // indented key: value after @execute
const RE_PROMPT = /^\s*@prompt\b/;
const RE_TOOL = /^\s*@tool\b/;
const RE_DEFINITION = /^\s*@(?:define|param|phase|scope|returns|effect|body)\b/;
const RE_MODULE_IMPORT = /^\s*@(?:module|use|include)\b/;
const RE_BIND = /^\s*@bind\b/;
const RE_EMIT_INPUT = /^\s*@(?:emit|embed|output|package)\b/;
const RE_CONTROL = /^\s*@(?:match|if|else_if|else)\b/;
const RE_MATCH_CASE = /^\s*(?:"[^"]*"|_)\s*==>/;
const RE_NOTE_START = /^\s*@note\s*$/;
const RE_VARIABLE = /@\{[^}]+\}/g;
const RE_SURFACE = /^\s*(?:#{1,6}\s+@[A-Za-z_][\w.-]*|>\s*\[!PROMPLET\b)/;

// ── Update decorations ─────────────────────────────────────────

function updateDecorations(editor, decs) {
  if (!editor || editor.document.languageId !== "weavemark") return;

  const doc = editor.document;
  const sourceAnalysis = analyzeSource(doc.getText());
  const executeRanges = [];
  const executeParamRanges = [];
  const promptRanges = [];
  const toolRanges = [];
  const definitionRanges = [];
  const moduleImportRanges = [];
  const bindRanges = [];
  const emitInputRanges = [];
  const controlRanges = [];
  const matchCaseRanges = [];
  const noteRanges = [];
  const variableRanges = [];
  const surfaceRanges = [];

  let inNote = false;
  let noteIndent = 0;
  let lastWasExecute = false;

  for (let i = 0; i < doc.lineCount; i++) {
    const line = doc.lineAt(i);
    const text = line.text;
    const range = line.range;
    if (sourceAnalysis.literalLines.has(i)) {
      continue;
    }

    // Track @note blocks
    if (RE_NOTE_START.test(text)) {
      inNote = true;
      noteIndent = text.search(/\S/);
      noteRanges.push(range);
      lastWasExecute = false;
      continue;
    }
    if (inNote) {
      // Note block continues while indented deeper or blank
      const nonWs = text.search(/\S/);
      if (text.trim() === "" || nonWs > noteIndent) {
        noteRanges.push(range);
        continue;
      }
      inNote = false;
    }

    // @execute line and its indented params
    if (RE_EXECUTE.test(text)) {
      executeRanges.push(range);
      lastWasExecute = true;
    } else if (lastWasExecute && RE_EXECUTE_PARAM.test(text)) {
      executeParamRanges.push(range);
    } else {
      lastWasExecute = false;

      if (RE_PROMPT.test(text)) {
        promptRanges.push(range);
      } else if (RE_TOOL.test(text)) {
        toolRanges.push(range);
      } else if (RE_DEFINITION.test(text)) {
        definitionRanges.push(range);
      } else if (RE_MODULE_IMPORT.test(text)) {
        moduleImportRanges.push(range);
      } else if (RE_BIND.test(text)) {
        bindRanges.push(range);
      } else if (RE_EMIT_INPUT.test(text)) {
        emitInputRanges.push(range);
      } else if (RE_CONTROL.test(text)) {
        controlRanges.push(range);
      } else if (RE_MATCH_CASE.test(text)) {
        matchCaseRanges.push(range);
      } else if (RE_SURFACE.test(text)) {
        surfaceRanges.push(range);
      }
    }

    // @{variables} on any line
    let m;
    RE_VARIABLE.lastIndex = 0;
    while ((m = RE_VARIABLE.exec(text)) !== null) {
      const start = new vscode.Position(i, m.index);
      const end = new vscode.Position(i, m.index + m[0].length);
      variableRanges.push(new vscode.Range(start, end));
    }
  }

  editor.setDecorations(decs.execute, executeRanges);
  editor.setDecorations(decs.executeParam, executeParamRanges);
  editor.setDecorations(decs.prompt, promptRanges);
  editor.setDecorations(decs.tool, toolRanges);
  editor.setDecorations(decs.definition, definitionRanges);
  editor.setDecorations(decs.moduleImport, moduleImportRanges);
  editor.setDecorations(decs.bind, bindRanges);
  editor.setDecorations(decs.emitInput, emitInputRanges);
  editor.setDecorations(decs.controlFlow, controlRanges);
  editor.setDecorations(decs.matchCase, matchCaseRanges);
  editor.setDecorations(decs.noteBlock, noteRanges);
  editor.setDecorations(decs.variable, variableRanges);
  editor.setDecorations(decs.surface, surfaceRanges);
}

// ── Lifecycle ───────────────────────────────────────────────────

/** @param {vscode.ExtensionContext} context */
function activate(context) {
  const selector = { language: "weavemark", scheme: "file" };
  const decs = createDecorations();

  // ── Decorations ────────────────────────────────────────────
  if (vscode.window.activeTextEditor) {
    updateDecorations(vscode.window.activeTextEditor, decs);
  }

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor) updateDecorations(editor, decs);
    })
  );

  let timeout;
  context.subscriptions.push({
    dispose() {
      clearTimeout(timeout);
    },
  });
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument((event) => {
      const editor = vscode.window.activeTextEditor;
      if (editor && event.document === editor.document) {
        clearTimeout(timeout);
        timeout = setTimeout(() => updateDecorations(editor, decs), 150);
      }
    })
  );

  context.subscriptions.push(...Object.values(decs));

  // ── Completions ────────────────────────────────────────────
  context.subscriptions.push(
    vscode.languages.registerCompletionItemProvider(
      selector,
      new WeaveMarkCompletionProvider(),
      ...TRIGGER_CHARACTERS
    )
  );

  // ── Hovers ─────────────────────────────────────────────────
  context.subscriptions.push(
    vscode.languages.registerHoverProvider(selector, new WeaveMarkHoverProvider())
  );

  // ── Diagnostics ────────────────────────────────────────────
  createDiagnosticsProvider(context);

  // ── Go-to-definition ──────────────────────────────────────
  context.subscriptions.push(
    vscode.languages.registerDefinitionProvider(selector, new WeaveMarkDefinitionProvider())
  );

  // ── Document symbols (Outline) ────────────────────────────
  context.subscriptions.push(
    vscode.languages.registerDocumentSymbolProvider(selector, new WeaveMarkDocumentSymbolProvider())
  );

  // ── Folding ────────────────────────────────────────────────
  context.subscriptions.push(
    vscode.languages.registerFoldingRangeProvider(selector, new WeaveMarkFoldingRangeProvider())
  );

  // ── Run commands (terminal integration) ────────────────────
  registerRunCommands(context);

  // ── Form panel (webview) ───────────────────────────────────
  registerFormPanel(context);
}

function deactivate() {}

module.exports = { activate, deactivate };
