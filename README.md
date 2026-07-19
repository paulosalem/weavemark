<p align="center">
  <img src="docs/weavemark_logo.png" alt="WeaveMark" width="600">
</p>

# WeaveMark
**A specification language for readable, reusable, and composable prompts.**

**Website:** [https://paulosalem.github.io/weavemark/](https://paulosalem.github.io/weavemark/)

> [!WARNING]
> WeaveMark is highly experimental. The notation, Processor
> behavior, examples, and public interfaces are still evolving, so expect rough
> edges, surprising results, and breaking changes.

> [!NOTE]
> WeaveMark is itself developed almost entirely through AI-assisted programming.
> That is part of the experiment: it treats prompt specification as a
> language-design problem and asks how far careful human direction plus
> AI-assisted programming can take language tooling.

**WeaveMark** is a Markdown-native **specification language** for prompts. Rather
than spelling out concrete wording, you *specify* intent — reusable refinements,
variables, branches, tools, and output contracts — and the **WeaveMark Processor**
decides how to realize it. A directive like `@refine` declares *what* should shape
a prompt; the processor works out *how* to weave it into concrete text. You get
software-grade reuse, composition, and versioning, while the source stays readable
prose.

The readable, reusable units you write in WeaveMark are called **promplets**. A
promplet is plain Markdown with a few directives; it can stand alone as one
concrete prompt, or be built from other promplets: shared personas, policies,
reasoning methods, domain constraints, and output structures reused and refined
across many prompts. Promplets are compiled by the **WeaveMark Processor**
(`weavemark`).

The twist: compilation is **largely LLM-based**, with deterministic structural
support. You can write an *abstract* constraint and let a language model realize
it as concrete prompt text, while parsing, variables, branching, and emission
stay deterministic. Prose stays central; directives just mark the seams for
composition, checks, reuse, and emission. Compiling *language* with a *language
model* is a deliberate experiment — see the FAQ for why.

Compilation and interpretation are distinct. **Compilation** turns readable
source and abstract directives into a structured prompt artifact.
**Interpretation** begins when that artifact is run: an execution engine treats
its named prompts, tools, contracts, and execution metadata as a runtime plan,
then records the model calls, tool use, intermediate steps, artifacts, and final
result.

## At a glance

| Concept | Meaning |
| --- | --- |
| **WeaveMark** | The formal, Markdown-native specification language for prompt systems — and the name of its toolchain and ecosystem. |
| **promplet** | A reusable prompt-composition artifact written in WeaveMark. |
| **WeaveMark Processor** | The `weavemark` command that compiles, inspects, and executes promplets. |

## What makes it different

- **Reuse that does not rot.** A reusable fragment lives in one file. Any
  promplet pulls it in with `@refine`, and the compiler weaves it into that
  document. Update the fragment once and every promplet that refines it picks up
  the new guidance on its next compile — without copy-paste to chase. Because
  compilation is model-based, the quality of each resulting prompt remains
  model- and run-dependent.
- **Semantic compilation, not templating.** `@refine`, `@style`, `@summarize`,
  and friends operate on *meaning*, so a base spec can be abstract and still
  compile into a concrete, coherent prompt.
- **Power with machinery.** An LLM supplies generative and interpretive power;
  language shapes that power, while computation sequences, checks, stores, and
  binds it to tools. Together they turn capability into useful actions and
  artifacts.
- **Batteries included.** A library of **50+** reusable methods ships in
  [`promplets/`](promplets): MECE, issue trees, ACH, SCAMPER, Six
  Thinking Hats, chain-of-thought, finance lenses, programming stacks and
  modules, teaching, and more.
- **Classic techniques, runnable.** Reflection, self-consistency, and
  tree-of-thought are reproduced as executable specs you can `--run` through
  different engines.
- **Specs that become software.** A software promplet compiles into a build-ready
  spec that `weavemark implement` hands to a programming agent — producing a real,
  runnable project (see [`outputs/implementations/orbital-drift/`](outputs/implementations/orbital-drift/README.md)).
- **Programming is still intent.** Agents may write the code—or even draft the
  promplet—but they still need intricate intent. A readable specification gives
  people and agents a durable artifact for negotiating, correcting, and refining
  that intent.
- **Explicit and inspectable.** Structural directives (`@if`, `@match`,
  `@prompt`, `@emit`, `@assert`) resolve locally and deterministically; only the
  semantic directives call the model. You always see the compiled artifact.
- **Source context with a retention choice.** `@reference` can use another file
  during compilation and either retain its resolved content in a deterministic
  Reference Appendix or omit the source from the generated artifact.
- **Multimodal.** Markdown image references (`![alt](chart.png)`) are sent to
  vision models as image inputs, and `@output type: image` turns a promplet into
  an image generator — toggle image lifting with `@compile images: on|off`.

## Mental model

A `.weavemark.md` file defines a promplet. It is Markdown with a few directives;
most of it stays the readable prompt intent you want compiled into a concrete
prompt.

```markdown
@refine module:weavemark.std.reasoning.base_analyst

Write a market brief for @{company}.

@match depth
  "short" ==>
    Keep it under 300 words.
  "detailed" ==>
    Include market size, competitors, risks, and recommendations.

@if include_sources
  Cite sources for every factual claim.
```

The Processor resolves refinements, variables, branches, emitted files, tools,
and assertions into a structured result. Semantic refinement goes beyond
templating: the base prompt is abstract, and compilation decides how to realize
it here.

The word **specification** is deliberate. An abstract `Spec` states properties
that any realization must preserve; a more concrete `Imp` adds decisions and
detail. Correct refinement means `Imp ⇒ Spec`, while generally `Spec ⇏ Imp`
because one specification permits many implementations. WeaveMark takes
inspiration from that discipline without claiming formal verification. See the
[Principles](docs/principles.html) for the precise model.

Use `@reference path/to/file keep:true|false` for source context. Retained
references are appended after a `***` document break; compilation-only
references are not mechanically copied into the generated prompt. The explicit
inline form is `@reference("path/to/file" keep:true)`. Language 0.9 also accepts
Claude-style path shorthand outside code spans and fences; the checked-in
[reference-context example](examples/terminal-output-only/reference-context/promplets/reference-aware-release-note.weavemark.md)
contains the project’s only shorthand demonstration.

## Installation

```bash
pip install weavemark
```

For local development:

```bash
pip install -e ".[dev]"
```

Full-resolution comic/storybook showcases use Git LFS. They are optional for
normal development; run `git lfs pull` when you want the original generated
PNG/PDF artifacts. Lightweight documentation previews remain in ordinary Git.

This installs the `weavemark` command — formally, the **WeaveMark Processor**.

## Quickstart

Compile a promplet into a pastable prompt. By default the Processor asks for any
missing inputs; add `--batch-only` for automation.

### Experimental protections

Protections are enabled by default. They constrain local reads and writes,
validate remote downloads, require confirmation before Python or external
process execution. Approved executable
items are remembered in `~/.weavemark/protection-approvals.json`.

> [!CAUTION]
> These protections reduce common risks; they are **not an OS sandbox**. Do not
> run promplets you do not trust. `--no-protections` deliberately restores the
> unrestricted trusted-promplet behavior for one invocation.

See the [Processor reference](docs/usage-reference.md#experimental-protections)
for policy keys, roots, batch behavior, and residual limitations.

Debug logs are independently configurable and omit binary/base64 payloads by
default while retaining normal variables and text. See
[configurable debug logging](docs/usage-reference.md#configurable-debug-logging).

```bash
# Guided: the Processor asks for any missing inputs, then compiles.
weavemark library tutorial-generator

# Automation: supply inputs, fail fast if any are missing, write to a file.
weavemark library tutorial-generator \
  --var topic="FastAPI dependency injection" \
  --var audience=intermediate \
  --var include_exercises=true \
  --var output_format=Markdown \
  --batch-only \
  --output tutorial-prompt.md
```

The output is a clean prompt with variables substituted and authoring directives
resolved. Open it, then paste it into ChatGPT, Claude, Gemini, Copilot Chat, or
your own application. From a source checkout you may instead use the prominent,
canonical repository path directly:
`promplets/catalog/standalone/tutorial-generator.weavemark.md`.

## Reuse in action

The superpower is that the *same* building blocks compile into completely
different artifacts. Two checked-in specs both refine the same finance
fragments (`passive-income-capital-growth`, `passive-income-forecasting`):

- [`financial-independence-decision.weavemark.md`](promplets/catalog/standalone/financial-independence-decision.weavemark.md)
  adds reasoning, finance guidelines, and decision lenses → a **decision-analysis
  prompt**.
- [`passive-income-planning-dashboard.weavemark.md`](promplets/catalog/standalone/passive-income-planning-dashboard.weavemark.md)
  adds a local-first web stack, decision-oriented dashboard, and SQLite
  persistence → a **build-ready app specification**.

Improve one finance fragment and both get better the next time they compile.
Then take the app spec one step further:

```bash
# 1) Compile the software promplet into a plain specification.
weavemark library passive-income-planning-dashboard \
  --var app_name=Fathom --batch-only --output outputs/fathom/compiled-spec.md

# 2) Hand it to a headless programming agent to build a runnable project.
weavemark implement outputs/fathom/compiled-spec.md --name fathom --profile copilot
```

This is not hypothetical: the checked-in
[Orbital Drift](outputs/implementations/orbital-drift/README.md) game was built
this way — with `package.json`, a test suite, and run instructions.

## Executable promplets

Some promplets do not just produce prompt text — they declare an execution
engine. Reflection, self-consistency, and tree-of-thought are reproduced as
runnable specs. Bound-tool promplets can also run model-directed tools directly;
the recurring monitor keeps all research logic in WeaveMark and binds only
individual web search/news/crawl calls:

```bash
export OPENAI_API_KEY="..."

weavemark library tree-of-thought-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/tree-of-thought-solver-example.json \
  --run --batch-only

weavemark library recurring-topic-monitor \
  --vars-file examples/batch-example-runs/execution-engines/inputs/recurring-topic-monitor-ai-news.json \
  --run
```

## Explore the library

Start with the showcase promplets: they demonstrate WeaveMark as more than a
single prompt template. The best examples combine reusable domain modules,
execution plans, tool bindings, media artifacts, or app-scale specifications.

| Showcase | Why it is worth exploring |
| --- | --- |
| [`childrens-book.weavemark.md`](promplets/catalog/executable/childrens-book.weavemark.md) | A full children's picture-book pipeline: author the page-by-page story, render one image per page, then package the result into print-ready HTML and PDF deliverables. |
| [`recurring-topic-monitor.weavemark.md`](promplets/catalog/executable/recurring-topic-monitor.weavemark.md) | An executable news/topic monitor with trusted Python tool bindings for web search, news search, and source crawling. It clusters new vs. repeated vs. materially changed findings from live evidence. |
| [`news-intelligence-board.weavemark.md`](promplets/catalog/standalone/news-intelligence-board.weavemark.md) | A local-first news and events intelligence board specification with durable source memory, event clustering, material-update resurfacing, and workflow-board views. |
| [`storyboard-chain.weavemark.md`](promplets/catalog/executable/storyboard-chain.weavemark.md) | A compact text-to-image chaining demo: one prompt writes a shot list, then a repeated image stage renders frame-by-frame story continuity. |
| [`prompt-refactoring-pipeline.weavemark.md`](promplets/catalog/standalone/prompt-refactoring-pipeline.weavemark.md) | Treats a messy prompt as a semantic artifact to refactor with `@extract`, `@normalize`, `@revise`, `@expand`, `@polish`, and `@assert`. |
| [`tree-of-thought-solver.weavemark.md`](promplets/catalog/executable/tree-of-thought-solver.weavemark.md) | Makes a reasoning execution strategy explicit with separate generation, evaluation, and synthesis prompts. |
| [`react-agent.weavemark.md`](promplets/catalog/executable/react-agent.weavemark.md) | A compact ReAct agent with tools declared beside the prompt and behavior varied by research depth. |

The full catalog is in [`docs/examples.md`](docs/examples.md), and the reusable
building blocks live in [`promplets/stdlib/`](promplets/stdlib) and
[`promplets/domains/`](promplets/domains).

The complete root [`promplets/`](promplets) tree is the canonical source and is
also shipped as an importable package resource. The `library` command presents it
together with project, user, and additional promplet libraries:

```bash
# Show every effective source and its filesystem root.
weavemark library sources

# Search all roots together.
weavemark library list finance

# Restrict a search or lookup to one source.
weavemark library list --source user
weavemark library list --collection stdlib --kind fragment
weavemark library show builtin:catalog/standalone/investment-brief

# Copy the full built-in corpus somewhere you can edit.
weavemark library copy ./weavemark-promplets
```

The default custom roots are project `./promplets/` and user
`~/.weavemark/promplets/`. Add more roots through `library_dirs` in
`~/.weavemark/config.json` or the nearest `.weavemark.config.json`, and through
repeatable `--library-dir` values.
For example:

```json
{
  "library_dirs": [
    "~/Documents/weavemark-promplets",
    "/work/team-promplets"
  ]
}
```

Bare library references search project, user, additional, then built-in roots.
Use a source qualifier or stable module identity when desired:

```bash
weavemark library investment-brief
weavemark library user:work/quarterly-review
weavemark library builtin:catalog/standalone/investment-brief
weavemark library module:weavemark.std.reasoning.base_analyst --scan
```

Other strong examples:

- [`investment-brief.weavemark.md`](promplets/catalog/standalone/investment-brief.weavemark.md)
  is a pastable analysis prompt with explicit evidence, uncertainty, and safety
  boundaries.
- [`multi-persona-debate.weavemark.md`](promplets/catalog/standalone/multi-persona-debate.weavemark.md)
  uses semantic `@expand` and `@revise` to build a balanced debate prompt with
  synthesis modes.
- [`creative-ideation.weavemark.md`](promplets/catalog/standalone/creative-ideation.weavemark.md)
  dispatches among reusable ideation methods such as SCAMPER, Six Thinking Hats,
  and reverse brainstorming.
- [`adaptive-interview.weavemark.md`](promplets/catalog/standalone/adaptive-interview.weavemark.md)
  uses nested `@match`, `@if`, `@compress`, and `@generate_examples` to adapt one
  protocol by role, seniority, and format.

## WeaveMark Processor quick reference

```bash
# Guided compile (asks for missing inputs).
weavemark library tutorial-generator

# Strict, non-interactive compile for automation.
weavemark library tutorial-generator \
  --batch-only \
  --var topic="Python decorators" --var audience=beginner \
  --var include_exercises=false --var output_format=Markdown

# Machine-readable output for another program.
weavemark <promplet> --batch-only --format json

# Optional traceability, full-call recording, and strict offline replay.
weavemark <promplet> --provenance outputs/run.provenance.json
weavemark <promplet> --record-run outputs/run
weavemark <promplet> --replay-run outputs/run

# Inspect required inputs without compiling.
weavemark <promplet> --scan

# Full terminal UI: input form + live preview.
weavemark <promplet> --ui

# Execute a spec through its engine (needs provider credentials).
weavemark <executable-promplet> --run

# Browse the built-in corpus and custom libraries.
weavemark library list
```

Use `--var KEY=VALUE` for a few inputs and `--vars-file vars.json` or
`--vars-file vars.yaml` for reusable input sets; YAML block scalars are especially
comfortable for long text. Inline `--var` values override file keys.
`--batch-only` disables prompts and fails before compilation if any discovered
input is missing. Structural composition runs locally; semantic directives such
as `@refine` and `@summarize` call the configured LLM, so set provider
credentials (e.g. `OPENAI_API_KEY`) first. Run `weavemark --help` for all
options.

## Tooling

- **VS Code extension** — directive, variable, match-case, and Markdown-aware
  highlighting plus WeaveMark Dark/Light themes for `.weavemark.md` files. Until
  it is on the marketplace, run
  `python scripts/install_vscode_extension.py`; see
  [`vscode-extension/`](vscode-extension/README.md).

## Author

WeaveMark is authored by Dr. Paulo Salem. Learn more at
[www.paulosalem.com](https://www.paulosalem.com) or connect on
[LinkedIn](https://www.linkedin.com/in/paulosalem/).

## How to cite WeaveMark

If WeaveMark helps your research, writing, or software work, please cite it as
software. Update the version if you are citing a specific release.

**BibTeX**

```bibtex
@misc{salem2026weavemark,
  author = {Salem, Paulo},
  title = {{WeaveMark}: An Experimental Language for Readable, Reusable, and Composable Prompts},
  year = {2026},
  url = {https://github.com/paulosalem/weavemark},
  note = {Version 0.9.0; computer software}
}
```

**APA**

Salem, P. (2026). *WeaveMark: An experimental language for readable, reusable, and
composable prompts* (Version 0.9.0) [Computer software]. GitHub.
https://github.com/paulosalem/weavemark

## For AI agents

If you are an AI programming agent (GitHub Copilot, Claude Code, Cursor, and the
like), WeaveMark is designed to work *with* you, not around you:

- **Organize your own work.** Capture reusable intent as promplets — personas,
  policies, reasoning methods, and output contracts — with `@refine`, instead of
  regenerating sprawling ad-hoc prompts. A specification language gives you
  durable, composable structure to build on.
- **Specify abstractly; let the Processor make it concrete.** Declare *what* you
  want and `weavemark` compiles it into concrete prompt text, role-tagged packs,
  or a build-ready software spec.
- **Validate before spending tokens.** `weavemark <spec> --scan` reports the
  inputs and structure a spec needs before any LLM call; `--batch-only --format
  json` gives machine-readable output.
- **Collaborate with humans cleanly.** A promplet is a precise, readable surface,
  so a person can review or edit only the well-scoped parts — a variable, a
  constraint, an output contract — boundaries you can define for them.

**Skills in this repo.** Ready-to-use agent skills (Claude Code and Copilot) live
under [`.claude/skills/`](.claude/skills/) and [`.github/skills/`](.github/skills/):

| Skill | What it does |
| --- | --- |
| [`weavemark`](.claude/skills/weavemark/SKILL.md) | Author, validate, compose, and run `.weavemark.md` specs. |
| [`weavemark-collaborative-handoff`](.claude/skills/weavemark-collaborative-handoff/SKILL.md) | Run, test, debug, and automate collaborative / human-in-the-loop specs (`@execute collaborative`). |
| [`weavemark-compiled-spec-implementation`](.github/skills/weavemark-compiled-spec-implementation/SKILL.md) | Hand a compiled software spec to a headless programming agent to build a runnable project. |
| [`weavemark-study-reporting`](.github/skills/weavemark-study-reporting/SKILL.md) | Update study reports, metrics, Markdown/HTML companions, and validation checks. |
| [`grammar-sync`](.claude/skills/grammar-sync/SKILL.md) | Keep the language definition in sync with its `docs/weavemark.ebnf` mirror. |

Repo-wide agent guidance lives in
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) and
[`CLAUDE.md`](CLAUDE.md).

## Frequently asked questions

### Why is the language called WeaveMark and the artifacts called promplets?

**WeaveMark** is a *markup* notation for prompts. Like any markup language — think
HTML — it shapes the content around it, but minimally invasively, keeping the focus
on the underlying prose (usually Markdown). The name also plays on *mark*: to trace
boundaries, to assemble marked pieces toward a goal, and to take careful notice —
something worth *remarking*.

A **promplet** is one artifact written in WeaveMark: a reusable unit of prompt
composition. The name reads two ways — *prompt + -let* (a small, modular artifact,
like an applet, especially when executable) and *prompt + let* (as in "let x be…",
emphasizing binding and composition). Keeping distinct names for the language and its
artifacts is intentional: like "a document written in HTML," you can say "a promplet
written in WeaveMark" with no ambiguity — no "spec" suffix needed.

### Where does the promplet concept come from?

The concept grew out of my own work; I developed it during **2025** without being
aware of anyone else using a similar term. Since then I have been glad to find that a
few other people have independently explored **kindred ideas** under the similar name
*promptlet* — each in their own way: a reusable [prompt snippet](https://www.josh.ing/promptlet),
a [weighted segment of a Midjourney multi-prompt](https://geekycuriosity.substack.com/p/midjourney-beginners-4-making-sense),
and a unit of [prompt reuse and structure](https://breakingrocks.net/Promptlets-The-Full-How-to-Guide-20f3a5cc79f9808a9422fae353036248).

None of these are the same as WeaveMark, and that is part of the fun: the idea of a
small, named, reusable unit of prompting seems to be in the air, and each project
takes it somewhere different. WeaveMark simply develops it **in its own direction** —
toward composable, refinable specifications you can compile. These related efforts are
a genuinely welcome source of ideas and inspiration. (WeaveMark spells it *promplet*;
several of them use *promptlet*.)

### Why does the notation use `@` and indentation for scoping?

To stay as readable as Markdown. `@` marks the few places WeaveMark adds a
directive, and indentation scopes its body without braces or closing tags. Most
of a promplet should still read like ordinary prose.

### Why Markdown instead of HTML or another markup language?

Markdown is already the lingua franca of prompts: readable in plain text,
familiar to LLM users, and easy to paste anywhere. WeaveMark is not fundamentally
limited to it — the `@`-based directive style is compatible with many markup
languages, and future versions could support others.

### LLM-based compilation? Are you insane?

A little, of course; where would [the fun](https://en.wikipedia.org/wiki/In_Praise_of_Folly)
be otherwise? Language is the ultimate thinking tool. What if natural language
could help us design useful new languages more easily? LLMs let us try — so let's
experiment.

### Why not a template engine?

Template engines are perfect when the result shape is known exactly: substitute
this variable, include that partial verbatim. Promplets allow more *abstract*
composition, at the cost of a generative model realizing the final prompt. That
makes them more reusable and more readable. Some promplets also go further —
running compiled prompts through engines like reflection or tree-of-thought, and
binding trusted companion programs — so WeaveMark can act as a prompting engine,
not only a language.

### This is not literate programming!

Not quite: our final "program" is the prompts to be used, woven from abstract,
readable prose. Under a liberal reading of "program" as "instructions to be
executed," WeaveMark is a kind of literate programming for natural-language
instructions — call it "programmatic prompting" if you prefer.

### Is this a harness?

As much as a car is a "fuel harness".

### Don't you have an actual job and a family to feed?

Why, yes — but what's the problem? Some people watch the World Cup.
Others spend a full waking day every week doomscrolling Instagram.
Still others feed the poor. And who sleeps before midnight anyway?
I do this. It is my idea of fun - and of contributing to the community.

## Learn more

- [Introduction](docs/introduction.html) — the mental model, Processor, compilation stages, and execution boundary.
- [Principles](docs/principles.html) — language as a tool for thought and the design commitments that follow.
- [Public tutorial track](docs/tutorial.html) — hands-on lessons from your first promplet to reuse, the semantic toolbox, and spec-to-app.
- [Python API](docs/python-api.md) — async library usage, execution, custom engines, and diagnostics.
- [WeaveMark Processor and language reference](docs/usage-reference.md) — batch mode, output formats, emissions, tools, assertions, execution engines, modules, and config.
- [Example promplets](docs/examples.md) — the included promplet catalog and showcase commands.
- [Development notes](docs/development.md) — editor extension, architecture, and prompt logging.
- [Migrating to 0.8](docs/migrating-to-0.8.md) — version policy, compatibility, diagnostics, protections, and replay.
- [Changelog](CHANGELOG.md) — release-level additions and behavioral changes.
- [Full language reference](src/weavemark/prompts/weavemark.system.md) — the formal WeaveMark reference used by the Processor.
