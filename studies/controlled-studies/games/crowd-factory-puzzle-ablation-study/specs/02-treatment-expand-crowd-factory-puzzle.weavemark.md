# Crowd Factory Puzzle: Expanded Browser Game Specification

@refine programming/foundations/software-spec
@refine programming/types/web-based-game
@refine programming/validation/playwright-mcp-browser-validation

Design a browser-based puzzle game called **Crowd Factory Puzzle**.

The game must use original names, visuals, rules, and assets. Use existing games
only as high-level mechanic references; do not copy protected characters, maps,
art, music, names, levels, UI, or distinctive presentation.

Concepts to expand and reconcile:

@iterate 2
  @expand mode: intention
    Lemmings-style autonomous crowds: many tiny agents, indirect control, assigned
    roles, environmental hazards, rescue pressure, and readable mass behavior.

  @expand mode: intention
    Factory automation belts and converters: conveyor routing, machines, inputs
    and outputs, throughput, bottlenecks, timing, resource transformation, and
    compact production chains.

  @expand mode: intention
    Sokoban-style spatial pushing puzzles: grid constraints, crates, blocking,
    irreversible mistakes, planning ahead, undo/restart, and level readability.

  The final design must not be three modules pasted together. It must explain the
  new integrated mechanic: how the player indirectly routes autonomous workers,
  uses belts and machines to transform resources, and solves spatial pushing
  constraints without losing the browser-game first-build scope.

  This implementation-ready game specification defines objective, core loop,
  player controls, puzzle objects, agent behavior, level progression, browser
  implementation plan, validation strategy, and acceptance criteria.
