// WeaveMark — Hover provider
//
// Shows documentation when hovering over:
//   • @directive names
//   • @{variable} references
//   • ==> match arrows
//   • @execute strategy names

const vscode = require("vscode");
const { DIRECTIVES, DEBUG_DIRECTIVES, EXECUTION_STRATEGIES } = require("./directives");
const { analyzeSource } = require("./language");

const PARAMETER_DOCS = {
  version: "WeaveMark language version. Current authored promplets should normally use `0.9`.",
  surface: "Optional surface adapter. `canonical` keeps raw directives; `markdown` enables directive headings and `[!PROMPLET ...]` callouts.",
  exposing: "Import selected definitions directly from a module. This is an import clause, not a `key:` parameter.",
  as: "Bind an imported module under an alias, or bind a semantic/execution result when used as `as:` on a definition invocation.",
  format: "Configured format identifier. On `@compile` this controls primary output; on role-tagged `@prompt` it records the prompt/template format.",
  context: "`auto`, `cascade`, or `local`; controls whether shared root context is prepended into named prompt blocks.",
  role: "Chat role for a role-tagged `@prompt`: `system`, `user`, `assistant`, or `tool`.",
  file: "Relative file path. Paths must stay inside the allowed project boundary.",
  type: "Output modality for `@output`: `text` or `image`.",
  quality: "Image-generation quality for an image `@output` contract.",
  edit: "Whether an image output edits the previous/reference image.",
  instructions: "Reusable promplet instructions semantically applied by `@package`.",
  detail_level: "Compile-time `@ask` depth as a percentage greater than `0%` and no greater than `100%`. Higher values let the compiler ask more deeply before finishing the scoped body.",
  lang: "Language hint for an embedded fenced block.",
  label: "Human-readable label attached to an embedded block or example.",
  indent: "Whether embedded content should be indented for readability.",
  language: "Host implementation language for a `@bind` companion.",
  from: "Relative companion implementation file for `@bind`.",
  symbol: "Exported function/class symbol in the companion implementation.",
  scheduler: "Functional scheduler: `sequential`, `graph`, or `graph-strict`.",
  uses: "Functional dependency list naming earlier result bindings used by this node. In graph-strict mode, every result placeholder in positional arguments, options, or body requires its root name here.",
  allow_effects: "Effects authorized for a functional executable spec.",
  initial: "Initial state for an inline FSLM `@machine`.",
  target: "Target state for an FSLM transition.",
  to: "Alias for `target:` on an FSLM transition.",
  internal: "Whether the autonomous FSLM runner may choose this transition.",
  external: "Whether host/user/environment events may trigger this transition.",
  tool: "Concrete tool authorized by this FSLM action after guards pass.",
  prompt_key: "Override the generated FSLM prompt key for a guard or action.",
  mode: "Directive-specific operating mode. Check the directive hover for accepted values.",
  default: "Default parameter value in a long-form `@define` signature.",
  implicit: "Marks a long-form `@param` as the implicit body parameter.",
};

