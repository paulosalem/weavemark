const assert = require("node:assert/strict");
const test = require("node:test");
const { loadWithVscodeMock } = require("./helpers");

class Range {
  constructor(startLine, startCharacter, endLine, endCharacter) {
    this.start = { line: startLine, character: startCharacter };
    this.end = { line: endLine, character: endCharacter };
  }
}

class Diagnostic {
  constructor(range, message, severity) {
    this.range = range;
    this.message = message;
    this.severity = severity;
  }
}

function createDocument(text) {
  return {
    languageId: "weavemark",
    uri: { fsPath: "/workspace/spec.weavemark.md", toString: () => "spec" },
    getText: () => text,
  };
}

test("diagnostics match current declarations and ignore literal regions", () => {
  const text = [
    "```weavemark",
    "@fenced_unknown",
    "```",
    "@note",
    "  @note_unknown",
    "@define custom_rule",
    "@custom_rule",
    "@use company.rules as rules",
    "@rules.qualified",
    "@unknown_rule",
    "@compile format: json",
    "@compile format: markdown",
    "@prompt Intro",
    "  First.",
    "@prompt intro",
    "  Second.",
    "@tool Search",
    "  First.",
    "@tool search",
    "  Second.",
    "@package template: one.md file: out.html",
    "@package template: two.md file: out.html",
    "@refine module:weavemark.std.reasoning.base_analyst",
  ].join("\n");
  const document = createDocument(text);
  const collection = {
    diagnostics: [],
    delete() {},
    set(_uri, diagnostics) {
      this.diagnostics = diagnostics;
    },
  };
  const disposable = { dispose() {} };
  const vscode = {
    Diagnostic,
    DiagnosticSeverity: { Error: 0, Warning: 1, Hint: 2 },
    Range,
    languages: {
      createDiagnosticCollection: () => collection,
    },
    window: {
      activeTextEditor: { document },
      onDidChangeActiveTextEditor: () => disposable,
    },
    workspace: {
      onDidChangeTextDocument: () => disposable,
      onDidSaveTextDocument: () => disposable,
      onDidCloseTextDocument: () => disposable,
    },
  };
  const { createDiagnosticsProvider } = loadWithVscodeMock(
    "src/diagnostics.js",
    vscode
  );
  const context = { subscriptions: { push() {} } };

  createDiagnosticsProvider(context);

  assert.deepEqual(
    collection.diagnostics.map((diagnostic) => diagnostic.message),
    [
      "Unknown directive: @unknown_rule",
      "Duplicate declaration: @compile",
      "Duplicate declaration: @prompt intro",
      "Duplicate declaration: @tool search",
      "Duplicate declaration: @package file out.html",
    ]
  );
  assert.equal(
    collection.diagnostics.every(
      (diagnostic) => diagnostic.severity === vscode.DiagnosticSeverity.Error
    ),
    true
  );
});
