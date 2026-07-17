@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst mingle: true
@refine module:weavemark.std.guidelines.context_sufficiency mingle: true
@refine module:weavemark.std.analysis.strategic_problem_analysis mingle: true
@refine module:weavemark.std.analysis.optionality_decision mingle: true
@refine module:weavemark.std.lenses.comparative_alternatives mingle: true
@refine module:weavemark.std.lenses.decision_gate mingle: true
@refine module:weavemark.std.lenses.explainability mingle: true

# Decision Advisor Prompt

@note
  Final prompt for a paste-ready decision-advisory instruction that turns a
  vague choice into criteria, options, tradeoffs, gate logic, and next evidence.

Help me make the decision below.

## Decision question

@{decision_question}

## Background

@{background}

## Options under consideration

@{options}

## Constraints and preferences

@{constraints}

## Decision timing

@{decision_timing}

## Criteria that matter

@{criteria}

## Required behavior

- Treat this as a consequential decision, not generic advice.
- Separate facts, assumptions, unknowns, preferences, and judgment calls.
- If context is limited, make a provisional recommendation only with visible
  caveats.
- Compare the realistic options against explicit criteria.
- Evaluate reversibility, option value, downside protection, and timing.
- Include the strongest counter-argument to the recommended path.
- Define what evidence would change the recommendation.

## Required output

Use labeled lines directly for compact snapshots. Do not add standalone format
labels such as `text`, `markdown`, or `json`.

1. **Context status** — sufficient, limited, or insufficient.
2. **Decision frame** — what decision is actually being made and why now.
3. **Options table** — option, upside, downside, reversibility, option value,
   risk, and best use case.
4. **Decision criteria** — criteria, weight or importance, and current read.
5. **Gate** — go, no-go, wait, or investigate, with one-sentence reason and
   confidence.
6. **Recommendation** — the best path, confidence, caveats, and strongest
   counter-argument.
7. **Next evidence** — the minimum evidence or experiment that would improve the
   decision.
8. **Change triggers** — what would flip the recommendation.
