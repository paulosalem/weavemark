@promplet version: 0.7

@use weavemark.std.planning.goals exposing goal_plan

@refine module:weavemark.domains.finance.finance_safety mingle: true

# Financial independence goal-to-plan prompt

@goal_plan goal: "@{goal}" domain: "personal finance" horizon: "@{horizon}" starting_point: "@{starting_point}" constraints: "@{constraints}" assumption_source: "@{public_assumptions}"

Apply the resulting plan specifically to financial independence. Treat the
result as planning support, not financial, tax, legal, or investment advice.
Keep the first actions simple enough for someone with no transaction upload,
portfolio upload, or spreadsheet model.
