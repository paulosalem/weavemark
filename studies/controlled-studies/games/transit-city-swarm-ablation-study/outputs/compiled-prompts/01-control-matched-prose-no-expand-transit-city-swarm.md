# Transit City Swarm: Browser Game Software Specification

Use this implementation-ready software specification to build a browser-based strategy game called **Transit City Swarm**. The specification is the source of truth for a programming agent or human developer. It must be concrete enough to start implementation without basic product-shape questions.

The game must use original names, visuals, rules, UI, maps, audio, assets, and presentation. Existing games may be referenced only as high-level mechanic inspiration. Do not copy protected characters, levels, maps, art direction, music, names, UI layouts, or distinctive presentation from any existing title.

## Product intent

Define **Transit City Swarm** as one integrated game, not three pasted-together modules. The design must reconcile and specialize these ideas into a new core system:

- Elegant transit network drawing: readable line creation, stations, routes, capacity, congestion, and minimalist legibility.
- Top-down city growth: zones, buildings, roads, population pressure, budgets, land-use effects, traffic, and growth feedback.
- Swarm pathfinding and pheromone-like demand trails: many simple agents, emergent demand paths, trail reinforcement, evaporation, congestion avoidance, and decentralized adaptation.

The specification MUST explain the integrated mechanic: how player-built networks shape city growth, how citizens or vehicles create and reinforce demand trails, how congestion changes growth, and how the player reads and responds to emergent flow.

## Required output shape

This coherent implementation-ready game specification uses these sections:

1. **Product intent**
   - Target player.
   - Player fantasy and value.
   - First-build scope.
   - Explicit out-of-scope items for the first build.

2. **Objective and success conditions**
   - Player objective.
   - Scoring, survival, growth, or win/loss conditions.
   - How a complete round/session begins, progresses, ends, and restarts.

3. **Core loop**
   - What the player observes.
   - What the player builds or changes.
   - How the simulation responds.
   - What feedback teaches the player.
   - How the player improves and tries again.

4. **Integrated simulation design**
   - City grid, stations, roads, zones, buildings, population, budgets, and growth pressure.
   - Transit lines, stops, vehicles, capacity, wait times, route load, and congestion.
   - Swarm agents representing citizens or trips.
   - Demand trails that reinforce successful paths, evaporate over time, and shift away from congestion.
   - Growth feedback: how access, congestion, travel time, and land use alter building upgrades, population density, revenue, and future demand.
   - Clear rules for how all systems influence each other.

5. **Player controls and interaction model**
   - Mouse controls for drawing, editing, deleting, and inspecting lines or zones.
   - Keyboard shortcuts if useful.
   - Touch controls if mobile play is in scope.
   - Pause, resume, restart, speed controls, and focus-loss behavior.
   - Empty, invalid, and error states for attempted actions.

6. **User experience and presentation**
   - Original visual style.
   - HUD layout and required information.
   - Readability rules for dense networks and moving agents.
   - Feedback for construction, invalid actions, congestion, growth, budget changes, score changes, and agent flow.
   - Onboarding that teaches through the first interactions where possible.
   - Accessibility and responsive layout requirements.
   - Stable game area with no disruptive layout shifts during play.

7. **Game state model**
   - Loading, menu, tutorial or first-run, playing, paused, game-over or completed, and restart states.
   - Persistent local state such as settings, progress, unlocked scenarios, or high scores, if included.
   - Handling page visibility changes, tab switching, and browser focus loss.

8. **Domain model**
   - Key entities, identifiers, and state fields for city cells, zones, buildings, stations, links, transit lines, vehicles, agents, demand trails, budget ledger entries, events, and scenario state.
   - State transitions for construction, demolition, route editing, agent spawning, path selection, trail update, congestion update, growth update, budget tick, and round end.
   - Persistence needs and data that should remain ephemeral.

9. **Implementation architecture**
   - Recommended browser implementation approach.
   - Rendering strategy, simulation tick strategy, input handling, UI state, and data flow.
   - Important modules/classes/components and their responsibilities.
   - Timing, randomness, deterministic seeding if useful, and performance constraints.
   - Asset ownership boundaries: no unlicensed copyrighted art, music, sound, fonts, names, or characters.

