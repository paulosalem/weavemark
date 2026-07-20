// WeaveMark — path and module definition provider

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const os = require("os");
const { analyzeSource } = require("./language");

const PROJECT_ROOT_MARKERS = [
  ".weavemark-root",
  "weavemark.json",
  ".git",
  "pyproject.toml",
];
const PATH_PATTERNS = [
  /^\s*@reference\s+("[^"]+"|'[^']+'|\S+)/,
  /@reference\(\s*("[^"]+"|'[^']+'|[A-Za-z0-9_./~+-]+)/,
  /(?<![A-Za-z0-9_@])@((?:(?:\.{0,2}\/|~\/|\/)[A-Za-z0-9_./~+-]*[A-Za-z0-9_+-])|(?:README|AGENTS|CLAUDE)(?:\.md)?|[A-Za-z0-9_+-]+(?:\.[A-Za-z0-9_+-]+)+)(?=$|[\s.,;:!?])/,
  /^\s*@refine\s+("[^"]+"|'[^']+'|\S+)/,
  /^\s*@embed\b.*\bfile:\s*("[^"]+"|'[^']+'|\S+)/,
  /^\s*@bind\b.*\bfrom:\s*("[^"]+"|'[^']+'|\S+)/,
  /^\s*@package\b.*\b(?:instructions|from):\s*("[^"]+"|'[^']+'|\S+)/,
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
    const pathReference = findReference(line, PATH_PATTERNS, position.character);
    if (pathReference && containsPosition(pathReference, position.character)) {
      const value = unquote(pathReference.value);
      if (value.startsWith("module:")) {
        return findModuleDefinition(value.slice("module:".length));
      }
      if (/^[A-Za-z_][\w-]*:/.test(value)) return undefined;

      for (const absolutePath of pathCandidates(document, value)) {
        try {
          const stat = await fs.promises.stat(absolutePath);
          if (stat.isFile()) {
            return new vscode.Location(
              vscode.Uri.file(absolutePath),
              new vscode.Position(0, 0)
            );
          }
        } catch {
          // Try the next runtime-equivalent candidate.
        }
      }
      return undefined;
    }

    const moduleReference = findReference(
      line,
      MODULE_PATTERNS,
      position.character
    );
    if (
      moduleReference &&
      containsPosition(moduleReference, position.character)
    ) {
      return findModuleDefinition(moduleReference.value);
    }
    return undefined;
  }
}

function findReference(line, patterns, character = null) {
  for (const pattern of patterns) {
    const flags = pattern.flags.includes("g") ? pattern.flags : `${pattern.flags}g`;
    const globalPattern = new RegExp(pattern.source, flags);
    for (const match of line.matchAll(globalPattern)) {
      const start = match.index + match[0].indexOf(match[1]);
      const reference = {
        start,
        end: start + match[1].length,
        value: match[1],
      };
      if (character === null || containsPosition(reference, character)) {
        return reference;
      }
    }
  }
  return null;
}

function pathCandidates(document, value) {
  if (value.startsWith("~/")) {
    return [path.resolve(os.homedir(), value.slice(2))];
  }
  if (path.isAbsolute(value)) return [path.resolve(value)];

  const documentDirectory = path.dirname(document.uri.fsPath);
  const projectRoot = findProjectRoot(documentDirectory);
  const candidates = [
    path.resolve(documentDirectory, value),
    path.resolve(projectRoot, "promplets", value),
    path.resolve(projectRoot, value),
  ];
  const workspaceFolder = vscode.workspace.getWorkspaceFolder?.(document.uri);
  if (workspaceFolder) {
    candidates.push(
      path.resolve(workspaceFolder.uri.fsPath, "promplets", value),
      path.resolve(workspaceFolder.uri.fsPath, value)
    );
  }
  return [...new Set(candidates)];
}

function findProjectRoot(startDirectory) {
  let current = path.resolve(startDirectory);
  while (true) {
    if (
      PROJECT_ROOT_MARKERS.some((marker) =>
        fs.existsSync(path.join(current, marker))
      )
    ) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) return path.resolve(startDirectory);
    current = parent;
  }
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
  findProjectRoot,
  findReference,
  pathCandidates,
  unquote,
};
