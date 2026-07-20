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
"matched" performance. Define a symmetric materiality threshold `epsilon > 0`:
outperformance is `Delta > epsilon`, matched performance is
`-epsilon <= Delta <= epsilon`, and underperformance is `Delta < -epsilon`.
Matched outcomes may therefore have a nonzero delta.

## Required output

| Quantity | Estimate | Confidence | Notes |
| --- | --- | --- | --- |
| `P(D outperforms the risk-free asset)` | probability | low/medium/high | main drivers |
| `P(D matches the risk-free asset)` | probability | low/medium/high | materiality band used |
| `P(D underperforms the risk-free asset)` | probability | low/medium/high | downside drivers |
| `E[Delta | outperform]` | positive absolute value | interval/distribution | likely outperform magnitude |
| `E[Delta | matched]` | signed value within the materiality band | interval/distribution | residual matched magnitude |
| `E[Delta | underperform]` | negative absolute value | interval/distribution | likely underperform magnitude |

The three probabilities must be mutually exclusive, collectively exhaustive,
and sum to 100% except for rounding.

## Delta

Report scenario-conditional deltas:

```text
Delta = terminal value of D - terminal value of the matched risk-free asset
E[Delta | outperform] > epsilon
-epsilon <= E[Delta | matched] <= epsilon
E[Delta | underperform] < -epsilon
```

Use absolute currency units when possible. If principal is unknown, report per
100 or 10,000 units of base currency. Include a confidence interval, credible
interval, scenario range, or distribution summary for the outperform and
underperform deltas.

Add the unconditional expected delta as a secondary derived quantity, using
probabilities as fractions:

```text
E[Delta] = P(outperform) * E[Delta | outperform]
         + P(matched) * E[Delta | matched]
         + P(underperform) * E[Delta | underperform]
```

Do not omit the weighted matched term merely because the band is narrow.

Separate facts, assumptions, estimates, and implications. Call out missing
information that could materially change the probabilities or conditional
deltas. Do not present investment advice as certainty.
