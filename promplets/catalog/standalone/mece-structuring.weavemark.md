@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst
@refine module:weavemark.std.reasoning.unstructured_input_normalization mingle: true
@refine module:weavemark.std.analysis.mece_core

# MECE Structuring

@note
  This spec turns the smaller `../library/analysis/mece-core.weavemark.md` methodology
  layer into a standalone analysis prompt. Specs that only need the abstract
  method should refine `../library/analysis/mece-core.weavemark.md` directly.

  Background reference:
  - Barbara Minto, "The Pyramid Principle."

You are applying the MECE structuring method.

Your objective is to organize the problem into buckets that are:

1. **Mutually exclusive** — no meaningful overlap, double-counting, or
   ambiguous assignment across sibling buckets
2. **Collectively exhaustive** — the full relevant universe is covered for the
   stated purpose

Use MECE as a disciplined problem-structuring method, not as empty formatting.
If a perfectly MECE decomposition is impossible because the real world is
messy, state the remaining overlap or gap explicitly and repair the structure
as far as practical instead of pretending it is cleaner than it is.

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

@if proposed_structure
  ## Initial Buckets Provided by the Caller

  Start from these buckets if they help, but improve, rename, split, merge,
  or discard them whenever that produces a cleaner MECE structure.

  @{proposed_structure}

## Common Failure Modes

- Mixing **diagnosis** and **solution** in the same structure.
  Bad example: `Onboarding friction / raise prices / competitor pressure`.
- Mixing **causes** and **symptoms**.
  Bad example: `Lower retention / poor product-market fit / declining NPS`.
- Mixing **parts of an equation** with the full equation.
  Bad example: `Profit / Revenue / Fixed cost`.
- Using labels that differ in breadth or granularity.
  Bad example: `Enterprise / SMB / Europe`.
- Creating a false sense of exhaustiveness with a large `Other` bucket.
- Forcing MECE where the correct answer is genuinely overlapping or
  multi-causal. In that case, define the primary logic clearly and state the
  overlap rather than hiding it.

## Presentation Rules

- If the calling prompt already specifies a deliverable format, honor it, but
  still include the essential MECE elements: the question, the boundary, the
  chosen decomposition logic, the structure itself, and a brief quality check.
- When helpful, show the structure as an indented tree, a table, or both.
- Label each level clearly so the reader can see what question that level
  answers.
- Use parallel wording across sibling buckets.
- If you repaired a flawed initial structure, explain the repair briefly.
- If the structure remains imperfect, say exactly where overlap or
  incompleteness remains.

## Default Response Structure

### Structuring Objective

State the question or decision the MECE structure is meant to support.

### Defined Universe and Boundaries

State what is included, excluded, the time horizon, and the unit of analysis.

### Chosen Decomposition Logic

Explain the logic used for the first level and why it is appropriate.

### MECE Structure

Present the structure with clear levels. For each level, keep the sibling set
parallel and explicitly MECE relative to the stated boundary.

### Quality Check

Briefly assess:
- mutual exclusivity
- collective exhaustiveness
- any residual overlaps or gaps
- any assumptions required to keep the structure usable

### Priority Areas for Analysis

Identify which branches should be analyzed first and why.
