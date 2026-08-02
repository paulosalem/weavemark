import { expect, test } from "@playwright/test";
import { execFile } from "node:child_process";
import {
  mkdir,
  mkdtemp,
  readFile,
  readdir,
  rm,
  stat,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, dirname, relative, resolve } from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

const within = (root, parts) => {
  if (
    !Array.isArray(parts) ||
    parts.some((part) => typeof part !== "string" || !part || part === "." || part === "..")
  ) {
    throw new Error("Unsafe bridge path.");
  }
  const candidate = resolve(root, ...parts);
  const relation = relative(root, candidate);
  if (relation.startsWith("..") || relation === "..") throw new Error("Bridge path escaped.");
  return candidate;
};

async function installRealWorkspaceBridge(page, root) {
  await page.exposeFunction("__aiKanbanFs", async ({ operation, parts, bytes }) => {
    const target = within(root, parts);
    if (operation === "stat") {
      try {
        const value = await stat(target);
        return {
          kind: value.isDirectory() ? "directory" : "file",
          name: basename(target),
          size: value.size,
          modified: value.mtimeMs,
        };
      } catch (error) {
        if (error.code === "ENOENT") return null;
        throw error;
      }
    }
    if (operation === "mkdir") {
      await mkdir(target, { recursive: false });
      return null;
    }
    if (operation === "touch") {
      await mkdir(dirname(target), { recursive: true });
      await writeFile(target, new Uint8Array());
      return null;
    }
    if (operation === "read") {
      const value = await readFile(target);
      const metadata = await stat(target);
      return { bytes: [...value], modified: metadata.mtimeMs };
    }
    if (operation === "write") {
      await mkdir(dirname(target), { recursive: true });
      await writeFile(target, Uint8Array.from(bytes));
      return null;
    }
    if (operation === "list") {
      return Promise.all(
        (await readdir(target, { withFileTypes: true })).map(async (entry) => ({
          name: entry.name,
          kind: entry.isDirectory() ? "directory" : "file",
        })),
      );
    }
    if (operation === "remove") {
      await rm(target, { force: false, recursive: false });
      return null;
    }
    throw new Error(`Unsupported bridge operation: ${operation}`);
  });

  await page.addInitScript(({ rootName }) => {
    const call = (operation, parts, extra = {}) =>
      window.__aiKanbanFs({ operation, parts, ...extra });

    class BridgeFileHandle {
      constructor(name, parts) {
        this.kind = "file";
        this.name = name;
        this.parts = parts;
      }

      async getFile() {
        const value = await call("read", this.parts);
        const bytes = Uint8Array.from(value.bytes);
        return {
          name: this.name,
          size: bytes.byteLength,
          lastModified: value.modified,
          arrayBuffer: async () =>
            bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
          text: async () => new TextDecoder().decode(bytes),
        };
      }

      async createWritable() {
        let pending = null;
        return {
          write: async (value) => {
            const bytes =
              typeof value === "string"
                ? new TextEncoder().encode(value)
                : value instanceof Blob
                  ? new Uint8Array(await value.arrayBuffer())
                  : value instanceof ArrayBuffer
                    ? new Uint8Array(value)
                    : new Uint8Array(value.buffer, value.byteOffset, value.byteLength);
            pending = [...bytes];
          },
          close: async () => {
            if (pending !== null) await call("write", this.parts, { bytes: pending });
          },
          abort: async () => {
            pending = null;
          },
        };
      }
    }

    class BridgeDirectoryHandle {
      constructor(name, parts = []) {
        this.kind = "directory";
        this.name = name;
        this.parts = parts;
      }

      async queryPermission() {
        return "granted";
      }

      async requestPermission() {
        return "granted";
      }

      async getDirectoryHandle(name, { create = false } = {}) {
        const parts = [...this.parts, name];
        const metadata = await call("stat", parts);
        if (metadata?.kind === "directory") return new BridgeDirectoryHandle(name, parts);
        if (metadata) throw new DOMException("Wrong kind", "TypeMismatchError");
        if (!create) throw new DOMException("Not found", "NotFoundError");
        await call("mkdir", parts);
        return new BridgeDirectoryHandle(name, parts);
      }

      async getFileHandle(name, { create = false } = {}) {
        const parts = [...this.parts, name];
        const metadata = await call("stat", parts);
        if (metadata?.kind === "file") return new BridgeFileHandle(name, parts);
        if (metadata) throw new DOMException("Wrong kind", "TypeMismatchError");
        if (!create) throw new DOMException("Not found", "NotFoundError");
        await call("touch", parts);
        return new BridgeFileHandle(name, parts);
      }

      async removeEntry(name) {
        const parts = [...this.parts, name];
        if (!(await call("stat", parts))) throw new DOMException("Not found", "NotFoundError");
        await call("remove", parts);
      }

      async resolve(handle) {
        return Array.isArray(handle?.parts) ? handle.parts : null;
      }

      async *values() {
        for (const entry of await call("list", this.parts)) {
          const parts = [...this.parts, entry.name];
          yield entry.kind === "directory"
            ? new BridgeDirectoryHandle(entry.name, parts)
            : new BridgeFileHandle(entry.name, parts);
        }
      }
    }

    const root = new BridgeDirectoryHandle(rootName);
    Object.defineProperty(window, "showDirectoryPicker", {
      configurable: true,
      value: async () => root,
    });
  }, { rootName: basename(root) });
}

