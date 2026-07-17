// WeaveMark directive catalog — documentation, parameters, snippets
//
// Single source of truth for all directives. Used by completions,
// hovers, diagnostics, and signature help.

const DIRECTIVES = {
  // ── Preamble ──────────────────────────────────────────────────
  promplet: {
    label: "@promplet",
    detail: "Version pragma — place at top of file",
    documentation:
      "Declares the WeaveMark language version and optional authoring surface. Must be the first directive if present.\n\n" +
      "**Parameters:**\n" +
      "- `version: <major.minor>` — Language version (current: `0.7`)\n" +
      "- `surface: canonical|markdown` — Optional surface adapter. Use `markdown` for directive headings and WeaveMark callouts.\n\n" +
      "**Example:**\n```\n@promplet version: 0.7 surface: markdown\n```",
    snippet: "@promplet version: ${1:0.7} surface: ${2|canonical,markdown|}",
    params: { version: null, surface: ["canonical", "markdown"] },
    category: "Preamble",
  },

  // ── Module System ─────────────────────────────────────────────
  module: {
    label: "@module",
    detail: "Declare a module namespace for this file",
    documentation:
      "Declares that this file is a module. A module file may contain only the module declaration and its definitions — no top-level prompt content. Each file may declare at most one module.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: fully-qualified module name (dot-separated, e.g. `my.lib.utils`)\n\n" +
      "**Example:**\n```\n@module my.finance.tools\n\n@define fetch_price(symbol: ticker symbol)\n  Fetch current price for @{symbol}.\n```",
    snippet: "@module ${1:my.module.name}",
    params: { file: null },
    category: "Module System",
  },
  use: {
    label: "@use",
    detail: "Import definitions from a module",
    documentation:
      "Imports macros and semantic functions from another module. You can use definitions through a namespace, or expose selected names directly with `exposing`.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: module name\n" +
      "- `exposing name1, name2` — Import selected definitions directly. The keyword is `exposing` (not `expose`).\n" +
      "- `as alias` — Bind the whole module under an alias for qualified use\n\n" +
      "**Examples:**\n```\n@use my.finance.tools exposing risk_score\n@use my.lib.utils as utils\n```",
    snippet: "@use ${1:my.module} exposing ${2:definition}",
    params: { exposing: null, as: null },
    category: "Module System",
  },
  include: {
    label: "@include",
    detail: "Insert reusable body content from an imported module",
    documentation:
      "Inserts the reusable body content of a module imported with `@use`, or of a resolvable module name. Unlike `@refine` (which loads another promplet file), `@include` targets modules.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: module name or alias\n\n" +
      "**Example:**\n```\n@use company.agent.reviewer as reviewer\n\n@include reviewer\n```",
    snippet: "@include ${1:module_or_alias}",
    params: {},
    category: "Module System",
  },

  // ── Macro & Semantic Function Definitions ─────────────────────
  define: {
    label: "@define",
    detail: "Define a macro or semantic function",
    documentation:
      "Defines a reusable macro (pure text expansion) or semantic function (effectful, with `@effect`).\n\n" +
      "**Compact signature:**\n```\n@define NAME(param: natural language description, body: implicit body description)\n  BODY\n```\n\n" +
      "**Extended signature** (use `@param` sub-directives when descriptions need more detail):\n```\n@define NAME\n  @param first_arg\n    Free-text description of the first positional arg.\n  @param body implicit: true mode: subspec\n    The implicit body argument.\n  @body\n    BODY\n```\n\n" +
      "**Adding `@effect` makes it a semantic function:**\n```\n@define fetch_price\n  @phase execute\n  @scope self\n  @returns price_data\n  @param symbol\n    Ticker symbol.\n  @effect market_data read\n  @body\n    Fetch the latest price for @{symbol}.\n```\n\n" +
      "**Example (pure macro):**\n```\n@define greet(name: person to greet)\n  Hello, @{name}!\n```\n\n" +
      "**Call it with:**\n```\n@greet Alice\n```",
    snippet: "@define ${1:name}(${2:param}: ${3:description})\n  ${4:body}",
    params: {},
    category: "Definitions",
  },
  param: {
    label: "@param",
    detail: "Declare a parameter inside @define (extended signature)",
    documentation:
      "Used inside a `@define` body to describe a parameter. Preferred when the inline signature becomes unwieldy.\n\n" +
      "**Syntax:**\n```\n@param name [default: value] [implicit: true] [mode: text|subspec|path]\n  Description of this parameter.\n```\n\n" +
      "**Example:**\n```\n@define summarize_portfolio\n  @param holdings\n    A list of asset holdings.\n  @param format default: bullets\n    One of: bullets, table, paragraph.\n  @body\n    Summarise the portfolio holdings in @{format} format.\n```",
    snippet: "@param ${1:name}\n  ${2:Description.}",
    params: {},
    category: "Definitions",
  },
  body: {
    label: "@body",
    detail: "Begin the expansion template inside a long-form @define",
    documentation:
      "Used inside a long-form `@define` block. The indented body is the WeaveMark expansion template for the macro or semantic function.\n\n" +
      "**Example:**\n```\n@define greet\n  @param name\n    Person to greet.\n  @body\n    Hello, @{name}!\n```",
    snippet: "@body\n  ${1:template body}",
    params: {},
    category: "Definitions",
  },
  bind: {
    label: "@bind",
    detail: "Attach a companion runtime implementation to a capability",
    documentation:
      "Associates a host-language implementation (Python, JavaScript, …) with a named capability or tool. Used by `@tool` for runtime call dispatch and by compile-phase `@effect` declarations. Always use `@bind` to supply implementations — never inline them.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: capability name\n" +
      "- `language: python|javascript|…` — Implementation language\n" +
      "- `from: <relative-path>` — Companion file path (must be relative, no `..`)\n" +
      "- `symbol: <name>` — Function/class symbol exported from that file\n\n" +
      "**Example:**\n```\n@bind fetch_price language: python from: ./tools/market.py symbol: fetch_price\n```",
    snippet: "@bind ${1:capability_name} language: ${2|python,javascript|} from: ${3:./impl.py} symbol: ${4:fn_name}",
    params: { language: ["python", "javascript", "typescript", "bash"], from: null, symbol: null },
    category: "Definitions",
  },

  // ── Semantic Function Sub-directives ──────────────────────────
  phase: {
    label: "@phase",
    detail: "Declare execution phase of a semantic function",
    documentation:
      "Used inside a `@define` block to declare when the semantic function runs.\n\n" +
      "- `compile` — Runs during LLM composition (may read files, modify prompt text).\n" +
      "- `execute` — Runs when the document is executed under `@execute weave`.\n\n" +
      "**Example:**\n```\n@define check_style\n  @phase compile\n  @scope body\n  @returns diagnostics\n  @param text\n    Text to inspect.\n  @effect inspect_text read\n  @body\n    Check style of @{text}.\n```",
    snippet: "@phase ${1|compile,execute|}",
    params: {},
    category: "Semantic Functions",
  },
  scope: {
    label: "@scope",
    detail: "Declare the region a semantic function may modify",
    documentation:
      "Used inside a `@define` block. Valid scopes:\n\n" +
      "- `self` — Only the directive call site.\n" +
      "- `body` — Only the directive's own body.\n" +
      "- `enclosing_block` — The nearest enclosing `@prompt` or `@if` block.\n" +
      "- `prompt` — The entire current `@prompt` section.\n" +
      "- `document` — The entire document.\n" +
      "- `metadata` — Output metadata (tags, annotations) only.\n\n" +
      "**Example:**\n```\n@define enforce_brevity\n  @phase compile\n  @scope prompt\n  Trim the prompt to essentials.\n```",
    snippet: "@scope ${1|self,body,enclosing_block,prompt,document,metadata|}",
    params: {},
    category: "Semantic Functions",
  },
  returns: {
    label: "@returns",
    detail: "Declare what a semantic function produces",
    documentation:
      "Used inside a `@define` block to name the value the function produces. The return value is bound to this name and can be referenced elsewhere as `@{name}`.\n\n" +
      "**Example:**\n```\n@define fetch_snapshot\n  @phase execute\n  @effect network\n  @returns market_snapshot\n  Fetch the market snapshot.\n```",
    snippet: "@returns ${1:result_name}",
    params: {},
    category: "Semantic Functions",
  },
  effect: {
    label: "@effect",
    detail: "Declare a side-effect capability required by a semantic function",
    documentation:
      "Used inside a `@define` block. A definition with at least one `@effect` becomes a *semantic function*; one without is a pure macro.\n\n" +
      "**Common effect names:**\n" +
      "- `read_file` — Read local files.\n" +
      "- `write_file` — Write local files.\n" +
      "- `network` — Perform network requests.\n" +
      "- `llm_call` — Invoke an LLM.\n" +
      "- `database` — Query a database.\n\n" +
      "**Example:**\n```\n@define load_context\n  @phase compile\n  @scope document\n  @returns replacement\n  @param file mode: path\n    File to load.\n  @effect read_file read\n  @body\n    Load context from @{file}.\n```",
    snippet: "@effect ${1|read_file,write_file,network,llm_call,database|}",
    params: {},
    category: "Semantic Functions",
  },

  // ── Composition ───────────────────────────────────────────────
  refine: {
    label: "@refine",
    detail: "Include & specialise from another spec (stdlib semantic function)",
    documentation:
      "**Stdlib semantic function** — defined in the default-loaded `semantics` module.\n\n" +
      "Semantically refines the current spec with another promplet referenced by a relative path, source-qualified path, or `module:<dotted.name>`. " +
      "By default, the imported spec is mingled into the current one so the final prompt preserves both sets of obligations as one coherent artifact. " +
      "Add an indented body to guide how semantic mingling should be performed for this specific refinement. The body is compiler-facing guidance; using a non-empty body with `mingle: false` is an error.\n\n" +
      "**Parameters:**\n" +
      "- `mingle: true|false` — `true` semantically integrates the refined spec (default); `false` preserves the loaded source more literally.\n\n" +
      "**Example:**\n```\n@refine base-prompt.weavemark.md mingle: true\n@refine shared/safety.weavemark.md\n```",
    snippet: "@refine ${1:file.weavemark.md}\n  ${2:mingle guidance}",
    params: { mingle: ["true", "false"] },
    category: "Composition",
  },
  ask: {
    label: "@ask",
    detail: "Ask compile-time questions while a scoped body is being composed",
    documentation:
      "**Stdlib semantic function** — defined in the default-loaded `semantics` module.\n\n" +
      "Requests host-mediated questions during compilation. `@ask` stays active while the target body or enclosing scope is being transformed. " +
      "If a transformation exposes new consequential ambiguity, the compiler may keep `@ask` in an intermediate compiler-result object and ask more questions in another compile-effect round. " +
      "The final accepted output must remove all resolved `@ask` directives.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: question type (default: `clarifying question`)\n" +
      "- `detail_level: <percentage>` — How deeply to clarify, greater than `0%` and no greater than `100%` (default: `20%`)\n\n" +
      "**Example:**\n```\n@ask clarifying question detail_level: 40%\n  Draft a customer interview prompt for @{product}.\n```",
    snippet: "@ask ${1:clarifying question} detail_level: ${2:20%}\n  ${3:body to clarify}",
    params: { detail_level: null },
    category: "Composition",
  },
  iterate: {
    label: "@iterate",
    detail: "Rerun traceable directive steps when judged materially improvable",
    documentation:
      "**Stdlib semantic function** — defined in the default-loaded `semantics` module.\n\n" +
      "Compiles the target through inside-out directive-application steps, records step envelopes, judges previous step results, and reruns only steps that can be materially improved while preserving the original directive semantics and parameters. " +
      "The optional positional integer counts improvement iterations after iteration 0 and is capped by the host compiler's `max_iterate_turns` setting. If the budget is exhausted, compilation returns the best available result with a warning.\n\n" +
      "A leading `@ask` wrapper can act as the iteration prelude while keeping ordinary `@ask` semantics: the `@ask` clarifies its own body, and that body is also the iteration target.\n\n" +
      "**Parameters:**\n" +
      "- Optional first positional argument: maximum improvement iterations\n\n" +
      "**Examples:**\n```\n@iterate 4\n  @expand mode: intention\n    Draft an API-design prompt.\n\n@iterate 4\n  @ask clarifying question detail_level: 40%\n    @expand mode: intention\n      Draft an onboarding prompt.\n```",
    snippet:
      "@iterate ${1:4}\n  ${2:body to improve}",
    params: {},
    category: "Composition",
  },
  expand: {
    label: "@expand",
    detail: "Add new content without removing existing",
    documentation:
      "**Stdlib semantic function** — defined in the default-loaded `semantics` module.\n\n" +
      "Expands a compact term, phrase, sentence, query, instruction, or short passage into coherent prompt prose.\n\n" +
      "**Parameters:**\n" +
      "- `mode: definition|intention|context` — What kind of expansion to perform (default: `definition`)\n" +
      "- `length: <percentage>` — Desired detail level (default: `100%`)\n" +
      "- `cap: <number|none>` — Optional character cap (default: `none`)\n" +
      "- `focus: \"...\"` — Free-form guidance for what aspect to expand\n\n" +
      "**Example:**\n```\n@expand mode: intention focus: \"safety implications\"\n  Add a safety considerations section.\n```",
    snippet: "@expand mode: ${1|definition,intention,context|} focus: \"${2:expansion focus}\"\n  ${3:concept to expand}",
    params: { mode: ["definition", "intention", "context"], length: null, cap: null, focus: null },
    category: "Composition",
  },
  revise: {
    label: "@revise",
    detail: "Replace conflicting requirements with new ones",
    documentation:
      "Applies the requested revision to its body. If the body is omitted, the revision applies to the current enclosing specification scope.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: revision instruction\n" +
      "- `mode: minimal|editorial` — How aggressively to revise\n\n" +
      "**Examples:**\n```\n@revise \"Output must be JSON only, no markdown.\" mode: editorial\n\n@revise \"Remove contradictions.\" mode: minimal\n  Draft prompt text.\n```",
    snippet: "@revise \"${1:revision instruction}\" mode: ${2|minimal,editorial|}\n  ${3:target body}",
    params: { mode: ["minimal", "editorial"] },
    category: "Composition",
  },

  // ── Semantic Transform ────────────────────────────────────────
  normalize: {
    label: "@normalize",
    detail: "Canonicalize structure and smooth wording",
    documentation:
      "**Stdlib macro** — defined in the default-loaded `semantics` module.\n\n" +
      "Applies the requested normalization to its body. If the body is omitted, normalization applies to the current enclosing specification scope.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: normalization guidance\n" +
      "- `scope: syntactic|semantic|both`\n" +
      "- `headings: keep|normalize`\n" +
      "- `lists: keep|normalize`\n" +
      "- `terminology: keep|normalize`\n" +
      "- `intensity: low|medium|high`\n\n" +
      "**Examples:**\n```\n@normalize \"Clean up wording and headings.\" scope: both intensity: medium\n\n@normalize \"Use consistent terminology.\" scope: semantic\n  Draft instructions to clean up.\n```",
    snippet: "@normalize \"${1:normalization guidance}\" scope: ${2|syntactic,semantic,both|} intensity: ${3|low,medium,high|}\n  ${4:target body}",
    params: {
      scope: ["syntactic", "semantic", "both"],
      headings: ["keep", "normalize"],
      lists: ["keep", "normalize"],
      terminology: ["keep", "normalize"],
      intensity: ["low", "medium", "high"],
    },
    category: "Semantic Transform",
  },
  style: {
    label: "@style",
    detail: "Apply tone, voice, and formatting preferences",
    documentation:
      "Applies the requested style to its body. If the body is omitted, the style applies to the current enclosing specification scope.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: style description (tone, voice, register, formatting, audience, or presentation constraints)\n\n" +
      "**Examples:**\n```\n@style \"Concise, direct, and friendly. Use bullet points.\"\n\n@style \"For senior engineers: precise and implementation-ready.\"\n  Draft the implementation prompt.\n```",
    snippet: "@style \"${1:style description}\"\n  ${2:target body}",
    params: {},
    category: "Semantic Transform",
  },
  polish: {
    label: "@polish",
    detail: "Give assembled content a coherent final presentation",
    documentation:
      "**Stdlib semantic function** — defined in the default-loaded `semantics` module.\n\n" +
      "Polishes its body into a coherent, presentation-ready prompt without adding or removing substantive information. If the body is omitted, polish applies to the current enclosing specification scope.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: optional presentation/organization guidance\n\n" +
      "**Examples:**\n```\n@polish \"Harmonize terminology and remove duplication without dropping requirements.\"\n\n@polish \"Make the assembled sections read as one coherent final prompt.\"\n  Rough assembled prompt text.\n```",
    snippet: "@polish \"${1:polish guidance}\"\n  ${2:target body}",
    params: {},
    category: "Semantic Transform",
  },

  // ── Lossy Content ─────────────────────────────────────────────
  summarize: {
    label: "@summarize",
    detail: "Replace content with a summary",
    documentation:
      "Condenses the prompt content into a shorter form.\n\n" +
      "**Parameters:**\n" +
      "- `length: short|medium|long`\n" +
      "- `focus: requirements|rationale|mixed`\n\n" +
      "**Example:**\n```\n@summarize length: short focus: requirements\n```",
    snippet: "@summarize ${1:length: short} ${2:focus: requirements}",
    params: { length: ["short", "medium", "long"], focus: ["requirements", "rationale", "mixed"] },
    category: "Lossy Content",
  },
  compress: {
    label: "@compress",
    detail: "Reduce token footprint while preserving meaning",
    documentation:
      "Aggressively reduces the prompt's size to fit token budgets.\n\n" +
      "**Parameters:**\n" +
      "- `target: tokens|chars` — Unit of measurement\n" +
      "- `budget: <number>` — Target size\n" +
      "- `preserve: hard|balanced` — How strictly to keep key content\n\n" +
      "**Example:**\n```\n@compress target: tokens budget: 800 preserve: balanced\n```",
    snippet: "@compress ${1:target: tokens} ${2:budget: 800}",
    params: { target: ["tokens", "chars"], preserve: ["hard", "balanced"] },
    category: "Lossy Content",
  },
  extract: {
    label: "@extract",
    detail: "Extract a subset into structured form",
    documentation:
      "Pulls out specific information from the prompt into a structured format.\n\n" +
      "**Parameters:**\n" +
      "- `format: bullets|json|yaml|markdown`\n\n" +
      "**Example:**\n```\n@extract format: json\n  All MUST constraints\n```",
    snippet: "@extract ${1:format: json}\n  ${2:what to extract}",
    params: { format: ["bullets", "json", "yaml", "markdown"] },
    category: "Lossy Content",
  },

  // ── Generation ────────────────────────────────────────────────
  generate_examples: {
    label: "@generate_examples",
    detail: "Add illustrative examples to the prompt",
    documentation:
      "Generates example input/output pairs to make the prompt clearer.\n\n" +
      "**Parameters:**\n" +
      "- `count: <number>` — How many examples\n" +
      "- `style: minimal|realistic`\n\n" +
      "**Example:**\n```\n@generate_examples count: 3 style: realistic\n```",
    snippet: "@generate_examples ${1:count: 3} ${2:style: realistic}",
    params: { count: null, style: ["minimal", "realistic"] },
    category: "Generation",
  },
  example: {
    label: "@example",
    detail: "Add an author-provided few-shot example",
    documentation:
      "**Stdlib macro** — defined in the default-loaded `semantics` module.\n\n" +
      "Adds a labeled example to clarify expected behavior or output shape.\n\n" +
      "**Parameters:**\n" +
      "- `label: <text>` — Example label\n" +
      "- `placement: append|integrate` — Placement preference\n\n" +
      "**Example:**\n```\n@example label: \"Good output\"\n  Input: pricing data\n  Output: concise risk summary\n```",
    snippet: "@example ${1:label: \"Example\"}\n  ${2:example content}",
    params: { label: null, placement: ["append", "integrate"] },
    category: "Generation",
  },

  // ── Visualization & Meta ──────────────────────────────────────
  inspect: {
    label: "@inspect",
    detail: "Mark a region for verbose post-compose inspection (stdlib)",
    documentation:
      "**Stdlib semantic function** — defined in the default-loaded `semantics` module.\n\n" +
      "Marks the enclosed block for detailed post-composition inspection. Useful for debugging what the compiler does at a specific point.\n\n" +
      "**Example:**\n```\n@inspect\n  @style\n    Concise, bullet-pointed.\n```",
    snippet: "@inspect\n  ${1:content to inspect}",
    params: {},
    category: "Meta",
  },

  // ── Constraints ───────────────────────────────────────────────
  structural_constraints: {
    label: "@structural_constraints",
    detail: "Reshape prompt to required sections/order",
    documentation:
      "Enforces a specific structure (sections, headings, ordering) on the prompt.\n\n" +
      "**Parameters:**\n" +
      "- `strict: true|false`\n\n" +
      "**Example:**\n```\n@structural_constraints\n  Sections: Goal, Constraints, Output Format\n```",
    snippet: "@structural_constraints\n  ${1:structure description}",
    params: { strict: ["true", "false"] },
    category: "Constraints",
  },
  assert: {
    label: "@assert",
    detail: "Enforce a correctness condition on the prompt (stdlib)",
    documentation:
      "**Stdlib semantic function** — defined in the default-loaded `semantics` module.\n\n" +
      "Validates that the composed prompt satisfies a condition. Fails composition if not met.\n\n" +
      "**Parameters:**\n" +
      "- `contains:` / `not_contains:` — Deterministic text checks\n" +
      "- `section:` — Require a section\n" +
      "- `variable:` — Require a resolved variable\n" +
      "- `severity: error|warning` — Whether violation blocks composition\n\n" +
      "**Example:**\n```\n@assert severity: error The prompt must include an output schema.\n@assert severity: warning The prompt should mention error handling.\n```",
    snippet: "@assert ${1:severity: error} ${2:condition}",
    params: {
      contains: null,
      not_contains: null,
      section: null,
      variable: null,
      severity: ["error", "warning"],
    },
    category: "Constraints",
  },

  // ── Control Flow ──────────────────────────────────────────────
  if: {
    label: "@if",
    detail: "Conditional content based on a variable",
    documentation:
      "Includes the indented block only when the variable is truthy.\n\n" +
      "**Example:**\n```\n@if include_safety\n  Always refuse harmful requests.\n@else\n  Be helpful and direct.\n```",
    snippet: "@if ${1:variable_name}\n  ${2:content when true}",
    params: {},
    category: "Control Flow",
  },
  else_if: {
    label: "@else_if",
    detail: "Additional conditional branch after @if",
    documentation:
      "Adds another condition in an `@if` chain. It must follow an `@if` or another `@else_if` at the same indentation level.\n\n" +
      "**Example:**\n```\n@if audience_is_expert\n  Use concise expert terminology.\n@else_if audience_is_beginner\n  Explain terms carefully.\n@else\n  Use balanced language.\n```",
    snippet: "@else_if ${1:condition}\n  ${2:content when true}",
    params: {},
    category: "Control Flow",
  },
  else: {
    label: "@else",
    detail: "Fallback branch for @if",
    documentation:
      "Provides content when the preceding `@if` condition is false.\n\n" +
      "**Example:**\n```\n@if verbose_mode\n  Explain each step in detail.\n@else\n  Be concise.\n```",
    snippet: "@else\n  ${1:fallback content}",
    params: {},
    category: "Control Flow",
  },
  match: {
    label: "@match",
    detail: "Pattern matching on a variable's value",
    documentation:
      "Selects content based on which case matches the variable. Use `_ ==>` as the default/fallback case.\n\n" +
      "**Example:**\n```\n@match user_tier\n  \"free\" ==>\n    Basic features only.\n  \"pro\" ==>\n    All features unlocked.\n  _ ==>\n    Unknown tier.\n```",
    snippet: "@match ${1:variable_name}\n  \"${2:value}\" ==>\n    ${3:content}\n  _ ==>\n    ${4:default content}",
    params: {},
    category: "Control Flow",
  },

  // ── Multi-Prompt & Execution ──────────────────────────────────
  compile: {
    label: "@compile",
    detail: "Declare compile-time output defaults",
    documentation:
      "Sets compiler options for the spec. These options are not downstream assistant instructions. " +
      "If no `@compile format` and no CLI `--format` are supplied, WeaveMark assumes Markdown (`.md`). " +
      "An explicit CLI `--format` overrides this spec default and shows a warning.\n\n" +
      "**Parameters:**\n" +
      "- `format: <configured-format>` — Default CLI output format (`markdown`, `json`, `mustache`, `jinja`, or a format from `weavemark.json`). " +
      "Also controls the extension of role-tagged `@prompt` emissions " +
      "(`<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`).\n" +
      "- `context: auto|cascade|local` — Whether root prefix/suffix text is prepended " +
      "to each named block. `auto` keeps the inferred default: `cascade` for pipeline specs " +
      "(those with `@execute`) and `local` for emission specs.\n" +
      "- `images: on|off` — Enable or disable lifting Markdown image references into multimodal input parts.\n\n" +
      "**Example:**\n```\n@compile format: json\n```",
    snippet: "@compile format: ${1|markdown,json,mustache,jinja|}",
    params: {
      format: ["markdown", "json", "mustache", "jinja"],
      context: ["auto", "cascade", "local"],
      images: ["on", "off"],
    },
    category: "Output",
  },
  prompt: {
    label: "@prompt",
    detail: "Define a named prompt section or artifact",
    documentation:
      "Slices the spec into named blocks. Disposition is inferred from " +
      "`@execute` and `role:`:\n\n" +
      "- When the spec contains `@execute` → blocks become pipeline stages " +
      "in the compiled `prompts` map.\n" +
      "- When the spec has no `@execute` and every `@prompt` block has " +
      "`role:` → blocks are emitted as artifact files " +
      "`<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`.\n" +
      "- When the spec has no `@execute` and no `@prompt` block has " +
      "`role:` → blocks remain in the compiled `prompts` map for `@refine` consumption.\n" +
      "- Mixing role-tagged and role-less `@prompt` blocks without `@execute` is an error.\n\n" +
      "**Parameters (free order):**\n" +
      "- `role: <system|user|assistant|tool>` — Strict LLM chat role for this block " +
      "(case-insensitive, normalized to lowercase). Required for emission.\n" +
      "- `format: <configured-format>` — Optional per-artifact content/template " +
      "format (e.g. `mustache`, `jinja`). Use dotted prompt names for pre-role " +
      "variants, e.g. `asset-deep-search.fallback`. Emission-only — rejected " +
      "when `@execute` is present or `role:` is absent. `as:` is reserved for " +
      "execution-result bindings.\n\n" +
      "**Example (pipeline):**\n```\n@execute reflection\n\n" +
      "@prompt generate\n  Generate 3 candidate approaches.\n\n" +
      "@prompt evaluate role: system\n  You are a strict evaluator.\n```\n\n" +
      "**Example (emission):**\n```\n@prompt intro role: system\n  You are a precise assistant.\n\n" +
      "@prompt request role: user\n  Summarize: @{input}\n```\n\n" +
      "**Example (variant + format):**\n```\n" +
      "@prompt asset-deep-search role: system format: mustache\n  You are searching for {{asset}}.\n\n" +
      "@prompt asset-deep-search.fallback role: system\n  Simpler instructions.\n```\n" +
      "Produces `asset-deep-search.system.mustache.md` and `asset-deep-search.fallback.system.md`.",
    snippet: "@prompt ${1:name}\n  ${2:prompt content}",
    params: {
      role: ["system", "user", "assistant", "tool"],
      format: ["markdown", "json", "mustache", "jinja"],
    },
    category: "Execution",
  },
  emit: {
    label: "@emit",
    detail: "Emit a composed block to an explicit file path",
    documentation:
      "Compiles the following block or top-level segment into a separate output file and removes it from the primary prompt.\n\n" +
      "For role-tagged chat-message artifacts, prefer `@prompt name role: r` " +
      "(plus optional prompt `format:`, without `@execute`) — the compiler infers the file name as " +
      "`<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`.\n\n" +
      "**Parameters:**\n" +
      "- `file: <relative-path>` — Output file path. `@emit` supports only `file` for now.\n\n" +
      "**Example:**\n```\n@emit file: system.md\n  You are a precise assistant.\n\n" +
      "@emit file: user.md\n  Summarize: @{input}\n```",
    snippet: "@emit file: ${1:path/to/prompt.md}\n  ${2:prompt content}",
    params: {},
    category: "Output",
  },
  output: {
    label: "@output",
    detail: "Declare a prompt's text or image output contract",
    documentation:
      "Declares the production contract for the current prompt scope. A text contract can constrain format or enforcement; an image contract controls generation and optional persistence.\n\n" +
      "**Parameters:**\n" +
      "- `type: text|image` — Output modality (default: `text`)\n" +
      "- `format:` / `enforce:` — Text-output requirements\n" +
      "- `size:` / `quality:` / `model:` / `n:` / `edit:` — Image-generation settings\n" +
      "- `file: <relative-path>` — Persist the produced artifact\n\n" +
      "**Examples:**\n```\n@output type: text format: json enforce: strict file: answer.json\n\n@output type: image size: 1536x1024 quality: high file: cover.png\n```",
    snippet:
      "@output type: ${1|text,image|} file: ${2:output.md}",
    params: {
      type: ["text", "image"],
      format: ["markdown", "json", "mustache", "jinja"],
      enforce: ["strict", "soft"],
      size: null,
      quality: ["low", "medium", "high", "auto"],
      model: null,
      n: null,
      edit: ["on", "off", "true", "false"],
      file: null,
    },
    category: "Output",
  },
  package: {
    label: "@package",
    detail: "Render or convert an execution artifact",
    documentation:
      "Declares a deterministic packaging step after execution. Supply `file:` plus exactly one source: `template:` to render from execution artifacts, or `from:` to convert an existing output.\n\n" +
      "**Examples:**\n```\n@package template: book-template.weavemark.md file: book.html\n@package from: book.html file: book.pdf\n```",
    snippet:
      "@package ${1|template,from|}: ${2:source} file: ${3:output.html}",
    params: { template: null, from: null, file: null },
    category: "Output",
  },
  execute: {
    label: "@execute",
    detail: "Declare the execution strategy",
    documentation:
      "Specifies how the prompt should be executed by the LLM. This is metadata — " +
      "it does not change the prompt text, but tells the runtime which strategy to use.\n\n" +
      "**Strategies:**\n" +
      "- `single-call` — One LLM call (default)\n" +
      "- `self-consistency` — Multiple samples, majority vote\n" +
      "- `tree-of-thought` — Full BFS/DFS Tree of Thought (Yao et al. 2023)\n" +
      "- `simplified-tree-of-thought` — Lightweight generate → evaluate → synthesise\n" +
      "- `reflection` — Generate → Critique → Revise loop\n" +
      "- `chain` — Run named prompt stages sequentially with `@{previous}` context\n" +
      "- `collaborative` — LLM generates → human edits → LLM continues\n" +
      "- `fslm` — Run an ellements finite-state linguistic machine with WeaveMark-backed NL guards, invariants, actions, and outputs\n" +
      "- `weave` — Execute effectful semantic functions as a data-flow graph or sequential pipeline\n\n" +
      "**FSLM-specific parameters:**\n" +
      "- `machine: <path-or-module>` — YAML, JSON, Python, or module reference for the machine\n" +
      "- `initial_event: <type>` — First event type when no runtime event object is supplied\n" +
      "- `max_steps: <number>` — Maximum machine steps\n" +
      "- `prompt_contract: strict` — Fail before execution if required prompts are missing\n\n" +
      "**Weave-specific parameters:**\n" +
      "- `scheduler: sequential|graph|graph-strict` — Execution order for weave nodes\n" +
      "  - `sequential` — Run nodes top-to-bottom in source order\n" +
      "  - `graph` — Topological sort based on `uses:` dependencies; unrelated nodes may run in parallel\n" +
      "  - `graph-strict` — Same as `graph` but treats undeclared `uses:` as an error\n\n" +
      "**Common parameters:**\n" +
      "- `mode: minimal|full`\n" +
      "- `depth: <number>` — Iteration depth\n" +
      "- `branching_factor: <number>` — Branches for tree-of-thought\n" +
      "- `samples: <number>` — Sample count for self-consistency\n" +
      "- `max_rounds: <number>` — Edit rounds for collaborative\n\n" +
      "**Example (FSLM):**\n```\n@execute fslm\n  machine: support-triage.fslm.yaml\n  initial_event: user_message\n```\n\n" +
      "**Example (weave):**\n```\n@execute weave\n  scheduler: graph\n```\n\n" +
      "**Example (reflection):**\n```\n@execute reflection\n  depth: 2\n```",
    snippet: "@execute ${1|single-call,self-consistency,tree-of-thought,simplified-tree-of-thought,reflection,chain,collaborative,fslm,weave|}",
    params: {
      mode: ["minimal", "full"],
      scheduler: ["sequential", "graph", "graph-strict"],
      repeat: null,
      count: null,
      rounds: null,
      max_rounds: null,
      branching_factor: null,
      samples: null,
      machine: null,
      max_steps: null,
      prompt_contract: ["strict"],
    },
    category: "Execution",
  },
  machine: {
    label: "@machine",
    detail: "Declare an inline FSLM machine",
    documentation:
      "Available after explicitly importing `weavemark.experimental.fslm`. Declares an inline finite-state linguistic machine that lowers into `@execute fslm` metadata.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: machine name\n" +
      "- `initial: <state>` — Initial state\n" +
      "- `version: <text>` — Optional machine version\n\n" +
      "**Example:**\n```\n@machine support_triage initial: triage\n  @state triage\n    ...\n```",
    snippet: "@machine ${1:name} initial: ${2:initial_state}\n  ${3:Machine description.}",
    params: { initial: null, version: null },
    category: "FSLM",
  },
  state: {
    label: "@state",
    detail: "Declare a state inside @machine",
    documentation:
      "Declares a state. The body describes what is true in that state and may contain `@transition` blocks.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: state name\n" +
      "- `terminal: true|false` — Whether this state ends execution\n\n" +
      "**Example:**\n```\n@state drafting\n  The machine has a draft answer.\n```",
    snippet: "@state ${1:name}\n  ${2:State objective.}",
    params: { terminal: ["true", "false"] },
    category: "FSLM",
  },
  transition: {
    label: "@transition",
    detail: "Declare an FSLM transition",
    documentation:
      "Declares an event-driven transition. `internal:` and `external:` are preserved as host-facing metadata; WeaveMark does not currently synthesize autonomous transition events. Guards remain authoritative when an event selects candidates.\n\n" +
      "**Parameters:**\n" +
      "- First positional argument: transition name\n" +
      "- `target:` or `to:` — Target state\n" +
      "- `event:` — Event type (defaults to the transition name)\n" +
      "- `internal: true|false` — Runner may choose this transition\n" +
      "- `external: true|false` — Host/user/environment may trigger this transition\n\n" +
      "**Example:**\n```\n@transition deliver_answer target: answered internal: true external: false\n  @input text\n    Final answer text.\n  @guard answer_is_good\n    The answer is grounded and safe.\n  @action send_answer tool: send_message\n    Send the answer.\n```",
    snippet: "@transition ${1:name} target: ${2:target_state} internal: ${3|true,false|} external: ${4|false,true|}\n  ${5:Transition description.}",
    params: { event: null, target: null, to: null, internal: ["true", "false"], external: ["true", "false"], weight: null },
    category: "FSLM",
  },
  input: {
    label: "@input",
    detail: "Declare transition input",
    documentation:
      "Declares one input the autonomous runner may provide when choosing a transition. Tool actions receive matching input names automatically when their tool schema has matching parameters.\n\n" +
      "**Example:**\n```\n@input query\n  Search query.\n```",
    snippet: "@input ${1:name}\n  ${2:Input description.}",
    params: { default: null, required: ["true", "false"] },
    category: "FSLM",
  },
  guard: {
    label: "@guard",
    detail: "Declare transition guard",
    documentation:
      "Declares a guard. The guard body is shown to the autonomous runner as choice guidance and then evaluated as the authoritative transition validation rule.\n\n" +
      "**Example:**\n```\n@guard answer_is_good\n  The answer is grounded, complete, and safe.\n```",
    snippet: "@guard ${1:name}\n  ${2:Guard rule.}",
    params: { kind: ["nl", "deterministic"], ref: null, prompt_key: null, min_confidence: null },
    category: "FSLM",
  },
  action: {
    label: "@action",
    detail: "Declare transition action",
    documentation:
      "Declares an action that runs after guards pass. Multiple actions are allowed and run top-to-bottom. `tool:` creates a concrete tool action; without `tool:`, the action is prompt-backed.\n\n" +
      "**Example:**\n```\n@action send_answer tool: send_message\n  Send the final answer.\n```",
    snippet: "@action ${1:name}\n  ${2:Action instruction.}",
    params: { tool: null, ref: null, kind: ["nl", "tool", "deterministic"], prompt_key: null, optional: ["true", "false"] },
    category: "FSLM",
  },

  // ── Tools ─────────────────────────────────────────────────────
  tool: {
    label: "@tool",
    detail: "Define a callable tool/function for the LLM",
    documentation:
      "Declares a function that the LLM can invoke. Parameters are listed as indented items.\n\n" +
      "**Parameter syntax:** `- name: type (required|optional) — description`\n\n" +
      "**Example:**\n```\n@tool search_web\n  Search the web for information.\n  - query: string (required) — The search query\n  - max_results: integer (optional) — Maximum results to return\n```",
    snippet: "@tool ${1:function_name}\n  ${2:Description of the tool.}\n  - ${3:param}: ${4:string} (${5|required,optional|}) — ${6:description}",
    params: {},
    category: "Tools",
  },

  // ── Meta & Debug ──────────────────────────────────────────────
  note: {
    label: "@note",
    detail: "Comment block (stripped before LLM sees the prompt)",
    documentation:
      "A documentation/comment block. Everything indented under `@note` is removed during composition " +
      "and never sent to the LLM.\n\n" +
      "**Example:**\n```\n@note\n  This section was added to clarify issue #42.\n  Revisit after the next launch.\n```",
    snippet: "@note\n  ${1:comment}",
    params: {},
    category: "Meta",
  },

  // ── Verbatim Injection ────────────────────────────────────────
  embed: {
    label: "@embed",
    detail: "Inject content verbatim (no processing) in a fenced block",
    documentation:
      "Inserts content **as-is** inside a fenced block — no directive or variable processing. " +
      "Can load from a file or use an inline block. Rich document formats (PDF, DOCX, PPTX, XLSX) " +
      "are automatically converted to Markdown via markitdown.\n\n" +
      "**Parameters:**\n" +
      "- `file: <path>` — Load content from an external file\n" +
      "- `lang: <language>` — Language hint for the fenced block (e.g., `python`, `json`)\n" +
      "- `label: \"<text>\"` — Caption placed before the block\n" +
      "- `indent: true|false` — Indent the block for visual clarity (default: `true`)\n\n" +
      "**Examples:**\n```\n@embed file: samples/data.json lang: json label: \"Sample input\"\n\n" +
      "@embed lang: python\n  def greet(name):\n      return f\"Hello, {name}!\"\n```",
    snippet: "@embed file: ${1:path/to/file}",
    params: {
      file: null,
      lang: null,
      label: null,
      indent: ["true", "false"],
    },
    category: "Verbatim",
  },
  concise: {
    label: "@concise",
    detail: "Present content concisely (default prelude macro)",
    documentation:
      "A default-imported presentation macro that asks for concise wording while preserving the selected content's substantive requirements.\n\n**Example:**\n```\n@concise\n  Draft the operational plan.\n```",
    snippet: "@concise\n  ${1:content}",
    params: {},
    category: "Presentation",
  },
};

