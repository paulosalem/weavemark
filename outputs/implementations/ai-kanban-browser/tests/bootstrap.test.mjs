import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("agent skill requires post-grant preflight values for register and watch", async () => {
  const skill = await readFile(
    new URL("../templates/skill/SKILL.md", import.meta.url),
    "utf8",
  );
  const grant = skill.indexOf("grant that actor the writer baton");
  const postGrant = skill.indexOf("After the grant is durable, run `preflight` and `status` again");
  const register = skill.indexOf("Register with");
  const watch = skill.indexOf("post-grant preflight control generation");
  assert.ok(grant >= 0);
  assert.ok(postGrant > grant);
  assert.ok(register > postGrant);
  assert.ok(watch > register);
  assert.match(skill, /never reuse pre-grant\s+values/);
});
