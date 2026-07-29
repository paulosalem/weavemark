# Curated promplets and examples

The public catalog intentionally contains a small set of complete, validated
entrypoints. Each one demonstrates a distinct WeaveMark capability and, where
practical, links to a runnable workflow or live result.

Reusable building blocks remain available under [`stdlib/`](../promplets/stdlib)
and [`domains/`](../promplets/domains). Specialized engine and benchmark material
lives under [`studies/runtime-studies/`](../studies/runtime-studies).

## Catalog

| Promplet | Kind | Distinctive proof |
|---|---|---|
| [`childrens-book.weavemark.md`](../promplets/catalog/executable/childrens-book.weavemark.md) | Executable | Orion and both Bebe Fusquinha editions; page-by-page image chain plus HTML/PDF packaging. |
| [`collaborative-writer.weavemark.md`](../promplets/catalog/executable/collaborative-writer.weavemark.md) | Executable | Human or surrounding-agent editorial handoff with a durable execution trace. |
| [`comic-strip.weavemark.md`](../promplets/catalog/executable/comic-strip.weavemark.md) | Executable | Reference-image-aware reflection workflow with inspection and revision. |
| [`financial-independence-goal-plan.weavemark.md`](../promplets/catalog/executable/financial-independence-goal-plan.weavemark.md) | Executable | Imported semantic macro, bound public-reference lookup, and grounded final plan. |
| [`market-snapshot.weavemark.md`](../promplets/catalog/executable/market-snapshot.weavemark.md) | Executable | Finance/search evidence graph packaged as a standalone HTML report. |
| [`recurring-topic-monitor.weavemark.md`](../promplets/catalog/executable/recurring-topic-monitor.weavemark.md) | Executable | Bounded search/crawl, prior-report memory, deduplication, and material-update detection. |
| [`ai-kanban-board.weavemark.md`](../promplets/catalog/standalone/ai-kanban-board.weavemark.md) | Software specification | Concise source compiled into a complete browser-only SQLite application contract. |
| [`knowledge-cards.weavemark.md`](../promplets/catalog/standalone/knowledge-cards.weavemark.md) | Software specification | Mobile-first learning feed with pre-generated packs and local progress. |
| [`prompt-refactoring-pipeline.weavemark.md`](../promplets/catalog/standalone/prompt-refactoring-pipeline.weavemark.md) | Prompt program | Nested semantic transformation of a contradictory prompt into a coherent artifact. |

## Runnable examples

| Example | Result |
|---|---|
| [`childrens-book-bebe-fusquinha/`](../examples/saved-artifact-workflows/childrens-book-bebe-fusquinha) | Complete English and Portuguese illustrated books. |
| [`childrens-book-orion-en/`](../examples/saved-artifact-workflows/childrens-book-orion-en) | Twelve-page Orion storybook and packaged outputs. |
| [`comic-strip-en/`](../examples/saved-artifact-workflows/comic-strip-en) | Complete comic, source chain, and inspection log. |
| [`market-snapshot/`](../examples/saved-artifact-workflows/market-snapshot) | Grounded VALE3 analysis, execution trace, and dashboard. |
| [`prompt-refactoring-pipeline/`](../examples/saved-artifact-workflows/prompt-refactoring-pipeline) | Focused source, YAML input, and compiled refactored prompt. |
| [`recurring-topic-monitor/`](../examples/saved-artifact-workflows/recurring-topic-monitor) | Saved topic-monitor reports and traces. |
| [`financial-independence-goal-plan/`](../examples/python-runtime-integrations/financial-independence-goal-plan) | Compiled plan, grounded assumptions, output, and trace. |
| [`collaborative-writer/`](../examples/interactive-ui-and-handoff-demos/collaborative-writer) | Self-contained collaborative runner and handoff artifacts. |

## Live applications

- [Orion storybook](https://paulosalem.github.io/weavemark/demos/orion-storybook/)
- [AI Kanban](https://paulosalem.github.io/weavemark/demos/ai-kanban/)
- [Knowledge Cards](https://paulosalem.github.io/weavemark/demos/knowledge-cards/)
- [VALE3 market dashboard](https://paulosalem.github.io/weavemark/examples/saved-artifact-workflows/market-snapshot/outputs/market-dashboard.html)

## Run a selected example

```bash
examples/saved-artifact-workflows/prompt-refactoring-pipeline/run.sh
examples/saved-artifact-workflows/market-snapshot/run.sh
examples/saved-artifact-workflows/childrens-book-orion-en/run.sh
```

Personalize one of the five concise guided demos:

```bash
examples/saved-artifact-workflows/recurring-topic-monitor/run-interactive.sh
examples/saved-artifact-workflows/market-snapshot/run-interactive.sh
examples/interactive-ui-and-handoff-demos/collaborative-writer/run-interactive.sh
examples/python-runtime-integrations/financial-independence-goal-plan/run-interactive.sh
examples/saved-artifact-workflows/prompt-refactoring-pipeline/run-interactive.sh path/to/prompt.md
```

These runners reuse WeaveMark's own variable discovery and guided prompts. They
prefill longer settings, ask for only the personal topic, ticker details, goal,
or revision, and save each run beneath its example's timestamped
`outputs/interactive/` directory. The original runners remain deterministic
reproduction paths for the checked-in artifacts. Market Snapshot also opens its
packaged HTML dashboard in the default browser after a successful run.

Start with a structural check when model access is not needed:

```bash
weavemark promplets/catalog/standalone/ai-kanban-board.weavemark.md --scan
```
