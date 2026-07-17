# Transit City Swarm: Matched-Prose No-Expand Browser Game Specification

@refine programming/foundations/software-spec
@refine programming/types/web-based-game
@refine programming/validation/playwright-mcp-browser-validation

Design a browser-based strategy game called **Transit City Swarm**.

The game must use original names, visuals, rules, and assets. Use existing games
only as high-level mechanic references; do not copy protected characters, maps,
art, music, names, levels, UI, or distinctive presentation.

Concepts to reconcile:

- Mini Metro-style transit network drawing: elegant line creation, stations,
  routes, capacity, congestion, and minimalist readability.
- SimCity-style city growth: top-down city systems, zones, buildings, roads,
  population pressure, budgets, land-use effects, traffic, and growth feedback.
- Ant-colony pathfinding and pheromone trails: many simple agents, emergent
  demand paths, trail reinforcement, evaporation, congestion avoidance, and
  decentralized adaptation.

The final design must not be three modules pasted together. It must explain the
new integrated mechanic: how player-built networks shape city growth, how
citizens or vehicles create demand trails, how congestion changes growth, and
how the player reads and responds to emergent flow.

This implementation-ready game specification defines objective, core loop,
player controls, simulation rules, feedback, progression, browser implementation
plan, validation strategy, and acceptance criteria.
