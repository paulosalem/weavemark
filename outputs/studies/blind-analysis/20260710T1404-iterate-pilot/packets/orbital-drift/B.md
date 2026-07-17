# Blind evaluation packet

Study: Orbital Drift
Variant: B
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# Orbital Drift: Framework-X variant

@directive-a programming/foundations/software-spec
@directive-a programming/types/web-based-game
@directive-a programming/types/type-2d-game
@directive-a game-design/production/playability-readability
@directive-a game-design/production/progression-balance-model
@directive-a programming/assets/generative-2d-sprites
@directive-a programming/validation/playwright-mcp-browser-validation

Use this implementation-ready specification to build **Orbital Drift**, a browser
racing game where the player pilots a small craft through planets, asteroid
fields, gravity wells, propulsion challenges, and lap-based racing.

The first build must be playable in one browser page, teach the variants quickly,
support restart without reload, and include a browser validation plan.

@directive-b mode: intention focus: "one playable browser racing loop with course, gates, drift physics, hazards, original assets, progression, and Playwright validation"
  Transform reusable browser-game, racing, asset, progression, and validation
  obligations into the Orbital Drift course rather than appending generic game
  sections.


## Compiled output

# Orbital Drift Implementation Specification

Build **Orbital Drift** as an implementation-ready, browser-playable 2D racing game. This specification is the source of truth for the first build. Prefer concrete, shippable decisions over open-ended questions. If the repository already has a framework, follow its conventions; if this is a greenfield build, use a simple browser stack that can run locally with one development or preview command.

## 1. Product intent

Orbital Drift is a one-page browser racing game where the player pilots a small spacecraft around a compact orbital course. The game teaches the variants quickly, lets the player complete lap-based races through gates, and makes drifting through gravity wells, asteroid fields, and propulsion challenges readable and satisfying.

The first build MUST deliver one complete playable loop:

- load the page;
- understand the objective and variants within the first 30 seconds;
- start a race;
- steer, thrust, brake or drift, and boost around a 2D orbital course;
- pass through gates in order;
- avoid or recover from hazards;
- finish the required laps or fail by running out of time or hull integrity;
- see clear feedback and results;
- restart without reloading the browser page;
- validate the experience in a real browser with Playwright MCP or an equivalent browser automation surface.

## 2. First-build scope

### In scope

- A single browser page containing the game canvas, HUD, start or menu UI, pause overlay, and result screen.
- One complete course with lap-based racing and ordered gates.
- Player spacecraft movement with acceleration-based thrust, inertia, drift, braking, and local gravity influence.
- At least three course ingredients:
  - planets or gravity wells that bend motion;
  - asteroid hazards;
  - propulsion challenges such as boost pads, fuel or boost recharge zones, or tight drift gates.
- Scoring based on time, lap completion, gates hit in order, collisions avoided, and optional drift or boost bonuses.
- Restart and replay without a page reload.
- Local persistence for settings and top 10 high scores using JSON-compatible browser storage.
- Original or generated 2D assets, with placeholder shapes allowed only when the asset contract and replacement path are documented.
- Browser validation evidence covering first load, active play, collisions or hazards, scoring, finish or failure, and restart.

### Out of scope for the first build

- Multiplayer.
- Server persistence.
- Account systems.
- Multiple ships or a large campaign.
- Paid assets, unlicensed copyrighted art, copied logos, copied music, copied characters, or distinctive protected art styles.
- Heavy asset pipelines that prevent quick local running.

## 3. Core game loop

Each frame follows this update order:

1. Process input events and current pressed-state variants.
2. Run gameplay systems:
   - game state transitions;
   - player thrust, rotation, braking, boost, inertia, and gravity;
   - course gate checks;
   - hazard collision;
   - scoring, timers, laps, and progression;
   - audio and feedback triggers.
3. Render the frame:
   - background starfield and orbital field;
   - course boundaries, gates, planets, asteroids, boost zones, and pickups;
   - player ship and effects;
   - HUD, prompts, pause overlay, or results.

All gameplay state SHOULD be represented with an ECS-style model. Entities carry components, and systems operate over matching component sets. Avoid global mutable singletons for gameplay data; keep configuration, entity state, input state, and rendering resources explicit.

