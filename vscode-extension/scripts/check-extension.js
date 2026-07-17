const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const { DIRECTIVES, DEBUG_DIRECTIVES } = require("../src/directives");

const root = path.resolve(__dirname, "..");
const sourceDirectory = path.join(root, "src");
const grammarPath = path.join(root, "syntaxes", "weavemark.tmLanguage.json");
const packagePath = path.join(root, "package.json");
const languageSchemaPath = path.resolve(root, "..", "docs", "weavemark.ebnf");

for (const file of fs.readdirSync(sourceDirectory).filter((name) => name.endsWith(".js"))) {
  execFileSync(process.execPath, ["--check", path.join(sourceDirectory, file)], {
    stdio: "inherit",
  });
}

JSON.parse(fs.readFileSync(grammarPath, "utf8"));
const manifest = JSON.parse(fs.readFileSync(packagePath, "utf8"));
const grammar = fs.readFileSync(grammarPath, "utf8");
const languageSchema = fs.readFileSync(languageSchemaPath, "utf8");
const schemaDirectives = new Set(
  [...languageSchema.matchAll(/directive:\s+@([A-Za-z_][\w.-]*\??)/g)].map(
    (match) => match[1]
  )
);
const catalogDirectives = new Set(Object.keys(DIRECTIVES));
const moduleDirectives = new Set([
  "refine",
  "ask",
  "iterate",
  "example",
  "inspect",
  "concise",
]);
const expectedDirectives = new Set([...schemaDirectives, ...moduleDirectives]);
const missingFromCatalog = [...expectedDirectives].filter(
  (name) => !catalogDirectives.has(name)
);
const unsupportedCatalogEntries = [...catalogDirectives].filter(
  (name) => !expectedDirectives.has(name)
);
if (missingFromCatalog.length || unsupportedCatalogEntries.length) {
  throw new Error(
    `Language catalog drift. Missing: ${missingFromCatalog.join(", ") || "none"}; ` +
      `unsupported: ${unsupportedCatalogEntries.join(", ") || "none"}`
  );
}
const missing = Object.keys(DIRECTIVES).filter(
  (name) => !new RegExp(`(?:^|[^A-Za-z0-9_-])${name}(?:$|[^A-Za-z0-9_-])`).test(grammar)
);
if (missing.length > 0) {
  throw new Error(`Grammar is missing directive(s): ${missing.join(", ")}`);
}
for (const name of Object.keys(DEBUG_DIRECTIVES)) {
  if (!grammar.includes(name.replace("?", ""))) {
    throw new Error(`Grammar is missing debug directive: ${name}`);
  }
}
if (manifest.capabilities?.untrustedWorkspaces?.supported !== "limited") {
  throw new Error(
    "Extension must expose only static language features in untrusted workspaces."
  );
}
if (manifest.contributes.configuration.properties["weavemark.cliPath"].scope !== "machine") {
  throw new Error("CLI path must remain machine-scoped.");
}
if (manifest.contributes.configuration.properties["weavemark.extraArgs"].type !== "array") {
  throw new Error("Extra arguments must remain an argument array.");
}

const allSource = fs
  .readdirSync(sourceDirectory)
  .filter((name) => name.endsWith(".js"))
  .map((name) => fs.readFileSync(path.join(sourceDirectory, name), "utf8"))
  .join("\n");
for (const forbidden of [
  "child_process\").exec",
  "child_process').exec",
  ".sendText(",
  "output_format",
  "@image",
  "format: ${1|markdown,json,xml",
]) {
  if (allSource.includes(forbidden)) {
    throw new Error(`Forbidden extension pattern remains: ${forbidden}`);
  }
}

console.log(
  `Extension checks passed: ${Object.keys(DIRECTIVES).length} current directives, ` +
    `${Object.keys(DEBUG_DIRECTIVES).length} debug directives.`
);
