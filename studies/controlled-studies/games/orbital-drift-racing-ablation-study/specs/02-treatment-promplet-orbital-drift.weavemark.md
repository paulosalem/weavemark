# Orbital Drift: WeaveMark Treatment

@refine programming/foundations/software-spec
@refine programming/types/web-based-game
@refine programming/types/type-2d-game
@refine game-design/production/playability-readability
@refine game-design/production/progression-balance-model
@refine programming/assets/generative-2d-sprites
@refine programming/validation/playwright-mcp-browser-validation

Use this implementation-ready specification to build **Orbital Drift**, a browser
racing game where the player pilots a small craft through planets, asteroid
fields, gravity wells, propulsion challenges, and lap-based racing.

The first build must be playable in one browser page, teach the controls quickly,
support restart without reload, and include a browser validation plan.

Key source concepts to expand:

@expand mode: intention
  Racing mechanics and progression: ordered gates, laps, score, restart, and
  escalating courses.

@expand mode: intention
  Drift physics and propulsion constraints: thrust, yaw, inertia, drag, fuel,
  and gravity wells.

@expand mode: intention
  Hazards and environmental obstacles: planets, asteroid fields, gravity
  anomalies, collisions, and readable risk/reward.

Integration: Use the expanded racing, drift-physics, and hazard notions as
reusable building blocks for one loop: gates structure progress, physics creates
skill expression, and hazards test mastery.
