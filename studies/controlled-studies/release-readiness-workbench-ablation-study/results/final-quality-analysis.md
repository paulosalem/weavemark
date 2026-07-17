# Release Readiness Workbench Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Manual brief | [00-control-manual-release-readiness-workbench.md](../outputs/compiled-prompts/00-control-manual-release-readiness-workbench.md) | 9 | 55 |
| [C2] Matched reusable-template control | [01-control-template-release-readiness-workbench.md](../outputs/compiled-prompts/01-control-template-release-readiness-workbench.md) | 151 | 1,069 |
| [T] WeaveMark treatment | [02-treatment-promplet-release-readiness-workbench.md](../outputs/compiled-prompts/02-treatment-promplet-release-readiness-workbench.md) | 575 | 4,762 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Manual brief

> Design a local-first web application that helps prepare a software release. It
> should collect release tasks, evidence, validation results, docs, examples, risks,
> and go/no-go decisions in one workspace.

### [C2] Matched reusable-template control

>   limitations, linked claim, and release impact.
> - Critical gates should block release unless explicitly waived with rationale,
>   owner, approver, expiry, accepted risk, and revisit trigger.
> - Validation checks need expected proof, owner, status, last run, failure meaning,

### [T] WeaveMark treatment

> Build **Release Readiness Workbench**, a local-first release command center that turns messy release material into structured gates, evidence, validation, risks, actions, notes, and go/no-go records. This is a directly implementable TypeScript/Next.js/Prisma/SQLite application specification for an AI programming agent. The result is a single local workspace for proving whether a release is ready across WeaveMark public README, docs, examples, generated outputs, study results, release notes, package artifacts, extension builds, CLI behavior, installation checks, single-output validation studies, qualitative evidence, score explanations, browser-facing examples, screenshots, traces, console/runtime findings, issues, PR notes, local TODOs, deferred work, waivers, and known limitations.

### [T] WeaveMark treatment source seam

>   @refine programming/foundations/software-spec
>     Mingle refinements into one release workspace; no appendices.

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

## What improved

- [T] WeaveMark treatment wins source-only leverage: 19.2 versus 15.72 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 322 versus 97.75 for [C2] Matched reusable-template control.
- Release gates, evidence quality, validation matrices, risks, waivers, actions, dashboards, and browser validation all shape one workflow.
- The treatment has higher source-only leverage than the matched reusable-template control.
- The final specification adds substantially more actionable release facts than the control.

## What failed or did not improve

- [T] WeaveMark treatment loses information density: 67.6 versus 91.4 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment loses information yield: 1,298.4 versus 1,437.5 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 4,762 words versus 1,069 for [C2] Matched reusable-template control.
- The matched template is already strong and keeps higher information density.
- The treatment loses information yield versus the template because the WeaveMark source is longer while the template shell stays very compact.
- No downstream release-workbench implementation outcome has been measured.

## Interpretation

A strong headline study, with the honest caveat that the template remains denser and more source-efficient on the yield proxy. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
