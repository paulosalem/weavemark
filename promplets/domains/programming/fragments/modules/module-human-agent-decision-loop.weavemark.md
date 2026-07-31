@promplet version: 0.7

@module weavemark.domains.programming.modules.human_agent_decision_loop

# Module: Human-Agent Decision Loop

Use this module when a human and agent should refine a consequential choice over
multiple feedback rounds before the human authorizes deeper execution.

## Decision thread

- Keep one durable decision thread attached to its parent work item. Model
  `briefing`, `exploring`, `needs_feedback`, `committed`, `deep_work`, `review`,
  and `accepted` phases separately from the board column projection.
- The initial human brief captures goals, starting suggestions, constraints,
  preferences, exclusions, budget or effort bounds, decision criteria, and known
  unknowns. The human can revise it until explicitly marking it Ready for agent.
- Preserve every proposal, feedback round, question, answer, selection, gate
  decision, and resulting artifact with actor, timestamp, execution turn, and
  provenance. Never flatten the conversation into only its latest message.

## Explore and refine

- The exploratory execution turn researches broadly enough to test the human's
  starting suggestions and discover credible alternatives without prematurely
  producing a deep implementation plan.
- Present a bounded option set through a structured comparison surface. Each
  option SHOULD show fit to criteria, evidence, tradeoffs, uncertainty, practical
  constraints, and why it differs from the others.
- Ask focused questions when missing information could change the ranking. Yield
  control with `needs_feedback`; do not guess through a consequential preference.
- Let the human rank, shortlist, reject, restore, annotate, or add options and
  revise constraints. Feedback is structured and append-only, with optional prose.
- Before the next research pass, the agent summarizes what it understood, cites
  the feedback round, updates only affected comparisons, and explains material
  ranking changes. Continue within the exploratory turn until the human commits or
  cancels.

## Human commitment gate

- Deep work requires an explicit human gate with one selected option, the current
  constraints, and a clear action label such as Research selected option deeply.
  An agent MUST NOT infer commitment from positive feedback or cross the gate.
- A product may bind the gate to a confirmed board transition. Moving an
  exploratory item from Planning to In Progress, for example, can atomically
  complete the exploration turn and queue a new deep-work turn.
- The deep-work turn snapshots the selected option, accepted constraints,
  unresolved questions, supporting evidence, and all relevant feedback. It does
  not silently reconsider rejected options unless new evidence invalidates the
  decision.
- Changing the selected option after commitment requires explicit cancellation or
  replacement of the deep-work turn and another recorded gate decision.

## Deep work and review

- Deep work produces decision-specific artifacts such as an itinerary, execution
  plan, implementation design, purchase shortlist, budget, risk register, or
  verification checklist.
- Return the item to Review with a prominent latest proposal, assumptions,
  alternatives where useful, evidence dates, unresolved risks, and focused
  approval or revision actions.
- Human revision requests resume the deep-work turn when they refine the selected
  option. Run again creates a later turn only for a genuinely new decision cycle.
- Acceptance records the chosen result without deleting exploration, feedback,
  superseded proposals, or prior execution turns.

## Interaction and tests

- Make phase, current control owner, requested human action, selected option, and
  next gated transition visible on the card and in detail.
- Test editable briefing, readiness, broad comparison, repeated feedback, agent
  questions, ranking changes, gate refusal without selection, confirmed
  transition, deep-turn snapshot, changed selection after commitment, review
  revisions, acceptance, cancellation, and complete historical reconstruction.
