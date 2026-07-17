# Transit City Swarm Final Quality Analysis

[View as HTML](final-quality-analysis.html)


## Outputs inspected

| Variant | Output | Lines | Words |
|---|---|---:|---:|
| [C1] Compact no-expand control | [00-control-compact-no-expand-transit-city-swarm.md](../outputs/compiled-prompts/00-control-compact-no-expand-transit-city-swarm.md) | 108 | 1,024 |
| [C2] Matched-prose no-expand control | [01-control-matched-prose-no-expand-transit-city-swarm.md](../outputs/compiled-prompts/01-control-matched-prose-no-expand-transit-city-swarm.md) | 147 | 1,410 |
| [T] Expanded WeaveMark treatment | [02-treatment-expand-transit-city-swarm.md](../outputs/compiled-prompts/02-treatment-expand-transit-city-swarm.md) | 473 | 2,895 |

## Metric definitions

- **Lines:** Saved output line count.
- **Words:** Saved compiled output word count.

## Verbatim snippets

### [C1] Compact no-expand control

> - transit-network drawing inspired by high-level Mini Metro-like mechanics;
> - city growth inspired by high-level SimCity-like systemic expansion;
> - ant-colony pathfinding concepts using pheromone-style trails and emergent route pressure.

### [C2] Matched-prose no-expand control

> The specification MUST explain the integrated mechanic: how player-built networks shape city growth, how citizens or vehicles create and reinforce demand trails, how congestion changes growth, and how the player reads and responds to emergent flow.

### [T] Expanded WeaveMark treatment

> This specification is the source of truth for building **Transit City Swarm**, an original browser strategy game. The first build MUST be a complete playable browser game: a player can load the page, learn the goal, play an entire round, see success/failure/score feedback, and restart without reloading. Do not use protected names, maps, art, music, UI, fonts, characters, or distinctive rule sets from existing games.

### [T] Expanded WeaveMark treatment source seam

> @expand mode: intention
>   Mini Metro-style transit network drawing: stops, routes, capacity, congestion,
>   and minimalist readability.

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

## What improved

- [T] Expanded WeaveMark treatment wins source-only leverage: 16.36 versus 7.83 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins discounted fact units: 213.5 versus 95 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information density: 73.7 versus 67.4 for [C2] Matched-prose no-expand control.
- [T] Expanded WeaveMark treatment wins information yield: 1,206.2 versus 527.8 for [C2] Matched-prose no-expand control.
- `@expand` makes compact concept labels readable and operational against the compact control.
- The treatment clearly states the integrated mechanic that connects network drawing, city growth, and demand trails.
- It now wins the matched-prose control on the deterministic leverage, fact-unit, density, and yield proxies.

## What failed or did not improve

- The matched-prose control remains the fairness baseline because it spells out the same inspiration set without `@expand`.
- The treatment is a longer generated artifact, so this is not an output-brevity claim.
- This is saved-output semantic evidence; behavioral proof still requires downstream implementation/use.

## Interpretation

A useful `@expand` study where compact named inspirations now produce stronger deterministic proxy metrics than matched prose, while still needing behavioral proof. The qualitative claim should therefore include both sides: WeaveMark improves semantic integration where listed above, but the measured failures and caveats are part of the result, not footnotes.
