import { expect, test } from "@playwright/test";

const installFakeWorkspace = async (page) => {
  await page.addInitScript(() => {
    class FakeFileHandle {
      constructor(name, path) {
        this.kind = "file";
        this.name = name;
        this.path = path;
        this.bytes = new Uint8Array();
        this.modified = Date.now();
      }

      async getFile() {
        const bytes = this.bytes.slice();
        return {
          name: this.name,
          size: bytes.byteLength,
          lastModified: this.modified,
          arrayBuffer: async () => bytes.buffer.slice(0),
          text: async () => new TextDecoder().decode(bytes),
        };
      }

      async createWritable() {
        window.__activeWrites += 1;
        window.__maxActiveWrites = Math.max(
          window.__maxActiveWrites,
          window.__activeWrites,
        );
        let finished = false;
        const finish = () => {
          if (!finished) {
            finished = true;
            window.__activeWrites -= 1;
          }
        };
        return {
          write: async (value) => {
            if (window.__delayWrites) {
              await new Promise((resolve) =>
                window.__nativeSetTimeout(resolve, window.__writeDelayMs || 25)
              );
            }
            if (this.path.join("/") === "board.sqlite") {
              window.__boardWriteCount += 1;
              if (window.__failBoardWriteAt === window.__boardWriteCount) {
                throw new Error("Injected board write failure");
              }
            }
            if (
              window.__failGrantPublication &&
              this.path.join("/") === ".ai-kanban/coordination/human.json" &&
              new TextDecoder().decode(value).includes('"requested_state": "agent"')
            ) {
              throw new Error("Injected grant publication failure");
            }
            this.bytes = value instanceof Uint8Array
              ? value.slice()
              : new Uint8Array(value);
          },
          close: async () => {
            this.modified += 1;
            finish();
          },
          abort: async () => finish(),
        };
      }
    }

    class FakeDirectoryHandle {
      constructor(name, path = []) {
        this.kind = "directory";
        this.name = name;
        this.path = path;
        this.entries = new Map();
      }

      async queryPermission() {
        return window.__fakePermission;
      }

      async requestPermission() {
        return window.__fakePermission;
      }

      async getDirectoryHandle(name, { create = false } = {}) {
        const existing = this.entries.get(name);
        if (existing?.kind === "directory") return existing;
        if (existing) throw new DOMException("Wrong kind", "TypeMismatchError");
        if (!create) throw new DOMException("Not found", "NotFoundError");
        const directory = new FakeDirectoryHandle(name, [...this.path, name]);
        this.entries.set(name, directory);
        return directory;
      }

      async getFileHandle(name, { create = false } = {}) {
        if (
          window.__failBootstrapRead &&
          [...this.path, name].join("/") === "AGENTS.md" &&
          !create
        ) {
          throw new Error("Injected bootstrap inspection failure");
        }
        const existing = this.entries.get(name);
        if (existing?.kind === "file") return existing;
        if (existing) throw new DOMException("Wrong kind", "TypeMismatchError");
        if (!create) throw new DOMException("Not found", "NotFoundError");
        const file = new FakeFileHandle(name, [...this.path, name]);
        this.entries.set(name, file);
        return file;
      }

      async resolve(handle) {
        return handle.path;
      }

      async *values() {
        if (this.path.join("/") === ".ai-kanban/coordination") {
          window.__coordinationReads += 1;
        }
        yield* this.entries.values();
      }
    }

    window.__fakePermission = "granted";
    window.__nativeSetTimeout = window.setTimeout.bind(window);
    window.__activeWrites = 0;
    window.__maxActiveWrites = 0;
    window.__delayWrites = false;
    window.__writeDelayMs = 25;
    window.__boardWriteCount = 0;
    window.__failBoardWriteAt = null;
    window.__failGrantPublication = false;
    window.__failBootstrapRead = false;
    window.__coordinationReads = 0;
    window.__fakeRoot = new FakeDirectoryHandle("Research Board");
    window.__fakeReadText = async (path) => {
      const parts = path.split("/");
      let current = window.__fakeRoot;
      for (const part of parts.slice(0, -1)) current = current.entries.get(part);
      const file = current.entries.get(parts.at(-1));
      return new TextDecoder().decode(file.bytes);
    };
    window.__fakeWrite = (path, value) => {
      const parts = path.split("/");
      let current = window.__fakeRoot;
      for (const part of parts.slice(0, -1)) current = current.entries.get(part);
      const file = current.entries.get(parts.at(-1));
      file.bytes = typeof value === "string"
        ? new TextEncoder().encode(value)
        : new Uint8Array(value);
      file.modified += 1;
    };
    window.__fakeSeedText = async (path, value) => {
      const parts = path.split("/");
      let current = window.__fakeRoot;
      for (const part of parts.slice(0, -1)) {
        current = await current.getDirectoryHandle(part, { create: true });
      }
      const file = new FakeFileHandle(parts.at(-1), parts);
      file.bytes = new TextEncoder().encode(value);
      current.entries.set(parts.at(-1), file);
    };
    Object.defineProperty(window, "showDirectoryPicker", {
      configurable: true,
      value: async () => window.__fakeRoot,
    });
  });
};

test("first run is focused, accessible, and backend-honest", async ({ page }) => {
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });

  await page.goto("/");
  await expect(page).toHaveTitle("AI Kanban");
  await expect(page.getByRole("button", { name: "Open Board Workspace" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Create Board Workspace" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Try demo" })).toBeVisible();
  await expect(page.locator("#application")).toBeHidden();
  await expect(page.getByText("No backend")).toBeVisible();
  expect(errors).toEqual([]);
});

