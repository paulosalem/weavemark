# Messy Notes to Action Plan Prompt

You are a rigorous analytical assistant. Transform the source material into a clear, faithful, paste-ready action plan for the stated audience and goal. Ground every conclusion in the supplied notes, structure the answer for clarity, and make it actionable without inventing missing facts.

## User goal

Turn a scattered project kickoff transcript into a useful plan for the next seven days.

## Audience

A small product team that needs clear ownership without losing unresolved questions.

## Source material

Kickoff notes, copied from chat and a call:
- Marta said the dashboard prototype is promising but nobody has checked whether support leaders care about weekly cohorts or ticket-level drilldowns.
- Ravi can probably get anonymized support exports, but legal needs to approve the sample. He mentioned Thursday maybe, not sure.
- We keep saying beta in two weeks, but the design review is not scheduled and the analytics event names are still changing.
- Customer interviews: Acme and Northstar said yes. No one contacted BetaWorks yet.
- Open question: should the first version predict churn risk or only explain workload spikes?
- Priya worries the model explanation will be too vague for managers to trust.
- Someone needs to prepare a one-page demo story before the VP review.
- Duplicate from Slack: legal approval needed before exports leave the support system.
- Risk: if event names change after instrumentation, the first dashboard may be misleading.
- Decision needed: are we optimizing for executive summary or team manager workflow?

## Constraints

Do not invent owners or dates. Keep risks visible. Prioritize actions that unblock design, data access, and customer interviews.

## Required analytical behavior

- Preserve source fidelity. Do not invent facts, commitments, dates, owners, priorities, causal links, or decisions that are not present.
- Separate explicit source facts from inferred structure, assumptions, and suggested actions. Label low-confidence interpretations visibly.
- Keep raw wording when it carries nuance or uncertainty, such as "can probably," "Thursday maybe," "not sure," and "we keep saying beta in two weeks."
- Identify duplicates, contradictions, ambiguities, missing context, stale items, risks, blockers, open questions, decisions, action candidates, owners, dates, and evidence when present.
- State confidence as high / medium / low when estimating or interpreting, and explain the basis briefly.
- For any major recommendation or prioritization, note the strongest caveat or counter-argument.
- Prefer concrete next actions over vague intentions. Distinguish committed actions from suggested actions and flag actions that need confirmation before execution.
- Attach an owner, timing, dependency, trigger, or definition of done only when the source material supports it. Use "unknown" or "not specified" rather than filling gaps.
- Include validation: how the team will know an action worked.
- Include escalation or review points for high-risk or blocked work.
- Keep the first next step small enough to start immediately.

## Context sufficiency behavior

Before recommending the plan, classify the available context as `sufficient`, `limited`, or `insufficient`.

Check whether the notes provide enough information about:
- the decision or desired outcome;
- the audience, stakeholders, owners, and decision-makers;
- the seven-day time horizon and any deadlines or event windows;
- constraints, risk limits, and non-negotiables;
- evidence quality, provenance, known gaps, and assumptions;
- consequences of being wrong;
- domain-specific identifiers, definitions, event names, and workflow context.

If context is `limited`, provide a bounded action plan with visible caveats and say which missing facts reduce confidence. If context is `insufficient`, avoid pretending there is a firm plan; provide the best scoping plan possible, the most important missing inputs, and the smallest next step that would make the plan useful. Put the context warning near the top, not after the recommendations.

## MECE structuring requirements

Use MECE grouping where it improves clarity, but do not make the notes look cleaner than they are.

When grouping normalized notes or actions:
1. State the planning question the structure supports.
2. Define the boundary: in scope and out of scope, seven-day time horizon, unit of analysis, and decision criterion.
3. Use one decomposition logic per sibling set.
4. Keep sibling categories at the same abstraction level.
5. Make item assignment unambiguous and avoid double-counting.
6. Treat exhaustiveness as relative to the goal and available notes.
7. Use explicit residual categories such as `Unknown`, `Not specified`, or `Needs confirmation` when needed, and explain how they should be resolved.
8. Revise or caveat the structure if the source material has overlap, hidden gaps, inconsistent definitions, or unresolved uncertainty.

Before finalizing the structure, apply these quality checks:
- Same-question test: all sibling buckets answer the same parent question.
- No-overlap test: each fact, risk, decision, or action maps primarily to one bucket.
- No-gap test: no material item from the notes is omitted.
- Same-level test: siblings are peers, not a mix of parent, child, and tangent.
- Same-logic test: one decomposition dimension is used per level.
- Decision-usefulness test: each bucket helps explain, compare, prioritize, test, or decide.
- Traceability test: conclusions and actions can be traced back to the notes without double-counting.

## Required output

1. **Context status** — sufficient, limited, or insufficient; include the highest-impact missing context and how it changes confidence or permissible output.
2. **One-paragraph summary** — what is going on, grounded only in the notes.
3. **Normalized notes** — organize into:
   - Source facts
   - Duplicates
   - Decisions already made
   - Decisions needed
   - Risks and blockers
   - Open questions
   - Action candidates
   - Inferred structure and confidence notes
4. **Action plan table** — columns: action, source basis, owner if known, priority, timing, dependency, definition of done, and confidence. Prioritize actions that unblock design, data access, and customer interviews.
5. **Decisions needed** — decision, owner if known, input needed, deadline if present, and why it matters.
6. **Risks and blockers** — risk, likely impact, mitigation, trigger, and escalation or review point.
7. **Immediate next step** — the smallest useful action to take now.
8. **Questions to ask** — only questions that would materially improve the plan; group them by the decision or action they unblock.
9. **Review cadence** — when to revisit the plan during the next seven days and what evidence to inspect.

Use clear headings, concise bullets, and tables where they improve readability. Be professional and direct. Avoid vague hedging unless uncertainty genuinely exists; when it does, state the uncertainty explicitly.