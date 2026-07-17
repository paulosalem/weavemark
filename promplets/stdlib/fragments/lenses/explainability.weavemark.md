@promplet version: 0.7

@module weavemark.std.lenses.explainability

# Explainability Lens

@note
  Reusable lens for viewing an answer through traceable reasoning,
  assumptions, evidence, calculations, and limits.

Use this lens for conclusions, model outputs, recommendations, analyses, or
generated artifacts when the user needs to understand why an answer is
justified.

## Required output

Start with the conclusion, then show the reasoning chain:

| Step | Claim or inference | Evidence or basis | Confidence |
| --- | --- | --- | --- |
| 1 | claim | source, calculation, assumption, or observation | low/medium/high |

Then include:

- **Key assumptions:** assumptions the conclusion depends on.
- **Checks performed:** calculations, comparisons, tests, or source checks actually used.
- **Limits:** what remains uncertain, unverified, or outside scope.
- **Simplest explanation:** a plain-language version a non-specialist can inspect quickly.
