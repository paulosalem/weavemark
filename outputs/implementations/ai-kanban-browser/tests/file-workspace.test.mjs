import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  MAX_ARCHIVE_ENCODED_BYTES,
  MAX_WORKSPACE_BYTES,
} from "../src/constants.js";
import {
  createManifest,
  FolderWorkspace,
  PortableWorkspace,
} from "../src/file-workspace.js";

class MemoryFileHandle {
  constructor(name, path, bytes = new Uint8Array(), controller = null) {
    this.kind = "file";
    this.name = name;
    this.path = path;
    this.bytes = bytes;
    this.controller = controller;
  }

  async getFile() {
    const bytes = this.bytes.slice();
    return {
      size: bytes.byteLength,
      lastModified: 1,
      arrayBuffer: async () => bytes.buffer.slice(0),
      text: async () => new TextDecoder().decode(bytes),
    };
  }

  async createWritable() {
    return {
      write: async (value) => {
        const key = this.path.join("/");
        const remaining = this.controller?.failuresByPath.get(key) || 0;
        if (remaining > 0) {
          this.controller.failuresByPath.set(key, remaining - 1);
          throw new Error(`Injected write failure: ${key}`);
        }
        this.bytes = value instanceof Uint8Array
          ? value.slice()
          : new Uint8Array(value);
      },
      close: async () => {},
      abort: async () => {},
    };
  }
}

class MemoryDirectoryHandle {
  constructor(name, path = [], controller = null) {
    this.kind = "directory";
    this.name = name;
    this.path = path;
    this.entries = new Map();
    this.controller = controller || this;
    if (!controller) this.failuresByPath = new Map();
  }

  async queryPermission() {
    return "granted";
  }

  async requestPermission() {
    return "granted";
  }

  async getDirectoryHandle(name, { create = false } = {}) {
    const existing = this.entries.get(name);
    if (existing?.kind === "directory") return existing;
    if (existing) throw new DOMException("Wrong kind", "TypeMismatchError");
    if (!create) throw new DOMException("Not found", "NotFoundError");
    const directory = new MemoryDirectoryHandle(
      name,
      [...this.path, name],
      this.controller,
    );
    this.entries.set(name, directory);
    return directory;
  }

  async getFileHandle(name, { create = false } = {}) {
    const existing = this.entries.get(name);
    if (existing?.kind === "file") return existing;
    if (existing) throw new DOMException("Wrong kind", "TypeMismatchError");
    if (!create) throw new DOMException("Not found", "NotFoundError");
    const file = new MemoryFileHandle(
      name,
      [...this.path, name],
      new Uint8Array(),
      this.controller,
    );
    this.entries.set(name, file);
    return file;
  }

  async resolve(handle) {
    return handle.path;
  }

  async removeEntry(name) {
    if (!this.entries.has(name)) {
      throw new DOMException("Not found", "NotFoundError");
    }
    this.entries.delete(name);
  }
}

async function putFile(root, path, value) {
  const parts = path.split("/");
  let directory = root;
  for (const part of parts.slice(0, -1)) {
    directory = await directory.getDirectoryHandle(part, { create: true });
  }
  const bytes = typeof value === "string"
    ? new TextEncoder().encode(value)
    : Uint8Array.from(value);
  directory.entries.set(
    parts.at(-1),
    new MemoryFileHandle(parts.at(-1), parts, bytes, root.controller),
  );
}

async function getFile(root, path) {
  const parts = path.split("/");
  let entry = root;
  for (const part of parts) entry = entry.entries.get(part);
  return entry;
}

test("readState fingerprints the exact bytes it returns", async () => {
  const first = Uint8Array.from([1, 2, 3, 4]);
  const second = Uint8Array.from([9, 8, 7, 6]);
  let reads = 0;
  const fileHandle = {
    kind: "file",
    name: "board.sqlite",
    async getFile() {
      reads += 1;
      const bytes = reads === 1 ? first : second;
      return {
        size: bytes.length,
        lastModified: reads,
        arrayBuffer: async () => bytes.buffer.slice(0),
      };
    },
  };
  const root = {
    name: "Board",
    async getFileHandle(name) {
      assert.equal(name, "board.sqlite");
      return fileHandle;
    },
    async resolve() {
      return ["board.sqlite"];
    },
  };
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: {
      workspace_id: "workspace-1",
      primary_state: "board.sqlite",
      revision: 12,
      content_fingerprints: {
        "board.sqlite": createHash("sha256").update(first).digest("hex"),
      },
    },
  });

  const returned = await workspace.readState();
  assert.deepEqual(returned, first);
  assert.equal(reads, 1);
  assert.equal(workspace.loadedSignature.revision, 12);
  assert.equal(
    workspace.loadedSignature.fingerprint,
    createHash("sha256").update(first).digest("hex"),
  );
});

