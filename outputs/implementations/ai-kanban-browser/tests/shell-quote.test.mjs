import test from "node:test";
import assert from "node:assert/strict";
import { shellQuote } from "../src/shell-quote.js";

test("recovery command arguments are POSIX shell quoted", () => {
  assert.equal(shellQuote("agent-1"), "'agent-1'");
  assert.equal(
    shellQuote("run'; touch owned; '"),
    "'run'\"'\"'; touch owned; '\"'\"''",
  );
});
