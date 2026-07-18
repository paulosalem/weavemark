# WeaveMark Example Studies

[View as HTML](results.html)

## Bottom line

These studies inspect public example outputs without contrastive controls. They check whether each example compiles into a useful final prompt, whether the output fits its stated intention, and whether it avoids leaked directives, placeholders, brittle meta-commentary, and other pathologies.

## At a glance

- Examples studied: **9**.
- Average rubric score: **23.7/25**.
- Outputs live in their own `examples/.../outputs/` folders.

## Metric definitions

- **Source words:** Words in the local study source for a variant; this is the local authoring burden.
- **Variable words:** Words in a variant's explicit input payload, when a template or refinement uses one.
- **Output words:** Words in the saved compiled final artifact.
- **Leverage:** Output words divided by local source words; larger means more final artifact per local word, not quality by itself.
- **Fact units:** Novelty-weighted semantic fact units extracted from the output by deterministic rules.
- **Density:** Discounted fact units per 1,000 output words; higher means a more information-dense output.
- **Yield:** Discounted fact units per 1,000 local source words; higher means more semantic material per local authoring word.
- **Rubric:** Sum of five 1-5 quality checks: intention fit, completeness, writing/structure, no leakage/pathologies, and direct usefulness.

## Example metrics

| Example | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield | Rubric |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Program Review Checklist](../../examples/terminal-output-only/program-review-checklist/outputs/compiled-prompt.md) | 506 | 22 | 788 | 1.56x | 43.75 | 55.5 | 86.5 | 24/25 |
| [Program Debugging Assistant](../../examples/terminal-output-only/program-debugging-assistant/outputs/compiled-prompt.md) | 319 | 172 | 948 | 2.97x | 67.75 | 71.5 | 212.4 | 24/25 |
| [Learning Tutor](../../examples/terminal-output-only/learning-tutor/outputs/compiled-prompt.md) | 234 | 90 | 942 | 4.03x | 57.75 | 61.3 | 246.8 | 22/25 |
| [Research Brief](../../examples/terminal-output-only/research-brief/outputs/compiled-prompt.md) | 281 | 103 | 1370 | 4.88x | 99.0 | 72.3 | 352.3 | 25/25 |
| [Decision Advisor](../../examples/terminal-output-only/decision-advisor/outputs/compiled-prompt.md) | 274 | 157 | 803 | 2.93x | 48.25 | 60.1 | 176.1 | 23/25 |
| [Investment Brief](../../examples/saved-artifact-workflows/investment-brief/outputs/compiled-prompt.md) | 191 | 42 | 731 | 3.83x | 52.5 | 71.8 | 274.9 | 24/25 |
| [Deep Summary](../../examples/terminal-output-only/deep-summary/outputs/compiled-prompt.md) | 205 | 179 | 1005 | 4.9x | 57.5 | 57.2 | 280.5 | 24/25 |
| [Messy Notes Action Plan](../../examples/terminal-output-only/messy-notes-action-plan/outputs/compiled-prompt.md) | 258 | 211 | 1058 | 4.1x | 67.0 | 63.3 | 259.7 | 25/25 |
| [Prompt Refiner](../../examples/terminal-output-only/prompt-refiner/outputs/compiled-prompt.md) | 205 | 98 | 635 | 3.1x | 45.5 | 71.7 | 222.0 | 22/25 |

## Detailed rubric

### Program Review Checklist

