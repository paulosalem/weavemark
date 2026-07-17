# Transit City Swarm: Expanded Browser Game Specification

@refine programming/foundations/software-spec
@refine programming/types/web-based-game
@refine programming/validation/playwright-mcp-browser-validation

Design **Transit City Swarm**, an original browser strategy game where three core concepts—transit-line drawing, swarm demand trails, and city growth dynamics—combine into a single integrated mechanic.

Key source concepts to expand:

@expand mode: intention
  Mini Metro-style transit network drawing: stops, routes, capacity, congestion,
  and minimalist readability.

@expand mode: intention
  SimCity-style city growth: zones, buildings, roads, budgets, land-use effects,
  traffic, and growth feedback.

@expand mode: intention
  Ant-colony pathfinding with pheromone trails: many simple agents, trail
  reinforcement, evaporation, congestion avoidance, and emergent demand paths.

Integration: Use the expanded Mini Metro, SimCity, and ant-colony notions as
reusable building blocks for one loop: routes alter accessibility, agents reveal
demand, growth creates pressure, and the player upgrades, prunes, or reroutes.

Do not copy protected names, maps, art, music, UI, or distinctive rule sets.

Required output: a concise implementation-ready game specification with concrete
entities, formulas/tuning parameters, controls, first-minute onboarding, HUD,
progression, win/loss or score conditions, performance rules, and Playwright
browser smoke acceptance for a complete playable round and restart.
