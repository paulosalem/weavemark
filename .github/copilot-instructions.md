# Copilot Instructions — WeaveMark

## Project Overview

WeaveMark is a prompt notation (**WeaveMark**) and toolchain for composing, executing, and benchmarking LLM prompting strategies. It includes:
- `src/weavemark/` — Core library (controller, parser, composition)
- `promplets/` — WeaveMark files (`.weavemark.md`) for various strategies
- `examples/benchmark-runners/strategy-comparison/runner.py` — Benchmark runner using lm-eval
- `vscode-extension/` — VS Code language support
- Depends on public `ellements` packages for LLM client, execution strategies, benchmarking helpers, and shared CLI presentation

## UI/UX Design Directive

- Whenever implementing a UI (graphical or textual), always aim for the most beautiful, most gorgeous, most wonderful option that still remains elegant, sleek, and highly functional.

## Browser GUI Validation Directive

- For any browser-based GUI change, run a thorough live evaluation via Playwright MCP whenever it is available before considering the work complete.
- Before Playwright validation, ensure the required LLM API keys are loaded from the user's local environment so live agent behavior can be tested end-to-end.

## LLM API Keys Are Available — Load Them Before Live Runs

**IMPORTANT — do not forget this.** The user's `OPENAI_API_KEY` (and other LLM provider keys) ARE available on this machine, exported from `~/.zshenv` and `~/.zshrc`. They are NOT inherited by non-interactive `bash -c '...'` invocations by default, which is why a fresh shell appears keyless. **Never claim "no API key available" without first trying to source them.**

To load the keys for any LLM-touching command (compose `--run`, `--scan` is fine without), prefix the command with:

```bash
source ~/.zshenv 2>/dev/null; source ~/.zshrc 2>/dev/null; <your command>
```

Or, equivalently, invoke an interactive login shell: `bash -lc 'source ~/.zshrc; <cmd>'`.

Quick check that the key is loaded:

```bash
source ~/.zshenv 2>/dev/null; [ -n "$OPENAI_API_KEY" ] && echo "key loaded" || echo "NO KEY"
```

Apply this routine for: `weavemark --run`, `weavemark --batch-only` (when the spec triggers LLM composition), benchmark scripts, Playwright agent tests, and any other end-to-end validation.

## Rule Synchronization Directive

- `AGENTS.md` is the canonical repository instruction file. `CLAUDE.md` imports
  it with `@AGENTS.md`.
- Whenever updating either Copilot instruction files or `AGENTS.md`, always
  update the counterpart file(s) as part of the same change so behavior rules
  stay synchronized across assistants.

## Reference authority

- `src/weavemark/prompts/weavemark.system.md` is authoritative for the WeaveMark
  language and semantic compilation contract.
- `docs/weavemark.ebnf` is derived from and must mirror the system prompt.
- The CLI parsers, public Python package exports/signatures, typed settings, and
  engine registries are authoritative for their respective executable surfaces.
- README, site pages, tutorials, examples, editor metadata, and prose tables are
  downstream documentation. Never change the language to match downstream docs;
  update downstream material from the relevant authority.

## HTML Documentation Syntax Highlighting

- In HTML documentation under `docs/`, every code snippet that shows WeaveMark
  source must use the shared syntax classes from `docs/site.css`: at minimum
  `syntax-directive` for directives such as `@refine`, `syntax-var` for
  `@{variables}`, `syntax-key` for directive parameters, and `syntax-string` for
  quoted WeaveMark values. Do not add uncolored WeaveMark snippets to HTML docs.

## Documentation Example Fidelity

- Every promplet shown in documentation (README, `docs/*.html`, `docs/*.md`)
  MUST correspond to a real, checked-in promplet that has actually been run and
  tested in the repo — never an invented, aspirational, or untested snippet.
- Abridging a real spec for display is fine (trim sections, elide `@refine`
  lines, shorten prose), but the abridged version must be a faithful reduction
  of an existing file under `promplets/` (or `outputs/examples/...` for compiled
  snapshots). Do not show directives, parameters, or file names that no live
  spec uses.
- Tutorials whose primary spec is not otherwise catalogued keep their canonical,
  tested copy under `promplets/tutorials/`, and the tutorial page links to it so
  readers can run the exact spec.