test("readState rejects swapped same-revision database bytes", async () => {
  const root = new MemoryDirectoryHandle("Board");
  const trusted = Uint8Array.from([1, 2, 3]);
  const swapped = Uint8Array.from([3, 2, 1]);
  await putFile(root, "board.sqlite", swapped);
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: {
      workspace_id: "workspace-1",
      primary_state: "board.sqlite",
      revision: 7,
      content_fingerprints: {
        "board.sqlite": createHash("sha256").update(trusted).digest("hex"),
      },
    },
  });
  await assert.rejects(
    workspace.readState(),
    (error) => error.code === "STATE_FINGERPRINT_MISMATCH",
  );
});

test("initialize preserves bootstrap files until their exact replacement is confirmed", async () => {
  const root = new MemoryDirectoryHandle("Board");
  await putFile(root, "AGENTS.md", "# User instructions\n");
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: createManifest("bootstrap-test"),
  });
  const bootstrap = {
    "AGENTS.md": "# Generated instructions\n",
    "CLAUDE.md": "@AGENTS.md\n",
    ".agents/skills/ai-kanban/SKILL.md": "# Skill\n",
    ".agents/skills/ai-kanban/ai_kanban.py": "print('skill')\n",
    ".agents/skills/ai-kanban/ai-kanban.sh": "#!/bin/sh\n",
    ".agents/skills/ai-kanban/ai-kanban.ps1": "Write-Output skill\n",
  };

  await assert.rejects(
    workspace.initialize(Uint8Array.from([1, 2, 3]), bootstrap),
    (error) => error.code === "BOOTSTRAP_CONFIRMATION_REQUIRED",
  );
  assert.equal(
    await (await getFile(root, "AGENTS.md")).getFile().then((file) => file.text()),
    "# User instructions\n",
  );
  assert.equal(root.entries.has("board.sqlite"), false);

  await workspace.initialize(Uint8Array.from([1, 2, 3]), bootstrap, {
    confirmedReplacements: [
      { path: "AGENTS.md", actualContent: "# User instructions\n" },
    ],
  });
  assert.equal(
    await (await getFile(root, "AGENTS.md")).getFile().then((file) => file.text()),
    "# Generated instructions\n",
  );
  assert.deepEqual((await getFile(root, "board.sqlite")).bytes, Uint8Array.from([1, 2, 3]));
});

test("archive export includes validated attachment and artifact bytes", async () => {
  const root = new MemoryDirectoryHandle("Board");
  const attachment = Uint8Array.from([0, 1, 2, 3, 255]);
  const artifact = new TextEncoder().encode("artifact result");
  await putFile(root, "attachments/photo.bin", attachment);
  await putFile(root, "artifacts/result.txt", artifact);
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: createManifest("archive-test"),
  });
  const references = [
    {
      relativePath: "attachments/photo.bin",
      size: attachment.length,
      fingerprint: createHash("sha256").update(attachment).digest("hex"),
      kind: "attachment",
    },
    {
      relativePath: "artifacts/result.txt",
      fingerprint: createHash("sha256").update(artifact).digest("hex"),
      kind: "artifact",
    },
  ];

  const stateBytes = Uint8Array.from([83, 81, 76]);
  const archive = await workspace.exportArchive(stateBytes, references, 27);
  assert.equal(archive.manifest.revision, 27);
  assert.equal(
    archive.manifest.content_fingerprints["board.sqlite"],
    createHash("sha256").update(stateBytes).digest("hex"),
  );
  assert.equal(archive.files["attachments/photo.bin"].encoding, "base64");
  assert.deepEqual(
    Buffer.from(archive.files["attachments/photo.bin"].data, "base64"),
    Buffer.from(attachment),
  );
  assert.deepEqual(
    Buffer.from(archive.files["artifacts/result.txt"].data, "base64"),
    Buffer.from(artifact),
  );
  const imported = await PortableWorkspace.fromArchiveFile({
    name: "draft.ai-kanban.json",
    size: new TextEncoder().encode(JSON.stringify(archive)).byteLength,
    text: async () => JSON.stringify(archive),
  });
  assert.deepEqual(await imported.readState(), stateBytes);
  await assert.rejects(
    workspace.exportArchive(Uint8Array.from([1]), [
      { relativePath: "../escape.bin", kind: "attachment" },
    ]),
    /relative|escape/i,
  );
});

