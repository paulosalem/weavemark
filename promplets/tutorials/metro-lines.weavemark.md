@promplet version: 0.7
@refine module:weavemark.domains.programming.types.web_based_game mingle: true
@refine module:weavemark.domains.programming.validation.playwright_mcp_browser_validation mingle: true

# Metro Lines

@iterate 2
  @expand mode: intention focus: "one integrated playable loop"
    Metro Lines: a browser game where the player draws transit
    routes, passenger swarms reveal demand, congestion creates
    pressure, and districts grow when the network succeeds.

Core fantasy: @{game_fantasy}
Target device: @{target_device}
Visual mood: @{visual_mood}

@match session_length
  "short" ==>
    Design a 5-minute score chase with quick restarts.
  "long" ==>
    Design a 25-minute city-growth arc with escalating pressure.

@if include_touch_controls
  Specify touch-friendly drawing, undo, and station selection.

@if include_accessibility
  Add keyboard-only play, reduced-motion mode, and non-color-only demand cues.

@output enforce: strict
  Return game loop, entities, controls, progression,
  scoring, accessibility, failure states, browser validation steps,
  and first-build scope.

@assert contains: "first-build scope"
@assert contains: "browser validation"
