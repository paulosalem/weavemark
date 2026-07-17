@promplet version: 0.7


@refine module:weavemark.std.guidelines.context_sufficiency mingle: true
@refine module:weavemark.std.guidelines.prompt_quality mingle: true
@refine module:weavemark.std.reasoning.prompt_refinement_core mingle: true

# Prompt Refiner Prompt

@note
  Final prompt for generating a better paste-ready prompt from a rough prompt.

Refine the prompt below so it is clearer, more useful, and easier to paste into
ChatGPT, Gemini, Claude, or another chat assistant.

## Target use

@{target_use}

## Target platform

@{target_platform}

## Rough prompt

@{raw_prompt}

## Must preserve

@{must_preserve}

## Desired output from the eventual assistant

@{desired_assistant_output}

## Required behavior

- Preserve the user's actual intent.
- Identify hidden tasks, implied audience, missing context, ambiguous terms, and
  contradictions.
- Strengthen the task, context, constraints, reasoning behavior, output
  contract, and success criteria.
- Make the prompt platform-neutral unless the target platform requires a special
  feature.
- Include placeholders only where the user still needs to paste material.
- Do not make the prompt longer than necessary.

## Required output

1. **Diagnosis** — the 3-7 most important weaknesses in the rough prompt.
2. **Clarified assumptions** — assumptions you made to produce a usable prompt.
3. **Refined prompt** — paste-ready, complete, and internally consistent.
4. **Compact variant** — a shorter prompt for quick use.
5. **Customization knobs** — fields the user can edit without rewriting the
   prompt.
