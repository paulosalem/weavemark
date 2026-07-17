// WeaveMark — safe CLI command integration

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const {
  buildCliArguments,
  launchCliTerminal,
  requireTrustedWorkspace,
  resolvePrompletPath,
} = require("./cli");

async function findVarsFiles(specPath) {
  const directory = path.join(path.dirname(specPath), "vars");
  const stem = path.basename(specPath).replace(/\.weavemark\.md$/, "").toLowerCase();

  try {
    return (await fs.promises.readdir(directory, { withFileTypes: true }))
      .filter((entry) => {
        if (!entry.isFile()) return false;
        const name = entry.name.toLowerCase();
        return (
          name.endsWith(".json") &&
          (name === `${stem}.json` || name.startsWith(`${stem}-`))
        );
      })
      .map((entry) => path.join(directory, entry.name))
      .sort();
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
}

async function resolveVarsArguments(specPath) {
  const varsFiles = await findVarsFiles(specPath);
  if (varsFiles.length === 0) return [];

  const items = varsFiles.map((filePath) => ({
    label: path.basename(filePath),
    description: path.relative(path.dirname(specPath), filePath),
    filePath,
  }));
  items.push({
    label: "Skip vars file",
    description: "Run without a discovered vars file",
    filePath: null,
  });

  const selected = await vscode.window.showQuickPick(items, {
    placeHolder:
      varsFiles.length === 1
        ? `Found ${path.basename(varsFiles[0])}`
        : "Select a vars file",
  });
  return selected?.filePath ? ["--vars-file", selected.filePath] : [];
}

async function runPromplet(uri, modeArgs, operation, terminalName) {
  if (!requireTrustedWorkspace(operation)) return;
  const specPath = await resolvePrompletPath(uri);
  if (!specPath) return;

  try {
    const varsArgs = await resolveVarsArguments(specPath);
    launchCliTerminal(
      buildCliArguments(specPath, [...modeArgs, ...varsArgs]),
      path.dirname(specPath),
      terminalName
    );
  } catch (error) {
    vscode.window.showErrorMessage(`WeaveMark: ${error.message}`);
  }
}

function compose(uri) {
  return runPromplet(uri, [], "composing promplets", "WeaveMark Compose");
}

function run(uri) {
  return runPromplet(
    uri,
    ["--run", "--verbose"],
    "executing promplets",
    "WeaveMark Run"
  );
}

function openTUI(uri) {
  return runPromplet(uri, ["--ui"], "opening the TUI", "WeaveMark TUI");
}

function discover() {
  if (!requireTrustedWorkspace("starting discovery")) return;
  try {
    const cwd = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    launchCliTerminal(
      buildCliArguments(null, ["--discover"]),
      cwd,
      "WeaveMark Discover"
    );
  } catch (error) {
    vscode.window.showErrorMessage(`WeaveMark: ${error.message}`);
  }
}

function registerRunCommands(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("weavemark.compose", compose),
    vscode.commands.registerCommand("weavemark.run", run),
    vscode.commands.registerCommand("weavemark.openTUI", openTUI),
    vscode.commands.registerCommand("weavemark.discover", discover)
  );
}

module.exports = {
  findVarsFiles,
  registerRunCommands,
  resolveVarsArguments,
};
