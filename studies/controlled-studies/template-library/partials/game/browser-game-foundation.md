## Browser game implementation foundation

- Build a first playable browser version with deterministic game state,
  explicit update/render/input boundaries, and no external server dependency.
- Use Canvas, SVG, or DOM rendering according to the simplest project fit.
- Define states for loading, menu, setup, active play, paused, victory, defeat,
  restart, and error/recovery.
- Use requestAnimationFrame with delta-time clamping so tab stalls do not break
  simulation.
- Persist only non-sensitive local settings or progress in browser storage when
  needed.
- Keep performance stable on ordinary laptops by avoiding unbounded particles,
  unbounded entity arrays, duplicate loops, and expensive per-frame DOM work.
- Include keyboard-first controls, visible focus, clear control help, pause,
  restart, resize handling, and tab visibility handling.
