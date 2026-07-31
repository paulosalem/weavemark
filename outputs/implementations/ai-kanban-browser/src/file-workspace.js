import {
  APPLICATION_FILES,
  APP_VERSION,
  ARCHIVE_FORMAT,
  BOOTSTRAP_FILES,
  MANIFEST_FILE,
  MAX_ARCHIVE_ENCODED_BYTES,
  MAX_ARCHIVE_FILE_BYTES,
  MAX_ARCHIVE_FILES,
  MAX_ARCHIVE_TOTAL_BYTES,
  MAX_WORKSPACE_BYTES,
  PROTOCOL_VERSION,
  RESERVED_DIRECTORIES,
  SCHEMA_VERSION,
  STATE_FILE,
  WORKSPACE_FORMAT,
  WORKSPACE_FORMAT_VERSION,
} from "./constants.js";
import {
  assertRelativePath,
  validateArchive,
  validateManifest,
  ValidationError,
} from "./validation.js";

const RECENT_DATABASE = "ai-kanban-browser";
const RECENT_STORE = "handles";
const RECENT_KEY = "recent-workspace";
const DIRECTORY_IDENTITIES_KEY = "directory-identities";
const directoryIdentityCache = new WeakMap();

export const nativeFileSystemSupported =
  typeof window !== "undefined" &&
  typeof window.showDirectoryPicker === "function" &&
  window.isSecureContext;

export class WorkspaceConflictError extends Error {
  constructor(details) {
    super("The workspace changed outside AI Kanban.");
    this.name = "WorkspaceConflictError";
    this.code = "EXTERNAL_FILE_CONFLICT";
    this.details = details;
  }
}

export class WorkspaceError extends Error {
  constructor(code, message, details = null) {
    super(message);
    this.name = "WorkspaceError";
    this.code = code;
    this.details = details;
  }
}

export class FolderWorkspace {
  constructor({ handle, manifest, permission = "granted" }) {
    this.handle = handle;
    this.manifest = manifest;
    this.name = handle.name;
    this.mode = "connected";
    this.permission = permission;
    this.lastSavedAt = null;
    this.loadedSignature = null;
    this.writerLock = null;
  }

  static async openNative() {
    const handle = await window.showDirectoryPicker({
      id: "ai-kanban-workspace",
      mode: "readwrite",
      startIn: "documents",
    });
    await requirePermission(handle, true);
    return FolderWorkspace.fromHandle(handle);
  }

  static async createNative() {
    const handle = await window.showDirectoryPicker({
      id: "ai-kanban-workspace-create",
      mode: "readwrite",
      startIn: "documents",
    });
    await requirePermission(handle, true);
    if (await entryExists(handle, MANIFEST_FILE) || await entryExists(handle, STATE_FILE)) {
      throw new WorkspaceError(
        "WORKSPACE_NOT_EMPTY",
        "This folder already contains AI Kanban state. Open it instead, or choose an empty folder.",
      );
    }
    const manifest = createManifest();
    return new FolderWorkspace({ handle, manifest });
  }

  async assertCreatable() {
    const protectedTargets = [
      MANIFEST_FILE,
      STATE_FILE,
      ".ai-kanban/coordination/human.json",
    ];
    if ((await Promise.all(
      protectedTargets.map((path) => entryExists(this.handle, path)),
    )).some(Boolean)) {
      throw new WorkspaceError(
        "WORKSPACE_NOT_EMPTY",
        "This folder acquired AI Kanban state while creation was waiting. Open it instead.",
      );
    }
  }

  setWriterLock(lock) {
    this.writerLock = lock;
  }

  static async fromHandle(handle) {
    const permission = await queryHandlePermission(handle);
    if (permission !== "granted") {
      throw new WorkspaceError(
        "PERMISSION_PROMPT_REQUIRED",
        "Reconnect requires permission from an explicit button.",
      );
    }
    const manifest = await readManifest(handle);
    const workspace = new FolderWorkspace({ handle, manifest, permission });
    await workspace.captureLoadedSignature();
    await rememberHandle(handle);
    return workspace;
  }

