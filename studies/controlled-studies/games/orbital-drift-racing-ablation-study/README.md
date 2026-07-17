# Orbital Drift Racing Game Ablation Study

This game study keeps one clean single-output comparison for **Orbital
Drift**, a browser racing game about piloting a small craft through asteroid
fields, gravity wells, orbital gates, and lap-based hazards.

The study asks whether a compact WeaveMark source can produce a stronger
implementation-ready game specification than a compact manual control and a
matched reusable-template control.

## Variants

| Variant | File | Purpose |
|---|---|---|
| [C1] Manual brief control | [`specs/00-control-manual-orbital-drift.weavemark.md`](specs/00-control-manual-orbital-drift.weavemark.md) | Minimal hand-written browser racing game specification. |
| [C2] Matched reusable-template control | [`specs/01-control-template-orbital-drift.weavemark.md`](specs/01-control-template-orbital-drift.weavemark.md) | Deterministic template shell using study-local game, browser implementation, assets, and validation partials. |
| [T] WeaveMark treatment | [`specs/02-treatment-promplet-orbital-drift.weavemark.md`](specs/02-treatment-promplet-orbital-drift.weavemark.md) | Reuses software-spec, web-game, and Playwright MCP validation layers. |

## What improved most

The WeaveMark treatment is strongest because reusable browser-game and
validation obligations shape the whole specification:

- game states, controls, hazards, scoring, restart, and feedback are made
  explicit;
- browser implementation and real-browser validation are integrated rather than
  appended;
- the source stays compact while the resulting game specification includes enough
  detail for a playable first build.

## Results

- [`results/ablation-summary.md`](results/ablation-summary.md) records the
  structural measurements and semantic-information metrics.
- [`results/final-quality-analysis.md`](results/final-quality-analysis.md)
  compares the saved single-output specifications with the contrastive method.
