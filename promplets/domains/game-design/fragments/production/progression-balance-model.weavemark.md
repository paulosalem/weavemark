@promplet version: 0.7

@module weavemark.domains.game_design.production.progression_balance_model

# Game Production: Progression and Balance Model

@note
  Reusable game-production layer for converting mechanics into a balanced first
  build with explicit content, tuning, and playtest evidence.

Use this layer when a game specification needs concrete progression and tuning
instead of only mechanic descriptions.

## Progression obligations

- Define the smallest complete content ladder that teaches mechanics in order.
- Map each level, wave, encounter, or round to the mechanic it introduces,
  combines, stresses, or tests.
- Keep rewards meaningful: every unlock, card, upgrade, or resource should
  change a decision rather than only increase numbers.
- Include catch-up, recovery, or restart behavior so early mistakes do not make
  the rest of the run meaningless unless failure is intentional.
- Identify dominant-strategy risks, runaway feedback loops, dead cards, useless
  upgrades, impossible waves, and uninteresting safe defaults.
- Define tuning knobs, starting values, safe ranges, and signs that each value is
  too low or too high.

## Required output shape

When applicable, include:

1. **Progression ladder** - ordered levels, waves, cards, upgrades, threats, and
   ecosystem states.
2. **Balance table** - parameter, initial value, range, player-facing effect,
   failure symptom, and adjustment rule.
3. **Synergy and counterplay matrix** - what combines, what counters it, and what
   prevents a dominant strategy.
4. **Playtest questions** - what a human or browser-validation pass should
   observe to tune the first build.
5. **Release balance gate** - criteria for calling the vertical slice credible.
