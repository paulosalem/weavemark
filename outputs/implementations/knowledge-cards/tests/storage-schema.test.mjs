import assert from "node:assert/strict";
import test from "node:test";
import { STORE_NAMES } from "../src/config.js";
import { STORAGE_SCHEMA } from "../src/domain/storageSchema.js";

test("IndexedDB schema declares required stores", () => {
  for (const name of Object.values(STORE_NAMES)) {
    assert.ok(STORAGE_SCHEMA.stores[name], `missing store ${name}`);
    assert.ok(STORAGE_SCHEMA.stores[name].keyPath);
  }
});
