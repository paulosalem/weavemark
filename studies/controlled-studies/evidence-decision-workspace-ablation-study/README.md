# Evidence-to-Decision Workspace Ablation Study

This study tests whether WeaveMark can produce a vastly stronger **single
final specification** without relying on prompt packs.

The target is a realistic application: a local-first workspace that turns messy
documents, notes, links, news, claims, contradictions, options, decisions, and
follow-up actions into one auditable operating surface.

## Variants

1. [`00-control-manual-evidence-decision-workspace.weavemark.md`](specs/00-control-manual-evidence-decision-workspace.weavemark.md)
   - compact manual prompt;
2. [`01-control-template-evidence-decision-workspace.weavemark.md`](specs/01-control-template-evidence-decision-workspace.weavemark.md)
   - matched reusable-template control rendered from study-local partials;
3. [`02-treatment-promplet-evidence-decision-workspace.weavemark.md`](specs/02-treatment-promplet-evidence-decision-workspace.weavemark.md)
   - WeaveMark treatment using semantic `@refine` and focused `@expand`,
     compiled to one final specification.

## Why this should be hard for templating

The final app must reinterpret every major surface around one trace:

```text
source -> normalized fact -> claim -> evidence/contradiction -> hypothesis/option
       -> decision gate -> action/output -> provenance/audit history
```

A template can include detailed prose for each section, but it cannot
semantically propagate this trace through storage, UI, APIs, automation,
validation, privacy, and failure handling unless the author manually writes that
whole transformed design into the variable payload.

## Results

- [Ablation summary](results/ablation-summary.md)
- [Contrastive analysis](results/final-quality-analysis.md)
