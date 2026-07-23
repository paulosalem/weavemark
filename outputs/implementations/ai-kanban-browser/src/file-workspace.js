const RECENT_DATABASE = "ai-kanban-browser";
const RECENT_STORE = "handles";
const RECENT_KEY = "recent-workspace";

export const nativeFileSystemSupported =
  typeof window.showOpenFilePicker === "function" &&
  typeof window.showSaveFilePicker === "function";

export class WorkspaceConflictError extends Error {
  constructor(message = "The workspace file changed outside AI Kanban.") {
    super(message);
    this.name = "WorkspaceConflictError";
    this.code = "EXTERNAL_FILE_CONFLICT";
  }
}

export class FileWorkspace {
  constructor({ handle = null, file = null, name, mode, baseline = null }) {
    this.handle = handle;
    this.file = file;
    this.name = name;
    this.mode = mode;
    this.baseline = baseline;
    this.lastSavedAt = null;
  }

  static async openNative() {
    const [handle] = await window.showOpenFilePicker({
      id: "ai-kanban-workspace",
      multiple: false,
      types: [sqlitePickerType()],
    });
    return FileWorkspace.fromHandle(handle);
  }

  static async createNative() {
    const handle = await window.showSaveFilePicker({
      id: "ai-kanban-workspace",
      suggestedName: "my-board.aikanban.sqlite",
      types: [sqlitePickerType()],
    });
    const file = await handle.getFile();
    return new FileWorkspace({
      handle,
      name: handle.name,
      mode: "connected",
      baseline: await signature(file),
    });
  }

  static async fromHandle(handle) {
    const permission = await verifyPermission(handle, true);
    if (!permission) {
      const error = new Error("Write permission was not granted for this workspace.");
      error.code = "PERMISSION_DENIED";
      throw error;
    }
    const file = await handle.getFile();
    const workspace = new FileWorkspace({
      handle,
      name: handle.name,
      mode: "connected",
      baseline: await signature(file),
    });
    await rememberHandle(handle);
    return workspace;
  }

  static async fromImportedFile(file) {
    return new FileWorkspace({
      file,
      name: file.name,
      mode: "import/download",
      baseline: await signature(file),
    });
  }

  static memoryDemo() {
    return new FileWorkspace({
      name: "Demo board · not saved",
      mode: "memory-only",
    });
  }

  async readBytes() {
    const file = this.handle ? await this.handle.getFile() : this.file;
    if (!file) return null;
    this.baseline = await signature(file);
    return new Uint8Array(await file.arrayBuffer());
  }

  async save(bytes, { force = false } = {}) {
    if (this.mode === "memory-only") {
      const error = new Error("Choose Save As to make the demo durable.");
      error.code = "NO_FILE_HANDLE";
      throw error;
    }
    if (this.mode === "import/download") {
      downloadBytes(bytes, this.name);
      this.lastSavedAt = new Date().toISOString();
      return { downloaded: true };
    }
    if (!this.handle) throw new Error("Connected workspace has no file handle.");

    const permission = await verifyPermission(this.handle, true);
    if (!permission) {
      const error = new Error("Write permission is required to save this workspace.");
      error.code = "PERMISSION_DENIED";
      throw error;
    }
    if (!force && this.baseline) {
      const current = await this.handle.getFile();
      const currentSignature = await signature(current);
      if (!sameSignature(this.baseline, currentSignature)) {
        throw new WorkspaceConflictError();
      }
    }

    const writable = await this.handle.createWritable();
    await writable.write(bytes);
    await writable.close();
    const written = await this.handle.getFile();
    this.baseline = await signature(written);
    this.lastSavedAt = new Date().toISOString();
    await rememberHandle(this.handle);
    return { downloaded: false };
  }

  async saveAs(bytes) {
    if (!nativeFileSystemSupported) {
      downloadBytes(bytes, this.name || "ai-kanban.aikanban.sqlite");
      this.mode = "import/download";
      this.lastSavedAt = new Date().toISOString();
      return;
    }
    const handle = await window.showSaveFilePicker({
      id: "ai-kanban-workspace",
      suggestedName: normalizedName(this.name),
      types: [sqlitePickerType()],
    });
    this.handle = handle;
    this.file = null;
    this.name = handle.name;
    this.mode = "connected";
    const existing = await handle.getFile();
    this.baseline = await signature(existing);
    await this.save(bytes, { force: true });
  }

