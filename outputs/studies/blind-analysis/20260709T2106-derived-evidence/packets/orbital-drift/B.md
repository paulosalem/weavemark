# Blind derived-evidence packet

Study: Orbital Drift
Variant: B
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 65
- Variable payload words: 0
- Output words: 3205
- Local leverage: 49.31x
- Candidate facts: 223
- Counted facts: 222
- Discounted fact units: 217.25
- Information density per 1k output words: 67.8
- Information yield per 1k source words: 3342.3

## Extracted fact candidates

- Build a playable single-page browser racing game where the player pilots a small spacecraft through a space environment containing planets, asteroid fields, gravity wells, propulsion-based movement, and lap-based racing.
- The first build is a complete vertical slice, not a prototype menu or static mockup.
- A player MUST be able to open one browser page, quickly learn the variants, start racing, complete or fail a round, see feedback about performance, and restart without reloading the page.
- Casual browser players who understand arcade racing and space flight conventions.
- Players should be able to learn the first build in under one minute.
- The game should reward improvement through smoother piloting, better racing lines, and controlled use of thrust around hazards and gravity wells.
- The game should deliver a compact arcade experience: fast restarts, readable hazards, satisfying craft variant, and clear lap-based progression through a space course.
- A single playable browser page.
- A visible space race course with:
- at least one lap requirement,
- planets or large celestial bodies,
- gravity wells that influence craft movement.
- A controllable player craft with propulsion and steering.
- Clear variants taught on first load.
- A HUD showing current lap, checkpoint progress, race timer, and restart guidance.
- Collision or hazard feedback for asteroids, planets, or course boundaries.
- Restart without full page reload.
- Pause or safe suspension behavior when the tab loses focus.
- A browser validation plan using Playwright MCP or equivalent browser automation.
- persistent progression beyond local high score or best time,
- mobile-specific virtual variants unless the implementation can add them cleanly without compromising keyboard play.
- Optional enhancements MAY include sound effects, particle trails, screen shake, mobile touch variants, and local best-time persistence, but the game must remain playable without them.
- The player must pilot the craft through the course gates in order and complete the required number of laps as quickly as possible while avoiding hazards and managing momentum.
- The game loop MUST be immediately understandable:
- Apply thrust and steering to pass through the next gate.
- Receive visual, spatial, and HUD feedback.
- Complete laps and improve time.
- The first build MAY use a pure time-trial model instead of a hard failure state.
- Race timer starts when active play begins.
- Checkpoint progress updates when the craft passes the correct gate.
- Lap count increments after all required checkpoints are passed and the craft crosses the start or finish gate in the correct sequence.
- Completion screen shows final time.
- Recommended failure or penalty model:
- Colliding with an asteroid, planet, or boundary applies a time penalty, velocity penalty, brief stun, or respawn to the last checkpoint.
- The player should understand why the penalty happened through visible feedback.
- If a fail state is implemented, it MUST provide immediate retry without page reload.
- On first load, the page MUST show:
- `Arrow Left` and `Arrow Right` or `A` and `D`: rotate
- `Space`: brake or stabilize, if implemented
- variants may differ, but the on-screen help must match the implementation exactly.
- The first interaction should teach by doing:
- The first gate should be visible and easy to reach.
- The early course should allow the player to feel thrust and inertia before encountering dense asteroid hazards.
- Gravity wells should be introduced with readable visual indicators before they become punishing.
- During play, the HUD MUST show:
- current lap and total laps,
- current checkpoint or next gate indicator,
- The HUD SHOULD avoid clutter and remain readable over the space background.
- The game MUST provide clear feedback for:
- Feedback may use motion, color, particles, brief messages, sounds, or animation.
- Visual feedback is required; audio is optional.
- Pressing the pause variant SHOULD pause the game.
- Losing page visibility or browser focus MUST pause or safely suspend gameplay.
- Returning to the tab MUST not cause a large uncontrolled physics jump.
- The player should be able to resume intentionally.
- The implementation MUST reset game state in memory without reloading the page:
- transient messages and collision state.
- Persistent best time, if implemented, should not be cleared by ordinary restart.
- Implement an explicit state model with at least:
- `menu` or `ready`: instructions visible, race not yet timing.
- ... 163 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/orbital-drift/B.json`
