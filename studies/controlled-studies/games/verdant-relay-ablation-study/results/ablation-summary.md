# Verdant Relay Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A browser game about defending a living railway garden from blight by combining tower-defense route pressure, deckbuilder card choices, ecosystem feedback, original assets, and browser validation.


## Study role

- **Evidence class:** Game implementation-specification study

- **Study role:** Headline-compatible structural-mingling stress test.

- **Semantic trace:** `habitat -> route pressure -> defense/card choice -> ecosystem feedback -> browser validation`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Manual brief](../specs/00-control-compact-manual-verdant-relay.weavemark.md) | Compact hand-written Verdant Relay request. | 57 | 0 | 57 | 1x | 5 | 87.7 | 87.7 |
| [[C2] Matched reusable-template control](../specs/01-control-template-verdant-relay.weavemark.md) | Template shell with browser-game, tower-defense, deckbuilding, ecosystem, asset, and validation partials. | 84 | 51 | 954 | 11.36x | 83 | 87 | 988.1 |
| [[T] WeaveMark treatment](../specs/02-treatment-promplet-verdant-relay.weavemark.md) | Refines and expands mechanics, production requirements, assets, and validation into one playable first-build specification. | 303 | 5 | 5,567 | 18.37x | 289.5 | 52 | 955.4 |

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
| Source-only leverage | 11.36 | 18.37 | win |
| Discounted fact units | 83 | 289.5 | win |
| Information density | 87 | 52 | loss |
| Information yield | 988.1 | 955.4 | loss |

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

- [T] WeaveMark treatment wins source-only leverage: 18.37 versus 11.36 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 289.5 versus 83 for [C2] Matched reusable-template control.
- The treatment integrates tower defense, deckbuilding, ecosystem simulation, assets, state, balance, UI, and validation into one playable trace.
- It wins leverage, information yield, and total fact units against the matched template.
- It is a useful stress test for whether several reusable mechanics can shape one final specification.

## Failures and caveats

- [T] WeaveMark treatment loses information density: 52 versus 87 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment loses information yield: 955.4 versus 988.1 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 5,567 words versus 954 for [C2] Matched reusable-template control.
- The treatment is much longer and less dense than the matched template.
- It is a synthetic game concept, so it should not carry the main real-work application claim.
- No generated browser game has been implemented and tested yet.

## Conclusion

A strong structural-mingling stress test, with length/density and synthetic-domain caveats.
