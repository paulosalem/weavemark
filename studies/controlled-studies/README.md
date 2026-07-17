# WeaveMark Controlled Studies

Controlled studies compare manual sources, matched reusable-template or
matched-prose controls, and WeaveMark treatments while keeping the user goal
roughly stable.

Read these files first:

- [`../AGENTS.md`](../AGENTS.md) - operational study method for agents and maintainers.
- [`results.md`](results.md) / [`results.html`](results.html) - consolidated controlled-study result.
- [`method.md`](method.md) - compact evaluation criteria and scoring guide.

Current bottom line: WeaveMark is strongest when `@refine` treats reusable
requirements as abstract specifications and semantically mingles them through one
new local source. The controlled study set is intentionally single-output: it
excludes prompt-pack studies and exploratory material.

## Realistic application studies

| Study | What the example is | Study role |
|---|---|---|
| [`release-readiness-workbench-ablation-study/`](release-readiness-workbench-ablation-study/) | A local-first release command center for turning release notes, docs, validation runs, package artifacts, screenshots, risks, waivers, and go/no-go decisions into one auditable workspace. | Headline evidence for single-output structural mingling in a realistic software-product workflow. |
| [`intelligence-execution-kanban-ablation-study/`](intelligence-execution-kanban-ablation-study/) | A local-first Kanban board for monitoring selected topics, turning signals into cards, deciding actions, delegating work, tracking status, and preserving output lineage. | Headline evidence for semantic propagation across cards, board states, decisions, delegation, and outputs. |
| [`evidence-decision-workspace-ablation-study/`](evidence-decision-workspace-ablation-study/) | A local-first analyst workspace for documents, notes, links, news, claims, contradictions, ACH-style hypotheses, decisions, and follow-up actions. | Headline evidence for evidence-to-decision trace propagation through storage, UI, APIs, automation, and validation. |
| [`learning-tutor-refinement-ablation-study/`](learning-tutor-refinement-ablation-study/) | A pasteable linear-algebra tutor prompt using geometric intuition, Socratic questions, misconception diagnosis, adaptive practice, and delayed review. | Supporting non-programming evidence for reusable pedagogy refinements. |
| [`research-brief-ablation-study/`](research-brief-ablation-study/) | A research-brief instruction for energy-storage strategy that requires source families, context limits, contradictions, alternatives, caveats, and explainable evidence handling. | Supporting non-programming evidence for reusable research-quality lenses. |

## Game specification studies

Games are kept because they model a realistic WeaveMark use case: an author can
define an implementation-ready game specification for a programming agent while
reusing production, validation, mechanics, and expansion fragments.

All game studies live under [`games/`](games/), one subfolder per actual game.

| Study | What the example is | Study role |
|---|---|---|
| [`games/orbital-drift-racing-ablation-study/`](games/orbital-drift-racing-ablation-study/) | A browser racing game about piloting a small craft through asteroid fields, gravity wells, orbital gates, lap routing, hazards, scoring, restart, and browser validation. | Supporting game-programming specification evidence with strong leverage and yield. |
| [`games/verdant-relay-ablation-study/`](games/verdant-relay-ablation-study/) | A browser game about defending a living railway garden from blight by combining tower-defense route pressure, deckbuilder card choices, ecosystem feedback, original assets, and browser validation. | Strong single-output structural-mingling stress test for several reusable mechanics shaping one playable first-build trace. |
| [`games/transit-city-swarm-ablation-study/`](games/transit-city-swarm-ablation-study/) | A browser strategy game combining transit-network drawing, city growth, and ant-colony pathfinding through pheromone-style demand trails and congestion feedback. | Focused `@expand` evidence with a strong matched-prose caveat. |
| [`games/crowd-factory-puzzle-ablation-study/`](games/crowd-factory-puzzle-ablation-study/) | A browser puzzle game about steering autonomous crowds through factory automation, belts, machines, crates, spatial pushing rules, hazards, and readable level constraints. | Focused `@expand` evidence where `@iterate` materially improves the treatment. |

## Update reports

```bash
python studies/tools/regenerate_reports.py --clear
```

That command clears per-study Markdown and HTML reports, clears
[`results.md`](results.md) and [`results.html`](results.html), updates
[`metrics/semantic-information.json`](metrics/semantic-information.json),
extracts verbatim snippets, and writes synchronized conclusions including
failures and caveats.
