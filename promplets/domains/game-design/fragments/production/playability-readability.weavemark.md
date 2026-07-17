@promplet version: 0.7

@module weavemark.domains.game_design.production.playability_readability

# Game Production: Playability and Readability

@note
  Reusable game-production layer for turning a mechanically rich game concept
  into a first build that is readable, teachable, and satisfying to play.

Use this layer when a game specification risks becoming a list of systems rather
than a legible player experience.

## Playability obligations

- Define what the player can understand in the first 30 seconds, first minute,
  and first complete run.
- Make every important state visible through spatial layout, icons, motion,
  sound, color, text, or preview affordances.
- Tie feedback to causality: the player should know what they did, what changed,
  why it mattered, and what they can do next.
- Define safe failure: losing should reveal the broken relationship, missed
  timing, bad placement, poor resource choice, or misunderstood rule.
- Keep early choices small and high-signal; introduce compound interactions only
  after the player has seen each ingredient.
- Require readable density at the actual target viewport, not only in abstract
  wireframes.

## Required output shape

When applicable, include:

1. **First-run teaching script** - what appears, what the player does, what the
   game says or shows, and what success looks like.
2. **Feedback vocabulary** - consistent cues for damage, healing, blocked
   actions, synergies, danger, recovery, rewards, and failure.
3. **Readability budget** - limits on simultaneous threats, effects, overlays,
   card text, counters, particles, and HUD elements.
4. **Failure explanation table** - failure, likely cause, player-readable clue,
   and recovery lesson.
5. **Feel checks** - input latency, animation timing, pause/resume behavior,
   hit feedback, and result-state clarity.