test("directory creation lock serializes creators sharing a folder identity", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { acquireDirectoryCreationLock } = await import("./src/file-workspace.js");
    const handle = { name: "Shared Board" };
    const first = await acquireDirectoryCreationLock(handle);
    const firstAcquired = first.acquired;
    const second = await acquireDirectoryCreationLock(handle);
    const secondAcquired = second.acquired;
    first.release();
    await new Promise((resolve) => setTimeout(resolve, 0));
    const third = await acquireDirectoryCreationLock(handle);
    const thirdAcquired = third.acquired;
    third.release();
    return {
      first: firstAcquired,
      second: secondAcquired,
      third: thirdAcquired,
    };
  });
  expect(result).toEqual({ first: true, second: false, third: true });
});

test("demo supports board, detail, decision, turn, filter, and handoff flows", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await expect(page.getByText("Demo workspace · memory only")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Macroeconomic pulse" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Choose our July family vacation" })).toBeVisible();

  await page.getByRole("heading", { name: "Choose our July family vacation" }).click();
  await page.getByRole("tab", { name: "Decision" }).click();
  await expect(page.getByRole("heading", { name: "Options and feedback" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Buenos Aires" })).toBeVisible();
  await page.getByRole("button", { name: "Close card workspace" }).click();

  await page.getByRole("button", { name: "Filters" }).click();
  const filters = page.locator("#filtersDialog");
  await filters.getByLabel("Kind").selectOption("question");
  await filters.getByRole("button", { name: "Apply filters" }).click();
  await expect(page.locator(".kanban-card")).toHaveCount(2);

  await page.getByRole("button", { name: "AI handoff" }).click();
  await expect(page.locator("#handoffExportText")).toHaveValue(/ai-kanban-handoff\/v1/);
  await page.getByRole("tab", { name: "Import response" }).click();
  await page.locator("#handoffImportText").fill('{"schema":"bad"}');
  await page.getByRole("button", { name: "Validate and preview" }).click();
  await expect(page.getByText("Cannot apply this packet")).toBeVisible();
});

test("direct-send review invalidates on every relevant change and clears on close", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await page.getByRole("button", { name: "AI handoff" }).click();
  await page.getByRole("tab", { name: "Direct send" }).click();
  await page.locator("#providerName").fill("Test provider");
  await page.locator("#providerEndpoint").fill("https://provider.example/send");
  await page.locator("#providerModel").fill("model-a");
  await page.locator("#providerCredential").fill("session-secret");
  await page.getByRole("button", { name: "Preview exact request" }).click();
  await expect(page.getByRole("button", { name: "Confirm and send" })).toBeVisible();

  await page.locator("#providerModel").fill("model-b");
  await expect(page.getByRole("button", { name: "Confirm and send" })).toBeHidden();
  await page.getByRole("button", { name: "Preview exact request" }).click();
  await expect(page.getByRole("button", { name: "Confirm and send" })).toBeVisible();
  await page.locator("#handoffCardSelect").selectOption({ index: 1 });
  await expect(page.getByRole("button", { name: "Confirm and send" })).toBeHidden();

  await page.getByRole("button", { name: "Close AI handoff" }).click();
  await page.getByRole("button", { name: "AI handoff" }).click();
  await page.getByRole("tab", { name: "Direct send" }).click();
  await expect(page.locator("#providerCredential")).toHaveValue("");
  await expect(page.getByRole("button", { name: "Confirm and send" })).toBeHidden();
});

test("image download preserves resolved bytes, MIME-derived extension, and not reference text", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(async () => {
    const { renderSurface } = await import("./src/surfaces.js");
    const surface = renderSurface({
      id: "image-output",
      type: "image",
      title: "Pixel proof",
      status: "complete",
      content: "data:image/png;base64,iVBORw0KGgo=",
      createdAt: new Date().toISOString(),
    });
    surface.id = "image-download-test";
    document.body.append(surface);
  });
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#image-download-test").getByRole("button", {
    name: "Download",
  }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("pixel-proof.png");
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  expect(Buffer.concat(chunks)).toEqual(
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
  );
});

test("card creation and keyboard movement preserve a usable board", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Keyboard movement check");
  await page.getByLabel("Intent and context").fill("Exercise the complete keyboard path.");
  await page.getByRole("button", { name: "Create card" }).click();
  await expect(page.locator("#detailTitle")).toHaveText("Keyboard movement check");
  await page.getByRole("button", { name: "Close card workspace" }).click();
  const card = page.locator(".kanban-card", { hasText: "Keyboard movement check" });
  await card.focus();
  await card.press("Alt+ArrowRight");
  await expect(page.locator('[data-column-id="planning"] .kanban-card', {
    hasText: "Keyboard movement check",
  })).toBeVisible();
  const moved = page.locator('[data-column-id="planning"] .kanban-card', {
    hasText: "Keyboard movement check",
  });
  const moveLeft = moved.getByRole("button", {
    name: "Move Keyboard movement check left",
  });
  await moveLeft.focus();
  await moveLeft.press("Enter");
  await expect(page.locator("#cardDetailDialog")).toBeHidden();
  await expect(page.locator('[data-column-id="inbox"] .kanban-card', {
    hasText: "Keyboard movement check",
  })).toBeVisible();

  await page.getByRole("heading", { name: "Keyboard movement check" }).click();
  const overviewTab = page.getByRole("tab", { name: "Overview" });
  await overviewTab.focus();
  await overviewTab.press("End");
  await expect(page.getByRole("tab", { name: "Activity" })).toHaveAttribute(
    "aria-selected",
    "true",
  );
  await page.getByRole("tab", { name: "Activity" }).press("Home");
  await expect(overviewTab).toHaveAttribute("aria-selected", "true");
  await overviewTab.press("ArrowRight");
  await expect(page.getByRole("tab", { name: "Plan" })).toHaveAttribute(
    "aria-selected",
    "true",
  );
});

