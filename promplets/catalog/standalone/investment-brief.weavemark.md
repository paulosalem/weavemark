@promplet version: 0.7

@refine module:weavemark.std.reasoning.base_analyst
@refine module:weavemark.domains.finance.finance_safety mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true
@refine module:weavemark.std.lenses.comparative_alternatives mingle: true
@refine module:weavemark.std.lenses.explainability mingle: true

# Investment brief

Write in a clear, sober, evidence-oriented style. Avoid hype, unsupported
certainty, and investment advice phrased as instructions to buy, sell, or hold.

Write an educational investment brief for @{ticker}.

Audience: @{audience}

Time horizon: @{time_horizon}

Use the following notes as source material:

@{source_notes}

@match depth
  "committee" ==>
    Keep the memo concise. Focus on decision relevance, downside, evidence
    quality, timing, and the smallest useful next research step.

  "deep" ==>
    Add detailed sections for unit economics, competitive dynamics, management
    quality, valuation sensitivity, and disconfirming evidence.

@if include_watchlist
  Add a watchlist table with:
  - metric
  - current reading
  - threshold that would change the assessment
  - evidence needed next

@tool fetch_financial_metrics
  Fetch recent financial metrics for a public company.
  - ticker: string (required) - Public ticker symbol
  - period: string enum: [quarter, annual] default: quarter - Reporting period

@output enforce: strict
  Return exactly these sections:
  1. Thesis
  2. Evidence
  3. Risks
  4. Alternatives
  5. Open questions
  6. Decision trigger

@assert includes: "Risks"
@assert includes: "Open questions"
@assert includes: "not financial advice"
