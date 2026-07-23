import assert from "node:assert/strict";
import test from "node:test";
import { runSmoke } from "../tools/smoke.mjs";

test("static server smoke loads app assets and pack index", async () => {
  const result = await runSmoke();
  assert.equal(result.packCount, 4);
});
