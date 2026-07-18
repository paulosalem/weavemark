# WeaveMark examples

This folder contains runnable examples and supporting inputs around the built-in
library in `../promplets/`. Runnable examples own their runner, inputs, and
outputs; examples with specific reusable source material may also own a small,
flat `promplets/` folder:

```text
examples/<category>/<example>/
  run.sh or run.py
  promplets/              # optional; no extra subdivision for a few local files
  inputs/
  outputs/
```

The category names set expectations:

- `terminal-output-only/` — one real-use `weavemark --verbose` command that
  shows processing progress and prints the composed prompt in the terminal.
- `saved-artifact-workflows/` — one richer workflow, often compile + execute,
  with saved artifacts under that example's `outputs/` folder.
- `batch-example-runs/` — curated batches that run many examples in sequence.
- `python-runtime-integrations/` — Python examples that pair WeaveMark programs
  with companion runtime components such as tool registries, finance APIs, web
  search, or crawl helpers.
- `interactive-ui-and-handoff-demos/` — TUI, discovery, and human/agent handoff
  demos.
- `benchmark-runners/` — benchmark runners.
- `executable-promplet-programs/` — supporting inputs for executable
  WeaveMark programs that are useful to inspect but do not currently need a
  dedicated runner.

Variable presets that support built-in catalog promplets directly live beside them as
`promplets/catalog/standalone/<name>.vars.json`. Compiled prompt snapshots that are useful for
inspection but are not owned by a runnable example live under
`outputs/examples/compiled-prompt-snapshots/`.

`_lib/example-env.sh` is the only shared helper; it just lets runners work from
any current directory.

## Reproducible setup

```bash
# Core examples.
pip install -e .

# Finance/web companion examples.
pip install -e ".[examples]"
playwright install chromium

# Strategy benchmark example (lm-eval is intentionally optional and heavy).
pip install -e ".[benchmarking]"
```

The strategy benchmark downloads and caches its tiny GSM8K slice on the first
run. After that, set `HF_DATASETS_OFFLINE=1` when you deliberately want a
cache-only run.

Set the provider credentials required by the model named in the visible runner
command. Every runner works from any current directory, uses default protections
without `--no-protections`, and writes only beneath its own `outputs/` folder.
Start with a no-cost structural check when evaluating a local setup:

```bash
weavemark promplets/catalog/standalone/program-review-checklist.weavemark.md --scan
```

### Runtime expectations

Costs and durations vary by provider and model. These bands are intentionally
qualitative rather than price promises:

| Example family | Provider/network | Typical time/cost shape | Expected result |
| --- | --- | --- | --- |
| `terminal-output-only/*` | One semantic compile | Short; usually one compiler tool loop | Composed prompt on stdout |
| `batch-example-runs/static-prompts` | Several semantic compiles | Medium; multiple independent prompts | Prompt files under local `outputs/` |
| `batch-example-runs/execution-engines` | Compile plus multi-call engines | Medium/high; strategy-dependent | Executed outputs and traces |
| `saved-artifact-workflows/comic-strip-en` and storybooks | Text plus image generation | High; multiple generated images | Images plus packaged HTML/PDF where available |
| `python-runtime-integrations/*` | Provider plus finance/search/crawl services | Medium/high; live external data | Tool records, traces, and synthesized brief |
| `benchmark-runners/strategy-comparison` | Repeated strategies plus lm-eval | High; intentionally bounded sample | Comparison table and benchmark JSON |
| `interactive-ui-and-handoff-demos/*` | Human/agent interaction | Open-ended | Requests, responses, or TUI session |

Run scripts are command transcripts, not hidden wrappers: inspect the script to
see the exact model, variables, outputs, and optional dependencies before
running it. A successful command exits zero; saved-artifact examples list or
write the documented output files, while terminal-only examples intentionally
leave no files.

Output folders use stable names so generated artifacts can be inspected later.
Compiled prompts are saved as `compiled-prompt.md` or `compiled-prompt.json`.
When an example executes a prompt with `weavemark --run`, the executed result is
saved as `execution-output.md` or `execution-output.json`; examples with
multi-step execution save `execution-trace.md` and may also save
`execution-steps.json`.

### Curated binary showcases

The complete comic and illustrated-book PNG/PDF outputs, plus the comic's
full-resolution character-sheet inputs, are intentionally available through
**Git LFS**. Install Git LFS before cloning when you want those originals:

```bash
git lfs install
git clone https://github.com/paulosalem/weavemark.git
```

An existing clone that contains only pointer files can fetch them with
`git lfs pull`. Storybook/comic outputs are curated snapshots. The comic
character sheets and style reference are required runtime inputs for reproducing
that workflow. Runner scripts may replace output snapshots locally, but changed
binaries should enter release history only deliberately because every version
consumes its full LFS storage and download bandwidth.

The documentation site uses lightweight regular-Git JPG previews because Git
LFS objects cannot be served by GitHub Pages. Full-resolution originals remain
available from the repository or a clone.

## Optional implementation step for software promplets

