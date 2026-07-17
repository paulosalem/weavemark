# Orbital Drift: Implementation-Ready Software Specification

Build **Orbital Drift**, a one-page browser racing game where the player pilots a small craft through ordered gates, laps, asteroid fields, planets, gravity wells, propulsion challenges, and readable risk/reward hazards. The first build MUST be playable in a browser without reloads, teach controls quickly, support pause and restart, and include browser-grounded validation.

## 1. Product Intent

**Target player:** casual browser players who can learn a momentum-based racing loop in under one minute and improve through repeated runs.

**Value delivered:** a compact, readable 2D space-racing experience where skill comes from managing thrust, yaw, inertia, fuel, gravity, hazards, and gate order.

**First-build scope:**
- One playable browser page.
- One complete racing course plus a minimal progression ladder of escalating course variants.
- Keyboard controls as the primary input.
- Restart/replay without full page reload.
- Browser validation using Playwright MCP or equivalent.
- Placeholder or generated 2D sprites with a defined asset pipeline.

**Out of scope for the first build:**
- Multiplayer.
- Backend services.
- Account systems.
- Paid content.
- Complex procedural campaign generation.
- Licensed copyrighted art, music, names, logos, sprites, characters, fonts, or distinctive third-party art styles.

## 2. Functional Scope

### Core loop

The player should:
1. Open the page and see a stable game canvas or game area with title, objective, controls, and Start.
2. Start the race.
3. Pilot the craft through numbered gates in order.
4. Complete the required lap count.
5. Avoid or recover from planets, asteroids, gravity wells, and course-boundary mistakes.
6. Manage momentum and fuel while optimizing time and score.
7. Finish, fail, pause, or restart.
8. Immediately replay without reloading the page.

### Required game states

Implement explicit game states:

- **Loading**: preload textures, sprite sheets, fonts, and audio placeholders if present; show progress or a minimal loading message.
- **MainMenu**: show title, Start, controls summary, and best score/time if available.
- **Playing**: run input, physics, hazards, scoring, HUD, camera, and rendering.
- **Paused**: freeze gameplay systems, show a semi-transparent overlay with Resume and Restart.
- **GameOver**: show failure reason, lap/gate reached, score, time, and Play Again / Main Menu.
- **Finished**: show completion time, score, lap count, penalties, best result, and Play Again / Main Menu.

The game MUST handle focus loss, tab switching, and page visibility changes by pausing or safely suspending gameplay.

## 3. Controls and First-Run Teaching

### Keyboard controls

Default controls:
- `W` or `ArrowUp`: thrust forward.
- `S` or `ArrowDown`: brake / reverse micro-thrust if implemented.
- `A` / `D` or `ArrowLeft` / `ArrowRight`: yaw left/right.
- `Space`: boost if fuel is available.
- `P` or `Escape`: pause/resume.
- `R`: restart current run without page reload.

Input MUST be responsive and predictable. Movement MUST be acceleration-based rather than instant position changes.

### First-run teaching script

In the first 30 seconds:
1. Main menu states: “Fly through gates in order. Thrust with W/↑, steer with A/D or ←/→, restart with R.”
2. First gate is near the craft with a visible arrow and number.
3. A safe open area lets the player feel inertia before tight hazards.
4. The HUD shows current gate, lap, time, score, speed, and fuel.
5. Missing a gate or colliding produces a readable clue, not just a penalty.

In the first minute:
- Introduce one asteroid cluster and one mild gravity well after the player has passed at least one simple gate.
- Show danger previews through color, rings, motion, or warning icons.
- Keep simultaneous threats low enough that the player can understand cause and effect.

First complete run:
- Requires a small number of ordered gates and 2 laps.
- Shows finish feedback, best time, score, and replay options.
- Makes success and failure reasons explicit.

## 4. Domain Model and ECS Architecture

All gameplay state SHOULD be represented as ECS-style entities with components. Avoid hidden global mutable singletons for gameplay objects.

### Core entities

**Player craft**
- Components: `Transform`, `Velocity`, `Sprite`, `PlayerInput`, `Collider`, `Fuel`, `RaceProgress`, `Health` or `Integrity`.
- Movement uses yaw, thrust, inertia, drag, collision response, and optional boost.
- Invulnerability frames after damage: 1.5 seconds with a visible flash effect.