  details() {
    return {
      name: this.name,
      mode: this.mode,
      size: this.baseline?.size ?? "Not saved",
      modified: this.baseline?.lastModified
        ? new Date(this.baseline.lastModified).toLocaleString()
        : "Not saved",
      fingerprint: this.baseline?.hash
        ? `${this.baseline.hash.slice(0, 12)}…`
        : "Not saved",
      lastSaved: this.lastSavedAt
        ? new Date(this.lastSavedAt).toLocaleString()
        : "This session has not saved yet",
    };
  }
}

export async function recentHandle() {
  try {
    return await idbGet(RECENT_KEY);
  } catch (error) {
    if (error instanceof DOMException) return null;
    throw error;
  }
}

export async function clearRecentHandle() {
  try {
    await idbDelete(RECENT_KEY);
  } catch (error) {
    if (!(error instanceof DOMException)) throw error;
  }
}

export async function queryHandlePermission(handle) {
  if (!handle?.queryPermission) return "prompt";
  return handle.queryPermission({ mode: "readwrite" });
}

export async function acquireWorkspaceLock(workspaceId) {
  if (!navigator.locks || !workspaceId) {
    return { acquired: true, release() {} };
  }
  let releaseLock;
  let announce;
  const acquired = new Promise((resolve) => {
    announce = resolve;
  });
  navigator.locks.request(
    `ai-kanban:${workspaceId}`,
    { ifAvailable: true, mode: "exclusive" },
    (lock) => {
      if (!lock) {
        announce(false);
        return undefined;
      }
      announce(true);
      return new Promise((resolve) => {
        releaseLock = resolve;
      });
    },
  );
  const didAcquire = await acquired;
  return {
    acquired: didAcquire,
    release() {
      releaseLock?.();
    },
  };
}

async function verifyPermission(handle, write) {
  const options = { mode: write ? "readwrite" : "read" };
  if ((await handle.queryPermission?.(options)) === "granted") return true;
  return (await handle.requestPermission?.(options)) === "granted";
}

async function rememberHandle(handle) {
  try {
    await idbSet(RECENT_KEY, handle);
  } catch (error) {
    if (!(error instanceof DOMException)) throw error;
  }
}

async function signature(file) {
  const bytes = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return {
    size: file.size,
    lastModified: file.lastModified,
    hash: [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join(""),
  };
}

function sameSignature(left, right) {
  return (
    left.size === right.size &&
    left.lastModified === right.lastModified &&
    left.hash === right.hash
  );
}

function sqlitePickerType() {
  return {
    description: "AI Kanban SQLite workspace",
    accept: {
      "application/vnd.sqlite3": [".sqlite", ".aikanban.sqlite"],
      "application/octet-stream": [".sqlite"],
    },
  };
}

function normalizedName(name = "") {
  if (name.endsWith(".aikanban.sqlite")) return name;
  return `${name.replace(/\.(sqlite|db)$/i, "") || "ai-kanban"}.aikanban.sqlite`;
}

function downloadBytes(bytes, name) {
  const blob = new Blob([bytes], { type: "application/vnd.sqlite3" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = normalizedName(name);
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 0);
}

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(RECENT_DATABASE, 1);
    request.addEventListener("upgradeneeded", () => {
      request.result.createObjectStore(RECENT_STORE);
    });
    request.addEventListener("success", () => resolve(request.result));
    request.addEventListener("error", () => reject(request.error));
  });
}

async function idbGet(key) {
  const database = await openDatabase();
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(RECENT_STORE, "readonly");
    const request = transaction.objectStore(RECENT_STORE).get(key);
    request.addEventListener("success", () => resolve(request.result || null));
    request.addEventListener("error", () => reject(request.error));
    transaction.addEventListener("complete", () => database.close());
  });
}

async function idbSet(key, value) {
  const database = await openDatabase();
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(RECENT_STORE, "readwrite");
    transaction.objectStore(RECENT_STORE).put(value, key);
    transaction.addEventListener("complete", () => {
      database.close();
      resolve();
    });
    transaction.addEventListener("error", () => reject(transaction.error));
  });
}

async function idbDelete(key) {
  const database = await openDatabase();
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(RECENT_STORE, "readwrite");
    transaction.objectStore(RECENT_STORE).delete(key);
    transaction.addEventListener("complete", () => {
      database.close();
      resolve();
    });
    transaction.addEventListener("error", () => reject(transaction.error));
  });
}
