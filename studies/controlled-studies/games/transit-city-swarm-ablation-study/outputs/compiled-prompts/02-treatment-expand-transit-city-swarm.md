# Transit City Swarm: Implementation-Ready Browser Game Specification

This specification is the source of truth for building **Transit City Swarm**, an original browser strategy game. The first build MUST be a complete playable browser game: a player can load the page, learn the goal, play an entire round, see success/failure/score feedback, and restart without reloading. Do not use protected names, maps, art, music, UI, fonts, characters, or distinctive rule sets from existing games.

## 1. Product Intent

**Player job:** draw and continuously adjust a compact public-transit network that channels swarming commuter demand while shaping city growth.

**Core fantasy:** the city is alive. Tiny commuter agents reveal desire paths like evaporating pheromone trails; the player's transit lines redirect those flows; neighborhoods grow around accessible corridors; growth creates new pressure that must be served.

**Target platform:** modern desktop browser first; responsive layout should remain readable on tablets and large mobile screens if viewport space allows.

**First-build scope:**
- Single map, one procedural city seed per round.
- 8-12 minute score-attack round.
- Mouse-first controls with keyboard shortcuts.
- Minimal original geometric art style: circles, lines, blocks, animated dots, heat trails.
- Local high score/settings persistence only.

**Out of scope for first build:**
- Real city maps.
- Multiplayer.
- User-generated maps.
- Licensed assets.
- Complex zoning UI comparable to full city builders.
- Server persistence.

## 2. Game Objective and Core Loop

### Objective

Maximize final **City Harmony Score** before the round timer ends or the city collapses from unmet demand. A strong score comes from moving commuters efficiently, enabling balanced growth, avoiding congestion, and maintaining budget solvency.

### Core loop

1. **Observe:** commuter swarms move between homes, jobs, services, and new growth nodes. Their repeated walking paths leave colored demand trails.
2. **Plan:** draw or reroute transit lines through stops to intercept high-demand trails and underserved districts.
3. **Operate:** vehicles move along routes, board passengers, and reduce walking pressure.
4. **Grow:** accessible areas densify and change land use; new destinations and demand appear.
5. **Adapt:** congestion, crowding, and budget pressure force the player to upgrade, prune, or reroute.
6. **Score/retry:** the round ends with a score breakdown and immediate restart.

## 3. Domain Model

### Map

- Fixed 2D rectangular map in normalized coordinates, rendered to canvas or SVG.
- Suggested playable area: 1200 x 800 world units.
- Map contains:
  - **Road grid/paths:** lightweight visual background and walking graph.
  - **District cells:** 20 x 20 logical grid for land use and growth simulation.
  - **Transit stops:** player-created nodes.
  - **Transit lines:** ordered stop sequences with vehicles.
  - **Agents:** simulated commuters.
  - **Trail field:** evaporating demand intensity over the map.

### Game states

Implement explicit states:
- `loading`
- `menu`
- `onboarding`
- `playing`
- `paused`
- `round_end`
- `restart`

Focus loss, tab hidden, or window blur MUST pause or safely suspend gameplay. Returning to the tab should resume only after player confirmation or clear visual indication.

### Entities

| Entity | Required fields |
|---|---|
| `DistrictCell` | `id`, `x`, `y`, `landUse`, `population`, `jobs`, `services`, `density`, `accessibility`, `satisfaction`, `growthMomentum` |
| `Stop` | `id`, `x`, `y`, `lineIds`, `queueByDestination`, `crowding`, `level`, `buildCost`, `radius` |
| `Line` | `id`, `color`, `stopIds[]`, `vehicles[]`, `capacityLevel`, `speedLevel`, `operatingCostPerMinute`, `isLoop` |
| `Vehicle` | `id`, `lineId`, `segmentIndex`, `t`, `direction`, `capacity`, `passengers[]`, `speed`, `dwellTime` |
| `Agent` | `id`, `homeCell`, `targetCell`, `mode`, `path`, `patience`, `waitTime`, `tripProgress`, `satisfactionImpact` |
| `TrailSample` | `cellX`, `cellY`, `intensity`, `directionVector`, `age`, `dominantPurpose` |
| `Budget` | `cash`, `incomeRate`, `maintenanceRate`, `constructionSpend`, `fareIncome` |
| `RoundStats` | `servedTrips`, `failedTrips`, `averageWait`, `averageTravelTime`, `congestionIndex`, `growthBalance`, `score` |

### Land use

Use four abstract land-use types:
- `residential`: creates home-origin demand.
- `commercial`: creates job/service destinations.
- `civic`: reduces dissatisfaction and stabilizes growth.
- `mixed`: both origin and destination, lower peak demand.

Initial city:
- 35% residential
- 25% commercial
- 10% civic
- 10% mixed
- 20% empty/low-density potential growth

