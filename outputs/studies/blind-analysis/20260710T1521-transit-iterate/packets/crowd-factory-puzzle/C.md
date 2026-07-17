# Blind evaluation packet

Study: Crowd Factory Puzzle
Variant: C
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# Crowd Factory Puzzle: No-Expand Browser Game Specification

@directive-a programming/foundations/software-spec
@directive-a programming/types/web-based-game
@directive-a programming/validation/playwright-mcp-browser-validation

Design a browser-based puzzle game that combines Lemmings-style autonomous
crowds, factory automation belts and converters, and Sokoban-style spatial
pushing puzzles.

The game must use original names, visuals, rules, and assets. Use existing games
only as high-level mechanic references; do not copy protected characters, maps,
art, music, names, levels, UI, or distinctive presentation.

This implementation-ready game specification defines objective, core loop,
player variants, puzzle objects, agent behavior, level progression, browser
implementation plan, validation strategy, and acceptance criteria.



## Compiled output

# Crowd Factory Puzzle: Browser Game Software Specification

Use this implementation-ready software specification to build an original browser-based puzzle game that combines:

- autonomous crowd agents that move according to simple rules and must be guided indirectly;
- factory automation systems such as belts, gates, routers, converters, buffers, counters, and resource transformations;
- spatial pushing puzzles where the player repositions crates, machines, blockers, or other objects to create workable paths.

The finished specification must be directly useful to an AI programming agent or human developer. It must be a software specification, not a brainstorming document, interview script, or implementation diary.

## Originality and asset boundaries

The game must use original names, visuals, rules, levels, UI, audio, and assets. Existing games may be referenced only as high-level mechanic inspiration. Do not copy protected characters, maps, art, music, names, levels, distinctive UI, story presentation, or recognizable trade dress from any existing game.

If the specification proposes a title, factions, creatures, machines, currencies, level names, or art direction, they must be original.

## Required specification content

Include all sections needed for a first playable browser implementation:

1. **Product intent**
   - Target player.
   - Player fantasy and value delivered.
   - Intended session length.
   - What makes the game understandable in the first minute and strategically deeper later.

2. **Game objective and core loop**
   - The player's objective in each level.
   - Win, loss, retry, and scoring or ranking conditions.
   - The learn-act-feedback-improve loop.
   - How a player completes a full round and restarts without reloading the page.

3. **Core mechanics**
   - Autonomous crowd-agent behavior, including movement rules, reactions to obstacles, routing, crowd flow, hazards, waiting, conversion, failure, and goal arrival.
   - Factory components such as belts, splitters, mergers, gates, converters, switches, sensors, timed devices, capacity limits, and resource or agent transformations.
   - Sokoban-style pushing rules, including what can be pushed, by whom, from which direction, collision constraints, locked states, reset affordances, and how pushing interacts with belts and agents.
   - Clear rules for timing, grid or physics model, collisions, determinism, randomness, and edge cases.
   - At least one concrete example level interaction showing how the three mechanic families combine.

4. **Player variants**
   - Keyboard and mouse variants as the baseline.
   - Touch variants if mobile play is in scope.
   - Pause, restart, undo or rewind if supported, level select, settings, and accessibility shortcuts.
   - Expected responsiveness and feedback for each action.

5. **Puzzle objects and domain model**
   - A concise catalog of entities: player avatar or cursor, crowd agents, machines, belts, pushable objects, walls, goals, hazards, switches, resources, UI state, and level definitions.
   - Important fields and state transitions for each entity.
   - Level data structure, identifiers, persistence needs, and save/progress format.
   - In-scope and out-of-scope features for the first build.

6. **Level progression and onboarding**
   - A playable tutorial sequence that teaches through interaction rather than only text.
   - Level progression from basic movement to combined crowd-routing, automation, conversion, and pushing puzzles.
   - Difficulty pacing, optional challenges, failure recovery, and hints.
   - Requirements for locked/unlocked levels and local progress persistence.

