// WeaveMark — safe CLI process and argument handling

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const { execFile } = require("child_process");

const PROMPLET_SUFFIX = ".weavemark.md";
const MAX_SCAN_OUTPUT_BYTES = 1024 * 1024;
const SCAN_TIMEOUT_MS = 30_000;

function getCliConfiguration() {
  const config = vscode.workspace.getConfiguration("weavemark");
  const cliPath = config.get("cliPath", "weavemark");
  const model = config.get("defaultModel", "");
  const extraArgs = config.get("extraArgs", []);

  if (typeof cliPath !== "string" || cliPath.trim() === "") {
    throw new Error("`weavemark.cliPath` must be a non-empty executable path.");
  }
  if (typeof model !== "string") {
    throw new Error("`weavemark.defaultModel` must be a string.");
  }
  if (
    !Array.isArray(extraArgs) ||
    extraArgs.some((value) => typeof value !== "string")
  ) {
    throw new Error("`weavemark.extraArgs` must be an array of argument strings.");
  }

  return {
    cliPath: cliPath.trim(),
    model: model.trim(),
    extraArgs: [...extraArgs],
  };
}

function buildCliArguments(specPath, modeArgs = [], variableValues = undefined) {
  const { model, extraArgs } = getCliConfiguration();
  const args = [];

  if (specPath) {
    args.push(specPath);
  }
  args.push(...modeArgs);

  if (variableValues) {
    for (const [name, value] of Object.entries(variableValues)) {
      if (value === "" || value === null || value === undefined) {
        continue;
      }
      args.push("--var", `${name}=${String(value)}`);
    }
  }
  if (model) {
    args.push("--model", model);
  }
  args.push(...extraArgs);
  return args;
}

function requireTrustedWorkspace(operation) {
  if (vscode.workspace.isTrusted) {
    return true;
  }
  vscode.window.showWarningMessage(
    `WeaveMark: Trust this workspace before ${operation}.`
  );
  return false;
}

async function resolvePrompletPath(uri) {
  let document;
  if (uri && uri.scheme === "file") {
    try {
      document = await vscode.workspace.openTextDocument(uri);
    } catch (error) {
      vscode.window.showErrorMessage(
        `WeaveMark: Cannot open the selected file — ${error.message}`
      );
      return null;
    }
  } else {
    document = vscode.window.activeTextEditor?.document;
  }

  if (!document) {
    vscode.window.showWarningMessage("WeaveMark: No file is open.");
    return null;
  }
  if (document.uri.scheme !== "file" || !document.fileName.endsWith(PROMPLET_SUFFIX)) {
    vscode.window.showWarningMessage(
      "WeaveMark: Select a local .weavemark.md file."
    );
    return null;
  }
  if (document.isDirty && !(await document.save())) {
    vscode.window.showWarningMessage(
      "WeaveMark: Save the promplet before running it."
    );
    return null;
  }
  return document.fileName;
}

function launchCliTerminal(args, cwd, terminalName = "WeaveMark") {
  const { cliPath } = getCliConfiguration();
  const executable = resolveExecutable(cliPath);
  const terminal = vscode.window.createTerminal({
    name: terminalName,
    iconPath: new vscode.ThemeIcon("zap"),
    shellPath: executable,
    shellArgs: args,
    cwd,
  });
  terminal.show(false);
  return terminal;
}

function scanPromplet(specPath) {
  const { cliPath } = getCliConfiguration();
  const executable = resolveExecutable(cliPath);
  return new Promise((resolve, reject) => {
    execFile(
      executable,
      [specPath, "--scan"],
      {
        cwd: path.dirname(specPath),
        encoding: "utf8",
        maxBuffer: MAX_SCAN_OUTPUT_BYTES,
        timeout: SCAN_TIMEOUT_MS,
        windowsHide: true,
      },
      (error, stdout, stderr) => {
        if (error) {
          reject(new Error(String(stderr || error.message).trim()));
          return;
        }
        try {
          resolve(validateScanMetadata(JSON.parse(stdout)));
        } catch (parseError) {
          reject(
            new Error(`Failed to parse WeaveMark scan output: ${parseError.message}`)
          );
        }
      }
    );
  });
}