  async initialize(
    stateBytes,
    bootstrapFiles,
    { confirmedReplacements = [] } = {},
  ) {
    if (!(stateBytes instanceof Uint8Array)) throw new TypeError("SQLite bytes are required.");
    for (const path of Object.keys(bootstrapFiles)) {
      if (!BOOTSTRAP_FILES.includes(path)) throw new ValidationError("Unexpected bootstrap file.");
    }
    if (BOOTSTRAP_FILES.some((path) => typeof bootstrapFiles[path] !== "string")) {
      throw new ValidationError("Every canonical bootstrap file must be preflighted.");
    }
    const status = await this.bootstrapStatus(bootstrapFiles);
    const conflicts = status.filter((item) => item.state === "path-conflict");
    if (conflicts.length) {
      throw new WorkspaceError(
        "BOOTSTRAP_PATH_CONFLICT",
        "A bootstrap path is occupied by a non-file entry and cannot be replaced.",
        conflicts,
      );
    }
    const confirmed = new Map(
      confirmedReplacements.map((item) => [
        typeof item === "string" ? item : item.path,
        typeof item === "string" ? null : item.actualContent,
      ]),
    );
    const unconfirmed = status.filter(
      (item) =>
        item.state === "modified" &&
        (
          !confirmed.has(item.path) ||
          (
            confirmed.get(item.path) !== null &&
            confirmed.get(item.path) !== item.actualContent
          )
        ),
    );
    if (unconfirmed.length) {
      throw new WorkspaceError(
        "BOOTSTRAP_CONFIRMATION_REQUIRED",
        "Existing bootstrap files require explicit replacement confirmation.",
        unconfirmed,
      );
    }
    const humanPath = ".ai-kanban/coordination/human.json";
    const targets = [
      STATE_FILE,
      ...BOOTSTRAP_FILES,
      humanPath,
      MANIFEST_FILE,
    ];
    const snapshots = await captureFileSnapshots(this.handle, targets);
    for (const path of [STATE_FILE, humanPath, MANIFEST_FILE]) {
      if (snapshots.get(path)?.existed) {
        throw new WorkspaceError(
          "WORKSPACE_NOT_EMPTY",
          `Workspace initialization will not overwrite an existing ${path}.`,
        );
      }
    }
    const previousManifest = structuredClone(this.manifest);
    const touched = new Set();
    const humanRecord = JSON.stringify({
      workspace_id: this.manifest.workspace_id,
      protocol_version: PROTOCOL_VERSION,
      actor_id: "human",
      holder_id: "human",
      sequence: 0,
      control_generation: 0,
      observed_revision: 0,
      requested_state: "human",
      timestamp: new Date().toISOString(),
    }, null, 2);
    try {
      await ensureDirectories(this.handle, RESERVED_DIRECTORIES);
      await writeBinaryCas(
        this.handle,
        STATE_FILE,
        stateBytes,
        snapshots.get(STATE_FILE),
        () => touched.add(STATE_FILE),
      );
      for (const item of status) {
        if (item.state === "missing" || item.state === "modified") {
          await writeBinaryCas(
            this.handle,
            item.path,
            new TextEncoder().encode(item.expectedContent),
            snapshots.get(item.path),
            () => touched.add(item.path),
          );
        }
      }
      await writeBinaryCas(
        this.handle,
        humanPath,
        new TextEncoder().encode(`${humanRecord}\n`),
        snapshots.get(humanPath),
        () => touched.add(humanPath),
      );
      await this.#refreshManifestFingerprints();
      await writeBinaryCas(
        this.handle,
        MANIFEST_FILE,
        new TextEncoder().encode(`${JSON.stringify(this.manifest, null, 2)}\n`),
        snapshots.get(MANIFEST_FILE),
        () => touched.add(MANIFEST_FILE),
      );
      await this.captureLoadedSignature(stateBytes);
    } catch (error) {
      this.manifest = previousManifest;
      const touchedSnapshots = new Map(
        [...snapshots].filter(([path]) => touched.has(path)),
      );
      const rollbackErrors = await restoreFileSnapshots(this.handle, touchedSnapshots);
      if (rollbackErrors.length) {
        throw new WorkspaceError(
          "INITIALIZATION_ROLLBACK_FAILED",
          "Workspace initialization failed and one or more files could not be restored.",
          {
            cause: error.message,
            rollbackErrors,
          },
        );
      }
      throw new WorkspaceError(
        "INITIALIZATION_FAILED",
        `Workspace initialization failed; every touched file was restored. ${error.message}`,
        error.message,
      );
    }
    await rememberHandle(this.handle);
  }

  async readState() {
    const bytes = await readBinary(this.handle, this.manifest.primary_state);
    if (bytes.byteLength > MAX_WORKSPACE_BYTES) {
      throw new WorkspaceError(
        "WORKSPACE_TOO_LARGE",
        "This workspace exceeds the 250 MB whole-file safety limit.",
      );
    }
    const expected = this.manifest.content_fingerprints?.[
      this.manifest.primary_state
    ];
    if (typeof expected !== "string" || !expected) {
      throw new WorkspaceError(
        "STATE_FINGERPRINT_MISSING",
        "manifest.json does not fingerprint the canonical SQLite state.",
      );
    }
    const actual = await sha256(bytes);
    if (actual !== expected) {
      throw new WorkspaceError(
        "STATE_FINGERPRINT_MISMATCH",
        "board.sqlite does not match its manifest fingerprint.",
        { expected, actual },
      );
    }
    await this.captureLoadedSignature(bytes);
    return bytes;
  }

