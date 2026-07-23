import { APP_VERSION, DB_VERSION, STORE_NAMES } from "../config.js";
import { nowIso } from "./time.js";

export const EXPORT_SCHEMA_VERSION = "knowledge-cards.export.v1";

const EXPORT_STORES = [
  STORE_NAMES.progress,
  STORE_NAMES.sessionOrders,
  STORE_NAMES.cardStates,
  STORE_NAMES.notes,
  STORE_NAMES.noteDrafts,
  STORE_NAMES.savedCards,
  STORE_NAMES.revisitQueue,
  STORE_NAMES.history,
  STORE_NAMES.preferences
];

export async function createExport(repo) {
  const stores = {};
  for (const store of EXPORT_STORES) stores[store] = await repo.getAll(store);
  return {
    schema_version: EXPORT_SCHEMA_VERSION,
    app: "knowledge-cards",
    app_version: APP_VERSION,
    database_version: DB_VERSION,
    exported_at: nowIso(),
    stores
  };
}

export function validateExportPayload(payload) {
  const errors = [];
  if (!payload || typeof payload !== "object") return ["Import must be a JSON object."];
  if (payload.schema_version !== EXPORT_SCHEMA_VERSION) errors.push("Unsupported export schema version.");
  if (payload.app !== "knowledge-cards") errors.push("Import file is not for Knowledge Cards.");
  if (!payload.stores || typeof payload.stores !== "object") errors.push("Import file must include stores.");
  for (const store of EXPORT_STORES) {
    if (!Array.isArray(payload.stores?.[store])) errors.push(`Import store ${store} must be an array.`);
  }
  return errors;
}

export async function previewImport(repo, payload) {
  const errors = validateExportPayload(payload);
  if (errors.length > 0) return { valid: false, errors, counts: {}, conflicts: [] };
  const conflicts = [];
  const counts = {};
  for (const store of EXPORT_STORES) {
    counts[store] = payload.stores[store].length;
    const current = new Map((await repo.getAll(store)).map((item) => [item.id ?? item.packId, item]));
    for (const item of payload.stores[store]) {
      const key = item.id ?? item.packId;
      if (current.has(key)) conflicts.push({ store, key });
    }
  }
  return { valid: true, errors: [], counts, conflicts };
}

export async function applyImport(repo, payload, { mode = "merge" } = {}) {
  const preview = await previewImport(repo, payload);
  if (!preview.valid) throw new Error(preview.errors.join("\n"));
  const transactionId = `import-${Date.now()}`;
  const rollback = {};
  for (const store of EXPORT_STORES) rollback[store] = await repo.getAll(store);
  await repo.put(STORE_NAMES.importExports, {
    id: transactionId,
    created_at: nowIso(),
    status: "previewed",
    mode,
    rollback
  });
  try {
    if (mode === "replace") {
      for (const store of EXPORT_STORES) await repo.clear(store);
    }
    for (const store of EXPORT_STORES) {
      for (const item of payload.stores[store]) await repo.put(store, item);
    }
    await repo.put(STORE_NAMES.importExports, {
      id: transactionId,
      created_at: nowIso(),
      updated_at: nowIso(),
      status: "committed",
      mode,
      rollback
    });
    return { transactionId, preview };
  } catch (error) {
    for (const store of EXPORT_STORES) {
      await repo.clear(store);
      for (const item of rollback[store]) await repo.put(store, item);
    }
    await repo.put(STORE_NAMES.importExports, {
      id: transactionId,
      created_at: nowIso(),
      updated_at: nowIso(),
      status: "rolled-back",
      mode,
      message: error.message,
      rollback
    });
    throw error;
  }
}