test("320px and reduced-motion modes retain controls without document overflow", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 760 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Try demo" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(320);
  await page.getByRole("button", { name: "Try demo" }).click();
  await expect(page.getByRole("button", { name: "New card" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(320);
  await page.getByRole("heading", { name: "Macroeconomic pulse" }).click();
  await expect(page.getByRole("button", { name: "Publish result" })).toBeVisible();
  const animationDuration = await page.locator(".kanban-card").first().evaluate(
    (element) => getComputedStyle(element).animationDuration,
  );
  expect(["0s", "0.001ms", "1e-06s"]).toContain(animationDuration);
});

test("loaded app remains functional after the network goes offline", async ({ page, context }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await context.setOffline(true);
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Offline planning");
  await page.getByRole("button", { name: "Create card" }).click();
  await expect(page.locator("#detailTitle")).toHaveText("Offline planning");
  await context.setOffline(false);
});

test("cross-tab save signals are connected-only and preserve dirty drafts", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.addInitScript(() => {
    const NativeBroadcastChannel = window.BroadcastChannel;
    window.__broadcastPosts = [];
    window.BroadcastChannel = class extends NativeBroadcastChannel {
      postMessage(value) {
        window.__broadcastPosts.push(value);
        return super.postMessage(value);
      }
    };
    const nativeSetTimeout = window.setTimeout.bind(window);
    window.setTimeout = (callback, delay, ...arguments_) =>
      nativeSetTimeout(callback, delay === 700 ? 10_000 : delay, ...arguments_);
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await page.getByRole("button", { name: "Save workspace" }).click();
  expect(await page.evaluate(() => window.__broadcastPosts)).toEqual([]);
  await page.getByRole("button", { name: "Workspace menu" }).click();
  await page.getByRole("button", { name: "Close workspace" }).click();

  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Unsaved cross-tab draft");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await page.evaluate(async () => {
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    const sender = new BroadcastChannel("ai-kanban-workspaces");
    sender.postMessage({
      type: "saved",
      workspaceId: manifest.workspace_id,
      revision: manifest.revision + 1,
      fingerprint: "f".repeat(64),
    });
    sender.close();
  });
  await expect(page.getByRole("heading", { name: "Your draft is safe." })).toBeVisible();
  await expect(page.getByRole("button", { name: "Export draft" })).toBeVisible();
  await expect(page.locator("#saveStatus")).toContainText("draft preserved");
  await expect(page.locator(".kanban-card", {
    hasText: "Unsaved cross-tab draft",
  })).toHaveCount(1);
});

test("clean cross-tab reload reacquires writable access when available", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await expect(page.locator("#saveStatus")).not.toContainText("Read-only");

  await page.evaluate(async () => {
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    const sender = new BroadcastChannel("ai-kanban-workspaces");
    sender.postMessage({
      type: "saved",
      workspaceId: manifest.workspace_id,
      revision: manifest.revision,
      fingerprint: manifest.content_fingerprints[manifest.primary_state],
    });
    sender.close();
  });

  await expect(page.locator("#workspaceAlert")).toContainText(
    "read-only until you reload",
  );
  await page.getByRole("button", { name: "Reload" }).click();
  await expect(page.locator("#saveStatus")).not.toContainText("Read-only");
  await expect(page.getByRole("button", { name: "New card" })).toBeEnabled();
});