  async readStateForStabilization() {
    const bytes = await readBinary(this.handle, this.manifest.primary_state);
    if (bytes.byteLength > MAX_WORKSPACE_BYTES) {
      throw new WorkspaceError(
        "WORKSPACE_TOO_LARGE",
        "This workspace exceeds the 250 MB whole-file safety limit.",
      );
    }
    return bytes;
  }

  async saveState(bytes, { revision = null } = {}) {
    return this.#writeState(bytes, { revision, forceRecovery: false });
  }

  async recoverState(bytes, { revision = null } = {}) {
    if (!this.writerLock?.acquired) {
      throw new WorkspaceError(
        "WORKSPACE_LOCK_REQUIRED",
        "Explicit draft recovery requires this tab's newly acquired workspace lock.",
      );
    }
    return this.#writeState(bytes, { revision, forceRecovery: true });
  }

  async #writeState(bytes, { revision, forceRecovery }) {
    assertStateSize(bytes);
    await requirePermission(this.handle, true);
    if (!forceRecovery) await this.assertUnchanged();
    const previousBytes = await readBinary(this.handle, this.manifest.primary_state);
    const previousManifestBytes = await readBinary(this.handle, MANIFEST_FILE);
    const previousManifest = structuredClone(this.manifest);
    try {
      await writeBinary(this.handle, this.manifest.primary_state, bytes);
      this.manifest.updated_at = new Date().toISOString();
      if (Number.isSafeInteger(revision)) this.manifest.revision = revision;
      await this.#refreshManifestFingerprints();
      await writeManifest(this.handle, this.manifest);
      this.lastSavedAt = new Date().toISOString();
      await this.captureLoadedSignature(bytes);
      await rememberHandle(this.handle);
    } catch (error) {
      await writeBinary(this.handle, this.manifest.primary_state, previousBytes).catch(() => {});
      this.manifest = previousManifest;
      await writeBinary(this.handle, MANIFEST_FILE, previousManifestBytes).catch(() => {});
      throw new WorkspaceError(
        "PARTIAL_SAVE",
        "Saving did not finish. The exact previous database and manifest bytes were restored when possible.",
        error.message,
      );
    }
  }

  async assertUnchanged() {
    if (!this.loadedSignature) return;
    const currentManifest = await readManifest(this.handle);
    const currentBytes = await readBinary(this.handle, currentManifest.primary_state);
    const current = {
      revision: Number(currentManifest.revision || 0),
      fingerprint: await sha256(currentBytes),
      manifestFingerprint: await manifestFingerprint(currentManifest),
    };
    if (
      current.revision !== this.loadedSignature.revision ||
      current.fingerprint !== this.loadedSignature.fingerprint ||
      current.manifestFingerprint !== this.loadedSignature.manifestFingerprint
    ) {
      throw new WorkspaceConflictError({
        loaded: this.loadedSignature,
        disk: current,
      });
    }
  }

  async captureLoadedSignature(stateBytes = null) {
    const bytes = stateBytes ?? await readBinary(this.handle, this.manifest.primary_state);
    this.loadedSignature = {
      revision: Number(this.manifest.revision || 0),
      fingerprint: await sha256(bytes),
      manifestFingerprint: await manifestFingerprint(this.manifest),
    };
  }

  async reloadManifest() {
    this.manifest = await readManifest(this.handle);
    return this.manifest;
  }

  async journalState() {
    const sidecars = [];
    for (const suffix of ["-journal", "-wal", "-shm"]) {
      const path = `${this.manifest.primary_state}${suffix}`;
      if (await entryExists(this.handle, path)) sidecars.push(path);
    }
    return sidecars;
  }

  async writeCoordination(path, record) {
    if (!path.startsWith(".ai-kanban/coordination/")) {
      throw new ValidationError("Coordination record path is outside the mailbox.");
    }
    await writeText(this.handle, path, `${JSON.stringify(record, null, 2)}\n`);
  }

  async readCoordinationRecords() {
    const directory = await directoryAt(this.handle, [".ai-kanban", "coordination"], false);
    const records = [];
    for await (const entry of directory.values()) {
      if (entry.kind !== "file" || !entry.name.endsWith(".json")) continue;
      try {
        const text = await (await entry.getFile()).text();
        records.push({ path: `.ai-kanban/coordination/${entry.name}`, value: JSON.parse(text) });
      } catch {
        records.push({ path: `.ai-kanban/coordination/${entry.name}`, value: null });
      }
    }
    return records;
  }

  async bootstrapStatus(expectedFiles) {
    const status = [];
    for (const [path, expectedContent] of Object.entries(expectedFiles)) {
      let actual = null;
      try {
        actual = await readText(this.handle, path);
      } catch (error) {
        if (error.name === "TypeMismatchError") {
          status.push({
            path,
            state: "path-conflict",
            expectedContent,
            actualContent: null,
          });
          continue;
        }
        if (error.name !== "NotFoundError") throw error;
      }
      status.push({
        path,
        state: actual == null ? "missing" : actual === expectedContent ? "current" : "modified",
        expectedContent,
        actualContent: actual,
      });
    }
    return status;
  }

  async repairBootstrap(items) {
    if (!this.writerLock?.acquired) {
      throw new WorkspaceError(
        "WORKSPACE_LOCK_REQUIRED",
        "Bootstrap repair requires this tab's writable workspace lock.",
      );
    }
    await this.assertUnchanged();
    const expectedRevision = this.loadedSignature.revision;
    const expectedFingerprint = this.loadedSignature.fingerprint;
    for (const item of items) {
      if (!["missing", "confirmed-replace"].includes(item.state)) continue;
      let current = null;
      try {
        current = await readText(this.handle, item.path);
      } catch (error) {
        if (error.name !== "NotFoundError") throw error;
      }
      const matchesApprovedComparison = item.state === "missing"
        ? current === null
        : current === item.actualContent;
      if (!matchesApprovedComparison) {
        throw new WorkspaceError(
          "BOOTSTRAP_CONFLICT",
          `Bootstrap file changed after approval: ${item.path}`,
        );
      }
      await writeText(this.handle, item.path, item.expectedContent);
    }
    if (
      this.loadedSignature.revision !== expectedRevision ||
      this.loadedSignature.fingerprint !== expectedFingerprint
    ) {
      throw new WorkspaceConflictError();
    }
    await this.#refreshManifestFingerprints();
    await writeManifest(this.handle, this.manifest);
    this.loadedSignature = {
      ...this.loadedSignature,
      manifestFingerprint: await manifestFingerprint(this.manifest),
    };
  }

  async exportArchive(stateBytes, referencedFiles = [], revision = null) {
    assertStateSize(stateBytes);
    const files = {};
    let totalBytes = stateBytes.byteLength;
    for (const path of BOOTSTRAP_FILES) {
      try {
        const content = await readText(this.handle, path);
        totalBytes += new TextEncoder().encode(content).byteLength;
        files[path] = content;
      } catch (error) {
        if (error.name !== "NotFoundError") throw error;
      }
    }
    if (totalBytes > MAX_ARCHIVE_TOTAL_BYTES) {
      throw new WorkspaceError(
        "ARCHIVE_SIZE_LIMIT",
        "Archive content exceeds the 250 MB total limit.",
      );
    }
    const references = new Map();
    for (const reference of referencedFiles) {
      const path = reference?.relativePath;
      validateArchiveContentPath(path, reference?.kind);
      references.set(path, reference);
    }
    for (const item of this.manifest.application_files || []) {
      if (
        typeof item?.path === "string" &&
        (item.path.startsWith("attachments/") || item.path.startsWith("artifacts/"))
      ) {
        validateArchiveContentPath(item.path);
        if (!references.has(item.path)) {
          references.set(item.path, {
            relativePath: item.path,
            fingerprint: item.fingerprint || this.manifest.content_fingerprints?.[item.path],
            kind: item.path.startsWith("attachments/") ? "attachment" : "artifact",
          });
        }
      }
    }
    if (references.size > MAX_ARCHIVE_FILES) {
      throw new WorkspaceError(
        "ARCHIVE_FILE_LIMIT",
        `Archive references exceed the ${MAX_ARCHIVE_FILES} file limit.`,
      );
    }
    for (const [path, reference] of references) {
      if (
        Number.isSafeInteger(reference.size) &&
        reference.size > MAX_ARCHIVE_FILE_BYTES
      ) {
        throw new WorkspaceError(
          "ARCHIVE_FILE_TOO_LARGE",
          `${path} exceeds the 50 MB per-file archive limit.`,
        );
      }
      let bytes;
      try {
        bytes = await readBinary(this.handle, path);
      } catch (error) {
        if (error.name === "NotFoundError") {
          throw new WorkspaceError(
            "ARCHIVE_REFERENCE_MISSING",
            `Referenced archive file is missing: ${path}`,
          );
        }
        throw error;
      }
      if (bytes.byteLength > MAX_ARCHIVE_FILE_BYTES) {
        throw new WorkspaceError(
          "ARCHIVE_FILE_TOO_LARGE",
          `${path} exceeds the 50 MB per-file archive limit.`,
        );
      }
      if (
        Number.isSafeInteger(reference.size) &&
        reference.size !== bytes.byteLength
      ) {
        throw new WorkspaceError(
          "ARCHIVE_REFERENCE_MISMATCH",
          `Referenced archive file size changed: ${path}`,
        );
      }
      const fingerprint = await sha256(bytes);
      if (reference.fingerprint && reference.fingerprint !== fingerprint) {
        throw new WorkspaceError(
          "ARCHIVE_REFERENCE_MISMATCH",
          `Referenced archive file fingerprint changed: ${path}`,
        );
      }
      totalBytes += bytes.byteLength;
      if (totalBytes > MAX_ARCHIVE_TOTAL_BYTES) {
        throw new WorkspaceError(
          "ARCHIVE_SIZE_LIMIT",
          "Archive content exceeds the 250 MB total limit.",
        );
      }
      files[path] = {
        encoding: "base64",
        data: toBase64(bytes),
        size: bytes.byteLength,
        fingerprint,
        kind: reference.kind || (
          path.startsWith("attachments/") ? "attachment" : "artifact"
        ),
      };
    }
    return buildArchive(this.manifest, stateBytes, files, revision);
  }

  details() {
    return {
      folder: this.name,
      permission: this.permission,
      mode: "Connected folder",
      workspaceId: this.manifest.workspace_id,
      schemaVersion: this.manifest.schema_version,
      protocolVersion: this.manifest.protocol_version,
      revision: this.manifest.revision,
      primaryState: this.manifest.primary_state,
      sizeGuidance: "250 MB recommended maximum; every save rewrites the complete database.",
      lastDurableWrite: this.lastSavedAt
        ? new Date(this.lastSavedAt).toLocaleString()
        : "No successful write this session",
    };
  }

  async #refreshManifestFingerprints() {
    const fingerprints = {};
    const files = [];
    const dynamicFiles = (this.manifest.application_files || [])
      .map((item) => item?.path)
      .filter(
        (path) =>
          typeof path === "string" &&
          (path.startsWith("attachments/") || path.startsWith("artifacts/")),
      );
    for (const path of new Set([...APPLICATION_FILES, ...dynamicFiles])) {
      if (path === MANIFEST_FILE) continue;
      if (dynamicFiles.includes(path)) validateArchiveContentPath(path);
      try {
        const bytes = await readBinary(this.handle, path);
        const fingerprint = await sha256(bytes);
        fingerprints[path] = fingerprint;
        files.push({ path, fingerprint, owner: "ai-kanban" });
      } catch (error) {
        if (error.name !== "NotFoundError") throw error;
      }
    }
    this.manifest.content_fingerprints = fingerprints;
    this.manifest.application_files = [
      { path: MANIFEST_FILE, owner: "ai-kanban" },
      ...files,
    ];
  }
}

