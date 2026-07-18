@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst
@refine module:weavemark.std.reasoning.unstructured_input_normalization mingle: true
@refine module:weavemark.std.analysis.issue_tree_core

# Issue Tree Analysis

@note
  This standalone prompt applies
  `module:weavemark.std.analysis.issue_tree_core` to caller-provided problem
  context and starting points.

  Related reference:
  - Barbara Minto, "The Pyramid Principle."

You are applying the issue tree method.

Your objective is to turn the problem into a hierarchy of decision-relevant
questions or drivers. Start from one clear root question, decompose it into
high-quality branches, and continue until the leaves are specific enough to
analyze, test, or act on.

Use the tree to guide thinking, not merely to decorate the answer. A good
issue tree is explicit about what question each node answers, what logic each
split uses, and what evidence would resolve the most important branches.

If the surrounding prompt already defines the problem, objective, and context,
apply this method to that material. Otherwise use the optional sections below.

@if problem
  ## Problem

  @{problem}

@if objective
  ## Objective

  @{objective}

@if additional_context
  ## Additional Context

  @{additional_context}

@if constraints
  ## Constraints

  @{constraints}

@if starting_points
  ## Initial Questions or Branches Provided by the Caller

  Use these as raw material if they help, but improve, rename, split, merge,
  or discard them when that yields a stronger tree.

  @{starting_points}

## Common Failure Modes

- Turning the tree into a task list instead of a logic structure.
- Mixing root-cause branches with solution ideas too early.
- Creating branches that are not true peers.
  Bad example: `Pricing / Enterprise / Europe / Competitor actions`.
- Expanding low-value branches deeply while leaving the critical branch vague.
- Confusing an issue tree with a probabilistic decision tree. An issue tree is
  primarily a decomposition and analysis-planning tool.
- Stopping at vague leaves such as `analyze customers` instead of specifying
  the question or metric to examine.
- Treating the first tree as final even after new evidence emerges.

## Presentation Rules

- If the calling prompt already specifies a deliverable format, honor it, but
  still make the issue tree explicit.
- Show the root question at the top.
- Present the tree in a clean hierarchy using indentation, numbering, or both.
- For the most important leaves, attach the key test, metric, or analysis
  needed to answer them.
- Clearly indicate any branch logic that is not obvious.
- If a branch set is not fully MECE, state the limitation explicitly rather
  than hiding it.

## Default Response Structure

### Root Question

State the single question the tree is designed to answer.

### Scope and Tree Type

State the boundary conditions and whether this is a diagnostic, driver,
solution, or strategic decision tree.

### Issue Tree

Present the hierarchy from root to leaves. Make clear what each level answers.

### Priority Branches

Identify the branches that deserve first attention and why.

### Analysis Plan by Leaf

For the most important leaves, state:
- what needs to be tested or measured
- what evidence or data would answer it
- what result would materially change the conclusion

### Assumptions and Tree Revisions

State the assumptions used, any non-MECE areas, and any likely revisions if
new evidence appears.
