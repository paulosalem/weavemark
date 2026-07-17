# Blind evaluation packet

Study: Crowd Factory Puzzle
Variant: B
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# Crowd Factory Puzzle: Expanded Browser Game Specification

@directive-a programming/foundations/software-spec
@directive-a programming/types/web-based-game
@directive-a programming/validation/playwright-mcp-browser-validation

Design a browser-based puzzle game called **Crowd Factory Puzzle**.

The game must use original names, visuals, rules, and assets. Use existing games
only as high-level mechanic references; do not copy protected characters, maps,
art, music, names, levels, UI, or distinctive presentation.

Concepts to expand and reconcile:

@iterate 2
  @directive-b mode: intention
    Lemmings-style autonomous crowds: many tiny agents, indirect variant, assigned
    roles, environmental hazards, rescue pressure, and readable mass behavior.

  @directive-b mode: intention
    Factory automation belts and converters: conveyor routing, machines, inputs
    and outputs, throughput, bottlenecks, timing, resource transformation, and
    compact production chains.

  @directive-b mode: intention
    Sokoban-style spatial pushing puzzles: grid constraints, crates, blocking,
    irreversible mistakes, planning ahead, undo/restart, and level readability.

  The final design must not be three modules pasted together. It must explain the
  new integrated mechanic: how the player indirectly routes autonomous workers,
  uses belts and machines to transform resources, and solves spatial pushing
  constraints without losing the browser-game first-build scope.

  This implementation-ready game specification defines objective, core loop,
  player variants, puzzle objects, agent behavior, level progression, browser
  implementation plan, validation strategy, and acceptance criteria.


## Compiled output

# Crowd Factory Puzzle: Browser Game Specification

## 1. Product Intent

**Crowd Factory Puzzle** is a browser-based puzzle game where the player indirectly guides a swarm of autonomous factory workers through compact conveyor-and-machine layouts while solving spatial pushing constraints. The game combines three integrated ideas:

- autonomous crowd rescue: many tiny workers keep moving according to local rules and must be saved in sufficient numbers;
- factory automation: belts, splitters, mergers, machines, buffers, and timing create resource-flow puzzles;
- grid-based pushing: movable crates, machine modules, belt segments, and blockers obey Sokoban-style constraints where pushes are legal only from reachable positions and mistakes can create deadlocks.

The target player enjoys compact logic puzzles, readable simulations, and rescue tension. A good first build must let a player open the page, learn the goal, play complete levels, understand success or failure, restart without reloading, and observe stable browser performance without console errors.

The first build MUST use original names, visuals, rules, and assets. Existing games may be used only as high-level mechanic references. Do not copy protected characters, maps, art, music, names, levels, UI, or distinctive presentation.

## 2. First-Build Scope

### In scope

Build a playable browser game with:

1. A title/menu screen.
2. A level-select or sequential level flow for at least 5 handcrafted tutorial/prototype levels.
3. A stable game state model: loading, menu, playing, paused, won, lost, and restart.
4. A grid-based factory floor.
5. Autonomous worker agents that move continuously or step-by-step on the grid.
6. Conveyor belts and routing elements that move workers and resources.
7. Converter machines that transform raw resources into outputs needed to unlock exits or satisfy objectives.
8. Pushable crates or modules that create recoverable and irreversible spatial-planning challenges.
9. Limited player interventions, including assigning worker roles and pushing/repositioning puzzle objects.
10. Win/loss conditions based on rescue thresholds, time, resource delivery, and preventable worker loss.
11. Clear HUD feedback, pause, restart, undo where feasible, and visible failure explanations.
12. Browser validation through Playwright MCP or equivalent browser automation.

### Out of scope for the first build

The first build SHOULD NOT require:

- online multiplayer;
- user-generated level editors;
- licensed art, music, fonts, characters, or names;
- complex physics beyond deterministic grid/timing rules;
- server persistence;
- large campaign progression;
- procedural level generation;
- mobile-perfect touch variants unless explicitly chosen during implementation.

## 3. Core Game Loop

Each level follows this loop:

