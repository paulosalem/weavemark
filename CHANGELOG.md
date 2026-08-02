# Changelog

## Unreleased

### Added

- `weavemark library NAME --replay` discovers a bundled strict-offline
  recording, restores its synthetic inputs and recorded model, validates
  compilation, and can restore retained final-run artifacts. Market Snapshot
  replay reproduces its executed report, trace, and standalone HTML dashboard
  without provider credentials or network access.
- Public VALE3 Market Snapshot and AI Kanban replay bundles, a 1200x630 social
  preview, and site discovery files (`robots.txt`, `sitemap.xml`, and
  `llms.txt`).
- Lightweight Python 3.11-3.13 package smoke jobs cover installation, scanning,
  library discovery, and offline replay.

### Changed

- Console startup now defers the LLM runtime for package import, version output,
  and library management; informational, structural, and replay commands use
  LiteLLM's bundled pricing map without an import-time network fetch.
- The documentation home page preserves its hero and principles-led structure
  while adding one compact replay card, original-run telemetry, and a hidden
  one-minute-video slot.
- Strict replay now reports recorded input, cached-input, output-token, and API
  cost statistics in verbose output.
- Documentation retains consent-first Google Analytics, and GitHub Actions use
  immutable commit references.

### Fixed

- The semantic compiler's package contract consistently requires
  `instructions`/body or `from`, never the obsolete `template` field.
- CLI help and Python API examples now reference maintained, runnable promplets.
- Public API and runtime exceptions share one `WeaveMarkError` hierarchy.
- Edited bound Python helpers reload in long-lived processes, and discovery
  reports one actionable provider error instead of repeated LiteLLM banners.

## 0.9.2 - 2026-07-31

### Added

- Reusable static-browser, file-backed application, browser SQLite, mobile-first
  feed, static content-pack, AI-handoff, and knowledge-card curriculum promplets.
- A backend-free AI Kanban application whose canonical workspace is a
  user-selected SQLite file, with provider-neutral AI handoffs and conflict-safe
  persistence.
- A mobile-first Knowledge Cards application with four reviewed 50-card packs,
  offline/local state, notes, saved cards, deterministic ordering, and explicit
  attention safeguards.
- A lightweight live reader for the generated twelve-page Orion storybook.
- Accessible collapsible mobile navigation shared by the documentation site,
  tutorial track, and in-page section menus.
- Reusable `adaptive_workspace_shell` and `focus_preserving_inspection` modules
  now define state-aware setup-to-workspace transitions, compact sticky
  navigation, accessible drawers, entity-owned disclosures, anchored contextual
  overlays, asynchronous inspection, and reversible synthesis focus layouts.
- Chain execution can now repeat a stage over a JSON array or object with
  `items:`, exposing `@{item}` and `@{item_key}` per iteration. Image stages can
  use `edit_from: first` or `edit_from: <stage>:first` to condition an entire
  generated visual family on one fixed prototype.
- Run statistics now report provider-reported input/output token counts and cost
  alongside the existing composition and execution figures, covering the whole
  invocation rather than a single call.
- Run statistics now report the number of input tokens served from the provider's
  prompt cache as their own `Tokens cached` entry, as in
  `Tokens cached  113,536 (98%)`. Both OpenAI's nested
  `prompt_tokens_details.cached_tokens` and Anthropic's top-level
  `cache_read_input_tokens` are recognised. The entry is omitted when nothing was
  cached, so cold runs show no distracting zero.
- GPT-5.6 family models (`gpt-5.6`, `gpt-5.6-sol`, `gpt-5.6-terra`,
  `gpt-5.6-luna`) can now be selected with `--model`. Those models reject
  function tools combined with any reasoning effort on `/v1/chat/completions`,
  so WeaveMark routes them through OpenAI's Responses API and emits its compiler
  tool definitions in that API's flat schema. Earlier models are unaffected.
  `WEAVEMARK_RESPONSES_API=1` forces that route for any other model with the
  same constraint; `WEAVEMARK_RESPONSES_API=0` forces it off. Calls on that
  route request `high` reasoning effort, overridable with
  `WEAVEMARK_REASONING_EFFORT`, because the route otherwise pins effort to a
  level at which compilation copies `@output` requirements into the deliverable
  instead of applying them.

### Changed

- Reframed the README and homepage around three complete proof paths: illustrated
  storybook, AI Kanban, and the VALE3 market report.
- Replaced the passive-income/Orbital Drift implementation tutorial with the
  browser-native AI Kanban source-to-app walkthrough.
- Clarified `@effect` read/write access modes in the language authority and
  public reference.
- Made the analytics consent request a quiet nonmodal banner.
- Curated the public catalog to nine distinct, validated entrypoints and the
  public examples to eight focused projects.
