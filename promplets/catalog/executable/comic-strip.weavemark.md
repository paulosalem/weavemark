@promplet version: 0.7

@note
  Comic-strip pipeline expressed FULLY in WeaveMark — authoring, reference-
  conditioned rendering, AND self-inspecting correction — with no external script.

  It runs as `@execute reflection`, which is a production chain followed by a
  critique -> revise loop. `critique` and `revise` are the reserved loop roles;
  every other @prompt stage is a production step run in source order.

  Stage `author` refines the shared illustrated-story core (comic-strip format and
  references pinned via a @refine binding). It SEES the five reference images
  (style-reference comic + four character sheets) as multimodal inputs and writes
  ONE detailed, on-model image-generation prompt for the strip.

  Stage `generate` is the artifact producer: it renders the strip from @{author}
  as ONE image, conditioning the image model DIRECTLY on the same references via
  `edit: on`, and persists it with `@output file:`.

  The `critique` role then vision-inspects the RENDERED strip against @{author}
  (panel count, duplicate/off-model characters, garbled lettering) and `revise`
  edits the image to fix any defects — repeating until it passes or rounds run out.

  Companion vars set title, premise, panel_count, layout, tone, art_style,
  setting, characters, and the five reference image paths. This spec also owns the
  comic-specific `panels` beat sheet: `panels` is a JSON object keyed by panel
  number ("1".."@{panel_count}"), each with a `.staging` line (what happens /
  who is on-screen) and a `.dialogue` line (the exact hand-lettered words). The
  author stage reads them via dotted paths (@{panels.1.staging}, …) so each panel
  is authored deliberately rather than improvised.

@execute reflection
  rounds: 3

@prompt author
  @refine module:weavemark.domains.creative.illustrated_story_core
    with story_format: "comic-strip"
    with references: true

  ## Panel beat sheet — exactly what happens in each panel

  Realize these EXACT beats, in this order, one per panel. The staging and
  dialogue of each panel are fixed: flesh out expression, framing, and comedic
  timing around them, but do not add, drop, reorder, or merge beats, and keep
  every line of dialogue verbatim as short hand-lettered speech balloons. Let the
  final panel land the punchline cleanly.

  - **Panel 1** — @{panels.1.staging}
    Dialogue — @{panels.1.dialogue}
  - **Panel 2** — @{panels.2.staging}
    Dialogue — @{panels.2.dialogue}
  - **Panel 3** — @{panels.3.staging}
    Dialogue — @{panels.3.dialogue}
  - **Panel 4** — @{panels.4.staging}
    Dialogue — @{panels.4.dialogue}
  - **Panel 5** — @{panels.5.staging}
    Dialogue — @{panels.5.dialogue}

@prompt generate
  @output type: image
    file: comic-strip.png
    size: 1536x1024
    quality: high
    edit: on
  @{author}

  Keep every recurring character strictly on-model from the attached character
  sheets, and match the style reference's palette, line work, shading, lettering,
  and framing.

  @if character_sheet_1
    ![Character sheet 1 — keep characters on-model](@{character_sheet_1})
  @if character_sheet_2
    ![Character sheet 2 — keep characters on-model](@{character_sheet_2})
  @if character_sheet_3
    ![Character sheet 3 — keep characters on-model](@{character_sheet_3})
  @if character_sheet_4
    ![Character sheet 4 — keep characters on-model](@{character_sheet_4})
  @if style_reference
    ![Style reference — match line art, coloring, lettering, panel framing](@{style_reference})

@prompt critique
  You are a strict comic-strip art director inspecting the attached RENDERED
  comic strip against its specification.

  Specification the image must satisfy:
  -----
  @{author}
  -----

  Check the image panel by panel for these defects:
  - Duplicate or extra copies of a character that should appear once in a panel.
  - Wrong number of panels versus the specification.
  - Characters drawn off-model (face, hair, outfit, or colors inconsistent).
  - Garbled, misspelled, or unreadable lettering.
  - Characters that should not be present, or missing required characters.

  Reply with exactly "OK" if the image faithfully satisfies the specification
  with none of these defects. Otherwise reply with a short bullet list of the
  concrete, fixable defects, citing the panel. List only defects.

@prompt revise
  @output type: image
    size: 1536x1024
    quality: high
    edit: on
  @{author}

  Keep every recurring character on-model from the attached character sheets, and
  preserve the style reference's palette, line work, shading, and lettering.

  @if character_sheet_1
    ![Character sheet 1 — keep characters on-model](@{character_sheet_1})
  @if character_sheet_2
    ![Character sheet 2 — keep characters on-model](@{character_sheet_2})
  @if character_sheet_3
    ![Character sheet 3 — keep characters on-model](@{character_sheet_3})
  @if character_sheet_4
    ![Character sheet 4 — keep characters on-model](@{character_sheet_4})

  The previous render had these defects — fix ALL of them exactly, and do NOT
  introduce any new issues:
  {{critique}}