1. **Read the factory problem.** The player sees worker spawn points, exits, hazards, raw resource inputs, machines, belts, goals, walls, crates, and route constraints.
2. **Plan the flow.** The player predicts how autonomous workers and resources will move, where traffic will jam, where resources will starve, and which pushes or role assignments are required.
3. **Intervene indirectly.** The player assigns limited roles, toggles gates, rotates or places belts where allowed, pushes crates/modules, or triggers timed mechanisms.
4. **Run and observe.** Workers move on their own; belts transport items; machines transform resources; hazards threaten losses; congestion and timing expose bottlenecks.
5. **Recover or restart.** The player uses undo for tactical learning or restart when the state has lost essential reachability, crate mobility, worker survival, or production viability.
6. **Succeed.** The level is won when enough workers are rescued and required factory outputs reach their targets before limits expire.

The first minute must be approachable: Level 1 should teach a single worker stream and one route change. Later levels can combine timing, congestion, pushing, bottlenecks, and hazards.

## 4. Objective and Success/Failure Criteria

Each level defines:

- **Rescue target:** minimum number or percentage of workers that must reach the exit.
- **Production target:** resources or crafted outputs required to unlock the exit or complete the contract.
- **Time or cycle limit:** optional countdown, maximum ticks, or limited spawn window.
- **Role inventory:** limited counts of assignable abilities.
- **Push/undo limits:** optional constraints for advanced levels.
- **Hazard tolerance:** maximum losses, damaged machines, or blocked outputs.

A level is won when all required objectives are met simultaneously, such as:

- at least 18 of 25 workers rescued;
- 6 packed crates delivered to the exit loader;
- no more than 3 workers lost;
- exit powered before the final gate closes.

A level is lost when rescue or production becomes impossible, the time limit expires, all workers are lost, a critical machine is blocked beyond recovery, or the player chooses restart.

## 5. Integrated Mechanics

### 5.1 Autonomous Workers

Workers are small agents called **Motes**. The player does not directly puppet individual Motes. Each Mote follows simple local rules:

1. Continue moving in its current direction when possible.
2. Follow conveyor arrows when on an active belt.
3. Turn according to deterministic priority rules at junctions.
4. Stop or reverse at blockers, walls, closed gates, or unsafe edges depending on role and tile rule.
5. React to hazards with panic, delay, loss, or role-specific mitigation.
6. Queue when the next tile is occupied, creating readable congestion.
7. Enter machines, elevators, gates, shelters, or exits only when their local condition permits it.

The crowd must feel autonomous. Workers keep moving unless redirected by terrain, roles, obstacles, environmental changes, or machines.

### 5.2 Indirect Player variant

The player’s verbs are strategic and limited:

- assign a role to a selected worker or next worker entering a marker zone;
- place or rotate a limited belt segment where the level allows;
- toggle timed gates or switches;
- push crates, machine modules, or belt blocks with the player cursor/tool avatar;
- mark a worker as a temporary blocker;
- deploy a rescue tool such as a bridge, foam pad, or hazard shield;
- pause, step, restart, and undo recent pushes or planning actions where feasible.

variant MUST remain indirect. The player influences routes, timing, roles, and environment rather than manually steering every worker.

### 5.3 Factory Flow

Factory systems are compact timed flow networks:

- **Raw inputs** enter from dispensers.
- **Belts** move resources and sometimes workers at known speeds.
- **Splitters** divide flow by alternating, priority, or filter rules.
- **Mergers** combine flows and can jam if arrival timing exceeds output capacity.
- **Converters** transform inputs into intermediate or final outputs using cycle timing.
- **Buffers** store limited items and expose starvation or overflow.
- **Output loaders** consume final products to unlock exits, open gates, or satisfy level goals.

The player should understand what goes in, what changes at each step, what comes out, how fast it moves, where constraints appear, and how to simplify or optimize the chain.

### 5.4 Spatial Pushing Constraints

Some levels include pushable objects:

- crates that block paths or hold switches;
- belt modules that must be pushed into alignment;
- machine modules with fixed input/output sides;
- hazard shields or bridge blocks;
- goal pads for factory components.

Pushing obeys strict grid rules:

- objects can be pushed but not pulled;
- the player/tool must be able to stand or act from the square opposite the push direction;
- walls, other crates, workers, machines, and hazards block movement;
- pushing into corners, against walls, or into chokepoints can create irreversible deadlocks;
- the player must preserve access to the correct side for future pushes.

Undo and restart are legitimate play tools. Undo supports tactical learning; restart is expected when a state loses essential reachability or crate mobility.

