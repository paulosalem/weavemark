# Research Brief Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A concise research-brief instruction for energy-storage strategy that requires source families, context limits, contradictions, alternatives, caveats, and explainable evidence handling.


## Study role

- **Evidence class:** Realistic non-programming research workflow

- **Study role:** Supporting refinement evidence.

- **Semantic trace:** `topic/context -> source quality -> contradiction -> alternatives -> explainable brief`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Manual request](../specs/00-control-manual-research-brief.weavemark.md) | Compact hand-written research brief request. | 44 | 0 | 44 | 1x | 4 | 90.9 | 90.9 |
| [[C2] Matched reusable-template control](../specs/01-control-template-research-brief.weavemark.md) | Template shell with study-local research-brief partial and variables. | 41 | 105 | 332 | 8.1x | 22 | 66.3 | 536.6 |
| [[T] WeaveMark treatment](../specs/02-treatment-refined-research-brief.weavemark.md) | Refines context sufficiency, evidence quality, research rigor, news quality, alternatives, and explainability. | 206 | 97 | 1,718 | 8.34x | 113.5 | 66.1 | 551 |

## Metric definitions

- **Source words:** Words in the local study source for a variant; this is the local authoring burden.
- **Variable words:** Words in a variant's explicit input payload, when a template or refinement uses one.
- **Output words:** Words in the saved compiled final artifact.
- **Leverage:** Output words divided by local source words; larger means more final artifact per local word, not quality by itself.
- **Fact units:** Novelty-weighted semantic fact units extracted from the output by deterministic rules.
- **Density:** Discounted fact units per 1,000 output words; higher means a more information-dense output.
- **Yield:** Discounted fact units per 1,000 local source words; higher means more semantic material per local authoring word.

## Treatment-control comparison

The strongest control is [C2] Matched reusable-template control. The treatment is [T] WeaveMark treatment.

| Metric | [C2] Matched reusable-template control | [T] WeaveMark treatment | Direction |
|---|---:|---:|---|
| Source-only leverage | 8.1 | 8.34 | win |
| Discounted fact units | 22 | 113.5 | win |
| Information density | 66.3 | 66.1 | loss |
| Information yield | 536.6 | 551 | win |

## Contrastive gain/loss scores

Primary scores are **blind*** using `hybrid-derived-metrics-and-masked-review`: anonymous absolute 1..7 scores were frozen before reveal, then converted to the -3..+3 treatment-control scale. *Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.*

Scores compare [T] WeaveMark treatment against [C2] Matched reusable-template control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better).

| Criterion | Blind* score | Evidence |
|---|---:|---|
| Authoring leverage | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Information yield | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Grounded expressiveness | +1 | masked-source-output review method. Blind* absolute scores: 5 for [T] versus 4 for the strongest control. |
| Input readability | +1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 4 for the strongest control. |
| Output readability | +1 | masked-output review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| Constraint integration | +1 | masked-source-output review method. Blind* absolute scores: 6 for [T] versus 4 for the strongest control. |
| Reusable abstraction quality | +1 | masked-source review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| **Total** | **+9** | Net contrastive gain/loss. |

## Score definitions

- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Gains

- [T] WeaveMark treatment wins source-only leverage: 8.34 versus 8.1 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 113.5 versus 22 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins information yield: 551 versus 536.6 for [C2] Matched reusable-template control.
- The treatment adds richer epistemic obligations: source families, contradictions, alternatives, evidence caveats, and explainability.
- It has a modest leverage and information-yield edge over the matched template.
- The comparison stays single-output after removing multi-artifact variants.

## Failures and caveats

- [T] WeaveMark treatment loses information density: 66.1 versus 66.3 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 1,718 words versus 332 for [C2] Matched reusable-template control.
- The measured leverage and yield wins are small.
- The matched template has nearly identical information density.
- No downstream researcher outcome, citation accuracy, or factuality result has been measured.

## Conclusion

A modest but realistic supporting win whose value is quality-lens integration more than raw metric dominance.