- Compiled-output examples must be copied from a real
  `outputs/examples/compiled-prompt-snapshots/...` artifact, not hand-written.
- When you add or change a documentation example, verify the corresponding spec
  still scans/compiles (`weavemark <file> --scan`, or a full run where feasible)
  before publishing the doc change.

## Example Script Principles

- Treat example `run.sh` scripts as inspectable command transcripts, not product CLIs. Their purpose is to show the core `weavemark` invocation directly.
- Keep runnable example folders self-contained: `examples/<category>/<example>/run.*`, `inputs/`, and `outputs/`. Categories include `terminal-output-only/`, `saved-artifact-workflows/`, `batch-example-runs/`, `python-runtime-integrations/`, `interactive-ui-and-handoff-demos/`, and `benchmark-runners/`.
- Keep example runner parameters hardcoded in the visible script body. Do not add `usage()` functions, argument parsing, demo selectors, `--compile` modes, or wrapper-specific options.
- The `weavemark` tool owns CLI usage. If a user needs options, point them to `weavemark --help` or the documentation instead of reimplementing help in example scripts.
- Keep shared shell support minimal. A tiny environment helper such as `examples/_lib/example-env.sh` is acceptable for cwd setup; presentation layers, command wrappers, and reusable runner frameworks are not.
- Prefer separate small scripts or clearly separated direct command blocks over parameterized shell runners when demonstrating variants.
- Example runners should create their local `outputs/` folders, but the important visible content should remain direct `promplet ...` commands with concise comments explaining what each command demonstrates.

## Collaborative / Interactive WeaveMark Workflows

- When running, testing, debugging, or automating `@execute collaborative` specs, use the `weavemark-collaborative-handoff` skill. It documents non-interactive smoke runs, filesystem agent handoff, response-file contracts, and the expected release artifacts.

## Language Definition Layout (three artifacts)

WeaveMark's language is defined across three coordinated files:

1. **`src/weavemark/prompts/weavemark.system.md`** — the **source of
   truth**: prose definition consumed by the LLM compiler at runtime,
   including per-directive ` ```promplet-schema ` blocks.
2. **`docs/weavemark.ebnf`** — deterministic mirror for offline tooling
   (structural validator, language servers, parser generators). Never
   sent to the LLM.
3. **Schema blocks inline in the prompt** — each directive section MAY
   carry a ` ```promplet-schema ` fenced block declaring its header
   surface (positional, params, flags, body-mode, optional LLM seam).

Keep them in sync via the `grammar-sync` skill:

- `python scripts/check_grammar_sync.py` — runs the deterministic check
- `python -m pytest tests/test_grammar_sync.py -q` — exercises both
  positive and negative cases
- Full skill instructions: `.github/prompts/grammar-sync.prompt.md` and
  `.claude/skills/grammar-sync/SKILL.md` (both share the same checker)

**Source-of-truth rule.** When prose and grammar disagree, fix the
grammar to match the prose — never the other way around — unless the
user has explicitly asked to change the prose based on the grammar.

## Architecture Rules

### Benchmark Runner — Event Loop Management

- **NEVER create one event loop per sample for strategy execution.** This was the root cause of cascading "Connection error" failures after ~12-15 samples. Accumulated aiohttp sessions in destroyed loops exhaust sockets/FDs.
- **Strategy path**: All samples run through a SINGLE event loop with `asyncio.Semaphore` for concurrency control. See `_run_all_strategy()` in `benchmark_strategies.py`.
- **Single-call path**: Uses `ThreadPoolExecutor` with sync `litellm.completion()` — no event loop needed.
- **Always clean up loops**: `shutdown_asyncgens()` → cancel pending → `loop.close()` → `gc.collect()`.

### WeaveMark Composition

