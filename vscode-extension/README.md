# WeaveMark for VS Code

Language and execution support for [WeaveMark](../README.md) promplets
(`.weavemark.md`).

## Features

- **Current language catalog** — completions and hovers for core directives,
  default prelude definitions, FSLM sugar, `@output`, and `@package`
- **Diagnostics** — unknown and duplicate declarations, invalid execution
  strategies, unresolved local refinement paths, and malformed variables
- **Navigation** — outline, folding, local path definitions, and workspace module
  definitions
- **Safe commands** — Compose, Run, TUI, Discover, and Fill & Run launch the
  configured CLI directly with argument arrays, never through shell command text
- **Form view** — validated scan metadata, strict messages, escaped content, and
  a nonce-based Content Security Policy
- **Variable highlighting** — `@{name}`
- **Match case syntax** — `"value" ==>` and `_ ==>` (wildcard)
- **Escape sequences** — `@@property` rendered as dimmed (literal `@` in output)
- **Note blocks** — `@note` + indented body shown as comments
- **Debug queries** — `@directives?`, `@vars?`, `@structure?`
- **Directive arguments** — `key: value` pairs with type-aware coloring (booleans, numbers, strings)
- **Module clauses** — `exposing`, `as`, imported names, and invalid old clauses (`expose`, `only`)
- **Macro/semantic definitions** — `@define`, `@param`, `@body`, `@phase`, `@scope`, `@returns`, `@effect`
- **Markdown surface sugar** — `## @prompt ...` headings and
  `> [!PROMPLET ...]` callouts
- **File paths** — underlined after path-bearing directives
- **Markdown base** — headings, bold, italic, fenced blocks, links, lists
- **Two themes** — WeaveMark Dark and WeaveMark Light with branded colors

## Installation

### From Source (Development)

1. Copy or symlink this directory into your VSCode extensions folder:

   ```bash
   # macOS / Linux
   ln -s "$(pwd)" ~/.vscode/extensions/weavemark

   # Windows (PowerShell, run as admin)
   New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.vscode\extensions\weavemark" -Target (Get-Location)
   ```

2. Reload VSCode (`Cmd+Shift+P` → "Developer: Reload Window")

3. Open any `.weavemark.md` file — syntax highlighting activates automatically

### Theme Activation

1. `Cmd+K Cmd+T` (or `Ctrl+K Ctrl+T`)
2. Select **WeaveMark Dark** or **WeaveMark Light**

## Security model

- The executable path and extra argument array are machine-scoped settings, so a
  repository cannot replace the CLI that VS Code launches.
- Syntax, diagnostics, navigation, and completions remain available in untrusted
  workspaces. Commands that scan or execute through the local CLI are blocked
  until the workspace is trusted.
- Process arguments are passed without shell parsing. Characters such as
  backticks, `$()`, quotes, semicolons, and newlines remain literal argument data.
- Webview scripts run only under a per-render nonce; remote content, inline event
  handlers, command URIs, and local-resource roots are disabled.

WeaveMark execution is intentionally powerful. In a trusted workspace, Run/TUI
can invoke configured models, tools, bindings, and package steps, and model calls
can transmit composed content to the configured provider. Review promplets and
their companion implementations before execution.

## Settings

```json
{
  "weavemark.cliPath": "/absolute/path/to/weavemark",
  "weavemark.defaultModel": "gpt-5.5",
  "weavemark.extraArgs": ["--library-dir", "/path/to/promplets"]
}
```

`cliPath` and `extraArgs` are user/machine settings. Each `extraArgs` item is one
literal process argument.

## Development checks

```bash
npm test
npm run check
```

## File Extension

WeaveMark files use the `.weavemark.md` extension. This keeps them recognizable as Markdown while enabling dedicated syntax highlighting.

```
promplets/
├── stdlib/fragments/reasoning/base-analyst.weavemark.md
├── catalog/standalone/market-research-brief.weavemark.md
└── catalog/executable/recurring-topic-monitor.weavemark.md
```

## Syntax Quick Reference

