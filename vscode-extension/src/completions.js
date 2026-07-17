// WeaveMark — Completion provider
//
// Provides:
//   • Directive completions when typing "@"
//   • Parameter value completions (key: value)
//   • Variable completions when typing "@{"
//   • File path completions for @refine
//   • Execution strategy completions for @execute
//   • Match case snippet

const vscode = require("vscode");
const path = require("path");
const {
  DIRECTIVES,
  DEBUG_DIRECTIVES,
  EXECUTION_STRATEGIES,
  IMPORT_CLAUSES,
  STANDARD_DEFINITIONS,
} = require("./directives");
const { analyzeSource } = require("./language");

// ── Directive completions ───────────────────────────────────────

function createDirectiveCompletions(document, position, prefix) {
  // Calculate the range that includes the "@" already typed
  const atCol = prefix.lastIndexOf("@");
  const replaceRange = new vscode.Range(position.line, atCol, position.line, position.character);

  const items = [];
  for (const [name, info] of Object.entries(DIRECTIVES)) {
    const item = new vscode.CompletionItem(info.label, vscode.CompletionItemKind.Keyword);
    item.detail = info.detail;
    item.documentation = new vscode.MarkdownString(info.documentation);
    item.insertText = new vscode.SnippetString(info.snippet);
    item.filterText = `@${name}`;
    item.sortText = `0-${info.category}-${name}`;
    item.range = replaceRange;
    items.push(item);
  }
  for (const [name, info] of Object.entries(DEBUG_DIRECTIVES)) {
    const item = new vscode.CompletionItem(info.label, vscode.CompletionItemKind.Function);
    item.detail = info.detail;
    item.documentation = new vscode.MarkdownString(info.documentation);
    item.insertText = new vscode.SnippetString(info.snippet);
    item.filterText = `@${name}`;
    item.sortText = `1-debug-${name}`;
    item.range = replaceRange;
    items.push(item);
  }
  const analysis = analyzeSource(document.getText());
  for (const name of analysis.declaredDirectives) {
    if (DIRECTIVES[name] || DEBUG_DIRECTIVES[name]) continue;
    const item = new vscode.CompletionItem(
      `@${name}`,
      vscode.CompletionItemKind.Function
    );
    item.detail = "Local or exposed WeaveMark definition";
    item.insertText = `@${name}`;
    item.filterText = `@${name}`;
    item.range = replaceRange;
    items.push(item);
  }
  for (const alias of analysis.moduleAliases) {
    const item = new vscode.CompletionItem(
      `@${alias}.`,
      vscode.CompletionItemKind.Module
    );
    item.detail = "Qualified definition from imported module";
    item.insertText = new vscode.SnippetString(`@${alias}.\${1:definition}`);
    item.filterText = `@${alias}.`;
    item.range = replaceRange;
    items.push(item);
  }
  return items;
}

// ── Variable scanning ───────────────────────────────────────────

function collectVariables(document) {
  const vars = new Set();
  const re = /@\{([A-Za-z_][\w.-]*)\}/g;
  const analysis = analyzeSource(document.getText());
  const text = analysis.lines
    .map((line, index) => (analysis.literalLines.has(index) ? "" : line))
    .join("\n");
  let m;
  while ((m = re.exec(text)) !== null) {
    vars.add(m[1]);
  }
  // Also collect variables from @match and @if lines
  const directiveVars = /^\s*@(?:match|if)\s+([A-Za-z_][\w.-]*)/gm;
  while ((m = directiveVars.exec(text)) !== null) {
    vars.add(m[1]);
  }
  return vars;
}

// ── Match-case snippet ─────────────────────────────────────────

function createMatchCaseSnippet() {
  const item = new vscode.CompletionItem('"value" ==>', vscode.CompletionItemKind.Snippet);
  item.detail = "Match case branch";
  item.documentation = new vscode.MarkdownString(
    "A case branch inside a `@match` block.\n\n" +
      '`"value" ==>` matches the literal value.\n' +
      "`_ ==>` is the default/fallback case."
  );
  item.insertText = new vscode.SnippetString('"${1:value}" ==>\n    ${2:content}');
  item.sortText = "2-match-case";
  return item;
}

function createDefaultCaseSnippet() {
  const item = new vscode.CompletionItem("_ ==>", vscode.CompletionItemKind.Snippet);
  item.detail = "Default match case (fallback)";
  item.documentation = new vscode.MarkdownString("The default/fallback case in a `@match` block.");
  item.insertText = new vscode.SnippetString("_ ==>\n    ${1:default content}");
  item.sortText = "2-match-default";
  return item;
}

