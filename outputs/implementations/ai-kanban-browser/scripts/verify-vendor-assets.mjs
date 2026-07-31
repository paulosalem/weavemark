import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

const expected = new Map([
  ["../vendor/sql-wasm.js", "77d6435bac506af0e3c59636dce9d22b1b14156348bc327f41a1577f3212360f"],
  ["../vendor/sql-wasm.wasm", "438c88f666dc054ce4e9395f80fe9db4218b1a3c379960454880f048a7898aed"],
  ["../vendor/LICENSE-sql.js", "7fb62155f36ad064cc97fbc2cc4ea41f600121f5a95873232b8e151be39427a6"],
]);

for (const [relative, fingerprint] of expected) {
  const url = new URL(relative, import.meta.url);
  const digest = createHash("sha256").update(await readFile(url)).digest("hex");
  if (digest !== fingerprint) {
    throw new Error(`${relative} fingerprint mismatch: ${digest}`);
  }
}

console.log(`Verified ${expected.size} pinned sql.js 1.14.1 assets.`);
