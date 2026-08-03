@promplet version: 0.7

@refine module:weavemark.std.reasoning.base_analyst
@refine module:weavemark.domains.finance.finance_safety mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true
@refine module:weavemark.std.analysis.strategic_problem_analysis mingle: true
@refine module:weavemark.domains.finance.financial_resilience_lens mingle: true
@refine module:weavemark.domains.finance.passive_income_capital_growth
@refine module:weavemark.domains.finance.passive_income_forecasting
@refine module:weavemark.std.lenses.decision_gate mingle: true

# Financial independence passive-income decision

Assess whether @{person_name}'s household has enough financial resilience to
reduce dependence on a high-pressure job.

## Household snapshot

- Age: @{age}
- Invested assets: @{invested_assets}
- Annual income: @{annual_income}
- Annual spending: @{annual_spending}
- Annual investments: @{annual_investments}
- Target spending: @{target_spending}
- Emergency fund: @{emergency_fund}
- Planning real return: @{real_return}

## Work alternatives

- Reduced-hours income: @{reduced_hours_income}
- Lower-pressure income: @{lower_pressure_income}

## Passive-income plan

- Expected monthly passive income: @{expected_monthly_passive_income}
- Confirmed monthly passive income: @{confirmed_monthly_passive_income}
- Monthly reinvestment target: @{monthly_reinvestment_target}
- Monthly tax reserve: @{monthly_tax_reserve}
- Principal-drawdown preference: @{principal_drawdown_preference}

Distinguish confirmed from projected income, income from principal sales, and
safe-to-spend cash from amounts reserved for taxes, liquidity, and reinvestment.
Compare the current job, reduced-hours work, and lower-pressure work. State the
strongest counterarguments and missing evidence before applying a decision gate.

@output enforce: strict
  Return exactly these sections:
  1. Decision context
  2. Confirmed facts and assumptions
  3. Coverage and resilience analysis
  4. Downside case and counterarguments
  5. Options and tradeoffs
  6. Decision gate
  7. Evidence to verify next

@assert contains: "Decision gate"
@assert contains: "Evidence to verify next"
