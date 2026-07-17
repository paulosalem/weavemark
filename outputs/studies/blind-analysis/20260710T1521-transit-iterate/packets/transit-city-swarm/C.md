# Blind evaluation packet

Study: Transit City Swarm
Variant: C
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# Transit City Swarm: Expanded Browser Game Specification

@directive-a programming/foundations/software-spec
@directive-a programming/types/web-based-game
@directive-a programming/validation/playwright-mcp-browser-validation

Design **Transit City Swarm**, an original browser strategy game.

@iterate 2
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

# Transit City Swarm: Implementation-Ready Browser Game Specification Prompt

Design **Transit City Swarm**, an original browser-playable strategy game prototype. The output must be the source-of-truth software specification for a competent developer or programming agent to implement the first playable build without asking basic product-shape questions.

Design exactly one integrated, immediately implementable first scenario. Do not brainstorm variants. The game loop must combine transit-line drawing, city growth, and swarm demand trails into one coherent mechanic: player-built transit routes reshape agent movement, visible demand trails, congestion, accessibility, and city growth.

The player builds, edits, prunes, reroutes, and upgrades transit routes on a small grid city. Routes change accessibility; accessibility changes where buildings grow, densify, stagnate, or decline. Simulated agents try to reach jobs, homes, and services. As they move or fail to move, they leave visible demand trails that reinforce when repeated demand uses or wants the same corridor and evaporate when demand fades. Trails are primarily an observational, player-facing planning signal, not a magical force that creates demand: the player reads trail intensity, direction, fading, unmet-demand marks, and congestion overlays to decide where to draw, remove, reroute, extend, or upgrade lines.

Congestion must be readable and consequential. Overloaded segments slow agents, redirect agents to alternate paths when available, reduce effective accessibility, suppress nearby growth, and create pressure to improve the network rather than simply add route length.

Return a compact game design and software specification for exactly one immediately implementable browser prototype scenario. The specification must separate product behavior from implementation details while making both precise enough to build. State safe assumptions explicitly. Define what is in scope and out of scope for the first build. Do not copy protected names, maps, art, music, UI, or distinctive rule sets.

## Required output

### 1. Product intent and core premise
In one concise paragraph, state the target player experience and central playable idea: player-built transit routes reshape agent movement, visible demand trails, congestion, accessibility, and city growth. Include the player job, objective, core action, challenge, and value delivered.

### 2. Functional scope for the first browser build
Define the first build as a complete playable browser round with:
- Game states: loading, menu or start screen, playing, paused, win, loss, and restart.
- variants for mouse and touch where practical; keyboard shortcuts MAY be included.
- Responsive layout expectations and stable game area behavior.
- HUD requirements for budget, turn, score, route tools, selected route or segment, congestion, trails, accessibility, and end-of-turn explanation.
- In-scope features for the prototype.
- Explicitly out-of-scope features for the prototype.

### 3. Scenario goal and accounting model
Define one fixed-length scenario with:
- Total turn count.
- Starting budget, per-turn income, maintenance costs, and upgrade costs.
- One coherent score formula that produces both per-turn score and cumulative score.
- Win target by the final turn.
- Loss threshold or failure condition.
- What the player is optimizing each turn.

The score, budget, win condition, loss condition, and end-of-turn explanation must use the same accounting model. Avoid disconnected point systems.

### 4. Exact first scenario layout
Specify exact grid coordinates for every initial entity so a developer can implement the scenario directly.

Include:
- Map size and coordinate system.
- Neighborhoods with exact bounds or center cells.
- Buildings with coordinates, type, population, jobs, service value, and starting growth state.
- Starting stops and routes, if any, with ordered coordinate paths.
- Demand sources and destinations.
- Initial budget and income.
- Number of turns.

The scenario must include:
- A few neighborhoods with distinct demand patterns.
- One obvious initial route opportunity.
- One congestion trap that emerges after early growth.
- One reason to prune or reroute instead of only adding more segments.
- One upgrade decision that competes with expansion.

### 5. Domain model and state transitions
Define the game state model with concrete entities, identifiers, and state changes:
- `GameState`, `Scenario`, `GridCell`, `Neighborhood`, `Building`, `Stop`, `Route`, `RouteSegment`, `Agent`, `DemandTrail`, `CongestionState`, `AccessibilityState`, `ScoreState`, and `Action`.
- Required fields for each entity.
- Persistence needs: local high score, settings, or scenario completion MAY be stored locally; no server persistence is required unless explicitly specified.
- State transitions for start, pause, resume, advance turn, win, loss, and restart.

### 6. Deterministic browser simulation model
Use browser-friendly simplifications. Specify:
- Fixed random seed or deterministic demand generation.
- Grid movement model.
- Pathfinding model, such as shortest path by weighted grid cost.
- Walking cost, transit cost, transfer cost, and blocked or slow segment costs.
- Stop catchment radius.
- Segment capacity.
- Congestion threshold and congestion penalty.
- Rerouting rule when congestion exceeds the threshold.
- Agent count per turn and spawn logic.
- Destination selection logic.
- Demand trail reinforcement per agent attempt.
- Trail evaporation per turn.
- Minimum visible trail intensity.
- Accessibility formula.
- Growth, densification, stagnation, and shrinkage rules.
- How satisfied trips increase growth.
- How congestion and unmet demand suppress growth.

