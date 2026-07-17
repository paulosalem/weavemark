# Transit City Swarm

Transit City Swarm is an original, dependency-free browser strategy game built from `compiled-spec.md`. The player watches swarm demand trails, draws a minimalist transit network, upgrades overloaded nodes, prunes weak corridors, and tries to keep city growth reliable before budget or congestion collapses.

## Run

```bash
npm run serve
```

Then open <http://localhost:5173>. Click **Start round**, place stops in **Build** mode, use **Upgrade** on red or busy stations/segments, use **Prune** to remove poor choices, and restart from the in-page controls.

## Verify

```bash
npm run check
npm test
```

For browser validation, run `npm run serve`, open <http://localhost:5173>, and smoke test: start a round, draw at least two connected stops, observe moving agents and amber demand trails, upgrade or prune a network element, pause/resume, and restart or play to a result without reloading.

## Validation performed

- Run command: `npm run serve -- --bind 127.0.0.1`
- URL tested: <http://127.0.0.1:5173>
- Browser flow exercised with Playwright MCP: first load, start round, build a connected line, handle invalid placement feedback, observe active agents/trails/scoring, reach a win result, play again, upgrade a station, prune a segment, pause/resume, restart without reload, and resize to a compact viewport.
- Visual artifact: `transit-city-swarm-smoke.png` captures an active round with the network, agents, and HUD visible.
- Browser console after fixes: no errors or warnings during the final smoke flow.

## Implemented scope

- Vanilla HTML/CSS/JavaScript canvas game; no external runtime dependencies.
- Deterministic seeded city with residential, commercial, and industrial districts, blockers, buildings, roads, stations, line segments, agents, demand trails, congestion fields, budget, score, reliability, pressure, and a timed game session.
- Playable loop: observe trails, build connected stops, select and extend lines, upgrade capacity, prune network pieces, watch agents route through the network, see growth/congestion feedback, win or lose, pause, change speed, and restart in page.
- Original names, visuals, rules, colors, map layout, and placeholder assets. No protected characters, maps, music, art, or proprietary rule sets are used.

## Known gaps

- Sound is intentionally omitted in this first build; all required feedback is visual and textual.
- Local persistence for settings/high scores is not included because the smallest complete first build only needs an in-page session and restart.
