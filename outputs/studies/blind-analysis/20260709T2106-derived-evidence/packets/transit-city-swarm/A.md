# Blind derived-evidence packet

Study: Transit City Swarm
Variant: A
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 89
- Variable payload words: 0
- Output words: 1024
- Local leverage: 11.51x
- Candidate facts: 70
- Counted facts: 70
- Discounted fact units: 69.5
- Information density per 1k output words: 67.9
- Information yield per 1k source words: 780.9

## Extracted fact candidates

- Use this implementation-ready software specification to build a browser-based strategy game with the working title **Transit City Swarm**.
- The specification is the source of truth for building the game.
- It must be directly useful to an AI programming agent or human developer and precise enough to begin implementation without asking basic product-shape questions.
- Prefer concrete requirements over exploratory questions.
- State safe assumptions and the smallest set of genuinely blocking open decisions, but do not turn the output into an interview script or brainstorming document.
- Design a browser-based strategy game that combines:
- transit-network drawing inspired by high-level Mini Metro-like mechanics;
- city growth inspired by high-level SimCity-like systemic expansion;
- ant-colony pathfinding concepts using pheromone-style trails and emergent route pressure.
- The game must use original names, visuals, rules, maps, UI, terminology, progression, audio, and assets.
- Existing games may be referenced only as high-level mechanic inspiration.
- Do not copy protected characters, maps, art, music, names, levels, UI, distinctive presentation, or other proprietary expressive elements.
- This coherent game specification uses these sections, adapted as needed to the game:
- Target player and play context.
- User job and value delivered.
- First-build scope and out-of-scope items.
- **Game Objective and Core Loop**
- Win/loss, scoring, survival, or success conditions.
- How the first minute teaches the player and how later play becomes deeper or more strategic.
- Transit network drawing and editing rules.
- Station, district, passenger, demand, route, line, vehicle, capacity, congestion, and transfer rules.
- Ant-colony pathfinding and pheromone-trail rules, including how agents choose paths, how trails strengthen, decay, and influence future routing.
- Timing, randomness, simulation ticks, spawning, escalation, balance, and failure conditions.
- Feedback loops between transit quality, city expansion, and route pressure.
- **Player variants and User Experience**
- Mouse, touch, keyboard, and any optional shortcuts.
- Menu, loading, playing, paused, win/lose, restart, and replay states.
- Empty states, errors, loading states, focus loss, tab switching, and page visibility behavior.
- Responsive layout and readable UI across common viewport sizes.
- Accessibility requirements, including keyboard reachability where practical, color contrast, readable labels, reduced-motion considerations, and non-color-only feedback.
- Animation, easing, motion, sound, particles, or other feedback that improves legibility and feel.
- Clear feedback for player actions through visual state, score changes, messages, animation, or sound.
- HUD constraints: keep information readable and limited to what the player needs now.
- Asset ownership boundaries: no unlicensed copyrighted art, music, sound, fonts, names, characters, maps, or distinctive presentation.
- Persistence needs such as settings, progress, unlocked levels, and high scores.
- Any data structures needed for graph routing, city simulation, pheromone maps, and browser storage.
- **Architecture and Browser Implementation Plan**
- Recommended browser technology approach.
- Major components and data flow.
- Simulation loop and separation between model, rendering, input, UI, and persistence.
- Important libraries or platform constraints.
- Extension points for future mechanics, levels, difficulty modes, procedural generation, accessibility, and analytics-free local telemetry if relevant.
- Performance targets for ordinary laptops and modern mobile browsers when mobile play is in scope.
- Loading strategy: defer or compress heavy assets and avoid layout shifts during play.
- Performance, reliability, portability, maintainability, and browser compatibility.
- Privacy and security boundaries for local-only state.
- Observability/debugging requirements useful during implementation.
- Stable gameplay behavior without console errors.
- Unlocks, milestones, escalating demand, city growth phases, or scenario structure.
- How the game remains approachable early and strategically deep later.
- Tuning parameters and suggested initial values.
- Unit checks for deterministic simulation rules where applicable.
- Integration checks for state transitions, persistence, routing, and UI interactions.
- compact and visual checks for game feel, readability, responsiveness, and accessibility.
- A playable smoke test that starts from first load, reaches active play, exercises variants and core interactions, observes scoring/progress feedback, and verifies restart or replay without a full page reload.
- **Playwright MCP Browser Validation Requirements**
- The implementing agent must use a repeated build-run-observe-improve loop.
- Before claiming browser validation, check whether Playwright MCP or equivalent browser automation tools are available.
- If Playwright MCP is unavailable, explicitly install or configure the official Playwright MCP server before browser validation. Prefer the host environment's standard MCP setup path; when Node/npm are available, the server command is commonly `npx @playwright/mcp@latest`.
- If the project itself needs Playwright tests, add Playwright through the project's package manager and install required browsers with the existing ecosystem command. Do not add duplicate or unrelated test tooling.
- ... 10 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/transit-city-swarm/A.json`
