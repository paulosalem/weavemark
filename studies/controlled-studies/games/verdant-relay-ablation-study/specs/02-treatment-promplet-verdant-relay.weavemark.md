# @{game_title}: WeaveMark Browser-Game Treatment

@compress "Produce a dense browser-game implementation spec; preserve structure and every hard requirement."
  @refine programming/foundations/software-spec
    Mingle mechanics, architecture, assets, validation, tuning, and readability
    into one browser-game implementation spec; never append generic fragments.

  @refine programming/types/web-based-game

  Design @{game_title}: a playable living-railway browser game where route
  defense, deckbuilder choices, ecosystem feedback, original assets, and real
  browser validation shape the same first build.

  Key source concepts to expand:

  @expand mode: intention
    Tower-defense lane protection: blight lanes, leaks, towers, waves, rewards,
    and upgrades.

  @expand mode: intention
    Deckbuilder card choice and economy: draw, hand, costs, card effects,
    synergies, and seeded small-deck progression.

  @expand mode: intention
    Ecosystem simulation and feedback loops: health, diversity, resilience,
    recovery, collapse, and visible biome state.

  Integration: Use the expanded tower-defense, deckbuilder, and ecosystem notions
  as reusable building blocks for one loop where tactics, economy, and long-term
  health all matter.

  ## Integrated mechanics

  @refine game-design/mechanics/tower-defense
    Railway blight lanes, leaks, rewards, upgrades, cards, and ecosystem state.

  @refine game-design/mechanics/deckbuilder
    Cards change wave outcomes through plant, habitat, intervention, route,
    resource, upgrade, and recovery choices.

  @refine game-design/mechanics/ecosystem-simulation
    Ecosystem state changes defense decisions, card value, recovery, and failure.

  Use focused 2D component and system boundaries for tiles, lanes, cards,
  ecosystem state, waves, overlays, animation, and restart.

  ## Player readability, progression, and tuning

  @refine game-design/production/playability-readability
  @refine game-design/production/progression-balance-model

  Use deterministic waves, seeded draws/events, and a small complete content set.

  ## Browser implementation, assets, and validation

  @refine programming/validation/playwright-mcp-browser-validation
    Prove load, start, card draw/play, placement/upgrade, wave, ecosystem
    feedback, leak/win, pause/resume, and restart in a real browser.

  Define an original visual direction and asset manifest covering dimensions,
  variants, gameplay states, animation, ownership, loading, and validation.
  Do not depend on unlicensed art.
  @refine product/product-validation-surface

  ## Required output

  Produce one information-rich implementation spec covering objective, loop,
  entities, state, simulation, content, UI, controls, assets, browser
  implementation, Playwright validation, progression, balance, playtests, risks,
  failures, release gate, and acceptance. Include concrete lists/tables for
  content, fields, tuning, validation, assets, and acceptance. Use field lists or
  tables instead of fenced examples for JSON-shaped game data.
