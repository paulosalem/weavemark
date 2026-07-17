@promplet version: 0.7

# Self-improving image (reflection)

# Artifact-aware reflection: the image is rendered, a vision model inspects the
# RENDERED result against the critique, and the strip is re-rendered with the
# fixes — stopping early when the critique is satisfied. This is the
# execution-phase counterpart of @iterate (it improves the output, not just the
# prompt).

@execute reflection
  rounds: 3

@prompt generate
  @output type: image
    size: 1024x1024
    quality: low
  A single friendly round robot mascot, centered on a plain white background,
  flat vector style, bold clean outlines, one subject only, and NO text anywhere.

@prompt critique
  You are inspecting the attached RENDERED image. Verify every requirement:
  exactly ONE robot, centered, on a plain white background, flat vector style,
  and NO text or lettering anywhere in the image.
  Reply with exactly "OK" if all requirements hold; otherwise reply with a short
  bullet list of the concrete, fixable defects.

@prompt revise
  @output type: image
    size: 1024x1024
    quality: low
  Regenerate the image as a single friendly round robot mascot, centered on a
  plain white background, flat vector style, bold clean outlines, one subject
  only, and NO text anywhere — fixing these defects from the previous render:
  @{critique}
