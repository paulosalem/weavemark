@promplet version: 0.7

@module weavemark.domains.product.metaphor_to_product

# Metaphor to Product

@note
  Reusable product-design layer for turning a compact metaphor into a coherent
  product specification.

Use this layer when the source idea is intentionally abstract, such as
"observatory", "workshop", "radar", "garden", "studio", or "control tower".

## Metaphor-expansion obligations

- Extract the useful conceptual structure from the metaphor, not decorative
  labels.
- Map metaphor elements to product responsibilities, data entities, workflows,
  user actions, and failure modes.
- Discard metaphor parts that would confuse the product.
- Preserve a clear non-metaphorical product explanation.
- Use the metaphor to generate coherent UI vocabulary only when it improves
  understanding.
- Identify what the metaphor makes easy to explain and what it hides.
- Convert abstract nouns into concrete interactions and state.

## Required product-mapping shape

When applicable, include:

1. **Metaphor map** - metaphor element to product responsibility.
2. **Core user job** - plain-language non-metaphorical statement.
3. **Entities and workflows** - concrete records, states, and actions.
4. **Interface model** - screens, panels, controls, and feedback.
5. **Failure modes** - where the metaphor could mislead implementation.
6. **Acceptance criteria** - behavior that proves the product exists.
