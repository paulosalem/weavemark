# Study: Intelligence-to-Execution Kanban Refinement

This study tests a single-final-specification case where refinement must modify the
structure of the target specification in many places. The goal is a local-first Kanban
workspace that connects incoming work intelligence with project execution:
selected topic monitoring, warnings, ideas, delegation, status checks, and output
artifacts all become one cohesive board/card system.

The study intentionally avoids `@prompt` and `@emit`. The WeaveMark treatment
compiles to one implementation-ready specification.

## Variants

| Variant | File | Purpose |
|---|---|---|
| Manual brief | [`specs/00-control-manual-intelligence-execution-kanban.weavemark.md`](specs/00-control-manual-intelligence-execution-kanban.weavemark.md) | A concise hand-written request for a Kanban workspace that monitors inputs and tracks outputs. |
| Matched reusable-template control | [`specs/01-control-template-intelligence-execution-kanban.weavemark.md`](specs/01-control-template-intelligence-execution-kanban.weavemark.md) | A deterministic template shell using study-local reusable partials for monitoring, local-first storage, workspace modules, and browser validation. |
| WeaveMark treatment | [`specs/02-treatment-promplet-intelligence-execution-kanban.weavemark.md`](specs/02-treatment-promplet-intelligence-execution-kanban.weavemark.md) | Mingles reusable Kanban, monitoring, signal-to-action, context-sufficiency, decision-strategy, dashboard, alert, explainability, and validation refinements into one final specification. |

## Reusable refinements introduced

- [`promplets/domains/work-intelligence/fragments/topic-intelligence-monitor.weavemark.md`](../../../promplets/domains/work-intelligence/fragments/topic-intelligence-monitor.weavemark.md)
- [`promplets/domains/work-intelligence/fragments/idea-execution-workspace.weavemark.md`](../../../promplets/domains/work-intelligence/fragments/idea-execution-workspace.weavemark.md)
- [`promplets/domains/work-intelligence/fragments/signal-to-action-workflow.weavemark.md`](../../../promplets/domains/work-intelligence/fragments/signal-to-action-workflow.weavemark.md)

These refinements are deliberately general: they can apply to other apps beyond
Kanban, such as dashboards, assistants, recurring monitors, project planners, or
personal research workspaces.

## What this demonstrates

The refined specification cannot be made coherent by inserting one "news" section and
one "ideas" section. The refinements change the meaning of:

- cards;
- board columns;
- movement rules;
- topic monitoring;
- signal triage;
- idea states;
- delegation;
- notifications;
- output lineage;
- activity history;
- API resources;
- database schema;
- validation and acceptance criteria.

A template can approximate the target only when its variable payload already
contains the transformed domain model. WeaveMark instead lets the short source
remain abstract while reusable refinements reshape the whole final specification.

## Commands

```bash
weavemark studies/controlled-studies/intelligence-execution-kanban-ablation-study/specs/02-treatment-promplet-intelligence-execution-kanban.weavemark.md \
  --vars-file studies/controlled-studies/intelligence-execution-kanban-ablation-study/inputs/promplet-vars.json \
  --output studies/controlled-studies/intelligence-execution-kanban-ablation-study/outputs/compiled-prompts/02-treatment-promplet-intelligence-execution-kanban.md \
  --no-file-summary
```

See [`results/ablation-summary.md`](results/ablation-summary.md) for structural
findings and [`results/final-quality-analysis.md`](results/final-quality-analysis.md)
for the compiled prompt contrastive analysis.
