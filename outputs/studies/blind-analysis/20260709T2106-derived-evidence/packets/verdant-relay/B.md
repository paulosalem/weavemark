# Blind derived-evidence packet

Study: Verdant Relay
Variant: B
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 251
- Variable payload words: 5
- Output words: 5950
- Local leverage: 23.71x
- Candidate facts: 319
- Counted facts: 319
- Discounted fact units: 313.5
- Information density per 1k output words: 52.7
- Information yield per 1k source words: 1249.0

## Extracted fact candidates

- Use this implementation-ready specification to build **Verdant Relay**, a playable browser game whose route defense, deckbuilder choices, living ecosystem feedback, original 2D assets, and real browser validation form one coherent first build.
- This is a software specification for a programming agent.
- It MUST be concrete enough to implement without asking basic product-shape questions.
- State first-build scope, safe assumptions, and genuine open decisions.
- Do not write an interview script or generic planning prompt.
- Game pitch:** Verdant Relay is a living-railway garden-defense deckbuilder. Blight travels along railway lanes toward a central garden relay. The player uses a small hand of cards to grow defensive plants, restore habitats, redirect route pressure, upgrade defenses, and recover damaged ecosystem nodes before leaks collapse the relay.
- Target user:** casual strategy players who understand tower defense and card choices but need clear first-run teaching, readable feedback, and short-session completion.
- First-build promise:** a complete vertical slice playable in one browser page: load, start, learn, draw cards, place or upgrade defenses, start deterministic waves, observe ecosystem feedback, leak or win, pause/resume, restart without page reload, and validate in a real browser.
- One map with 3 railway lanes, a protected Garden Relay, and visible habitat tiles.
- 6 deterministic waves plus a short tutorial wave.
- Seeded deck draws and seeded ecosystem events for repeatable testing.
- 12 cards, 4 defensive plant types, 4 blight threat types, 3 habitat/resource types, 2 upgrade tiers.
- Local-only browser play; no backend, accounts, multiplayer, leaderboards, paid content, or network dependency.
- Original or generated placeholder 2D sprites with documented generation prompts, metadata, and provenance.
- Playwright MCP or equivalent browser validation proving the main play loop.
- Out of scope for the first build**
- Procedural maps, endless mode, large card pools, advanced pathfinding, online saves, mobile-first layout beyond responsive readability, music composition beyond simple generated or placeholder audio, and monetization.
- Protected objective:** the Garden Relay at the rail terminus has `relay_health = 10`. Blight units that reach it cause leaks. If `relay_health <= 0`, the run fails.
- Win condition:** defeat all units in Wave 6 while keeping `relay_health > 0` and ecosystem `resilience >= 20`.
- Ecosystem `resilience <= 0` at the end of a wave.
- A scripted validation failure occurs only in tests, not normal play.
- Read wave preview: lanes, threat icons, route arrows, spawn timing, rewards, and ecosystem risk.
- Spend `sun_energy` and `spore_tokens` to play cards: plant, upgrade, habitat, intervention, route, resource, or recovery.
- Preview placement/range/target/effect; invalid actions show exact reasons.
- Systems simulate movement, attacks, growth, blight spread, pollination, decay, leaks, rewards, and recovery.
- End wave: gain rewards, draft 1 of 3 cards or upgrade/remove 1 card, update ecosystem, show failure lessons or next-wave plan.
- Continue, win, lose, pause/resume, or restart.
- Player sees title, one-sentence goal, Start button, and a simple 3-lane map.
- Tutorial points to the Garden Relay, incoming blight lane, hand of cards, and one legal planting tile.
- First card play is constrained but real; player previews range, places a `Moss Sprayer`, starts the tutorial wave, sees blight slowed/damaged, earns a reward, and draws the next hand.
- Gameplay systems MUST run only in states that permit them.
- State; Entered by; Active systems; Required UI; Exit
- `Loading`; page load; asset preload, manifest validation; progress bar, fallback text; `MainMenu` when assets ready
- `MainMenu`; load complete or quit; animated background only; Start, Options, Credits/Asset provenance; Start -> `PlayingSetup`
- `PlayingSetup`; new run/wave end; input, card preview, placement preview; map, HUD, hand, wave preview, ecosystem panel; Start Wave -> `WaveActive`; Pause -> `Paused`
- `WaveActive`; wave start; movement, attack, blight, ecosystem tick, animation, sound; same HUD plus wave progress and speed variants; wave clear -> `Reward`; relay/ecosystem fail -> `GameOver`; Pause -> `Paused`
- `Reward`; wave clear; draft/upgrade/remove UI; reward choices, deck delta, next-wave preview; Continue -> `PlayingSetup`
- `Paused`; Escape, P, visibility loss, blur; no gameplay simulation; UI still responds; Resume, Restart, Main Menu, options overlay; Resume returns to prior state
- `GameOver`; loss or win; result animation, score persistence; Win/Lose reason, stats, lesson, Play Again, Main Menu; Play Again -> reset run
- `Error`; unrecoverable asset/runtime issue; none except reporting; clear error message and restart/reload option; restart or reload
- Page visibility changes, tab switching, and focus loss MUST pause or safely suspend gameplay.
- Restart MUST reset run state without full page reload.
- Recommended stack: TypeScript, Vite, HTML Canvas 2D or PixiJS.
- Keep the engine small and inspectable.
- Run simulation systems using fixed-step ticks.
- All gameplay state is expressed as entities with components; avoid global mutable singletons.
- Global services MAY exist for rendering, asset registry, input, audio, seeded RNG, and persistence, but gameplay facts live in world state.
- Systems are pure or near-pure over world state where feasible and are deterministic under a seed.
- Use a stable top-down or slight isometric 2D view.
- Camera bounds clamp to the map; never show void outside the map.
- If camera movement is used, smooth-follow or pan with lerp speed factor near `5.0`.
- Screen shake MAY occur on relay damage: amplitude `4px`, decay `0.3s`, disabled by reduced-motion setting.
- Preserve aspect ratio and readable UI at common desktop browser sizes; mobile MAY stack panels but must remain playable if claimed.
- Store settings, tutorial completion, and top-10 scores locally as JSON in `localStorage`.
- A later desktop wrapper MAY export the same structure as a `RON/JSON file`.
- Do not persist secrets or user personal data.
- Lanes: `north_rail`, `central_rail`, `south_rail`.
- Each lane has visible rail ties and arrows showing threat direction.
- Garden Relay occupies 2x2 tiles at the right edge.
- Habitat tiles sit adjacent to rails and can host plants/interventions.
- ... 259 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/verdant-relay/B.json`
