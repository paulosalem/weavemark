# Crowd Factory Puzzle Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Compact no-expand control | [00-control-compact-no-expand-crowd-factory-puzzle.md](../outputs/compiled-prompts/00-control-compact-no-expand-crowd-factory-puzzle.md) | 104 | 1,171 |
| [C2] Matched-prose no-expand control | [01-control-matched-prose-no-expand-crowd-factory-puzzle.md](../outputs/compiled-prompts/01-control-matched-prose-no-expand-crowd-factory-puzzle.md) | 116 | 1,314 |
| [T] Expanded WeaveMark treatment | [02-treatment-expand-crowd-factory-puzzle.md](../outputs/compiled-prompts/02-treatment-expand-crowd-factory-puzzle.md) | 486 | 3,334 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Compact no-expand control

> - autonomous crowd agents that move according to simple rules and must be guided indirectly;
> - factory automation systems such as belts, gates, routers, converters, buffers, counters, and resource transformations;
> - spatial pushing puzzles where the player repositions crates, machines, blockers, or other objects to create workable paths.

### [C2] Matched-prose no-expand control

> The final design must not read like three pasted-together modules. It must define a single integrated mechanic: how the player indirectly routes autonomous workers, uses belts and machines to transform resources, and solves spatial pushing constraints within a realistic first-build scope.

### [T] Expanded WeaveMark treatment

> ## 5. Integrated Mechanics

### [T] Expanded WeaveMark treatment source seam

>   @expand mode: intention
>     Factory automation belts and converters: conveyor routing, machines, inputs
>     and outputs, throughput, bottlenecks, timing, resource transformation, and
>     compact production chains.

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

## What improved

- [T] Expanded WeaveMark treatment wins source-only leverage: 17.46 versus 7.22 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins discounted fact units: 244.75 versus 89.25 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information density: 73.4 versus 67.9 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information yield: 1,281.4 versus 490.4 for [C2] Matched-prose no-expand control.
- `@expand` keeps the source modular and still frames a coherent factory-crowd puzzle.
- The treatment wins the matched-prose control on the deterministic leverage, fact-unit, density, and yield proxies.
- It captures integration framing across autonomous workers, belts, machines, crates, hazards, and levels.

## What failed or did not improve

- The source concepts are concrete enough that manual prose can unpack them very effectively.
- The matched-prose control remains an important fairness baseline even when the treatment wins the proxy metrics.
- This is saved-output semantic evidence; behavioral proof still requires downstream implementation/use.

## Interpretation

A positive `@expand` result: useful for clarity and framing, and currently ahead of matched prose on deterministic proxy metrics. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
