// WeaveMark — Document symbol provider
//
// Populates the Outline view and breadcrumbs with:
//   • @execute — strategy declaration
//   • @prompt — named prompt sections
//   • @tool — tool definitions
//   • @match / @if — control flow blocks
//   • @refine / @ask / @iterate — composition effects
//   • Markdown headings (# ## ###)

const vscode = require("vscode");
const { analyzeSource } = require("./language");

const SYMBOL_PATTERNS = [
  { re: /^\s*@module\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Module, prefix: "📦 @module" },
  { re: /^\s*@use\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Namespace, prefix: "↪ @use" },
  { re: /^\s*@define\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Function, prefix: "✨ @define" },
  { re: /^\s*@execute\s+(\S+)/, kind: vscode.SymbolKind.Event, prefix: "⚡ @execute" },
  { re: /^\s*@machine\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Class, prefix: "🤖 @machine" },
  { re: /^\s*@state\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Object, prefix: "◎ @state" },
  { re: /^\s*@transition\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Event, prefix: "→ @transition" },
  { re: /^\s*@guard\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Boolean, prefix: "◇ @guard" },
  { re: /^\s*@action\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Method, prefix: "▶ @action" },
  { re: /^\s*@prompt\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Function, prefix: "📝 @prompt" },
  { re: /^\s*@emit\s+file:\s+(\S+)/, kind: vscode.SymbolKind.File, prefix: "📤 @emit" },
  { re: /^\s*@output\b(.*)/, kind: vscode.SymbolKind.TypeParameter, prefix: "⇥ @output" },
  { re: /^\s*@package\b.*\bfile:\s*(\S+)/, kind: vscode.SymbolKind.File, prefix: "📦 @package" },
  { re: /^\s*@tool\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Method, prefix: "🔧 @tool" },
  { re: /^\s*@bind\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Interface, prefix: "🔌 @bind" },
  { re: /^\s*@match\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Enum, prefix: "🔀 @match" },
  { re: /^\s*@if\s+(.+?)\s*$/, kind: vscode.SymbolKind.Boolean, prefix: "❓ @if" },
  { re: /^\s*@else_if\s+(.+?)\s*$/, kind: vscode.SymbolKind.Boolean, prefix: "❓ @else_if" },
  { re: /^\s*@refine\s+(\S+)/, kind: vscode.SymbolKind.Module, prefix: "📎 @refine" },
  { re: /^\s*@ask(?:\s+(.+?))?\s*$/, kind: vscode.SymbolKind.Event, prefix: "❔ @ask" },
  { re: /^\s*@iterate(?:\s+(.+?))?\s*$/, kind: vscode.SymbolKind.Event, prefix: "↻ @iterate" },
  { re: /^\s*@polish(?:\s+(.+?))?\s*$/, kind: vscode.SymbolKind.Event, prefix: "✨ @polish" },
  { re: /^\s*@embed\s+.*(?:file|label):\s*(\S+)/, kind: vscode.SymbolKind.File, prefix: "📎 @embed" },
  { re: /^\s*#{1,6}\s+@([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Event, prefix: "☑ markdown surface" },
  { re: /^\s*>\s*\[!PROMPLET\s+([A-Za-z_][\w.-]*)/, kind: vscode.SymbolKind.Event, prefix: "☑ callout" },
  { re: /^\s*(#{1,6})\s+(.+)$/, kind: vscode.SymbolKind.String, prefix: "" },
];

class WeaveMarkDocumentSymbolProvider {
  provideDocumentSymbols(document) {
    const symbols = [];
    const analysis = analyzeSource(document.getText());

    for (let i = 0; i < document.lineCount; i++) {
      if (analysis.ignoredLines.has(i)) continue;
      const line = document.lineAt(i);
      const text = line.text;

      for (const pat of SYMBOL_PATTERNS) {
        const m = text.match(pat.re);
        if (!m) continue;

        let name;
        if (pat.prefix === "") {
          // Markdown heading
          const level = m[1].length;
          name = `${"#".repeat(level)} ${m[2]}`;
        } else {
          name = `${pat.prefix} ${m[1] || ""}`.trim();
        }

        const range = line.range;
        const symbol = new vscode.DocumentSymbol(name, "", pat.kind, range, range);
        symbols.push(symbol);
        break;
      }
    }

    return symbols;
  }
}

module.exports = { WeaveMarkDocumentSymbolProvider };
