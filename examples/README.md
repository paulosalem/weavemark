# WeaveMark runnable examples

This directory contains the deliberately small set of maintained public example
projects. Every project owns its inputs, an explicit invocation surface (a runner
or direct README command), and inspectable outputs.

## Saved artifact workflows

- [`arcana/`](saved-artifact-workflows/arcana) contains a complete 55-card
  archetypal deck, executable image pipeline, and packaged reflective browser
  game with optional OpenAI interpretation and narration.
- [`childrens-book-bebe-fusquinha/`](saved-artifact-workflows/childrens-book-bebe-fusquinha)
  contains the complete English and Portuguese Bebe Fusquinha editions.
- [`childrens-book-orion-en/`](saved-artifact-workflows/childrens-book-orion-en)
  contains the Orion storybook source chain and packaged artifacts.
- [`comic-strip-en/`](saved-artifact-workflows/comic-strip-en) contains the
  complete comic workflow and inspection log.
- [`market-snapshot/`](saved-artifact-workflows/market-snapshot) contains the
  grounded VALE3 report, trace, and standalone dashboard.
- [`prompt-refactoring-pipeline/`](saved-artifact-workflows/prompt-refactoring-pipeline)
  contains one focused semantic prompt-transformation run.
- [`recurring-topic-monitor/`](saved-artifact-workflows/recurring-topic-monitor)
  contains retained topic-monitor reports and traces.

## Runtime and handoff integrations

- [`financial-independence-goal-plan/`](python-runtime-integrations/financial-independence-goal-plan)
  demonstrates imported macros, a bound public-reference function, and a grounded
  final plan.
- [`collaborative-writer/`](interactive-ui-and-handoff-demos/collaborative-writer)
  demonstrates interactive and surrounding-agent editorial handoff.

The shared shell bootstrap is [`_lib/example-env.sh`](_lib/example-env.sh).
Python runners use
[`_lib/weavemark_example_progress.py`](_lib/weavemark_example_progress.py) for
concise progress and Markdown normalization. Commands without an explicit model
use WeaveMark's configured default.

## Setup

```bash
pip install -e .
pip install -e ".[examples]"  # finance/search companions
playwright install chromium   # live web-search examples
```

Illustrated book and comic originals use Git LFS. Lightweight derivatives power
the documentation site and live Orion reader.

Every runner works from the repository root or another current directory and
writes only beneath its own `outputs/` folder. Inspect a runner before executing
it to see its provider, effects, and artifact paths.

## Personalize a run

Five examples include an additional guided runner. They prefill the verbose
settings and let WeaveMark ask only for the short inputs that make the result
yours:

```bash
examples/saved-artifact-workflows/recurring-topic-monitor/run-interactive.sh
examples/saved-artifact-workflows/market-snapshot/run-interactive.sh
examples/interactive-ui-and-handoff-demos/collaborative-writer/run-interactive.sh
examples/python-runtime-integrations/financial-independence-goal-plan/run-interactive.sh
examples/saved-artifact-workflows/prompt-refactoring-pipeline/run-interactive.sh path/to/prompt.md
```

The prompts are, respectively: a topic; provider and display tickers plus a
company name; a writing topic; a financial goal, country, and horizon; and a
revision instruction. Personalized artifacts are kept under a timestamped
`outputs/interactive/` directory, separate from the reproducible checked-in
results. Market Snapshot also opens its packaged HTML dashboard in your default
browser when the run completes.