## 4. Mechanics

### 4.1 Transit-line drawing

The player draws lines by placing stops and connecting them in order.

Rules:
- A line requires at least 2 stops.
- Maximum stops per line at level 1: 8.
- Maximum active lines at start: 3.
- Stops snap lightly to nearby roads/intersections but must not require perfect clicking.
- Lines may cross visually; no collision system is needed for rail geometry.
- Vehicles automatically spawn on each active line.

Controls:
- Left click empty map: place stop for selected line.
- Left click existing stop: append it to selected line.
- Drag stop: reposition within valid radius, updating routes.
- Right click or Delete on selected stop: remove stop if line remains valid.
- Click line color tab: select line.
- `Space`: pause/resume.
- `R`: restart from confirmation prompt or round-end screen.
- `Esc`: cancel current drawing/selection.
- `1`-`5`: select line slot.
- Mouse wheel or `+`/`-`: zoom if implemented; otherwise omit zoom entirely.

Transit capacity:
- Base vehicle capacity: 12 agents.
- Base vehicle speed: 80 world units/second.
- Base dwell time at stop: `0.5 + 0.04 * boardingCount` seconds.
- Vehicle count per line: `ceil(lineLength / 450)`, minimum 1, maximum 5.
- Passenger boards if the line moves them closer to their target by at least 15% estimated path cost.

### 4.2 Swarm demand trails

Agents are simple commuters. They do not need individually perfect intelligence; their collective motion must reveal demand.

Agent generation:
- Every 2 seconds, spawn demand batches from residential/mixed cells.
- Spawn count per cell: `floor(population * peakMultiplier * unmetDemandFactor / 25)`, clamped 0-6 per tick.
- Targets are selected among commercial/civic/mixed cells weighted by jobs/services and distance.

Agent modes:
- `walking_to_stop`
- `waiting`
- `riding`
- `walking_to_destination`
- `failed`

Walking and trail behavior:
- Walking speed: 35 world units/second.
- Each walking agent deposits trail intensity along its path:
  - `deposit = 1.0` for normal demand.
  - `deposit = 1.6` if wait/travel frustration is high.
- Trail intensity evaporates each second:
  - `trailIntensity *= 0.985`
  - Intensities below 0.02 are removed.
- Trail color:
  - blue/green: served or improving demand.
  - orange: crowded/waiting demand.
  - red: failed or severe unmet demand.
- Agents should bias walking path selection away from very congested trail cells:
  - `pathCost = distanceCost + 0.8 * crowdingCost - 0.35 * usefulTrailAttraction`
- The player reads strong trails as "build here" signals, not as decorative effects.

Failure/satisfaction:
- Agent patience starts at 100.
- Waiting drains `1.0/sec`.
- Walking in congested cells drains `0.25/sec`.
- Riding restores `0.4/sec`, capped at original patience.
- If patience reaches 0 before destination, the trip fails and adds red trail intensity.

### 4.3 City growth dynamics

Growth reacts to accessibility, satisfaction, and congestion.

Every 10 seconds, update each district cell:
- `accessibility = weightedStopsWithinRadius + servedTripRatioNearby - congestionPenalty`
- `growthMomentum += 0.15 * accessibility + 0.10 * satisfaction - 0.12 * congestionIndex - 0.05 * taxPressure`
- If `growthMomentum > 1.0`, increase density and reset momentum by `-0.6`.
- If `growthMomentum < -1.0`, reduce satisfaction or density and reset momentum by `+0.4`.

Growth effects:
- Residential density increases future origin demand.
- Commercial density increases destination demand and fare income.
- Civic density reduces nearby patience drain by up to 20%.
- Mixed cells smooth peak demand but grow slower.
- Over-serving only one district type creates imbalance:
  - `growthBalance` decreases when residential-to-jobs accessibility ratio is below 0.6 or above 1.8.

Buildings:
- Represent buildings as simple rectangles or icons inside cells.
- More density means taller/brighter blocks.
- No copyrighted city-building visual identity may be copied.

### 4.4 Budget and upgrades

Starting budget: 600 credits.

Costs:
- Build stop: 45 credits.
- Add line: 120 credits.
- Extend line segment: `0.08 * segmentLength` credits.
- Upgrade line capacity: 180 / 320 / 520 credits by level.
- Upgrade stop: 100 / 220 credits by level.
- Maintenance: `4 * activeLines + 0.8 * stops + 1.5 * vehicles` credits/minute.

Income:
- Served trip fare: 2 credits.
- Commercial growth bonus: `0.2 * commercialDensityIncrease`.
- End-of-minute city grant: `max(0, 30 * averageSatisfaction)`.