## 6. Domain Model

### 6.1 Entities

- **Level**
  - id, name, dimensions, tile grid, objectives, spawn schedule, role inventory, time/cycle limits.
- **Tile**
  - type: floor, wall, belt, splitter, merger, machine, gate, hazard, water, pit, fire, exit, goal, switch, buffer.
  - direction and configuration where applicable.
- **Mote**
  - id, position, direction, state, role, carried item, alive/rescued/lost status, animation timer.
- **ResourceItem**
  - id, resource type, position, carrier or belt slot, destination state.
- **Machine**
  - id, recipe, input slots, output slots, processing time, progress, blocked/starved/active state.
- **PushableObject**
  - id, type, position, orientation, push rules, goal compatibility.
- **Hazard**
  - type, active window, effect, mitigation rules.
- **PlayerState**
  - selected tool, role inventory, cursor/tool position if applicable, undo stack, pause state.
- **SimulationClock**
  - tick count, elapsed time, speed, paused/running state.

### 6.2 State Transitions

- loading -> menu;
- menu -> playing;
- playing -> paused;
- paused -> playing;
- playing -> won when objectives are met;
- playing -> lost when objectives are impossible or limits expire;
- won/lost -> restart or next level.

## 7. Puzzle Objects and Rules

### 7.1 Terrain

- **Floor:** normal walkable tile.
- **Wall:** blocks workers, resources, and pushable objects.
- **Pit/Water/Fire:** loses or delays workers unless mitigated.
- **Timed Gate:** opens/closes on switch, timer, or production condition.
- **Exit:** rescues workers when unlocked and reachable.
- **Goal Pad:** target for crates, machine modules, or produced goods.

### 7.2 Belts and Routing

- Belts move items and workers in their arrow direction.
- Belt speed must be deterministic and visible.
- Splitters use one clear rule per level: alternating, priority direction, or item filter.
- Mergers accept only if the output lane has capacity.
- Belt crossings SHOULD be avoided in first-build levels unless implemented with clear bridge/underpass visuals.
- If a belt output faces a wall, blocked machine side, full buffer, or occupied tile, items queue or jam visibly.

### 7.3 Machines

Machines have readable inputs and outputs:

- **Input side(s):** where resources enter.
- **Output side:** where transformed goods emerge.
- **Recipe:** required inputs and produced outputs.
- **Cycle time:** number of ticks/seconds required after inputs are available.
- **Buffer limit:** maximum queued input/output items.
- **State feedback:** idle, starved, processing, output blocked, complete.

Example first-build recipes:

- Scrap + Bolt -> Panel
- Panel + Spark Cell -> Gate Battery
- Foam Canister -> Safety Pad
- Raw Package -> Packed Crate

### 7.4 Roles

Roles must be legible, limited, and functionally distinct. Each role creates tradeoffs and must not solve every problem.

Suggested first-build roles:

| Role | Function | Tradeoff |
|---|---|---|
| Builder | Places a short temporary bridge or ramp | Limited charges; slow; can clog traffic |
| Blocker | Stops or turns workers at a tile | Sacrifices one worker’s movement while active |
| Digger | Opens soft terrain or removes debris | Can create unsafe holes or wrong routes |
| Climber | Crosses one-height obstacles or ladders | Does not protect against hazards |
| Floater | Survives one fall or pit crossing | Consumes role; may still block flow |
| Scout | Temporarily previews route or triggers safe path hints | Does not change terrain |
| Rescuer | Pulls nearby stalled worker from hazard edge | Short range and cooldown |
| Mitigator | Neutralizes one hazard tile for a short time | Timing-sensitive and limited |

The first build MAY implement a smaller subset, but it must include enough role variety to demonstrate indirect crowd variant.

### 7.5 Hazards

Hazards drive pressure and decision-making:

- pits that require bridges, floaters, belts, or rerouting;
- water/fire requiring mitigation or alternate paths;
- moving machinery that crushes or blocks on cycles;
- timed gates that split the crowd;
- collapses that alter terrain;
- scarce safe routes that create bottlenecks.

Hazards must show cause and effect clearly. The player should know why a worker was lost.

## 8. Simulation and Timing Requirements

The game SHOULD use deterministic simulation ticks. Rendering may interpolate between ticks for smoothness.

Specify or implement:

- worker movement speed;
- belt item speed;
- machine cycle duration;
- spawn interval;
- gate timing;
- role activation duration;
- collision/queue order;
- tie-breaking at junctions;
- undo snapshot cadence.

Bottlenecks are identified by comparing:

- input supply rate;
- belt capacity;
- splitter/merger capacity;
- machine processing rate;
- buffer size;
- output demand;
- travel time between stages;
- worker congestion and tile occupancy.

The UI should reveal stalls through icons, color, animation, or short messages: “Machine starved,” “Output blocked,” “Belt jammed,” “Exit locked,” or “Deadlock likely.”

## 9. Level Design Principles

Levels MUST be readable compact puzzles, not sprawling simulations.

Good levels should:

- introduce one new rule at a time;
- preserve visible routes from spawn to exit;
- use goals, walls, crates, and belts to make constraints legible;
- make tempting bad pushes understandable;
- include near-misses, chain reactions, and satisfying rescues;
- create survival thresholds so saving enough workers matters more than perfection;
- avoid hidden assumptions and arbitrary trial-and-error;
- provide enough maneuvering space before asking for difficult pushes;
- make irreversible mistakes detectable quickly;
- keep production chains short enough to reason about.

Suggested progression:

1. **First Shift:** workers follow belts to an exit; player rotates one belt.
2. **Bridge Queue:** introduce builder/blocker timing over a pit.
3. **Panel Line:** feed raw inputs through one converter to unlock exit.
4. **Crate Alignment:** push a belt module into place without trapping it.
5. **Rush Hour Foundry:** combine hazards, splitters, machine output blocking, and rescue threshold.

## 10. User Experience

### 10.1 Screens

- **Menu:** title, play, level select if implemented, settings.
- **Level Intro:** objective summary, role inventory, target counts.
- **Playing HUD:** saved/lost/total workers, production target, timer/cycle count, role counts, pause/restart/undo.
- **Pause:** resume, restart, menu.
- **Win:** stars or rating, saved count, production stats, next level.
- **Loss:** reason, restart, undo if possible.

### 10.2 Feedback

Use clear feedback through:

- worker animation and direction;
- belt arrows and motion;
- machine progress bars;
- jam/starve/block icons;
- hazard warning animation;
- role assignment highlights;
- push legality indicators;
- success/failure messages;
- optional sound if original and lightweight.

HUD information must be readable and limited to what the player needs now.

### 10.3 Accessibility and Responsiveness

The game SHOULD:

- maintain readable grid scaling across common viewport sizes;
- avoid layout shifts during play;
- support keyboard and mouse at minimum;
- include pause on focus loss, tab switching, or page visibility changes;
- avoid color-only state communication;
- keep text legible;
- provide reduced-motion-friendly animation where practical.

## 11. variants

Minimum desktop variants:

- mouse click/tap tile: select worker, object, role target, or tool target;
- drag or arrow/WASD: move the push cursor/tool avatar if implemented;
- click role button then worker/tile: assign role;
- R: restart;
- Z: undo;
- Space: pause/resume or single-step when paused;
- Esc: pause/menu.

variants must be responsive and predictable. Illegal actions should fail clearly without corrupting simulation state.

## 12. Architecture and Implementation Notes

The implementation SHOULD separate:

1. **Simulation engine**
   - deterministic tick update;
   - entity state;
   - movement, belts, machines, hazards, collisions, objectives.
2. **Level data**
   - JSON or TypeScript objects defining grid, entities, objectives, recipes, and tutorial text.
3. **Renderer**
   - canvas or DOM/SVG grid rendering;
   - interpolation and animation;
   - HUD.
4. **Input controller**
   - mouse/keyboard events;
   - tool selection;
   - push validation;
   - pause/restart/undo.
5. **Validation/test layer**
   - unit tests for deterministic rules where feasible;
   - Playwright browser smoke tests or compact MCP validation evidence.

A simple first build may use HTML, CSS, and JavaScript/TypeScript without a heavy engine. If using a framework, follow existing project conventions and avoid unnecessary dependencies.

### 12.1 Persistence

Persist only appropriate local state:

- unlocked levels;
- best rescued count or rating;
- settings such as sound or reduced motion.

Do not require server storage for the first build.

### 12.2 Performance

The game must run smoothly on ordinary laptops and modern browsers. Mobile may be supported if scope allows. Keep assets small, original, and quick to load. Avoid heavy layout recalculation during active play.