## 4. Game states

Implement these states and transitions:

- **Loading**: show a progress indicator while textures, sprite data, sounds, and fonts load. If assets are generated at runtime or represented by placeholders, still expose a stable loading state.
- **MainMenu**: show the title, short variants, Start, Options, and Quit or Back where applicable. Use a subtle animated background.
- **Playing**: run active gameplay. Show only high-value HUD information: lap, next gate, timer, speed or boost, hull, and score.
- **Paused**: freeze gameplay systems, show a semi-transparent overlay with Resume, Restart, and Main Menu.
- **GameOver**: show final time, score, best time or high score, cause of success or failure, Play Again, and Main Menu.

Pause or safely suspend active gameplay when browser focus is lost, the tab is hidden, or the page visibility changes.

## 5. variants and feel

Provide keyboard variants as the required baseline:

- left and right: rotate ship;
- up or W: thrust;
- down or S: brake or reverse-thrust dampening;
- space or shift: boost when available;
- P or Escape: pause;
- R: restart from result screen or active run after confirmation or safe debounce.

Mouse, touch, or gamepad variants MAY be added if they are responsive and documented, but they are not required for the first build.

Movement MUST be acceleration-based, not instant position snapping. The ship should feel like it is drifting in low-friction space while remaining controllable enough for a first-time player. Use tuning knobs for thrust, rotation rate, drag, braking force, boost impulse, gravity strength, collision bounce, and maximum safe speed.

After taking damage, apply 1.5 seconds of invulnerability frames with a visible flash effect. On damage, use screen shake with amplitude 4px and decay over 0.3 seconds. Camera follow SHOULD lerp toward the player at 5.0 speed factor, clamp to course bounds, and never show outside-of-map void unless the visual design intentionally fills that area.

## 6. Entities and components

Use these core components or equivalent names:

- `Transform`: position, rotation, scale, and optional anchor.
- `Velocity`: linear velocity, angular velocity, acceleration, and damping.
- `Sprite`: sprite key, animation key, frame timing, tint or flash state.
- `Health`: hull value, max hull, invulnerability timer, damage events.
- `PlayerInput`: thrust, turn, brake, boost, pause, restart.
- `Collider`: collision shape, radius or polygon, collision category, trigger flag.

Add course-specific components as needed:

- `GravityWell`: radius, strength, falloff, safe inner radius, visual field.
- `Gate`: sequence index, width, direction, passed state, next-gate indicator.
- `Hazard`: damage, bounce, warning radius, movement pattern if any.
- `BoostPad` or `RechargeZone`: impulse, recharge amount, cooldown, visual cue.
- `LapTracker`: current lap, total laps, next gate, split times.
- `Score`: elapsed time, penalties, bonuses, final score, high-score eligibility.

## 7. Course design

The first course MUST be small enough to learn in one run and deep enough to reward improvement. It should contain:

- 3 laps by default;
- 8 to 12 ordered gates;
- 2 to 4 planets or gravity wells;
- 10 to 25 asteroids depending on viewport and readability;
- 1 to 3 boost or recharge features;
- a clear start and finish line;
- a visible next-gate indicator.

Gate rules:

- Gates must be passed in order.
- Passing the correct gate gives a positive cue and advances the next-gate marker.
- Passing the wrong gate gives a readable blocked or wrong-way cue without soft-locking the run.
- Missing a gate should be recoverable by looping back.
- The player should always know which gate is next through color, arrow, pulsing outline, minimap marker, or HUD text.

Gravity rules:

- Gravity wells alter the ship trajectory but must be previewed visually with rings, arrows, distortion, or particle flow.
- Early gravity influence should be forgiving.
- Later course segments can require using gravity to drift efficiently.
- Collision with a planet or inner danger zone damages or bounces the ship unless a safe orbit ring is explicitly shown.

Hazard rules:

- Asteroids must be visually distinct from gates, planets, boost pads, and background decoration.
- First-run hazards should be sparse and avoid unavoidable collisions.
- Dense asteroid fields should appear only after the player has learned steering and braking.
- Damage must state its cause through motion, sound, flash, HUD change, or result text.

## 8. First-run teaching script

Within the first 30 seconds:

