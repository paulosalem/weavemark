# Blind evaluation packet

Study: Transit City Swarm
Variant: A
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# Transit City Swarm: Expanded Browser Game Specification

@directive-a programming/foundations/software-spec
@directive-a programming/types/web-based-game
@directive-a programming/validation/playwright-mcp-browser-validation

Design **Transit City Swarm**, an original browser strategy game.

@directive-b mode: intention focus: "one integrated playable loop, concrete rules, first scenario, scoring, and browser validation"
  Reconcile transit-line drawing, city growth, and swarm demand trails into one
  mechanic: player-built routes alter accessibility and building growth; agents
  leave reinforcing/evaporating demand trails; congestion redirects agents and
  suppresses growth; the player reads trails to draw, prune, reroute, and
  upgrade.

Do not copy protected names, maps, art, music, UI, or distinctive rule sets.

Required output: a concise implementation-ready game specification with concrete
entities, formulas/tuning parameters, variants, first-minute onboarding, HUD,
progression, win/loss or score conditions, performance rules, and Playwright
browser smoke acceptance for a complete playable round and restart.


## Compiled output

# Transit City Swarm: Expanded Browser Game Specification

Produce a concise, implementation-ready software specification for **Transit City Swarm**, an original browser strategy game.

The specification is the source of truth for building the software. It MUST be concrete enough that a competent programming agent can implement a complete first build without asking basic product-shape questions. Prefer safe assumptions over open-ended questions; list only genuinely blocking open decisions, if any.

## Product intent

Design **Transit City Swarm** as an original browser-playable strategy game about shaping a growing transit city by reading agent demand trails and drawing adaptive routes. The player’s job is to keep a living city accessible as population and destinations grow. The value delivered is a readable, fast, strategic toy where routes, congestion, growth, and swarm movement form one integrated loop.

Do not copy protected names, maps, art, music, UI, or distinctive rule sets. Use original place names, simple generated geometry, original visual language, and implementation-owned assets only.

## Required core concept

Reconcile all of the following into one playable mechanic:

- The player draws, prunes, reroutes, and upgrades transit routes.
- Player-built routes change accessibility between districts.
- Building growth is encouraged by accessibility and suppressed by congestion.
- Agents travel between homes, jobs, services, and leisure destinations.
- Agents leave reinforcing demand trails on frequently desired paths.
- Trails evaporate over time so old demand fades.
- Congestion redirects agents, slows service, and suppresses nearby growth.
- The player reads visible trails and congestion feedback to decide where to build, modify, or upgrade routes.

The result MUST describe one integrated playable loop, not three disconnected systems.

## Required output shape

Return a concise implementation-ready game specification with these sections:

1. **Product intent and player objective**
2. **Functional scope for the first build**
3. **Core loop**
4. **Domain model and game state**
5. **Entities and data fields**
6. **Concrete rules, formulas, and tuning parameters**
7. **variants and interaction model**
8. **First-minute onboarding**
9. **HUD, feedback, and presentation**
10. **Progression, scenario, scoring, win/loss, and restart**
11. **Architecture and implementation notes**
12. **Performance, browser, accessibility, and persistence requirements**
13. **Acceptance criteria**
14. **Playwright MCP browser validation plan and smoke acceptance**

## Functional scope for the first build

Specify a complete first build that includes at minimum:

- One playable scenario lasting a complete round.
- A generated or hand-authored city grid/map suitable for browser play.
- Homes, jobs, services, and at least one growth-capable building type.
- Agents with origin, destination, route choice, patience, and trail contribution.
- Player-created transit routes with stops and line segments.
- Route editing: draw, confirm, delete/prune, reroute, and upgrade.
- Congestion visualization and demand-trail visualization.
- Score, round timer or turn counter, budget or build capacity, and restart.
- Menu/loading, playing, paused, win/lose or score-summary, and restart states.
- A playable first-minute tutorial/onboarding flow taught through interaction.
- Browser-visible validation criteria for a complete round and restart.

Out of scope for the first build unless explicitly included as optional enhancements: licensed maps, online multiplayer, server persistence, paid assets, complex pathfinding beyond what is needed for a smooth first build, and mobile-only interaction patterns.

## Core game obligations

Define the player’s objective, core action, challenge, and win/loss or scoring condition. Make the core loop immediately understandable:

1. Observe demand trails, congestion, accessibility, budget, and growth pressure.
2. Draw or edit routes to connect high-demand origins and destinations.
3. Run simulation ticks while agents choose paths and leave trails.
4. Receive feedback through movement, congestion, growth, score, warnings, and trail changes.
5. Upgrade, prune, reroute, or restart to improve performance.

Balance the first minute so it is approachable, then make later play deeper through denser demand, limited budget, congestion, competing growth centers, or score pressure.

## Concrete systems to specify

The specification MUST include concrete entities, formulas, and tuning parameters. Include enough exact values that implementation can start immediately. At minimum define:

- Map size, tile size, coordinate system, and viewport behavior.
- District/building fields such as `id`, `type`, `position`, `population`, `jobs`, `serviceCapacity`, `growth`, `accessibility`, and `congestionPenalty`.
- Agent fields such as `id`, `origin`, `destination`, `state`, `patience`, `path`, `waitTime`, and `trailStrength`.
- Route fields such as `id`, `color`, `stops`, `segments`, `level`, `capacity`, `frequency`, `speed`, `operatingCost`, and `ridership`.
- Stop fields such as `position`, `coverageRadius`, `waitingAgents`, and `servedRoutes`.
- Demand-trail rules including reinforcement amount, evaporation rate, visibility threshold, and how trails aggregate.
- Accessibility formula based on reachable destinations, travel time, route level, stop coverage, and congestion.
- Growth formula based on accessibility, demand satisfaction, local congestion, and caps.
- Congestion formula based on waiting agents, route capacity, segment load, and service frequency.
- Agent route-choice logic, including when congestion causes rerouting.
- Scoring formula that rewards delivered trips, accessibility, balanced growth, low congestion, and budget efficiency.
- Win/loss or end-of-round score conditions for the first scenario.
- Restart behavior without full page reload.

