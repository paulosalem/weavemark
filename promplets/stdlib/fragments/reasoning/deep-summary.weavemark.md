@promplet version: 0.7

@module weavemark.std.reasoning.deep_summary

# Deep Summary

@note
  Reusable summarization layer for producing faithful, layered summaries that
  preserve meaning, uncertainty, decisions, and actionability.

Use this layer when the user needs more than a short recap: they need the
important claims, evidence, implications, risks, and next steps separated cleanly.

## Summary obligations

- Preserve the source's actual meaning, priority, and uncertainty.
- Do not invent facts, sources, motives, or conclusions absent from the source.
- Distinguish the author's claims from your synthesis.
- Surface disagreements, caveats, weak evidence, and missing context.
- Preserve numbers, dates, names, definitions, and constraints exactly when they
  matter.
- Make the summary useful at multiple depths: fast orientation first, detail
  after.
- If the source is too thin or ambiguous, say so before summarizing strongly.

## Layered summary shape

When useful, include:

1. **One-sentence summary** — the core point in plain language.
2. **Executive summary** — the 3-5 most important takeaways.
3. **Structured digest** — claims, evidence, decisions, risks, open questions,
   and action items.
4. **Implications** — what changes for the audience or decision-maker.
5. **Confidence and gaps** — what is solid, what is uncertain, and what should be
   checked before acting.
6. **Reusable takeaway** — the principle, pattern, or lesson that generalizes.
