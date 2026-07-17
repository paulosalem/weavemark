# Transit City Swarm Ablation Study

This game study isolates **Transit City Swarm**, a browser strategy game that
combines transit-network drawing, city growth, and ant-colony pathfinding with
pheromone-style demand trails.

The study tests whether `@expand` helps a compact concept-level source become a
more integrated implementation-ready game specification.

## Variants

| Variant | File | Purpose |
|---|---|---|
| [C1] Compact no-expand control | [`specs/00-control-compact-no-expand-transit-city-swarm.weavemark.md`](specs/00-control-compact-no-expand-transit-city-swarm.weavemark.md) | Names the concept sources with little explanation. |
| [C2] Matched-prose no-expand control | [`specs/01-control-matched-prose-no-expand-transit-city-swarm.weavemark.md`](specs/01-control-matched-prose-no-expand-transit-city-swarm.weavemark.md) | Manually spells out the concept details without using `@expand`. |
| [T] Expanded WeaveMark treatment | [`specs/02-treatment-expand-transit-city-swarm.weavemark.md`](specs/02-treatment-expand-transit-city-swarm.weavemark.md) | Uses `@expand mode: intention` to unpack concept labels into game mechanics. |

## Finding

`@expand` improves source clarity and integration framing, especially compared
with the compact control. The matched-prose control remains a strong caveat:
when the author manually writes the expansion details, a no-expand source can
match or exceed some raw information metrics.

See [`results/ablation-summary.md`](results/ablation-summary.md) and
[`results/final-quality-analysis.md`](results/final-quality-analysis.md).
