# Blind evaluation packet

Study: Orbital Drift
Variant: B
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# Orbital Drift: Framework-X variant

@directive-a programming/foundations/software-spec
@directive-a programming/types/web-based-game
@directive-a programming/validation/playwright-mcp-browser-validation

Use this implementation-ready specification to build **Orbital Drift**, a browser
racing game where the player pilots a small craft through planets, asteroid
fields, gravity wells, propulsion challenges, and lap-based racing.

The first build must be playable in one browser page, teach the variants quickly,
support restart without reload, and include a browser validation plan.


## Compiled output

# Orbital Drift: Implementation-Ready Browser Game Specification

## 1. Product Intent

Build a playable single-page browser racing game where the player pilots a small spacecraft through a space environment containing planets, asteroid fields, gravity wells, propulsion-based movement, and lap-based racing.

The first build is a complete vertical slice, not a prototype menu or static mockup. A player MUST be able to open one browser page, quickly learn the variants, start racing, complete or fail a round, see feedback about performance, and restart without reloading the page.

### Target Player

- Casual browser players who understand arcade racing and space flight conventions.
- Players should be able to learn the first build in under one minute.
- The game should reward improvement through smoother piloting, better racing lines, and controlled use of thrust around hazards and gravity wells.

### Value Delivered

The game should deliver a compact arcade experience: fast restarts, readable hazards, satisfying craft variant, and clear lap-based progression through a space course.

## 2. First-Build Scope

### In Scope

The first build MUST include:

1. A single playable browser page.
2. A visible space race course with:
   - a start or finish line,
   - a sequence of checkpoints or gates,
   - at least one lap requirement,
   - planets or large celestial bodies,
   - asteroid fields or asteroid obstacles,
   - gravity wells that influence craft movement.
3. A controllable player craft with propulsion and steering.
4. Clear variants taught on first load.
5. A HUD showing current lap, checkpoint progress, race timer, and restart guidance.
6. Collision or hazard feedback for asteroids, planets, or course boundaries.
7. Restart without full page reload.
8. Pause or safe suspension behavior when the tab loses focus.
9. A browser validation plan using Playwright MCP or equivalent browser automation.

### Out of Scope for First Build

The first build SHOULD NOT require:

- multiplayer,
- online leaderboards,
- account login,
- paid assets,
- complex level editors,
- procedural campaigns,
- advanced ship customization,
- persistent progression beyond local high score or best time,
- mobile-specific virtual variants unless the implementation can add them cleanly without compromising keyboard play.

Optional enhancements MAY include sound effects, particle trails, screen shake, mobile touch variants, and local best-time persistence, but the game must remain playable without them.

## 3. Core Game Design

### Player Objective

The player must pilot the craft through the course gates in order and complete the required number of laps as quickly as possible while avoiding hazards and managing momentum.

### Core Loop

The game loop MUST be immediately understandable:

1. Learn the goal and variants.
2. Start or continue the race.
3. Apply thrust and steering to pass through the next gate.
4. Receive visual, spatial, and HUD feedback.
5. Avoid or recover from hazards.
6. Complete laps and improve time.
7. Restart quickly and try again.

### Win, Loss, and Scoring

The first build MAY use a pure time-trial model instead of a hard failure state.

Minimum required scoring:

- Race timer starts when active play begins.
- Checkpoint progress updates when the craft passes the correct gate.
- Lap count increments after all required checkpoints are passed and the craft crosses the start or finish gate in the correct sequence.
- Completion screen shows final time.
- Restart is available after completion.

Recommended failure or penalty model:

- Colliding with an asteroid, planet, or boundary applies a time penalty, velocity penalty, brief stun, or respawn to the last checkpoint.
- The player should understand why the penalty happened through visible feedback.

If a fail state is implemented, it MUST provide immediate retry without page reload.

## 4. User Experience

### First Load

On first load, the page MUST show:

- game title,
- one-sentence objective,
- concise variants,
- start instruction,
- visible playfield or preview.

Example variant copy:

- `Arrow Left` and `Arrow Right` or `A` and `D`: rotate
- `Arrow Up` or `W`: thrust
- `Space`: brake or stabilize, if implemented
- `P`: pause
- `R`: restart

variants may differ, but the on-screen help must match the implementation exactly.

### Playable Onboarding

The first interaction should teach by doing:

- The first gate should be visible and easy to reach.
- The early course should allow the player to feel thrust and inertia before encountering dense asteroid hazards.
- Gravity wells should be introduced with readable visual indicators before they become punishing.

### HUD Requirements

During play, the HUD MUST show:

