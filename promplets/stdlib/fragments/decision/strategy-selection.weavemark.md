@promplet version: 0.7

@module weavemark.std.decision.strategy_selection

# Decision Strategy Selection

@note
  Reusable decision layer for adapting the reasoning method to the shape of a
  decision.

Use this layer when a decision needs a strategy fitted to its shape instead of
one generic decision template.

## Strategy-selection obligations

- Classify the decision shape before recommending a method.
- Distinguish reversible, irreversible, adversarial, forecast-heavy, portfolio,
  values-heavy, and option-preserving decisions.
- Choose the analysis method because it changes the recommendation, not because
  it sounds sophisticated.
- Identify what evidence would flip the decision.
- Preserve optionality when information value is high and delay is cheap.
- Recommend commitment when delay is costly and uncertainty cannot be resolved.
- Make the next action proportional to the decision's stakes and reversibility.

## Required strategy surface

When applicable, include:

1. **Decision shape** - classification with reasons.
2. **Chosen method** - why this method fits better than alternatives.
3. **Decisive uncertainties** - the unknowns most likely to change action.
4. **Option set** - choices, hybrids, deferrals, probes, and no-action baseline.
5. **Reversal or escalation triggers** - what would change the plan.
6. **Recommended next move** - action, evidence to gather, and review point.
