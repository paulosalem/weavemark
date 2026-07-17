// WeaveMark — Diagnostics provider
//
// Reports problems:
//   • Unknown directives
//   • Unclosed @{ variable placeholders
//   • @match without default (_ ==>) case
//   • @refine pointing to a non-existent file
//   • @if without matching content
//   • @execute with unknown strategy

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const { ALL_DIRECTIVE_NAMES, EXECUTION_STRATEGIES } = require("./directives");
const {
  analyzeSource,
  findDirectiveToken,
  isKnownDirective,
} = require("./language");

const DIAGNOSTIC_SOURCE = "WeaveMark";

function createDiagnosticsProvider(context) {
  const collection = vscode.languages.createDiagnosticCollection("weavemark");
  context.subscriptions.push(collection);
  const pendingUpdates = new Map();

  function updateDiagnostics(document) {
    if (document.languageId !== "weavemark") {
      collection.delete(document.uri);
      return;
    }

    const diagnostics = [];
    const text = document.getText();
    const analysis = analyzeSource(text);
    const lines = analysis.lines;
    let inMatchBlock = false;
    let matchHasDefault = false;
    let matchLine = -1;
    let matchIndent = 0;
    let currentPromptScope = "default";
    let currentPromptIndent = -1;
    let seenCompile = false;
    let seenExecution = false;
    const seenPrompts = new Set();
    const seenTools = new Set();
    const seenOutputs = new Set();
    const seenPackages = new Set();

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (analysis.ignoredLines.has(i)) continue;
      const stripped = line.trimStart();
      const indent = line.length - stripped.length;
      if (
        currentPromptScope !== "default" &&
        stripped !== "" &&
        indent <= currentPromptIndent
      ) {
        currentPromptScope = "default";
        currentPromptIndent = -1;
      }

      // ── Unknown directive ──────────────────────────────────
      const directiveToken = findDirectiveToken(line);
      if (directiveToken) {
        const fullName = directiveToken.name;
        if (!isKnownDirective(fullName, ALL_DIRECTIVE_NAMES, analysis)) {
          const range = new vscode.Range(
            i,
            directiveToken.start,
            i,
            directiveToken.start + directiveToken.tokenLength
          );
          diagnostics.push(
            new vscode.Diagnostic(
              range,
              `Unknown directive: @${fullName}`,
              vscode.DiagnosticSeverity.Error
            )
          );
        }
      }

      // ── Duplicate declarations ───────────────────────────────
      if (/^\s*@compile\b/.test(line)) {
        if (seenCompile) {
          diagnostics.push(duplicateDiagnostic(i, line, "@compile"));
        }
        seenCompile = true;
      }
      if (/^\s*@execute\b/.test(line)) {
        if (seenExecution) {
          diagnostics.push(duplicateDiagnostic(i, line, "@execute"));
        }
        seenExecution = true;
      }
      const promptMatch = line.match(/^(\s*)@prompt\s+([A-Za-z_][\w.-]*)/);
      if (promptMatch) {
        const key = promptMatch[2].toLowerCase();
        if (seenPrompts.has(key)) {
          diagnostics.push(
            duplicateDiagnostic(i, line, `@prompt ${promptMatch[2]}`)
          );
        }
        seenPrompts.add(key);
        currentPromptScope = key;
        currentPromptIndent = promptMatch[1].length;
      }
      const toolMatch = line.match(/^\s*@tool\s+([A-Za-z_][\w.-]*)/);
      if (toolMatch) {
        const key = toolMatch[1].toLowerCase();
        if (seenTools.has(key)) {
          diagnostics.push(
            duplicateDiagnostic(i, line, `@tool ${toolMatch[1]}`)
          );
        }
        seenTools.add(key);
      }
      if (/^\s*@output\b/.test(line)) {
        if (seenOutputs.has(currentPromptScope)) {
          diagnostics.push(
            duplicateDiagnostic(
              i,
              line,
              `@output for ${currentPromptScope}`
            )
          );
        }
        seenOutputs.add(currentPromptScope);
      }
      const packageMatch = line.match(
        /^\s*@package\b.*\bfile:\s*(?:"([^"]+)"|'([^']+)'|(\S+))/
      );
      if (packageMatch) {
        const target = packageMatch[1] || packageMatch[2] || packageMatch[3];
        const key = target.toLowerCase();
        if (seenPackages.has(key)) {
          diagnostics.push(
            duplicateDiagnostic(i, line, `@package file ${target}`)
          );
        }
        seenPackages.add(key);
      }

      // ── Import clause spelling ──────────────────────────────
      const badImportClause = line.match(/^\s*@use\b.*\b(expose|only)\b/);
      if (badImportClause) {
        const keyword = badImportClause[1];
        const col = line.indexOf(keyword);
        diagnostics.push(
          new vscode.Diagnostic(
            new vscode.Range(i, col, i, col + keyword.length),
            keyword === "expose"
              ? "Use `exposing`, not `expose`, to import selected definitions."
              : "Use `exposing` for selected imports.",
            vscode.DiagnosticSeverity.Warning
          )
        );
      }

      // ── Old @prompt as: parameter ────────────────────────────
      const promptAs = line.match(/^\s*@prompt\b.*\bas\s*:/);
      if (promptAs) {
        const col = line.search(/\bas\s*:/);
        diagnostics.push(
          new vscode.Diagnostic(
            new vscode.Range(i, col, i, col + promptAs[0].slice(col).match(/^as\s*:/)[0].length),
            "`@prompt as:` was replaced by `format:`. `as:` is reserved for semantic/execution result bindings.",
            vscode.DiagnosticSeverity.Warning
          )
        );
      }

      // ── Unknown execution strategy ────────────────────────
      const execMatch = line.match(/^\s*@execute\s+(\S+)/);
      if (execMatch) {
        const strategy = execMatch[1];
        if (!EXECUTION_STRATEGIES.includes(strategy)) {
          const col = line.indexOf(strategy);
          const range = new vscode.Range(i, col, i, col + strategy.length);
          diagnostics.push(
            new vscode.Diagnostic(
              range,
              `Unknown execution strategy: "${strategy}". Expected: ${EXECUTION_STRATEGIES.join(", ")}`,
              vscode.DiagnosticSeverity.Warning
            )
          );
        }
      }

      // ── @match block tracking ─────────────────────────────
      const matchDirective = line.match(/^(\s*)@match\s+/);
      if (matchDirective) {
        // Close previous match block if open
        if (inMatchBlock && !matchHasDefault) {
          diagnostics.push(
            new vscode.Diagnostic(
              new vscode.Range(matchLine, 0, matchLine, lines[matchLine].length),
              "@match block has no default case (_ ==>). Add a fallback to handle unexpected values.",
              vscode.DiagnosticSeverity.Hint
            )
          );
        }
        inMatchBlock = true;
        matchHasDefault = false;
        matchLine = i;
        matchIndent = matchDirective[1].length;
      }

      // Check for default case in match
      if (inMatchBlock && /^\s*_\s*==>/.test(line)) {
        matchHasDefault = true;
      }

      // End match block on same-or-less indent directive
      if (inMatchBlock && i > matchLine) {
        const nonWs = line.search(/\S/);
        if (nonWs >= 0 && nonWs <= matchIndent && /^(\s*)@[A-Za-z_][\w.-]*/.test(line)) {
          if (!matchHasDefault) {
            diagnostics.push(
              new vscode.Diagnostic(
                new vscode.Range(matchLine, 0, matchLine, lines[matchLine].length),
                "@match block has no default case (_ ==>). Add a fallback to handle unexpected values.",
                vscode.DiagnosticSeverity.Hint
              )
            );
          }
          inMatchBlock = false;
        }
      }

      // ── Unclosed @{ variable placeholder ─────────────────
      const opens = (line.match(/@\{/g) || []).length;
      const closes = (line.match(/}/g) || []).length;
      if (opens > closes) {
        const idx = line.lastIndexOf("@{");
        diagnostics.push(
          new vscode.Diagnostic(
            new vscode.Range(i, idx, i, idx + 2),
            "Unclosed `@{` — missing closing `}`",
            vscode.DiagnosticSeverity.Error
          )
        );
      }

      // ── @refine file existence ─────────────────────────────
      const refineMatch = line.match(
        /^\s*@refine\s+(?:"([^"]+)"|'([^']+)'|(\S+))/
      );
      if (refineMatch) {
        const filePath = refineMatch[1] || refineMatch[2] || refineMatch[3];
        if (
          filePath.startsWith("module:") ||
          /^[A-Za-z_][\w-]*:/.test(filePath)
        ) {
          continue;
        }
        const docDir = path.dirname(document.uri.fsPath);
        const absPath = path.resolve(docDir, filePath);
        if (!fs.existsSync(absPath)) {
          const col = line.indexOf(filePath);
          const range = new vscode.Range(i, col, i, col + filePath.length);
          diagnostics.push(
            new vscode.Diagnostic(
              range,
              `File not found: ${filePath}`,
              vscode.DiagnosticSeverity.Error
            )
          );
        }
      }
    }

    // Final match block at end of file
    if (inMatchBlock && !matchHasDefault) {
      diagnostics.push(
        new vscode.Diagnostic(
          new vscode.Range(matchLine, 0, matchLine, lines[matchLine].length),
          "@match block has no default case (_ ==>). Add a fallback to handle unexpected values.",
          vscode.DiagnosticSeverity.Hint
        )
      );
    }

    for (const d of diagnostics) {
      d.source = DIAGNOSTIC_SOURCE;
    }
    collection.set(document.uri, diagnostics);
  }

  function scheduleUpdate(document) {
    const key = document.uri.toString();
    clearTimeout(pendingUpdates.get(key));
    pendingUpdates.set(
      key,
      setTimeout(() => {
        pendingUpdates.delete(key);
        updateDiagnostics(document);
      }, 200)
    );
  }

  // Run on open, save, and change
  if (vscode.window.activeTextEditor) {
    updateDiagnostics(vscode.window.activeTextEditor.document);
  }

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor) updateDiagnostics(editor.document);
    }),
    vscode.workspace.onDidChangeTextDocument((event) => {
      scheduleUpdate(event.document);
    }),
    vscode.workspace.onDidSaveTextDocument((document) => {
      updateDiagnostics(document);
    }),
    vscode.workspace.onDidCloseTextDocument((doc) => {
      const key = doc.uri.toString();
      clearTimeout(pendingUpdates.get(key));
      pendingUpdates.delete(key);
      collection.delete(doc.uri);
    }),
    {
      dispose() {
        for (const timeout of pendingUpdates.values()) {
          clearTimeout(timeout);
        }
        pendingUpdates.clear();
      },
    }
  );

  return collection;
}

function duplicateDiagnostic(lineNumber, line, declaration) {
  return new vscode.Diagnostic(
    new vscode.Range(lineNumber, 0, lineNumber, line.length),
    `Duplicate declaration: ${declaration}`,
    vscode.DiagnosticSeverity.Error
  );
}

module.exports = { createDiagnosticsProvider };
