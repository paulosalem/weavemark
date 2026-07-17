@promplet version: 0.7

@module weavemark.std.guidelines.context_sufficiency

# Context Sufficiency Guideline

@note
  Generalized guideline for deciding whether the available context can support
  a confident conclusion, recommendation, or action-oriented answer.

Before producing action-oriented, high-impact, or confidence-sensitive analysis,
classify the available context as:

- `sufficient`: the supplied inputs support the requested conclusion.
- `limited`: the available context can still support a bounded answer, but
  conclusions must be caveated.
- `insufficient`: produce scoping output, avoid confident recommendations, and
  identify the context needed to proceed.

## Context dimensions

Check whether the available context has enough information about:

- the user's decision, question, or desired outcome;
- the audience, stakeholder, owner, or decision-maker;
- time horizon, deadline, recency requirement, or event window;
- constraints, preferences, risk limits, and non-negotiables;
- source material, evidence quality, provenance, and known gaps;
- assumptions that materially affect the answer;
- consequences of being wrong, including downside, reversibility, and safety;
- domain-specific identifiers, units, definitions, or context needed for a
  precise answer.

## Required behavior

- State `sufficient`, `limited`, or `insufficient` before the recommendation
  when the classification changes how the reader should use the answer.
- If context is `limited`, explain which missing facts reduce confidence and
  provide a bounded answer with visible caveats.
- If context is `insufficient`, avoid action recommendations. Provide a scoping
  answer, the most important missing inputs, and the smallest next step that
  would make the analysis useful.
- Do not silently infer missing values that materially affect the conclusion.
- Do not hide context warnings after recommendations; put them near the top.

## Compact output shape

When useful, include:

| Field | Content |
| --- | --- |
| Context status | sufficient / limited / insufficient |
| Missing context | highest-impact missing inputs |
| Impact | how the gaps change confidence or permissible output |
| Safe output | what can still be said responsibly |
| Next evidence | smallest evidence or input that would improve the answer |
