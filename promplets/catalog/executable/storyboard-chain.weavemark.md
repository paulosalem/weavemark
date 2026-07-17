@promplet version: 0.7

@note
  A general prompt-CHAINING demo (not tied to storybooks). @execute chain runs
  the @prompt stages in order: `beats` writes a short numbered shot list; then
  the `frame` stage is REPEATED once per shot (repeat + count), rendering each
  frame in sequence. Each frame edits the previous one (edit: on) so the visual
  style carries "one frame after the other". Demonstrates text -> iterated image
  chaining with @{previous}/@{index}.

@execute chain
  repeat: frame
  count: @{shots}

@prompt beats
  Write a numbered shot list of exactly @{shots} beats for a tiny wordless
  visual story: @{premise}. One short line per beat. Keep a consistent single
  main character and setting throughout.

@prompt frame
  @output type: image
    size: 1024x1024
    quality: high
    edit: on
  A single wordless illustration, flat modern vector style, bold clean outlines,
  warm palette, NO text. This is frame @{index} of @{count} in a sequence.

  The full shot list:
  @{beats}

  Render ONLY frame @{index} now, matching the style and the main character of
  the previous frame so the sequence stays visually consistent.
