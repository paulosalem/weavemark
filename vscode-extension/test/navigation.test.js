const assert = require("node:assert/strict");
const test = require("node:test");
const { loadWithVscodeMock } = require("./helpers");

const vscodeMock = {
  CompletionItemKind: {},
  workspace: {
    getWorkspaceFolder: () => undefined,
  },
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
    /^\s*@reference\s+("[^"]+"|'[^']+'|\S+)/,
    /@reference\(\s*("[^"]+"|'[^']+'|[A-Za-z0-9_./~+-]+)/,
    /(?<![A-Za-z0-9_@])@((?:(?:\.{0,2}\/|~\/|\/)[A-Za-z0-9_./~+-]*[A-Za-z0-9_+-])|(?:README|AGENTS|CLAUDE)(?:\.md)?|[A-Za-z0-9_+-]+(?:\.[A-Za-z0-9_+-]+)+)(?=$|[\s.,;:!?])/,
    /^\s*@refine\s+("[^"]+"|'[^']+'|\S+)/,
    /^\s*@package\b.*\b(?:instructions|from):\s*("[^"]+"|'[^']+'|\S+)/,
  ];

  const moduleReference = findReference(
    "@refine module:company.rules",
    patterns
  );
  const packageReference = findReference(
    '@package instructions: "book instructions/main.weavemark.md" file: out.html',
    patterns
  );
  const inlineReference = findReference(
    'See @reference("docs/guide.md" keep:true) for details.',
    patterns
  );
  const shorthandReference = findReference(
    "See @README for details.",
    patterns
  );

  assert.equal(moduleReference.value, "module:company.rules");
  assert.equal(
    unquote(packageReference.value),
    "book instructions/main.weavemark.md"
  );
  assert.equal(unquote(inlineReference.value), "docs/guide.md");
  assert.equal(shorthandReference.value, "README");

  const laterReference = findReference(
    "Compare @first.md with @second.md.",
    patterns,
    28
  );
  assert.equal(laterReference.value, "second.md");
});
