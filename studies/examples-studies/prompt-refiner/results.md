# Prompt Refiner Example Study

[View as HTML](results.html)

## Intention

Produce a prompt-improvement prompt that preserves intent and improves clarity.

## Metrics

| Example | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield | Rubric |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Prompt Refiner](../../../examples/terminal-output-only/prompt-refiner/outputs/compiled-prompt.md) | 205 | 98 | 635 | 3.1x | 45.5 | 71.7 | 222.0 | 22/25 |

## Rubric

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 4/5 | Matches 4/5 expected intent terms. |
| Completeness | 3/5 | Compiled output has 635 words. |
| Writing and structure | 5/5 | Uses 9 headings and 31 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 5 directive verbs and 31 bullets. |
