# Transit City Swarm Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A browser strategy game that combines transit-network drawing, city growth, and ant-colony pathfinding through pheromone-style demand trails and congestion feedback.


## Study role

- **Evidence class:** Game `@expand` study

- **Study role:** Focused expansion evidence with a matched-prose comparison.

- **Semantic trace:** `transit network -> city growth -> swarm demand trails -> congestion -> player routing`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Compact no-expand control](../specs/00-control-compact-no-expand-transit-city-swarm.weavemark.md) | Compact source that names the inspirations without expansion. | 89 | 0 | 1,024 | 11.51x | 69.5 | 67.9 | 780.9 |
| [[C2] Matched-prose no-expand control](../specs/01-control-matched-prose-no-expand-transit-city-swarm.weavemark.md) | Manual prose expansion without using `@expand`. | 180 | 0 | 1,410 | 7.83x | 95 | 67.4 | 527.8 |
| [[T] Expanded WeaveMark treatment](../specs/02-treatment-expand-transit-city-swarm.weavemark.md) | Uses `@expand mode: intention` to unpack concept labels into mechanics. | 177 | 0 | 2,895 | 16.36x | 213.5 | 73.7 | 1,206.2 |

## Metric definitions

- **Source words:** Words in the local study source for a variant; this is the local authoring burden.
- **Variable words:** Words in a variant's explicit input payload, when a template or refinement uses one.
- **Output words:** Words in the saved compiled final artifact.
- **Leverage:** Output words divided by local source words; larger means more final artifact per local word, not quality by itself.
- **Fact units:** Novelty-weighted semantic fact units extracted from the output by deterministic rules.
- **Density:** Discounted fact units per 1,000 output words; higher means a more information-dense output.
- **Yield:** Discounted fact units per 1,000 local source words; higher means more semantic material per local authoring word.

## Treatment-control comparison

The strongest control is [C2] Matched-prose no-expand control. The treatment is [T] Expanded WeaveMark treatment.

| Metric | [C2] Matched-prose no-expand control | [T] Expanded WeaveMark treatment | Direction |
|---|---:|---:|---|
| Source-only leverage | 7.83 | 16.36 | win |
| Discounted fact units | 95 | 213.5 | win |
| Information density | 67.4 | 73.7 | win |
| Information yield | 527.8 | 1,206.2 | win |

## Contrastive gain/loss scores

Primary scores are **blind*** using `hybrid-derived-metrics-and-masked-review`: anonymous absolute 1..7 scores were frozen before reveal, then converted to the -3..+3 treatment-control scale. *Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.*

Scores compare [T] Expanded WeaveMark treatment against [C2] Matched-prose no-expand control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better).

| Criterion | Blind* score | Evidence |
|---|---:|---|
| Authoring leverage | +3 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 1 for the strongest control. |
| Information yield | +3 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 1 for the strongest control. |
| Grounded expressiveness | +1 | masked-source-output review method. Blind* absolute scores: 4 for [T] versus 3 for the strongest control. |
| Input readability | -1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 6 for the strongest control. |
| Output readability | +0 | masked-output review method. Blind* absolute scores: 5 for [T] versus 5 for the strongest control. |
| Constraint integration | +1 | masked-source-output review method. Blind* absolute scores: 4 for [T] versus 3 for the strongest control. |
| Reusable abstraction quality | +1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 4 for the strongest control. |
| **Total** | **+8** | Net contrastive gain/loss. |

## Score definitions

- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Gains

- [T] Expanded WeaveMark treatment wins source-only leverage: 16.36 versus 7.83 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins discounted fact units: 213.5 versus 95 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information density: 73.7 versus 67.4 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information yield: 1,206.2 versus 527.8 for [C2] Matched-prose no-expand control.
- `@expand` makes compact concept labels readable and operational against the compact control.
- The treatment clearly states the integrated mechanic that connects network drawing, city growth, and demand trails.
- It now wins the matched-prose control on the deterministic leverage, fact-unit, density, and yield proxies.

## Failures and caveats

- The matched-prose control remains the fairness baseline because it spells out the same inspiration set without `@expand`.
- The treatment is a longer generated artifact, so this is not an output-brevity claim.
- This is saved-output semantic evidence; behavioral proof still requires downstream implementation/use.

## Conclusion

A useful `@expand` study where compact named inspirations now produce stronger deterministic proxy metrics than matched prose, while still needing behavioral proof.
