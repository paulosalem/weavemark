# Blind derived-evidence packet

Study: Crowd Factory Puzzle
Variant: C
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 189
- Variable payload words: 0
- Output words: 1412
- Local leverage: 7.47x
- Candidate facts: 82
- Counted facts: 82
- Discounted fact units: 81.5
- Information density per 1k output words: 57.7
- Information yield per 1k source words: 431.2

## Extracted fact candidates

- Use this implementation-ready software specification to build a browser-based puzzle game called **Crowd Factory Puzzle**.
- The specification is the source of truth for a programming agent or human developer to build the first playable version.
- The output must be directly useful as implementation guidance, not a requirements interview, planning conversation, or brainstorm.
- Prefer concrete requirements and safe assumptions over exploratory questions.
- State the smallest set of genuinely blocking open decisions, if any.
- Design **Crowd Factory Puzzle** as an original browser puzzle game with original names, visuals, rules, and assets.
- Existing games may be used only as high-level mechanic references.
- Do not copy protected characters, maps, art, music, names, levels, UI, or distinctive presentation.
- The game should integrate three inspirations into one coherent mechanic rather than presenting three pasted-together modules:
- Autonomous crowd-routing puzzle play: many tiny agents move on their own, the player indirectly variants them, assigned roles change how they interact with the level, hazards create rescue pressure, and the behavior of the group remains readable at a glance.
- Compact factory automation: conveyors, sorters, converters, inputs, outputs, throughput, bottlenecks, timing, resource transformation, and short production chains create spatial and timing puzzles.
- Grid-based pushing constraints: crates, blockers, machine modules, and route objects occupy cells; pushing and repositioning them can create irreversible mistakes unless the player plans ahead and uses undo/restart.
- The core design must explain how the player indirectly routes autonomous workers, uses belts and machines to transform resources, and solves spatial pushing constraints while staying within a realistic first-build browser-game scope.
- This specification has clear sections that include, at minimum:
- Define the player job, value delivered, and why the game is fun.
- Define the win condition, failure condition, scoring or rating system, and what a complete round or level means.
- Define what MUST be included in the first playable build.
- Define what SHOULD be included if time allows.
- Define what is explicitly out of scope, especially online services, level editors, advanced animation, large asset pipelines, complex AI, or mobile-specific polish unless required for the first build.
- Explain the loop: inspect level, plan route, reposition objects, assign or trigger worker roles, start/simulate flow, observe bottlenecks and hazards, undo/restart/refine, complete the level.
- Make the first minute approachable while allowing later levels to become deeper and more strategic.
- Define the grid, worker spawn points, exits, resource sources, conveyors, machines, crates, blockers, hazards, and rescue targets.
- Explain how autonomous workers move without direct per-worker variant.
- Explain how the player changes the environment or assigns roles to influence crowd behavior.
- Explain how factory conversion interacts with worker routing and pushing puzzles.
- Explain how spatial mistakes are handled through undo, restart, previews, or level design.
- Specify keyboard and mouse variants, with touch support only if it is in scope.
- Include pause, restart, undo, level select/progression, and clear failure/retry paths.
- Ensure variants are responsive, predictable, and browser-friendly.
- Define each object type, its state, interactions, constraints, and visual feedback.
- Include workers, worker roles, conveyors, machines/converters, crates, gates, hazards, goal zones, resource items, blockers, switches, and tutorial signage if used.
- State deterministic timing, collision, queueing, routing, pushing, transformation, and hazard rules.
- Define worker movement speed, pathing rules, priority rules, collision/stacking behavior, role behavior, hazard response, and exit behavior.
- Keep behavior readable and debuggable. Avoid complex opaque AI for the first build.
- Define how many agents can be active while maintaining smooth browser performance.
- Provide a progression plan for a small first-build level set.
- Teach through playable interactions where possible.
- Introduce one new concept at a time, then combine mechanics.
- Include example level concepts that demonstrate routing, conversion, bottleneck, pushing, and rescue-pressure puzzles without copying existing game layouts.
- Establish a coherent original visual style suitable for simple browser implementation.
- Define HUD elements, status messages, feedback animations, accessibility expectations, readable colors, and responsive layout behavior.
- Preserve aspect ratio and readable UI across common viewport sizes.
- Avoid layout shifts during play; the game area should feel stable.
- Handle focus loss, tab switching, and page visibility changes by pausing or safely suspending gameplay.
- Persist appropriate local state such as settings, progress, unlocked levels, and best ratings.
- **Game states and domain model**
- Specify game states such as loading, menu, level select, playing, paused, win, lose, restart, and settings.
- Define core entities, identifiers, state transitions, persistence needs, and level data format.
- Separate product behavior from implementation details while making both precise enough to implement.
- Recommend a practical first-build architecture using standard web technology.
- Specify rendering approach, input handling, game loop/tick model, state management, level loading, persistence, audio policy, asset ownership boundaries, and extension points.
- Define performance expectations for ordinary laptops and modern mobile browsers if mobile play is in scope.
- Ensure no unlicensed copyrighted art, music, sound, fonts, names, or characters are required.
- Include performance, reliability, accessibility, maintainability, portability, and privacy/security requirements where relevant.
- Require stable performance, no console errors, quick loading, and deterministic puzzle behavior.
- Include unit, integration, end-to-end, compact, and visual/browser checks as appropriate.
- Require a playable smoke test that starts from first load, reaches active play, exercises variants and collisions or core interactions, observes scoring/progress feedback, and verifies restart or replay without a full page reload.
- **Playwright MCP browser validation**
- The implementing agent MUST use a repeated build-run-observe-improve loop:
- Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
- ... 22 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/crowd-factory-puzzle/C.json`
