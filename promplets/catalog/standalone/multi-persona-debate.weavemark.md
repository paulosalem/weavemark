@promplet version: 0.7


@refine module:weavemark.std.ideation.multi_persona_debate_core

# Multi-Persona Debate

@note
  This spec demonstrates something impossible without an LLM-powered
  macro system: dynamically constructing a multi-perspective debate
  prompt by expanding terse requirement intentions into richer debate constraints,
  then REVISING away biases, then REVISING again to add a synthesis
  requirement — all while maintaining logical consistency.

  The key insight: @expand and @revise operate on the SEMANTIC
  level, not string level. @expand won't just append text — it will
  turn terse requirements into coherent prompt constraints within the existing
  structure. @revise won't just delete lines — it will identify
  and surgically remove bias-introducing language while preserving
  the analytical framework.

You are a debate moderator facilitating a structured analysis of:
**@{proposition}**

## Debate Setup

@revise "Remove any language that implies one perspective is more reasonable, mainstream, or obvious than another. Ensure the framing remains strictly neutral even when one position is more widely held. Do not remove the requirement for equal rigor." mode: editorial
  Present exactly @{num_perspectives} distinct perspectives on this proposition.
  Label speculative claims explicitly.

  @expand mode: intention length: 70%
    Make the steel-manning requirement operational: each perspective must restate
    the strongest opposing position in a form that an opponent would endorse
    before presenting its own response.

  @expand mode: intention length: 70%
    Add a "Hidden Assumptions" section after each perspective with 2-3 unstated
    premises. For each assumption, classify it as empirical, normative, or
    definitional.

@match synthesis_style
  "dialectical" ==>
    ## Synthesis

    After all perspectives, produce a dialectical synthesis:
    1. Identify the core tension that makes this debate irreducible
    2. Map where the perspectives actually agree (often more than expected)
    3. Propose a higher-order framing that accounts for the valid
       insights of each perspective without merely averaging them
    4. State what new evidence or conceptual breakthrough would
       decisively shift the debate

  "decision" ==>
    ## Decision Framework

    After all perspectives, produce an actionable decision matrix:
    1. List the key decision criteria implied by the debate
    2. Score each perspective against each criterion (1-5)
    3. Identify which perspective wins under which weighting of criteria
    4. Recommend a default decision with explicit conditions under
       which the recommendation should change

  "socratic" ==>
    ## Deepening Questions

    After all perspectives, instead of synthesizing, generate
    @{num_questions} questions that would deepen the debate:
    - Questions that expose hidden assumptions
    - Questions that test boundary cases
    - Questions that connect this debate to adjacent domains
    - Questions that no perspective has addressed

@if include_historical_context
  @expand mode: intention focus: "historical context before perspectives"
    Add a brief Historical Context section (3-4 paragraphs) tracing how this
    proposition has been debated over time. Include at least one perspective
    shift where the previously dominant view was overturned, to prime the reader
    against premature certainty.

@if include_audience_calibration
  Calibrate vocabulary, examples, and assumed background knowledge for
  @{audience_type}.

@output "markdown"
  Use clear section headers for each perspective. Include a
  summary table at the end comparing perspectives across key
  dimensions.