**Gate**
- Components: `Transform`, `GateIndex`, `LapRequirement`, `Collider`, `VisualState`.
- Gates must be passed in order.
- The active gate is highlighted; future gates are visible but visually secondary.
- Passing the wrong gate gives a clear “wrong gate” cue and no progress.

**Planet / gravity body**
- Components: `Transform`, `GravitySource`, `Collider`, `Sprite`.
- Exerts readable attraction inside a visible radius.
- Collision damages, bounces, or fails the player according to tuning.

**Asteroid**
- Components: `Transform`, `Velocity` if moving, `Collider`, `Sprite`, `Hazard`.
- Can be static or slowly drifting.
- Must remain readable at the target viewport.

**Gravity well / anomaly**
- Components: `Transform`, `GravityField`, `VisualEffect`, `Hazard`.
- Can pull, slingshot, slow, or distort trajectory.
- Must be visually distinct from solid planets.

**HUD and UI**
- Track score, lap, gate, time, fuel, speed, best time, pause state, and failure/completion messages.

### Game loop

Each frame:
1. Process input events.
2. Update state transitions.
3. Run player control and propulsion systems.
4. Run gravity, drag, collision, hazard, scoring, and race-progress systems.
5. Update camera.
6. Render world, effects, HUD, and overlays.

Use delta-time based updates and clamp extreme frame deltas after tab restore.

## 5. Racing Mechanics and Progression

### Race rules

- The course is defined by ordered gates.
- The player must pass gates in exact order.
- Completing the last gate increments lap count and returns the target to gate 1.
- First build target: 2 laps, 6-10 gates.
- A finish occurs when the required lap count is completed.
- A failure can occur through integrity loss, timeout, leaving bounds too long, or fuel exhaustion if fuel exhaustion is implemented as hard failure.
- Restart MUST reset player position, velocity, fuel, hazards, race progress, time, and score without reloading the page.

### Score model

Score SHOULD reward:
- Gate completion.
- Lap completion.
- Fast completion time.
- Clean sections without collisions.
- Fuel-efficient or boost-skilled play if fuel is implemented.

Score SHOULD penalize:
- Collisions.
- Wrong-gate attempts.
- Leaving course bounds.
- Excessive time.

The game must always make score changes and penalties visible.

### Minimal progression ladder

Include the smallest complete content ladder that teaches mechanics in order:

| Course step | Mechanic introduced | Course content | Success signal |
|---|---|---|---|
| Tutorial loop | Basic thrust, yaw, inertia, ordered gates | 4 wide gates, no hazards | Player completes one short lap |
| Rookie race | Lap structure and timing | 6 gates, 2 laps, gentle curves | Player understands active gate and lap HUD |
| Drift challenge | Momentum control | Narrower gate spacing, mild drag tuning | Player can brake/turn without overshooting every gate |
| Gravity bend | Gravity well use and avoidance | One visible gravity well near an optional faster line | Player sees slingshot risk/reward |
| Asteroid field | Hazard reading | Sparse asteroid cluster on the racing line | Player adapts route and collision timing |
| Combined course | Mastery test | Ordered gates, planets, gravity wells, asteroids, fuel/boost | Player completes a credible vertical slice |

For the first playable build, implement at least Tutorial loop plus one combined race course. Additional ladder steps MAY be selectable variants or tuning presets.

## 6. Drift Physics and Propulsion Constraints

Physics MUST create skill expression without becoming unreadable.

### Required physics concepts

- **Thrust:** forward acceleration along craft heading.
- **Yaw:** rotation changes heading, not velocity instantly.
- **Inertia:** craft keeps moving after thrust stops.
- **Drag:** light damping prevents endless uncontrollable drift.
- **Boost:** optional burst acceleration consuming fuel.
- **Fuel:** finite or regenerating resource that limits boost or thrust depending on design.
- **Gravity wells:** environmental forces that alter trajectory.

### Initial tuning targets

