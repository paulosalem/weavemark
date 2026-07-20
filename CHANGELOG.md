# Changelog

## Unreleased

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