- **Intention:** Produce a practical review checklist tailored to a programming project.
- **Source:** [program-review-checklist.weavemark.md](../../promplets/catalog/standalone/program-review-checklist.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/program-review-checklist/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 5/5 | Matches 5/5 expected intent terms. |
| Completeness | 4/5 | Compiled output has 788 words. |
| Writing and structure | 5/5 | Uses 5 headings and 24 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 4 directive verbs and 24 bullets. |

### Program Debugging Assistant

- **Intention:** Produce a debugging assistant prompt that diagnoses behavior from evidence.
- **Source:** [program-debugging-assistant.weavemark.md](../../promplets/catalog/standalone/program-debugging-assistant.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/program-debugging-assistant/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 5/5 | Matches 5/5 expected intent terms. |
| Completeness | 4/5 | Compiled output has 948 words. |
| Writing and structure | 5/5 | Uses 14 headings and 28 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 5 directive verbs and 28 bullets. |

### Learning Tutor

- **Intention:** Produce an adaptive tutor prompt grounded in learner context and practice.
- **Source:** [learning-tutor.weavemark.md](../../promplets/catalog/standalone/learning-tutor.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/learning-tutor/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 3/5 | Matches 3/5 expected intent terms. |
| Completeness | 4/5 | Compiled output has 942 words. |
| Writing and structure | 5/5 | Uses 6 headings and 39 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 5 directive verbs and 39 bullets. |

### Research Brief

- **Intention:** Produce a research brief prompt with source expectations and caveats.
- **Source:** [research-brief.weavemark.md](../../promplets/catalog/standalone/research-brief.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/research-brief/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 5/5 | Matches 5/5 expected intent terms. |
| Completeness | 5/5 | Compiled output has 1370 words. |
| Writing and structure | 5/5 | Uses 9 headings and 57 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 5 directive verbs and 57 bullets. |

### Decision Advisor

- **Intention:** Produce a decision-advice prompt with options, tradeoffs, and uncertainty.
- **Source:** [decision-advisor.weavemark.md](../../promplets/catalog/standalone/decision-advisor.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/decision-advisor/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 4/5 | Matches 4/5 expected intent terms. |
| Completeness | 4/5 | Compiled output has 803 words. |
| Writing and structure | 5/5 | Uses 8 headings and 46 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 6 directive verbs and 46 bullets. |

### Investment Brief

- **Intention:** Produce an educational investment brief with evidence, risks, alternatives, and decision triggers.
- **Source:** [investment-brief.weavemark.md](../../promplets/catalog/standalone/investment-brief.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/saved-artifact-workflows/investment-brief/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 5/5 | Matches 5/5 expected intent terms. |
| Completeness | 4/5 | Compiled output has 731 words. |
| Writing and structure | 5/5 | Uses 0 headings and 34 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 4 directive verbs and 34 bullets. |

### Deep Summary

- **Intention:** Produce a deep-summary prompt that preserves structure and audience needs.
- **Source:** [deep-summary-prompt.weavemark.md](../../promplets/catalog/standalone/deep-summary-prompt.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/deep-summary/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 4/5 | Matches 4/5 expected intent terms. |
| Completeness | 5/5 | Compiled output has 1005 words. |
| Writing and structure | 5/5 | Uses 13 headings and 41 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 6 directive verbs and 41 bullets. |

### Messy Notes Action Plan

- **Intention:** Turn messy notes into an organized action plan.
- **Source:** [messy-notes-action-plan.weavemark.md](../../promplets/catalog/standalone/messy-notes-action-plan.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/messy-notes-action-plan/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 5/5 | Matches 5/5 expected intent terms. |
| Completeness | 5/5 | Compiled output has 1058 words. |
| Writing and structure | 5/5 | Uses 8 headings and 43 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 5 directive verbs and 43 bullets. |

### Prompt Refiner

- **Intention:** Produce a prompt-improvement prompt that preserves intent and improves clarity.
- **Source:** [prompt-refiner.weavemark.md](../../promplets/catalog/standalone/prompt-refiner.weavemark.md)
- **Output:** [compiled-prompt.md](../../examples/terminal-output-only/prompt-refiner/outputs/compiled-prompt.md)

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 4/5 | Matches 4/5 expected intent terms. |
| Completeness | 3/5 | Compiled output has 635 words. |
| Writing and structure | 5/5 | Uses 9 headings and 31 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 5 directive verbs and 31 bullets. |
