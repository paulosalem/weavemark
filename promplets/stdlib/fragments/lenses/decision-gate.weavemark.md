@promplet version: 0.7

@module weavemark.std.lenses.decision_gate

# Decision Gate Lens

@note
  Reusable lens for viewing an analysis as a clear pass, fail, wait, or
  investigate decision against explicit criteria.

Use this lens for decisions, recommendations, plans, proposals, or strategic
questions that should be reduced to explicit gate logic.

## Required output

Define the gate criteria and thresholds before classifying the decision.

Start with these labeled lines, without adding any standalone format label:

- `Gate: go | no-go | wait | investigate`
- `Reason: one-sentence rationale`
- `Confidence: low | medium | high`

Then provide a compact table:

| Criterion | Threshold | Current read | Gate status | Confidence |
| --- | --- | --- | --- | --- |
| criterion | pass/fail condition | current evidence | pass/fail/unknown | low/medium/high |

End with:

- **Blockers:** what prevents a stronger decision.
- **Next evidence:** the minimum evidence needed to move the gate.
- **Change trigger:** what would flip the recommendation.
