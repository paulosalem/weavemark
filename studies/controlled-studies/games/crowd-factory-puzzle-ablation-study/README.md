# Crowd Factory Puzzle Ablation Study

This game study isolates **Crowd Factory Puzzle**, a browser puzzle game about
autonomous crowds, factory automation, spatial pushing rules, and readable
level-design constraints.

The study tests whether `@expand` helps a compact concept-level source become a
more integrated implementation-ready game specification.

## Variants

| Variant | File | Purpose |
|---|---|---|
| [C1] Compact no-expand control | [`specs/00-control-compact-no-expand-crowd-factory-puzzle.weavemark.md`](specs/00-control-compact-no-expand-crowd-factory-puzzle.weavemark.md) | Names the concept sources with little explanation. |
| [C2] Matched-prose no-expand control | [`specs/01-control-matched-prose-no-expand-crowd-factory-puzzle.weavemark.md`](specs/01-control-matched-prose-no-expand-crowd-factory-puzzle.weavemark.md) | Manually spells out the concept details without using `@expand`. |
| [T] Expanded WeaveMark treatment | [`specs/02-treatment-expand-crowd-factory-puzzle.weavemark.md`](specs/02-treatment-expand-crowd-factory-puzzle.weavemark.md) | Uses `@expand mode: intention` to unpack concept labels into game mechanics. |

## Finding

`@expand` helps source clarity and integrated framing, but the gain is smaller
than in Transit City Swarm because the source concepts are already concrete:
workers, belts, machines, crates, grids, hazards, and levels are easy to unpack
manually.

See [`results/ablation-summary.md`](results/ablation-summary.md) and
[`results/final-quality-analysis.md`](results/final-quality-analysis.md).