Provide simple formulas, tables, or pseudocode that can be implemented in JavaScript without interpretation.

### 7. Explicit update order
Define the exact per-turn order of operations, for example:
1. Player observes map, trails, congestion, score, and budget.
2. Player takes route-editing actions.
3. Maintenance and action costs are applied.
4. Agents spawn.
5. Agents choose destinations.
6. Agents pathfind using current route, walking, and congestion weights.
7. Agents move or fail.
8. Trails reinforce from attempted movement and unmet demand.
9. Trails evaporate.
10. Segment congestion is calculated.
11. Accessibility is recalculated.
12. Buildings grow, densify, stagnate, or shrink.
13. Score, budget, win/loss state, and explanation are updated.

Make congestion, trails, accessibility, growth, and scoring unambiguous.

### 8. Player actions
Define each action with numeric cost, limit, and effect:
- Draw new route segment.
- Extend existing route.
- Remove or prune segment.
- Reroute segment.
- Add stop.
- Upgrade capacity.
- Optional inspect or pause action.

Make pruning and rerouting strategically useful. For example, pruning a low-value segment may reduce maintenance, improve average route speed, or redirect agents toward a stronger corridor.

### 9. User experience, visual feedback, and first-minute onboarding
Specify how the browser prototype should teach and visualize the game:
- First-minute onboarding that lets a new player understand the objective and variants within one minute, preferably through the first interaction rather than only instructions.
- Demand trails: intensity, fading, direction, unmet demand, and recent reinforcement.
- Congestion: segment color, warnings, and capacity numbers.
- Route capacity and upgrades.
- Agent movement and rerouting.
- Building growth, stagnation, and decline.
- Accessibility changes.
- End-of-turn score explanation.
- Empty, error, disabled-action, insufficient-budget, invalid-route, win, loss, pause, and restart states.
- Accessibility and readability requirements, including color plus shape or icon redundancy for important map states.

Trails must be the primary planning affordance: a new player should be able to look at the trails and infer where to draw, prune, reroute, or upgrade.

### 10. Architecture and implementation notes
Specify a practical browser implementation plan:
- Recommended rendering approach, such as HTML Canvas with DOM HUD, SVG, or DOM grid; choose one and justify briefly.
- Main modules/components and their responsibilities.
- Data flow between player input, simulation, rendering, scoring, and persistence.
- Deterministic update loop rules.
- Asset constraints: use original minimal vector/shape art, simple generated audio or no audio, and no unlicensed copyrighted art, music, sound, fonts, names, or characters.
- Performance rules for ordinary laptops and modern mobile browsers when mobile play is in scope.
- Handling for focus loss, tab switching, and page visibility changes: pause or safely suspend gameplay.
- Browser compatibility assumptions.

### 11. Non-functional requirements
Define requirements for:
- Responsiveness and input predictability.
- Stable frame rate and avoidance of jank.
- No layout shifts during play.
- Fast initial load and lightweight assets.
- Clear failure/retry path.
- Restart without full page reload.
- Maintainable code structure.
- Privacy: no unnecessary network calls or personal data collection.
- Reliability: no console/runtime errors during normal play.

### 12. Browser validation and Playwright MCP acceptance
Define what the first browser build must prove:
- Player can open the page, understand the goal, edit routes, and advance turns.
- Player can play a complete round, reach win or loss, and restart without reloading.
- Agents visibly respond to route changes.
- Demand trails reinforce and fade.
- Congestion changes travel time or routing.
- Congestion suppresses nearby growth.
- Building growth responds to accessibility and satisfied demand.
- Score panel updates after each turn using the specified formula.
- The scenario can be completed in the browser.
- A new player can understand the objective and variants within one minute.
- The game runs without console/runtime errors in the validation pass.

The implementing agent MUST validate with a real browser, preferably Playwright MCP or equivalent. Before claiming browser validation, check whether Playwright MCP or equivalent browser automation is available. If it is not available, install or configure the official Playwright MCP server where possible; when Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`. If setup cannot be completed, state the exact blocker and do not claim browser validation happened.

The implementation loop MUST be build-run-observe-improve:
1. Inspect the specification, repository structure, package scripts, tests, and framework conventions.
2. Implement the smallest coherent visible/testable slice.
3. Start the app with an existing development or preview command, or add the minimal project-appropriate command.
4. Open the running URL in the browser and interact as a real user: start, edit routes, advance turns, observe agents/trails/congestion/growth/score, pause, win or lose, and restart.
5. Observe rendered page, accessibility tree where useful, console output, screenshots or traces, and persisted state.
6. Fix defects and repeat until the main experience works and no high-value improvement remains obvious.

Include a Playwright browser smoke acceptance checklist for a complete playable round and restart. Specify the command used to run the app, the URL to test, the flows to exercise, expected observations, screenshot/trace evidence if applicable, and how to distinguish verified behavior from unverified assumptions.

### 13. Tuning constants table
End with one table listing every numeric constant used, including map size, coordinates or entity counts, turn count, seed, agent counts, movement costs, catchment radius, capacities, congestion thresholds, trail rates, growth rates, action costs, maintenance costs, score weights, win target, loss threshold, UI timing constants, and performance targets.

Required output: concise, implementation-ready, concrete, and internally consistent.
