# Evidence-to-Decision Workspace Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A local-first analyst workspace that turns documents, notes, links, news, claims, contradictions, options, decisions, and follow-up actions into an auditable decision surface.


## Study role

- **Evidence class:** Realistic workflow/product application

- **Study role:** Headline structural-mingling evidence.

- **Semantic trace:** `source -> claim -> evidence/contradiction -> ACH -> decision gate -> action/output`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Manual brief](../specs/00-control-manual-evidence-decision-workspace.weavemark.md) | Compact hand-written evidence-to-decision workspace request. | 55 | 0 | 55 | 1x | 5 | 90.9 | 90.9 |
| [[C2] Matched reusable-template control](../specs/01-control-template-evidence-decision-workspace.weavemark.md) | Template shell with evidence, decision, local-first, workspace, and validation partials. | 67 | 111 | 1,092 | 16.3x | 96.5 | 88.4 | 1,440.3 |
| [[T] WeaveMark treatment](../specs/02-treatment-promplet-evidence-decision-workspace.weavemark.md) | Refines source fidelity, ACH, contradiction handling, decision gates, local-first architecture, and AI safety. | 249 | 66 | 6,632 | 26.63x | 396.5 | 59.8 | 1,592.4 |

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
| Source-only leverage | 16.3 | 26.63 | win |
| Discounted fact units | 96.5 | 396.5 | win |
| Information density | 88.4 | 59.8 | loss |
| Information yield | 1,440.3 | 1,592.4 | win |

## Contrastive gain/loss scores

Primary scores are **blind*** using `hybrid-derived-metrics-and-masked-review`: anonymous absolute 1..7 scores were frozen before reveal, then converted to the -3..+3 treatment-control scale. *Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.*

Scores compare [T] WeaveMark treatment against [C2] Matched reusable-template control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better).

| Criterion | Blind* score | Evidence |
|---|---:|---|
| Authoring leverage | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Information yield | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Grounded expressiveness | +2 | masked-source-output review method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Input readability | +1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 4 for the strongest control. |
| Output readability | +1 | masked-output review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| Constraint integration | +2 | masked-source-output review method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Reusable abstraction quality | +1 | masked-source review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| **Total** | **+11** | Net contrastive gain/loss. |

## Score definitions

- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Gains

- [T] WeaveMark treatment wins source-only leverage: 26.63 versus 16.3 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 396.5 versus 96.5 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins information yield: 1,592.4 versus 1,440.3 for [C2] Matched reusable-template control.
- The treatment converts evidence quality, ACH, contradictions, decision gates, actions, storage, UI, APIs, and AI safety into one architecture.
- It wins leverage and information yield against the matched reusable-template control.
- The final specification has the largest fact-unit count in the study corpus.

## Failures and caveats

- [T] WeaveMark treatment loses information density: 59.8 versus 88.4 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 6,632 words versus 1,092 for [C2] Matched reusable-template control.
- The matched template remains denser.
- Output readability is mixed because the treatment is much longer and requires careful navigation.
- No analyst-task or implementation outcome has been measured.

## Conclusion

The strongest realistic application result on total semantic content and yield, though not on compactness.