7. **User experience and presentation**
   - Original visual style, readable game board, HUD, menus, pause screen, win/lose states, settings, and level select.
   - Feedback through motion, animation timing, sound cues, particles, messages, state changes, or other legible signals.
   - Empty, loading, error, and first-run states.
   - Accessibility requirements: readable contrast, scalable UI, keyboard operability, focus management, reduced-motion option, captions or visual alternatives for audio cues, and clear non-color-only indicators.
   - Responsive behavior across common viewport sizes while preserving a stable game area and avoiding layout shifts during play.

8. **Browser implementation plan**
   - Recommended architecture for a modern browser implementation.
   - Game state model: loading, menu, playing, paused, won, lost, level transition, and restart states.
   - Rendering approach, update loop, input handling, collision resolution, animation system, level parser, persistence, and asset loading.
   - Performance targets for ordinary laptops and, if mobile is in scope, modern mobile browsers.
   - Browser compatibility assumptions.
   - Local state that may be persisted, such as settings, progress, unlocked levels, and best scores.
   - Asset ownership boundaries: no unlicensed copyrighted art, music, sound, fonts, names, or characters.

9. **Non-functional requirements**
   - Performance, reliability, portability, maintainability, accessibility, and privacy expectations.
   - Requirements for quick loading, deferred or compressed assets, stable frame pacing, safe handling of tab switching or focus loss, and absence of console/runtime errors.
   - Security and privacy constraints appropriate for a local browser game.

10. **Validation strategy**
   - Unit tests for deterministic game rules, collision, pushing, routing, conversion, level completion, scoring, and persistence.
   - Integration tests for level loading, input handling, state transitions, restart/retry, menus, and settings.
   - Browser-grounded validation using Playwright MCP or equivalent browser automation.
   - A repeated build-run-observe-improve loop:
     1. Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
     2. Implement the smallest coherent browser-visible slice.
     3. Start the application with an existing development or preview command, or add the minimal project-appropriate command if none exists.
     4. Open the running URL with Playwright MCP and interact as a real user: click, type, drag, resize, start a level, exercise variants, trigger collisions and conversions, win or fail, pause, restart, and replay without a full page reload.
     5. Observe the rendered page, accessibility tree, console output, network behavior, screenshots or traces, and persisted state.
     6. Compare observed behavior against the specification for clarity, responsiveness, stability, accessibility, visual polish, and absence of console/runtime errors.
     7. Inspect relevant source files when browser behavior reveals a defect or design weakness.
     8. Improve the implementation and repeat until the main experience works and no high-value improvement remains obvious.
   - Before claiming browser validation, check whether Playwright MCP or equivalent browser automation is available. If Playwright MCP is not available, install or configure the official Playwright MCP server where possible; when Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`.
   - If MCP setup cannot be completed, state the exact blocker and do not claim browser validation happened.
   - If the project needs Playwright tests, add Playwright through the project package manager and install required browsers using the existing ecosystem command; do not add duplicate or unrelated test tooling.

11. **Acceptance criteria**
   - Testable conditions proving that a player can open the browser page, learn the goal, play a complete level, understand success or failure, restart without reloading, and experience stable performance.
   - Criteria for originality, gameplay completeness, variants, puzzle rule correctness, onboarding, accessibility, browser compatibility, persistence, and validation evidence.
   - Required final implementation report items: command used to run the app, URL tested, user flows exercised, screenshots or trace artifacts for the spatial interface, console/network/runtime errors found and resolved, and remaining limitations or follow-up opportunities.
   - The final report must distinguish verified behavior from unverified assumptions.

## Output requirements

This is a coherent, concrete software specification. Use MUST, SHOULD, and MAY carefully. Prefer specific implementable requirements over vague aspirations. State safe assumptions and only the smallest set of genuinely blocking open decisions. Separate product behavior from implementation details while making both precise enough for a developer to act.
