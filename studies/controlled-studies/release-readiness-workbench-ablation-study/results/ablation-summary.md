# Release Readiness Workbench Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A local-first release command center that turns release notes, docs, validation runs, screenshots, package artifacts, risks, waivers, and go/no-go decisions into one auditable workspace.


## Study role

- **Evidence class:** Realistic workflow/product application

- **Study role:** Headline structural-mingling evidence.

- **Semantic trace:** `release material -> readiness claim -> gate/evidence -> validation/failure -> action/waiver/decision -> launch/audit`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Manual brief](../specs/00-control-manual-release-readiness-workbench.weavemark.md) | Compact hand-written release-workbench request. | 55 | 0 | 55 | 1x | 5 | 90.9 | 90.9 |
| [[C2] Matched reusable-template control](../specs/01-control-template-release-readiness-workbench.weavemark.md) | Template shell with study-local release, storage, workspace, and validation partials. | 68 | 84 | 1,069 | 15.72x | 97.75 | 91.4 | 1,437.5 |
| [[T] WeaveMark treatment](../specs/02-treatment-promplet-release-readiness-workbench.weavemark.md) | Refines release, evidence, validation, decision, dashboard, notification, and programming layers. | 248 | 55 | 4,762 | 19.2x | 322 | 67.6 | 1,298.4 |

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
| Source-only leverage | 15.72 | 19.2 | win |
| Discounted fact units | 97.75 | 322 | win |
| Information density | 91.4 | 67.6 | loss |
| Information yield | 1,437.5 | 1,298.4 | loss |

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

- [T] WeaveMark treatment wins source-only leverage: 19.2 versus 15.72 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 322 versus 97.75 for [C2] Matched reusable-template control.
- Release gates, evidence quality, validation matrices, risks, waivers, actions, dashboards, and browser validation all shape one workflow.
- The treatment has higher source-only leverage than the matched reusable-template control.
- The final specification adds substantially more actionable release facts than the control.

## Failures and caveats

- [T] WeaveMark treatment loses information density: 67.6 versus 91.4 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment loses information yield: 1,298.4 versus 1,437.5 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 4,762 words versus 1,069 for [C2] Matched reusable-template control.
- The matched template is already strong and keeps higher information density.
- The treatment loses information yield versus the template because the WeaveMark source is longer while the template shell stays very compact.
- No downstream release-workbench implementation outcome has been measured.

## Conclusion

A strong headline study, with the honest caveat that the template remains denser and more source-efficient on the yield proxy.