Solvency:
- Cash may go negative down to -200.
- Below 0, construction is disabled except deleting/pruning.
- At -200 for 20 continuous seconds, trigger collapse loss.

Upgrade actions:
- Capacity upgrade increases vehicle capacity by 50%.
- Speed upgrade increases vehicle speed by 20% but increases maintenance by 15%.
- Stop upgrade increases queue comfort and catchment radius.
- Pruning/removing stops refunds 20% of original stop cost and may anger nearby agents.

## 5. HUD and User Experience

### Layout

- Central map is always dominant.
- Top bar:
  - time remaining
  - score
  - cash
  - satisfaction
  - congestion
- Left or bottom line panel:
  - line color tabs
  - line status: vehicles, capacity, crowding
  - upgrade buttons
- Right compact inspector:
  - selected stop/line/district details
  - contextual actions
- Bottom message strip:
  - onboarding prompts
  - warnings
  - milestone feedback

### Feedback requirements

Player actions MUST produce immediate visible feedback:
- Stop placement pulse.
- Route redraw animation or highlight.
- Vehicle spawn/movement.
- Queue growth at crowded stops.
- Demand trails fading and shifting.
- Floating score/fare feedback for served trips.
- Clear blocked action messages for invalid placement, insufficient funds, or line constraints.

### Accessibility and responsiveness

- Text must remain readable at common laptop sizes.
- Color must not be the only channel: use line thickness, icons, pulsing, or labels for severe states.
- Provide pause and restart controls visible in UI.
- Avoid layout shifts during play.
- Keyboard shortcuts should not trap browser focus unexpectedly.
- If sound is included, provide mute; the first build may be silent.

## 6. First-Minute Onboarding

Use playable onboarding, not a long instruction page.

Timeline:
1. **0-10 seconds:** show title, one-sentence goal, "Draw a transit line through demand trails."
2. **10-20 seconds:** highlight two pulsing districts and suggest placing first two stops.
3. **20-35 seconds:** spawn visible commuter dots and a faint orange trail between underserved areas.
4. **35-45 seconds:** after first line works, show "Passengers served: +score, +cash."
5. **45-60 seconds:** introduce growth: nearby buildings brighten or rise; warn "Growth creates new demand."
6. After 60 seconds, onboarding tips become dismissible contextual hints.

The player must be able to start interacting within 10 seconds of first load.

## 7. Progression, Round End, and Scoring

### Round length

Default round: 10 minutes. For testing, support a debug or query-parameter accelerated round if appropriate, but the normal user flow remains 10 minutes.

### Escalation

Every 90 seconds:
- Increase spawn pressure by 8%.
- Unlock one upgrade or line slot until max.
- Add 1-3 growth sparks in high-accessibility areas.
- Increase random disruption chance slightly.

Optional disruptions:
- station crowding surge
- road blockage increasing walking cost
- festival demand spike to civic/commercial cell

### Loss conditions

A round ends early if any occurs:
- Budget collapse: cash at -200 for 20 seconds.
- City dissatisfaction collapse: satisfaction below 15% for 30 seconds.
- Demand failure spiral: failed trips exceed served trips for 60 seconds after minute 3.

### Win/score condition

If the player survives the full round, show final score. There is no fixed "win" threshold, but use medals:
- Bronze: 2,500
- Silver: 5,000
- Gold: 8,500
- Platinum: 12,000

Score formula:
score =
  servedTrips * 10
  + averageSatisfaction * 40
  + growthBalance * 1500
  + commercialVitality * 500
  - failedTrips * 8
  - congestionIndex * 1200
  - max(0, -cash) * 2
Round-end screen MUST show:
- final score and medal
- served trips
- failed trips
- average wait
- congestion
- growth balance
- high score if local storage is enabled
- Restart button

## 8. Implementation Notes

### Recommended architecture

Use a simple browser app architecture:
- `GameState`: authoritative simulation state.
- `SimulationSystem`: agents, vehicles, city growth, budget.
- `InputSystem`: pointer/keyboard state and commands.
- `RenderSystem`: map, trails, agents, lines, HUD.
- `UISystem`: panels, messages, pause/restart, onboarding.
- `ValidationHooks`: optional deterministic helpers for smoke tests.

Canvas is appropriate for the map and agents; HTML/CSS is appropriate for HUD panels. SVG is acceptable if performance remains stable.

### Timing

- Use `requestAnimationFrame` for rendering.
- Use fixed-step simulation updates, e.g. 20 ticks/second.
- Clamp large frame deltas after tab switching.
- Separate render interpolation from simulation state where practical.

### Randomness

- Use seedable randomness for map generation and test reproducibility.
- Store the active seed in round stats.
- A restart from the round-end screen may use the same seed by default with a "new city" option.

### Persistence

