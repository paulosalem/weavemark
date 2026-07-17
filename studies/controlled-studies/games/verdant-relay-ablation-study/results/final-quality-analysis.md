# Verdant Relay Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Manual brief | [00-control-compact-manual-verdant-relay.md](../outputs/compiled-prompts/00-control-compact-manual-verdant-relay.md) | 10 | 57 |
| [C2] Matched reusable-template control | [01-control-template-verdant-relay.md](../outputs/compiled-prompts/01-control-template-verdant-relay.md) | 139 | 954 |
| [T] WeaveMark treatment | [02-treatment-promplet-verdant-relay.md](../outputs/compiled-prompts/02-treatment-promplet-verdant-relay.md) | 665 | 5,567 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Manual brief

> Design a browser game called Verdant Relay that combines tower defense,
> deckbuilding, and ecosystem simulation. The player protects a living railway
> garden from spreading blight by placing defenses, playing cards, and maintaining
> ecological balance.

### [C2] Matched reusable-template control

> - This is the coherent implementation-ready specification for Verdant Relay.
> - Treat this specification as the source of truth for a programming agent or human engineer.
> - Include first-build scope, out-of-scope items, architecture, domain model,
>   durable records, workflows, UI surfaces, automation rules, validation plan,

### [T] WeaveMark treatment

> Build **Verdant Relay**, a playable first-build browser game where the player protects a living railway corridor from blight waves by placing and upgrading ecological defenses, playing deckbuilder cards, and maintaining ecosystem health. The specification is the source of truth for implementation, validation, tuning, assets, and acceptance.

### [T] WeaveMark treatment source seam

> @compress "Produce a dense browser-game implementation spec; preserve structure and every hard requirement."
>   @refine programming/foundations/software-spec
>     Mingle mechanics, architecture, assets, validation, tuning, and readability
>     into one browser-game implementation spec; never append generic fragments.

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

- [T] WeaveMark treatment wins source-only leverage: 18.37 versus 11.36 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 289.5 versus 83 for [C2] Matched reusable-template control.
- The treatment integrates tower defense, deckbuilding, ecosystem simulation, assets, state, balance, UI, and validation into one playable trace.
- It wins leverage, information yield, and total fact units against the matched template.
- It is a useful stress test for whether several reusable mechanics can shape one final specification.

## What failed or did not improve

- [T] WeaveMark treatment loses information density: 52 versus 87 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment loses information yield: 955.4 versus 988.1 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 5,567 words versus 954 for [C2] Matched reusable-template control.
- The treatment is much longer and less dense than the matched template.
- It is a synthetic game concept, so it should not carry the main real-work application claim.
- No generated browser game has been implemented and tested yet.

## Interpretation

A strong structural-mingling stress test, with length/density and synthetic-domain caveats. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
