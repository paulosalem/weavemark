# Blind derived-evidence packet

Study: Transit City Swarm
Variant: C
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 187
- Variable payload words: 0
- Output words: 1244
- Local leverage: 6.65x
- Candidate facts: 76
- Counted facts: 76
- Discounted fact units: 75.25
- Information density per 1k output words: 60.5
- Information yield per 1k source words: 402.4

## Extracted fact candidates

- Use this implementation-ready software specification to build a browser-based strategy game called **Transit City Swarm**.
- The specification is the source of truth for a programming agent or developer who will build the game; it must be concrete, testable, and directly actionable rather than a brainstorm, interview script, or list of open-ended questions.
- Specify a playable web game in which the player plans and adapts a growing urban transit organism.
- Elegant transit-network drawing: the player creates readable lines, routes, stops, transfers, and capacity upgrades on a minimalist top-down city map.
- City-growth simulation: zones, buildings, roads, population pressure, budgets, land-use effects, traffic, and growth feedback respond to player choices.
- Swarm-style demand adaptation: many simple citizens or vehicles move through the city, leave demand trails, reinforce successful corridors, evaporate unused paths, avoid congestion, and expose emergent transport needs.
- The final design must not feel like three separate modules pasted together.
- Define the integrated mechanic: player-built networks shape city growth; citizens and vehicles create visible demand trails; congestion changes both flow and development pressure; and the player reads emergent flow patterns to decide where to draw, extend, reroute, upgrade, or prune the network.
- The game must use original names, visuals, rules, systems, UI, maps, audio, fonts, and assets.
- Existing games may be used only as high-level mechanic references.
- Do not copy protected characters, maps, art, music, names, levels, interface layouts, distinctive presentation, or proprietary rule sets.
- State this requirement in the specification and define safe placeholder asset guidance for a first build.
- This coherent implementation-ready game specification uses these sections:
- Target player and user job.
- What value the game delivers in a short browser session.
- First-build scope and explicit out-of-scope items.
- **Objective and win/loss or scoring**
- Scoring, success, failure, or endurance conditions.
- How a complete round begins, escalates, ends, and restarts.
- The repeatable loop of observing demand, drawing or modifying network elements, watching swarm movement, receiving feedback, earning or losing resources, and improving the city.
- The first-minute experience and how the player learns through interaction.
- How later play becomes deeper, faster, or more strategic.
- City map representation: zones, buildings, roads, stations, stops, line segments, districts, terrain or blockers if applicable.
- Transit-network rules: creating lines, connecting stops, capacity, route length, transfer behavior, upgrade costs, deletion/rerouting, and readability constraints.
- Swarm demand rules: citizen or vehicle agents, origin/destination selection, route choice, demand trails, reinforcement, evaporation, congestion avoidance, and decentralized adaptation.
- City-growth rules: how accessibility, congestion, land use, services, budget, population pressure, and travel reliability change building growth and demand.
- Feedback loops: how player networks influence city growth, how growth changes demand, and how demand trails reveal the next strategic decision.
- Timing, randomness, tick/update rules, and deterministic seeds where useful for testing.
- **Player variants and user experience**
- Supported variants for mouse and keyboard; include touch support only if in scope.
- Network drawing, selecting, inspecting, upgrading, pausing, restarting, and speed variants.
- HUD information that must remain readable and limited to what the player needs now.
- Empty states, onboarding, tooltips, error states, invalid placement feedback, and clear retry paths.
- Game states: loading, menu, playing, paused, win/lose or results, and restart.
- Accessibility and responsive behavior across common browser viewport sizes.
- Original visual style suitable for minimalist but legible city simulation.
- Color, motion, animation, sound, and feedback guidelines.
- How demand trails, congestion, capacity, station load, city growth, and budget pressure are visualized without clutter.
- Rules for avoiding layout shifts and preserving aspect ratio during play.
- Key entities such as City, District, Zone, Building, Road, Station, Line, Segment, Agent, DemandTrail, CongestionCell, Budget, Upgrade, GameClock, and GameSession.
- Important fields, identifiers, relationships, and state transitions.
- Persistence needs such as settings, high scores, unlocked scenarios, or local saved sessions.
- Browser implementation approach using standard web technologies or an appropriate lightweight game stack.
- Major components, data flow, render loop, simulation loop, input handling, and UI layer.
- Performance strategy for many agents and trail fields.
- Asset loading, deferred or compressed assets, and local-state persistence.
- Maintainable extension points for new map seeds, scenarios, upgrades, building types, or agent behaviors.
- Responsive input and stable performance on ordinary laptops and modern mobile browsers if mobile is included.
- Quick load for casual play; defer heavy assets.
- Page visibility and focus-loss handling: pause or safely suspend gameplay on tab switching or focus loss.
- No console/runtime errors in normal play.
- Security and privacy constraints for a local browser game.
- Early, mid, and late-game progression.
- Resource economy, budget pressure, unlocks, milestones, difficulty growth, and failure pressure.
- Balancing principles that make the first minute approachable while allowing strategic depth.
- Testable conditions showing that a first build is complete.
- Include at minimum: a player can open the page, understand the goal, start a round, draw or modify a network, observe agents and demand trails, see city growth or congestion feedback, receive score/resource feedback, pause, lose/win or finish a run, and restart without a full page reload.
- Include performance, browser stability, originality, and no-console-error criteria.
- **Verification and browser validation strategy**
- Include unit, integration, simulation, visual, compact, and end-to-end checks where appropriate.
- ... 16 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/transit-city-swarm/C.json`
