@promplet version: 0.7

@module weavemark.std.reasoning.prompt_refinement_core

# Prompt Refinement Core

@note
  Reusable prompt-refinement method for transforming rough prompts into clear,
  reusable, platform-neutral instructions.

Use this method when the source prompt is a draft, a copied team prompt, a vague
request, or an organically grown instruction set.

## Refinement obligations

- Preserve the user's actual intent before improving expression.
- Identify hidden tasks, implied audiences, missing inputs, and ambiguous terms.
- Remove contradictions, duplicated requirements, and stale instructions.
- Convert vague qualities into observable success criteria.
- Separate role, task, context, constraints, process, and output contract.
- Keep platform-specific features optional unless the user requested one
  platform.
- Make the prompt safe to paste as a single prompt.
- Include placeholders only when the user still needs to supply material.

## Refined-prompt structure

When useful, produce:

1. **Prompt diagnosis** — what was missing, contradictory, or underspecified.
2. **Clarified assumptions** — assumptions made to produce a usable prompt.
3. **Refined prompt** — the paste-ready prompt.
4. **Compact variant** — a shorter prompt for quick use.
5. **Customization knobs** — small fields the user can edit without rewriting
   the prompt.

If the user asks for only the final prompt, omit diagnosis and variants.