test("connected folder creation, durable files, close, and reopen use one portable boundary", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await expect(page.locator("#saveStatus")).toContainText("read/write granted");
  const durable = await page.evaluate(async () => {
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    const board = window.__fakeRoot.entries.get("board.sqlite");
    const skill = await window.__fakeReadText(".agents/skills/ai-kanban/SKILL.md");
    return {
      manifest,
      boardSize: board.bytes.byteLength,
      skill,
    };
  });
  expect(durable.manifest.primary_state).toBe("board.sqlite");
  expect(durable.manifest.workspace_id).toBeTruthy();
  expect(durable.boardSize).toBeGreaterThan(50_000);
  expect(durable.skill).toContain("AI Kanban agent skill");

  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Explicit save regression");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await page.getByRole("button", { name: "Save workspace" }).click();
  await expect(page.locator("#saveStatus")).toContainText("Saved · read/write granted");
  await expect(page.getByText("Explicit conflict recovery is required")).toHaveCount(0);

  await page.getByRole("button", { name: "Workspace menu" }).click();
  await page.getByRole("button", { name: "Close workspace" }).click();
  await expect(page.getByRole("button", { name: "Open Board Workspace" })).toBeVisible();
  await page.getByRole("button", { name: "Open Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await expect(page.getByRole("heading", { name: "Explicit save regression" })).toBeVisible();
});

test("swapped workspace reload releases the old writable context", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const swapped = new BoardRepository();
    const snapshot = await swapped.create({ workspaceId: "swapped-workspace" });
    const bytes = await swapped.exportBytes();
    await swapped.close();
    swapped.terminate();
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const fingerprint = [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    manifest.workspace_id = "swapped-workspace";
    manifest.revision = Number(snapshot.meta.revision);
    manifest.content_fingerprints["board.sqlite"] = fingerprint;
    const stateFile = manifest.application_files.find(
      (item) => item.path === "board.sqlite",
    );
    stateFile.fingerprint = fingerprint;
    window.__fakeWrite("board.sqlite", bytes);
    window.__fakeWrite("manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
  });
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Local draft before swap");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await expect(page.getByRole("heading", { name: "Your draft is safe." })).toBeVisible();
  await page.getByRole("button", { name: "Reload workspace" }).click();
  await expect(page.locator("#workspaceAlert")).toContainText(
    /different workspace|identity changed/i,
  );
  await expect(page.getByRole("button", { name: "New card" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Save workspace" })).toBeDisabled();
});

test("browser adoption rejects SQLite protocol metadata that disagrees with manifest", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.addScriptTag({ url: "/vendor/sql-wasm.js" });
  await page.evaluate(async () => {
    const SQL = await window.initSqlJs({
      locateFile: (file) => `/vendor/${file}`,
    });
    const database = new SQL.Database(
      window.__fakeRoot.entries.get("board.sqlite").bytes.slice(),
    );
    database.run(
      "UPDATE metadata SET value='2' WHERE key='protocol_version'",
    );
    const bytes = database.export();
    database.close();
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const fingerprint = [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    manifest.content_fingerprints["board.sqlite"] = fingerprint;
    manifest.application_files.find(
      (item) => item.path === "board.sqlite",
    ).fingerprint = fingerprint;
    window.__fakeWrite("board.sqlite", bytes);
    window.__fakeWrite("manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
  });
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Protocol conflict draft");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await expect(page.getByRole("heading", { name: "Your draft is safe." })).toBeVisible();
  await page.getByRole("button", { name: "Reload workspace" }).click();
  await expect(page.locator("#workspaceAlert")).toContainText(
    /format, schema, or protocol/i,
  );
  await expect(page.getByRole("button", { name: "New card" })).toBeDisabled();
});

test("activation detects and rolls back a crashed unpublished grant", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.open(
      window.__fakeRoot.entries.get("board.sqlite").bytes.slice(),
    );
    const result = await repository.mutate("setControl", {
      state: "granting_agent",
      holderId: "human",
      ownerId: "human",
      incrementGeneration: true,
    });
    const bytes = await repository.exportBytes();
    await repository.close();
    repository.terminate();
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const fingerprint = [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    manifest.revision = Number(result.snapshot.meta.revision);
    manifest.content_fingerprints["board.sqlite"] = fingerprint;
    manifest.application_files.find(
      (item) => item.path === "board.sqlite",
    ).fingerprint = fingerprint;
    window.__fakeWrite("board.sqlite", bytes);
    window.__fakeWrite("manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
  });
  await page.getByRole("button", { name: "Workspace menu" }).click();
  await page.getByRole("button", { name: "Close workspace" }).click();
  await page.getByRole("button", { name: "Open Board Workspace" }).click();
  await expect(page.getByText(/unpublished agent grant/)).toBeVisible();
  await expect(page.getByRole("button", { name: "New card" })).toBeDisabled();
  await page.getByRole("button", {
    name: "Roll back unpublished grant",
  }).click();
  await expect(page.locator("#saveStatus")).toContainText("read/write granted");
  await expect(page.getByRole("button", { name: "New card" })).toBeEnabled();
  const control = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const reader = new BoardRepository();
    const snapshot = await reader.open(
      window.__fakeRoot.entries.get("board.sqlite").bytes.slice(),
    );
    await reader.close();
    reader.terminate();
    return {
      state: snapshot.meta.control_state,
      holder: snapshot.meta.control_holder,
    };
  });
  expect(control).toEqual({ state: "human", holder: "human" });
});

test("lost-lock tabs cannot publish agent-control or bootstrap mutations", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.addInitScript(() => {
    const request = navigator.locks.request.bind(navigator.locks);
    window.__denyWorkspaceLock = false;
    navigator.locks.request = (name, options, callback) => {
      if (
        window.__denyWorkspaceLock &&
        name.startsWith("ai-kanban:") &&
        !name.startsWith("ai-kanban:create:")
      ) {
        return Promise.resolve(callback(null));
      }
      return request(name, options, callback);
    };
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.getByRole("button", { name: "Workspace menu" }).click();
  await page.getByRole("button", { name: "Close workspace" }).click();
  await page.evaluate(() => {
    window.__denyWorkspaceLock = true;
  });
  await page.getByRole("button", { name: "Open Board Workspace" }).click();
  await expect(page.locator("#saveStatus")).toContainText("Read-only");
  await page.evaluate(async () => {
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    await window.__fakeSeedText(
      ".ai-kanban/coordination/agent-lock-test.json",
      `${JSON.stringify({
        workspace_id: manifest.workspace_id,
        protocol_version: 1,
        actor_id: "lock-test",
        holder_id: "lock-test",
        run_id: "run-lock",
        sequence: 1,
        control_generation: 0,
        observed_revision: manifest.revision,
        requested_state: "granting_agent",
        status: "requesting_control",
        current_turn_id: null,
        timestamp: new Date().toISOString(),
      }, null, 2)}\n`,
    );
  });
  await page.getByRole("button", { name: "Agent control" }).click();
  await page.getByRole("button", { name: "Retry" }).click();
  await expect(page.locator("#agentControlAction")).toBeDisabled();
  await expect(page.locator("#repairFromAgentButton")).toBeDisabled();
  const human = JSON.parse(
    await page.evaluate(() =>
      window.__fakeReadText(".ai-kanban/coordination/human.json"),
    ),
  );
  expect(human.sequence).toBe(0);
});

test("unsupported browsers receive explicit archive language", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, "showDirectoryPicker", {
      configurable: true,
      value: undefined,
    });
  });
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Import Board Archive" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Create Download-only Board" })).toBeVisible();
  await expect(page.getByText(/portable archives instead/)).toBeVisible();
});

test("workspace creation preserves existing bootstrap files until explicitly confirmed", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.evaluate(() => window.__fakeSeedText("AGENTS.md", "# Personal instructions\n"));
  page.once("dialog", (dialog) => dialog.dismiss());
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#welcome")).toBeVisible();
  expect(await page.evaluate(() => window.__fakeReadText("AGENTS.md"))).toBe(
    "# Personal instructions\n",
  );
  expect(await page.evaluate(() => window.__fakeRoot.entries.has("board.sqlite"))).toBe(false);

  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  expect(await page.evaluate(() => window.__fakeReadText("AGENTS.md"))).toContain(
    "# AI Kanban workspace",
  );
});

