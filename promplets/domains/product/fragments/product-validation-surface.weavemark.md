@promplet version: 0.7

@module weavemark.domains.product.product_validation_surface

# Product Validation Surface

@note
  Reusable product layer for making a product specification testable as a real
  user experience.

Use this layer when a product specification needs validation cases, not only
feature lists.

## Validation obligations

- Define the first successful user session.
- Define empty, active, error, recovery, and repeated-use states.
- Include acceptance criteria that can be checked by inspection or automation.
- Capture what evidence proves the product works.
- Include negative tests for invalid input, missing context, and stale state.
- Distinguish must-have first-build behavior from later enhancements.
- Tie validation to user value, not only technical completion.

## Required validation shape

When applicable, include:

1. **First-session script** - the path a new user should complete.
2. **State coverage** - empty, active, error, recovery, and repeated-use states.
3. **Evidence checklist** - screenshots, traces, saved data, or outputs.
4. **Failure probes** - invalid or stressful cases to test.
5. **Release gate** - criteria for a credible first public demo.
