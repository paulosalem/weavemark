const assert = require("node:assert/strict");
const test = require("node:test");
const { analyzeSource, isKnownDirective } = require("../src/language");

test("source analysis ignores fences, escapes, and opaque bodies", () => {
  const source = [
    "```weavemark",
    "@fake",
    "```",
    "@@literal",
    "@note",
    "  @also_fake",
    "@define local_rule",
    "@use company.rules exposing imported_rule as rules",
    "@rules.qualified",
    "## @define heading_rule",
    "> [!PROMPLET heading_rule]",
  ].join("\n");
  const analysis = analyzeSource(source);
  const catalog = new Set(["note", "define", "use"]);

  assert.equal(analysis.ignoredLines.has(1), true);
  assert.equal(analysis.ignoredLines.has(3), true);
  assert.equal(analysis.ignoredLines.has(5), true);
  assert.equal(isKnownDirective("local_rule", catalog, analysis), true);
  assert.equal(isKnownDirective("imported_rule", catalog, analysis), true);
  assert.equal(isKnownDirective("rules.qualified", catalog, analysis), true);
  assert.equal(isKnownDirective("heading_rule", catalog, analysis), true);
  assert.equal(isKnownDirective("unknown", catalog, analysis), false);
});
