# Executable Financial Independence Goal Planner

Turn one plain-language personal-finance goal into a practical, educational decision-support plan. Treat the result as planning support, not regulated financial, legal, tax, accounting, investment, brokerage, or fiduciary advice. Do not guarantee returns, rates, tax outcomes, benefit eligibility, risk reductions, or that financial independence will be achieved.

Use the public-assumptions execution result as planning context only. The user must verify any current limits, rates, tax rules, benefits, source dates, eligibility rules, and professional implications before acting. Do not request private account uploads, transaction files, identity data, portfolio statements, or credentials.

## Goal inputs

- Goal: Reach financial independence while keeping work optional, not necessarily retiring early
- Domain: personal finance
- Country/tax context: United States
- Horizon: 15 years
- Starting point: I have a steady income, save irregularly, and want a simple plan I can review monthly.
- Constraints: Avoid extreme frugality, avoid private-data uploads, keep the first actions simple, and treat all public assumptions as facts to verify.
- Assumption source: public assumptions retrieved at execution time from public reference sources for the goal, domain, country, and horizon.

## Safety and evidence rules

- Separate supplied inputs, public retrieved assumptions, deterministic calculations, estimates, unknowns, interpretation, and suggested options.
- Prefer verified source data over memory. If public assumptions are missing, stale, ambiguous, conflicting, or incomplete, say so plainly and avoid inventing values.
- Surface downside risks and tradeoffs before action-oriented suggestions.
- Frame actions as options and planning steps, not commands.
- Recommend checking an appropriate fiduciary financial planner, tax professional, legal professional, accountant, benefits administrator, or official government source when tax, benefits, legal, retirement-account, insurance, estate, or high-stakes decisions could materially change the plan.
- If missing goals, liquidity needs, debt details, household obligations, risk tolerance, income stability, or tax context would change the recommendation, list the focused questions or data points the user should answer; do not pretend missing data is known.
- For any calculations or numeric targets, verify units, time periods, rates, inflation assumptions, currencies, contribution timing, tax treatment, and cash-flow timing before reporting. Treat calculator-style results as consequences of stated assumptions, not recommendations by themselves.

## Planning method

First state explicit assumptions. If the public assumption source is incomplete, stale, or unavailable, say what the user must verify before acting.

### 1. Define the finish line

Purpose: translate the goal into observable success criteria.

Requirements:
- Define one measurable financial-independence target, one target date or horizon, and one review trigger.
- Make clear that “work optional” means the plan should support choice and resilience, not necessarily early retirement.
- Use ranges or formulas when exact values require private data the user has not provided.
- Identify what must be verified before any target can be treated as reliable.

Done when: the plan has one measurable target, one date or horizon, and one review trigger.

### 2. Map the current state

Purpose: separate facts, estimates, unknowns, and constraints before recommending action.

Requirements:
- List supplied facts from the user.
- List reasonable planning estimates separately from facts.
- List unknowns that materially affect the plan, such as income, expenses, current savings, debt, emergency fund, tax bracket, employer benefits, insurance needs, dependents, and risk tolerance.
- Respect the constraint to avoid private-data uploads; suggest user-kept summaries instead of account files.
- Do not infer hidden account balances, returns, contribution limits, tax outcomes, benefit eligibility, or expenses.

Done when: the plan lists the user's current resources, gaps, and unknowns without pretending missing data is known.

### 3. Build the milestone ladder

Purpose: turn the 15-year goal into near-, middle-, and long-horizon milestones.

Requirements:
- Include first-week, first-month, quarterly, annual, and horizon-level milestones.
- Connect each milestone to observable behavior or a measurable planning metric.
- Keep the ladder compatible with simple monthly review and non-extreme frugality.
- Name the assumptions each milestone depends on and what would require revision.

Done when: the plan has first-week, first-month, quarterly, and horizon-level milestones.

### 4. Choose the next action set

Purpose: make the first move concrete enough to do without another planning session.

Requirements:
- Name 3-5 first-month actions.
- Put actions in a practical order.
- Explain why each action comes first.
- Keep actions simple, low-friction, and consistent with avoiding extreme frugality.
- Present actions as options the user can adapt after verifying assumptions.
- Mention downside risks, opportunity costs, and safeguards before or alongside action suggestions.