test("an unpublished failed grant rolls durable control back to human", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.evaluate(async () => {
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    await window.__fakeSeedText(
      ".ai-kanban/coordination/agent-test-agent.json",
      `${JSON.stringify({
        workspace_id: manifest.workspace_id,
        protocol_version: 1,
        actor_id: "test-agent",
        holder_id: "test-agent",
        run_id: "run-rollback",
        sequence: 1,
        control_generation: 0,
        observed_revision: 0,
        requested_state: "granting_agent",
        status: "requesting_control",
        current_turn_id: null,
        timestamp: new Date().toISOString(),
      }, null, 2)}\n`,
    );
    window.__boardWriteCount = 0;
    window.__failBoardWriteAt = 2;
  });
  await page.getByRole("button", { name: "Agent control" }).click();
  await page.getByRole("button", { name: "Retry" }).click();
  await expect(page.getByRole("button", { name: "Grant agent control" })).toBeEnabled();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Grant agent control" }).click();
  await expect(page.getByText(/safely rolled back to the human owner/)).toBeVisible();
  await expect(page.locator("#saveStatus")).toContainText("read/write granted");
  const durable = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const reader = new BoardRepository();
    const snapshot = await reader.open(
      window.__fakeRoot.entries.get("board.sqlite").bytes.slice(),
    );
    await reader.close();
    reader.terminate();
    return {
      state: snapshot.meta.control_state,
      holder: snapshot.meta.control_holder,
      human: JSON.parse(
        await window.__fakeReadText(".ai-kanban/coordination/human.json"),
      ),
    };
  });
  expect(durable.state).toBe("human");
  expect(durable.holder).toBe("human");
  expect(durable.human.requested_state).toBe("human");
});

test("a possibly published failed grant requires cooperative return, never overwrite", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.evaluate(async () => {
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    await window.__fakeSeedText(
      ".ai-kanban/coordination/agent-test-agent.json",
      `${JSON.stringify({
        workspace_id: manifest.workspace_id,
        protocol_version: 1,
        actor_id: "test-agent",
        holder_id: "test-agent",
        run_id: "run-publication",
        sequence: 1,
        control_generation: 0,
        observed_revision: 0,
        requested_state: "granting_agent",
        status: "requesting_control",
        current_turn_id: null,
        timestamp: new Date().toISOString(),
      }, null, 2)}\n`,
    );
    window.__failGrantPublication = true;
  });
  await page.getByRole("button", { name: "Agent control" }).click();
  await page.getByRole("button", { name: "Retry" }).click();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Grant agent control" }).click();
  await expect(page.getByText(/grant may already be visible/)).toBeVisible();
  await expect(page.locator("#saveStatus")).toContainText("test-agent has control");
  await page.locator("#workspaceAlert").getByRole("button", {
    name: "Request control back",
  }).click();
  await expect.poll(() => page.evaluate(async () =>
    JSON.parse(
      await window.__fakeReadText(".ai-kanban/coordination/human.json"),
    ).requested_state,
  )).toBe("reclaim_requested");
  const stateValue = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const reader = new BoardRepository();
    const snapshot = await reader.open(
      window.__fakeRoot.entries.get("board.sqlite").bytes.slice(),
    );
    await reader.close();
    reader.terminate();
    return snapshot.meta.control_state;
  });
  expect(stateValue).toBe("agent");
});

