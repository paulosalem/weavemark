# Blind evaluation packet

Study: Transit City Swarm
Variant: C
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# Transit City Swarm: No-Expand Browser Game Specification

@directive-a programming/foundations/software-spec
@directive-a programming/types/web-based-game
@directive-a programming/validation/playwright-mcp-browser-validation

Design a browser-based strategy game that combines Mini Metro-style transit
network drawing, SimCity-style city growth, and ant-colony pathfinding with
pheromone trails.

The game must use original names, visuals, rules, and assets. Use existing games
only as high-level mechanic references; do not copy protected characters, maps,
art, music, names, levels, UI, or distinctive presentation.

This implementation-ready game specification defines objective, core loop,
player variants, simulation rules, feedback, progression, browser implementation
plan, validation strategy, and acceptance criteria.



## Compiled output

# Transit City Swarm: Browser Game Specification

Use this implementation-ready software specification to build a browser-based strategy game with the working title **Transit City Swarm**.

The specification is the source of truth for building the game. It must be directly useful to an AI programming agent or human developer and precise enough to begin implementation without asking basic product-shape questions. Prefer concrete requirements over exploratory questions. State safe assumptions and the smallest set of genuinely blocking open decisions, but do not turn the output into an interview script or brainstorming document.

## Product Direction

Design a browser-based strategy game that combines:

- transit-network drawing inspired by high-level Mini Metro-like mechanics;
- city growth inspired by high-level SimCity-like systemic expansion;
- ant-colony pathfinding concepts using pheromone-style trails and emergent route pressure.

The game must use original names, visuals, rules, maps, UI, terminology, progression, audio, and assets. Existing games may be referenced only as high-level mechanic inspiration. Do not copy protected characters, maps, art, music, names, levels, UI, distinctive presentation, or other proprietary expressive elements.

## Required Specification Shape

This coherent game specification uses these sections, adapted as needed to the game:

1. **Product Intent**
   - Target player and play context.
   - User job and value delivered.
   - First-build scope and out-of-scope items.

2. **Game Objective and Core Loop**
   - Player objective.
   - Primary actions.
   - Challenge model.
   - Win/loss, scoring, survival, or success conditions.
   - How the first minute teaches the player and how later play becomes deeper or more strategic.

3. **Core Mechanics**
   - Transit network drawing and editing rules.
   - Station, district, passenger, demand, route, line, vehicle, capacity, congestion, and transfer rules.
   - City-growth simulation rules.
   - Ant-colony pathfinding and pheromone-trail rules, including how agents choose paths, how trails strengthen, decay, and influence future routing.
   - Timing, randomness, simulation ticks, spawning, escalation, balance, and failure conditions.
   - Feedback loops between transit quality, city expansion, and route pressure.

4. **Player variants and User Experience**
   - Mouse, touch, keyboard, and any optional shortcuts.
   - Menu, loading, playing, paused, win/lose, restart, and replay states.
   - HUD information and prioritization.
   - Empty states, errors, loading states, focus loss, tab switching, and page visibility behavior.
   - Responsive layout and readable UI across common viewport sizes.
   - Accessibility requirements, including keyboard reachability where practical, color contrast, readable labels, reduced-motion considerations, and non-color-only feedback.

5. **Game Feel and Presentation**
   - Original visual style.
   - Animation, easing, motion, sound, particles, or other feedback that improves legibility and feel.
   - Clear feedback for player actions through visual state, score changes, messages, animation, or sound.
   - HUD constraints: keep information readable and limited to what the player needs now.
   - Asset ownership boundaries: no unlicensed copyrighted art, music, sound, fonts, names, characters, maps, or distinctive presentation.

6. **Domain Model**
   - Key entities and their fields.
   - State transitions and identifiers.
   - Persistence needs such as settings, progress, unlocked levels, and high scores.
   - Any data structures needed for graph routing, city simulation, pheromone maps, and browser storage.

7. **Architecture and Browser Implementation Plan**
   - Recommended browser technology approach.
   - Major components and data flow.
   - Rendering approach.
   - Simulation loop and separation between model, rendering, input, UI, and persistence.
   - Important libraries or platform constraints.
   - Extension points for future mechanics, levels, difficulty modes, procedural generation, accessibility, and analytics-free local telemetry if relevant.
   - Performance targets for ordinary laptops and modern mobile browsers when mobile play is in scope.
   - Loading strategy: defer or compress heavy assets and avoid layout shifts during play.

8. **Non-Functional Requirements**
   - Performance, reliability, portability, maintainability, and browser compatibility.
   - Privacy and security boundaries for local-only state.
   - Observability/debugging requirements useful during implementation.
   - Stable gameplay behavior without console errors.

9. **Progression and Balance**
   - Difficulty curve.
   - Unlocks, milestones, escalating demand, city growth phases, or scenario structure.
   - How the game remains approachable early and strategically deep later.
   - Tuning parameters and suggested initial values.

10. **Validation Strategy**
   - Unit checks for deterministic simulation rules where applicable.
   - Integration checks for state transitions, persistence, routing, and UI interactions.
   - End-to-end browser checks.
   - compact and visual checks for game feel, readability, responsiveness, and accessibility.
   - A playable smoke test that starts from first load, reaches active play, exercises variants and core interactions, observes scoring/progress feedback, and verifies restart or replay without a full page reload.

11. **Playwright MCP Browser Validation Requirements**
   - The implementing agent must use a repeated build-run-observe-improve loop.
   - Before claiming browser validation, check whether Playwright MCP or equivalent browser automation tools are available.
   - If Playwright MCP is unavailable, explicitly install or configure the official Playwright MCP server before browser validation. Prefer the host environment's standard MCP setup path; when Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`.
   - If the project itself needs Playwright tests, add Playwright through the project's package manager and install required browsers with the existing ecosystem command. Do not add duplicate or unrelated test tooling.
   - If MCP setup cannot be completed, state the exact blocker and do not pretend browser validation happened.
   - Validation must include starting the application, opening the running URL with Playwright MCP, interacting as a real user, observing rendered page behavior, inspecting console/network/runtime errors, and iterating until the main experience works.
   - Evidence should include the command used to run the app, tested URL, flows exercised, screenshots or traces when useful, errors found and resolved, and remaining limitations.
   - Final reporting must distinguish verified behavior from unverified assumptions.

12. **Acceptance Criteria**
   - Testable conditions that indicate the first build is complete.
   - Include browser-game completion criteria: a player can open the page, learn the goal, play a complete round, understand success or failure, restart without reloading, and experience stable performance without console errors.
   - Include specification-quality criteria: all core mechanics, browser states, implementation plan, validation plan, and ownership constraints are clear enough for implementation.

## Writing Requirements

Use MUST, SHOULD, and MAY carefully for requirements, recommendations, and optional enhancements. Separate product behavior from implementation details while making both concrete. Include assumptions where needed. Avoid vague phrases such as “make it fun” unless they are paired with implementable mechanics or validation criteria.
