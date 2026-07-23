import { DEFAULT_PREFERENCES, HISTORY_LIMIT, STORE_NAMES } from "../config.js";
import { entityId, STORAGE_SCHEMA } from "./storageSchema.js";
import { nowIso } from "./time.js";

export async function createRepository() {
  if (!("indexedDB" in globalThis)) return new MemoryRepository("IndexedDB is unavailable; using temporary memory state.");
  return LocalRepository.open();
}

export class LocalRepository {
  constructor(db) {
    this.db = db;
    this.warning = null;
  }

  static open() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(STORAGE_SCHEMA.dbName, STORAGE_SCHEMA.version);
      request.onupgradeneeded = () => migrate(request.result);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(new LocalRepository(request.result));
    });
  }

  get(store, key) {
    return requestPromise(this.db.transaction(store, "readonly").objectStore(store).get(key));
  }

  getAll(store) {
    return requestPromise(this.db.transaction(store, "readonly").objectStore(store).getAll());
  }

  put(store, value) {
    const tx = this.db.transaction(store, "readwrite");
    tx.objectStore(store).put(value);
    return txDone(tx);
  }

  delete(store, key) {
    const tx = this.db.transaction(store, "readwrite");
    tx.objectStore(store).delete(key);
    return txDone(tx);
  }

  clear(store) {
    const tx = this.db.transaction(store, "readwrite");
    tx.objectStore(store).clear();
    return txDone(tx);
  }

  async getPreferences() {
    return (await this.get(STORE_NAMES.preferences, "default")) ?? { ...DEFAULT_PREFERENCES };
  }

  savePreferences(prefs) {
    return this.put(STORE_NAMES.preferences, { ...DEFAULT_PREFERENCES, ...prefs, id: "default", updated_at: nowIso() });
  }

  async addHistory(event) {
    const item = { id: `${Date.now()}-${crypto.randomUUID()}`, created_at: nowIso(), ...event };
    await this.put(STORE_NAMES.history, item);
    const all = await this.getAll(STORE_NAMES.history);
    if (all.length > HISTORY_LIMIT) {
      all.sort((a, b) => String(a.created_at).localeCompare(String(b.created_at)));
      for (const extra of all.slice(0, all.length - HISTORY_LIMIT)) await this.delete(STORE_NAMES.history, extra.id);
    }
    return item;
  }

  getCardState(packId, cardId) {
    return this.get(STORE_NAMES.cardStates, entityId(packId, cardId));
  }

  saveCardState(packId, cardId, patch) {
    return this.put(STORE_NAMES.cardStates, {
      id: entityId(packId, cardId),
      packId,
      cardId,
      updated_at: nowIso(),
      ...patch
    });
  }
}

export class MemoryRepository {
  constructor(warning = null) {
    this.warning = warning;
    this.stores = new Map(Object.values(STORE_NAMES).map((name) => [name, new Map()]));
    this.stores.get(STORE_NAMES.preferences).set("default", { ...DEFAULT_PREFERENCES });
  }

  async get(store, key) {
    return clone(this.stores.get(store)?.get(Array.isArray(key) ? key.join("::") : key));
  }

  async getAll(store) {
    return [...(this.stores.get(store)?.values() ?? [])].map(clone);
  }

  async put(store, value) {
    const key = value.id ?? value.packId;
    this.stores.get(store).set(key, clone(value));
  }

  async delete(store, key) {
    this.stores.get(store).delete(Array.isArray(key) ? key.join("::") : key);
  }

  async clear(store) {
    this.stores.get(store).clear();
  }

  async getPreferences() {
    return (await this.get(STORE_NAMES.preferences, "default")) ?? { ...DEFAULT_PREFERENCES };
  }

  savePreferences(prefs) {
    return this.put(STORE_NAMES.preferences, { ...DEFAULT_PREFERENCES, ...prefs, id: "default", updated_at: nowIso() });
  }

  async addHistory(event) {
    const item = { id: `${Date.now()}-${Math.random().toString(16).slice(2)}`, created_at: nowIso(), ...event };
    await this.put(STORE_NAMES.history, item);
    return item;
  }

  getCardState(packId, cardId) {
    return this.get(STORE_NAMES.cardStates, entityId(packId, cardId));
  }

  saveCardState(packId, cardId, patch) {
    return this.put(STORE_NAMES.cardStates, {
      id: entityId(packId, cardId),
      packId,
      cardId,
      updated_at: nowIso(),
      ...patch
    });
  }
}

function migrate(db) {
  for (const [name, definition] of Object.entries(STORAGE_SCHEMA.stores)) {
    if (!db.objectStoreNames.contains(name)) {
      const store = db.createObjectStore(name, { keyPath: definition.keyPath });
      for (const [indexName, keyPath, options] of definition.indexes) store.createIndex(indexName, keyPath, options);
    }
  }
}

function requestPromise(request) {
  return new Promise((resolve, reject) => {
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function txDone(tx) {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onabort = () => reject(tx.error);
    tx.onerror = () => reject(tx.error);
  });
}

function clone(value) {
  return value == null ? value : structuredClone(value);
}
