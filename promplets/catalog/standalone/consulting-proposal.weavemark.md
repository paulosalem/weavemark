@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst

# Consulting Proposal

@note
  This consulting proposal spec demonstrates a realistic pipeline:
  @refine pulls in the analyst persona, prose sets audience and tone, @output constrains the deliverable, @match
  selects the engagement scope, and @assert validates quality.

You are preparing a management consulting proposal for **@{client_name}**,
a @{client_industry} company seeking to **@{engagement_goal}**.

Tailor the language, depth, and examples for @{audience_type}. Use an
authoritative, structured, data-driven consulting style.

## Engagement Context

@{client_name} is facing the following challenges:
@{challenges}

The consulting engagement itself lasts **@{timeline}** and the expected budget
range is **@{budget_range}**. The implementation roadmap may extend beyond that
engagement. For transformation work, use the engagement to validate the
diagnosis, mobilize governance, begin the near-term work, and leave an owned
roadmap for later phases; do not promise that the full transformation will be
complete within the consulting timeline.

@match engagement_scope
  "diagnostic" ==>
    ### Deliverable: Diagnostic Assessment

    Produce a 2-week diagnostic that:
    1. Maps current-state processes across @{focus_areas}
    2. Identifies the top 5 pain points by impact severity
    3. Estimates the cost of inaction for each (annualized $)
    4. Recommends whether a full transformation engagement is warranted

    Format: Executive slide deck (10–15 slides) + data appendix.

  "transformation" ==>
    ### Deliverable: Transformation Roadmap

    @summarize
      Design a phased transformation roadmap covering:
      - Phase 1 (Quick Wins, 0–3 months): Low-effort, high-impact changes
        that build momentum and stakeholder confidence.
      - Phase 2 (Foundation, 3–9 months): Infrastructure, process redesign,
        and capability building required for sustainable change.
      - Phase 3 (Scale, 9–18 months): Full rollout, change management, and
        performance measurement against KPIs.

      For each phase, specify:
      - Workstreams and ownership
      - Dependencies and critical path
      - Investment required and quantified ROI estimates
      - Risk factors with specific, actionable mitigation strategies

    @assert contains: "quantified ROI estimates"
    @assert contains: "specific, actionable mitigation strategies"

  "strategy" ==>
    ### Deliverable: Strategic Options Paper

    Present 3 mutually exclusive strategic options for achieving
    **@{engagement_goal}**. For each option:

    1. **Thesis**: One-sentence strategic hypothesis
    2. **Evidence**: Supporting data points and market signals
    3. **Financial model**: Revenue impact, cost structure, payback period
    4. **Risks**: Probability-weighted risk assessment
    5. **Recommendation**: Go / No-Go with conditions

    Conclude with a clear recommendation of the preferred option,
    supported by a decision matrix scoring each on feasibility,
    impact, speed, and risk.

@output "markdown"
  Use professional consulting report formatting with clear section
  numbering, executive summary up front, and appendices for
  supporting data.

Give the assembled proposal one coherent consulting-report flow without adding
or removing substantive recommendations, evidence, risks, or financial details.

Focus on delivering actionable, evidence-based recommendations that
@{client_name} can begin executing during the **@{timeline}** engagement, with
clear ownership and milestones for implementation that continues afterward.