- current lap and total laps,
- current checkpoint or next gate indicator,
- elapsed race time,
- restart variant,
- pause status when paused.

The HUD SHOULD avoid clutter and remain readable over the space background.

### Feedback Requirements

The game MUST provide clear feedback for:

- thrusting,
- turning or orientation,
- passing a checkpoint,
- completing a lap,
- collision or hazard contact,
- being affected by a gravity well,
- race completion,
- restart.

Feedback may use motion, color, particles, brief messages, sounds, or animation. Visual feedback is required; audio is optional.

### Pause and Focus Handling

- Pressing the pause variant SHOULD pause the game.
- Losing page visibility or browser focus MUST pause or safely suspend gameplay.
- Returning to the tab MUST not cause a large uncontrolled physics jump.
- The player should be able to resume intentionally.

### Restart Without Reload

The implementation MUST reset game state in memory without reloading the page:

- craft position,
- craft velocity and orientation,
- checkpoint progress,
- lap count,
- race timer,
- transient messages and collision state.

Persistent best time, if implemented, should not be cleared by ordinary restart.

## 5. Domain Model and Game State

### Required Game States

Implement an explicit state model with at least:

- `menu` or `ready`: instructions visible, race not yet timing.
- `playing`: physics, variants, timer, collisions, and progress are active.
- `paused`: simulation suspended.
- `finished`: final time shown, restart available.

Optional states:

- `countdown`
- `crashed`
- `loading`

State transitions MUST be deterministic and easy to test.

### Core Entities

#### PlayerCraft

Required properties:

- position: x, y
- velocity: x, y
- rotation angle
- angular velocity or direct rotation rate
- radius or collision shape
- thrust state
- alive or active state
- last valid checkpoint, if respawn is implemented

Behavior:

- rotates based on player input,
- accelerates forward when thrust is applied,
- preserves momentum,
- is affected by drag or damping sufficient to keep the game controllable,
- is affected by gravity wells,
- collides with hazards or boundaries according to the selected collision model.

#### Course

Required properties:

- list of checkpoints or gates in order,
- start or finish gate,
- required lap count,
- bounds or playfield dimensions,
- obstacle list,
- gravity well list.

Behavior:

- validates checkpoint order,
- increments lap only after required gates are completed,
- provides the next target indicator.

#### Checkpoint or Gate

Required properties:

- position,
- size or line segment,
- order index,
- visual active or inactive state.

Behavior:

- only the next required gate should advance progress,
- passing an inactive or wrong gate should not skip the sequence,
- successful pass should trigger feedback.

#### Planet

Required properties:

- position,
- radius,
- visual style,
- optional gravity contribution,
- collision behavior.

Planets can be decorative, collidable, gravitational, or both. Their behavior must be visually legible.

#### Asteroid

Required properties:

- position,
- radius or polygon shape,
- optional velocity or rotation,
- collision behavior.

Asteroid fields may be static for the first build. Moving asteroids are optional.

#### GravityWell

Required properties:

- position,
- effective radius,
- strength,
- falloff rule,
- visual indicator.

Behavior:

- pulls or influences the craft when within range,
- must be tuned so the player can recover,
- must not create unavoidable traps near the first gate.

#### RaceTimer

Required properties:

- start time,
- elapsed time,
- paused duration or accumulated active time,
- final time.

Behavior:

- runs only during active play,
- pauses during pause or visibility suspension,
- freezes on race completion.

### Persistence

The first build MAY store a best time in `localStorage`.

If used:

- store only non-sensitive local gameplay data,
- handle unavailable or failing storage gracefully,
- provide no account or network dependency.

## 6. variants and Physics

### Input Requirements

Keyboard support is required.

Recommended mapping:

- `W` or `ArrowUp`: thrust
- `A` or `ArrowLeft`: rotate left
- `D` or `ArrowRight`: rotate right
- `Space`: brake, dampen velocity, or stabilize orientation
- `P` or `Escape`: pause
- `R`: restart

The implementation MUST prevent browser scrolling or accidental page interaction for keys used during active play when appropriate.

### Physics Requirements

The physics model should be simple, readable, and arcade-friendly.

Required:

- Use a fixed timestep or delta-time-safe update loop.
- Cap extreme velocities or forces to avoid tunneling and loss of variant.
- Apply mild damping so the craft remains controllable.
- Keep collision behavior consistent across machines with different frame rates.

Recommended rules:

- Thrust adds acceleration along the craft's forward direction.
- Rotation is independent from velocity direction.
- Gravity wells apply acceleration toward their center with a capped force.
- Planets with gravity may use the same gravity function as wells.
- Collisions either:
  - bounce the craft away,
  - respawn it at the last checkpoint,
  - apply a penalty and reduce velocity.