export class PortableWorkspace {
  constructor({ manifest = createManifest(), stateBytes = null, files = {}, demo = false, name }) {
    this.manifest = manifest;
    this.stateBytes = stateBytes;
    this.files = files;
    this.demo = demo;
    this.name = name || (demo ? "Personal Research demo" : "Imported archive");
    this.mode = demo ? "memory-only" : "archive";
    this.permission = "not applicable";
    this.lastSavedAt = null;
  }

  static demo() {
    return new PortableWorkspace({ demo: true, name: "Personal Research · Demo" });
  }

  static fromArchiveFile(file) {
    if (!Number.isSafeInteger(file?.size) || file.size < 0) {
      return Promise.reject(
        new WorkspaceError("INVALID_ARCHIVE", "The selected archive has no trustworthy size."),
      );
    }
    if (file.size > MAX_ARCHIVE_ENCODED_BYTES) {
      return Promise.reject(
        new WorkspaceError(
          "IMPORT_SIZE_LIMIT",
          "The encoded archive exceeds the safe import limit.",
        ),
      );
    }
    return file.text().then(async (text) => {
      if (new TextEncoder().encode(text).byteLength > MAX_ARCHIVE_ENCODED_BYTES) {
        throw new WorkspaceError(
          "IMPORT_SIZE_LIMIT",
          "The encoded archive exceeds the safe import limit.",
        );
      }
      let parsed;
      try {
        parsed = JSON.parse(text);
      } catch {
        throw new WorkspaceError("INVALID_ARCHIVE", "The selected archive is not valid JSON.");
      }
      const validation = validateArchive(parsed);
      if (!validation.ok) {
        throw new WorkspaceError("INVALID_ARCHIVE", validation.errors.join(" "));
      }
      const stateBytes = fromBase64(parsed.board_base64);
      const stateFingerprint = parsed.manifest.content_fingerprints?.[
        parsed.manifest.primary_state
      ];
      if (
        stateFingerprint &&
        stateFingerprint !== await sha256(stateBytes)
      ) {
        throw new WorkspaceError(
          "INVALID_ARCHIVE",
          "The archived board fingerprint does not match board_base64.",
        );
      }
      for (const [path, entry] of Object.entries(parsed.files)) {
        if (typeof entry === "string") continue;
        const bytes = fromBase64(entry.data);
        if (await sha256(bytes) !== entry.fingerprint) {
          throw new WorkspaceError(
            "INVALID_ARCHIVE",
            `Archived file fingerprint mismatch: ${path}`,
          );
        }
      }
      return new PortableWorkspace({
        manifest: parsed.manifest,
        stateBytes,
        files: parsed.files,
        name: file.name,
      });
    });
  }

