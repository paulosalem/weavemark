@promplet version: 0.7

@module weavemark.prelude.presentation

@define concise(body: content to present concisely)
  Presentation constraints:
  - Be concise, direct, and high-signal.
  - Remove filler and avoid unnecessary preamble.

  @{body}

@define style
  @phase compile
  @scope body
  @returns replacement

  @param description default: ""
    Presentation constraints: tone, voice, register, formatting, audience, or
    other style guidance.

  @param body implicit: true mode: subspec
    Required non-empty WeaveMark content governed by the style guidance.

  @effect transform_text write
  @effect diagnostics write

  @body
    Rewrite or constrain the selected presentation text using this style
    guidance: @{description}. Integrate the guidance directly into the resulting
    prompt text. @{body} is the explicit target. Return only the styled prompt
    content; do not emit this policy or operation labels.