function createImportClauseCompletions() {
  return IMPORT_CLAUSES.map((clause) => {
    const item = new vscode.CompletionItem(clause, vscode.CompletionItemKind.Keyword);
    item.detail = clause === "exposing" ? "Expose selected definitions directly" : "Alias the imported module";
    item.insertText =
      clause === "exposing"
        ? new vscode.SnippetString("exposing ${1:refine}")
        : new vscode.SnippetString("as ${1:alias}");
    item.sortText = `0-import-${clause}`;
    return item;
  });
}

function createExposedDefinitionCompletions() {
  return STANDARD_DEFINITIONS.map((name) => {
    const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Function);
    item.detail = "Importable semantics definition";
    item.insertText = name;
    item.sortText = `1-stdlib-${name}`;
    return item;
  });
}

// ── Provider ────────────────────────────────────────────────────

class WeaveMarkCompletionProvider {
  provideCompletionItems(document, position, _token, _context) {
    if (analyzeSource(document.getText()).ignoredLines.has(position.line)) {
      return undefined;
    }
    const line = document.lineAt(position).text;
    const prefix = line.substring(0, position.character);

    // 1. Typing "@" at line start → directive completions
    if (/^\s*@[A-Za-z_][\w.-]*$/.test(prefix) || /^\s*@$/.test(prefix)) {
      return createDirectiveCompletions(document, position, prefix);
    }

    // 2. After @execute <strategy> or on @execute line → strategy names
    if (/^\s*@execute\s+\S*$/.test(prefix)) {
      return EXECUTION_STRATEGIES.map((s) => {
        const item = new vscode.CompletionItem(s, vscode.CompletionItemKind.EnumMember);
        item.detail = `Execution strategy`;
        return item;
      });
    }

    // 3. Module names for imports/includes
    if (/^\s*@(use|include)\s+[A-Za-z_][\w.-]*$/.test(prefix)) {
      return this._getModuleCompletions(document);
    }

    // 4. Parameter value completions: "key: " → suggest values
    const kvMatch = prefix.match(/^\s+([A-Za-z_][\w.-]*):\s*(\S*)$/);
    if (kvMatch) {
      // Check preceding lines for the directive
      for (let i = position.line - 1; i >= 0 && i >= position.line - 5; i--) {
        const prevLine = document.lineAt(i).text;
        const dirMatch = prevLine.match(/^\s*@([A-Za-z_][\w.-]*)/);
        if (dirMatch) {
          const directive = DIRECTIVES[dirMatch[1]];
          const values = directive && directive.params[kvMatch[1]];
          if (Array.isArray(values)) {
            return values.map((v) => {
              const item = new vscode.CompletionItem(v, vscode.CompletionItemKind.Value);
              item.detail = `${kvMatch[1]} value`;
              return item;
            });
          }
          break;
        }
      }
    }

    // 5. Inline parameter completions on directive line: @directive ... key:
    const inlineKvMatch = prefix.match(/^\s*@([A-Za-z_][\w.-]*)\s+.*?([A-Za-z_][\w.-]*):\s*(\S*)$/);
    if (inlineKvMatch) {
      const directive = DIRECTIVES[inlineKvMatch[1]];
      const values = directive && directive.params[inlineKvMatch[2]];
      if (Array.isArray(values)) {
        return values.map((v) => {
          const item = new vscode.CompletionItem(v, vscode.CompletionItemKind.Value);
          item.detail = `${inlineKvMatch[2]} value`;
          return item;
        });
      }
    }

    // 6. Variable completions when typing @{
    if (/@\{[A-Za-z_][\w.-]*$/.test(prefix) || /@\{$/.test(prefix)) {
      const vars = collectVariables(document);
      return [...vars].map((v) => {
        const item = new vscode.CompletionItem(v, vscode.CompletionItemKind.Variable);
        item.detail = "WeaveMark variable";
        return item;
      });
    }

    // 7. @use import clauses and exposed stdlib definitions
    if (/^\s*@use\s+[A-Za-z_][\w.-]*\s+exposing(?:\s+[\w.,\s-]*)?$/.test(prefix)) {
      return createExposedDefinitionCompletions();
    }
    if (/^\s*@use\s+[A-Za-z_][\w.-]*\s+(?:[A-Za-z]*)?$/.test(prefix)) {
      return createImportClauseCompletions();
    }

    // 8. Inside @match block → case snippets
    if (/^\s{2,}$/.test(prefix) || /^\s{2,}["_]/.test(prefix)) {
      // Check if we're inside a @match block
      for (let i = position.line - 1; i >= 0 && i >= position.line - 20; i--) {
        const prevLine = document.lineAt(i).text;
        if (/^\s*@match\b/.test(prevLine)) {
          return [createMatchCaseSnippet(), createDefaultCaseSnippet()];
        }
        if (/^\s*@[A-Za-z_][\w.-]*/.test(prevLine) && !/^\s*@match/.test(prevLine)) {
          break;
        }
      }
    }

    // 9. File path completions
    if (/^\s*@refine\s+\S*$/.test(prefix)) {
      return this._getRefineFileCompletions(document);
    }
    if (/^\s*@embed\s+file:\s*\S*$/.test(prefix)) {
      return this._getWorkspaceFileCompletions(document);
    }
    if (/^\s*@bind\s+\S+\s+.*\bfrom:\s*\S*$/.test(prefix)) {
      return this._getWorkspaceFileCompletions(document);
    }
    if (/^\s*@package\s+.*\b(?:template|from):\s*\S*$/.test(prefix)) {
      return this._getWorkspaceFileCompletions(document);
    }

    return undefined;
  }

  async _getRefineFileCompletions(document) {
    const docDir = path.dirname(document.uri.fsPath);
    const items = [];
    const files = await findWorkspaceFiles(document, "**/*.weavemark.md", 500);

    for (const file of files) {
      if (file.fsPath === document.uri.fsPath) continue;
      const rel = toPrompletPath(path.relative(docDir, file.fsPath));
      const item = new vscode.CompletionItem(rel, vscode.CompletionItemKind.File);
      item.detail = "WeaveMark file";
      item.insertText = quotePath(rel);
      items.push(item);
    }
    for (const module of await collectWorkspaceModules(files)) {
      const item = new vscode.CompletionItem(
        `module:${module}`,
        vscode.CompletionItemKind.Module
      );
      item.detail = "Workspace WeaveMark module";
      item.insertText = `module:${module}`;
      items.push(item);
    }
    return items;
  }

  async _getWorkspaceFileCompletions(document) {
    const docDir = path.dirname(document.uri.fsPath);
    const files = await findWorkspaceFiles(document, "**/*", 200);
    return files
      .filter((file) => file.fsPath !== document.uri.fsPath)
      .map((file) => {
        const rel = toPrompletPath(path.relative(docDir, file.fsPath));
        const item = new vscode.CompletionItem(rel, vscode.CompletionItemKind.File);
        item.detail = "Workspace file";
        item.insertText = quotePath(rel);
        return item;
      });
  }

  async _getModuleCompletions(document) {
    const files = await findWorkspaceFiles(document, "**/*.weavemark.md", 500);
    return (await collectWorkspaceModules(files)).map((moduleName) => {
      const item = new vscode.CompletionItem(
        moduleName,
        vscode.CompletionItemKind.Module
      );
      item.detail = "Workspace WeaveMark module";
      item.insertText = moduleName;
      return item;
    });
  }
}

async function findWorkspaceFiles(document, include, limit) {
  const folder = vscode.workspace.getWorkspaceFolder(document.uri);
  const exclude = "**/{node_modules,.git,.venv,__pycache__,dist,build}/**";
  if (folder) {
    return vscode.workspace.findFiles(
      new vscode.RelativePattern(folder, include),
      exclude,
      limit
    );
  }
  return vscode.workspace.findFiles(include, exclude, limit);
}

async function collectWorkspaceModules(files) {
  const modules = new Set();
  for (const uri of files) {
    const document = await vscode.workspace.openTextDocument(uri);
    const match = document
      .getText()
      .match(/^\s*@module\s+([A-Za-z_][\w.-]*)/m);
    if (match) modules.add(match[1]);
  }
  return [...modules].sort();
}

function quotePath(value) {
  return /\s/.test(value)
    ? `"${value.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`
    : value;
}

function toPrompletPath(value) {
  return value.split(path.sep).join("/");
}

// Trigger characters for completions
const TRIGGER_CHARACTERS = ["@", "{", ":", " "];

module.exports = {
  TRIGGER_CHARACTERS,
  WeaveMarkCompletionProvider,
  collectWorkspaceModules,
  quotePath,
  toPrompletPath,
};