  async readState() {
    return this.stateBytes;
  }

  async saveState(bytes, { revision = null } = {}) {
    assertStateSize(bytes);
    this.stateBytes = new Uint8Array(bytes);
    if (Number.isSafeInteger(revision)) this.manifest.revision = revision;
    this.manifest.updated_at = new Date().toISOString();
    this.lastSavedAt = new Date().toISOString();
    await this.downloadArchive(bytes, revision);
  }

  exportArchive(stateBytes, _referencedFiles = [], revision = null) {
    assertStateSize(stateBytes);
    return buildArchive(this.manifest, stateBytes, this.files, revision);
  }

  async downloadArchive(stateBytes, revision = null) {
    assertStateSize(stateBytes);
    const archive = await buildArchive(
      this.manifest,
      stateBytes,
      this.files,
      revision,
    );
    downloadText(
      JSON.stringify(archive, null, 2),
      `${slug(this.name)}.ai-kanban.json`,
      "application/json",
    );
  }

  bootstrapStatus() {
    return Promise.resolve([]);
  }

  details() {
    return {
      workspace: this.name,
      mode: this.demo ? "Memory-only demo" : "Archive import/download",
      permission: "No connected folder",
      workspaceId: this.manifest.workspace_id,
      revision: this.manifest.revision,
      sizeGuidance: "250 MB recommended maximum; every download contains the complete database.",
      lastDurableWrite: this.lastSavedAt
        ? new Date(this.lastSavedAt).toLocaleString()
        : this.demo
          ? "Never — this demo is memory-only"
          : "Imported archive has not been downloaded this session",
    };
  }
}