function resolveExecutable(configuredPath, environmentPath = process.env.PATH || "") {
  if (path.isAbsolute(configuredPath)) {
    return configuredPath;
  }
  if (configuredPath.includes("/") || configuredPath.includes("\\")) {
    throw new Error(
      "`weavemark.cliPath` must be an absolute path or a bare executable name."
    );
  }

  const extensions =
    process.platform === "win32"
      ? (process.env.PATHEXT || ".EXE;.CMD;.BAT;.COM").split(";")
      : [""];
  for (const directory of environmentPath.split(path.delimiter)) {
    if (!directory) continue;
    for (const extension of extensions) {
      const candidate = path.join(directory, configuredPath + extension);
      try {
        const stat = fs.statSync(candidate);
        if (!stat.isFile()) continue;
        if (process.platform !== "win32") {
          fs.accessSync(candidate, fs.constants.X_OK);
        }
        return candidate;
      } catch {
        // Try the next PATH entry.
      }
    }
  }
  throw new Error(
    `Cannot find the WeaveMark CLI executable ${JSON.stringify(configuredPath)} on PATH. ` +
      "Set `weavemark.cliPath` to an absolute trusted path."
  );
}

function validateScanMetadata(value) {
  if (!isRecord(value)) {
    throw new Error("scan result must be a JSON object");
  }
  const inputs = Array.isArray(value.inputs)
    ? value.inputs.map(validateInputMetadata)
    : [];
  const inputNames = new Set(inputs.map((input) => input.name));
  if (inputNames.size !== inputs.length) {
    throw new Error("scan result contains duplicate input names");
  }
  const execution = isRecord(value.execution) ? value.execution : null;
  return {
    title: optionalText(value.title, "title", 500),
    description: optionalText(value.description, "description", 10_000),
    inputs,
    execution: execution
      ? { type: optionalText(execution.type, "execution.type", 200) }
      : null,
    prompt_names: stringArray(value.prompt_names, "prompt_names", 500),
    tool_names: stringArray(value.tool_names, "tool_names", 500),
  };
}

function validateInputMetadata(value, index) {
  if (!isRecord(value)) {
    throw new Error(`inputs[${index}] must be an object`);
  }
  const name = optionalText(value.name, `inputs[${index}].name`, 200);
  if (!/^[A-Za-z_][\w.-]*$/.test(name)) {
    throw new Error(`inputs[${index}].name is not a valid variable name`);
  }
  const inputType = optionalText(
    value.input_type,
    `inputs[${index}].input_type`,
    50
  );
  if (!["text", "multiline", "select", "boolean", "file"].includes(inputType)) {
    throw new Error(`inputs[${index}].input_type is not supported`);
  }
  return {
    name,
    input_type: inputType,
    options:
      value.options === null
        ? []
        : stringArray(value.options, `inputs[${index}].options`, 500),
    default:
      value.default === null || value.default === undefined
        ? ""
        : optionalText(value.default, `inputs[${index}].default`, 100_000),
    description: optionalText(
      value.description,
      `inputs[${index}].description`,
      10_000
    ),
    file_hint: optionalText(
      value.file_hint,
      `inputs[${index}].file_hint`,
      1_000
    ),
    source_directive: optionalText(
      value.source_directive,
      `inputs[${index}].source_directive`,
      200
    ),
  };
}

function optionalText(value, label, maxLength) {
  if (value === null || value === undefined) return "";
  if (typeof value !== "string" || value.length > maxLength) {
    throw new Error(`${label} must be a string no longer than ${maxLength}`);
  }
  return value;
}

function stringArray(value, label, maxItems) {
  if (!Array.isArray(value) || value.length > maxItems) {
    throw new Error(`${label} must be an array with at most ${maxItems} items`);
  }
  return value.map((item, index) =>
    optionalText(item, `${label}[${index}]`, 10_000)
  );
}

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

module.exports = {
  PROMPLET_SUFFIX,
  buildCliArguments,
  getCliConfiguration,
  launchCliTerminal,
  requireTrustedWorkspace,
  resolveExecutable,
  resolvePrompletPath,
  scanPromplet,
  validateScanMetadata,
};