- Moved reasoning-engine benchmarks and contrastive mining into self-contained
  runtime studies; moved `@emit` and reference-context fixtures into tutorials.
- The default text model is now `gpt-5.6-terra`, replacing `gpt-5.5`. Terra
  costs exactly half as much per token, and every shipped example was rerun on
  it end to end: the market snapshot came in at $0.34 against $0.74, the
  recurring topic monitor at $0.95 against $1.08 while returning more findings,
  and the illustrated books, comic, financial plan, collaborative writer, and
  refactoring pipeline all produced deliverables at least as good as before.
  `--model gpt-5.5` still selects the previous default.
- The verbose run footer is now printed once, after packaging, so its tokens,
  cost, and elapsed time cover every model call the invocation made, including
  semantic `@package` application.
- The bundled market snapshot is fully variable-driven: its packaged deliverable
  is `market-dashboard.html` and its title, security identification, and
  research character follow the supplied ticker variables.

### Removed

- Redundant catalog wrappers, unimplemented product specifications, duplicate
  finance/research examples, broad batch runners, and artifact-free terminal
  examples.
- Example-study reports whose source projects were removed from the curated
  public surface.

### Fixed

- Prevented save races, cross-workspace writes, hidden-state leaks, corrupt-file
  dead ends, misleading fallback copy, and mobile action overlap in AI Kanban.
- Removed nested vertical scrolling from Knowledge Cards, made the document the
  single scroll owner, and hardened progress, mutation, source, connection, and
  content-validation behavior.
- Restored direct local demo links while preserving GitHub Pages demo routes.
- Replaced undiscoverable narrow-screen horizontal navigation with explicit
  disclosure menus.
- The collaborative engine now writes repository-relative response paths into its
  agent-turn requests when the run happens inside the current working directory.
  It previously wrote absolute paths, so every committed transcript recorded the
  author's own directory layout.
- A `single-call` promplet can now actually spend the tool budget it advertises.
  `max_iterations` bounded model round trips independently of `max_tool_calls`,
  so a promplet offering thirty calls while allowing twenty round trips could
  never reach its own budget: a model that took the offer at face value ran out
  of iterations and failed the run instead of finishing it, and one that stopped
  early passed only by being less thorough. The engine now raises the iteration
  ceiling to fit the declared tool budget, including the round trip that reports
  the budget as exhausted. Actual tool use is still bounded by `max_tool_calls`,
  and a larger `max_iterations` is left untouched.
- The recurring topic monitor example runs again. Its input files supplied
  `previous_reports` as an empty string, which counts as no value at all, so
  `run.sh` stopped with a missing-input error before reaching a provider even
  though the variable is only read when `use_previous_reports` is true.
- An escaped `@@` immediately after a word character, as in `admin@@example.com`,
  is no longer mistaken for a reference. The reference scanner now honours the
  escape before its "preceded by text" rule, so such addresses compile instead of
  failing with a spurious missing-fragment error.
- `@output` now rejects an unquoted multi-word format string instead of silently
  keeping only its first word. Quote the format or move it to an indented body.
- The prompt refactoring pipeline no longer leaks its own transformation
  requirements into the prompt it produces. It stated them in an `@output`
  block, but an `@output` body is appended to the composed prompt, so the
  refactorer received them as material to keep rather than as work to perform.
  Those requirements now live in the `@polish`, `@revise`, and `@normalize`
  instructions that carry them out. Its assertions check headings the deliverable
  must actually have instead of strings the composition always contained.

## 0.9.1 - 2026-07-20

### Added

- Semantic `@package instructions:` application with reusable and inline
  instruction composition, canonical `@{output}` context, and a reusable
  internal promplet-application runtime.
- Explicit `--open` support for opening successfully packaged artifacts after
  execution.
- Module-owned default `@bind` implementations. Importing a module selects its
  defaults as metadata, local bindings override them, and runtime protection
  remains authoritative before Python execution.
- A flagship VALE3 market-learning workflow with reusable finance capabilities,
  a grounded Markdown report, execution trace, and responsive standalone HTML
  dashboard.
- Consent-first GA4 documentation analytics with persistent preferences and
  advertising signals disabled.

### Changed

- Renamed the misleading semantic-package parameter from `template:` to
  `instructions:` as a clean language break.
- Replaced the executable tool-binding tutorial with an end-to-end market-report
  tutorial and promoted the market workflow into the home-page hero examples.
- Moved reusable market-research definitions and their reviewed default adapter
  into the finance domain module.

### Fixed

- Filtered unrelated market-search results and restricted official-context
  evidence to company-owned domains.
- Hardened generated dashboard instructions against narrow-viewport overflow
  and preserved evidence, currency, source, accessibility, print, and security
  constraints.
- Made CI/release validation install the declared example dependencies and
  validate maintained LFS images whether checkout content is hydrated or a
  pointer.

