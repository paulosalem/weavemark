# Orbital Drift

A dependency-light single-page canvas racing game built from `compiled-spec.md`. Pilot a small spacecraft through ordered gates for two laps while managing inertia, asteroid collisions, planets, and gravity wells.

## Run

```bash
npm start
```

Open <http://127.0.0.1:4173>. No package install is required for the current project because it uses only browser APIs, Python's static file server, and Node's built-in test runner.

## Controls

| Action | Keys |
| --- | --- |
| Rotate | `A` / `D` or `ArrowLeft` / `ArrowRight` |
| Thrust | `W` or `ArrowUp` |
| Brake / stabilize | `Space`, `S`, or `ArrowDown` |
| Pause / resume | `P`, `Escape`, or `Enter` while paused |
| Restart | `R` |

## Verify

```bash
npm test
```

Browser smoke validation should start the app with `npm start`, open <http://127.0.0.1:4173>, and exercise first load, active play, steering/thrust, checkpoint progress, gravity influence, collision feedback, pause/resume, and restart without reload.

Validation performed for this implementation:

- `npm test`
- `npm start` serving <http://127.0.0.1:4173>
- Playwright MCP browser smoke covering first load, active play, thrust/steering, checkpoint progress, gravity well influence, asteroid collision penalty, pause/resume timer suspension, restart without reload, and console output with no errors or warnings after the favicon fix.

## Implementation notes

- Stack: plain HTML, CSS, and JavaScript with a `<canvas>` renderer.
- Collision model: asteroid, planet, and boundary hits bounce the craft away, add a 2-second time penalty, and briefly dampen control.
- Persistence: only the local best time is stored in `localStorage`; storage failures are logged and gameplay continues.
- Scope choices: audio, moving asteroids, online leaderboards, account login, mobile touch controls, and external assets are intentionally omitted for the first build.
- Known gaps: none for the requested first-build browser implementation.