Some compiled examples are not meant to be the final answer; they are
implementation-ready software specifications. After compiling one of those promplets,
users can optionally ask GitHub Copilot CLI to implement it headlessly in a fresh
output directory:

```bash
weavemark implement \
  outputs/examples/compiled-prompt-snapshots/passive-income-planning-dashboard/compiled-prompt.md \
  --name passive-income-planning-dashboard
```

The command copies the compiled prompt into a fresh workspace under
`outputs/implementations/<name>/`, writes the exact implementation-agent prompt,
saves a manifest and transcript path, and runs the configured headless profile
from that implementation directory. This step is intentionally separate from
`run.sh` examples because it is mutating, agent-dependent, slower, and not needed
to inspect WeaveMark compilation.

Alternatives for exposing implementation to users:

- keep `weavemark implement` as the canonical opt-in path for any compiled
  software specification;
- add a small per-example `run-implementation.sh` only when a particular example
  needs a polished implementation demo;
- paste or attach the compiled spec manually in a programming agent such as Copilot
  CLI, VS Code Copilot, Claude Code, or another local agent;
- add richer provider-specific adapters later if configurable process profiles
  are not enough;
- provide a manual GitHub Actions workflow that runs an implementation agent in a
  disposable checkout and publishes artifacts or a draft PR.

Output expectations differ by category:

- Terminal-output-only runs intentionally have no wrapper banners or artifact
  summaries, but they do pass `--verbose` so WeaveMark processing progress is
  visible before the composed prompt.
- Batch example runs print clear section banners between examples and delay
  saved-file messages until one final artifact summary, so they remain readable
  even though they produce many outputs.
- Python-runtime integration and interactive UI/handoff runners show the
  companion/tool/handoff experience first, then summarize saved artifacts.

Useful entry points:

- `terminal-output-only/program-review-checklist/run.sh` runs one concrete spec
  with a vars file, showing verbose processing before the composed prompt.
- `saved-artifact-workflows/investment-brief/run.sh` compiles the completed
  investment-brief spec used by the hands-on tutorial and saves the compiled
  prompt for inspection.
- `terminal-output-only/messy-notes-action-plan/run.sh`,
  `terminal-output-only/deep-summary/run.sh`,
  `terminal-output-only/decision-advisor/run.sh`,
  `terminal-output-only/learning-tutor/run.sh`,
  `terminal-output-only/research-brief/run.sh`,
  `terminal-output-only/prompt-refiner/run.sh`, and
  `terminal-output-only/program-debugging-assistant/run.sh` compile practical
  prompts meant to be pasted into ChatGPT, Gemini, Claude, or another chat
  assistant.
- `batch-example-runs/static-prompts/run.sh` compiles the static prompt examples,
  including the `support-ticket-prompt-pack` `@emit` example and the
  `creative-ideation` examples that show one source spec semantically mingling
  three reusable ideation methods through `@refine`.
- `batch-example-runs/execution-engines/run.sh` runs Tree-of-Thought,
  Self-Consistency, Reflection, JSON, and the native bound-tool recurring monitor
  with saved traces.
- `saved-artifact-workflows/crisis-strategy/run.sh` runs one tool-enabled
  strategy-analysis spec, saving the compiled prompt and executed result.
- `saved-artifact-workflows/program-review-json/run.sh` shows the
  machine-readable JSON form of one prompt and saves it for downstream
  automation.
- `interactive-ui-and-handoff-demos/collaborative-investment-strategy/run-agent-handoff.sh`
  runs the collaborative examples in AI-agent handoff mode: each human/editor
  turn is written as a request file, and the surrounding AI agent writes the
  response file before the script continues.
- `python-runtime-integrations/tool-calling/run.py` compiles a WeaveMark `@tool`
  schema and runs it with a local calculator tool, saving the prompt, tool calls,
  final answer, and trace.
- `python-runtime-integrations/live-investment-decision/run.py` compiles a
  WeaveMark investment-decision brief from reusable finance, evidence, news,
  comparison, and explainability specs, then runs Ellements finance/search/crawl
  companions before synthesizing a source-grounded learning brief.
- `catalog/executable/recurring-topic-monitor` runs directly through the regular
  `weavemark ... --run` path. Query planning, source selection, crawling,
  relevance ranking, deduplication, previous-report comparison, and synthesis
  live in the promplet; its Python companion only binds one web search, news
  search, or crawl call at a time.
- `python-runtime-integrations/market-snapshot/run.py` compiles the experimental
  Weave stock snapshot, executes the bound Ellements finance/search/crawl tools
  through companion runtime components, and saves the tool results plus a
  `gpt-5.5` learning brief.
- `python-runtime-integrations/financial-independence-goal-plan/run.py` compiles
  the advanced goal-to-plan macro example, runs the bound public-reference
  lookup companion, and saves a ready-to-paste financial-independence planning
  prompt plus the weave plan and runtime assumptions.
- `benchmark-runners/strategy-comparison/run.sh` compares reasoning strategies on
  a tiny benchmark slice.

The live finance/web examples use optional Ellements extras:

```bash
pip install "weavemark[examples]"
playwright install chromium
```