Done when: the plan names 3-5 first-month actions, their order, and why each comes first.

### 5. Install the review loop

Purpose: keep the plan alive as conditions change.

Requirements:
- Use a lightweight monthly review cadence.
- Include metrics to check, such as savings rate, emergency-fund coverage, debt progress, contribution consistency, spending categories, insurance/benefits checkpoints, and progress toward the financial-independence target.
- Include conditions for revising the strategy, such as income change, household change, health/insurance change, major debt change, tax-law or benefit-rule change, market volatility, inflation assumptions changing, or discovery that a public assumption was stale.
- Avoid treating technical indicators, market forecasts, or historical averages as guarantees.

Done when: the plan includes a lightweight cadence, metrics to check, and conditions for revising the strategy.

## Required output

Return exactly these sections:

1. Goal profile
2. Assumptions to verify
3. Milestone ladder
4. First-month actions
5. Review cadence
6. Failure modes and safeguards

Within those sections:
- State explicit assumptions before relying on them.
- Use public assumptions only as context to verify.
- Ask the user to verify current limits, rates, tax rules, benefits, and personal constraints before acting.
- Include the phrase and content category “assumptions to verify.”
- Include the phrase and content category “first-month actions.”
- Do not request private account uploads.
- Do not guarantee returns, outcomes, forecasts, tax results, benefit eligibility, or risk reductions.

# Runtime public assumptions

```json
{
  "effect": "web_search read",
  "mode": "curated-public-reference-pack",
  "privacy_boundary": "Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.",
  "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
  "domain": "personal finance",
  "country": "United States",
  "horizon": "15 years",
  "queries": [
    "United States official retirement account contribution limits",
    "United States investor education compound interest calculator",
    "United States consumer finance budgeting emergency fund guidance",
    "financial independence planning assumptions safe withdrawal rate 15 years",
    "personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference"
  ],
  "sources": [
    {
      "query": "United States official retirement account contribution limits",
      "provider": "curated public reference",
      "results": [
        {
          "title": "IRS retirement plan contribution limits",
          "url": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions",
          "why_it_matters": "Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning."
        },
        {
          "title": "IRS IRA contribution limits",
          "url": "https://www.irs.gov/retirement-plans/traditional-and-roth-iras",
          "why_it_matters": "IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan."
        }
      ]
    },
    {
      "query": "United States investor education compound interest calculator",
      "provider": "curated public reference",
      "results": [
        {
          "title": "Investor.gov compound interest calculator",
          "url": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator",
          "why_it_matters": "Compounding examples help turn distant goals into reviewable savings and investment assumptions."
        }
      ]
    },
    {
      "query": "United States consumer finance budgeting emergency fund guidance",
      "provider": "curated public reference",
      "results": [
        {
          "title": "Consumer Financial Protection Bureau budgeting resources",
          "url": "https://www.consumerfinance.gov/consumer-tools/budgeting/",
          "why_it_matters": "Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions."
        }
      ]
    },
    {
      "query": "financial independence planning assumptions safe withdrawal rate 15 years",
      "provider": "curated public reference",
      "results": [
        {
          "title": "Bogleheads wiki: Safe withdrawal rates",
          "url": "https://www.bogleheads.org/wiki/Safe_withdrawal_rates",
          "why_it_matters": "Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user."
        }
      ]
    }
  ],
  "assumptions_to_verify": [
    "current tax-advantaged account contribution limits",
    "current local tax treatment and withdrawal rules",
    "inflation and expected expense assumptions",
    "safe-withdrawal assumptions appropriate to the user's country",
    "health insurance, housing, family, and job-risk constraints"
  ],
  "planning_lenses": [
    "savings-rate leverage",
    "expense-floor realism",
    "income resilience",
    "emergency-fund runway",
    "investment-policy clarity",
    "review cadence and behavior guardrails"
  ]
}
```

Use these runtime assumptions as the `public_assumptions` context referenced above. Verify current limits, rates, tax rules, and benefits before acting.