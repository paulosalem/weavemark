@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst mingle: true
@refine module:weavemark.std.reasoning.unstructured_input_normalization mingle: true
@refine module:weavemark.std.reasoning.action_planning mingle: true
@refine module:weavemark.std.analysis.mece_core mingle: true
@refine module:weavemark.std.guidelines.context_sufficiency mingle: true

# Messy Notes to Action Plan Prompt

@note
  Final prompt for generating a paste-ready ChatGPT/Gemini/Claude instruction
  that turns messy notes into a faithful action plan.

Transform the source material below into a clear, faithful action plan.

## User goal

@{goal}

## Audience

@{audience}

## Source material

@{notes}

## Constraints

@{constraints}

## Required behavior

- Preserve the facts, wording, commitments, and uncertainty in the notes.
- Do not invent owners, dates, decisions, or priorities.
- Separate explicit facts from inferred structure.
- Normalize the notes before planning: identify duplicates, contradictions,
  risks, open questions, decisions, and action candidates.
- Use MECE grouping where it improves clarity, but do not pretend the notes are
  cleaner than they are.
- If the context is insufficient for a firm plan, say so near the top and create
  the best scoping plan possible.

## Required output

1. **Context status** — sufficient, limited, or insufficient.
2. **One-paragraph summary** — what is going on.
3. **Normalized notes** — facts, decisions, risks, open questions, and action
   candidates.
4. **Action plan table** — action, owner if known, priority, timing, dependency,
   and definition of done.
5. **Decisions needed** — decision, owner if known, input needed, and deadline if
   present.
6. **Risks and blockers** — risk, likely impact, mitigation, and trigger.
7. **Immediate next step** — the smallest useful action to take now.
8. **Questions to ask** — only the questions that would materially improve the
   plan.
