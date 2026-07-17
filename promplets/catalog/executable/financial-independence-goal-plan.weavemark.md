@promplet version: 0.7

@use weavemark.std.planning.goals exposing goal_plan lookup_public_goal_assumptions

@refine module:weavemark.domains.finance.finance_safety mingle: true

@bind web_search language: python from: "./companions/public_finance_reference.py" symbol: lookup_public_goal_assumptions

@execute weave
  scheduler: graph-strict
  allow_effects: [web_search]

# Executable Financial Independence Goal Planner

@lookup_public_goal_assumptions goal: "@{goal}" domain: "personal finance" country: "@{country}" horizon: "@{horizon}" as: public_assumptions

@goal_plan goal: "@{goal}" domain: "personal finance" horizon: "@{horizon}" starting_point: "@{starting_point}" constraints: "@{constraints}" assumption_source: "@{public_assumptions}"

Use the public assumptions only as planning context. Ask the user to verify any
current limits, rates, tax rules, or benefits before acting. Do not request
private account uploads.
