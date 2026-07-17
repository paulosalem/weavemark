@promplet version: 0.7
@compile format: markdown

@emit file: "build-spec.md"
  @refine module:weavemark.domains.programming.types.web_based_game mingle: true
  @refine module:weavemark.domains.programming.validation.playwright_mcp_browser_validation mingle: true

  # Metro Lines first build

  @iterate 2
    @expand mode: intention focus: "playable systems with visible feedback"
      Metro Lines: the player draws transit routes, passenger
      swarms expose demand, congestion creates pressure, and
      districts evolve when the network succeeds or fails.

  Core fantasy: @{game_fantasy}
  Target device: @{target_device}
  Visual mood: @{visual_mood}

  @match session_length
    "short" ==>
      Build a quick score chase with visible demand spikes and restarts.
    "long" ==>
      Build a city-growth arc with unlocks, congestion pressure, and recovery.

  @if include_touch_controls
    Add touch drawing, tap-to-select stations, and a large undo target.

  @if include_accessibility
    Include keyboard-only line drawing, reduced motion, and shape-based demand cues.

@emit file: "playtest-checklist.md"
  # Metro Lines playtest checklist

  Validate the first build in a real browser:
  - draw a route between two districts
  - watch passenger swarms choose the route
  - create congestion and observe visible feedback
  - undo a route and confirm demand updates
  - trigger the win or score condition within one session
  - open the console and fix errors before claiming success

@emit file: "art-direction.md"
  # Metro Lines art direction

  Mood: @{visual_mood}

  Use:
  - crisp routes with high contrast
  - station glyphs that remain readable at small sizes
  - passenger swarms that show direction without overwhelming the map
  - district growth animations that can be disabled
  - a HUD that always shows score, congestion, and current tool
