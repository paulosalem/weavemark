# Intelligence-to-Execution Kanban Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A local-first Kanban board for monitoring selected topics, turning signals into cards, deciding actions, delegating work, tracking status, and preserving output lineage.


## Study role

- **Evidence class:** Realistic workflow/product application

- **Study role:** Headline structural-mingling evidence.

- **Semantic trace:** `signal -> card -> board transition -> decision/action/delegation -> output`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Manual brief](../specs/00-control-manual-intelligence-execution-kanban.weavemark.md) | Compact hand-written Kanban workspace request. | 67 | 0 | 67 | 1x | 6 | 89.6 | 89.6 |
| [[C2] Matched reusable-template control](../specs/01-control-template-intelligence-execution-kanban.weavemark.md) | Template shell with monitoring, local-first storage, workspace, and validation partials. | 65 | 74 | 1,066 | 16.4x | 96.75 | 90.8 | 1,488.5 |
| [[T] WeaveMark treatment](../specs/02-treatment-promplet-intelligence-execution-kanban.weavemark.md) | Refines monitoring, signal-to-action workflow, Kanban state, decisions, alerts, and validation. | 219 | 54 | 4,177 | 19.07x | 137.75 | 33 | 629 |

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
| Source-only leverage | 16.4 | 19.07 | win |
| Discounted fact units | 96.75 | 137.75 | win |
| Information density | 90.8 | 33 | loss |
| Information yield | 1,488.5 | 629 | loss |

## Contrastive gain/loss scores

Primary scores are **blind*** using `hybrid-derived-metrics-and-masked-review`: anonymous absolute 1..7 scores were frozen before reveal, then converted to the -3..+3 treatment-control scale. *Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.*

Scores compare [T] WeaveMark treatment against [C2] Matched reusable-template control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better).

| Criterion | Blind* score | Evidence |
|---|---:|---|
| Authoring leverage | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Information yield | -2 | derived-evidence method. Blind* absolute scores: 4 for [T] versus 7 for the strongest control. |
| Grounded expressiveness | +2 | masked-source-output review method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Input readability | +1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 4 for the strongest control. |
| Output readability | +1 | masked-output review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| Constraint integration | +2 | masked-source-output review method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Reusable abstraction quality | +1 | masked-source review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| **Total** | **+7** | Net contrastive gain/loss. |

## Score definitions

- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Gains

- [T] WeaveMark treatment wins source-only leverage: 19.07 versus 16.4 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 137.75 versus 96.75 for [C2] Matched reusable-template control.
- The treatment propagates the signal-to-card trace through board states, delegation, notifications, APIs, activity history, and acceptance criteria.
- It produces much more total semantic content than the matched template while preserving a single implementation specification.
- The source keeps the domain abstract while reusable work-intelligence refinements define concrete responsibilities.

## Failures and caveats

- [T] WeaveMark treatment loses information density: 33 versus 90.8 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment loses information yield: 629 versus 1,488.5 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 4,177 words versus 1,066 for [C2] Matched reusable-template control.
- The matched template has higher information density.
- The treatment loses information yield against the template because the reusable-template shell is extremely compact.
- No generated Kanban implementation has been behaviorally compared yet.

## Conclusion

A strong realistic study for semantic propagation, with a measured density/yield loss that should stay visible.