## Browser game experience requirements

The game MUST run in a web browser and feel stable and responsive.

Specify:

- Supported variants: mouse first, with keyboard shortcuts where useful; touch MAY be supported if included.
- Drawing behavior: click/drag or click-to-place route stops; preview line; invalid placement feedback; confirm/cancel.
- Editing behavior: select line, move stop, delete segment/line, upgrade line.
- Pause, resume, restart, and focus-loss behavior.
- Clear feedback for actions through visual state, animation, score changes, messages, or simple sound if sound is in scope.
- Readable HUD limited to what the player needs now.
- Stable layout with no avoidable layout shifts during play.
- Responsive behavior across common laptop viewports; mobile support only if explicitly scoped.
- Local persistence only for appropriate state such as settings and high score.

## Presentation requirements

Establish an original coherent visual style that can be implemented with simple browser-native rendering. The spec should define:

- Map appearance.
- Buildings and growth states.
- Agents or flow particles.
- Transit lines, stops, upgrades, and selection states.
- Demand trails using readable color/opacity/width rules.
- Congestion using warnings, heat, pulsing, or slowdown indicators.
- HUD elements, tutorial prompts, score summary, and restart button.

Keep assets original and lightweight. Avoid unlicensed copyrighted art, music, sound, fonts, names, characters, maps, or distinctive rule sets.

## Architecture and implementation notes

Specify a practical browser implementation approach. The first build SHOULD be implementable with HTML/CSS/JavaScript or TypeScript and Canvas/SVG/WebGL as appropriate. Include:

- Major components/modules.
- Game loop timing model.
- Simulation tick rate and render cadence.
- Deterministic random seed option if useful for tests.
- State transitions: loading/menu, tutorial, playing, paused, round-over, restart.
- Data flow between input, simulation, rendering, HUD, and persistence.
- Extension points for more maps, building types, route upgrades, or scenarios.
- Unit/integration/end-to-end/compact or visual checks that indicate completeness.

## Non-functional requirements

Include requirements for:

- Performance: stable interactive frame rate on ordinary laptops; bounded agent count; throttled pathfinding; no runaway memory growth.
- Reliability: no console/runtime errors during normal play; restart resets state cleanly.
- Accessibility: readable contrast, keyboard-accessible core UI where practical, focus management for menus/buttons, pause on visibility changes.
- Portability: modern Chromium/Firefox/WebKit-compatible browser behavior where reasonable.
- Maintainability: clear data structures and named constants for tuning values.
- Privacy/security: no unnecessary network calls or personal data collection for the first build.

## Playwright MCP browser validation

The implementation plan MUST require Playwright MCP or equivalent browser automation for validation.

State that the implementing agent MUST use a repeated build-run-observe-improve loop:

1. Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
2. Implement the smallest coherent visible slice.
3. Start the application with an existing development or preview command; if none exists, add a minimal project-appropriate command and document it.
4. Open the running URL with Playwright MCP and interact as a real user.
5. Observe the rendered page, accessibility tree, console output, network behavior, screenshots or traces, and persisted state that affects the user experience.
6. Compare observed behavior against the specification for clarity, responsiveness, stability, accessibility, visual polish, and absence of console/runtime errors.
7. Inspect source files when browser behavior reveals a defect.
8. Improve the implementation and repeat until the main experience works and no high-value improvement remains obvious.

Before claiming browser validation, the implementing agent MUST check whether Playwright MCP or equivalent tools are available. If unavailable, install or configure the official Playwright MCP server where possible; with Node/npm, the server command is commonly `npx @playwright/mcp@latest`. If the project needs Playwright tests, add Playwright through the project package manager and install required browsers with the ecosystem command. Do not pretend validation happened if setup cannot be completed; state the exact blocker.

## Required Playwright browser smoke acceptance

Define a Playwright MCP smoke test for a complete playable round and restart. It MUST start from first load and verify at least:

- App loads without console errors.
- Main menu or start state is visible.
- Player can start the first scenario.
- Tutorial/first-minute prompts appear and can be completed or dismissed through intended actions.
- Player can draw or place a valid route.
- Agents begin moving or demand changes visibly respond to the route.
- Demand trails reinforce and/or evaporate visibly over time.
- Congestion or capacity feedback can be observed or induced.
- Score/progress/HUD updates during play.
- A complete round can end by timer, objective, loss, or compact accelerated test condition.
- Round summary communicates success/failure or score.
- Restart returns to a fresh playable state without full page reload.
- No high-severity console/runtime errors occur during the tested flow.

Each validation pass SHOULD record:

- command used to run the app;
- URL tested;
- user flows exercised;
- screenshots or trace artifacts for the visual game state;
- console/network/runtime errors found and resolved;
- remaining limitations or follow-up opportunities.

Final reporting MUST distinguish verified behavior from unverified assumptions.

## Acceptance criteria

The specification is complete when it enables a first build where a player can open the browser page, learn the goal, play a complete round, understand why they succeeded or failed, restart without reloading, and experience stable performance without console errors. The acceptance criteria MUST be testable and tied directly to the systems above.
