# Research Brief Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Manual request | [00-control-manual-research-brief.md](../outputs/compiled-prompts/00-control-manual-research-brief.md) | 7 | 44 |
| [C2] Matched reusable-template control | [01-control-template-research-brief.md](../outputs/compiled-prompts/01-control-template-research-brief.md) | 37 | 332 |
| [T] WeaveMark treatment | [02-treatment-refined-research-brief.md](../outputs/compiled-prompts/02-treatment-refined-research-brief.md) | 227 | 1,718 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Manual request

> Prepare a research brief on grid-scale energy storage for city planners.

### [C2] Matched reusable-template control

>   impact missing inputs near the top.
> - Use a balanced source mix: public agencies, operators, deployments,
>   independent technical reviews, skeptical economic analysis, vendor claims
>   clearly labeled, recent news when recency matters, technical/legal/financial

### [T] WeaveMark treatment

> # Refined Research Brief

### [T] WeaveMark treatment source seam

> @promplet version: 0.7

## Contrastive gain/loss scores

Primary scores are **blind*** using `hybrid-derived-metrics-and-masked-review`: anonymous absolute 1..7 scores were frozen before reveal, then converted to the -3..+3 treatment-control scale. *Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.*

Scores compare [T] WeaveMark treatment against [C2] Matched reusable-template control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better).

| Criterion | Blind* score | Evidence |
|---|---:|---|
| Authoring leverage | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Information yield | +2 | derived-evidence method. Blind* absolute scores: 7 for [T] versus 4 for the strongest control. |
| Grounded expressiveness | +1 | masked-source-output review method. Blind* absolute scores: 5 for [T] versus 4 for the strongest control. |
| Input readability | +1 | masked-source review method. Blind* absolute scores: 5 for [T] versus 4 for the strongest control. |
| Output readability | +1 | masked-output review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| Constraint integration | +1 | masked-source-output review method. Blind* absolute scores: 6 for [T] versus 4 for the strongest control. |
| Reusable abstraction quality | +1 | masked-source review method. Blind* absolute scores: 6 for [T] versus 5 for the strongest control. |
| **Total** | **+9** | Net contrastive gain/loss. |

## Score definitions

- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## What improved

- [T] WeaveMark treatment wins source-only leverage: 8.34 versus 8.1 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 113.5 versus 22 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins information yield: 551 versus 536.6 for [C2] Matched reusable-template control.
- The treatment adds richer epistemic obligations: source families, contradictions, alternatives, evidence caveats, and explainability.
- It has a modest leverage and information-yield edge over the matched template.
- The comparison stays single-output after removing multi-artifact variants.

## What failed or did not improve

- [T] WeaveMark treatment loses information density: 66.1 versus 66.3 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 1,718 words versus 332 for [C2] Matched reusable-template control.
- The measured leverage and yield wins are small.
- The matched template has nearly identical information density.
- No downstream researcher outcome, citation accuracy, or factuality result has been measured.

## Interpretation

A modest but realistic supporting win whose value is quality-lens integration more than raw metric dominance. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
