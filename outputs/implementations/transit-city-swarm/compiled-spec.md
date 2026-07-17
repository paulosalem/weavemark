# Transit City Swarm: Browser Game Software Specification

Use this implementation-ready software specification to build a browser-based strategy game called **Transit City Swarm**. The specification is the source of truth for a programming agent or developer who will build the game; it must be concrete, testable, and directly actionable rather than a brainstorm, interview script, or list of open-ended questions.

## Product intent

Specify a playable web game in which the player plans and adapts a growing urban transit organism. The game combines:

- Elegant transit-network drawing: the player creates readable lines, routes, stops, transfers, and capacity upgrades on a minimalist top-down city map.
- City-growth simulation: zones, buildings, roads, population pressure, budgets, land-use effects, traffic, and growth feedback respond to player choices.
- Swarm-style demand adaptation: many simple citizens or vehicles move through the city, leave demand trails, reinforce successful corridors, evaporate unused paths, avoid congestion, and expose emergent transport needs.

The final design must not feel like three separate modules pasted together. Define the integrated mechanic: player-built networks shape city growth; citizens and vehicles create visible demand trails; congestion changes both flow and development pressure; and the player reads emergent flow patterns to decide where to draw, extend, reroute, upgrade, or prune the network.

## Originality and asset boundaries

The game must use original names, visuals, rules, systems, UI, maps, audio, fonts, and assets. Existing games may be used only as high-level mechanic references. Do not copy protected characters, maps, art, music, names, levels, interface layouts, distinctive presentation, or proprietary rule sets. State this requirement in the specification and define safe placeholder asset guidance for a first build.

## Required specification shape

This coherent implementation-ready game specification uses these sections:

1. **Product intent**
   - Target player and user job.
   - What value the game delivers in a short browser session.
   - First-build scope and explicit out-of-scope items.

2. **Objective and win/loss or scoring**
   - Player objective.
   - Scoring, success, failure, or endurance conditions.
   - How a complete round begins, escalates, ends, and restarts.

3. **Core loop**
   - The repeatable loop of observing demand, drawing or modifying network elements, watching swarm movement, receiving feedback, earning or losing resources, and improving the city.
   - The first-minute experience and how the player learns through interaction.
   - How later play becomes deeper, faster, or more strategic.

4. **Integrated simulation design**
   - City map representation: zones, buildings, roads, stations, stops, line segments, districts, terrain or blockers if applicable.
   - Transit-network rules: creating lines, connecting stops, capacity, route length, transfer behavior, upgrade costs, deletion/rerouting, and readability constraints.
   - Swarm demand rules: citizen or vehicle agents, origin/destination selection, route choice, demand trails, reinforcement, evaporation, congestion avoidance, and decentralized adaptation.
   - City-growth rules: how accessibility, congestion, land use, services, budget, population pressure, and travel reliability change building growth and demand.
   - Feedback loops: how player networks influence city growth, how growth changes demand, and how demand trails reveal the next strategic decision.
   - Timing, randomness, tick/update rules, and deterministic seeds where useful for testing.

5. **Player controls and user experience**
   - Supported controls for mouse and keyboard; include touch support only if in scope.
   - Network drawing, selecting, inspecting, upgrading, pausing, restarting, and speed controls.
   - HUD information that must remain readable and limited to what the player needs now.
   - Empty states, onboarding, tooltips, error states, invalid placement feedback, and clear retry paths.
   - Game states: loading, menu, playing, paused, win/lose or results, and restart.
   - Accessibility and responsive behavior across common browser viewport sizes.

6. **Game feel and presentation**
   - Original visual style suitable for minimalist but legible city simulation.
   - Color, motion, animation, sound, and feedback guidelines.
   - How demand trails, congestion, capacity, station load, city growth, and budget pressure are visualized without clutter.
   - Rules for avoiding layout shifts and preserving aspect ratio during play.

7. **Domain model and state**
   - Key entities such as City, District, Zone, Building, Road, Station, Line, Segment, Agent, DemandTrail, CongestionCell, Budget, Upgrade, GameClock, and GameSession.
   - Important fields, identifiers, relationships, and state transitions.
   - Persistence needs such as settings, high scores, unlocked scenarios, or local saved sessions.

8. **Architecture and implementation plan**
   - Browser implementation approach using standard web technologies or an appropriate lightweight game stack.
   - Major components, data flow, render loop, simulation loop, input handling, and UI layer.
   - Performance strategy for many agents and trail fields.
   - Asset loading, deferred or compressed assets, and local-state persistence.
   - Maintainable extension points for new map seeds, scenarios, upgrades, building types, or agent behaviors.

9. **Non-functional requirements**
   - Responsive input and stable performance on ordinary laptops and modern mobile browsers if mobile is included.
   - Quick load for casual play; defer heavy assets.
   - Page visibility and focus-loss handling: pause or safely suspend gameplay on tab switching or focus loss.
   - No console/runtime errors in normal play.
   - Security and privacy constraints for a local browser game.
   - Portability and maintainability expectations.

10. **Progression and balance**
    - Early, mid, and late-game progression.
    - Resource economy, budget pressure, unlocks, milestones, difficulty growth, and failure pressure.
    - Balancing principles that make the first minute approachable while allowing strategic depth.

11. **Acceptance criteria**
    - Testable conditions showing that a first build is complete.
    - Include at minimum: a player can open the page, understand the goal, start a round, draw or modify a network, observe agents and demand trails, see city growth or congestion feedback, receive score/resource feedback, pause, lose/win or finish a run, and restart without a full page reload.
    - Include performance, browser stability, originality, and no-console-error criteria.

12. **Verification and browser validation strategy**
    - Include unit, integration, simulation, visual, manual, and end-to-end checks where appropriate.
    - Require a browser-grounded build-run-observe-improve loop.
    - Use Playwright MCP or equivalent browser automation as the preferred browser-observation surface.
    - Before claiming browser validation, check whether Playwright MCP or equivalent browser automation tools are available.
    - If Playwright MCP is unavailable, install or configure the official Playwright MCP server before browser validation when possible. When Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`.
    - If the project itself needs Playwright tests, add Playwright through the project package manager and install required browsers using the existing ecosystem command. Do not add duplicate or unrelated test tooling.
    - If MCP setup cannot be completed, state the exact blocker and do not pretend browser validation happened.
    - Validation must include at least one playable smoke test from first load through active play, controls, core interaction, scoring or progress feedback, and restart or replay without a full page reload.
    - Each validation pass should record the run command, URL tested, user flows exercised, screenshots or traces for visual/spatial behavior, console/network/runtime errors found and resolved, and remaining limitations.
    - Final reporting must distinguish verified behavior from unverified assumptions.

## Quality bar

Prefer concrete requirements over vague aspirations. Use MUST, SHOULD, and MAY carefully. State safe assumptions and the smallest set of genuinely blocking open decisions, if any. Separate product behavior from implementation details while making both precise enough for a competent programming agent to start building immediately.

Do not merely say “the app builds.” A browser-based game is incomplete until it has been exercised in a real browser. Treat awkward first-run UX, broken focus, unreadable layout, unresponsive input, invisible state changes, jank, and console errors as implementation defects. When a browser-observed improvement is obvious and within scope, the implementing agent should make it rather than only report it.

This is the finished software specification for **Transit City Swarm**.
