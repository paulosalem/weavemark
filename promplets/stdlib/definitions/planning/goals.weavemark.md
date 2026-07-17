@promplet version: 0.7

@module weavemark.std.planning.goals

@define planning_checkpoint
  @param name
    The checkpoint heading.

  @param purpose
    Why this checkpoint exists.

  @param done_when
    Observable completion condition.

  @body
    ### @{name}

    Purpose: @{purpose}

    Done when: @{done_when}

@define goal_plan
  @param goal
    Plain-language user goal.

  @param domain
    Domain where the goal lives.

  @param horizon
    Desired time horizon.

  @param starting_point
    Brief description of the user's current situation.

  @param constraints
    Boundaries, preferences, and things the plan must avoid.

  @param assumption_source
    Public assumptions, runtime lookup result, or user-verified reference material.

  @body
    # Goal-to-plan compiler

    Turn one plain-language goal into a practical plan.

    - Goal: @{goal}
    - Domain: @{domain}
    - Horizon: @{horizon}
    - Starting point: @{starting_point}
    - Constraints: @{constraints}
    - Assumption source: @{assumption_source}

    First state explicit assumptions. If the assumption source is incomplete or
    stale, say what the user must verify before acting.

    @planning_checkpoint name: "Define the finish line" purpose: "Translate the goal into observable success criteria." done_when: "The plan has one measurable target, one date or horizon, and one review trigger."

    @planning_checkpoint name: "Map the current state" purpose: "Separate facts, estimates, unknowns, and constraints before recommending action." done_when: "The plan lists the user's current resources, gaps, and unknowns without pretending missing data is known."

    @planning_checkpoint name: "Build the milestone ladder" purpose: "Turn a distant goal into near, middle, and long-horizon milestones." done_when: "The plan has first-week, first-month, quarterly, and horizon-level milestones."

    @planning_checkpoint name: "Choose the next action set" purpose: "Make the first move concrete enough to do without another planning session." done_when: "The plan names 3-5 first-month actions, their order, and why each comes first."

    @planning_checkpoint name: "Install the review loop" purpose: "Keep the plan alive as conditions change." done_when: "The plan includes a lightweight cadence, metrics to check, and conditions for revising the strategy."

    ## Required output

    @output enforce: strict
      Return exactly these sections:
      1. Goal profile
      2. Assumptions to verify
      3. Milestone ladder
      4. First-month actions
      5. Review cadence
      6. Failure modes and safeguards

    @assert includes: "first-month actions"
    @assert includes: "assumptions to verify"

@define lookup_public_goal_assumptions
  @phase execute
  @scope self
  @returns value

  @param goal
    Plain-language user goal.

  @param domain
    Domain where the goal lives.

  @param country
    Country or jurisdiction for public reference lookup.

  @param horizon
    Desired time horizon.

  @effect web_search read

  @body
    Search public reference sources for current, non-private assumptions that
    help plan @{goal} in @{domain} for @{country} over @{horizon}. Return source
    titles, URLs, query terms, assumptions to verify, and caveats. Do not read
    private accounts, transactions, portfolios, or identity data.
