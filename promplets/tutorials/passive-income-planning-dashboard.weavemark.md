@promplet version: 0.7

@refine module:weavemark.domains.programming.stacks.typescript_nextjs_prisma_sqlite
@refine module:weavemark.domains.programming.types.local_first_webapp
@refine module:weavemark.domains.programming.modules.dashboard
@refine module:weavemark.domains.finance.passive_income_capital_growth
@refine module:weavemark.domains.finance.passive_income_forecasting

# Passive-Income Planning Dashboard

Design @{app_name}, a local-first web application for people pursuing financial
independence through passive income and disciplined capital growth.

Make the primary dashboard answer:

- how much recurring income is confirmed versus projected;
- how much is safe-to-spend after taxes, reserves, and reinvestment;
- whether the capital-growth target remains viable;
- which assumptions are stale or insufficiently supported;
- which shortfall or capital erosion risks need attention.

Preserve source-level payment schedules, currencies, dates, confidence, and
evidence. Support conservative, expected, and optimistic scenarios, comparison
with prior forecasts, local export/import, restart recovery, and accessible
table equivalents for every chart.

@structural_constraints strict: true
  The specification MUST contain exactly these sections in order:
  1. Product boundaries and privacy
  2. Technology and runtime
  3. Financial model and terminology
  4. Durable data and integrity
  5. Forecasting behavior
  6. Decision-oriented dashboard
  7. Responsive and accessible interaction
  8. Local operations and recovery
  9. Verification

@assert contains: "safe-to-spend"
@assert contains: "capital erosion"
