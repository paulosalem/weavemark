const assert = require("node:assert/strict");
const test = require("node:test");
const { loadWithVscodeMock } = require("./helpers");

const vscodeMock = {
  workspace: {
    isTrusted: true,
    getConfiguration() {
      return { get(_name, fallback) { return fallback; } };
    },
  },
  window: {},
  ThemeIcon: class ThemeIcon {},
};

test("webview HTML has a nonce CSP and escapes all metadata", () => {
  const { buildFormHtml } = loadWithVscodeMock("src/form.js", vscodeMock);
  const attack = `"><script id="attack">alert(1)</script>`;
  const html = buildFormHtml(
    { cspSource: "vscode-webview:" },
    {
      title: attack,
      description: attack,
      inputs: [
        {
          name: "topic",
          input_type: "file",
          options: [],
          default: attack,
          description: attack,
          file_hint: attack,
          source_directive: attack,
        },
      ],
      execution: { type: attack },
      tool_names: [attack],
      prompt_names: [attack],
    },
    `/tmp/${attack}.weavemark.md`
  );

  assert.match(html, /default-src 'none'/);
  assert.match(html, /script-src 'nonce-[^']+'/);
  assert.doesNotMatch(html, /unsafe-inline|onclick=/);
  assert.doesNotMatch(html, /<script id="attack">/);
  assert.match(html, /&lt;script id=&quot;attack&quot;&gt;/);
});

test("webview messages accept only declared string-valued inputs", () => {
  const { validateFormValues } = loadWithVscodeMock("src/form.js", vscodeMock);
  const inputs = [{ name: "topic" }, { name: "enabled" }];

  assert.deepEqual(
    { ...validateFormValues({ topic: "$(touch nope)", enabled: "true" }, inputs) },
    { topic: "$(touch nope)", enabled: "true" }
  );
  assert.equal(validateFormValues({ unexpected: "value" }, inputs), null);
  assert.equal(validateFormValues({ topic: { nested: true } }, inputs), null);
});
