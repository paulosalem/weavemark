<p align="center">
  <img src="https://raw.githubusercontent.com/paulosalem/weavemark/main/docs/weavemark_logo.png" alt="WeaveMark" width="600">
</p>

# WeaveMark

**A specification language for readable, reusable, and composable prompts.**

[![PyPI](https://img.shields.io/pypi/v/weavemark.svg)](https://pypi.org/project/weavemark/)
[![Python versions](https://img.shields.io/pypi/pyversions/weavemark.svg)](https://pypi.org/project/weavemark/)
[![CI](https://github.com/paulosalem/weavemark/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/paulosalem/weavemark/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Website](https://paulosalem.github.io/weavemark/) · [Tutorials](https://paulosalem.github.io/weavemark/docs/tutorial.html) · [Language reference](docs/usage-reference.md) · [PyPI](https://pypi.org/project/weavemark/)

> [!WARNING]
> WeaveMark is highly experimental. Its notation, Processor behavior, examples, and public interfaces are still evolving. Expect rough edges and breaking changes.

Write your prompt (or **promplet**) as readable Markdown plus special directives, *woven* into it. These include reuse (`@refine`), control flow (`@match`), polishing (`@polish`), dynamic clarifications (`@ask`), and many others. Then
use the **WeaveMark Processor** to: **compile** a concrete prompt, which can then be fed to an AI assistant or programming agent; or, optionally, actually **execute** it directly, independently of any other tool.

Compilation is intentionally hybrid: variables, branches, imports, output contracts, and validation are structural; semantic directives such as `@refine` are realized by an LLM. Execution, when requested, relies on predefined engines that follow well-established LLM patterns, as well as user-specified companion programs.

## See what it produced

| Illustrated storybook | AI Kanban | Market report |
|---|---|---|
| [![Orion storybook page](docs/tutorial-storybook-page.jpg)](https://paulosalem.github.io/weavemark/demos/orion-storybook/) | [![AI Kanban board](docs/showcase-ai-kanban.jpg)](https://paulosalem.github.io/weavemark/demos/ai-kanban/) | [![VALE3 market dashboard](docs/showcase-market-report.jpg)](https://paulosalem.github.io/weavemark/examples/saved-artifact-workflows/market-snapshot/outputs/market-dashboard.html) |
| A twelve-page story authored, illustrated page by page, and packaged to HTML/PDF. [Source](https://github.com/paulosalem/weavemark/blob/main/promplets/catalog/executable/childrens-book.weavemark.md?plain=1) · [Tutorial](https://paulosalem.github.io/weavemark/docs/tutorial-illustrated.html) | A concise software promplet compiled into a detailed contract and implemented as a backend-free browser app. [Source](https://github.com/paulosalem/weavemark/blob/main/promplets/catalog/standalone/ai-kanban-board.weavemark.md?plain=1) · [Compiled spec](https://github.com/paulosalem/weavemark/blob/main/outputs/implementations/ai-kanban-browser/compiled-spec.md) · [Tutorial](https://paulosalem.github.io/weavemark/docs/tutorial-implement.html) | Finance data and bounded search evidence executed through a strict graph, then packaged as a standalone report. [Source](https://github.com/paulosalem/weavemark/blob/main/promplets/catalog/executable/market-snapshot.weavemark.md?plain=1) · [Trace](https://github.com/paulosalem/weavemark/blob/main/examples/saved-artifact-workflows/market-snapshot/outputs/execution-trace.md) · [Tutorial](https://paulosalem.github.io/weavemark/docs/tutorial-executable.html) |

These are checked-in outputs, not mockups. The examples retain their source promplets, compiled plans or specifications, run artifacts, and tests.

## Try it yourself

Install the current release, then replay two real compilations without an API key or network call. `--verbose` shows the compilation steps and recorded provider statistics; `--output` writes the compiled artifact instead of printing it.

```bash
pip install weavemark

weavemark library market-snapshot --replay --verbose \
  --output vale3-market-prompt.md

weavemark library ai-kanban-board --replay --verbose \
  --output ai-kanban-spec.md
```

Replay validates the source, inputs, compiler prompt, schema, imported modules, tool results, and recorded call hashes. It replays compilation only: finance and search effects do not run. The original VALE3 run reported 11,002 input tokens, 0 cached, 20,728 output tokens, and $0.3384 total API cost. AI Kanban's recorded compilation reported 133,084 input tokens, 114,603 cached, 11,799 output tokens, and $0.2015 total API cost. Replaying either costs nothing.

You can also inspect any bundled promplet structurally:

```bash
weavemark library market-snapshot --scan
```

For a fresh semantic compilation and a real finance/search execution, install the example integrations and configure a model provider. The market data and web search need no additional keys.

```bash
pip install "weavemark[examples]"
export OPENAI_API_KEY="..."

weavemark library market-snapshot \
  --var provider_ticker=VALE3.SA \
  --var display_ticker=VALE3 \
  --var "company_name=Vale S.A." \
  --var "research_focus=iron ore demand, capital allocation, and material risks" \
  --run --verbose \
  --output-dir market-report \
  --open
```

WeaveMark compiles the promplet, runs the finance and search effects as a strict
dependency graph, writes the brief, packages it into
`market-report/market-dashboard.html`, and `--open` launches that dashboard in
your browser. Change the ticker variables for any asset you follow.

The finance helper is ordinary Python, so WeaveMark asks once before importing
it. Answer `y` to continue.

This is a real effectful run rather than a template expansion. Ours took about
three minutes and $0.34 of `gpt-5.6-terra` usage; add `--verbose`, as above, and
WeaveMark closes with the exact token counts, prompt-cache hits, and
provider-reported cost. `gpt-5.6-terra` is the default and currently recommended
model, and what every bundled example is exercised on; `--model` picks another.

You pay that cost once, not on every use. The compiled prompt is an ordinary
file: write it with `--output`, commit it, review it in a pull request, and reuse
it as often as you like, recompiling only when the source changes. That is why
this repository checks its compiled prompts in next to their sources.

For the compile-only path, where a short product source becomes a detailed
implementation contract that a programming agent then builds, follow
[Spec to app](https://paulosalem.github.io/weavemark/docs/tutorial-implement.html). For a first authored example with
variables, follow [Your first promplet](https://paulosalem.github.io/weavemark/docs/tutorial.html). For image
generation and other effectful runs, use only promplets you trust and read the
example-specific setup first.

## The source stays readable

This abridged AI Kanban source composes reusable architecture instead of repeating
it:

```markdown
@refine module:weavemark.domains.programming.stacks.browser_static_esmodules
@refine module:weavemark.domains.programming.types.browser_file_backed_webapp
@refine module:weavemark.domains.programming.modules.browser_sqlite_file_store
@refine module:weavemark.domains.programming.modules.browser_ai_handoff

# AI Kanban

Build a polished static JavaScript board whose canonical state is a
user-selected .aikanban.sqlite file. No backend.

@output enforce: strict
  Return architecture, storage, interaction, recovery, and test contracts.
```

The reusable modules carry file lifecycle, worker-owned SQLite, compatibility,
security, accessibility, and AI-handoff rules. The entrypoint stays focused on the product.

## Why use a language?

- **Reuse without copy-paste.** Shared constraints live in one promplet. Every
  dependent source picks up the new guidance on its next compile; the quality of
  each realization remains model- and run-dependent.
- **Semantic composition.** `@refine`, `@style`, `@summarize`, and related
  directives operate on meaning rather than only substituting text.
- **Readable control flow.** Variables, `@if`, `@match`, modules, assertions, and
  output contracts remain visible beside ordinary Markdown.
- **Executable plans.** Promplets can select reflection, chain,
  self-consistency, tree-of-thought, functional, collaborative, or FSLM
  execution.
- **Finished artifacts.** A run can persist images, reports, traces, prompt packs,
  packaged HTML/PDF, or a software specification.
- **Inspectability.** Source, compiled artifacts, bindings, execution metadata,
  and traces can be reviewed independently.

## What is deterministic?

| Surface | Behavior |
|---|---|
| Parsing, variables, branches, imports, files, assertions | Structural and local |
| `@refine`, `@style`, `@summarize`, semantic packaging | LLM-judged compilation |
| Execution engines and graph dependencies | Explicit runtime plan |
| Bound tools and Python companions | Host-authorized effects; not an OS sandbox |
| Generated text, code, and images | Model- and run-dependent |

WeaveMark does not claim formal verification or deterministic prompt quality. It
provides a durable language surface around generative behavior.

## Structured progress for tools and GUIs

`--verbose` remains the polished human terminal view. Automation should use the
same underlying lifecycle through `--events-jsonl FILE`, which flushes ordered
JSON Lines records while composition, execution, artifact persistence,
packaging, and `--open` are happening:

```bash
weavemark library market-snapshot \
  --vars-file inputs.json \
  --run \
  --output-dir outputs/market-snapshot \
  --events-jsonl outputs/market-snapshot/events.jsonl
```

Each record carries an ISO timestamp, monotonic sequence, type, optional phase,
and structured data, including absolute artifact and package paths and open
outcomes, so desktop and workflow clients never need to parse Rich terminal text.
Adding `--interaction-stdin jsonl` makes the channel bidirectional: WeaveMark
emits interaction requests through the stream and reads scoped responses from
stdin. Terminal confirmation behavior is unchanged without it, and invalid,
closed, or timed-out interaction streams deny the requested capability.

## Installation and safety

```bash
# Normal installation
pip install weavemark

# Source development
pip install -e ".[dev]"
```

Protections are enabled by default for local reads/writes, downloads, Python, and
external processes. They reduce common risks but are **not an operating-system
sandbox**. Do not run untrusted promplets; `--no-protections` deliberately
disables these checks for one invocation. [SECURITY.md](SECURITY.md) has the
full threat model.

WeaveMark depends on [ellements](https://pypi.org/project/ellements/), a library
of LLM building blocks I also maintain and build several projects on; that is why
it is a required dependency rather than a third-party one.

Full-resolution comic and storybook PNG/PDF artifacts use Git LFS. They are not
needed for normal installation; run `git lfs pull` in a clone when you want the
original media.

## More examples

| Example | What it demonstrates |
|---|---|
| [Illustrated stories](https://paulosalem.github.io/weavemark/docs/tutorial-illustrated.html) | Multimodal inputs, image outputs, reflection, repeated page chains, HTML/PDF packaging. |
| [AI Kanban](https://paulosalem.github.io/weavemark/docs/tutorial-implement.html) | Reusable software architecture, concise source, compiled contract, programming-agent implementation. |
| [Market report](https://paulosalem.github.io/weavemark/docs/tutorial-executable.html) | Module-owned bindings, effect graph, grounded synthesis, execution trace, semantic HTML packaging. |
| [Knowledge Cards](https://paulosalem.github.io/weavemark/demos/knowledge-cards/) | A mobile-first static app with manifest-discovered content packs and local state. |
| [Recurring topic monitor](promplets/catalog/executable/recurring-topic-monitor.weavemark.md) | Bounded search/news/crawl tools with event memory and material-change detection. |
| [Reasoning strategies](studies/runtime-studies/reasoning-strategies) | Reflection, self-consistency, and tree-of-thought promplets with their saved runs. |

The full maintained catalog is in [docs/examples.md](docs/examples.md). Reusable
building blocks live under [promplets/stdlib](promplets/stdlib) and
[promplets/domains](promplets/domains).

## Project guide

- [Introduction](https://paulosalem.github.io/weavemark/docs/introduction.html) — mental model and execution boundary.
- [Principles](https://paulosalem.github.io/weavemark/docs/principles.html) — design commitments and refinement model.
- [Tutorial track](https://paulosalem.github.io/weavemark/docs/tutorial.html) — nine connected hands-on lessons.
- [Processor reference](docs/usage-reference.md) — CLI, configuration, effects,
  engines, packages, protection, and replay.
- [Python API](docs/python-api.md) — async compilation and custom engines.
- [Agent usage](docs/agent-usage.md) — using WeaveMark from coding agents.
- [Citation](docs/citation.md) — BibTeX and APA.
- [Contributing](CONTRIBUTING.md) — what kind of contribution helps most now.
- [Security](SECURITY.md) — threat model, protections, and how to report issues.
- [Development](docs/development.md) — architecture and contribution workflow.

For traceability and replay, the Processor supports `--provenance`,
`--record-run`, and `--replay-run`; see the
[reference](docs/usage-reference.md#provenance-recording-and-replay).

## Frequently asked questions

### Why is the language called WeaveMark and the artifacts called promplets?

**WeaveMark** is a *markup* notation for prompts. Like any markup language -- think
HTML -- it shapes the content around it, but minimally invasively, keeping the focus
on the underlying prose (usually Markdown). The name also plays on *mark*: to trace
boundaries, to assemble marked pieces toward a goal, and to take careful notice,
something worth *remarking*.

A **promplet** is one artifact written in WeaveMark: a reusable unit of prompt
composition. The name reads two ways — *prompt + -let* (a small, modular artifact,
like an applet, especially when executable) and *prompt + let* (as in "let x be…",
emphasizing binding and composition).

### Where does the promplet concept come from?

The concept grew out of my own work; I developed it during **2025** without being
aware of anyone else using a similar term. Since then I realized that a few other
people have independently explored **kindred ideas** under the similar name
*promptlet* -- each in their own way: [composable prompt artifacts](https://github.com/riddles-in-the-dark/Promptlet), a reusable [prompt snippet](https://www.josh.ing/promptlet), a [weighted segment of a Midjourney multi-prompt](https://geekycuriosity.substack.com/p/midjourney-beginners-4-making-sense), and a unit of [prompt reuse and structure](https://www.breakingrocks.net/Promptlets-The-Full-How-to-Guide-20f3a5cc79f9808a9422fae353036248).

None of these are the same as WeaveMark. But the idea of a small, named, reusable
unit of prompting seems to be in the air, and each project takes it somewhere
different. WeaveMark simply develops it **in its own direction**. (WeaveMark spells
it *promplet*; several of them use *promptlet*.)

### Why does the notation use `@` and indentation for scoping?

To stay as readable as Markdown as possible. `@` marks the few places WeaveMark adds a
directive, and indentation scopes its body with minimal visual noise. Most
of a promplet should still read like ordinary prose, except those that are entirely just compositions of other pieces.

### Why Markdown instead of HTML or another markup language?

Markdown is already the lingua franca of prompts: readable in plain text,
familiar to LLM users, and easy to paste anywhere. WeaveMark is not fundamentally
limited to it: the `@`-based directive style is compatible with many markup
languages, including HTML, and future versions could support those better.

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

Not quite: our final "program" is the prompts to be used, woven from abstract, readable
prose. Under a liberal reading of "program" as "instructions to be executed," WeaveMark
is a kind of literate programming for natural-language instructions — call it
"programmatic prompting" if you prefer.

### Is this a harness?

As much as a car is a "fuel harness".

### Don't you have an actual job and a family to feed?

Why, yes -- but what's the problem? Some people watch the World Cup.
Others spend a full waking day every week doomscrolling Instagram.
Still others feed the poor. And who sleeps before midnight anyway?
I do this. It is my idea of fun, and of contributing to the community.

## Related work

Most prompt formats (Prompty, POML, Dotprompt) render deterministically; optimizers (DSPy, SAMMO) do let a model rewrite prompt text, but a metric over a dataset decides the result; spec-driven workflows (Spec Kit, Kiro) trust the model's judgement, yet expand a single intent and cannot import one specification into another. WeaveMark compiles with a language model and composes reusable modules by meaning. See the [full comparison of 25 projects](https://paulosalem.github.io/weavemark/docs/related-work.html).

## Citation

If WeaveMark helps your research, writing, or software work, please cite it as software ([BibTeX and APA](docs/citation.md)):

> Salem, P. (2026). *WeaveMark: A specification language for readable, reusable, and composable prompts* [Computer software]. GitHub. https://github.com/paulosalem/weavemark

## Author

WeaveMark is authored by Dr. Paulo Salem. Learn more at
[www.paulosalem.com](https://www.paulosalem.com) or connect on
[LinkedIn](https://www.linkedin.com/in/paulosalem/).
