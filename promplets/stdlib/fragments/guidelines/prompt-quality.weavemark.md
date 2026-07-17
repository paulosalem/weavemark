@promplet version: 0.7

@module weavemark.std.guidelines.prompt_quality

# Prompt Quality Guideline

@note
  Reusable guideline for assessing and improving prompts meant for general LLMs
  such as ChatGPT, Gemini, Claude, or local assistants.

Use this guideline when writing, reviewing, or refactoring a prompt.

## Prompt-quality obligations

A strong prompt should make these elements explicit when they matter:

- task and desired outcome;
- audience, user role, or decision-maker;
- source material and what to do with it;
- constraints, preferences, exclusions, and non-negotiables;
- output structure, format, length, and ordering;
- required reasoning behavior, checks, or comparison criteria;
- uncertainty, missing-context, and evidence-handling rules;
- examples or counterexamples when they reduce ambiguity;
- success criteria for judging the answer.

## Common prompt failures

- Asking for a result without defining what good means.
- Mixing several tasks without priority or sequencing.
- Hiding important constraints in prose instead of making them inspectable.
- Requesting confidence while omitting evidence or context.
- Over-specifying style while under-specifying substance.
- Asking for sources, facts, or recent events without saying how to handle lack
  of search access.
- Leaving the model to guess audience, depth, and output contract.

## Improvement target

The improved prompt should be:

- specific enough to reduce rework;
- flexible enough to work across major chat assistants;
- explicit about what to do when context is missing;
- easy to paste, inspect, and modify;
- free of contradictory or duplicate instructions.
