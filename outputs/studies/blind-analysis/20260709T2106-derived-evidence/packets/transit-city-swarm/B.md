# Blind derived-evidence packet

Study: Transit City Swarm
Variant: B
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 180
- Variable payload words: 0
- Output words: 1410
- Local leverage: 7.83x
- Candidate facts: 96
- Counted facts: 96
- Discounted fact units: 95.0
- Information density per 1k output words: 67.4
- Information yield per 1k source words: 527.8

## Extracted fact candidates

- Use this implementation-ready software specification to build a browser-based strategy game called **Transit City Swarm**.
- The specification is the source of truth for a programming agent or human developer.
- It must be concrete enough to start implementation without basic product-shape questions.
- The game must use original names, visuals, rules, UI, maps, audio, assets, and presentation.
- Existing games may be referenced only as high-level mechanic inspiration.
- Do not copy protected characters, levels, maps, art direction, music, names, UI layouts, or distinctive presentation from any existing title.
- Define **Transit City Swarm** as one integrated game, not three pasted-together modules.
- The design must reconcile and specialize these ideas into a new core system:
- Elegant transit network drawing: readable line creation, stations, routes, capacity, congestion, and minimalist legibility.
- Top-down city growth: zones, buildings, roads, population pressure, budgets, land-use effects, traffic, and growth feedback.
- Swarm pathfinding and pheromone-like demand trails: many simple agents, emergent demand paths, trail reinforcement, evaporation, congestion avoidance, and decentralized adaptation.
- The specification MUST explain the integrated mechanic: how player-built networks shape city growth, how citizens or vehicles create and reinforce demand trails, how congestion changes growth, and how the player reads and responds to emergent flow.
- This coherent implementation-ready game specification uses these sections:
- Explicit out-of-scope items for the first build.
- Scoring, survival, growth, or win/loss conditions.
- How a complete round/session begins, progresses, ends, and restarts.
- What the player builds or changes.
- What feedback teaches the player.
- How the player improves and tries again.
- City grid, stations, roads, zones, buildings, population, budgets, and growth pressure.
- Transit lines, stops, vehicles, capacity, wait times, route load, and congestion.
- Swarm agents representing citizens or trips.
- Demand trails that reinforce successful paths, evaporate over time, and shift away from congestion.
- Growth feedback: how access, congestion, travel time, and land use alter building upgrades, population density, revenue, and future demand.
- Clear rules for how all systems influence each other.
- **Player variants and interaction model**
- Mouse variants for drawing, editing, deleting, and inspecting lines or zones.
- Touch variants if mobile play is in scope.
- Pause, resume, restart, speed variants, and focus-loss behavior.
- Empty, invalid, and error states for attempted actions.
- HUD layout and required information.
- Readability rules for dense networks and moving agents.
- Feedback for construction, invalid actions, congestion, growth, budget changes, score changes, and agent flow.
- Onboarding that teaches through the first interactions where possible.
- Accessibility and responsive layout requirements.
- Stable game area with no disruptive layout shifts during play.
- Loading, menu, tutorial or first-run, playing, paused, game-over or completed, and restart states.
- Persistent local state such as settings, progress, unlocked scenarios, or high scores, if included.
- Handling page visibility changes, tab switching, and browser focus loss.
- Key entities, identifiers, and state fields for city cells, zones, buildings, stations, links, transit lines, vehicles, agents, demand trails, budget ledger entries, events, and scenario state.
- State transitions for construction, demolition, route editing, agent spawning, path selection, trail update, congestion update, growth update, budget tick, and round end.
- Persistence needs and data that should remain ephemeral.
- Recommended browser implementation approach.
- Rendering strategy, simulation tick strategy, input handling, UI state, and data flow.
- Important modules/classes/components and their responsibilities.
- Timing, randomness, deterministic seeding if useful, and performance constraints.
- Asset ownership boundaries: no unlicensed copyrighted art, music, sound, fonts, names, or characters.
- Scenario or level structure if included.
- Unlocks, constraints, budgets, or escalating demand.
- Tuning parameters for capacity, trail reinforcement, trail evaporation, congestion, growth, cost, revenue, and scoring.
- Unit checks for simulation rules.
- Integration checks for city growth, routing, congestion, and budget interactions.
- Browser validation plan using Playwright MCP or equivalent real-browser automation.
- compact and visual checks for readability, responsiveness, accessibility, and game feel.
- Testable conditions showing the first build is complete.
- Include at minimum: first load, learning the goal, playing a complete round, seeing meaningful feedback, restarting without page reload, stable performance, responsive input, no console errors, and browser-observed validation evidence.
- The game must run in a web browser and feel playable, not merely render a static prototype.
- Load quickly enough for casual play; defer or compress heavy assets.
- Run smoothly on ordinary laptops. Modern mobile browser support is optional only if explicitly scoped; if mobile is included, preserve readability and input predictability.
- Preserve aspect ratio and readable UI across common viewport sizes.
- ... 36 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/transit-city-swarm/B.json`
