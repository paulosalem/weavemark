@promplet version: 0.7

@module weavemark.std.lenses.comparative_alternatives

# Comparative Alternatives Lens

@note
  Reusable lens for viewing a decision as a direct comparison among options,
  emphasizing differentiators, tradeoffs, and decisive criteria.

Use this lens for choices among products, strategies, investments,
architectures, actions, or recommendations.

## Required output

Start with:

- `Leading option: option`
- `Runner-up: option`
- `Decisive criterion: criterion`
- `Confidence: low | medium | high`

Then provide a compact comparison:

| Criterion | Option A | Option B | Option C | Winner | Why it matters |
| --- | --- | --- | --- | --- | --- |
| criterion | assessment | assessment | assessment | option | decision relevance |

End with:

- **Best if:** when each option is the right choice.
- **Avoid if:** when each option is the wrong choice.
- **Ranking trigger:** what evidence or constraint would change the order.