| Parameter | Initial value | Safe range | Player-facing effect | Too low symptom | Too high symptom | Adjustment rule |
|---|---:|---:|---|---|---|---|
| Thrust acceleration | 260 px/s² | 180-420 | Craft reaches useful speed | Feels sluggish | Overshoots every gate | Tune until first gate is reachable in 2-4 seconds |
| Max practical speed | 420 px/s | 300-650 | Caps readability | Race feels slow | Hazards unreadable | Reduce if collisions feel unfair |
| Drag | 0.985 per frame at 60fps | 0.96-0.995 | Controls drift persistence | No drift skill | Unrecoverable sliding | Tune after thrust |
| Yaw speed | 3.2 rad/s | 2.2-4.5 | Turning responsiveness | Cannot align | Twitchy steering | Tune for gate width |
| Boost acceleration | 520 px/s² | 350-800 | Risk/reward speed | Not worth using | Dominates race | Require fuel and recovery timing |
| Fuel capacity | 100 | 60-160 | Resource planning | Boost absent | Always boosting | Add pickups or regen if runs stall |
| Gravity strength | 35,000 field units | 10,000-80,000 | Slingshot/avoidance | Invisible effect | Feels unfair | Increase only with visible radius cues |
| Collision damage | 25 integrity | 10-50 | Consequence | Hazards ignorable | Instant frustration | Ensure recovery before next hazard |

### Gravity rules

- Every gravity source must show its influence radius or visual field.
- Force should be predictable and stable.
- Planets may combine collision with attraction.
- Gravity wells may be non-solid but must clearly communicate pull direction and danger.
- Use gravity to create optional faster lines, not unavoidable punishment.

### Failure and recovery

Early mistakes should not make the rest of the run meaningless unless the game has intentionally entered failure. Provide one or more:
- temporary invulnerability after collision;
- position reset to last passed gate;
- fuel pickup or slow regeneration;
- soft boundary return;
- clear restart shortcut.

## 7. Hazards, Obstacles, and Risk/Reward

### Required hazards

- **Planets:** large readable bodies with collision and gravity.
- **Asteroid fields:** clusters that force route planning and steering control.
- **Gravity anomalies:** visible non-solid fields that alter movement.
- **Course boundaries:** optional soft limits or warning zones.

### Hazard readability

Each hazard must communicate:
- where it is;
- whether it is solid;
- whether it pulls, damages, slows, or redirects;
- when the player is in danger;
- how to recover or avoid it.

Use consistent visual vocabulary:
- Active gate: bright outline, number, arrow indicator.
- Next route: subtle line or arrow.
- Gravity field: transparent rings, swirl particles, or radial distortion.
- Collision danger: red/orange outline or warning pulse.
- Fuel pickup or boost affordance: blue/cyan.
- Damage: flash, screen shake, sound or visual burst, integrity change.
- Failure: pause action, show cause, offer restart.

### Readability budget

At the actual target viewport:
- No more than 1 active gate and 1 highlighted next target.
- No more than 2 simultaneous strong particle systems near the craft.
- HUD must remain minimal: lap, gate, time, score, speed/fuel, integrity.
- Asteroid clusters must leave visible navigable gaps.
- Avoid layout shifts during active play.

## 8. Camera, Rendering, Sound, and Feel

### Camera

- Smooth follow: lerp toward player position at 5.0 speed factor.
- Clamp to level boundaries; never show outside-of-map void unless intentionally styled.
- Screen shake on damage: amplitude 4px, decay over 0.3 seconds.
- Keep active gate and immediate hazards readable; camera should not lag so much that upcoming gates are hidden.

### Rendering

Use Canvas 2D, WebGL, Pixi, Phaser, or another browser-appropriate 2D approach. Preserve aspect ratio and readable UI across common desktop viewport sizes. Mobile MAY be supported, but if not, show a clear keyboard-focused message.

### Sound

Sound is optional for the first build, but if included:
- categories: `music`, `sfx`, `ui`;
- independent volume controls persisted locally;
- one-shot effects for gate pass, collision, boost, finish, and UI clicks;
- spatial panning MAY be based on entity position relative to camera.

## 9. Asset Production and Generative 2D Sprites

The first build may use simple vector placeholders, but the specification must support generated 2D sprite production.

### Required first-build sprites

