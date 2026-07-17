# Evidence-to-Decision Workspace Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Manual brief | [00-control-manual-evidence-decision-workspace.md](../outputs/compiled-prompts/00-control-manual-evidence-decision-workspace.md) | 9 | 55 |
| [C2] Matched reusable-template control | [01-control-template-evidence-decision-workspace.md](../outputs/compiled-prompts/01-control-template-evidence-decision-workspace.md) | 152 | 1,092 |
| [T] WeaveMark treatment | [02-treatment-promplet-evidence-decision-workspace.md](../outputs/compiled-prompts/02-treatment-promplet-evidence-decision-workspace.md) | 1,675 | 6,632 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Manual brief

> Design a local-first web application that helps me collect documents, notes,
> links, and news; audit claims and evidence; compare explanations and options;
> make decisions; assign follow-up actions; and preserve provenance.

### [C2] Matched reusable-template control

> - This is the coherent implementation-ready specification for Evidence-to-Decision Workspace.
> - Treat this specification as the source of truth for a programming agent or human engineer.
> - Include first-build scope, out-of-scope items, architecture, domain model,
>   durable records, workflows, UI surfaces, automation rules, validation plan,

### [T] WeaveMark treatment

> Build **Evidence-to-Decision Workspace**: a local-first web application where messy sources become traceable claims, evidence, contradictions, explanations, decisions, actions, alerts, and reusable outputs. The product is an evidence command center for:

### [T] WeaveMark treatment source seam

> Design @{app_name}: a local-first workspace where messy sources become
> traceable claims, evidence, contradictions, explanations, decisions, actions,
> alerts, and reusable outputs.

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

## What improved

- [T] WeaveMark treatment wins source-only leverage: 26.63 versus 16.3 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 396.5 versus 96.5 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins information yield: 1,592.4 versus 1,440.3 for [C2] Matched reusable-template control.
- The treatment converts evidence quality, ACH, contradictions, decision gates, actions, storage, UI, APIs, and AI safety into one architecture.
- It wins leverage and information yield against the matched reusable-template control.
- The final specification has the largest fact-unit count in the study corpus.

## What failed or did not improve

- [T] WeaveMark treatment loses information density: 59.8 versus 88.4 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 6,632 words versus 1,092 for [C2] Matched reusable-template control.
- The matched template remains denser.
- Output readability is mixed because the treatment is much longer and requires careful navigation.
- No analyst-task or implementation outcome has been measured.

## Interpretation

The strongest realistic application result on total semantic content and yield, though not on compactness. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