test("handoff saves serialize and stale agents cannot trigger force recovery", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.addInitScript(() => {
    const nativeSetTimeout = window.setTimeout.bind(window);
    window.setTimeout = (callback, delay, ...arguments_) =>
      nativeSetTimeout(callback, delay === 700 ? 10_000 : delay, ...arguments_);
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.evaluate(() => {
    window.__maxActiveWrites = 0;
    window.__delayWrites = true;
  });
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Pending before handoff");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await page.evaluate(async () => {
    await window.__fakeSeedText(
      ".ai-kanban/coordination/agent-test-agent.json",
      `${JSON.stringify({
        workspace_id: JSON.parse(await window.__fakeReadText("manifest.json")).workspace_id,
        protocol_version: 1,
        actor_id: "test-agent",
        holder_id: "test-agent",
        run_id: "run-1",
        sequence: 1,
        control_generation: 0,
        observed_revision: 1,
        requested_state: "granting_agent",
        status: "requesting_control",
        current_turn_id: null,
        timestamp: new Date().toISOString(),
      }, null, 2)}\n`,
    );
  });
  await page.getByRole("button", { name: "Agent control" }).click();
  await page.getByRole("button", { name: "Retry" }).click();
  await expect(page.getByRole("button", { name: "Grant agent control" })).toBeEnabled();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Grant agent control" }).click();
  await expect(page.locator("#saveStatus")).toContainText("test-agent has control");
  expect(await page.evaluate(() => window.__maxActiveWrites)).toBe(1);
  await expect(page.getByRole("button", { name: "New card" })).toBeDisabled();
  await page.locator(".kanban-card", { hasText: "Pending before handoff" }).click();
  await expect(page.locator("#detailTitle")).toHaveText("Pending before handoff");
  await page.getByRole("tab", { name: "Turns" }).click();
  await expect(page.getByText("No turns yet")).toBeVisible();
  await page.getByRole("button", { name: "Close card workspace" }).click();

  const beforeReclaim = await page.evaluate(async () => {
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    const board = window.__fakeRoot.entries.get("board.sqlite").bytes;
    await window.__fakeWrite(
      ".ai-kanban/coordination/agent-test-agent.json",
      `${JSON.stringify({
        workspace_id: manifest.workspace_id,
        protocol_version: 1,
        actor_id: "test-agent",
        holder_id: "test-agent",
        run_id: "run-1",
        sequence: 2,
        control_generation: 1,
        observed_revision: manifest.revision,
        requested_state: "agent",
        status: "watching",
        current_turn_id: null,
        timestamp: "2020-01-01T00:00:00Z",
      }, null, 2)}\n`,
    );
    return Array.from(board);
  });
  await page.getByRole("button", { name: "Agent control" }).click();
  await page.getByRole("button", { name: "Retry" }).click();
  await expect(page.getByRole("button", { name: "Request control back" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Recover control/ })).toHaveCount(0);
  await page.getByRole("button", { name: "Request control back" }).click();
  await expect.poll(() => page.evaluate(async () =>
    JSON.parse(
      await window.__fakeReadText(".ai-kanban/coordination/human.json"),
    ).requested_state,
  )).toBe("reclaim_requested");
  const afterReclaim = await page.evaluate(async () => ({
    board: Array.from(window.__fakeRoot.entries.get("board.sqlite").bytes),
    human: JSON.parse(
      await window.__fakeReadText(".ai-kanban/coordination/human.json"),
    ),
  }));
  expect(afterReclaim.board).toEqual(beforeReclaim);
  expect(afterReclaim.human.requested_state).toBe("reclaim_requested");
  expect(afterReclaim.human.sequence).toBe(2);

  const beforeAccept = await page.evaluate(async () => {
    const original = window.__fakeRoot.entries.get("board.sqlite").bytes.slice();
    const { BoardRepository } = await import("./src/repository.js");
    const agent = new BoardRepository();
    await agent.open(original);
    const yielded = await agent.mutate(
      "setControl",
      {
        state: "human",
        holderId: "human",
        ownerId: "human",
        incrementGeneration: true,
      },
      { holderId: "test-agent" },
    );
    const bytes = await agent.exportBytes();
    await agent.close();
    agent.terminate();
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const fingerprint = [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    manifest.revision = Number(yielded.snapshot.meta.revision);
    manifest.content_fingerprints["board.sqlite"] = fingerprint;
    window.__fakeWrite("board.sqlite", bytes);
    window.__fakeWrite("manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
    window.__fakeWrite(
      ".ai-kanban/coordination/agent-test-agent.json",
      `${JSON.stringify({
        workspace_id: manifest.workspace_id,
        protocol_version: 1,
        actor_id: "test-agent",
        holder_id: "human",
        run_id: "run-1",
        sequence: 3,
        control_generation: Number(yielded.snapshot.meta.control_generation),
        observed_revision: Number(yielded.snapshot.meta.revision),
        requested_state: "human",
        status: "stopped",
        current_turn_id: null,
        timestamp: new Date().toISOString(),
      }, null, 2)}\n`,
    );
    return Array.from(bytes);
  });
  await page.getByRole("button", { name: "Retry" }).click();
  await expect(page.locator("#agentControlAction")).toHaveText("Accept returned control");
  await page.locator("#agentControlAction").click();
  await expect(page.locator("#saveStatus")).toContainText("read/write granted");
  const accepted = await page.evaluate(async () => ({
    board: Array.from(window.__fakeRoot.entries.get("board.sqlite").bytes),
    human: JSON.parse(
      await window.__fakeReadText(".ai-kanban/coordination/human.json"),
    ),
  }));
  expect(accepted.board).toEqual(beforeAccept);
  expect(accepted.human.sequence).toBe(3);
  expect(accepted.human.requested_state).toBe("human");
});

test("only complete or approved outputs are featured and publishable", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Output safety");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("tab", { name: "Outputs" }).click();

  const addOutput = async (status, title, content) => {
    await page.getByRole("button", { name: "＋ Add output" }).click();
    const dialog = page.locator("#genericDialog");
    await dialog.locator('select[name="status"]').selectOption(status);
    await dialog.locator('input[name="title"]').fill(title);
    await dialog.locator('textarea[name="content"]').fill(content);
    await dialog.getByRole("button", { name: "Add output" }).click();
  };
  await addOutput("draft", "Draft result", "Do not publish this draft.");
  await expect(page.getByRole("button", { name: "Publish result" })).toBeDisabled();
  await addOutput("complete", "Trusted result", "Publish this complete result.");
  await expect(page.getByRole("button", { name: "Publish result" })).toBeEnabled();
  await addOutput("failed", "Newer failed result", "Do not feature this failure.");
  await page.getByRole("tab", { name: "Overview" }).click();
  const latest = page.locator(".detail-section").filter({
    has: page.getByRole("heading", { name: "Latest successful result" }),
  });
  await expect(latest).toContainText("Trusted result");
  await expect(latest).not.toContainText("Newer failed result");
  await page.getByRole("button", { name: "Publish result" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await expect(page.getByRole("heading", { name: "Output safety · published result" })).toBeVisible();
});

test("forgetting research memory leaves only a content-free tombstone", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await page.getByRole("heading", { name: "Macroeconomic pulse" }).click();
  await page.getByRole("tab", { name: "Memory" }).click();
  const memory = page.locator(".memory-card").filter({
    has: page.getByRole("heading", { name: "Interest-rate outlook" }),
  });
  await expect(memory).toContainText("Banco Central do Brasil");
  page.once("dialog", (dialog) => dialog.accept());
  await memory.getByRole("button", { name: "Forget" }).click();
  const tombstone = page.locator(".memory-card").filter({
    has: page.getByRole("heading", { name: "Forgotten memory" }),
  });
  await expect(tombstone).toContainText("Payload and provenance were removed");
  await expect(page.getByText("Interest-rate outlook")).toHaveCount(0);
  await expect(page.getByText("Banco Central do Brasil")).toHaveCount(0);
  await expect(page.getByText("https://www.bcb.gov.br/")).toHaveCount(0);
});

test("dependency removal works from the card workspace", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try demo" }).click();
  await page.locator(".kanban-card", {
    hasText: "Choose our July family vacation",
  }).click();
  const dependencySection = page.locator(".detail-section").filter({
    has: page.getByRole("heading", { name: "Dependencies" }),
  });
  await dependencySection.getByRole("button", { name: "Add dependency" }).click();
  const dependencySelect = page.locator('#genericDialog select[name="dependsOnId"]');
  const macroValue = await dependencySelect.locator("option").filter({
    hasText: "Macroeconomic pulse",
  }).getAttribute("value");
  await dependencySelect.selectOption(macroValue);
  await page.locator("#genericDialog").getByRole("button", {
    name: "Add dependency",
  }).click();
  await expect(dependencySection).toContainText("Macroeconomic pulse");
  await dependencySection.getByRole("button", { name: "Remove" }).click();
  await expect(dependencySection).toContainText("No dependencies");
});