10. **Progression and balance**
    - First-minute experience.
    - Difficulty ramp.
    - Scenario or level structure if included.
    - Unlocks, constraints, budgets, or escalating demand.
    - Tuning parameters for capacity, trail reinforcement, trail evaporation, congestion, growth, cost, revenue, and scoring.

11. **Validation strategy**
    - Unit checks for simulation rules.
    - Integration checks for city growth, routing, congestion, and budget interactions.
    - Browser validation plan using Playwright MCP or equivalent real-browser automation.
    - Manual and visual checks for readability, responsiveness, accessibility, and game feel.

12. **Acceptance criteria**
    - Testable conditions showing the first build is complete.
    - Include at minimum: first load, learning the goal, playing a complete round, seeing meaningful feedback, restarting without page reload, stable performance, responsive input, no console errors, and browser-observed validation evidence.

## Browser and implementation requirements

The game must run in a web browser and feel playable, not merely render a static prototype.

- Load quickly enough for casual play; defer or compress heavy assets.
- Run smoothly on ordinary laptops. Modern mobile browser support is optional only if explicitly scoped; if mobile is included, preserve readability and input predictability.
- Preserve aspect ratio and readable UI across common viewport sizes.
- Avoid layout shifts during play.
- Keep HUD information limited to what the player needs now.
- Use animation, easing, particles, sound, or other feedback only where they improve legibility and game feel.
- Balance the first minute to be approachable, with later play becoming deeper, faster, or more strategic.
- Include pause, restart, and clear failure/retry paths.

## Browser validation requirements

The implementing agent MUST use a repeated build-run-observe-improve loop for the browser result:

1. Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
2. Implement the smallest coherent slice that should be visible or testable in the browser.
3. Start the application with an existing development or preview command. If no command exists, add the minimal project-appropriate command and document it.
4. Open the running URL with Playwright MCP or equivalent browser automation and interact as a real user: click, drag, resize, start a game round, build/edit routes, observe congestion/growth feedback, pause, resume, lose or complete a session if applicable, and restart.
5. Observe the rendered page, accessibility tree, console output, network behavior, screenshots, and any persisted state that affects the user experience.
6. Compare observed behavior against the specification and against professional product quality: clarity, responsiveness, stability, accessibility, visual polish, and absence of console/runtime errors.
7. Inspect source files when browser behavior reveals a defect or design weakness.
8. Improve the implementation, then repeat the browser pass until the main experience works and no high-value improvement remains obvious.

Before claiming browser validation, check whether Playwright MCP or equivalent browser automation is available. If it is not available, install or configure the official Playwright MCP server where possible. When Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`. If project-level Playwright tests are needed, add Playwright through the project package manager and install required browsers with the existing ecosystem command. Do not add duplicate or unrelated test tooling. If MCP setup cannot be completed, state the exact blocker and do not pretend browser validation happened.

Each validation pass SHOULD leave concrete evidence:

- command used to run the application;
- URL tested;
- user flows exercised;
- screenshots or traces when useful for the spatial interface;
- console, network, or runtime errors found and resolved;
- remaining limitations or follow-up opportunities.

For this game, browser validation MUST include at least one playable smoke test that starts from first load, reaches active play, exercises controls and the core transit/city/swarm interactions, observes scoring or progress feedback, and verifies restart or replay without a full page reload.

## Quality bar

The specification should be precise, testable, and directly actionable.

- Prefer concrete requirements over exploratory questions.
- State assumptions and open decisions explicitly, but do not turn the output into a conversation with the user.
- Use MUST, SHOULD, and MAY carefully for requirements, recommendations, and optional enhancements.
- Separate product behavior from implementation details while making both precise enough for a developer to act.
- Define what is in scope and out of scope for the first build.
- Never stop at “the app builds” when the result is interactive. A browser-based game is incomplete until it has been exercised in a real browser.
- Treat awkward first-run UX, broken focus, unreadable layout, unresponsive input, invisible state changes, jank, and console errors as implementation defects.
- Final reporting MUST distinguish verified behavior from unverified assumptions.
