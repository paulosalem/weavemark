# Transit City Swarm

A polished, original, dependency-light browser strategy game built from `compiled-spec.md`. The player draws a living transit line across a procedural city, watches citizen swarm trails reveal demand, upgrades overloaded stops, manages budget/reliability, finishes a shift, and restarts without reloading.

## Run

```bash
npm install
npm start
```

Open <http://127.0.0.1:4287>.

You can also serve the folder directly with `python3 -m http.server 4287 --bind 127.0.0.1`; no build step is required.

## Play

1. Press **Start round**.
2. Use **Build line** or key `1`, then click the map to place connected stops.
3. Watch warm demand trails, red congestion cells, station load rings, budget, reliability, score, and population.
4. Use **Inspect** (`2`), **Upgrade** (`3`), **Prune** (`E`), **Pause** (`Space`), **Restart** (`R`), speed controls, or **Finish shift**.
5. Press **Play again** on the result screen to restart without a full page reload.

## Verification

```bash
npm test
npm run smoke
```

- `npm test` runs deterministic simulation checks with Node's built-in test runner.
- `npm run smoke` runs a Chromium Playwright flow from first load through start, line drawing, active swarm feedback, pause/resume, finish, screenshot capture, and replay. The smoke screenshot is saved at `test-results/transit-city-swarm-smoke.png`.

## Implementation notes

- Plain local web technology: `index.html`, `styles.css`, and ES modules in `src/`.
- No copied art, maps, characters, audio, fonts, or proprietary rules; all visuals are procedural canvas drawing and system fonts.
- The simulation core is deterministic from seed `1427` and models districts, buildings, roads, stations, line capacity, agents, demand trails, congestion, budget, reliability, city growth, and round results.
- Browser validation target is desktop Chromium via Playwright. Pointer events are used for mouse/touch-compatible input, but automated validation currently covers desktop.

## Known gaps

No known gaps for the first-build acceptance criteria in `compiled-spec.md`.