test("external changes stop autosave and preserve a recoverable local draft", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await expect(page.locator("#workspaceName")).toHaveText("Research Board");
  await page.evaluate(async () => {
    const original = window.__fakeRoot.entries.get("board.sqlite").bytes.slice();
    const { BoardRepository } = await import("./src/repository.js");
    const external = new BoardRepository();
    await external.open(original);
    await external.mutate("createCard", {
      title: "External durable change",
      description: "Written by another approved owner.",
    });
    const updated = await external.exportBytes();
    const snapshot = external.snapshotValue;
    await external.close();
    external.terminate();
    const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
    manifest.revision = Number(snapshot.meta.revision);
    manifest.updated_at = new Date().toISOString();
    const digest = await crypto.subtle.digest("SHA-256", updated);
    const fingerprint = [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
    manifest.content_fingerprints["board.sqlite"] = fingerprint;
    const stateFile = manifest.application_files.find(
      (item) => item.path === "board.sqlite",
    );
    if (stateFile) stateFile.fingerprint = fingerprint;
    window.__fakeWrite("board.sqlite", updated);
    window.__fakeWrite("manifest.json", `${JSON.stringify(manifest, null, 2)}\n`);
  });

  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Local draft change");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await expect(page.getByRole("heading", { name: "Your draft is safe." })).toBeVisible();
  await expect(page.getByText("External change detected")).toBeVisible();
  await page.getByRole("button", { name: "Reload workspace" }).click();
  await expect(page.getByRole("heading", { name: "External durable change" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Local draft change" })).toHaveCount(0);
});

    test("failed grant pre-save preserves the dirty draft and pending save", async ({ page }) => {
      await installFakeWorkspace(page);
      await page.addInitScript(() => {
        const nativeSetTimeout = window.setTimeout.bind(window);
        window.setTimeout = (callback, delay, ...arguments_) =>
          nativeSetTimeout(callback, delay === 700 ? 10_000 : delay, ...arguments_);
      });
      await page.goto("/");
      await page.getByRole("button", { name: "Create Board Workspace" }).click();
      await page.getByRole("button", { name: "New card" }).click();
      await page.getByLabel("Title").fill("Dirty grant draft");
      await page.getByRole("button", { name: "Create card" }).click();
      await page.getByRole("button", { name: "Close card workspace" }).click();
      await page.evaluate(async () => {
        const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
        await window.__fakeSeedText(
          ".ai-kanban/coordination/agent-dirty-grant.json",
          `${JSON.stringify({
            workspace_id: manifest.workspace_id,
            protocol_version: 1,
            actor_id: "dirty-grant",
            holder_id: "dirty-grant",
            run_id: "run-dirty-grant",
            sequence: 1,
            control_generation: 0,
            observed_revision: manifest.revision + 1,
            requested_state: "granting_agent",
            status: "requesting_control",
            current_turn_id: null,
            timestamp: new Date().toISOString(),
          })}\n`,
        );
        window.__boardWriteCount = 0;
        window.__failBoardWriteAt = 1;
      });
      await page.getByRole("button", { name: "Agent control" }).click();
      await page.getByRole("button", { name: "Retry" }).click();
      page.once("dialog", (dialog) => dialog.accept());
      await page.getByRole("button", { name: "Grant agent control" }).click();

      await expect(page.locator(".kanban-card", { hasText: "Dirty grant draft" })).toHaveCount(1);
      await expect(page.locator("#saveStatus")).toContainText("Unsaved");
      await expect(page.getByRole("button", { name: "New card" })).toBeEnabled();
      await page.evaluate(() => {
        window.__failBoardWriteAt = null;
      });
      await page.getByRole("button", { name: "Save workspace" }).click();
      await expect(page.locator("#saveStatus")).toContainText("Saved");
    });

    test("Use my draft reacquires a lock and keeps the dialog open when unavailable", async ({ page }) => {
      await installFakeWorkspace(page);
      await page.addInitScript(() => {
        const request = navigator.locks.request.bind(navigator.locks);
        window.__denyDraftRecoveryLock = false;
        navigator.locks.request = (name, options, callback) => {
          if (
            window.__denyDraftRecoveryLock &&
            name.startsWith("ai-kanban:") &&
            !name.startsWith("ai-kanban:create:") &&
            name !== "ai-kanban:directory-identity-registry"
          ) {
            return Promise.resolve(callback(null));
          }
          return request(name, options, callback);
        };
        const nativeSetTimeout = window.setTimeout.bind(window);
        window.setTimeout = (callback, delay, ...arguments_) =>
          nativeSetTimeout(callback, delay === 700 ? 10_000 : delay, ...arguments_);
      });
      await page.goto("/");
      await page.getByRole("button", { name: "Create Board Workspace" }).click();
      await page.getByRole("button", { name: "New card" }).click();
      await page.getByLabel("Title").fill("Recover with lock");
      await page.getByRole("button", { name: "Create card" }).click();
      await page.getByRole("button", { name: "Close card workspace" }).click();
      await page.evaluate(async () => {
        const manifest = JSON.parse(await window.__fakeReadText("manifest.json"));
        window.__denyDraftRecoveryLock = true;
        const sender = new BroadcastChannel("ai-kanban-workspaces");
        sender.postMessage({
          type: "saved",
          workspaceId: manifest.workspace_id,
          revision: manifest.revision + 1,
          fingerprint: "a".repeat(64),
        });
        sender.close();
      });
      await expect(page.locator("#conflictDialog")).toBeVisible();
      page.once("dialog", (dialog) => dialog.accept());
      await page.getByRole("button", { name: "Use my draft" }).click();
      await expect(page.locator("#conflictDialog")).toBeVisible();
      await expect(page.locator("#workspaceAlert")).toContainText(
        /exclusive workspace lock/,
      );

      await page.evaluate(() => {
        window.__denyDraftRecoveryLock = false;
      });
      page.once("dialog", (dialog) => dialog.accept());
      await page.getByRole("button", { name: "Use my draft" }).click();
      await expect(page.locator("#conflictDialog")).not.toBeVisible();
      await expect(page.locator("#saveStatus")).toContainText("Saved");
    });

    test("activation failure stops coordination and releases the workspace lock", async ({ page }) => {
      await installFakeWorkspace(page);
      await page.goto("/");
      await page.getByRole("button", { name: "Create Board Workspace" }).click();
      await page.getByRole("button", { name: "Workspace menu" }).click();
      await page.getByRole("button", { name: "Close workspace" }).click();
      await page.evaluate(() => {
        window.__failBootstrapRead = true;
      });
      await page.getByRole("button", { name: "Open Board Workspace" }).click();
      await expect(page.locator("#welcome")).toBeVisible();
      await page.waitForTimeout(200);
      const readsAfterFailure = await page.evaluate(() => window.__coordinationReads);
      await page.waitForTimeout(4_000);
      expect(await page.evaluate(() => window.__coordinationReads)).toBe(readsAfterFailure);

      await page.evaluate(() => {
        window.__failBootstrapRead = false;
      });
      await page.getByRole("button", { name: "Open Board Workspace" }).click();
      await expect(page.locator("#workspaceName")).toHaveText("Research Board");
      await expect(page.locator("#saveStatus")).not.toContainText("Read-only");
    });

    test("portable archive open rejects manifest and SQLite revision disagreement", async ({ page }) => {
      await page.goto("/");
      const archive = await page.evaluate(async () => {
        const { BoardRepository } = await import("./src/repository.js");
        const { createManifest } = await import("./src/file-workspace.js");
        const repository = new BoardRepository();
        const snapshot = await repository.create({ workspaceId: "archive-revision-mismatch" });
        const bytes = await repository.exportBytes();
        await repository.close();
        repository.terminate();
        const digest = await crypto.subtle.digest("SHA-256", bytes);
        const fingerprint = [...new Uint8Array(digest)]
          .map((byte) => byte.toString(16).padStart(2, "0"))
          .join("");
        const manifest = createManifest("archive-revision-mismatch");
        manifest.schema_version = Number(snapshot.meta.schema_version);
        manifest.revision = Number(snapshot.meta.revision) + 1;
        manifest.content_fingerprints["board.sqlite"] = fingerprint;
        manifest.application_files.find((item) => item.path === "board.sqlite").fingerprint =
          fingerprint;
        let binary = "";
        for (const byte of bytes) binary += String.fromCharCode(byte);
        return JSON.stringify({
          format: "ai-kanban-archive/v1",
          exported_at: new Date().toISOString(),
          manifest,
          board_base64: btoa(binary),
          files: {},
        });
      });
      await page.locator("#archiveInput").setInputFiles({
        name: "revision-mismatch.ai-kanban.json",
        mimeType: "application/json",
        buffer: Buffer.from(archive),
      });
      await expect(page.locator(".toast")).toContainText(/manifest commit marker/i);
      await expect(page.locator("#welcome")).toBeVisible();
    });

test("close and beforeunload protect in-flight saves with newer pending revisions", async ({ page }) => {
  await installFakeWorkspace(page);
  await page.addInitScript(() => {
    const nativeSetTimeout = window.setTimeout.bind(window);
    window.setTimeout = (callback, delay, ...arguments_) =>
      nativeSetTimeout(callback, delay === 700 ? 10_000 : delay, ...arguments_);
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Create Board Workspace" }).click();
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Older saved revision");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  await page.evaluate(() => {
    window.__delayWrites = true;
    window.__writeDelayMs = 500;
  });
  await page.getByRole("button", { name: "Save workspace" }).click();
  await expect.poll(() => page.evaluate(() => window.__activeWrites)).toBeGreaterThan(0);
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByLabel("Title").fill("Newer pending revision");
  await page.getByRole("button", { name: "Create card" }).click();
  await page.getByRole("button", { name: "Close card workspace" }).click();
  const unloadProtected = await page.evaluate(() => {
    const event = new Event("beforeunload", { cancelable: true });
    window.dispatchEvent(event);
    return event.defaultPrevented;
  });
  expect(unloadProtected).toBe(true);

  await page.getByRole("button", { name: "Workspace menu" }).click();
  await page.getByRole("button", { name: "Close workspace" }).click();
  await expect(page.locator("#welcome")).toBeVisible({ timeout: 10_000 });
  await page.evaluate(() => {
    window.__delayWrites = false;
  });
  await page.getByRole("button", { name: "Open Board Workspace" }).click();
  await expect(page.getByRole("heading", { name: "Older saved revision" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Newer pending revision" })).toBeVisible();
});