export function createManifest(workspaceId = crypto.randomUUID()) {
  const timestamp = new Date().toISOString();
  return {
    format: WORKSPACE_FORMAT,
    format_version: WORKSPACE_FORMAT_VERSION,
    protocol_version: PROTOCOL_VERSION,
    schema_version: SCHEMA_VERSION,
    app_version: APP_VERSION,
    workspace_id: workspaceId,
    revision: 0,
    primary_state: STATE_FILE,
    reserved_directories: [...RESERVED_DIRECTORIES],
    application_files: APPLICATION_FILES.map((path) => ({ path, owner: "ai-kanban" })),
    agent_bootstrap_paths: [...BOOTSTRAP_FILES],
    content_fingerprints: {},
    created_at: timestamp,
    updated_at: timestamp,
  };
}

export async function recentHandle() {
  try {
    return await idbGet(RECENT_KEY);
  } catch (error) {
    if (error instanceof DOMException) return null;
    throw error;
  }
}

export async function reconnectRecent(handle) {
  await requirePermission(handle, true);
  return FolderWorkspace.fromHandle(handle);
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
  if (!workspaceId) return { acquired: false, release() {} };
  return acquireNamedLock(`ai-kanban:${workspaceId}`);
}

export async function acquireDirectoryCreationLock(handle) {
  const identity = await directoryIdentity(handle);
  return acquireNamedLock(`ai-kanban:create:${identity}`);
}

async function directoryIdentity(handle) {
  if (directoryIdentityCache.has(handle)) return directoryIdentityCache.get(handle);
  if (
    typeof indexedDB === "undefined" ||
    typeof handle?.isSameEntry !== "function"
  ) {
    const fallback = crypto.randomUUID();
    directoryIdentityCache.set(handle, fallback);
    return fallback;
  }
  const resolveIdentity = async () => {
    const identities = await idbGet(DIRECTORY_IDENTITIES_KEY).catch(() => []);
    for (const item of Array.isArray(identities) ? identities : []) {
      try {
        if (await handle.isSameEntry(item.handle)) {
          directoryIdentityCache.set(handle, item.id);
          return item.id;
        }
      } catch {
        // Ignore handles whose permission or structured clone is no longer valid.
      }
    }
    const id = crypto.randomUUID();
    await idbSet(DIRECTORY_IDENTITIES_KEY, [
      ...(Array.isArray(identities) ? identities : []),
      { id, handle },
    ]);
    directoryIdentityCache.set(handle, id);
    return id;
  };
  if (!navigator.locks) return resolveIdentity();
  return navigator.locks.request(
    "ai-kanban:directory-identity-registry",
    { mode: "exclusive" },
    resolveIdentity,
  );
}

