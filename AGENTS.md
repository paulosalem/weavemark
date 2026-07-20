# Agent Instructions

## Project overview

WeaveMark is a prompt notation for composing, executing, and benchmarking LLM
prompting strategies. Core code lives under `src/weavemark/`. It depends on
public `ellements` packages for the LLM client, execution strategies,
benchmarking helpers, and shared CLI presentation.

## Instruction synchronization

`AGENTS.md` is the canonical repository instruction file. `CLAUDE.md` imports it
with `@AGENTS.md` and should remain a thin import file rather than duplicating
these rules.

Nested `AGENTS.md` files may add domain-specific instructions for their
subtrees.

## Repository-user welcome

The first assistant reply in a new conversation in this repository must briefly
welcome the person and establish their role before offering general help. When
their first message is ambiguous, including a greeting such as `hi`, reply with
this question:

> Welcome to WeaveMark. Are you here as a repository user who wants to try it,
> or as a maintainer working on the project?

Do not substitute a generic “What would you like to work on?” greeting for this
role question. Do not ask again once the person's role is known. If their first
message clearly establishes their role, acknowledge it and proceed directly.

- For a maintainer, follow the engineering instructions in this file.
- For a repository user, use the `weavemark-repository-user` skill before
  proposing, running, or customizing an example. The skill is mirrored at
  `.github/skills/weavemark-repository-user/SKILL.md` for Copilot CLI and
  `.claude/skills/weavemark-repository-user/SKILL.md` for Claude Code.

## Machine-local agent workspace

Temporary agent material must live outside this repository at:

```text
~/.weavemark/agent-workspace/weavemark/
```

Use these subdirectories:

- `reports/` - audits, reviews, investigation reports, and release assessments.
- `notes/` - working notes, plans, decision drafts, and handoff context.
- `artifacts/` - generated evidence or intermediate outputs that are useful
  locally but are not product deliverables.
- `tmp/` - disposable files. Clean these when the task ends.

The location may be overridden for automation with `WEAVEMARK_AGENT_WORKSPACE`,
but it must remain outside the repository.

## Repository hygiene

- Do not add agent plans, audit reports, scratch notes, session state, raw logs,
  or temporary evidence to this repository.
- Do not symlink the machine-local workspace into the repository.
- Do not copy material from the local workspace into the repository unless the
  user explicitly asks to promote it into product documentation or another
  tracked file.
- Do not store secrets in either the repository or the agent workspace.
- Product artifacts that are intentionally part of WeaveMark - source, tests,
  documentation, maintained examples, and explicitly curated outputs - belong in
  the repository. The local-workspace rule applies to agent process material, not
  to intentional project content.

## UI/UX design directive

- Whenever implementing a UI, graphical or textual, always aim for the most
  beautiful, most gorgeous, most wonderful option that remains elegant, sleek,
  and highly functional.

## Browser GUI validation directive

- For any browser-based GUI change, run a thorough live evaluation via Playwright
  MCP whenever it is available before considering the work complete.
- Before Playwright validation, ensure the required LLM API keys are loaded from
  the user's local environment so live agent behavior can be tested end-to-end.

## LLM API keys are available locally

The user's `OPENAI_API_KEY` and other LLM provider keys are available on this
machine, exported from the local shell environment. They are not inherited by
non-interactive `bash -c '...'` invocations by default. Never claim "no API key
available" without first trying to source the local environment.

For LLM-touching commands such as `weavemark --run`, `weavemark --batch-only`
when the spec triggers LLM composition, benchmark scripts, Playwright agent
tests, and other end-to-end validation, load the environment without printing
secrets:

```bash
zsh -lc 'source ~/.zshenv >/dev/null 2>&1; source ~/.zshrc >/dev/null 2>&1; <your command>'
```

`weavemark --scan` does not require model credentials.

## Reference authority

- `src/weavemark/prompts/weavemark.system.md` is authoritative for the WeaveMark
  language and semantic compilation contract.
- `docs/weavemark.ebnf` is derived from and must mirror the system prompt.
- The CLI parsers, public Python package exports/signatures, typed settings, and
  engine registries are authoritative for their respective executable surfaces.
- README, site pages, tutorials, examples, editor metadata, and prose tables are
  downstream documentation. Never change the language to match downstream docs;
  update downstream material from the relevant authority.

## HTML documentation syntax highlighting

- In HTML documentation under `docs/`, every code snippet that shows WeaveMark
  source must use the shared syntax classes from `docs/site.css`: at minimum
  `syntax-directive` for directives such as `@refine`, `syntax-var` for
  `@{variables}`, `syntax-key` for directive parameters, and `syntax-string` for
  quoted WeaveMark values. Do not add uncolored WeaveMark snippets to HTML docs.

