# Study: Learning Tutor Refinement

This study tests whether `@refine`, `@expand`, `@match`, and `@if` can turn a
short learning request into a coherent adaptive tutoring prompt.

The target task is a pasteable chat prompt for learning linear algebra through
geometric intuition, Socratic questioning, misconception diagnosis, practice,
and delayed review.

## Variants

| Variant | File | Purpose |
|---|---|---|
| Compact manual | [`specs/00-control-compact-manual-linear-algebra-tutor.weavemark.md`](specs/00-control-compact-manual-linear-algebra-tutor.weavemark.md) | Names the tutor goal but leaves pedagogy implicit. |
| Matched prose | [`specs/01-control-matched-prose-linear-algebra-tutor.weavemark.md`](specs/01-control-matched-prose-linear-algebra-tutor.weavemark.md) | Writes the intended pedagogy manually without directives. |
| Refined + expanded | [`specs/02-treatment-refined-expand-linear-algebra-tutor.weavemark.md`](specs/02-treatment-refined-expand-linear-algebra-tutor.weavemark.md) | Uses reusable teaching refinements, concept expansion, learner-profile branching, and delayed-review branching. |

## Key result

The WeaveMark variant is the strongest single-prompt result in this batch. It
uses fewer local words than the matched-prose baseline, activates 97 reusable
fragment lines, and compiles into a 2,344-word tutor prompt with concrete first
interaction, adaptive branches, diagnosis rules, practice ladder, and review
cards.

See [`results/ablation-summary.md`](results/ablation-summary.md) and
[`results/final-quality-analysis.md`](results/final-quality-analysis.md).
