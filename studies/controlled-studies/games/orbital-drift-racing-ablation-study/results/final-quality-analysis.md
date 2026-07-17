# Orbital Drift Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Manual brief | [00-control-manual-orbital-drift.md](../outputs/compiled-prompts/00-control-manual-orbital-drift.md) | 8 | 52 |
| [C2] Matched reusable-template control | [01-control-template-orbital-drift.md](../outputs/compiled-prompts/01-control-template-orbital-drift.md) | 91 | 672 |
| [T] WeaveMark treatment | [02-treatment-promplet-orbital-drift.md](../outputs/compiled-prompts/02-treatment-promplet-orbital-drift.md) | 507 | 3,467 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Manual brief

> Use this implementation-ready specification to build **Orbital Drift**, a browser
> racing game where the player pilots a small craft through planets, asteroid
> fields, gravity wells, propulsion challenges, and lap-based racing.

### [C2] Matched reusable-template control

> - Design Orbital Drift as a complete single-page browser racing game.
> - Product intent: The player pilots a small craft through a compact asteroid belt with planets, orbital gates, repair beacons, gravity wells, propulsion, and lap-based racing. The first build must be playable in one browser page: start racing, pass checkpoints, experience hazards and gravity, finish or fail a round, see feedback, and restart without reloading.
> - Include one playable course, start/finish line, ordered checkpoints or gates,
>   at least one lap, visible hazards, recovery aids, timer, progress feedback,

### [T] WeaveMark treatment

> # Orbital Drift: Implementation-Ready Software Specification

### [T] WeaveMark treatment source seam

> # Orbital Drift: WeaveMark Treatment

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

- [T] WeaveMark treatment wins source-only leverage: 22.81 versus 11.02 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins discounted fact units: 228.25 versus 55 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment wins information yield: 1,501.6 versus 901.6 for [C2] Matched reusable-template control.
- The treatment has a very large authoring-leverage and information-yield win over the matched template.
- Browser-game architecture, controls, states, hazards, restart, scoring, and validation are integrated rather than appended.
- The cleaned study is now a single named game instead of a broad multi-variant showcase.

## What failed or did not improve

- [T] WeaveMark treatment loses information density: 65.8 versus 81.8 for [C2] Matched reusable-template control.
- [T] WeaveMark treatment is much longer: 3,467 words versus 672 for [C2] Matched reusable-template control.
- The product theme is still synthetic compared with the real workflow/product studies.
- The matched template is shorter and denser.
- No actual browser game implementation has been generated and tested as behavioral proof.

## Interpretation

A strong game-specification result, best used as supporting implementation-spec evidence rather than the main claim. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
