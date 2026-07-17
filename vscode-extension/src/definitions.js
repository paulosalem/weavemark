// WeaveMark — path and module definition provider

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const { analyzeSource } = require("./language");

const PATH_PATTERNS = [
  /^\s*@refine\s+("[^"]+"|'[^']+'|\S+)/,
  /^\s*@embed\b.*\bfile:\s*("[^"]+"|'[^']+'|\S+)/,
  /^\s*@bind\b.*\bfrom:\s*("[^"]+"|'[^']+'|\S+)/,
  /^\s*@package\b.*\b(?:template|from):\s*("[^"]+"|'[^']+'|\S+)/,
];
const MODULE_PATTERNS = [
  /^\s*@use\s+([A-Za-z_][\w.-]*)/,
  /^\s*@include\s+(?:module:)?([A-Za-z_][\w.-]*)/,
];

class WeaveMarkDefinitionProvider {
  async provideDefinition(document, position) {
    if (analyzeSource(document.getText()).ignoredLines.has(position.line)) {
      return undefined;
    }
    const line = document.lineAt(position).text;
    const pathReference = findReference(line, PATH_PATTERNS);
    if (pathReference && containsPosition(pathReference, position.character)) {
      const value = unquote(pathReference.value);
      if (value.startsWith("module:")) {
        return findModuleDefinition(value.slice("module:".length));
      }
      if (/^[A-Za-z_][\w-]*:/.test(value)) return undefined;

      const absolutePath = path.resolve(path.dirname(document.uri.fsPath), value);
      try {
        const stat = await fs.promises.stat(absolutePath);
        if (stat.isFile()) {
          return new vscode.Location(
            vscode.Uri.file(absolutePath),
            new vscode.Position(0, 0)
          );
        }
      } catch {
        return undefined;
      }
    }

    const moduleReference = findReference(line, MODULE_PATTERNS);
    if (
      moduleReference &&
      containsPosition(moduleReference, position.character)
    ) {
      return findModuleDefinition(moduleReference.value);
    }
    return undefined;
  }
}

function findReference(line, patterns) {
  for (const pattern of patterns) {
    const match = line.match(pattern);
    if (!match) continue;
    return {
      start: line.indexOf(match[1]),
      end: line.indexOf(match[1]) + match[1].length,
      value: match[1],
    };
  }
  return null;
}

function containsPosition(reference, character) {
  return character >= reference.start && character <= reference.end;
}

function unquote(value) {
  if (
    value.length >= 2 &&
    ((value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'")))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

async function findModuleDefinition(moduleName) {
  const files = await vscode.workspace.findFiles(
    "**/*.weavemark.md",
    "**/{node_modules,.git,.venv,__pycache__,dist,build}/**",
    500
  );
  const declaration = new RegExp(
    `^\\s*@module\\s+${escapeRegExp(moduleName)}(?:\\s|$)`,
    "m"
  );
  for (const uri of files) {
    const document = await vscode.workspace.openTextDocument(uri);
    const match = declaration.exec(document.getText());
    if (match) {
      const line = document.positionAt(match.index).line;
      return new vscode.Location(uri, new vscode.Position(line, 0));
    }
  }
  return undefined;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

module.exports = {
  WeaveMarkDefinitionProvider,
  findReference,
  unquote,
};
