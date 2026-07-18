@promplet version: 0.7

@refine module:weavemark.std.reasoning.base_analyst mingle: true
@refine module:weavemark.std.reasoning.deep_summary mingle: true
@refine module:weavemark.std.guidelines.context_sufficiency mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true
@refine module:weavemark.std.lenses.explainability mingle: true

# Deep Summary Prompt

@note
  Final prompt for producing a paste-ready deep summarization instruction for a
  general chat assistant.

Summarize the source material below for **@{audience}**.

## Summary goal

@{summary_goal}

## Desired depth

@{desired_depth}

## Source material

@{source_material}

## Required behavior

- Preserve the source's meaning, priorities, uncertainty, and important details.
- Do not invent facts, motives, examples, dates, numbers, or sources.
- Distinguish what the source says from your synthesis or implication.
- Keep names, quantities, deadlines, and definitions exact when they matter.
- Surface contradictions, weak evidence, missing context, and unresolved
  questions.
- If the material is insufficient or ambiguous, say so before giving strong
  conclusions.

## Required output

1. **One-sentence summary**.
2. **Executive summary** — 3-5 bullets.
3. **Structured digest** — key claims, evidence, decisions, risks, open
   questions, and action items.
4. **Reasoning trace** — explain the most important synthesis steps and the
   evidence or source basis for each.
5. **Implications for @{audience}**.
6. **Confidence and gaps** — evidence grade, missing context, and what to verify
   before acting.
7. **Reusable takeaway** — the general lesson or pattern worth remembering.
