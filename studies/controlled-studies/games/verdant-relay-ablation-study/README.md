# Verdant Relay Ablation Study

**Status:** synthetic technical stress test. Keep this study because it is a
strong single-output structural-mingling case, but do not present it as the main
evidence that WeaveMark models realistic work applications.

This study tests whether WeaveMark can create a much stronger
implementation-ready browser-game specification for **Verdant Relay** without
relying on prompt packs.

The target game, Verdant Relay, combines:

- tower-defense route pressure;
- deckbuilder card choice and synergy;
- ecosystem simulation feedback loops;
- browser-game implementation and validation;
- original sprite/asset production requirements.

## Variants

1. [`00-control-compact-manual-verdant-relay.weavemark.md`](specs/00-control-compact-manual-verdant-relay.weavemark.md)
   - compact manual prompt;
2. [`01-control-template-verdant-relay.weavemark.md`](specs/01-control-template-verdant-relay.weavemark.md)
   - matched reusable-template control rendered from study-local game partials;
3. [`02-treatment-promplet-verdant-relay.weavemark.md`](specs/02-treatment-promplet-verdant-relay.weavemark.md)
   - WeaveMark treatment using semantic `@refine` and focused `@expand`,
     compiled to one final browser-game implementation specification.

## Why this is a single-output structural test

The game cannot be coherent if the reusable mechanics are merely appended. Tower
defense, deckbuilding, and ecosystem simulation must change the same objects:

```text
habitat tile -> route pressure -> defense placement -> card effect
             -> ecosystem feedback -> wave outcome -> browser validation
```

A template can manually write this integrated design into variables. WeaveMark
should instead express the mechanics as reusable specifications and let semantic
mingling propagate them through the final single specification.

## Results

- [`results/ablation-summary.md`](results/ablation-summary.md) records the
  structural measurements and best-variant finding.
- [`results/final-quality-analysis.md`](results/final-quality-analysis.md)
  compares the compiled outputs with the contrastive evaluation method.
