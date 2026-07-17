# Orbital Drift Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A browser racing game about piloting a small craft through asteroid fields, gravity wells, orbital gates, lap routing, hazards, scoring, restart, and browser validation.


## Study role

- **Evidence class:** Game implementation-specification study

- **Study role:** Supporting game-programming specification evidence.

- **Semantic trace:** `ship control -> orbital hazards -> race loop -> browser implementation -> validation`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Manual brief](../specs/00-control-manual-orbital-drift.weavemark.md) | Minimal hand-written Orbital Drift request. | 52 | 0 | 52 | 1x | 5 | 96.2 | 96.2 |
| [[C2] Matched reusable-template control](../specs/01-control-template-orbital-drift.weavemark.md) | Template shell with game, browser implementation, asset, and validation partials. | 61 | 61 | 672 | 11.02x | 55 | 81.8 | 901.6 |
| [[T] WeaveMark treatment](../specs/02-treatment-promplet-orbital-drift.weavemark.md) | Refines software-spec, web-game, and Playwright MCP validation layers. | 152 | 0 | 3,467 | 22.81x | 228.25 | 65.8 | 1,501.6 |

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
| Source-only leverage | 11.02 | 22.81 | win |
| Discounted fact units | 55 | 228.25 | win |
| Information density | 81.8 | 65.8 | loss |
| Information yield | 901.6 | 1,501.6 | win |

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

- [T] WeaveMark treatment wins source-only leverage: 22.81 versus 11.02 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 228.25 versus 55 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins information yield: 1,501.6 versus 901.6 for [C2] Matched reusable-template control.
- The treatment has a very large authoring-leverage and information-yield win over the matched template.
- Browser-game architecture, controls, states, hazards, restart, scoring, and validation are integrated rather than appended.
- The cleaned study is now a single named game instead of a broad multi-variant showcase.

## Failures and caveats

- [T] WeaveMark treatment loses information density: 65.8 versus 81.8 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 3,467 words versus 672 for [C2] Matched reusable-template control.
- The product theme is still synthetic compared with the real workflow/product studies.
- The matched template is shorter and denser.
- No actual browser game implementation has been generated and tested as behavioral proof.

## Conclusion

A strong game-specification result, best used as supporting implementation-spec evidence rather than the main claim.
