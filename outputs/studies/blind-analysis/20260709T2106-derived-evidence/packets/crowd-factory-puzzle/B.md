# Blind derived-evidence packet

Study: Crowd Factory Puzzle
Variant: B
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 182
- Variable payload words: 0
- Output words: 1314
- Local leverage: 7.22x
- Candidate facts: 90
- Counted facts: 90
- Discounted fact units: 89.25
- Information density per 1k output words: 67.9
- Information yield per 1k source words: 490.4

## Extracted fact candidates

- Use this implementation-ready software specification to build a browser-based puzzle game called **Crowd Factory Puzzle**.
- The specification is the source of truth for a programming agent or human developer that will build the first playable version.
- It must be concrete enough to implement without asking basic product-shape questions.
- This is a software specification, not a requirements interview, brainstorm, pitch, or planning conversation.
- Prefer concrete decisions and safe assumptions over exploratory questions.
- Mark only genuinely blocking open decisions.
- Specify a compact, browser-first puzzle game that integrates these mechanic references into one original design:
- Lemmings-style autonomous crowds: many tiny agents, indirect variant, assigned roles, environmental hazards, rescue pressure, and readable mass behavior.
- Factory automation belts and converters: conveyor routing, machines, inputs and outputs, throughput, bottlenecks, timing, resource transformation, and compact production chains.
- Sokoban-style spatial pushing puzzles: grid constraints, crates, blocking, irreversible mistakes, planning ahead, undo/restart, and level readability.
- The final design must not read like three pasted-together modules.
- It must define a single integrated mechanic: how the player indirectly routes autonomous workers, uses belts and machines to transform resources, and solves spatial pushing constraints within a realistic first-build scope.
- Use original names, visuals, rules, and assets.
- Existing games may be referenced only as high-level mechanic inspiration.
- Do not copy protected characters, maps, art, music, names, levels, UI, or distinctive presentation.
- Define asset ownership boundaries: no unlicensed copyrighted art, music, sounds, fonts, names, characters, or level layouts.
- Include these sections, adapted to the game:
- User job and value delivered.
- First-build scope and explicit out-of-scope features.
- Core loop: learn, plan, act, observe feedback, undo/restart or improve, complete the level.
- Win condition, loss/failure condition, scoring or rating if any.
- How the game teaches itself in the first minute.
- Explain the unified puzzle system in concrete terms.
- Define how autonomous workers move, how the player indirectly influences them, how conveyor belts and machines transform resources or workers’ carried items, and how pushable objects create spatial constraints.
- Clarify why the combined system creates planning depth without exceeding first-build complexity.
- Include examples-as-rules for at least two representative puzzle situations.
- **Puzzle objects and domain model**
- Define the key entities, states, identifiers, and transitions, including at minimum:
- Grid, tiles, entrances, exits, goals, hazards, blockers, and checkpoints if used.
- Autonomous workers and their readable state.
- Belts, splitters, gates, converters, machines, inputs, outputs, queues, and timing.
- Pushable crates or blocks, immovable walls, locks, switches, and any irreversible or recoverable mistakes.
- Level data structure and persistence needs.
- Game states: loading, menu, level select, playing, paused, won, failed, restarting, and settings where applicable.
- Keyboard and mouse variants for the first build.
- Touch variants only if in scope; otherwise state that the first build is desktop-browser first.
- Pause, restart, undo, level reset, and retry paths.
- Focus-loss, tab-switching, and page-visibility behavior: pause or safely suspend gameplay.
- Readable HUD: objective, remaining workers/resources, timer or move count if used, current tool/role, undo availability, and level status.
- Empty states, loading states, failure feedback, success feedback, and error handling.
- Accessibility requirements: readable contrast, keyboard operability for core actions where practical, non-color-only communication, reduced-motion consideration, and clear text labels.
- First playable level set and teaching sequence.
- How new objects and rules are introduced.
- Difficulty curve from approachable first minute to deeper planning.
- Level readability rules and constraints that prevent unfair puzzles.
- Restart and undo expectations for irreversible mistakes.
- Recommended implementation approach suitable for an ordinary browser game.
- Major components/modules and data flow.
- Rendering approach, update loop, timing model, collision/grid rules, worker simulation, belt/machine simulation, input handling, UI state, level loading, and local persistence.
- Performance requirements: stable frame pacing, no avoidable layout shifts during play, quick casual load, compressed/deferred assets, and smooth behavior on ordinary laptops.
- Browser compatibility expectations and responsive layout rules that preserve aspect ratio and readable UI across common viewport sizes.
- Maintainability and extension points for new levels, tiles, machines, worker roles, and visual themes.
- Coherent original visual style, even if minimal.
- Feedback rules for player actions: motion, animation, sound placeholders, score/status changes, messages, particles, hit pauses, or screen shake only when they improve legibility.
- How mass worker behavior remains readable.
- Asset style guide for the first build using original simple shapes, icons, or generated placeholder assets.
- The implementing agent must use a repeated build-run-observe-improve loop:
- Inspect the specification, repository structure, package scripts, existing tests, and framework conventions.
- Implement the smallest coherent browser-visible slice.
- Start the application with an existing development or preview command. If none exists, add the minimal project-appropriate command and document it.
- ... 30 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/crowd-factory-puzzle/B.json`