```markdown
@promplet version: 0.8 surface: markdown

@define reusable_warning
  @param severity default: medium
    Warning severity.
  @body
    Treat this as a @{severity} risk.

@refine ../library/reasoning/base-analyst.weavemark.md mingle: true

@ask clarifying question detail_level: 40%  # Compile-time questions
  Clarify consequential ambiguity while this body is compiled.

@note                                        # Engineer comment (stripped from output)
  This is not included in the final prompt.

@match report_depth                          # Pattern matching
  "executive" ==>
    Executive summary content.
  "detailed" ==>
    Detailed report content.
  _ ==>
    Default fallback.

@if include_competitors                      # Conditional branch
  Competitor analysis goes here.
@else_if include_market_context
  Market context goes here.
@else
  Skip competitors.

@revise "Integrate the new requirement." mode: minimal  # Semantic revision
  Draft content to revise.

@style "For senior engineers: concise, authoritative, data-driven."
  Draft content to restyle.

@normalize "Smooth structure and wording." scope: both
  Draft content to normalize.

@{company} operates in @{industry}.          # WeaveMark variables
The program_@{version}_final is ready.       # Explicit variable boundary

@@property @@Override user@@example.com      # Escaped @ (literal in output)

@directives?                                 # Debug: list directives
@vars?                                       # Debug: list variables
```

Markdown-surface syntax is colored too when you write promplets with
`@promplet version: 0.8 surface: markdown`:

```markdown
## @prompt analyst role: system format: mustache

You are analysing {{asset}}.

> [!PROMPLET style]
> Calm, precise, executive.
```

## Color Palette

### Dark Theme (Dracula-inspired, vivid neon)

| Element | Color | Hex |
|---------|-------|-----|
| Directives (`@keyword`) | **Hot Pink** | `#FF79C6` |
| Module/import keywords (`@use`, `exposing`) | **Cyan** | `#8BE9FD` |
| Definitions (`@define`, `@body`) | **Neon Green** | `#50FA7B` |
| Surface sugar (`## @prompt`, callouts) | **Lavender** | `#BD93F9` |
| Variables (`@{name}`) | **Bright Orange** | `#FFB86C` |
| Match cases (`"value"`) | **Neon Green** | `#50FA7B` |
| Match arrow (`==>`) | **Red** | `#FF5555` |
| File paths | **Cyan** | `#8BE9FD` |
| Strings (`"..."`) | **Yellow-Green** | `#F1FA8C` |
| Key names (`key:`) | **Cyan italic** | `#8BE9FD` |
| Key values | **Purple** | `#BD93F9` |
| Booleans / numbers | **Purple** | `#BD93F9` |
| `@{ }` punctuation | **Purple** | `#BD93F9` |
| Notes / `@@` escapes | **Dim gray** | `#6272A4` |
| Debug queries | **Yellow bold** | `#F1FA8C` |
| Headings | **Purple bold** | `#BD93F9` |
| Inline monospace spans | **Green** | `#50FA7B` |
| List markers | **Pink** | `#FF79C6` |

### Light Theme (Material-inspired, rich contrast)

| Element | Color | Hex |
|---------|-------|-----|
| Directives (`@keyword`) | **Vivid Purple** | `#AF00DB` |
| Module/import keywords (`@use`, `exposing`) | **Blue** | `#0070C1` |
| Definitions (`@define`, `@body`) | **Forest Green** | `#098658` |
| Surface sugar (`## @prompt`, callouts) | **Deep Purple** | `#6F42C1` |
| Variables (`@{name}`) | **Burnt Orange** | `#D16900` |
| Match cases (`"value"`) | **Forest Green** | `#098658` |
| Match arrow (`==>`) | **Red** | `#E51400` |
| File paths | **Blue** | `#0070C1` |
| Strings (`"..."`) | **Green** | `#098658` |
| Key names (`key:`) | **Blue italic** | `#0070C1` |
| Key values | **Purple** | `#AF00DB` |
| Booleans / numbers | **Purple** | `#AF00DB` |
| `@{ }` punctuation | **Purple** | `#AF00DB` |
| Notes / `@@` escapes | **Gray** | `#A0A1A7` |
| Debug queries | **Orange bold** | `#D16900` |
| Headings | **Blue bold** | `#0070C1` |
| Inline monospace spans | **Green** | `#098658` |
| List markers | **Purple** | `#AF00DB` |