## 13. Deadlock and Failure Diagnostics

The game should help the player understand failure without solving the puzzle for them.

Detect or communicate:

- crate pushed into a non-goal corner;
- crate pinned along a wall with no goal path;
- blocked goal square;
- mutually blocking crates;
- player/tool cannot reach required push side;
- machine output blocked;
- machine starved;
- merger jammed;
- rescue threshold no longer reachable;
- exit locked due to missing production output.

When producing hints, prefer explaining the constraint: “This module cannot be pulled back; keep access to its left side.”

## 14. Non-Functional Requirements

- No unlicensed copyrighted assets, character designs, music, names, fonts, or copied level layouts.
- No console/runtime errors during normal play.
- Deterministic rules should make bugs reproducible.
- Restart must work without full page reload.
- Pause must safely suspend simulation.
- Code should be maintainable, with clear data structures for levels and rules.
- The first build should prefer clarity and correctness over visual complexity.
- The game area should remain stable with no disruptive layout shifts.

## 15. Acceptance Criteria

The build is complete when all of the following are true:

1. The browser page loads to a coherent menu or first level.
2. The player can start a level and understand the objective.
3. At least 5 levels are playable or, if project constraints require fewer, at least 3 levels demonstrate the integrated autonomous-crowd, factory-flow, and pushing mechanics.
4. Workers move autonomously according to deterministic visible rules.
5. The player can influence worker flow indirectly through roles, route changes, pushes, or environmental interventions.
6. Belts, splitters/mergers or equivalent routing, and at least one converter machine are functional.
7. Pushable objects obey grid constraints and can create meaningful planning problems.
8. Hazards or failure conditions create rescue pressure.
9. Win, loss, restart, pause, and retry paths work without reloading the page.
10. HUD feedback explains saved/lost counts, production progress, role inventory, and major stalls.
11. The game uses original presentation and assets.
12. Browser validation confirms active play, interaction, feedback, restart, and absence of console errors.

## 16. Verification Plan

### 16.1 Implementation checks

The implementing agent MUST inspect the repository structure, package scripts, existing tests, and framework conventions before implementation. Build the smallest coherent visible slice first, then expand through playable levels.

Recommended checks:

- deterministic movement unit tests for worker direction, queueing, belt movement, and role effects;
- machine recipe tests for input consumption, cycle timing, output blocking, and starvation;
- push legality tests for walls, crates, corners, and unreachable push sides;
- objective tests for rescue thresholds and production targets;
- restart/undo state restoration checks.

### 16.2 Browser validation with Playwright MCP

Use Playwright MCP or equivalent browser automation as the preferred browser-observation surface.

Before claiming validation:

1. Check whether Playwright MCP or equivalent browser automation tools are available.
2. If unavailable, install or configure the official Playwright MCP server when possible. A common Node/npm command is `npx @playwright/mcp@latest`.
3. If project-level Playwright tests are needed, add Playwright through the project package manager and install browsers using the project-appropriate command.
4. Do not add duplicate or unrelated test tooling.
5. If MCP setup cannot be completed, state the exact blocker and do not pretend browser validation happened.

Run a repeated build-run-observe-improve loop:

1. Start the application with an existing development or preview command. If none exists, add a minimal project-appropriate command and document it.
2. Open the running URL with Playwright MCP.
3. Interact as a real user: start a level, assign roles, push objects, route belts, trigger machines, encounter hazards, win or lose, pause, restart, and replay without full reload.
4. Observe rendered page, accessibility tree where useful, console output, network behavior, screenshots, and persisted state.
5. Compare observed behavior against this specification for clarity, responsiveness, stability, accessibility, visual polish, and absence of runtime errors.
6. Inspect and improve source files when behavior reveals a defect.
7. Repeat until the main experience works and no high-value improvement remains obvious.

Each validation pass SHOULD record:

- command used to run the app;
- URL tested;
- user flows exercised;
- screenshots or trace artifacts for spatial gameplay;
- console/network/runtime errors found and resolved;
- remaining limitations or follow-up opportunities.

For this game, browser validation MUST include at least one playable smoke test from first load through active play, core interactions, scoring/progress feedback, and restart/replay without full reload. Final reporting MUST distinguish verified behavior from unverified assumptions.
