import assert from "node:assert/strict";
import test from "node:test";
import { STORE_NAMES } from "../src/config.js";
import { createExport, applyImport, previewImport, validateExportPayload } from "../src/domain/importExport.js";
import { MemoryRepository } from "../src/domain/repositories.js";

test("export/import validates schema and previews conflicts", async () => {
  const repo = new MemoryRepository();
  await repo.put(STORE_NAMES.notes, { id: "pack::card", packId: "pack", cardId: "card", body: "A note" });
  const payload = await createExport(repo);
  assert.deepEqual(validateExportPayload(payload), []);
  const preview = await previewImport(repo, payload);
  assert.equal(preview.valid, true);
  assert.equal(preview.conflicts.length > 0, true);
});

test("merge import applies compatible records", async () => {
  const source = new MemoryRepository();
  await source.put(STORE_NAMES.savedCards, { id: "pack::one", packId: "pack", cardId: "one", cardTitle: "One" });
  const payload = await createExport(source);
  const target = new MemoryRepository();
  await applyImport(target, payload, { mode: "merge" });
  const saved = await target.getAll(STORE_NAMES.savedCards);
  assert.equal(saved.length, 1);
  assert.equal(saved[0].cardId, "one");
});

test("invalid imports are rejected", () => {
  assert.notDeepEqual(validateExportPayload({ schema_version: "wrong" }), []);
});
