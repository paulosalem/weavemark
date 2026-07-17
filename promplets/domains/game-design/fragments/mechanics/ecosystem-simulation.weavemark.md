@promplet version: 0.7

@module weavemark.domains.game_design.mechanics.ecosystem_simulation

# Game Mechanic: Ecosystem Simulation

@note
  Reusable game-design layer for games where plants, creatures, resources, or
  habitats interact through simple living-system feedback loops.

Use this layer when a game needs ecological relationships, resource cycles,
population pressure, resilience, invasive threats, pollination, seasons, or
habitat balance.

## Ecosystem obligations

- Define living entities: plants, creatures, pests, pollinators, predators,
  decomposers, habitats, resources, or environmental conditions.
- Define resource flows such as water, nutrients, sunlight, shelter, energy,
  population, waste, growth, decay, or fertility.
- Define interaction rules: growth, consumption, pollination, predation,
  competition, symbiosis, spread, decay, reproduction, and recovery.
- Define positive and negative feedback loops so the ecosystem can improve,
  collapse, stabilize, or shift state.
- Define player-readable indicators for health, stress, abundance, shortage,
  spread, resilience, and looming failure.
- Define time progression through ticks, seasons, days, waves, turns, or
  encounter phases.

## Design discipline

- The first build SHOULD use a small number of entity types and resource flows.
- Simulation rules MUST be understandable enough for the player to reason about.
- Emergence SHOULD come from simple rule interactions, not opaque hidden math.
- Balance success around resilience and recovery, not only maximizing one score.
- Failure SHOULD teach which relationship broke: resource shortage, pest
  pressure, overgrowth, pollution, missing pollination, or poor timing.

## Browser-game implementation guidance

- Prefer visible state overlays and tooltips for living-system feedback.
- Use deterministic or seeded randomness when results affect puzzle fairness.
- Keep entity counts within browser performance limits.
- Acceptance requires a player to change the ecosystem, observe at least one
  feedback loop, understand why it helped or hurt, and recover or restart.
