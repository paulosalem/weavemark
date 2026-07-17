@promplet version: 0.7

@module weavemark.std.analysis.mece_core

# Core MECE Methodology

MECE means **Mutually Exclusive, Collectively Exhaustive**. It is a
problem-structuring discipline: partition a clearly defined universe into
sibling buckets that do not materially overlap and that, together, cover the
relevant decision space.

MECE is not a formatting style. Use it only when it improves diagnosis,
prioritization, recommendation quality, or action design.

## Core obligations

- Define the universe before decomposing it. State what is being divided, for
  what purpose, over what time horizon, and with what unit of analysis.
- Use one decomposition logic at a time for each sibling set. Do not mix
  dimensions such as segment, geography, cause, solution, and metric at the
  same level.
- Keep siblings at the same abstraction level. Do not place a whole next to one
  of its parts.
- Make assignment unambiguous. A reasonable reader should be able to place an
  item primarily in one bucket without double-counting.
- Treat exhaustiveness as relative to the stated objective and boundary. Cover
  every material driver, option, risk, case, or scenario needed for the
  decision.
- Prefer explicit residual handling over vague catch-all buckets. If `Other`,
  `Unknown`, or `Not yet classified` appears, define what belongs there and how
  it will be resolved.
- Structure for decision usefulness, not taxonomic neatness. A MECE structure
  should help explain, compare, prioritize, test, or decide.
- Revise the structure when new evidence reveals overlap, hidden gaps,
  inconsistent definitions, or a better decomposition basis.

## Required workflow

A MECE analysis must make these workflow elements operationally visible when
integrated into a specific problem. Do not omit the boundary dimensions or
quality-check names just because the method is being specialized.

1. State the exact question, decision, diagnosis, or planning problem the
   structure must support.
2. Define the boundary conditions:
   - in scope and out of scope
   - time horizon
   - unit of analysis
   - metric, outcome, or decision criterion
3. Choose the first-level decomposition logic and explain why it fits this
   problem.
4. Draft first-level buckets using parallel wording and a single logical basis.
5. Test mutual exclusivity:
   - Can the same material item fit in more than one bucket?
   - Are labels vague, nested, partially synonymous, or at different levels?
   - Are causes, symptoms, actions, and outcomes mixed as siblings?
6. Test collective exhaustiveness:
   - What material item, scenario, risk, driver, or option is not covered?
   - Does a residual bucket hide important uncertainty?
7. Decompose only where more detail is decision-useful. At each deeper level,
   repeat the same MECE tests.
8. State any remaining overlap or incompleteness explicitly, with the cleanest
   practical workaround.

## Quality checks

Before accepting a structure, run these checks:

- **Same-question test**: all sibling buckets answer the same parent question.
- **No-overlap test**: one observation, case, dollar, risk, or option maps
  primarily to one bucket.
- **No-gap test**: no material item falls outside the structure.
- **Same-level test**: siblings are peers, not a mix of parent, child, and
  tangent.
- **Same-logic test**: one decomposition dimension is used per level.
- **Decision-usefulness test**: each bucket helps explain, analyze, compare, or
  decide something material.
- **Traceability test**: downstream conclusions can be mapped back to the
  structure without double-counting.
