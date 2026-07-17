# Learning Tutor Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Compact manual | [00-control-compact-manual-linear-algebra-tutor.md](../outputs/compiled-prompts/00-control-compact-manual-linear-algebra-tutor.md) | 5 | 42 |
| [C2] Matched prose control | [01-control-matched-prose-linear-algebra-tutor.md](../outputs/compiled-prompts/01-control-matched-prose-linear-algebra-tutor.md) | 35 | 236 |
| [T] WeaveMark treatment | [02-treatment-refined-expand-linear-algebra-tutor.md](../outputs/compiled-prompts/02-treatment-refined-expand-linear-algebra-tutor.md) | 279 | 2,066 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Compact manual

> # Compact Manual Linear Algebra Tutor

### [C2] Matched prose control

> The tutor should teach a motivated returning beginner who remembers algebra but
> has weak geometric intuition. The tutor should not lecture all at once. It
> should begin by probing the learner's current mental model, ask one focused
> question at a time, and adapt based on the answer.

### [T] WeaveMark treatment

> # Linear Algebra Tutor Prompt

### [T] WeaveMark treatment source seam

> The final prompt must be one coherent tutor prompt. It should define the tutor
> role, first interaction, adaptive question sequence, misconception diagnosis,
> practice ladder, feedback rules, and final mastery check.

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

## What improved

- [T] WeaveMark treatment wins source-only leverage: 12.6 versus 1 for [C2] Matched prose control.
- [T] WeaveMark treatment wins discounted fact units: 141.25 versus 18 for [C2] Matched prose control.
- [T] WeaveMark treatment wins information yield: 861.3 versus 76.3 for [C2] Matched prose control.
- The treatment uses fewer local source words than the matched-prose control and produces far more semantic content.
- Pedagogy, diagnosis, practice, branching, and delayed review become one concrete tutor behavior.
- This is a strong non-programming demonstration of reusable refinement.

## What failed or did not improve

- [T] WeaveMark treatment loses information density: 68.4 versus 76.3 for [C2] Matched prose control.
- [T] WeaveMark treatment is much longer: 2,066 words versus 236 for [C2] Matched prose control.
- The artifact is still a prompt for a tutor, not a measured learner outcome.
- Because the control is matched prose rather than a reusable-template control, it is not apples-to-apples with headline software-specification studies.
- The final tutor prompt is much longer, so usability depends on whether the receiving model follows the structure.

## Interpretation

A strong supporting non-programming result, especially on leverage and yield versus matched prose. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
