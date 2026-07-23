#!/usr/bin/env node
import assert from "node:assert/strict";
import { once } from "node:events";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { validateAllPacks } from "./validate-packs.mjs";
import { createStaticServer } from "./serve.mjs";

export async function runSmoke() {
  const validation = await validateAllPacks({ writeIndex: false });
  assert.equal(validation.ok, true, validation.errors.join("\n"));
  const server = createStaticServer();
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const { port } = server.address();
  const base = `http://127.0.0.1:${port}`;
  try {
    for (const path of ["/", "/index.html", "/styles/site.css", "/src/main.js", "/content/packs/index.json"]) {
      const response = await fetch(`${base}${path}`);
      assert.equal(response.ok, true, `${path} should load`);
      assert.match(response.headers.get("content-type") ?? "", /text|json|javascript/);
    }
    const index = await (await fetch(`${base}/content/packs/index.json`)).json();
    assert.equal(index.packs.length, 4);
    assert.equal(index.packs.reduce((sum, pack) => sum + pack.card_count, 0), 200);
    return { base, packCount: index.packs.length };
  } finally {
    server.close();
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = await runSmoke();
  console.log(`Static smoke passed for ${result.packCount} packs.`);
}
