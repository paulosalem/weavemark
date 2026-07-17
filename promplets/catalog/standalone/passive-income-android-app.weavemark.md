@promplet version: 0.7


@refine module:weavemark.domains.programming.types.android_app
@refine module:weavemark.domains.programming.stacks.android_kotlin_compose
@refine module:weavemark.domains.programming.modules.mobile_financial_dashboard
@refine module:weavemark.domains.finance.passive_income_capital_growth
@refine module:weavemark.domains.finance.passive_income_forecasting

# Passive-income Android app specification

@{app_name} is a native Android app for people pursuing financial independence
through passive income and disciplined capital growth.

## Product focus

The app helps the user know, before spending, how much passive income is likely
to be available this month and in future months. It should make the tradeoff
between consumption, reinvestment, reserves, and capital growth visible without
turning the product into a trading terminal or a generic budgeting app.

## Specific needs layered on top of the refined specs

- The primary answer is: "How much can I consume this month without compromising
  my capital-growth plan?"
- The financial-domain specs should induce the product's financial modules:
  passive income sources, expected payment dates, confirmed income, taxes,
  reserves, reinvestment rules, capital-growth assumptions, safe-to-spend
  calculations, scenarios, warnings, and review trails.
- The app forecasts monthly passive income and safe-to-spend amounts for at
  least 12 months.
- The app compares conservative, expected, and optimistic scenarios so users can
  avoid planning around best-case income.
- The app makes capital erosion visible when consumption, taxes, or missed income
  would force principal drawdown.
- The app should be local-first and privacy-preserving. Optional sync or backup
  may exist, but the core planning experience must work on device.
- Do not include detailed database table definitions unless a field is critical
  to forecasting correctness, privacy, or user trust.
