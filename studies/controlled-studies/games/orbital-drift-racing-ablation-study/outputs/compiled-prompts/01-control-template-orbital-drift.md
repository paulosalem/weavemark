# Orbital Drift: Matched Reusable Template Control

## Implementation specification contract

- This is the coherent implementation-ready specification for Orbital Drift.
- Treat this specification as the source of truth for a programming agent or human engineer.
- Include first-build scope, out-of-scope items, architecture, domain model,
  durable records, workflows, UI surfaces, automation rules, validation plan,
  failure handling, privacy/provenance rules, and acceptance criteria.
- Distinguish required first-build behavior from optional later enhancements.
- Avoid separate support prompts, prompt packs, or artifact manifests.
- Every major requirement should have an observable user-facing or validation
  consequence.
- Use concrete field names, states, events, screens, checks, and recovery paths
  instead of generic quality advice.


## Browser racing game template

- Design Orbital Drift as a complete single-page browser racing game.
- Product intent: The player pilots a small craft through a compact asteroid belt with planets, orbital gates, repair beacons, gravity wells, propulsion, and lap-based racing. The first build must be playable in one browser page: start racing, pass checkpoints, experience hazards and gravity, finish or fail a round, see feedback, and restart without reloading.
- Include one playable course, start/finish line, ordered checkpoints or gates,
  at least one lap, visible hazards, recovery aids, timer, progress feedback,
  pause, restart, and completion/failure states.
- Vehicle movement should use deterministic 2D vectors with acceleration,
  velocity, damping, rotation, stable frame-time handling, and clear collision or
  penalty behavior.
- Gates must be passed in order; wrong gates should not advance progress; lap
  count increments only after the full gate sequence and finish crossing.
- Show title, one-sentence objective, concise controls, start instruction, HUD,
  next-gate indicator, timer, checkpoint progress, collision/penalty feedback,
  and restart guidance.
- Validation should exercise first load, start, movement, checkpoint progress,
  hazard interaction, scoring/timer feedback, pause/resume, restart without page
  reload, and console-error inspection.


## Browser game implementation foundation

- Build a first playable browser version with deterministic game state,
  explicit update/render/input boundaries, and no external server dependency.
- Use Canvas, SVG, or DOM rendering according to the simplest project fit.
- Define states for loading, menu, setup, active play, paused, victory, defeat,
  restart, and error/recovery.
- Use requestAnimationFrame with delta-time clamping so tab stalls do not break
  simulation.
- Persist only non-sensitive local settings or progress in browser storage when
  needed.
- Keep performance stable on ordinary laptops by avoiding unbounded particles,
  unbounded entity arrays, duplicate loops, and expensive per-frame DOM work.
- Include keyboard-first controls, visible focus, clear control help, pause,
  restart, resize handling, and tab visibility handling.


## Original asset and sprite pipeline

- Use only original, non-infringing assets. Do not request, imitate, or include
  copyrighted characters, logos, sprites, or distinctive owned styles.
- First builds may use placeholder shapes, but the specification should define
  sprite roles, sizes, collision footprints, state names, animation metadata,
  palette, frame count, FPS, loop flag, transparent background, sheet packing,
  filenames, and loading rules.
- Store asset provenance, generation prompt if used, source file, derived file,
  metadata, and quality checks.
- Validate readability at game scale, consistent palette, transparent
  backgrounds, hitbox fit, no unwanted text, no artifacts, and no infringement.


## Browser validation and evidence

- Validate the actual browser experience, not only static source inspection.
- Record command used to run the app, URL tested, browser flows exercised,
  screenshots or traces when available, console errors found and resolved, and
  remaining limitations.
- Browser validation should cover first load, primary user flow, invalid inputs,
  persistence across restart or reload, responsive layout, keyboard/focus
  behavior, recovery states, and absence of runtime console errors.
- Prefer Playwright MCP or an equivalent real-browser tool when available. If the
  browser tool cannot run, report the exact blocker and do not claim browser
  validation happened.
- Acceptance requires a first-session path that proves the product is usable,
  understandable, recoverable, and backed by saved evidence.


## Required output

This complete implementation specification includes product intent, first-build
scope, out-of-scope items, player objective, game loop, controls, physics,
hazards, scoring, visual style, browser architecture, state model, data and
local-storage choices, validation plan, browser smoke test, evidence to report,
risks, and acceptance criteria.