- **Root text cascading**: Text before the first `@prompt` (prefix) and after the last `@prompt` (suffix) is prepended/appended to each named sub-prompt **by default for pipeline specs** (those with `@execute`). For emission specs (role-tagged `@prompt` blocks without `@execute`), the prefix/suffix are NOT cascaded by default. Override either default with `@compile context: cascade|local`; `auto` keeps the inferred default. The `@execute` block is stripped from the prefix. Other directives (`@refine`, `@output_format`, etc.) are preserved.
- **`@prompt` disposition**: A spec with top-level `@execute` makes every `@prompt` block a pipeline stage in `<prompts>`. A spec without `@execute` where every `@prompt` block declares `role:` becomes artifact emission: each block is written to `<emits>` as `<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`, with extensions resolved through `weavemark.json` format mappings. A spec without `@execute` and without any `role:` keeps blocks in `<prompts>` for `@refine` consumption. Mixing role-tagged and role-less `@prompt` blocks without `@execute` is an error.
- **`@prompt` parameter rules**: `role:` accepts only `system|user|assistant|tool` (case-insensitive, normalized lowercase). Optional `format:` is a configured format identifier, e.g. `mustache`; when it differs from `@compile format`, its configured extension is inserted before the outer extension. Use dotted prompt names for pre-role variants, e.g. `@prompt asset-deep-search.fallback role: system`. `format:` is rejected when `@execute` is present or when no `role:` is declared. `as:` is reserved for semantic-function result bindings. Emit filenames must be unique case-insensitively across all `@prompt` and `@emit` targets.
- **`@note` blocks** are stripped during composition — they're for prompt engineers, not the LLM.
- **`@refine` compatibility**: A spec with `@execute` can still be used as a `@refine` target. The parent spec's `@execute` takes precedence.

### Spec File Conventions

- **One spec per strategy**: Don't create separate "baseline" and "reusable" versions. A single spec serves both roles (standalone + `@refine` target).
- **Specs must align with literature**: Each spec should have a `@note` block citing the original paper. Prompts should reflect the canonical technique, not arbitrary variants.
- **`@{problem}`**: Always include the problem placeholder in specs that need per-sample substitution. Mustache syntax (`{{...}}`) is literal template content, not WeaveMark variable syntax.

### Strategy Integration

- Strategies come from `ellements.execution` (via the `BUILTIN_STRATEGIES` registry); WeaveMark wraps them in thin engine adapters under `promplet.engines.*`
- The `@execute` directive maps to strategy types: `single-call`, `self-consistency`, `tree-of-thought`, `simplified-tree-of-thought`, `reflection`
- `tree-of-thought` = full BFS/DFS algorithm (canonical Yao et al. 2023, expensive ~90 calls/problem)
- `simplified-tree-of-thought` = generate→evaluate→synthesize (~5 calls/problem, used in benchmark demos)
- Strategy configs (branching_factor, samples, temperature, max_depth, beam_width, search_type) go in the `@execute` block as indented key-value params

## Critical Patterns

### Concurrency in Benchmarks

```python
# BAD — one loop per sample, connections leak
for sample in samples:
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(strategy.execute(...))
    loop.close()

# GOOD — single loop, semaphore concurrency
async def _run_all():
    sem = asyncio.Semaphore(2)
    async def process(idx, req):
        async with sem:
            return await strategy.execute(...)
    return await asyncio.gather(*[process(i, r) for i, r in enumerate(requests)])

loop = asyncio.new_event_loop()
results = loop.run_until_complete(_run_all())
```

### LiteLLM LoggingWorker Reset

When switching from composition phase (uses `asyncio.run()`) to benchmark phase (new event loops), disable the LiteLLM async logging worker to prevent stale Queue errors:

```python
import litellm.litellm_core_utils.logging_worker as _lw
_lw.LoggingWorker.start = lambda self: None
_lw.LoggingWorker.enqueue = lambda self, *a, **kw: None
```

## Test Commands

```bash
# Full test suite
python -m pytest tests/ -q

# Expected: ~94 passed, ~105 skipped (skips are integration tests needing API keys)
```

## Key Files

- `src/weavemark/controller.py` — Composition engine, root text cascading (`_extract_root_text`, `_cascade_root_context`)
- `examples/benchmark-runners/strategy-comparison/runner.py` — Benchmark runner (single event loop for strategies)
- `promplets/stdlib/fragments/reasoning/chain-of-thought.weavemark.md` — CoT spec (also serves as @refine target)
- `promplets/catalog/executable/self-consistency-solver.weavemark.md` — SC spec
- `promplets/catalog/executable/tree-of-thought-solver.weavemark.md` — ToT spec (parallel independent paths)
- `examples/benchmark-runners/strategy-comparison/run.sh` — Demo script for running benchmarks