Choose one collision response and document it in program comments or constants.

### Course Legibility

- The next checkpoint MUST be visually distinct.
- Completed checkpoints SHOULD dim or change color.
- Gravity wells MUST be visually marked with rings, glow, arrows, distortion, or other readable indicators.
- Asteroid fields MUST be visually distinct from background stars.

## 7. Screens and Flows

### Ready Flow

1. Player opens page.
2. Game displays title, objective, variants, and start prompt.
3. Player presses a start key or thrust key.
4. Game enters active play and starts timer.

### Racing Flow

1. Player steers and thrusts toward the highlighted next gate.
2. Passing the correct gate advances checkpoint progress.
3. Completing all gates and crossing the finish sequence increments lap.
4. Completing final lap enters finished state.
5. HUD updates throughout.

### Collision or Penalty Flow

1. Craft overlaps a hazard.
2. Game provides immediate visual feedback.
3. Game applies the selected penalty.
4. Player can continue or restart.

### Pause Flow

1. Player presses pause or tab loses visibility.
2. Simulation and timer stop.
3. Pause overlay appears.
4. Player resumes or restarts.

### Finish Flow

1. Final lap completes.
2. Timer stops.
3. Completion message and final time appear.
4. Best time updates if implemented.
5. Restart is clearly available without reload.

## 8. Architecture and Implementation Notes

### Platform

The game should run in a modern browser as a single page.

Acceptable implementation approaches:

- plain HTML, CSS, and JavaScript with `<canvas>`,
- TypeScript if the project already supports it or setup is simple,
- a lightweight framework only if already present or clearly beneficial.

For a first build, prefer a straightforward canvas implementation unless repository conventions indicate otherwise.

### Suggested Component Structure

A clean implementation should separate:

- input handling,
- game state management,
- physics update,
- collision detection,
- course progression,
- rendering,
- HUD and overlays,
- persistence,
- browser lifecycle handling.

Example modules or sections:

- `InputController`
- `Game`
- `Physics`
- `Course`
- `Renderer`
- `HUD`
- `Storage`
- `BrowserLifecycle`

### Rendering

The renderer MUST make the game readable before it is decorative.

Minimum visual elements:

- starfield or dark space background,
- player craft with clear nose direction,
- thrust flame or trail when accelerating,
- planets,
- asteroids,
- gravity well indicators,
- checkpoints or gates,
- HUD text.

Avoid relying on external unlicensed assets. Use generated shapes, gradients, emoji only if legible, or project-owned assets.

### Timing

Use `requestAnimationFrame` for rendering and updates.

The game loop MUST account for variable frame time. If using delta time directly, clamp large deltas after tab resume. If using a fixed timestep, cap accumulated steps to avoid spiral-of-death behavior.

### Collision Detection

Circle-based collision is sufficient for the first build.

Required collision checks:

- craft against asteroids,
- craft against collidable planets or course bounds if implemented,
- craft crossing or entering the active checkpoint gate.

Collision feedback should be obvious but not so disruptive that the first minute becomes frustrating.

### Accessibility and Responsive Behavior

The first build SHOULD:

- keep text readable at common laptop viewport sizes,
- preserve the game area aspect ratio or scale gracefully,
- avoid layout shifts during play,
- provide sufficient contrast for HUD and gates,
- ensure variants can be used from the keyboard,
- avoid flashing effects that could be uncomfortable.

Mobile support is optional, but the page should not break on narrower viewports. If mobile play is not supported, show keyboard-first variants and keep the layout readable.

### Browser Compatibility

Support current versions of Chromium-based browsers. Firefox and Safari support are desirable if no extra complexity is required.

The game MUST not depend on network availability after page load unless the project already requires a dev server for assets.

### Asset and Licensing Boundaries

Do not use unlicensed copyrighted art, music, sounds, fonts, names, ships, planets, characters, or franchise references.

Use original procedural visuals, simple vector shapes, CSS, canvas drawing, or licensed project assets.

## 9. Non-Functional Requirements

### Performance

- The game should feel smooth on ordinary laptops.
- Target 60 FPS where practical.
- Avoid unnecessary allocations inside the hottest update and render loops.
- Keep first load lightweight.
- Defer heavy optional assets if any are added.

### Reliability

- No uncaught runtime errors during normal play.
- Restart must work repeatedly.
- Pausing and resuming must not corrupt physics or timer state.
- The game should recover gracefully if `localStorage` is unavailable.

### Maintainability

