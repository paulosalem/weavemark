# Blind derived-evidence packet

Study: Crowd Factory Puzzle
Variant: A
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 90
- Variable payload words: 0
- Output words: 1171
- Local leverage: 13.01x
- Candidate facts: 70
- Counted facts: 70
- Discounted fact units: 70.0
- Information density per 1k output words: 59.8
- Information yield per 1k source words: 777.8

## Extracted fact candidates

- Use this implementation-ready software specification to build an original browser-based puzzle game that combines:
- autonomous crowd agents that move according to simple rules and must be guided indirectly;
- factory automation systems such as belts, gates, routers, converters, buffers, counters, and resource transformations;
- spatial pushing puzzles where the player repositions crates, machines, blockers, or other objects to create workable paths.
- The finished specification must be directly useful to an AI programming agent or human developer.
- It must be a software specification, not a brainstorming document, interview script, or implementation diary.
- The game must use original names, visuals, rules, levels, UI, audio, and assets.
- Existing games may be referenced only as high-level mechanic inspiration.
- Do not copy protected characters, maps, art, music, names, levels, distinctive UI, story presentation, or recognizable trade dress from any existing game.
- If the specification proposes a title, factions, creatures, machines, currencies, level names, or art direction, they must be original.
- Include all sections needed for a first playable browser implementation:
- Player fantasy and value delivered.
- What makes the game understandable in the first minute and strategically deeper later.
- **Game objective and core loop**
- Win, loss, retry, and scoring or ranking conditions.
- How a player completes a full round and restarts without reloading the page.
- Autonomous crowd-agent behavior, including movement rules, reactions to obstacles, routing, crowd flow, hazards, waiting, conversion, failure, and goal arrival.
- Factory components such as belts, splitters, mergers, gates, converters, switches, sensors, timed devices, capacity limits, and resource or agent transformations.
- Sokoban-style pushing rules, including what can be pushed, by whom, from which direction, collision constraints, locked states, reset affordances, and how pushing interacts with belts and agents.
- Clear rules for timing, grid or physics model, collisions, determinism, randomness, and edge cases.
- At least one concrete example level interaction showing how the three mechanic families combine.
- Keyboard and mouse variants as the baseline.
- Touch variants if mobile play is in scope.
- Pause, restart, undo or rewind if supported, level select, settings, and accessibility shortcuts.
- Expected responsiveness and feedback for each action.
- **Puzzle objects and domain model**
- A concise catalog of entities: player avatar or cursor, crowd agents, machines, belts, pushable objects, walls, goals, hazards, switches, resources, UI state, and level definitions.
- Important fields and state transitions for each entity.
- Level data structure, identifiers, persistence needs, and save/progress format.
- In-scope and out-of-scope features for the first build.
- A playable tutorial sequence that teaches through interaction rather than only text.
- Level progression from basic movement to combined crowd-routing, automation, conversion, and pushing puzzles.
- Difficulty pacing, optional challenges, failure recovery, and hints.
- Requirements for locked/unlocked levels and local progress persistence.
- Original visual style, readable game board, HUD, menus, pause screen, win/lose states, settings, and level select.
- Feedback through motion, animation timing, sound cues, particles, messages, state changes, or other legible signals.
- Empty, loading, error, and first-run states.
- Accessibility requirements: readable contrast, scalable UI, keyboard operability, focus management, reduced-motion option, captions or visual alternatives for audio cues, and clear non-color-only indicators.
- Responsive behavior across common viewport sizes while preserving a stable game area and avoiding layout shifts during play.
- Recommended architecture for a modern browser implementation.
- Game state model: loading, menu, playing, paused, won, lost, level transition, and restart states.
- Rendering approach, update loop, input handling, collision resolution, animation system, level parser, persistence, and asset loading.
- Performance targets for ordinary laptops and, if mobile is in scope, modern mobile browsers.
- Local state that may be persisted, such as settings, progress, unlocked levels, and best scores.
- Asset ownership boundaries: no unlicensed copyrighted art, music, sound, fonts, names, or characters.
- Performance, reliability, portability, maintainability, accessibility, and privacy expectations.
- Requirements for quick loading, deferred or compressed assets, stable frame pacing, safe handling of tab switching or focus loss, and absence of console/runtime errors.
- Security and privacy constraints appropriate for a local browser game.
- Unit tests for deterministic game rules, collision, pushing, routing, conversion, level completion, scoring, and persistence.
- Integration tests for level loading, input handling, state transitions, restart/retry, menus, and settings.
- Browser-grounded validation using Playwright MCP or equivalent browser automation.
- Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
- Implement the smallest coherent browser-visible slice.
- Start the application with an existing development or preview command, or add the minimal project-appropriate command if none exists.
- Open the running URL with Playwright MCP and interact as a real user: click, type, drag, resize, start a level, exercise variants, trigger collisions and conversions, win or fail, pause, restart, and replay without a full page reload.
- Observe the rendered page, accessibility tree, console output, network behavior, screenshots or traces, and persisted state.
- Compare observed behavior against the specification for clarity, responsiveness, stability, accessibility, visual polish, and absence of console/runtime errors.
- Inspect relevant source files when browser behavior reveals a defect or design weakness.
- Improve the implementation and repeat until the main experience works and no high-value improvement remains obvious.
- Before claiming browser validation, check whether Playwright MCP or equivalent browser automation is available. If Playwright MCP is not available, install or configure the official Playwright MCP server where possible; when Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`.
- ... 10 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/crowd-factory-puzzle/A.json`
