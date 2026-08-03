@promplet version: 0.7

# Contributor onboarding

@iterate 2
  @polish "Make the onboarding sequence concrete, concise, and safe for a first contribution."
    Write a contributor onboarding guide that covers:
    - local setup
    - one focused first change
    - the smallest relevant validation command
    - how to report a blocked or failed check

@output enforce: strict
  Return exactly these sections:
  1. Setup
  2. First change
  3. Validation
  4. Blockers