test("initialization restores every touched file after a late failure", async () => {
  const root = new MemoryDirectoryHandle("Board");
  await putFile(root, "AGENTS.md", "# Original user instructions\n");
  root.failuresByPath.set("manifest.json", 1);
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: createManifest("atomic-initialize"),
  });

  const bootstrap = {
    "AGENTS.md": "# Generated instructions\n",
    "CLAUDE.md": "@AGENTS.md\n",
    ".agents/skills/ai-kanban/SKILL.md": "# Skill\n",
    ".agents/skills/ai-kanban/ai_kanban.py": "print('skill')\n",
    ".agents/skills/ai-kanban/ai-kanban.sh": "#!/bin/sh\n",
    ".agents/skills/ai-kanban/ai-kanban.ps1": "Write-Output skill\n",
  };

  await assert.rejects(
    workspace.initialize(Uint8Array.from([1, 2, 3]), bootstrap, {
      confirmedReplacements: [{
        path: "AGENTS.md",
        actualContent: "# Original user instructions\n",
      }],
    }),
    (error) => error.code === "INITIALIZATION_FAILED",
  );

  assert.equal(
    await (await getFile(root, "AGENTS.md")).getFile().then((file) => file.text()),
    "# Original user instructions\n",
  );
  for (const path of [
    "board.sqlite",
    "CLAUDE.md",
    ".agents/skills/ai-kanban/SKILL.md",
    ".ai-kanban/coordination/human.json",
    "manifest.json",
  ]) {
    assert.equal(await getFile(root, path), undefined, `${path} should be removed`);
  }
});

test("save and archive paths reject oversized state before writing", async () => {
  class OversizedBytes extends Uint8Array {
    get byteLength() {
      return MAX_WORKSPACE_BYTES + 1;
    }
  }
  const oversized = new OversizedBytes(0);
  const root = new MemoryDirectoryHandle("Board");
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: createManifest("size-limit"),
  });
  await assert.rejects(
    workspace.saveState(oversized),
    (error) => error.code === "WORKSPACE_TOO_LARGE",
  );
  await assert.rejects(
    workspace.exportArchive(oversized),
    (error) => error.code === "WORKSPACE_TOO_LARGE",
  );
  assert.equal(root.entries.size, 0);
});

test("bootstrap repair uses exact-content CAS immediately before overwrite", async () => {
  const root = new MemoryDirectoryHandle("Board");
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: createManifest("repair-cas"),
  });

  workspace.setWriterLock({ acquired: true });
  await workspace.initialize(Uint8Array.from([1]), {
    "AGENTS.md": "# Compared content\n",
    "CLAUDE.md": "@AGENTS.md\n",
    ".agents/skills/ai-kanban/SKILL.md": "# Skill\n",
    ".agents/skills/ai-kanban/ai_kanban.py": "print('skill')\n",
    ".agents/skills/ai-kanban/ai-kanban.sh": "#!/bin/sh\n",
    ".agents/skills/ai-kanban/ai-kanban.ps1": "Write-Output skill\n",
  });
  const [comparison] = await workspace.bootstrapStatus({
    "AGENTS.md": "# Generated content\n",
  });
  (await getFile(root, "AGENTS.md")).bytes = new TextEncoder().encode(
    "# Changed after comparison\n",
  );
  await assert.rejects(
    workspace.repairBootstrap([{
      ...comparison,
      state: "confirmed-replace",
    }]),
    (error) => error.code === "BOOTSTRAP_CONFLICT",
  );
  assert.equal(
    await (await getFile(root, "AGENTS.md")).getFile().then((file) => file.text()),
    "# Changed after comparison\n",
  );
  workspace.setWriterLock({ acquired: false });
  await assert.rejects(
    workspace.repairBootstrap([{
      ...comparison,
      state: "confirmed-replace",
    }]),
    (error) => error.code === "WORKSPACE_LOCK_REQUIRED",
  );
});

