# Study: Research Brief Refinement Ablation

This study demonstrates WeaveMark for non-programming prompts. The goal is a
concise research brief instruction that stays responsible about evidence,
context limits, source families, contradictions, and explainability.

## Variants

| Variant | File | Purpose |
|---|---|---|
| Manual request | [`specs/00-control-manual-research-brief.weavemark.md`](specs/00-control-manual-research-brief.weavemark.md) | A compact manually written research request. |
| Matched reusable-template control | [`specs/01-control-template-research-brief.weavemark.md`](specs/01-control-template-research-brief.weavemark.md) | A deterministic template shell using a study-local reusable research-brief partial plus local mission and context variables. |
| WeaveMark refinement | [`specs/02-treatment-refined-research-brief.weavemark.md`](specs/02-treatment-refined-research-brief.weavemark.md) | Reuses context sufficiency, evidence quality, research rigor, news quality, comparative alternatives, and explainability fragments. |

## What improved most

The largest gain came from refinement of epistemic obligations. A template can
ask for citations and caveats, but WeaveMark can reuse multiple abstract
quality lenses and let compilation mingle them with the concrete research topic.

The study stays single-output so its comparison remains straightforward:
manual request, matched reusable-template control, and WeaveMark treatment.

## Commands

```bash
weavemark studies/controlled-studies/research-brief-ablation-study/specs/02-treatment-refined-research-brief.weavemark.md \
  --vars-file studies/controlled-studies/research-brief-ablation-study/inputs/energy-storage.json \
  --output studies/controlled-studies/research-brief-ablation-study/outputs/compiled-prompts/02-treatment-refined-research-brief.md \
  --no-file-summary
```

See [`results/ablation-summary.md`](results/ablation-summary.md) for the
structural experiment notes and
[`results/final-quality-analysis.md`](results/final-quality-analysis.md) for the
compiled prompt contrastive analysis.