- Use named constants for tuning values such as thrust, damping, gravity strength, collision penalty, lap count, and checkpoint positions.
- Keep game state explicit rather than scattered across unrelated DOM fields.
- Prefer simple data structures and readable functions over premature abstraction.
- Include comments where physics, checkpoint sequencing, or collision response may be non-obvious.

### Privacy and Security

- Do not collect personal data.
- Do not send gameplay data to a server.
- If local best time is stored, keep it local and non-sensitive.

## 10. Acceptance Criteria

The first build is complete only when all applicable criteria are met.

### Playability

- A player can open one browser page and understand the objective and variants.
- A player can start the race and actively pilot the craft.
- The craft responds predictably to thrust and steering.
- The course includes visible planets, asteroid fields, gravity wells, and lap-based checkpoint racing.
- The player can complete at least one full race.
- The player receives clear checkpoint, lap, collision, gravity, and finish feedback.
- Restart works without a full page reload.
- Pause or tab visibility suspension prevents uncontrolled simulation jumps.

### Game Feel

- The first minute is approachable.
- The next target is always legible.
- Hazards are visible before they punish the player.
- Gravity wells influence movement in a way the player can see and learn.
- HUD information is readable and limited to useful race information.

### Technical Quality

- The application starts with a documented existing or newly added project command.
- The game runs without console errors during tested flows.
- The implementation avoids unlicensed assets.
- The layout is stable during active play.
- Frame timing remains stable enough for comfortable play on an ordinary laptop.
- Repeated restarts do not leak obvious state or duplicate loops/listeners.

### Specification Compliance

- The implementation distinguishes product behavior from implementation details.
- Any safe assumptions made during implementation are documented.
- Any genuine blockers or open decisions are minimal and explicit.

## 11. Verification Plan

The implementing agent MUST verify the game through both program-level checks and real browser interaction.

### Static and Unit-Level Checks

Run project-appropriate checks where available:

- linting,
- type checking,
- unit tests,
- build command.

If the project has no test setup, do not add heavy unrelated tooling solely for unit tests. Prefer minimal checks appropriate to the existing stack.

Recommended unit or logic tests if a test harness exists:

- checkpoint order advances only for the active checkpoint,
- lap increments only after the full checkpoint sequence,
- timer pauses and resumes correctly,
- restart resets transient game state,
- gravity force is capped,
- collision penalty or respawn behaves deterministically.

### Browser Validation with Playwright MCP

Use Playwright MCP as the preferred browser-observation surface for validating the browser game.

Before claiming browser validation:

1. Check whether Playwright MCP or equivalent browser automation is available.
2. If unavailable, install or configure the official Playwright MCP server using the host environment's standard setup. When Node and npm are available, the server command is commonly `npx @playwright/mcp@latest`.
3. If project-level Playwright tests are needed, add Playwright through the project package manager and install required browsers with the ecosystem-appropriate command.
4. Do not add duplicate or unrelated test tooling.
5. If MCP setup cannot be completed, report the exact blocker and do not claim that browser validation happened.

### Required Browser-Grounded Implementation Loop

The implementing agent MUST use a repeated build-run-observe-improve loop:

1. Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
2. Implement the smallest coherent playable slice.
3. Start the application with an existing development or preview command. If no command exists, add the minimal project-appropriate command and document it.
4. Open the running URL with Playwright MCP.
5. Interact as a real player:
   - start from first load,
   - read variants,
   - start active play,
   - thrust and rotate,
   - pass at least one checkpoint,
   - encounter or approach an asteroid or collision interaction,
   - observe gravity well influence,
   - complete a lap or verify lap progression,
   - pause and resume,
   - restart without reload.
6. Observe rendered page behavior, accessibility tree where useful, screenshots, console output, network behavior, and persisted state if best time is implemented.
7. Compare observed behavior against this specification and professional game quality.
8. Fix defects and repeat until the main experience works and no high-value improvement remains obvious.

### Required Playable Smoke Test

Browser validation MUST include at least one playable smoke test covering:

- first load,
- active play,
- variants,
- core physics,
- checkpoint or lap progress,
- collision or hazard interaction,
- gravity well interaction,
- scoring or timer feedback,
- restart without full page reload,
- absence of console runtime errors.

### Evidence to Report

Each browser validation pass SHOULD leave concrete evidence:

- command used to run the application,
- URL tested,
- user flows exercised,
- screenshots or trace artifacts for the visual interface,
- console, network, or runtime errors found and resolved,
- remaining limitations or follow-up opportunities.

Final reporting MUST distinguish verified behavior from unverified assumptions. Do not stop at "the app builds"; the browser-based game is incomplete until it has been exercised interactively in the browser.