| Asset | First-build requirement | May be placeholder? |
|---|---|---|
| Player craft | readable small ship with heading direction | yes |
| Active/inactive gate | numbered ring or portal | yes |
| Planet | solid gravity body | yes |
| Asteroid | rock obstacle | yes |
| Gravity well | non-solid anomaly field | yes |
| Boost/fuel effect | thrust flame or particle trail | yes |
| Collision effect | flash/particles | yes |

### Sprite spec contract

For every generated sprite, maintain a structured spec with:
- name;
- description;
- style;
- `frame_width`;
- `frame_height`;
- `background_color`;
- animations with stable names, `frame_count`, `fps`, `loop`, and description;
- `additional_prompt`.

Example shape:

json
{
  "name": "player_craft",
  "description": "Small triangular racing spacecraft with readable nose direction, cyan engine glow, compact silhouette",
  "style": "pixel_art",
  "frame_width": 64,
  "frame_height": 64,
  "background_color": "transparent",
  "animations": [
    {
      "name": "idle",
      "frame_count": 2,
      "fps": 6,
      "loop": true,
      "description": "Subtle engine pulse while centered and facing upward"
    },
    {
      "name": "boost",
      "frame_count": 4,
      "fps": 12,
      "loop": true,
      "description": "Engine flame grows and flickers behind the craft"
    }
  ],
  "additional_prompt": "Centered in frame, no text, no UI, no scene background"
}
### Frame-prompt rules

Generate or request individual frames first, then pack deterministically. Do not rely on an image model to create an exact production-ready sprite sheet grid.

Each frame prompt must include:
1. fixed frame constraints such as “A single 64x64 2D game sprite frame”;
2. canonical appearance repeated every time;
3. visual style;
4. animation name and frame index;
5. pose or motion-progress instruction;
6. transparent background requirement;
7. quality constraints: no text, no UI, no extra characters, no scene background.

For pixel art, require crisp edges, limited palette, readable silhouette, no painterly blur, and small-canvas legibility.

### Packing and metadata

After frames are selected:
- pack frames in deterministic order by animation and frame index;
- use horizontal strip, grid, or atlas;
- define padding;
- export rectangles with `x`, `y`, `w`, `h`;
- export animation metadata with names, frame count, FPS, and loop flag;
- use stable asset filenames and paths;
- preserve prompts, model settings, generated images, selected frames, sheets, metadata, and provenance.

For browser games, a simple native JSON manifest or TexturePacker-style JSON is sufficient.

### Asset quality checks

Check:
- clarity at in-game scale;
- style match;
- consistency of proportions, palette, outline, and view angle;
- transparent alpha when required;
- stable alignment and center point;
- smooth animation at declared FPS;
- collision fit;
- no watermarks, text, UI remnants, unwanted shadows, cropped limbs, merged props, or background artifacts.

## 10. Implementation Notes

### Browser constraints

- Load quickly enough for casual play; defer or compress heavy assets.
- Run smoothly on ordinary laptops and modern browsers.
- Preserve aspect ratio and stable layout.
- Avoid console errors.
- Persist appropriate local state only: settings, best time, high score, unlocked course variants, and volume.

### Persistence

Use local storage or equivalent browser-local persistence for:
- best score/time;
- volume settings;
- selected options;
- unlocked course variants if implemented.

### Architecture

Recommended modules:
- `GameApp` / bootstrap and state machine.
- `InputSystem`.
- `PhysicsSystem`.
- `GravitySystem`.
- `CollisionSystem`.
- `RaceProgressSystem`.
- `ScoringSystem`.
- `RenderSystem`.
- `CameraSystem`.
- `AssetLoader`.
- `AudioSystem` if sound exists.
- `ValidationHooks` or debug overlay for Playwright-observable state.

Expose enough DOM text or debug state for validation to confirm game state, lap, gate, score, and restart behavior.

## 11. Failure Explanation Table

| Failure | Likely cause | Player-readable clue | Recovery lesson |
|---|---|---|---|
| Missed active gate | entered gates out of order or overshot | active gate remains highlighted; wrong-gate pulse | follow numbered route and reduce speed before turns |
| Collision with planet | ignored gravity/collision body | red flash, shake, integrity loss, “Planet impact” | steer wider or use gravity for slingshot at safe distance |
| Hit asteroid | poor line through field | impact burst, damage, asteroid warning color | choose visible gap and avoid boosting into dense clusters |
| Lost to gravity well | entered pull radius too fast or too close | swirl intensifies, trajectory bends | approach at a shallow angle or avoid field edge |
| Fuel exhausted | overused boost/thrust if fuel limits thrust | fuel warning and reduced boost | conserve boost for exits and straights |
| Timeout or poor score | slow route and repeated penalties | timer/score summary | use cleaner gate lines and fewer collisions |

