# Intelligence-to-Execution Kanban Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Manual brief | [00-control-manual-intelligence-execution-kanban.md](../outputs/compiled-prompts/00-control-manual-intelligence-execution-kanban.md) | 10 | 67 |
| [C2] Matched reusable-template control | [01-control-template-intelligence-execution-kanban.md](../outputs/compiled-prompts/01-control-template-intelligence-execution-kanban.md) | 149 | 1,066 |
| [T] WeaveMark treatment | [02-treatment-promplet-intelligence-execution-kanban.md](../outputs/compiled-prompts/02-treatment-promplet-intelligence-execution-kanban.md) | 384 | 4,177 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Manual brief

> Build a local-first Kanban workspace that helps me monitor selected topics,
> capture relevant news and information, turn important inputs into cards, manage
> ideas, decide what to do, delegate work, track status, and produce useful project
> outputs.

### [C2] Matched reusable-template control

>   by topic, and tied to meaningful card conversions or status changes.
> - The system should answer: what came in, why it mattered, what was decided, who
>   is doing what, what is blocked, what changed, and what output was produced.

### [T] WeaveMark treatment

> Build a local-first TypeScript/Next.js Kanban for a single user or local workspace that converts monitored topic signals into reviewed cards, decisions, actions, delegations, typed outputs, alerts, and updated watch rules.

### [T] WeaveMark treatment source seam

> @compress "Produce a dense implementation spec; preserve structure and every hard requirement."
>   @refine programming/foundations/software-spec
>   @refine programming/stacks/stack-typescript-nextjs-prisma-sqlite
>   @refine programming/types/type-local-first-webapp

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

- [T] WeaveMark treatment wins source-only leverage: 19.07 versus 16.4 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 137.75 versus 96.75 for [C2] Matched reusable-template control.
- The treatment propagates the signal-to-card trace through board states, delegation, notifications, APIs, activity history, and acceptance criteria.
- It produces much more total semantic content than the matched template while preserving a single implementation specification.
- The source keeps the domain abstract while reusable work-intelligence refinements define concrete responsibilities.

## What failed or did not improve

- [T] WeaveMark treatment loses information density: 33 versus 90.8 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment loses information yield: 629 versus 1,488.5 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 4,177 words versus 1,066 for [C2] Matched reusable-template control.
- The matched template has higher information density.
- The treatment loses information yield against the template because the reusable-template shell is extremely compact.
- No generated Kanban implementation has been behaviorally compared yet.

## Interpretation

A strong realistic study for semantic propagation, with a measured density/yield loss that should stay visible. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