async function acquireNamedLock(name) {
  if (!navigator.locks) {
    const fallback = {
      acquired: true,
      release() {
        fallback.acquired = false;
      },
    };
    return fallback;
  }
  let releaseLock;
  let announce;
  const acquired = new Promise((resolve) => {
    announce = resolve;
  });
  navigator.locks.request(
    name,
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
  const result = {
    acquired: await acquired,
    release() {
      releaseLock?.();
      result.acquired = false;
    },
  };
  return result;
}

export function downloadArchive(archive, name = "ai-kanban-workspace") {
  downloadText(
    JSON.stringify(archive, null, 2),
    `${slug(name)}.ai-kanban.json`,
    "application/json",
  );
}

async function buildArchive(manifest, stateBytes, files, revision = null) {
  assertStateSize(stateBytes);
  const archiveManifest = structuredClone(manifest);
  const fingerprint = await sha256(stateBytes);
  if (Number.isSafeInteger(revision)) archiveManifest.revision = revision;
  archiveManifest.updated_at = new Date().toISOString();
  archiveManifest.content_fingerprints ||= {};
  archiveManifest.content_fingerprints[archiveManifest.primary_state] = fingerprint;
  const stateFile = (archiveManifest.application_files || []).find(
    (item) => item.path === archiveManifest.primary_state,
  );
  if (stateFile) stateFile.fingerprint = fingerprint;
  return {
    format: ARCHIVE_FORMAT,
    exported_at: new Date().toISOString(),
    manifest: archiveManifest,
    board_base64: toBase64(stateBytes),
    files: { ...files },
  };
}

function assertStateSize(bytes) {
  if (!(bytes instanceof Uint8Array)) {
    throw new TypeError("SQLite state must be Uint8Array bytes.");
  }
  if (bytes.byteLength > MAX_WORKSPACE_BYTES) {
    throw new WorkspaceError(
      "WORKSPACE_TOO_LARGE",
      "The 250 MB whole-file limit applies before every save or archive write.",
    );
  }
}

function validateArchiveContentPath(path, kind = null) {
  const parts = assertRelativePath(path, "archive content path");
  const expectedRoot = kind === "attachment"
    ? "attachments"
    : kind === "artifact"
      ? "artifacts"
      : null;
  if (
    !["attachments", "artifacts"].includes(parts[0]) ||
    (expectedRoot && parts[0] !== expectedRoot)
  ) {
    throw new ValidationError(
      "Archive content must stay under attachments/ or artifacts/.",
    );
  }
}

async function readManifest(handle) {
  let parsed;
  try {
    parsed = JSON.parse(await readText(handle, MANIFEST_FILE));
  } catch (error) {
    if (error.name === "NotFoundError") {
      throw new WorkspaceError("MISSING_MANIFEST", "This folder has no manifest.json.");
    }
    throw new WorkspaceError("INVALID_MANIFEST", "manifest.json is unreadable or invalid JSON.");
  }
  const validation = validateManifest(parsed);
  if (!validation.ok) {
    throw new WorkspaceError("INVALID_MANIFEST", validation.errors.join(" "));
  }
  if (Number(parsed.schema_version) > SCHEMA_VERSION) {
    throw new WorkspaceError("FUTURE_SCHEMA", "This workspace was created by a newer AI Kanban version.");
  }
  return parsed;
}

async function writeManifest(handle, manifest) {
  await writeText(handle, MANIFEST_FILE, `${JSON.stringify(manifest, null, 2)}\n`);
}

async function requirePermission(handle, request) {
  const options = { mode: "readwrite" };
  let state = await handle.queryPermission?.(options);
  if (state === "granted") return true;
  if (!request) return false;
  state = await handle.requestPermission?.(options);
  if (state !== "granted") {
    throw new WorkspaceError("PERMISSION_DENIED", "Read/write folder permission was not granted.");
  }
  return true;
}

async function ensureDirectories(root, paths) {
  for (const path of paths) await directoryAt(root, assertRelativePath(path), true);
}

async function directoryAt(root, parts, create) {
  let current = root;
  for (const segment of parts) current = await current.getDirectoryHandle(segment, { create });
  return current;
}

async function fileAt(root, path, create) {
  const parts = assertRelativePath(path);
  const name = parts.pop();
  const directory = await directoryAt(root, parts, create);
  const handle = await directory.getFileHandle(name, { create });
  const resolved = await root.resolve(handle);
  if (!resolved || resolved.join("/") !== [...parts, name].join("/")) {
    throw new WorkspaceError("PATH_ESCAPE", "A workspace path resolved outside the selected folder.");
  }
  return handle;
}

async function readBinary(root, path) {
  const handle = await fileAt(root, path, false);
  const file = await handle.getFile();
  if (file.size > MAX_WORKSPACE_BYTES) {
    throw new WorkspaceError(
      "WORKSPACE_TOO_LARGE",
      `${path} exceeds the 250 MB whole-file safety limit.`,
    );
  }
  return new Uint8Array(await file.arrayBuffer());
}

async function readText(root, path) {
  const handle = await fileAt(root, path, false);
  return (await handle.getFile()).text();
}

async function writeBinary(root, path, bytes) {
  const handle = await fileAt(root, path, true);
  const writable = await handle.createWritable({ keepExistingData: false });
  try {
    await writable.write(bytes);
    await writable.close();
  } catch (error) {
    await writable.abort?.();
    throw error;
  }
}

function writeText(root, path, content) {
  return writeBinary(root, path, new TextEncoder().encode(content));
}

async function captureFileSnapshots(root, paths) {
  const snapshots = new Map();
  for (const path of paths) {
    try {
      snapshots.set(path, {
        existed: true,
        bytes: await readBinary(root, path),
      });
    } catch (error) {
      if (error.name !== "NotFoundError") throw error;
      snapshots.set(path, { existed: false, bytes: null });
    }
  }
  return snapshots;
}

async function restoreFileSnapshots(root, snapshots) {
  const errors = [];
  for (const [path, snapshot] of [...snapshots].reverse()) {
    try {
      if (snapshot.existed) await writeBinary(root, path, snapshot.bytes);
      else await removeFile(root, path);
    } catch (error) {
      errors.push({ path, message: error.message });
    }
  }
  return errors;
}

async function assertFileSnapshotCurrent(root, path, snapshot) {
  let current = null;
  try {
    current = await readBinary(root, path);
  } catch (error) {
    if (error.name !== "NotFoundError") throw error;
  }
  const unchanged = snapshot?.existed
    ? current !== null && equalBytes(current, snapshot.bytes)
    : current === null;
  if (!unchanged) {
    throw new WorkspaceError(
      "INITIALIZATION_CONFLICT",
      `Workspace target changed immediately before initialization write: ${path}`,
    );
  }
}

async function writeBinaryCas(root, path, bytes, snapshot, beforeWrite) {
  await assertFileSnapshotCurrent(root, path, snapshot);
  beforeWrite();
  await writeBinary(root, path, bytes);
}

function equalBytes(left, right) {
  if (left.byteLength !== right.byteLength) return false;
  return left.every((byte, index) => byte === right[index]);
}

async function removeFile(root, path) {
  const parts = assertRelativePath(path);
  const name = parts.pop();
  let directory;
  try {
    directory = await directoryAt(root, parts, false);
  } catch (error) {
    if (error.name === "NotFoundError") return;
    throw error;
  }
  try {
    await directory.removeEntry(name);
  } catch (error) {
    if (error.name !== "NotFoundError") throw error;
  }
}

async function entryExists(root, path) {
  try {
    await fileAt(root, path, false);
    return true;
  } catch (error) {
    if (error.name === "NotFoundError") return false;
    throw error;
  }
}

async function sha256(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function manifestFingerprint(manifest) {
  return sha256(
    new TextEncoder().encode(JSON.stringify(manifest)),
  );
}

function toBase64(bytes) {
  let result = "";
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    result += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
  }
  return btoa(result);
}

function fromBase64(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return bytes;
}

function downloadText(text, name, type) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([text], { type }));
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 0);
}

function slug(value) {
  return String(value || "ai-kanban-workspace")
    .toLowerCase()
    .replace(/\.(ai-kanban\.json|json)$/i, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || "ai-kanban-workspace";
}

async function rememberHandle(handle) {
  if (typeof indexedDB === "undefined") return;
  try {
    await idbSet(RECENT_KEY, handle);
  } catch (error) {
    if (!(error instanceof DOMException)) throw error;
  }
}

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(RECENT_DATABASE, 1);
    request.addEventListener("upgradeneeded", () => request.result.createObjectStore(RECENT_STORE));
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