## 0.9.0 - 2026-07-19

### Added

- Markdown-native `<!-- ... -->` author comments, stripped before WeaveMark
  parsing while remaining literal inside inline and fenced code.
- Language 0.9 source references: block and inline `@reference`, Claude-style
  `@path` shorthand, compiler-only or retained context, recursive resolution,
  provenance metadata, and deterministic Reference Appendices.
- Tag-triggered PyPI Trusted Publishing and GitHub release automation, guarded
  by synchronized version and finalized-changelog validation.
- JSON, YAML, and YML input-variable files with strict object and duplicate-key
  validation.
- Repository-wide Markdown rendering and local-link hygiene checks.
- A safe, idempotent local installer for the bundled VS Code extension, with
  VS Code/Insiders/VSCodium detection, atomic copy or development-link modes,
  conflict protection, verification, and uninstall support.

### Changed

- The current WeaveMark language version is 0.9.
- Executable promplets now carry their normal engine semantics entirely in
  `@execute`; redundant catalog runtime sidecars were removed.
- Runtime config is reserved for explicit provider, policy, and host overrides.
  Promplet input data belongs in `--vars-file` or `--var`.
- The programming library now focuses on the maintained local-first
  TypeScript/Next.js/Prisma/SQLite stack. Unsupported Rust/Bevy, Android/Kotlin,
  PostgreSQL, and generic SaaS fragments and their niche catalog examples were
  removed.
- The passive-income software example is now a local-first planning dashboard.
- Added a news intelligence board that reuses the workflow-board module family
  for durable event memory and material-update deduplication.
- Removed unused generic writing and product-metaphor fragments while retaining
  the decision, teaching, release, game-design, and work-intelligence layers
  exercised by controlled studies.
- Moved the household financial-resilience lens into the finance domain and made
  the news board reuse the study-backed topic-intelligence monitor.
- Generalized notifications beyond their former finance-specific examples,
  added finance-safety boundaries to CompoundVision, and repaired controlled
  game-study sources that referenced removed programming fragments.
- The recurring news/events monitor now runs through the regular
  `weavemark ... --run` path. Its promplet owns query planning, source
  selection, crawling, ranking, deduplication, history comparison, and
  synthesis; Python is limited to thin search/news/crawl bindings.
- Single-call executables can now run matching `@tool`/`@bind` implementations
  natively with explicit iteration and total tool-call budgets.
- `@embed folder:` loads a bounded folder of Markdown reports, enabling
  `@summarize`-based memory for recurring workflows.
- Reflection-engine runtime values are no longer misclassified as missing user
  inputs during batch preflight.
- Compiler binding metadata is canonicalized across valid wire-name variants,
  and one bounded protocol-repair retry handles malformed semantic-compiler JSON.
- Markdown persistence normalizes trailing whitespace across CLI, Python, and
  collaborative example artifacts.

### Fixed

- Tutorial snippets no longer present Markdown `#` headings as WeaveMark
  comments.
- GitHub README rendering around Quickstart protections and command examples.
- Nested Markdown fences in generated execution traces.
- Ambiguous short names for public library targets and stale pre-module paths in
  catalog notes.
- Broken comic reference-image paths and Python examples that depended on a
  sibling source checkout instead of installed dependencies.
- Dashboard guidance now prioritizes decisions, evidence, freshness, quiet and
  attention states, and error/offline behavior rather than generic chart density.

## 0.8.0

WeaveMark 0.8 is the first unified processor, language, extension, and
provenance release.

### Added

- Optional compilation provenance manifests.
- Sensitive, explicit run recording and strict offline replay.
- Provider-reported token, latency, and cost aggregation.
- Typed diagnostics with stable codes and JSON rendering.
- Per-surface debug logging policy with binary omission, rotation, retention,
  and restrictive permissions.
- `weavemark --version` and `weavemark.__version__`.
- Experimental default-on promplet protection boundaries.

### Changed

- The current language version is 0.8.
- `CompositionResult` is now owned by the compilation result layer rather than
  the controller.
- Invalid variables files, output formats, runtime configuration, and numeric
  FSLM options fail explicitly instead of producing tracebacks or fallbacks.
- `lm-eval` moved from the core install to the `benchmarking` extra.
- Core and optional dependencies now have explicit compatible upper bounds.
- Full-resolution showcase PNG/PDF outputs moved to narrowly scoped Git LFS
  tracking; lightweight site previews remain in ordinary Git.
- Repository and distribution artifact/size gates reject generated dependency
  trees, caches, package binaries, oversized ordinary files, and leaked LFS
  pointers.

### Compatibility

Promplets declaring language version 0.7 remain supported. An omitted
`@promplet` declaration means “use the current processor language,” currently
0.8. See [Migrating to 0.8](docs/migrating-to-0.8.md).