1. The menu states the goal: complete 3 laps by flying through gates in order.
2. A compact variant strip shows thrust, turn, brake or drift, boost, pause, and restart.
3. On Start, the first gate pulses and the HUD says Gate 1.
4. The first straight section has no hazard and teaches thrust and turning.
5. The second section introduces a gentle gravity well with a visual ring and a short cue such as drift around gravity.
6. The third section introduces asteroids with enough space to recover.
7. The first successful gate pass gives a clear sound or visual pulse and updates the HUD immediately.
8. The first collision gives a flash, brief invulnerability, hull feedback, and a recoverable bounce.

Within the first minute, the player should have seen thrust, drift, a gate, a gravity well, an asteroid hazard, score or time feedback, and restart or pause access. Within the first complete run, the player should understand why they won, lost, or can improve.

## 9. Feedback vocabulary and readability budget

Use a consistent cue vocabulary:

- Correct gate: green or cyan pulse, soft chime, score or split update.
- Wrong gate or missed order: amber or red outline, muted buzz, next-gate arrow remains unchanged.
- Damage: ship flash, hull decrement, 4px screen shake, short impact sound.
- Invulnerability: blinking ship or shield ring for 1.5 seconds.
- Gravity: visible field rings, particle flow, or arrows showing pull direction.
- Boost ready: bright boost meter and engine glow.
- Boost used: exhaust streak, meter drain, speed-line effect.
- Recharge: meter fill animation and positive tone.
- Finish: result panel, final time, score, best result comparison, restart call to action.
- Failure: result panel that names the cause and teaches recovery.

Readability budget for the first build:

- No more than one tutorial message on screen during active steering.
- No more than 2 simultaneous large particle effects near the ship.
- No more than 25 active asteroid hazards on the first course.
- HUD should fit in one compact band or corner cluster.
- Avoid layout shifts during play.
- Maintain readable UI and course elements at common desktop viewports and reasonable mobile widths if responsive mobile play is attempted.

## 10. Progression and balance model

Use this smallest complete content ladder:

| Step | Segment | Introduces or tests | Expected player lesson |
|---|---|---|---|
| 1 | Start to Gate 1 | thrust and turning | move forward and aim at the highlighted gate |
| 2 | Gate 2 to Gate 3 | inertia and braking | plan turns early instead of snapping |
| 3 | Gate 4 | gentle gravity well | gravity can help bend a line |
| 4 | Gate 5 to Gate 6 | sparse asteroids | hazards punish over-thrusting |
| 5 | Gate 7 | boost or recharge | boost is useful but needs timing |
| 6 | Final gates | combined drift, gravity, hazards | clean racing line beats constant thrust |

Initial tuning table:

| Parameter | Initial value | Safe range | Player-facing effect | Too low symptom | Too high symptom | Adjustment rule |
|---|---:|---:|---|---|---|---|
| total laps | 3 | 1 to 5 | run length | too short to learn | fatigue before mastery | first build targets 2 to 4 minutes |
| gates | 10 | 8 to 12 | course clarity | boring loop | hard to navigate | add only if next-gate cue remains clear |
| thrust | 260 px/s/s | 180 to 380 | acceleration | sluggish | uncontrollable | tune with first straight |
| drag | 0.985 per frame equivalent | 0.96 to 0.995 | drift duration | too sticky | endless sliding | tune so braking matters |
| rotation rate | 3.8 rad/s | 2.5 to 5.5 | steering | cannot line up | twitchy | tune while circling a planet |
| boost impulse | 280 px/s | 120 to 420 | risk-reward speed | not worth using | skips course readability | boost should help one segment, not solve all |
| gravity strength | medium | low to high | orbital drift | invisible effect | pulls into planets | preview field and tune around Gate 4 |
| asteroid damage | 1 hull | 1 to 3 | hazard weight | ignored | run ends abruptly | first collision should teach, not end |
| hull | 3 | 2 to 5 | mistake allowance | frustrating | no tension | first build should allow recovery |
| time limit | 180 s | 90 to 300 | urgency | no pressure | stressful before learning | allow first clean run plus mistakes |

Dominant-strategy risks and counterplay:

