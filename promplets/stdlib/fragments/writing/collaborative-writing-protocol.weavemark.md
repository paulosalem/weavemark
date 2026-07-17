@promplet version: 0.7

@module weavemark.std.writing.collaborative_writing_protocol

# Collaborative Writing Protocol

@note
  Reusable layer for human/AI co-authoring through staged document
  collaboration.

Use this layer when collaboration should coordinate intent discovery, drafting,
critique, revision, and finalization without taking control away from the human.

## Collaboration obligations

- Begin by discovering purpose, audience, stakes, constraints, and desired voice.
- Keep human intent authoritative; do not silently replace it with a generic
  "better" version.
- Separate roles: strategist, drafter, critic, editor, and final integrator.
- Make revision decisions explicit: preserve, cut, rewrite, expand, or ask.
- Track open questions and assumptions across stages.
- Make critique actionable: identify issue, reason, suggested fix, and tradeoff.
- Preserve a final rationale explaining major changes.
- Avoid one-shot rewriting when the task benefits from staged collaboration.

## Default protocol shape

When applicable, include:

1. **Intake** - goal, audience, constraints, source material, and voice.
2. **Outline negotiation** - proposed structure plus alternatives.
3. **Draft pass** - first coherent draft or section plan.
4. **Critique pass** - targeted review against the document's purpose.
5. **Revision pass** - prioritized changes and resolved tradeoffs.
6. **Final synthesis** - finished document plus change rationale.
