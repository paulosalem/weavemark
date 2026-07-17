const assert = require("node:assert/strict");
const test = require("node:test");
const { loadWithVscodeMock } = require("./helpers");

const vscodeMock = {
  CompletionItemKind: {},
  workspace: {},
};

test("path completions quote whitespace without shell escaping", () => {
  const { quotePath } = loadWithVscodeMock("src/completions.js", vscodeMock);

  assert.equal(quotePath("plain/file.md"), "plain/file.md");
  assert.equal(
    quotePath('folder with space/file"name.md'),
    '"folder with space/file\\"name.md"'
  );
});

test("definition references support module and quoted path forms", () => {
  const { findReference, unquote } = loadWithVscodeMock(
    "src/definitions.js",
    vscodeMock
  );
  const patterns = [
    /^\s*@refine\s+("[^"]+"|'[^']+'|\S+)/,
    /^\s*@package\b.*\b(?:template|from):\s*("[^"]+"|'[^']+'|\S+)/,
  ];

  const moduleReference = findReference(
    "@refine module:company.rules",
    patterns
  );
  const packageReference = findReference(
    '@package template: "book templates/main.weavemark.md" file: out.html',
    patterns
  );

  assert.equal(moduleReference.value, "module:company.rules");
  assert.equal(
    unquote(packageReference.value),
    "book templates/main.weavemark.md"
  );
});
