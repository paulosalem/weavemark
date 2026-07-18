# Executable Financial Independence Goal Planner

Turn one plain-language personal-finance goal into a practical, educational decision-support plan. Do not present the result as regulated financial, legal, tax, accounting, brokerage, or fiduciary advice.

- Goal: Reach financial independence while keeping work optional, not necessarily retiring early
- Domain: personal finance
- Country/tax context: United States
- Horizon: 15 years
- Starting point: I have a steady income, save irregularly, and want a simple plan I can review monthly.
- Constraints: Avoid extreme frugality, avoid private-data uploads, keep the first actions simple, and treat all public assumptions as facts to verify.
- Public assumptions context: use the `public_assumptions` execution result from the public-reference lookup as planning context only. If that source is incomplete, stale, ambiguous, conflicting, or unavailable, say so and list what the user must verify before acting.

## Finance safety and evidence rules

- Treat the plan as educational analysis and decision support, not as personalized regulated advice.
- Do not guarantee returns, prices, yields, forecasts, tax outcomes, benefits, account limits, risk reductions, or independence dates.
- Prefer verified public source data over memory. When data is missing, stale, ambiguous, or conflicting, disclose the limitation and do not invent values.
- Surface downside risks and trade-offs before action-oriented suggestions.
- Separate supplied inputs, public/retrieved assumptions, deterministic calculations, estimates, interpretation, unknowns, and suggested options.
- Frame actions as options and planning steps rather than commands.
- Suggest checking qualified fiduciary, tax, legal, accounting, or benefits professionals when the decision depends on tax treatment, retirement-account rules, benefits eligibility, estate/legal issues, or high-stakes trade-offs.
- Ask the user to verify current limits, rates, tax rules, benefits, and account-specific constraints before acting.
- Do not request private account uploads, transaction histories, brokerage credentials, identity documents, or other sensitive financial records.
- For any calculation-like statement, verify units, signs, rates, periods, currencies, contribution timing, inflation assumptions, tax treatment, and cash-flow timing before relying on the result.

## Planning method

First state explicit assumptions. If public assumptions are incomplete or stale, state what the user must verify before acting.

### Define the finish line

Purpose: Translate the goal into observable success criteria.

Done when: The plan has one measurable target, one date or horizon, and one review trigger. The target may be expressed as an estimate or range when the available information does not justify a precise number.

### Map the current state

Purpose: Separate facts, estimates, unknowns, and constraints before recommending action.

Done when: The plan lists the user's current resources, gaps, and unknowns without pretending missing data is known.

### Build the milestone ladder

Purpose: Turn a distant goal into near, middle, and long-horizon milestones.

Done when: The plan has first-week, first-month, quarterly, and horizon-level milestones.

### Choose the next action set

Purpose: Make the first move concrete enough to do without another planning session.

Done when: The plan names 3-5 first-month actions, their order, and why each comes first.

### Install the review loop

Purpose: Keep the plan alive as conditions change.

Done when: The plan includes a lightweight cadence, metrics to check, and conditions for revising the strategy.

## Required output

Return exactly these sections:
1. Goal profile
2. Assumptions to verify
3. Milestone ladder
4. First-month actions
5. Review cadence
6. Failure modes and safeguards

Within those sections:
- Make the goal measurable without overclaiming precision.
- Identify assumptions from public sources separately from facts supplied by the user.
- Name gaps and unknowns plainly.
- Include first-week, first-month, quarterly, and 15-year milestones.
- Include 3-5 simple first-month actions, in order, with a short reason each comes first.
- Include a monthly review cadence with metrics and revision triggers.
- Include safeguards for stale public assumptions, tax or benefits rule changes, excessive risk, unrealistic savings expectations, liquidity shortfalls, burnout from extreme frugality, and overconfidence in forecasts.
- Use public assumptions only as planning context; ask the user to verify current limits, rates, tax rules, benefits, and account-specific details before acting.
