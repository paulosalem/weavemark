# CLAUDE.md — WeaveMark

## Project Overview

WeaveMark is a prompt notation (**WeaveMark**) for composing, executing, and benchmarking LLM prompting strategies. Core at `src/weavemark/`. It depends on public `ellements` packages for LLM client, execution strategies, benchmarking helpers, and shared CLI presentation.

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

- Whenever updating either `CLAUDE.md` or Copilot instruction files, always update the counterpart file(s) as part of the same change so behavior rules stay synchronized across assistants.

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
- Full skill instructions: `.claude/skills/grammar-sync/SKILL.md`

**Source-of-truth rule.** When prose and grammar disagree, fix the
grammar to match the prose — never the other way around — unless the
user has explicitly asked to change the prose based on the grammar.

## Critical Engineering Lessons

### Event Loop & Connection Exhaustion (MUST READ)

**Problem**: The benchmark runner originally created a new `asyncio` event loop per sample. After ~12-15 samples, accumulated aiohttp sessions (in TIME_WAIT TCP state) from destroyed loops exhausted sockets/FDs, causing cascading "Connection error" failures that looked like API issues but were actually local resource exhaustion.

**Root cause chain**:
1. Each sample → new event loop → new aiohttp sessions for litellm
2. Loop destroyed, but TCP connections linger in TIME_WAIT (~60s)
3. After ~12 samples × 5 calls/sample = ~60 connections, socket limit hit
4. All subsequent connections fail → retry loops make it worse (more connections)

**Solution**: Single event loop for all strategy samples. `asyncio.Semaphore` for concurrency control. See `_run_all_strategy()` in `examples/benchmark-runners/strategy-comparison/runner.py`.

### LiteLLM LoggingWorker Across Event Loops

LiteLLM's async LoggingWorker creates an `asyncio.Queue` bound to the first event loop. Composition phase uses `asyncio.run()` which creates and destroys a loop. The benchmark phase then creates new loops, causing "Queue is bound to a different event loop" errors.

**Fix**: Monkey-patch the worker between phases:
```python
import litellm.litellm_core_utils.logging_worker as _lw
_lw.LoggingWorker.start = lambda self: None
```

### Strategy Retry Architecture

The internal `BaseStrategy._call_llm()` retries individual failed LLM calls. This is crucial because:
- ToT has 5 LLM calls (3 generate + evaluate + synthesize)
- Without per-call retry: 1 failed call → entire pipeline fails → benchmark retries ALL 5 calls
- With per-call retry: 1 failed call → retried 3x with backoff → pipeline continues

The benchmark runner has its OWN retry loop (5 attempts) as a safety net, but the engine-level retry handles ~95% of transient failures.

### WeaveMark Composition — Root Cascading & `@prompt` Disposition

- **Root text cascading**: Text before the first `@prompt` (prefix) and after the last indented `@prompt` body (suffix) is prepended/appended to each named block **by default for pipeline specs** (those with `@execute`). For **emission specs** (role-tagged `@prompt` blocks without `@execute`), prefix/suffix are NOT cascaded by default. Override either default with `@compile context: cascade|local`; `auto` keeps the inferred default.
- **`@prompt` disposition is inferred lexically**:
  - Spec has top-level `@execute` → every `@prompt` block becomes a pipeline stage in `<prompts>`.
  - No `@execute`, every `@prompt` declares `role:` → each block is emitted to `<emits>` as `<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`, where extensions are resolved through `weavemark.json` format mappings.
  - No `@execute`, no `role:` on any `@prompt` → blocks stay in `<prompts>` for `@refine` consumption by a parent spec.
  - Mixing role-tagged and role-less `@prompt` blocks without `@execute` is an error.
- **`@prompt` parameters**: `role:` must be exactly one of `system|user|assistant|tool` (case-insensitive). Optional `format:` is a configured format identifier, e.g. `mustache`; when it differs from `@compile format`, its configured extension is inserted before the outer extension. Use dotted prompt names for pre-role variants, e.g. `@prompt asset-deep-search.fallback role: system`. `format:` is emission-only — rejected when `@execute` is present, and rejected without an accompanying `role:`. `as:` is reserved for semantic-function result bindings. Emit filenames are checked case-insensitively for collisions across all `@prompt` and `@emit` targets.
- The legacy `@message` directive has been removed — use role-tagged `@prompt` instead. The compiler treats `@prompt name role: r` as the canonical artifact form when the spec has no `@execute`.

## Key Files

- `src/weavemark/controller.py` — Composition engine
  - `_extract_root_text()` — Extracts prefix/suffix for cascading
  - `_cascade_root_context()` — Injects root text into sub-prompts
  - `compose()` — Main composition entry point
- `examples/benchmark-runners/strategy-comparison/runner.py` — Benchmark runner
  - `_run_all_strategy()` — Single-loop strategy execution
  - `_process_one_async()` — Per-sample async processor with retry
  - `create_benchmark_model()` — lm-eval adapter factory
- `promplets/**/*.weavemark.md` — Built-in promplets

## Spec Files

- WeaveMark variables use `@{name}`. Mustache syntax (`{{...}}`) is literal template content, not WeaveMark variable syntax.

| File | Strategy | Notes |
|------|----------|-------|
| `reasoning/chain-of-thought.weavemark.md` | single-call | Also used as `@refine` target by SC. `@note` citing Wei et al. 2022 / Kojima et al. 2022 |
| `self-consistency-solver.weavemark.md` | self-consistency | `@note` cites Wang et al. 2022. Output format: number only |
| `tree-of-thought-solver.weavemark.md` | tree-of-thought | Full BFS/DFS algorithm (Yao et al. 2023). Step-level thought decomposition + intermediate evaluation. Expensive (~90 calls/problem) |
| `simplified-tree-of-thought-solver.weavemark.md` | simplified-tree-of-thought | Generate → evaluate → synthesize with complete solutions. Cheap (~5 calls/problem). Used in benchmark demos |
| `reflection-solver.weavemark.md` | reflection | Generate → critique → revise loop. `@note` cites Shinn et al. 2023 / Madaan et al. 2023 |

## Test Commands

```bash
python -m pytest tests/ -q    # ~96 passed, ~105 skipped
```
