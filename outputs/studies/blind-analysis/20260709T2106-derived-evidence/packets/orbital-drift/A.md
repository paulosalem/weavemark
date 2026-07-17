# Blind derived-evidence packet

Study: Orbital Drift
Variant: A
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 61
- Variable payload words: 61
- Output words: 672
- Local leverage: 11.02x
- Candidate facts: 55
- Counted facts: 55
- Discounted fact units: 55.0
- Information density per 1k output words: 81.8
- Information yield per 1k source words: 901.6

## Extracted fact candidates

- This is the coherent implementation-ready specification for Orbital Drift.
- Treat this specification as the source of truth for a programming agent or human engineer.
- Include first-build scope, out-of-scope items, architecture, domain model,
- durable records, workflows, UI surfaces, automation rules, validation plan,
- failure handling, privacy/provenance rules, and acceptance criteria.
- Distinguish required first-build behavior from optional later enhancements.
- Avoid separate support prompts, prompt packs, or artifact manifests.
- Every major requirement should have an observable user-facing or validation
- Use concrete field names, states, events, screens, checks, and recovery paths
- instead of generic quality advice.
- Design Orbital Drift as a complete single-page browser racing game.
- Product intent: The player pilots a small craft through a compact asteroid belt with planets, orbital gates, repair beacons, gravity wells, propulsion, and lap-based racing. The first build must be playable in one browser page: start racing, pass checkpoints, experience hazards and gravity, finish or fail a round, see feedback, and restart without reloading.
- Include one playable course, start/finish line, ordered checkpoints or gates,
- at least one lap, visible hazards, recovery aids, timer, progress feedback,
- pause, restart, and completion/failure states.
- Vehicle movement should use deterministic 2D vectors with acceleration,
- velocity, damping, rotation, stable frame-time handling, and clear collision or
- Gates must be passed in order; wrong gates should not advance progress; lap
- count increments only after the full gate sequence and finish crossing.
- Show title, one-sentence objective, concise variants, start instruction, HUD,
- next-gate indicator, timer, checkpoint progress, collision/penalty feedback,
- Validation should exercise first load, start, movement, checkpoint progress,
- hazard interaction, scoring/timer feedback, pause/resume, restart without page
- Build a first playable browser version with deterministic game state,
- explicit update/render/input boundaries, and no external server dependency.
- Use Canvas, SVG, or DOM rendering according to the simplest project fit.
- Define states for loading, menu, setup, active play, paused, victory, defeat,
- Use requestAnimationFrame with delta-time clamping so tab stalls do not break
- Persist only non-sensitive local settings or progress in browser storage when
- Keep performance stable on ordinary laptops by avoiding unbounded particles,
- unbounded entity arrays, duplicate loops, and expensive per-frame DOM work.
- Include keyboard-first variants, visible focus, clear variant help, pause,
- restart, resize handling, and tab visibility handling.
- Use only original, non-infringing assets. Do not request, imitate, or include
- copyrighted characters, logos, sprites, or distinctive owned styles.
- First builds may use placeholder shapes, but the specification should define
- sprite roles, sizes, collision footprints, state names, animation metadata,
- palette, frame count, FPS, loop flag, transparent background, sheet packing,
- Store asset provenance, generation prompt if used, source file, derived file,
- Validate readability at game scale, consistent palette, transparent
- backgrounds, hitbox fit, no unwanted text, no artifacts, and no infringement.
- Validate the actual browser experience, not only static source inspection.
- Record command used to run the app, URL tested, browser flows exercised,
- screenshots or traces when available, console errors found and resolved, and
- Browser validation should cover first load, primary user flow, invalid inputs,
- persistence across restart or reload, responsive layout, keyboard/focus
- behavior, recovery states, and absence of runtime console errors.
- Prefer Playwright MCP or an equivalent real-browser tool when available. If the
- browser tool cannot run, report the exact blocker and do not claim browser
- Acceptance requires a first-session path that proves the product is usable,
- understandable, recoverable, and backed by saved evidence.
- This complete implementation specification includes product intent, first-build
- scope, out-of-scope items, player objective, game loop, variants, physics,
- hazards, scoring, visual style, browser architecture, state model, data and
- local-storage choices, validation plan, browser smoke test, evidence to report,

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/orbital-drift/A.json`
