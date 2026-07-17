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

# Crowd Factory Puzzle: Browser Game Software Specification

Use this implementation-ready software specification to build a browser-based puzzle game called **Crowd Factory Puzzle**. The specification is the source of truth for a programming agent or human developer to build the first playable version.

The output must be directly useful as implementation guidance, not a requirements interview, planning conversation, or brainstorm. Prefer concrete requirements and safe assumptions over exploratory questions. State the smallest set of genuinely blocking open decisions, if any.

## Product intent

Design **Crowd Factory Puzzle** as an original browser puzzle game with original names, visuals, rules, and assets. Existing games may be used only as high-level mechanic references. Do not copy protected characters, maps, art, music, names, levels, UI, or distinctive presentation.

The game should integrate three inspirations into one coherent mechanic rather than presenting three pasted-together modules:

- Autonomous crowd-routing puzzle play: many tiny agents move on their own, the player indirectly variants them, assigned roles change how they interact with the level, hazards create rescue pressure, and the behavior of the group remains readable at a glance.
- Compact factory automation: conveyors, sorters, converters, inputs, outputs, throughput, bottlenecks, timing, resource transformation, and short production chains create spatial and timing puzzles.
- Grid-based pushing constraints: crates, blockers, machine modules, and route objects occupy cells; pushing and repositioning them can create irreversible mistakes unless the player plans ahead and uses undo/restart.

The core design must explain how the player indirectly routes autonomous workers, uses belts and machines to transform resources, and solves spatial pushing constraints while staying within a realistic first-build browser-game scope.

## Required specification shape

This specification has clear sections that include, at minimum:

1. **Objective and target player**
   - Define the player job, value delivered, and why the game is fun.
   - Define the win condition, failure condition, scoring or rating system, and what a complete round or level means.

2. **First-build scope**
   - Define what MUST be included in the first playable build.
   - Define what SHOULD be included if time allows.
   - Define what is explicitly out of scope, especially online services, level editors, advanced animation, large asset pipelines, complex AI, or mobile-specific polish unless required for the first build.

3. **Core loop**
   - Explain the loop: inspect level, plan route, reposition objects, assign or trigger worker roles, start/simulate flow, observe bottlenecks and hazards, undo/restart/refine, complete the level.
   - Make the first minute approachable while allowing later levels to become deeper and more strategic.

4. **Integrated game mechanic**
   - Define the grid, worker spawn points, exits, resource sources, conveyors, machines, crates, blockers, hazards, and rescue targets.
   - Explain how autonomous workers move without direct per-worker variant.
   - Explain how the player changes the environment or assigns roles to influence crowd behavior.
   - Explain how factory conversion interacts with worker routing and pushing puzzles.
   - Explain how spatial mistakes are handled through undo, restart, previews, or level design.

5. **Player variants and interaction**
   - Specify keyboard and mouse variants, with touch support only if it is in scope.
   - Include pause, restart, undo, level select/progression, and clear failure/retry paths.
   - Ensure variants are responsive, predictable, and browser-friendly.

6. **Puzzle objects and rules**
   - Define each object type, its state, interactions, constraints, and visual feedback.
   - Include workers, worker roles, conveyors, machines/converters, crates, gates, hazards, goal zones, resource items, blockers, switches, and tutorial signage if used.
   - State deterministic timing, collision, queueing, routing, pushing, transformation, and hazard rules.

7. **Agent behavior**
   - Define worker movement speed, pathing rules, priority rules, collision/stacking behavior, role behavior, hazard response, and exit behavior.
   - Keep behavior readable and debuggable. Avoid complex opaque AI for the first build.
   - Define how many agents can be active while maintaining smooth browser performance.

8. **Level progression and onboarding**
   - Provide a progression plan for a small first-build level set.
   - Teach through playable interactions where possible.
   - Introduce one new concept at a time, then combine mechanics.
   - Include example level concepts that demonstrate routing, conversion, bottleneck, pushing, and rescue-pressure puzzles without copying existing game layouts.

