@promplet version: 0.7

@module weavemark.std.reasoning.unstructured_input_normalization

# Unstructured Input Normalization

@note
  Reusable reasoning layer for turning pasted notes, transcripts, brainstorms,
  fragments, and mixed-quality source material into a faithful working set.

Use this layer before analysis, summarization, action planning, or decision
support when the input is messy, partial, duplicated, chronological, emotional,
or internally inconsistent.

## Normalization obligations

- Preserve source fidelity. Do not invent facts, commitments, dates, owners, or
  causal links that are not present.
- Separate explicit statements from reasonable inferences.
- Identify duplicates, contradictions, ambiguities, missing context, and stale
  items before building on the material.
- Extract named entities, owners, dates, decisions, tasks, risks, blockers,
  questions, evidence, and assumptions when present.
- Keep raw wording when it carries nuance, emotion, or stakeholder intent.
- Convert fragments into clear units without making them falsely certain.
- Mark low-confidence interpretations visibly.

## Default normalized working set

When the output needs to show the normalization step, include:

| Section | Purpose |
| --- | --- |
| Source facts | What the input explicitly says. |
| Inferred structure | Relationships or categories inferred from the input. |
| Decisions | Choices already made or still needed. |
| Action candidates | Potential tasks, follow-ups, or commitments. |
| Risks and blockers | Things that could prevent progress. |
| Open questions | Missing inputs or ambiguities that matter. |
| Confidence notes | Places where interpretation is uncertain. |

Normalization is a preparation step, not a license to over-organize. If the
input is genuinely chaotic, preserve enough uncertainty that later analysis does
not rest on a fake clean story.