## 12. Balance, Dominant Strategy, and Playtest Questions

### Dominant-strategy risks

- Boost always optimal: reduce fuel, increase cooldown, or add tighter turns.
- Hugging walls safer than racing line: adjust boundaries and gate placement.
- Gravity wells always avoided: add optional faster slingshot path.
- Collisions too forgiving: increase time/score penalty.
- Collisions too punishing: add invulnerability, reset, or damage reduction.

### Playtest questions

Browser or human validation should observe:
- Can a new player start and understand the goal within 30 seconds?
- Does the craft feel responsive while still drifting?
- Can the player identify the active gate at all times?
- Are gravity wells readable before they affect the craft?
- Are collisions attributable to visible hazards?
- Does restart work instantly without reload?
- Is the HUD readable during motion?
- Is the first complete race finishable after a few attempts?
- Are there console errors, layout shifts, jank, or stuck states?

### Release balance gate

The vertical slice is credible when:
- a first-time player can complete the tutorial loop;
- the combined course is challenging but not confusing;
- every failure has a visible cause;
- the player can improve time/score through skill;
- restart/replay is reliable;
- browser validation confirms active play, collisions/core interactions, progress feedback, and restart.

## 13. Browser Validation Plan

Use Playwright MCP as the preferred browser-observation surface whenever available.

### Setup obligations

- Check whether Playwright MCP or equivalent browser automation is available.
- If unavailable, install or configure the official Playwright MCP server when possible; with Node/npm this is commonly `npx @playwright/mcp@latest`.
- If project Playwright tests are needed, add Playwright through the project package manager and install required browsers using the existing ecosystem command.
- If MCP setup cannot be completed, state the exact blocker and do not claim browser validation happened.

### Build-run-observe-improve loop

The implementing agent MUST:
1. Inspect the specification, repository structure, scripts, tests, and framework conventions.
2. Implement the smallest coherent playable browser slice.
3. Start the app with an existing dev or preview command, or add a minimal project-appropriate command.
4. Open the running URL with Playwright MCP.
5. Interact as a real player: start, steer, thrust, pass gates, collide or trigger a core hazard, pause, finish or fail, and restart.
6. Observe rendered page, accessibility tree, console output, network behavior, screenshots, and persisted state.
7. Compare observations against this specification.
8. Fix defects and repeat until the main experience works and no high-value improvement remains obvious.

### Evidence to report

Each validation pass SHOULD record:
- command used;
- URL tested;
- flows exercised;
- screenshots or traces for visual/spatial behavior;
- console/network/runtime errors found and resolved;
- remaining limitations.

For this game, validation MUST include a playable smoke test that starts from first load, reaches active play, exercises controls and collisions or core interactions, observes scoring/progress feedback, and verifies restart without a full page reload.

## 14. Acceptance Criteria

The first build is complete when all of the following are true:

1. The browser page loads into a stable menu or loading state.
2. The player can start a race and understand the objective.
3. Keyboard controls move the craft with thrust, yaw, inertia, and drag.
4. Gates must be passed in order, and active gate/lap progress is visible.
5. At least one complete course can be finished.
6. At least one hazard class affects play, and the combined course includes readable planets, asteroid fields, or gravity wells.
7. Score, time, lap, gate, fuel/speed, and finish/failure feedback are visible as applicable.
8. Pause and restart work without full page reload.
9. The game handles focus loss or tab visibility safely.
10. Placeholder or generated assets are organized with stable names and a path toward sprite metadata.
11. Browser validation has been performed or an exact blocker is reported.
12. A Playwright MCP or equivalent smoke test verifies first load, active play, controls, collision/core interaction, progress feedback, and restart.
13. There are no known blocking console/runtime errors in the verified flow.
14. The final report distinguishes verified behavior from unverified assumptions.