const runCli = async (workspace, ...arguments_) => {
  const cli = resolve(workspace, ".agents/skills/ai-kanban/ai_kanban.py");
  const { stdout, stderr } = await execFileAsync(
    process.env.PYTHON || "python",
    [cli, "--workspace", workspace, ...arguments_],
    { maxBuffer: 10 * 1024 * 1024 },
  );
  assertNoDiagnostics(stderr);
  return JSON.parse(stdout);
};

const assertNoDiagnostics = (stderr) => {
  expect(stderr, "agent CLI should not emit diagnostics").toBe("");
};

const protocolArguments = ({ actor, runId, revision, generation, key }) => [
  "--actor",
  actor,
  "--run-id",
  runId,
  "--revision",
  String(revision),
  "--generation",
  String(generation),
  "--idempotency-key",
  key,
];

test("real browser workspace and real agent CLI complete one control lifecycle", async ({
  page,
}) => {
  test.setTimeout(180_000);
  const workspace = await mkdtemp(resolve(tmpdir(), "ai-kanban-real-protocol-"));
  try {
    await installRealWorkspaceBridge(page, workspace);
    await page.goto("/");
    await page.getByRole("button", { name: "Try demo" }).click();
    await page.getByRole("button", { name: /Create a real demo workspace/ }).click();
    await expect(page.locator("#workspaceName")).toHaveText(basename(workspace), {
      timeout: 60_000,
    });

    await page.getByRole("heading", { name: "Macroeconomic pulse" }).click();
    await page.getByRole("button", { name: "Ready for agent" }).click();
    await page.getByRole("button", { name: "Close card workspace" }).click();
    await page.getByRole("button", { name: "Save workspace" }).click();
    await expect(page.locator("#saveStatus")).toContainText("Saved", { timeout: 60_000 });

    const actor = "real-agent";
    const runId = "real-run";
    const beforeGrant = await runCli(workspace, "preflight");
    await runCli(workspace, "announce", "--actor", actor, "--run-id", runId);

    await page.getByRole("button", { name: "Agent control" }).click();
    await page.getByRole("button", { name: "Retry" }).click();
    await expect(page.getByRole("button", { name: "Grant agent control" })).toBeEnabled();
    page.once("dialog", (dialog) => dialog.accept());
    await page.getByRole("button", { name: "Grant agent control" }).click();
    await expect(page.locator("#loadingOverlay")).toBeHidden({ timeout: 60_000 });
    await expect(page.locator("#saveStatus")).toContainText(`${actor} has control`, {
      timeout: 60_000,
    });

    const granted = await runCli(workspace, "preflight");
    expect(granted.generation).toBe(beforeGrant.generation + 1);
    expect(granted.control_holder).toBe(actor);

    const registered = await runCli(
      workspace,
      "register",
      ...protocolArguments({
        actor,
        runId,
        revision: granted.revision,
        generation: granted.generation,
        key: "register-real-agent",
      }),
      "--name",
      "Real protocol agent",
      "--host",
      "playwright",
    );
    const claimed = await runCli(
      workspace,
      "claim",
      ...protocolArguments({
        actor,
        runId,
        revision: registered.revision,
        generation: granted.generation,
        key: "claim-real-turn",
      }),
    );
    expect(claimed.turn_id).toBeTruthy();
    const started = await runCli(
      workspace,
      "start",
      ...protocolArguments({
        actor,
        runId,
        revision: claimed.revision,
        generation: granted.generation,
        key: "start-real-turn",
      }),
      "--turn-id",
      claimed.turn_id,
    );
    const asked = await runCli(
      workspace,
      "ask",
      ...protocolArguments({
        actor,
        runId,
        revision: started.revision,
        generation: granted.generation,
        key: "ask-real-turn",
      }),
      "--turn-id",
      claimed.turn_id,
      "--question",
      "Which evidence horizon should this protocol test use?",
      "--context",
      "A human answer must survive return, regrant, and resume.",
    );
    await runCli(
      workspace,
      "yield",
      ...protocolArguments({
        actor,
        runId,
        revision: asked.revision,
        generation: granted.generation,
        key: "yield-for-real-answer",
      }),
    );

    await page.getByRole("button", { name: "Agent control" }).click();
    await page.getByRole("button", { name: "Retry" }).click();
    await expect(page.locator("#agentControlAction")).toHaveText("Accept returned control");
    await page.locator("#agentControlAction").click();
    await expect(page.locator("#loadingOverlay")).toBeHidden({ timeout: 60_000 });
    await expect(page.locator("#saveStatus")).toContainText("read/write granted");
    await page.getByRole("heading", { name: claimed.title }).click();
    await page.getByRole("tab", { name: "Turns" }).click();
    await expect(
      page.getByText("Which evidence horizon should this protocol test use?"),
    ).toBeVisible();
    await page.getByRole("button", { name: "Answer", exact: true }).click();
    await page.getByLabel("Your answer").fill("Use the latest complete twelve months.");
    await page.getByRole("button", { name: "Answer and resume" }).click();
    await page.getByRole("button", { name: "Close card workspace" }).click();
    await page.getByRole("button", { name: "Save workspace" }).click();
    await expect(page.locator("#saveStatus")).toContainText("Saved", { timeout: 60_000 });

    const resumeRunId = "real-run-resumed";
    await runCli(
      workspace,
      "announce",
      "--actor",
      actor,
      "--run-id",
      resumeRunId,
    );
    await page.getByRole("button", { name: "Agent control" }).click();
    await page.getByRole("button", { name: "Retry" }).click();
    await expect(page.getByRole("button", { name: "Grant agent control" })).toBeEnabled();
    page.once("dialog", (dialog) => dialog.accept());
    await page.getByRole("button", { name: "Grant agent control" }).click();
    await expect(page.locator("#loadingOverlay")).toBeHidden({ timeout: 60_000 });
    await expect(page.locator("#saveStatus")).toContainText(`${actor} has control`);

    const resumedGrant = await runCli(workspace, "preflight");
    const resumedRegistration = await runCli(
      workspace,
      "register",
      ...protocolArguments({
        actor,
        runId: resumeRunId,
        revision: resumedGrant.revision,
        generation: resumedGrant.generation,
        key: "register-real-resume",
      }),
      "--name",
      "Real protocol agent",
      "--host",
      "playwright",
    );
    const resumed = await runCli(
      workspace,
      "resume",
      ...protocolArguments({
        actor,
        runId: resumeRunId,
        revision: resumedRegistration.revision,
        generation: resumedGrant.generation,
        key: "resume-real-turn",
      }),
      "--turn-id",
      claimed.turn_id,
    );
    expect(resumed.answers).toEqual([
      expect.objectContaining({
        question: "Which evidence horizon should this protocol test use?",
        answer: "Use the latest complete twelve months.",
      }),
    ]);
    const checkpoint = await runCli(
      workspace,
      "checkpoint",
      ...protocolArguments({
        actor,
        runId: resumeRunId,
        revision: resumed.revision,
        generation: resumedGrant.generation,
        key: "checkpoint-real-turn",
      }),
      "--turn-id",
      claimed.turn_id,
      "--summary",
      "Real cross-runtime protocol checkpoint after durable human input.",
      "--progress",
      "50",
    );
    const completed = await runCli(
      workspace,
      "complete",
      ...protocolArguments({
        actor,
        runId: resumeRunId,
        revision: checkpoint.revision,
        generation: resumedGrant.generation,
        key: "complete-real-turn",
      }),
      "--turn-id",
      claimed.turn_id,
      "--result",
      "Real browser and CLI protocol completed successfully.",
    );
    await runCli(
      workspace,
      "yield",
      ...protocolArguments({
        actor,
        runId: resumeRunId,
        revision: completed.revision,
        generation: resumedGrant.generation,
        key: "yield-real-agent",
      }),
    );

    await page.getByRole("button", { name: "Agent control" }).click();
    await page.getByRole("button", { name: "Retry" }).click();
    await expect(page.locator("#agentControlAction")).toHaveText("Accept returned control");
    await page.locator("#agentControlAction").click();
    await expect(page.locator("#loadingOverlay")).toBeHidden({ timeout: 60_000 });
    await expect(page.locator("#saveStatus")).toContainText("read/write granted");
    await page.getByRole("heading", { name: claimed.title }).click();
    await page.getByRole("tab", { name: "Turns" }).click();
    await expect(
      page.getByText("Real browser and CLI protocol completed successfully."),
    ).toBeVisible();
  } finally {
    await page.close().catch(() => {});
    await rm(workspace, { recursive: true, force: true });
  }
});