class WeaveMarkHoverProvider {
  provideHover(document, position) {
    const line = document.lineAt(position).text;
    const escapedRange = document.getWordRangeAtPosition(position, /@@\w+/);
    if (escapedRange) {
      const md = new vscode.MarkdownString();
      md.appendMarkdown("### Escaped Directive\n\n");
      md.appendMarkdown(
        "`@@` outputs a literal `@` character. The directive is **not** processed.\n"
      );
      return new vscode.Hover(md, escapedRange);
    }
    if (analyzeSource(document.getText()).ignoredLines.has(position.line)) {
      return undefined;
    }
    const range = document.getWordRangeAtPosition(position, /@\w+\??/);

    // 1. Hover over @directive
    if (range) {
      const word = document.getText(range).replace("@", "");
      const info = DIRECTIVES[word] || DEBUG_DIRECTIVES[word];
      if (info) {
        const md = new vscode.MarkdownString();
        md.appendMarkdown(`### ${info.label}\n\n`);
        if (info.category) {
          md.appendMarkdown(`*Category: ${info.category}*\n\n`);
        }
        md.appendMarkdown(info.documentation);
        return new vscode.Hover(md, range);
      }
    }

    // 2. Hover over @{variable}
    const varRange = document.getWordRangeAtPosition(position, /@\{[A-Za-z_][\w.-]*\}/);
    if (varRange) {
      const varText = document.getText(varRange);
      const varName = varText.replace(/^@\{|\}$/g, "");
      const usages = this._countUsages(document, varName);
      const md = new vscode.MarkdownString();
      md.appendMarkdown(`### Variable: \`@{${varName}}\`\n\n`);
      md.appendMarkdown(`WeaveMark variable replaced at composition time with values from a vars file, CLI arguments, or the Python library API.\n\n`);
      md.appendMarkdown(`**Usages in this file:** ${usages}\n\n`);
      md.appendMarkdown(`*Provide values via:*\n`);
      md.appendMarkdown(`- \`weavemark spec.weavemark.md --vars-file vars.json --batch-only\`\n`);
      md.appendMarkdown(`- Inline: \`weavemark spec.weavemark.md --var ${varName}="value"\`\n`);
      md.appendMarkdown(`- Python: \`await compile_file("spec.weavemark.md", {"${varName}": "value"})\`\n`);
      return new vscode.Hover(md, varRange);
    }

    // 3. Hover over ==> (match arrow)
    const arrowRange = document.getWordRangeAtPosition(position, /==>/);
    if (arrowRange) {
      const md = new vscode.MarkdownString();
      md.appendMarkdown("### Match Case Arrow `==>`\n\n");
      md.appendMarkdown('Separates a match pattern from its content in a `@match` block.\n\n');
      md.appendMarkdown('- `"value" ==>` matches a specific string\n');
      md.appendMarkdown('- `_ ==>` is the default/fallback case\n');
      return new vscode.Hover(md, arrowRange);
    }

    // 4. Hover over execution strategy name (after @execute)
    const execMatch = line.match(/^\s*@execute\s+(\S+)/);
    if (execMatch) {
      const strategyName = execMatch[1];
      const strategyStart = line.indexOf(strategyName);
      const strategyEnd = strategyStart + strategyName.length;
      const strategyRange = new vscode.Range(position.line, strategyStart, position.line, strategyEnd);
      if (strategyRange.contains(position) && EXECUTION_STRATEGIES.includes(strategyName)) {
        const descriptions = {
          "single-call": "Sends the prompt in a single LLM call. Simplest and fastest strategy.",
          "self-consistency": "Generates multiple independent samples and picks the most common answer via majority voting. Improves reliability for reasoning tasks.",
          "tree-of-thought": "Full tree search requiring `@prompt thought_step`, `@prompt evaluate_step`, and `@prompt synthesize`.",
          "simplified-tree-of-thought": "Lightweight flow requiring `@prompt generate`, `@prompt evaluate`, and `@prompt synthesize`.",
          "reflection": "Generate an initial response → Critique it → Revise based on the critique. Requires `@prompt generate`, `@prompt critique`, and `@prompt revise` sections.",
          "chain": "Runs named prompt stages in source order. Each stage can use `@{previous}` and prior stage outputs; text and image output contracts may be mixed.",
          "collaborative": "Human-in-the-loop generation/edit/continuation flow for collaborative drafting.",
          "fslm": "Runs an ellements finite-state linguistic machine. Inline sugar generates collision-safe prompt keys with state and transition context, such as `guard.<state>.<transition>.<id>` and `action.<state>.<transition>.<name>`.",
          "functional": "Executes validated semantic nodes through authorized Python `@bind` capabilities and renders native dependency/results into the document. Render-only documents return directly; nonempty remaining instructions use the configured LLM.",
        };
        const md = new vscode.MarkdownString();
        md.appendMarkdown(`### Strategy: \`${strategyName}\`\n\n`);
        md.appendMarkdown(descriptions[strategyName] || "");
        return new vscode.Hover(md, strategyRange);
      }
    }

    // 5. Hover over @use clauses and common key: parameters
    const bareRange = document.getWordRangeAtPosition(position, /[A-Za-z_][\w.-]*/);
    if (bareRange) {
      const word = document.getText(bareRange);

      if (/^\s*@use\b/.test(line)) {
        const importDoc = this._importClauseDocumentation(word);
        if (importDoc) {
          const md = new vscode.MarkdownString();
          md.appendMarkdown(importDoc);
          return new vscode.Hover(md, bareRange);
        }
      }

      const keyStart = bareRange.end.character;
      if (line.slice(keyStart).trimStart().startsWith(":") && PARAMETER_DOCS[word]) {
        const md = new vscode.MarkdownString();
        md.appendMarkdown(`### Parameter: \`${word}:\`\n\n`);
        md.appendMarkdown(PARAMETER_DOCS[word]);
        return new vscode.Hover(md, bareRange);
      }
    }

    return undefined;
  }

  _importClauseDocumentation(word) {
    if (word === "exposing") {
      return "### `exposing`\n\nImports selected module definitions directly into the current namespace.\n\n```weavemark\n@use my.finance.tools exposing risk_score, summarize_portfolio\n```";
    }
    if (word === "as") {
      return "### `as`\n\nAliases the imported module for qualified use.\n\n```weavemark\n@use company.finance as finance\n```";
    }
    if (word === "expose") {
      return "### Did you mean `exposing`?\n\nWeaveMark uses `exposing`, not `expose`, for direct imports.";
    }
    if (word === "only") {
      return "### Use `exposing`\n\nWeaveMark uses `exposing` for selected imports.";
    }
    return undefined;
  }

  _countUsages(document, varName) {
    const text = document.getText();
    const escaped = varName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(`@\\{${escaped}\\}`, "g");
    let count = 0;
    while (re.exec(text)) count++;
    return count;
  }
}

module.exports = { WeaveMarkHoverProvider };
