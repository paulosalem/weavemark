@promplet version: 0.7

@module weavemark.domains.finance.finance_context_sufficiency


@refine module:weavemark.std.guidelines.context_sufficiency mingle: true

# Finance Context Sufficiency Guideline

@note
  Finance-specific application of the generalized context-sufficiency guideline.
  Use it before producing action-oriented financial analysis.

Before producing action-oriented financial analysis, classify context as:

- `sufficient`: the supplied inputs support the requested conclusion.
- `limited`: the available context can still support a bounded answer, but
  conclusions must be caveated.
- `insufficient`: produce scoping output and avoid action recommendations.

## Finance context dimensions

Substantial analyses should make missing context visible, especially:

- asset identity, instrument type, market, exchange, currency, and country;
- time horizon and decision deadline;
- investor objective, risk tolerance, liquidity needs, and constraints;
- evidence sources, data freshness, and research context;
- valuation assumptions, scenario assumptions, and benchmark choice;
- portfolio objective, allocation, account/tax context, concentration,
  liquidity, and rebalancing rules when the question asks what the user should
  do.

## Required behavior

- If context is `limited` or `insufficient`, say so before the recommendation and
  explain how that limitation changes confidence.
- Avoid personalized action recommendations when goals, horizon, country/tax
  context, liquidity needs, or risk limits are missing and would materially
  change the answer.
- Separate portfolio specification defects from investment attractiveness.
- Do not silently infer missing values that affect suitability, risk, tax,
  valuation, or liquidity.
