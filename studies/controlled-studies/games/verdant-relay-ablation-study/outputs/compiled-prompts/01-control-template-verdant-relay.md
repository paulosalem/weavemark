# Verdant Relay: Matched Reusable Template Control

## Implementation specification contract

- This is the coherent implementation-ready specification for Verdant Relay.
- Treat this specification as the source of truth for a programming agent or human engineer.
- Include first-build scope, out-of-scope items, architecture, domain model,
  durable records, workflows, UI surfaces, automation rules, validation plan,
  failure handling, privacy/provenance rules, and acceptance criteria.
- Distinguish required first-build behavior from optional later enhancements.
- Avoid separate support prompts, prompt packs, or artifact manifests.
- Every major requirement should have an observable user-facing or validation
  consequence.
- Use concrete field names, states, events, screens, checks, and recovery paths
  instead of generic quality advice.


## Case-specific game concept

Design Verdant Relay, a browser game where the player protects a living railway garden from spreading blight. The player manages railway route pressure, habitat cells, blight trains, pests, spores, invasive vines, card-driven interventions, living defenses, ecosystem health, recovery, readability, and first-build balance.

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


## Tower-defense mechanic template

- Define a protected objective, route graph, waves, threats, defenses, resources,
  placement rules, targeting rules, leaks, rewards, upgrades, and route pressure.
- Paths should have forks, chokepoints, previews, threat timing, and blocked
  placement explanations.
- Threats need speed, durability, behavior, spawn timing, reward, damage, visual
  feedback, and failure consequence.
- Defenses need cost, range, targeting rule, reload cadence, effect type,
  upgrade path, placement constraint, preview, and feedback.
- Waves should teach one mechanic at a time before combining pressure, timing,
  counters, and recovery.
- The UI should show range previews, route previews, current wave, next wave,
  leak state, resources, selected defense, invalid placement reason, and result.


## Deckbuilding mechanic template

- Define deck, draw pile, hand, discard pile, exhausted cards, reshuffle, energy
  or action budget, card cost, timing, target, effect, rarity, tags, and upgrade
  state.
- Cards should support placement, intervention, recovery, resource conversion,
  tactical events, upgrades, route manipulation, and emergency actions.
- The first card set should include clear archetypes, synergies, counters,
  invalid-play cases, and readable effect previews.
- The UI should show card cost, target, effect preview, invalid-play reason,
  draw/discard counts, reshuffle state, and what will happen before confirmation.
- Card effects must update the game state deterministically and be testable.


## Ecosystem-simulation mechanic template

- Model living tiles, resources, hazards, growth, decay, spread, resilience,
  recovery, and stress.
- Feedback loops should be simple and readable: beneficial states improve
  defenses or resources, harmful states spread or reduce effectiveness, and
  recovery actions visibly change future outcomes.
- Use deterministic or seeded ticks so players can reason about cause and effect.
- Provide overlays and tooltips for health, stress, abundance, shortage, spread,
  resilience, and looming failure.
- Ecosystem state should change tactical value, not remain decorative.
- Validation should test resource flow, spread, recovery, failure thresholds, and
  player-readable feedback.


## Playability, readability, progression, and balance

- The first minute should teach objective, controls, primary feedback, and one
  successful action before introducing combined pressure.
- Every failure should be explainable through visible cause, feedback, and a
  concrete recovery or retry path.
- Define a first-build progression ladder, initial content set, unlock or wave
  sequence, tuning knobs, safe ranges, dominant-strategy checks, and playtest
  questions.
- Accessibility basics include readable contrast, keyboard operation, no
  color-only critical signals, reduced motion where effects are intense, and
  text that matches implemented controls.
- Acceptance should require a complete vertical slice with stable performance,
  readable UI, explainable success/failure, and no unresolved placeholder
  mechanics.


## Original asset and sprite pipeline

- Use only original, non-infringing assets. Do not request, imitate, or include
  copyrighted characters, logos, sprites, or distinctive owned styles.
- First builds may use placeholder shapes, but the specification should define
  sprite roles, sizes, collision footprints, state names, animation metadata,
  palette, frame count, FPS, loop flag, transparent background, sheet packing,
  filenames, and loading rules.
- Store asset provenance, generation prompt if used, source file, derived file,
  metadata, and quality checks.
- Validate readability at game scale, consistent palette, transparent
  backgrounds, hitbox fit, no unwanted text, no artifacts, and no infringement.


## Browser validation and evidence

- Validate the actual browser experience, not only static source inspection.
- Record command used to run the app, URL tested, browser flows exercised,
  screenshots or traces when available, console errors found and resolved, and
  remaining limitations.
- Browser validation should cover first load, primary user flow, invalid inputs,
  persistence across restart or reload, responsive layout, keyboard/focus
  behavior, recovery states, and absence of runtime console errors.
- Prefer Playwright MCP or an equivalent real-browser tool when available. If the
  browser tool cannot run, report the exact blocker and do not claim browser
  validation happened.
- Acceptance requires a first-session path that proves the product is usable,
  understandable, recoverable, and backed by saved evidence.


## Required output

This coherent implementation specification includes game objective,
first-session script, core loop, mechanics, entities, content tables, state
model, deterministic simulation rules, card set, tower/defense set, wave
definitions, ecosystem feedback loops, UI layout, controls, asset pipeline,
browser implementation plan, browser validation strategy, progression ladder,
balance matrix, playtest questions, risks, failure explanations, release gate,
and acceptance criteria.