Use local storage only for:
- high score
- last selected settings
- mute preference
- optional last seed

The game must remain playable if local storage is unavailable.

### Asset boundaries

Use original procedural shapes, simple CSS, generated tones, or permissively licensed assets with attribution if any assets are included. Do not include unlicensed copyrighted art, sound, music, fonts, names, maps, or characters.

## 9. Non-Functional Requirements

### Performance

Target ordinary laptops and modern browsers:
- 60 FPS target for rendering.
- Simulation should remain playable above 30 FPS.
- Initial load should avoid heavy assets and unnecessary dependencies.
- Suggested first-build caps:
  - active agents displayed: 900
  - simulated demand batches may aggregate beyond display cap
  - stops: 80
  - lines: 5
  - vehicles: 30
  - trail cells: 80 x 54 or similar grid
- If caps are exceeded, aggregate agents visually rather than freezing.
- No persistent console errors during normal play.

### Browser compatibility

Support current stable Chromium. Avoid APIs that prevent straightforward operation in Firefox/Safari unless documented. The browser area should preserve aspect ratio and readable UI across common viewport sizes.

### Reliability

- Restart must fully reset simulation state without page reload.
- Pause must stop timers, spawning, movement, and budget drain.
- Invalid player actions must fail safely with a visible message.
- The game should not become unwinnable due to one accidental click in the first minute.

### Maintainability

- Keep tuning parameters centralized.
- Use clear entity names and state transitions.
- Separate simulation from rendering enough that acceptance tests can inspect state or use visible UI reliably.

## 10. Acceptance Criteria

The first build is complete only when all conditions are met:

1. Opening the browser page shows the game without console/runtime errors.
2. The player can start within 10 seconds and understand the basic goal.
3. The player can create a valid transit line with at least two stops.
4. Agents spawn, move, create visible demand trails, wait, ride, and complete or fail trips.
5. Transit vehicles move along player-created lines and visibly affect demand/crowding.
6. City cells grow or decline based on accessibility, satisfaction, and congestion.
7. Budget, score, satisfaction, congestion, and time are visible and update during play.
8. Upgrades or pruning/rerouting provide meaningful mid-round decisions.
9. A round can reach a score/loss/end screen with a clear breakdown.
10. Restart begins a fresh playable round without full page reload.
11. Pause/focus-loss behavior safely suspends gameplay.
12. Layout remains stable and readable at common desktop viewport sizes.
13. No unlicensed protected assets, names, maps, music, UI, or distinctive rule sets are used.
14. Browser validation evidence distinguishes verified behavior from assumptions.

## 11. Verification Plan

### Implementation checks

Run project-appropriate checks:
- package install/build command
- lint/type checks if configured
- unit tests for score, growth, budget, route validity, and restart reset where practical
- manual playthrough for at least one full or accelerated round

### Browser-grounded validation

The implementing agent MUST use a repeated build-run-observe-improve loop:

1. Inspect the specification, repository structure, scripts, tests, and framework conventions.
2. Implement the smallest coherent browser-visible slice.
3. Start the app with an existing dev/preview command; if none exists, add the minimal project-appropriate command and document it.
4. Open the running URL with Playwright MCP or equivalent browser automation.
5. Interact as a real user: click, drag, use shortcuts, create lines, upgrade/prune, pause, resume, finish or force a round end, and restart.
6. Observe rendered page, accessibility tree where useful, console output, screenshots, and persisted state.
7. Compare observed behavior against this specification for clarity, responsiveness, stability, accessibility, visual polish, and absence of runtime errors.
8. Fix observed defects and repeat until the main experience works and no high-value improvement remains obvious.

If Playwright MCP is unavailable, install or configure the official Playwright MCP server before claiming browser validation. When Node/npm are available, the common server command is `npx @playwright/mcp@latest`. If setup cannot be completed, state the exact blocker and do not pretend browser validation happened.

### Required Playwright browser smoke acceptance

Provide a browser smoke validation that exercises a complete playable flow:

1. Start the app and open the tested URL.
2. Verify title/menu/onboarding appears.
3. Start a round.
4. Place at least two stops and create one transit line.
5. Observe agents, vehicles, demand trails, HUD updates, and score/cash changes.
6. Exercise at least one control beyond drawing, such as pause/resume, line selection, upgrade, or stop removal.
7. Reach round end through normal, accelerated, or test-hooked completion.
8. Verify score/loss/end screen appears with breakdown.
9. Click Restart.
10. Verify a fresh playable round starts without full page reload.
11. Confirm no uncaught console errors occurred during the flow.

Validation evidence SHOULD include:
- command used to run the application
- URL tested
- flows exercised
- screenshots or trace artifacts
- console/network/runtime errors found and resolved
- remaining limitations or follow-up opportunities