## Documentation example fidelity

- Every promplet shown in documentation, including README, `docs/*.html`, and
  `docs/*.md`, must correspond to a real, checked-in promplet that has actually
  been run and tested in the repo. Never use an invented, aspirational, or
  untested snippet.
- Abridging a real spec for display is fine: trim sections, elide `@refine`
  lines, or shorten prose as needed. The abridged version must remain a faithful
  reduction of an existing file under `promplets/`, or
  `outputs/examples/...` for compiled snapshots. Do not show directives,
  parameters, or file names that no live spec uses.
- Tutorials whose primary spec is not otherwise catalogued keep their canonical,
  tested copy under `promplets/tutorials/`, and the tutorial page links to it so
  readers can run the exact spec.
- Compiled-output examples must be copied from a real
  `outputs/examples/compiled-prompt-snapshots/...` artifact, not hand-written.
- When you add or change a documentation example, verify the corresponding spec
  still scans or compiles with `weavemark <file> --scan`, or a full run where
  feasible, before publishing the doc change.

## Example script principles

- Treat example `run.sh` scripts as inspectable command transcripts, not product
  CLIs. Their purpose is to show the core `weavemark` invocation directly.
- Keep runnable example folders self-contained: `examples/<category>/<example>/run.*`,
  `inputs/`, and `outputs/`. Categories include `terminal-output-only/`,
  `saved-artifact-workflows/`, `batch-example-runs/`,
  `python-runtime-integrations/`, `interactive-ui-and-handoff-demos/`, and
  `benchmark-runners/`.
- Keep example runner parameters hardcoded in the visible script body. Do not add
  `usage()` functions, argument parsing, demo selectors, `--compile` modes, or
  wrapper-specific options.
- The `weavemark` tool owns CLI usage. If a user needs options, point them to
  `weavemark --help` or the documentation instead of reimplementing help in
  example scripts.
- Keep shared shell support minimal. A tiny environment helper such as
  `examples/_lib/example-env.sh` is acceptable for cwd setup; presentation
  layers, command wrappers, and reusable runner frameworks are not.
- Prefer separate small scripts or clearly separated direct command blocks over
  parameterized shell runners when demonstrating variants.
- Example runners should create their local `outputs/` folders, but the important
  visible content should remain direct `weavemark ...` commands with concise
  comments explaining what each command demonstrates.

## Collaborative / interactive WeaveMark workflows

- When running, testing, debugging, or automating `@execute collaborative` specs,
  use the `weavemark-collaborative-handoff` skill. It documents non-interactive
  smoke runs, filesystem agent handoff, response-file contracts, and expected
  release artifacts.

## Language definition layout

WeaveMark's language is defined across three coordinated artifacts:

1. `src/weavemark/prompts/weavemark.system.md` - the source of truth: prose
   definition consumed by the LLM compiler at runtime, including per-directive
   `promplet-schema` fenced blocks.
2. `docs/weavemark.ebnf` - deterministic mirror for offline tooling, structural
   validator, language servers, and parser generators. Never sent to the LLM.
3. Schema blocks inline in the prompt - each directive section may carry a
   `promplet-schema` fenced block declaring its header surface: positional,
   params, flags, body-mode, and optional LLM seam.

Keep them in sync via the `grammar-sync` skill:

```bash
python scripts/check_grammar_sync.py
python -m pytest tests/test_grammar_sync.py -q
```

Full skill instructions: `.claude/skills/grammar-sync/SKILL.md`

Source-of-truth rule: when prose and grammar disagree, fix the grammar to match
the prose - never the other way around - unless the user has explicitly asked to
change the prose based on the grammar.

## Critical engineering lessons

### Event loop and connection exhaustion

The benchmark runner originally created a new `asyncio` event loop per sample.
After about 12-15 samples, accumulated aiohttp sessions from destroyed loops
exhausted sockets/file descriptors and caused cascading "Connection error"
failures that looked like API issues.

Root cause chain:

1. Each sample created a new event loop and new aiohttp sessions for LiteLLM.
2. The loop was destroyed, but TCP connections lingered in `TIME_WAIT`.
3. After enough samples and calls, the socket limit was hit.
4. Subsequent connections failed and retry loops amplified the failure.

Solution: use one event loop for all strategy samples and an `asyncio.Semaphore`
for concurrency control. See `_run_all_strategy()` in
`examples/benchmark-runners/strategy-comparison/runner.py`.

