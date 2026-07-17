@promplet version: 0.7

@module weavemark.domains.game_design.mechanics.tower_defense

# Game Mechanic: Tower Defense

@note
  Reusable game-design layer for games where threats traverse lanes, paths, or
  regions while the player places, upgrades, or times defenses.

Use this layer for browser games that need readable waves, defensive placement,
targeting, upgrades, pressure pacing, and clear feedback.

## Core tower-defense obligations

- Define the protected objective: base, garden, convoy, portal, colony, city,
  reactor, or another vulnerable target.
- Define threat paths or movement fields. Threat movement MUST be readable before
  and during the wave.
- Define wave cadence, threat types, spawn timing, route choice, health, speed,
  resistance, special behavior, and reward.
- Define defensive units, range, targeting rules, damage or effect type, reload
  cadence, upgrade path, cost, selling or repositioning rules, and placement
  constraints.
- Provide preview information before commitment: attack range, path coverage,
  cost, blocked placement reason, and expected effect where feasible.
- Make success and failure legible: leaks, damage, blocked targets, slowed
  enemies, defeated enemies, earned resources, and wave completion.

## Pressure and pacing

- Early waves SHOULD teach one defensive decision at a time.
- Later waves SHOULD combine threats that require tradeoffs rather than only more
  damage.
- Failure SHOULD be recoverable through restart, replay, or an understandable
  improvement path.
- Difficulty SHOULD be tunable through enemy health, speed, spawn count, path
  layout, resource income, defense cost, upgrade strength, and wave spacing.

## Browser-game implementation guidance

- Prefer deterministic wave definitions for a first build.
- Keep pathfinding simple and inspectable unless path manipulation is the main
  mechanic.
- Keep visual load manageable with aggregation, clear icons, and status overlays.
- Acceptance requires a player to start a wave, place or upgrade a defense, see
  attacks resolve, understand leaks or success, and replay or continue.
