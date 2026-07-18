@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst
@refine module:weavemark.domains.finance.finance_safety mingle: true
@refine module:weavemark.domains.finance.finance_context_sufficiency mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true
@refine module:weavemark.std.analysis.strategic_problem_analysis
@refine module:weavemark.std.analysis.optionality_decision
@refine module:weavemark.domains.finance.financial_resilience_lens
@refine module:weavemark.domains.finance.passive_income_capital_growth
@refine module:weavemark.domains.finance.passive_income_forecasting
@refine module:weavemark.std.analysis.mece_core
@refine module:weavemark.std.lenses.decision_gate mingle: true

# Financial independence passive-income decision

@{person_name} is deciding whether their household has enough financial
resilience to reduce dependence on a high-pressure job and move toward more
work optionality while preserving capital growth.

## Situation

- Age: @{age}
- Current invested assets: @{invested_assets}
- Annual household income: @{annual_income}
- Annual spending: @{annual_spending}
- Current annual investments: @{annual_investments}
- Desired annual work-optional spending: @{target_spending}
- Current emergency fund: @{emergency_fund}
- Assumed long-run real portfolio return: @{real_return}
- Estimated reduced-hours income: @{reduced_hours_income}
- Estimated lower-pressure role income: @{lower_pressure_income}
- Expected monthly passive income: @{expected_monthly_passive_income}
- Confirmed monthly passive income average: @{confirmed_monthly_passive_income}
- Monthly reinvestment target for capital growth: @{monthly_reinvestment_target}
- Monthly tax reserve on passive income: @{monthly_tax_reserve}
- Principal drawdown preference: @{principal_drawdown_preference}
- Current job pressure: high and visibly affecting health, but not an emergency
- Household preference: preserve long-term flexibility while reducing chronic
  stress within the next 12 to 18 months

## Decision question

Should @{person_name} keep maximizing income, reduce hours, switch to lower-paid
but healthier work, or use only safe-to-spend passive income to support a
12-month transition period while collecting better evidence?

## Local emphasis

- Treat this as a strategic financial independence and work-optionality decision,
  not as generic personal finance commentary.
- Use the passive-income and capital-growth specs as analysis obligations:
  distinguish confirmed from projected income, income from selling capital, and
  safe-to-spend money from reinvestment or reserve money.
- Explain the MECE method in enough detail for the respondent to apply it
  correctly, but integrate that explanation into this financial-independence
  decision rather than presenting it as a detached methodology lecture.
- Compare the four options using action-changing thresholds tied to the supplied
  numbers.
- Include a 12-month passive-income evidence plan if immediate switching is not
  justified.
