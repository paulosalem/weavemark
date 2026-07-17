# Crowd Factory Puzzle Ablation Summary

[View as HTML](ablation-summary.html)


## What the example is

A browser puzzle game about steering autonomous crowds through factory automation, belts, machines, crates, spatial pushing rules, hazards, and readable level constraints.


## Study role

- **Evidence class:** Game `@expand` study

- **Study role:** Focused expansion evidence where source concepts are already concrete.

- **Semantic trace:** `workers -> belts/machines -> crate pushing -> hazards -> readable levels`


## Variant metrics

| Variant | Role | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [[C1] Compact no-expand control](../specs/00-control-compact-no-expand-crowd-factory-puzzle.weavemark.md) | Compact source that names the puzzle inspirations without expansion. | 90 | 0 | 1,171 | 13.01x | 70 | 59.8 | 777.8 |
| [[C2] Matched-prose no-expand control](../specs/01-control-matched-prose-no-expand-crowd-factory-puzzle.weavemark.md) | Manual prose expansion without using `@expand`. | 182 | 0 | 1,314 | 7.22x | 89.25 | 67.9 | 490.4 |
| [[T] Expanded WeaveMark treatment](../specs/02-treatment-expand-crowd-factory-puzzle.weavemark.md) | Uses `@expand mode: intention` to unpack concept labels into mechanics. | 191 | 0 | 3,334 | 17.46x | 244.75 | 73.4 | 1,281.4 |

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
| Source-only leverage | 7.22 | 17.46 | win |
| Discounted fact units | 89.25 | 244.75 | win |
| Information density | 67.9 | 73.4 | win |
| Information yield | 490.4 | 1,281.4 | win |

## Contrastive gain/loss scores

Primary scores are **blind*** using `hybrid-derived-metrics-and-masked-review`: anonymous absolute 1..7 scores were frozen before reveal, then converted to the -3..+3 treatment-control scale. *Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.*

Scores compare [T] Expanded WeaveMark treatment against [C2] Matched-prose no-expand control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better).

| Criterion | Blind* score | Evidence |
|---|---:|---|
| Authoring leverage | +3 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 1 for the strongest control. |
| Information yield | +3 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 1 for the strongest control. |
| Grounded expressiveness | +2 | masked-source-output review method. Blind* absolute scores: 7 for [T] versus 3 for the strongest control. |
| Input readability | -1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 6 for the strongest control. |
| Output readability | +1 | masked-output review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| Constraint integration | +2 | masked-source-output review method. Blind* absolute scores: 6 for [T] versus 3 for the strongest control. |
| Reusable abstraction quality | +1 | masked-source review method. Blind* absolute scores: 6 for [T] versus 4 for the strongest control. |
| **Total** | **+11** | Net contrastive gain/loss. |

## Score definitions

- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Gains

- [T] Expanded WeaveMark treatment wins source-only leverage: 17.46 versus 7.22 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins discounted fact units: 244.75 versus 89.25 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information density: 73.4 versus 67.9 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information yield: 1,281.4 versus 490.4 for [C2] Matched-prose no-expand control.
- `@expand` keeps the source modular and still frames a coherent factory-crowd puzzle.
- The treatment wins the matched-prose control on the deterministic leverage, fact-unit, density, and yield proxies.
- It captures integration framing across autonomous workers, belts, machines, crates, hazards, and levels.

## Failures and caveats

- The source concepts are concrete enough that manual prose can unpack them very effectively.
- The matched-prose control remains an important fairness baseline even when the treatment wins the proxy metrics.
- This is saved-output semantic evidence; behavioral proof still requires downstream implementation/use.

## Conclusion

A positive `@expand` result: useful for clarity and framing, and currently ahead of matched prose on deterministic proxy metrics.
