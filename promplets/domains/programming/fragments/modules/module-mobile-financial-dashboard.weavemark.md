@promplet version: 0.7

@module weavemark.domains.programming.modules.mobile_financial_dashboard

# Module: Mobile Financial Visibility Dashboard

Use this module when a mobile product must answer a financial-status question
quickly without overwhelming the user. Domain-specific specs should supply the
exact financial concepts, calculations, and warnings.

### Dashboard Purpose

- Put the main answer at the top: what the user can safely do now, why, and what
  could change it.
- Show the current month, next month, and a 12-month lookahead.
- Make assumptions visible near the numbers they affect.
- Separate confirmed amounts from projected amounts.
- Prefer plain-language status cards over dense tables.

### Required Views

- Today card: the main financial answer, its confidence, the most important
  deductions or buffers, and the current health/status signal.
- Monthly calendar or timeline: expected events, confirmed events, forecast
  confidence, and shortfalls or surpluses.
- Scenario panel: compare conservative, expected, and optimistic assumptions.
- Health card: show whether the user's plan preserves the relevant domain target.
- Alerts: notify only when a material threshold changes, such as a projected
  shortfall, missed event, unsafe action, or assumption becoming stale.

### Interaction Principles

- Let users change assumptions inline and immediately see the effect.
- Show explanations before advanced controls.
- Keep exports simple: monthly summary, assumptions, and scenario comparison.
- Avoid noisy dashboard behavior unless it changes the user's near-term decision.
