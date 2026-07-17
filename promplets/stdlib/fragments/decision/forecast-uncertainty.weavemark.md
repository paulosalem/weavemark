@promplet version: 0.7

@module weavemark.std.decision.forecast_uncertainty

# Forecast and Uncertainty Reasoning

@note
  Reusable decision layer for forecasts, uncertainty ranges, and
  scenario-sensitive recommendations.

Use this layer when future conditions materially affect the decision.

## Forecast obligations

- Separate known facts, assumptions, forecasts, and preferences.
- Use ranges or scenarios instead of false precision.
- Identify leading indicators and signposts.
- Include base-rate reasoning when relevant.
- Track correlation and dependency between uncertainties.
- Compare robust choices against best-case optimized choices.
- State what can be learned cheaply before committing.

## Required forecast shape

When applicable, include:

1. **Forecast variables** - what must be estimated.
2. **Base case / upside / downside** - with triggers.
3. **Indicators to watch** - what evidence updates the forecast.
4. **Robust action** - what works across scenarios.
5. **Contingent action** - what changes if a signpost fires.
6. **Review cadence** - when to revisit the decision.
