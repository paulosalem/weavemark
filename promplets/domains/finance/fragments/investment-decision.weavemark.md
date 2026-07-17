@promplet version: 0.7

@module weavemark.domains.finance.investment_decision

# Investment Decision Lens

@note
  Reusable lens for viewing an investment decision through risk-free
  benchmark-relative probabilities, scenario-conditional delta magnitudes, and
  uncertainty.

Use this lens when an investment decision `D` should be seen as a
probability-weighted comparison against a matched risk-free asset.

## Frame

State the benchmark assumptions: risk-free asset, horizon, currency, principal
or unit size, liquidity, taxes/fees if relevant, and the materiality band for
"matched" performance. The matched scenario has `Delta = 0` by definition.

## Required output

| Quantity | Estimate | Confidence | Notes |
| --- | --- | --- | --- |
| `P(D outperforms the risk-free asset)` | probability | low/medium/high | main drivers |
| `P(D matches the risk-free asset)` | probability | low/medium/high | materiality band used |
| `P(D underperforms the risk-free asset)` | probability | low/medium/high | downside drivers |
| `E[Delta | outperform]` | positive absolute value | interval/distribution | likely outperform magnitude |
| `Delta | matched` | `0` | classification band | matched by definition |
| `E[Delta | underperform]` | negative absolute value | interval/distribution | likely underperform magnitude |

The three probabilities must be mutually exclusive, collectively exhaustive,
and sum to 100% except for rounding.

## Delta

Report scenario-conditional deltas:

```text
Delta = terminal value of D - terminal value of the matched risk-free asset
E[Delta | outperform] > 0
Delta | matched = 0
E[Delta | underperform] < 0
```

Use absolute currency units when possible. If principal is unknown, report per
100 or 10,000 units of base currency. Include a confidence interval, credible
interval, scenario range, or distribution summary for the outperform and
underperform deltas.

Optionally add the unconditional expected delta as a secondary derived quantity:

```text
E[Delta] = P(outperform) * E[Delta | outperform] + P(underperform) * E[Delta | underperform]
```

The matched term is omitted because its delta is `0`.

Separate facts, assumptions, estimates, and implications. Call out missing
information that could materially change the probabilities or conditional
deltas. Do not present investment advice as certainty.