// Debug query pseudo-directives
const DEBUG_DIRECTIVES = {
  "directives?": {
    label: "@directives?",
    detail: "Debug: list all recognised directives",
    documentation: "Outputs a list of all directives the composition engine recognises. Useful for debugging.",
    snippet: "@directives?",
    category: "Debug",
  },
  "vars?": {
    label: "@vars?",
    detail: "Debug: list available and missing variables",
    documentation: "Shows which `@{variables}` are defined and which are still unresolved. Useful for debugging.",
    snippet: "@vars?",
    category: "Debug",
  },
  "structure?": {
    label: "@structure?",
    detail: "Debug: describe the prompt's structure",
    documentation: "Outputs an outline of the prompt's current structure after composition. Useful for debugging.",
    snippet: "@structure?",
    category: "Debug",
  },
};

// Execution strategy names (valid values for @execute)
const EXECUTION_STRATEGIES = ["single-call", "self-consistency", "tree-of-thought", "simplified-tree-of-thought", "reflection", "chain", "collaborative", "fslm", "weave"];

const IMPORT_CLAUSES = ["exposing", "as"];

const STANDARD_DEFINITIONS = [
  "refine",
  "ask",
  "iterate",
  "assert",
  "inspect",
  "style",
  "polish",
  "normalize",
  "revise",
  "expand",
  "summarize",
  "compress",
  "extract",
  "generate_examples",
  "example",
  "structural_constraints",
  "concise",
];

// Set of all known directive names (for diagnostics)
const ALL_DIRECTIVE_NAMES = new Set([
  ...Object.keys(DIRECTIVES),
  ...Object.keys(DEBUG_DIRECTIVES),
]);

module.exports = {
  DIRECTIVES,
  DEBUG_DIRECTIVES,
  EXECUTION_STRATEGIES,
  IMPORT_CLAUSES,
  STANDARD_DEFINITIONS,
  ALL_DIRECTIVE_NAMES,
};