- Constant full thrust can dominate if drag and braking are too forgiving; counter with tighter gates, asteroid placement, and boost timing.
- Riding gravity wells can become too strong; counter with inner danger zones and gate direction.
- Ignoring hazards can dominate if hull is too high; counter with time penalties or speed loss on collision.
- Overusing boost can trivialize course lines; counter with limited recharge and poor variant at unsafe speeds.
- Excess visual effects can hide hazards; counter with the readability budget.

Release balance gate: a new player should complete or nearly complete a run after 2 to 4 attempts, understand the cause of failure, and improve a measurable score or time after practice.

## 11. Failure explanation table

| Failure | Likely cause | Player-readable clue | Recovery lesson |
|---|---|---|---|
| Missed gate | entered wrong angle or skipped sequence | next gate stays highlighted, wrong-gate cue | follow the pulsing gate and turn earlier |
| Hit asteroid | over-thrusted through dense field | impact flash, hull loss, bounce | brake before hazards and choose wider line |
| Fell into gravity danger | flew too close to planet | stronger field rings and danger color | use gravity edge, not the core |
| Ran out of time | inefficient route or too many collisions | timer warning and result breakdown | use drift and boost on straights |
| Lost hull | repeated collisions | hull HUD, invulnerability flash | slow down after damage and recover |
| Got disoriented | next objective not visible | arrow, minimap, or HUD must point to next gate | follow the indicator before accelerating |

## 12. Visual style and asset pipeline

Use a coherent original visual style: readable 2D arcade space racing with crisp silhouettes, bright gates, dark space background, clean UI, and strong color separation. Generated assets are allowed, but treat sprite generation as an asset pipeline, not a one-off art request.

Required first-build sprites or visual assets:

- player ship with idle, thrust, turn_left, turn_right, boost, hit, and explode or disabled states;
- gate with inactive, next, passed, and wrong-order feedback;
- asteroid variants;
- planet or gravity well visuals;
- boost pad or recharge zone;
- particles for thrust, boost, gate pass, collision, and finish;
- HUD icons for hull, boost, lap, and timer if icons improve readability.

For every generated sprite, define a structured sprite spec with these fields:

- `name`;
- `description`;
- `style`;
- `frame_width`;
- `frame_height`;
- `background_color`;
- `animations`, each with `name`, `frame_count`, `fps`, `loop`, and `description`;
- `additional_prompt`.

Recommended first-pass values:

- style: `pixel_art` or clean vector-like arcade sprites;
- frame size: 64x64 for ship and asteroids, 128x128 or scalable vector/canvas rendering for gates and planets;
- transparent background for reusable sprites;
- 2 to 4 frames for idle, hit, blink, and simple effects;
- 4 to 8 frames for thrust, boost, turn, spin, or explosion.

Construct one image-generation prompt per frame. Each prompt MUST combine:

1. fixed frame constraints, such as a single 64x64 2D game sprite frame;
2. the full canonical appearance repeated every time;
3. concrete style, palette, outline, lighting, and view angle;
4. animation name and frame index;
5. pose or motion-progress instruction;
6. transparent background requirement;
7. no text, no UI, no extra characters, no scene background, no watermark.

Generate frames individually, then pack them deterministically. Do not rely on an image model to produce a production-ready exact sprite sheet grid. Store prompts, model settings, selected frames, rejected-frame notes, sheets, metadata, and provenance.

Sprite metadata MUST include:

- frame order sorted by animation and frame index;
- packing strategy: horizontal strip, grid, atlas, or individual PNGs;
- padding if texture bleeding is possible;
- sheet dimensions derived from frame size, count, padding, and columns;
- per-frame rectangles with `x`, `y`, `w`, and `h`;
- animation metadata with stable names, frame count, FPS, and loop flag;
- stable asset filenames and paths;
- a JSON manifest or TexturePacker-style JSON usable by the browser game.

Quality checks for assets:

- readable at actual in-game scale;
- style matches the rest of the game;
- proportions, palette, outline, and view angle remain coherent across frames;
- transparent backgrounds have alpha when required;
- anchor points and collision footprint match gameplay;
- frame order animates smoothly and looping animations connect cleanly;
- no text, watermarks, UI fragments, unwanted shadows, stray pixels, cropped parts, or background remnants.

