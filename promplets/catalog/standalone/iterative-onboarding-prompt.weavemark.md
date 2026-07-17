@promplet version: 0.7

@refine module:weavemark.std.reasoning.prompt_refinement_core mingle: true

# Iterative Onboarding Prompt

This promplet builds a reusable prompt for designing a product's first-run
onboarding flow. It clarifies intent once, then judges and improves the draft
across a few passes so the delivered prompt is specific and buildable.

@iterate 3
  @ask clarifying question detail_level: 35%
    @expand mode: intention
      Draft a prompt for the first-run onboarding flow for @{product}.

      Use the clarification to fix the one thing that matters most: the single
      activation moment the first session should reach, and the question the
      flow must answer for the user before they leave.

      The final prompt must instruct an assistant to produce:
      - Goal and activation metric — the moment that counts as "onboarded".
      - Screen-by-screen flow — purpose, key content, and primary action per screen.
      - Decisions — what to ask now, what to defer, and defaults for skipped steps.
      - Acceptance criteria — observable conditions that mean each screen works.
      - Edge cases — returning users, denied permissions, empty states, errors, and drop-off recovery.
      - Verification steps — how to test the flow before shipping.

      Keep it concrete: name real screens and actions, not generic advice.
