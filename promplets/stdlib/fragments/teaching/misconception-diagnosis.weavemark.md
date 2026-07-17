@promplet version: 0.7

@module weavemark.std.teaching.misconception_diagnosis

# Misconception Diagnosis

@note
  Reusable teaching layer for finding and repairing conceptual misunderstandings.

Use this layer when teaching should infer why a learner is stuck and respond
with targeted repair rather than generic explanation.

## Diagnosis obligations

- Separate symptom from cause: a wrong answer may come from notation, vocabulary,
  missing prerequisite, false analogy, arithmetic slip, or conceptual inversion.
- Ask for the learner's reasoning when the error source is ambiguous.
- Name the misconception only after evidence supports it.
- Explain why the misconception is tempting.
- Provide a minimal contrast case that separates the misconception from the
  correct concept.
- Use one repair exercise immediately after the correction.
- Track whether the repair worked before moving to harder material.

## Required diagnosis surface

When applicable, include:

1. **Observed clue** - what in the learner response suggests the issue.
2. **Likely misconception** - with confidence and uncertainty.
3. **Why it happens** - the attractive but wrong mental shortcut.
4. **Contrast example** - a small case where the wrong model fails.
5. **Repair prompt** - a learner action that rebuilds the correct model.
6. **Verification question** - a quick check that the repair transferred.
