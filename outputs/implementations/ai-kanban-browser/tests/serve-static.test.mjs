import test from "node:test";
import assert from "node:assert/strict";
import { posix, win32 } from "node:path";
import {
  decodeRequestPath,
  resolveContainedPath,
} from "../scripts/serve-static-paths.mjs";

test("malformed request encoding is rejected without reaching path resolution", () => {
  assert.throws(() => decodeRequestPath("/%GG"), URIError);
  assert.equal(decodeRequestPath("/assets/app.js"), "/assets/app.js");
});

test("static path containment uses platform-native relative semantics", () => {
  assert.equal(
    resolveContainedPath("/site", "/assets/app.js", posix),
    "/site/assets/app.js",
  );
  assert.throws(
    () => resolveContainedPath("/site", "/../secret", posix),
    /escapes/,
  );
  assert.equal(
    resolveContainedPath("C:\\site", "\\assets\\app.js", win32),
    "C:\\site\\assets\\app.js",
  );
  assert.throws(
    () => resolveContainedPath("C:\\site", "\\..\\secret", win32),
    /escapes/,
  );
  assert.throws(
    () => resolveContainedPath("C:\\site", "C:\\other\\secret", win32),
    /escapes/,
  );
});
