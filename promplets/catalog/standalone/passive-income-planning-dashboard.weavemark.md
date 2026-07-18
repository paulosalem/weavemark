@promplet version: 0.7

@refine module:weavemark.domains.programming.foundations.base_spec_author mingle: true
@refine module:weavemark.domains.programming.stacks.typescript_nextjs_prisma_sqlite mingle: true
@refine module:weavemark.domains.programming.types.local_first_webapp mingle: true
@refine module:weavemark.domains.programming.modules.dashboard mingle: true
@refine module:weavemark.domains.programming.modules.local_sqlite_storage mingle: true
@refine module:weavemark.domains.programming.modules.notifications mingle: true
@refine module:weavemark.domains.finance.passive_income_capital_growth mingle: true
@refine module:weavemark.domains.finance.passive_income_forecasting mingle: true

# Passive-Income Planning Dashboard

Design **@{app_name}**, a local-first web application for people pursuing
financial independence through passive income and disciplined capital growth.

## Product decision

The product helps the user answer:

> How much passive income can I use this month without compromising taxes,
> reserves, reinvestment, or my capital-growth policy?

It is a planning and evidence tool, not a brokerage, bank, trading terminal, tax
calculator, or generic household-budget app.

## Financial visibility

- Track passive-income sources, expected payment dates, confirmed receipts,
  taxes, reserves, reinvestment rules, and capital-growth assumptions.
- Distinguish confirmed income from expected income and cash income from
  principal sales or drawdown.
- Forecast monthly gross income, deductions, reinvestment, and safe-to-use
  amounts for at least 12 months.
- Compare conservative, expected, and optimistic scenarios without presenting
  any scenario as guaranteed.
- Make capital erosion visible when spending, taxes, fees, or missed income would
  require principal drawdown.
- Show the assumption, source, freshness, and user override behind every derived
  amount.

## Dashboard

- Primary card: this month's safe-to-use amount, confidence, decisive deductions,
  and the condition most likely to change it.
- Timeline: expected, confirmed, late, changed, and missing income events.
- Scenario comparison: conservative, expected, and optimistic monthly paths.
- Capital-policy card: reinvestment target, reserve status, principal-drawdown
  risk, and material threshold changes.
- Attention queue: stale assumptions, missing confirmations, projected
  shortfalls, tax-reserve gaps, and policy violations.
- Quiet state: current answer, last review, next expected payment, and next
  scheduled review without filling the screen with charts.

## Local-first persistence

SQLite is authoritative for sources, income events, confirmations, assumptions,
scenario versions, policy changes, review decisions, and notifications. The app
works offline for entry, review, forecasting, and export. Optional backup/sync
must not be required for the core workflow.

## Inputs and corrections

- Support careful manual entry and CSV import with preview, mapping, validation,
  duplicate detection, and rollback.
- Never infer a confirmed payment from an expected schedule.
- Let users correct classifications, dates, amounts, and assumptions while
  preserving the previous value and reason.
- Recompute affected scenarios immediately after an accepted correction.

## Notifications

Notify only for decision-changing events: a confirmed/missed payment, projected
shortfall, reserve breach, stale critical assumption, or safe-to-use threshold
change. Every notification explains what changed and links to the underlying
evidence.

## Safety and boundaries

- Label outputs as planning support, not individualized financial, tax, legal, or
  investment advice.
- Do not guarantee yield, payment timing, asset value, tax treatment, or financial
  independence.
- Keep imported statements and planning data local by default.
- Never request brokerage credentials or execute financial transactions.

@output enforce: strict
  Return:
  1. Product promise and explicit non-goals
  2. Local-first architecture and SQLite persistence
  3. Financial data model and calculation provenance
  4. Dashboard, timeline, scenarios, attention, and quiet/error/offline states
  5. Entry, CSV import, correction, and review workflows
  6. Forecasting and safe-to-use calculation rules
  7. Notification policy
  8. Privacy, safety, and advice boundaries
  9. Testing and acceptance criteria

@assert includes: "safe-to-use"
@assert includes: "confirmed"
@assert includes: "principal drawdown"
@assert includes: "Local-first"
