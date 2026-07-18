@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst
@refine module:weavemark.std.analysis.ach_core

# Analysis of Competing Hypotheses (ACH)

@note
  This standalone prompt applies
  `module:weavemark.std.analysis.ach_core` to caller-provided hypotheses and
  evidence.

  References:
  - Heuer Jr., Richards J. (1999). "Psychology of Intelligence
    Analysis."
  - Heuer Jr., Richards J., and Randolph H. Pherson (2010).
    "Structured Analytic Techniques for Intelligence Analysis."

You are applying the Analysis of Competing Hypotheses (ACH) method.

Your objective is to compare multiple plausible explanations for the
same situation and determine which hypothesis is least inconsistent with
the evidence. Do not argue for a favorite story. Stress-test every
serious alternative.

## Problem

@{problem}

@if decision_question
  ## Decision Question

  @{decision_question}

@if additional_context
  ## Additional Context

  @{additional_context}

@if hypotheses
  ## Hypotheses Provided by the Caller

  Start with these hypotheses, but improve the set if needed. You may
  add, merge, split, rename, or discard hypotheses when that produces a
  cleaner ACH comparison.

  @{hypotheses}

@if evidence
  ## Evidence Provided by the Caller

  @{evidence}

@if assumptions
  ## Known Assumptions

  @{assumptions}

@if constraints
  ## Constraints

  @{constraints}

## Presentation Rules

- If the calling prompt already specifies a deliverable format, honor
  it, but still include the essential ACH elements: explicit
  hypotheses, an evidence inventory, disconfirming evidence, a ranked
  judgment, and collection priorities.
- Make concrete examples prominent. Use full sentences or short
  paragraphs when presenting them; do not reduce them to bare nouns or
  clipped bullet fragments unless the source material is genuinely that
  sparse.
- When you state a principle, mechanism, or hypothesis, follow it
  closely with verbatim examples that illustrate it.
- Do not create a separate "examples" section. The examples should live
  next to the instruction, principle, or conclusion they illuminate.
- If no external format is specified, use the default structure below.
- Prefer concise analytical prose plus tables where they improve
  comparison.

## Default Response Structure

### Analytic Question

State the question ACH is answering.

### Hypothesis Set

List the competing hypotheses actually evaluated. Note any changes made
to the caller's original set. For each major hypothesis, immediately
follow the statement with several verbatim examples that show what the
hypothesis is trying to explain.

### Evidence Inventory

Create a table with these columns:
- ID
- Evidence or Observation
- Type (fact / assumption / unknown / indicator)
- Reliability (high / medium / low)
- Diagnostic Value (high / medium / low)
- Notes

### ACH Matrix

Create a matrix with evidence IDs as rows and hypotheses as columns. Use
only: C, I, N, or M.

After the matrix, explain the 3-5 most diagnostic rows and why they
matter. Quote the most important rows verbatim while explaining them.

### Key Inconsistencies

For each hypothesis, list the strongest disconfirming evidence against
it, and place the verbatim examples directly under the inconsistency
they illustrate.

### Hypothesis Ranking

Rank the hypotheses from least inconsistent to most inconsistent.
For each hypothesis, state:
- Overall judgment
- Why it survives or fails
- Confidence (high / medium / low)

Immediately under each ranking judgment, include several verbatim
examples showing the evidence that most strongly supports or weakens
that hypothesis.

### Leading Explanation

State the current leading hypothesis and why it is preferred. Make
clear that ACH identifies the least inconsistent explanation, not a
proven truth. Support the explanation with verbatim examples placed
directly beneath the reasoning.

### Viable Alternatives

Identify any remaining plausible alternatives and what keeps them alive.
Place the verbatim examples next to each alternative, not in a detached
appendix.

### Collection Priorities

List the next 3-7 evidence questions, observations, or research actions
that would most reduce uncertainty.

### Assumptions, Bias Risks, and Caveats

List key assumptions, possible cognitive biases, data-quality
limitations, and conditions that could change the conclusion.
