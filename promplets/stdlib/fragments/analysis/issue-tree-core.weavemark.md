@promplet version: 0.7

@module weavemark.std.analysis.issue_tree_core

# Issue Tree Analysis Core

Issue trees decompose a top-level question into a hierarchy of smaller,
answerable questions or drivers. A good issue tree makes analysis tractable,
exposes the logic of the problem, and shows where to investigate first.

## Core issue-tree obligations

- Start with one precise root question. The tree should answer a single
  decision-relevant question, not several loosely related ones.
- Use the right tree type for the problem:
  - **Diagnostic tree** for `Why is this happening?`
  - **Driver tree** for `What determines this outcome?`
  - **Solution tree** for `How can we achieve this objective?`
  - **Strategic decision tree** for `Should we pursue this option, and on what basis?`
- At each split, child branches should collectively answer the parent question.
  Whenever possible, make sibling branches MECE.
- Use one logic per split. Do not mix causes, actions, stakeholder groups, and
  success metrics at the same level.
- Keep branches at the same level of abstraction and in parallel form.
- Decompose only to the level needed for concrete analysis. Leaves should point
  to specific analyses, data requests, experiments, or decisions.
- Prioritize high-impact, high-uncertainty branches. Do not expand every branch
  to identical depth just for visual symmetry.
- Treat the tree as provisional and revise it when evidence shows the original
  branch logic was incomplete or wrong.

## Required issue-tree workflow

1. State the root question in one sentence.
2. Define scope and boundary conditions:
   - decision or outcome that matters
   - in scope and out of scope
   - time horizon
   - relevant constraints
3. Identify the tree type: diagnostic, driver, solution, or strategic decision.
4. Draft first-level branches that each answer a necessary part of the root
   question.
5. Test the first-level split for mutual distinguishability, exhaustiveness,
   decision relevance, peer level, and one consistent logic.
6. Decompose the most important branches into second- and third-level questions
   or drivers.
7. Stop when a leaf can be answered by a concrete calculation, customer or
   market cut, process review, data request, experiment, or strategic choice.
8. For each important leaf, specify the evidence, metric, or analysis that
   would resolve it.
9. Highlight the branches that matter most for the final decision and explain
   why they are prioritized.

## Branch-building guidance

- Prefer question or driver labels that clearly indicate what must be answered.
- For diagnostic problems, branch by plausible causes.
- For driver problems, branch by the equation or operating model that generates
  the outcome.
- For solution problems, branch by feasible levers or workstreams, not random
  ideas.
- For strategic decision problems, branch by decision criteria rather than
  premature answers.
