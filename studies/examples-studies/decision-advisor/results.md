# Decision Advisor Example Study

[View as HTML](results.html)

## Intention

Produce a decision-advice prompt with options, tradeoffs, and uncertainty.

## Metrics

| Example | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield | Rubric |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Decision Advisor](../../../examples/terminal-output-only/decision-advisor/outputs/compiled-prompt.md) | 274 | 157 | 803 | 2.93x | 48.25 | 60.1 | 176.1 | 23/25 |

## Rubric

| Criterion | Score | Rationale |
|---|---:|---|
| Intention fit | 4/5 | Matches 4/5 expected intent terms. |
| Completeness | 4/5 | Compiled output has 803 words. |
| Writing and structure | 5/5 | Uses 8 headings and 46 bullet rows. |
| No leakage/pathologies | 5/5 | Detected 0 internal leaks and 0 pathology markers. |
| Direct usefulness | 5/5 | Instruction/action signal combines 6 directive verbs and 46 bullets. |