test("initialization final CAS preserves sentinels created after assertCreatable", async () => {
  const root = new MemoryDirectoryHandle("Board");
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: createManifest("creation-cas"),
  });
  await workspace.assertCreatable();
  await putFile(root, ".ai-kanban/coordination/human.json", "sentinel\n");
  const bootstrap = Object.fromEntries([
    "AGENTS.md",
    "CLAUDE.md",
    ".agents/skills/ai-kanban/SKILL.md",
    ".agents/skills/ai-kanban/ai_kanban.py",
    ".agents/skills/ai-kanban/ai-kanban.sh",
    ".agents/skills/ai-kanban/ai-kanban.ps1",
  ].map((path) => [path, `${path}\n`]));

  await assert.rejects(
    workspace.initialize(Uint8Array.from([1, 2, 3]), bootstrap),
    (error) => error.code === "WORKSPACE_NOT_EMPTY",
  );
  assert.equal(
    await (await getFile(root, ".ai-kanban/coordination/human.json"))
      .getFile()
      .then((file) => file.text()),
    "sentinel\n",
  );
  assert.equal(await getFile(root, "board.sqlite"), undefined);
});

test("save rollback restores exact on-disk manifest bytes", async () => {
  const root = new MemoryDirectoryHandle("Board");
  const workspace = new FolderWorkspace({
    handle: root,
    manifest: createManifest("exact-manifest-rollback"),
  });
  const bootstrap = Object.fromEntries([
    "AGENTS.md",
    "CLAUDE.md",
    ".agents/skills/ai-kanban/SKILL.md",
    ".agents/skills/ai-kanban/ai_kanban.py",
    ".agents/skills/ai-kanban/ai-kanban.sh",
    ".agents/skills/ai-kanban/ai-kanban.ps1",
  ].map((path) => [path, `${path}\n`]));
  await workspace.initialize(Uint8Array.from([1, 2, 3]), bootstrap);
  const parsed = JSON.parse(
    await (await getFile(root, "manifest.json")).getFile().then((file) => file.text()),
  );
  const exactManifest = `{\n  "format": "${parsed.format}",\n${Object.entries(parsed)
    .filter(([key]) => key !== "format")
    .map(([key, value]) => `  ${JSON.stringify(key)}: ${JSON.stringify(value)}`)
    .join(",\n")}\n}\n\n`;
  await putFile(root, "manifest.json", exactManifest);
  workspace.manifest = parsed;
  await workspace.captureLoadedSignature(Uint8Array.from([1, 2, 3]));
  root.failuresByPath.set("manifest.json", 1);

  await assert.rejects(
    workspace.saveState(Uint8Array.from([4, 5, 6]), { revision: 1 }),
    (error) => error.code === "PARTIAL_SAVE",
  );
  assert.equal(
    await (await getFile(root, "manifest.json")).getFile().then((file) => file.text()),
    exactManifest,
  );
  assert.deepEqual((await getFile(root, "board.sqlite")).bytes, Uint8Array.from([1, 2, 3]));
});

test("archive imports reject oversized File.size before reading", async () => {
  let read = false;
  await assert.rejects(
    PortableWorkspace.fromArchiveFile({
      name: "oversized.ai-kanban.json",
      size: MAX_ARCHIVE_ENCODED_BYTES + 1,
      text: async () => {
        read = true;
        return "{}";
      },
    }),
    (error) => error.code === "IMPORT_SIZE_LIMIT",
  );
  assert.equal(read, false);
});

test("archive imports allow base64 overhead before enforcing decoded limits", async () => {
  let read = false;
  await assert.rejects(
    PortableWorkspace.fromArchiveFile({
      name: "encoded-overhead.ai-kanban.json",
      size: MAX_WORKSPACE_BYTES + 1,
      text: async () => {
        read = true;
        return "{}";
      },
    }),
    (error) => error.code === "INVALID_ARCHIVE",
  );
  assert.equal(read, true);
});
