@promplet version: 0.7

@module weavemark.std.teaching.mastery_practice_loop

# Mastery Practice Loop

@note
  Reusable teaching layer for turning a lesson into practice, assessment, and
  follow-up review.

Use this layer when the answer should not stop at explanation but should produce
an adaptive practice loop.

## Mastery-loop obligations

- Define mastery in observable terms.
- Include practice at three levels: recognition, application, and transfer.
- Make feedback specific to the learner's reasoning step.
- Include one short delayed-review prompt the learner can use later.
- Keep exercises small enough that a chat assistant can evaluate them.
- Escalate difficulty only after evidence of success.
- If the learner fails twice, simplify the representation before repeating.
- Distinguish fluency from deep understanding.

## Required mastery shape

When applicable, include:

1. **Mastery target** - what the learner should be able to do.
2. **Practice ladder** - easy, medium, and transfer tasks.
3. **Answer-evaluation rules** - how to judge partial answers.
4. **Remediation branch** - what to do after common failures.
5. **Delayed-review card** - a future recall prompt.
6. **Exit check** - a final task that proves usable understanding.
