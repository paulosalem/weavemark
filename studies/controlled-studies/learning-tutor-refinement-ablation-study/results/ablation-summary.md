# Learning Tutor Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A pasteable linear-algebra tutor prompt that teaches through geometric intuition, Socratic questions, misconception diagnosis, adaptive practice, and delayed review.


## Study role

- **Evidence class:** Realistic non-programming assistant task

- **Study role:** Supporting refinement evidence.

- **Semantic trace:** `learner profile -> concept explanation -> diagnosis -> practice ladder -> delayed review`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Compact manual](../specs/00-control-compact-manual-linear-algebra-tutor.weavemark.md) | Short tutor request that leaves pedagogy mostly implicit. | 42 | 0 | 42 | 1x | 3 | 71.4 | 71.4 |
| [[C2] Matched prose control](../specs/01-control-matched-prose-linear-algebra-tutor.weavemark.md) | Manual prose version of the intended teaching method. | 236 | 0 | 236 | 1x | 18 | 76.3 | 76.3 |
| [[T] WeaveMark treatment](../specs/02-treatment-refined-expand-linear-algebra-tutor.weavemark.md) | Refines reusable teaching methods and expands the tutoring loop. | 164 | 6 | 2,066 | 12.6x | 141.25 | 68.4 | 861.3 |

## Metric definitions

- **Source words:** Words in the local study source for a variant; this is the local authoring burden.
- **Variable words:** Words in a variant's explicit input payload, when a template or refinement uses one.
- **Output words:** Words in the saved compiled final artifact.
- **Leverage:** Output words divided by local source words; larger means more final artifact per local word, not quality by itself.
- **Fact units:** Novelty-weighted semantic fact units extracted from the output by deterministic rules.
- **Density:** Discounted fact units per 1,000 output words; higher means a more information-dense output.
- **Yield:** Discounted fact units per 1,000 local source words; higher means more semantic material per local authoring word.

## Treatment-control comparison

The strongest control is [C2] Matched prose control. The treatment is [T] WeaveMark treatment.

| Metric | [C2] Matched prose control | [T] WeaveMark treatment | Direction |
|---|---:|---:|---|
| Source-only leverage | 1 | 12.6 | win |
| Discounted fact units | 18 | 141.25 | win |
| Information density | 76.3 | 68.4 | loss |
| Information yield | 76.3 | 861.3 | win |

## Contrastive gain/loss scores

Primary scores are **blind*** using `hybrid-derived-metrics-and-masked-review`: anonymous absolute 1..7 scores were frozen before reveal, then converted to the -3..+3 treatment-control scale. *Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.*

Scores compare [T] WeaveMark treatment against [C2] Matched prose control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better).

| Criterion | Blind* score | Evidence |
|---|---:|---|
| Authoring leverage | +3 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 1 for the strongest control. |
| Information yield | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Grounded expressiveness | +3 | masked-source-output review method. Blind* absolute scores: 7 for [T] versus 2 for the strongest control. |
| Input readability | -1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 6 for the strongest control. |
| Output readability | +2 | masked-output review method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Constraint integration | +3 | masked-source-output review method. Blind* absolute scores: 7 for [T] versus 2 for the strongest control. |
| Reusable abstraction quality | +2 | masked-source review method. Blind* absolute scores: 6 for [T] versus 2 for the strongest control. |
| **Total** | **+14** | Net contrastive gain/loss. |

## Score definitions

- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Gains

- [T] WeaveMark treatment wins source-only leverage: 12.6 versus 1 for [C2] Matched prose control.
- [T] WeaveMark treatment wins discounted fact units: 141.25 versus 18 for [C2] Matched prose control.
- [T] WeaveMark treatment wins information yield: 861.3 versus 76.3 for [C2] Matched prose control.
- The treatment uses fewer local source words than the matched-prose control and produces far more semantic content.
- Pedagogy, diagnosis, practice, branching, and delayed review become one concrete tutor behavior.
- This is a strong non-programming demonstration of reusable refinement.

## Failures and caveats

- [T] WeaveMark treatment loses information density: 68.4 versus 76.3 for [C2] Matched prose control.
- [T] WeaveMark treatment is much longer: 2,066 words versus 236 for [C2] Matched prose control.
- The artifact is still a prompt for a tutor, not a measured learner outcome.
- Because the control is matched prose rather than a reusable-template control, it is not apples-to-apples with headline software-specification studies.
- The final tutor prompt is much longer, so usability depends on whether the receiving model follows the structure.

## Conclusion

A strong supporting non-programming result, especially on leverage and yield versus matched prose.