## 13. Sound and settings

Implement lightweight sound if feasible without delaying the playable loop. Use these categories:

- `music` for looping background music;
- `sfx` for thrust, boost, gate, collision, finish, and failure;
- `ui` for menu and button sounds.

Provide independent sliders or toggles for `music`, `sfx`, and `ui`, and persist settings locally. If sound assets are not available in the first build, include silent-safe hooks and visible feedback so the game remains fully playable.

## 14. Architecture and implementation notes

Use a stable canvas or WebGL rendering surface. Preserve aspect ratio and readable UI across common viewport sizes. Avoid layout shifts during play.

Recommended module boundaries:

- boot and asset loading;
- game state machine;
- ECS world, entities, components, and systems;
- input manager;
- physics and gravity systems;
- collision and gate systems;
- scoring and progression;
- rendering;
- UI and HUD;
- audio;
- persistence;
- validation helpers or test hooks.

Persistence:

- Store settings and top 10 scores in JSON-compatible localStorage.
- Include versioned keys so future builds can migrate safely.
- Do not persist unnecessary personal data.

Performance:

- Target smooth play on ordinary laptops and modern browsers.
- Keep asset sizes small and defer heavy work.
- Avoid per-frame allocations that cause jank.
- Cap or pool particles.
- Ensure no console errors during normal play.

Accessibility and usability:

- Provide visible variants and readable text.
- Do not rely on color alone for gate state or danger.
- Make pause and restart keyboard-accessible.
- Keep focus behavior stable.
- Respect reduced-motion preferences where practical by limiting shake and particles.

## 15. Acceptance criteria

The first build is complete only when all of these are true:

- The game opens in one browser page and reaches MainMenu from Loading.
- The player can start a race, fly the ship, pass ordered gates, interact with gravity, encounter hazards, and finish or fail a run.
- variants are responsive and predictable.
- The objective and variants are understandable in the first 30 seconds.
- Correct gate, wrong gate, damage, boost, finish, and failure states have clear feedback.
- Restart works without page reload.
- Pause and focus-loss behavior safely suspend gameplay.
- The HUD remains readable and limited to high-value information.
- Local settings and top 10 high scores persist when implemented.
- Original or placeholder assets load consistently, and the sprite or asset manifest can drive animation playback without compact coordinate guessing.
- The game has no known console errors in the validated browser flow.
- The implementation includes a browser validation plan and evidence from at least one playable smoke test.

## 16. Browser validation plan with Playwright MCP

Before claiming validation, check whether Playwright MCP or equivalent browser automation is available. If it is not available, install or configure the official Playwright MCP server where the host environment permits it. When Node and npm are available, the server command is commonly `npx @playwright/mcp@latest`. If setup cannot be completed, state the exact blocker and do not claim browser validation happened.

Use this repeated build-run-observe-improve loop:

1. Inspect repository structure, package scripts, framework conventions, and this specification.
2. Implement the smallest coherent browser-visible slice.
3. Start the app with the existing development or preview command. If none exists, add the minimal project-appropriate command and document it.
4. Open the running URL with Playwright MCP.
5. Interact like a player:
   - load the page;
   - start the game;
   - use thrust, turn, brake, and boost;
   - pass at least one correct gate;
   - intentionally hit or narrowly avoid a hazard;
   - observe gravity influence;
   - pause and resume;
   - finish, fail, or force a result state;
   - restart without reload.
6. Observe rendered page, accessibility tree where useful, console output, network behavior, screenshots or traces, and persisted state.
7. Compare observations against the acceptance criteria and professional quality: clarity, responsiveness, stability, accessibility, visual polish, and absence of runtime errors.
8. Fix defects or obvious UX weaknesses, then repeat until the main loop works and no high-value improvement remains obvious.

Validation evidence SHOULD include:

- command used to run the app;
- URL tested;
- browser and viewport;
- user flows exercised;
- screenshots or traces for the menu, active play, collision or hazard, finish or failure, and restart;
- console, network, or runtime errors found and resolved;
- remaining limitations and follow-up opportunities.

Final reporting MUST distinguish verified behavior from unverified assumptions. Do not stop at the app builds; the browser game is incomplete until it has been exercised in a real browser.
