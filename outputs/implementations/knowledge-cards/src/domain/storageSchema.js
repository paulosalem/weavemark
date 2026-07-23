import { DB_NAME, DB_VERSION, STORE_NAMES } from "../config.js";

export const STORAGE_SCHEMA = Object.freeze({
  dbName: DB_NAME,
  version: DB_VERSION,
  stores: {
    [STORE_NAMES.packCache]: {
      keyPath: "cacheKey",
      indexes: [["byPack", "packId", { unique: false }]]
    },
    [STORE_NAMES.progress]: {
      keyPath: "packId",
      indexes: [["byUpdated", "updated_at", { unique: false }]]
    },
    [STORE_NAMES.sessionOrders]: {
      keyPath: "id",
      indexes: [["byPack", "packId", { unique: false }]]
    },
    [STORE_NAMES.cardStates]: {
      keyPath: "id",
      indexes: [["byPack", "packId", { unique: false }]]
    },
    [STORE_NAMES.notes]: {
      keyPath: "id",
      indexes: [["byPack", "packId", { unique: false }]]
    },
    [STORE_NAMES.noteDrafts]: {
      keyPath: "id",
      indexes: [["byPack", "packId", { unique: false }]]
    },
    [STORE_NAMES.savedCards]: {
      keyPath: "id",
      indexes: [["byPack", "packId", { unique: false }]]
    },
    [STORE_NAMES.revisitQueue]: {
      keyPath: "id",
      indexes: [["byPack", "packId", { unique: false }]]
    },
    [STORE_NAMES.history]: {
      keyPath: "id",
      indexes: [["byPack", "packId", { unique: false }], ["byTime", "created_at", { unique: false }]]
    },
    [STORE_NAMES.preferences]: {
      keyPath: "id",
      indexes: []
    },
    [STORE_NAMES.importExports]: {
      keyPath: "id",
      indexes: [["byTime", "created_at", { unique: false }]]
    }
  }
});

export function entityId(packId, cardId) {
  return `${packId}::${cardId}`;
}

export function sessionOrderId(packId, sessionId) {
  return `${packId}::${sessionId}`;
}