9. **User experience and presentation**
   - Establish a coherent original visual style suitable for simple browser implementation.
   - Define HUD elements, status messages, feedback animations, accessibility expectations, readable colors, and responsive layout behavior.
   - Preserve aspect ratio and readable UI across common viewport sizes.
   - Avoid layout shifts during play; the game area should feel stable.
   - Handle focus loss, tab switching, and page visibility changes by pausing or safely suspending gameplay.
   - Persist appropriate local state such as settings, progress, unlocked levels, and best ratings.

10. **Game states and domain model**
    - Specify game states such as loading, menu, level select, playing, paused, win, lose, restart, and settings.
    - Define core entities, identifiers, state transitions, persistence needs, and level data format.
    - Separate product behavior from implementation details while making both precise enough to implement.

11. **Browser implementation plan**
    - Recommend a practical first-build architecture using standard web technology.
    - Specify rendering approach, input handling, game loop/tick model, state management, level loading, persistence, audio policy, asset ownership boundaries, and extension points.
    - Define performance expectations for ordinary laptops and modern mobile browsers if mobile play is in scope.
    - Ensure no unlicensed copyrighted art, music, sound, fonts, names, or characters are required.

12. **Non-functional requirements**
    - Include performance, reliability, accessibility, maintainability, portability, and privacy/security requirements where relevant.
    - Require stable performance, no console errors, quick loading, and deterministic puzzle behavior.

13. **Validation strategy**
    - Include unit, integration, end-to-end, compact, and visual/browser checks as appropriate.
    - Require a playable smoke test that starts from first load, reaches active play, exercises variants and collisions or core interactions, observes scoring/progress feedback, and verifies restart or replay without a full page reload.

14. **Playwright MCP browser validation**
    - The implementing agent MUST use a repeated build-run-observe-improve loop:
      1. Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
      2. Implement the smallest coherent slice that should be visible or testable in the browser.
      3. Start the application with an existing development or preview command. If no command exists, add the minimal project-appropriate command and document it.
      4. Open the running URL with Playwright MCP or an equivalent browser automation surface and interact as a real user: click, type, drag, resize, navigate menus, start a level, move objects, run the simulation, win or lose, restart, and exercise important empty, loading, success, and error states.
      5. Observe the rendered page, accessibility tree, console output, network behavior, screenshots, and persisted state that affects the user experience.
      6. Compare observed behavior against the specification and professional product quality: clarity, responsiveness, stability, accessibility, visual polish, and absence of console/runtime errors.
      7. Inspect relevant source files when browser behavior reveals a defect or design weakness.
      8. Improve the implementation, then repeat the browser pass until the main experience works and no high-value improvement remains obvious.
    - Before claiming browser validation, check whether Playwright MCP or equivalent browser automation tools are available.
    - If Playwright MCP is not available, install or configure the official Playwright MCP server before validation when the environment permits it. When Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`.
    - If project-level Playwright tests are needed, add Playwright through the project package manager and install required browsers with the existing ecosystem command. Do not add duplicate or unrelated test tooling.
    - If MCP setup cannot be completed, state the exact blocker and do not pretend browser validation happened.
    - Evidence should include the command used to run the app, URL tested, user flows exercised, screenshots or traces for spatial interface checks, console/network/runtime errors found and resolved, and remaining limitations.
    - Final reporting MUST distinguish verified behavior from unverified assumptions.

15. **Acceptance criteria**
    - Provide testable completion criteria for the first build.
    - A good first build is complete only when a player can open the browser page, learn the goal, play at least one complete level, understand why they succeeded or failed, restart without reloading, and experience stable performance without console errors.
    - Include criteria for original asset use, readable puzzle rules, undo/restart behavior, level progression, browser stability, and validation evidence.

## Output requirements

This is one coherent implementation-ready game specification. Use concrete bullets, tables, and examples where helpful. Avoid vague recommendations. Use MUST, SHOULD, and MAY carefully for requirements, recommendations, and optional enhancements. Do not include copied protected content. Do not describe the design as a collection of separate inspirations; state the final integrated Crowd Factory Puzzle rules directly.
