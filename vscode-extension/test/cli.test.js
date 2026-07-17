const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { loadWithVscodeMock } = require("./helpers");

function createVscodeMock(settings = {}) {
  const terminals = [];
  const warnings = [];
  return {
    terminals,
    warnings,
    workspace: {
      isTrusted: settings.isTrusted ?? true,
      getConfiguration() {
        return {
          get(name, fallback) {
            return settings[name] ?? fallback;
          },
        };
      },
    },
    window: {
      createTerminal(options) {
        const terminal = { options, show() {} };
        terminals.push(terminal);
        return terminal;
      },
      showWarningMessage(message) {
        warnings.push(message);
      },
    },
    ThemeIcon: class ThemeIcon {
      constructor(id) {
        this.id = id;
      }
    },
  };
}

test("CLI arguments preserve hostile-looking values as inert arguments", () => {
  const vscode = createVscodeMock({
    defaultModel: "model; shutdown",
    extraArgs: ["--output", "result;$(touch nope).md"],
  });
  const { buildCliArguments } = loadWithVscodeMock("src/cli.js", vscode);

  const args = buildCliArguments(
    "/tmp/a;$(touch nope).weavemark.md",
    ["--run"],
    { topic: '"; touch /tmp/nope; echo "' }
  );

  assert.deepEqual(args, [
    "/tmp/a;$(touch nope).weavemark.md",
    "--run",
    "--var",
    'topic="; touch /tmp/nope; echo "',
    "--model",
    "model; shutdown",
    "--output",
    "result;$(touch nope).md",
  ]);
});

test("terminal launches the CLI directly with an argument array", () => {
  const vscode = createVscodeMock({
    cliPath: "/trusted/bin/weavemark",
  });
  const { launchCliTerminal } = loadWithVscodeMock("src/cli.js", vscode);
  const args = ["/tmp/spec.weavemark.md", "--run"];

  launchCliTerminal(args, "/tmp", "WeaveMark Test");

  assert.equal(vscode.terminals.length, 1);
  assert.equal(vscode.terminals[0].options.shellPath, "/trusted/bin/weavemark");
  assert.deepEqual(vscode.terminals[0].options.shellArgs, args);
  assert.equal(vscode.terminals[0].options.cwd, "/tmp");
});

test("bare CLI names resolve only through PATH entries", () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "weavemark-cli-"));
  const executable = path.join(directory, "weavemark");
  fs.writeFileSync(executable, "#!/bin/sh\n");
  fs.chmodSync(executable, 0o700);
  const vscode = createVscodeMock();
  const { resolveExecutable } = loadWithVscodeMock("src/cli.js", vscode);

  try {
    assert.equal(resolveExecutable("weavemark", directory), executable);
    assert.throws(
      () => resolveExecutable("./weavemark", directory),
      /absolute path or a bare executable name/
    );
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("execution is refused in untrusted workspaces", () => {
  const vscode = createVscodeMock({ isTrusted: false });
  const { requireTrustedWorkspace } = loadWithVscodeMock("src/cli.js", vscode);

  assert.equal(requireTrustedWorkspace("executing promplets"), false);
  assert.match(vscode.warnings[0], /Trust this workspace/);
});

test("scan metadata is constrained to the form's supported schema", () => {
  const vscode = createVscodeMock();
  const { validateScanMetadata } = loadWithVscodeMock("src/cli.js", vscode);

  const metadata = validateScanMetadata({
    title: "Example",
    inputs: [
      {
        name: "audience",
        input_type: "select",
        options: ["expert"],
        default: null,
      },
    ],
    execution: { type: "chain", ignored: "value" },
    prompt_names: ["default"],
    tool_names: [],
    ignored: "<script>",
  });

  assert.deepEqual(metadata.execution, { type: "chain" });
  assert.equal(metadata.inputs[0].default, "");
  assert.equal(Object.hasOwn(metadata, "ignored"), false);
  assert.throws(
    () =>
      validateScanMetadata({
        inputs: [{ name: "bad name", input_type: "text" }],
        prompt_names: [],
        tool_names: [],
      }),
    /valid variable name/
  );
});