### LiteLLM LoggingWorker across event loops

LiteLLM's async `LoggingWorker` creates an `asyncio.Queue` bound to the first
event loop. Composition may use `asyncio.run()`, creating and destroying a loop.
Benchmark phases that create new loops can then hit "Queue is bound to a
different event loop" errors.

Patch the worker between phases when needed:

```python
import litellm.litellm_core_utils.logging_worker as _lw

_lw.LoggingWorker.start = lambda self: None
```

### Strategy retry architecture

The internal `BaseStrategy._call_llm()` retries individual failed LLM calls. This
matters because:

- Tree-of-thought can make several LLM calls for generation, evaluation, and
  synthesis.
- Without per-call retry, one failed call causes the whole pipeline to fail and
  benchmark retries repeat all calls.
- With per-call retry, a transient failed call is retried with backoff and the
  pipeline can continue.

The benchmark runner has its own retry loop as a safety net, but engine-level
retry handles most transient failures.

### WeaveMark composition - root cascading and `@prompt` disposition

- Root text cascading: text before the first `@prompt` and after the last
  indented `@prompt` body is prepended/appended to each named block by default
  for pipeline specs that use `@execute`. For emission specs, role-tagged
  `@prompt` blocks without `@execute`, prefix/suffix are not cascaded by default.
  Override either default with `@compile context: cascade|local`; `auto` keeps
  the inferred default.
- `@prompt` disposition is inferred lexically:
  - Spec has top-level `@execute`: every `@prompt` block becomes a pipeline stage
    in `<prompts>`.
  - No `@execute`, every `@prompt` declares `role:`: each block is emitted to
    `<emits>` as `<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`,
    where extensions are resolved through `weavemark.json` format mappings.
  - No `@execute`, no `role:` on any `@prompt`: blocks stay in `<prompts>` for
    `@refine` consumption by a parent spec.
  - Mixing role-tagged and role-less `@prompt` blocks without `@execute` is an
    error.
- `@prompt` parameters: `role:` must be exactly one of
  `system|user|assistant|tool`, case-insensitive. Optional `format:` is a
  configured format identifier, such as `mustache`; when it differs from
  `@compile format`, its configured extension is inserted before the outer
  extension. Use dotted prompt names for pre-role variants, such as
  `@prompt asset-deep-search.fallback role: system`. `format:` is emission-only,
  rejected when `@execute` is present, and rejected without an accompanying
  `role:`. `as:` is reserved for semantic-function result bindings. Emit
  filenames are checked case-insensitively for collisions across all `@prompt`
  and `@emit` targets.
- The legacy `@message` directive has been removed. Use role-tagged `@prompt`
  instead. The compiler treats `@prompt name role: r` as the canonical artifact
  form when the spec has no `@execute`.

## Key files

- `src/weavemark/controller.py` - composition engine.
  - `_extract_root_text()` - extracts prefix/suffix for cascading.
  - `_cascade_root_context()` - injects root text into sub-prompts.
  - `compose()` - main composition entry point.
- `examples/benchmark-runners/strategy-comparison/runner.py` - benchmark runner.
  - `_run_all_strategy()` - single-loop strategy execution.
  - `_process_one_async()` - per-sample async processor with retry.
  - `create_benchmark_model()` - lm-eval adapter factory.
- `promplets/**/*.weavemark.md` - built-in promplets.

## Spec files

- WeaveMark variables use `@{name}`. Mustache syntax, such as `{{...}}`, is
  literal template content, not WeaveMark variable syntax.

| File | Strategy | Notes |
|------|----------|-------|
| `reasoning/chain-of-thought.weavemark.md` | single-call | Also used as `@refine` target by self-consistency. `@note` cites Wei et al. 2022 / Kojima et al. 2022 |
| `self-consistency-solver.weavemark.md` | self-consistency | `@note` cites Wang et al. 2022. Output format: number only |
| `tree-of-thought-solver.weavemark.md` | tree-of-thought | Full BFS/DFS algorithm (Yao et al. 2023). Step-level thought decomposition plus intermediate evaluation. Expensive, around 90 calls/problem |
| `simplified-tree-of-thought-solver.weavemark.md` | simplified-tree-of-thought | Generate, evaluate, and synthesize with complete solutions. Cheap, around 5 calls/problem. Used in benchmark demos |
| `reflection-solver.weavemark.md` | reflection | Generate, critique, and revise loop. `@note` cites Shinn et al. 2023 / Madaan et al. 2023 |

## Test commands

```bash
python -m pytest tests/ -q
```
