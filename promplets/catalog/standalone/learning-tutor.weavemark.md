@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst mingle: true
@refine module:weavemark.std.reasoning.learner_model mingle: true
@refine module:weavemark.std.guidelines.context_sufficiency mingle: true
@refine module:weavemark.std.lenses.explainability mingle: true

# Learning Tutor Prompt

@note
  Final prompt for a paste-ready tutoring instruction that adapts explanation,
  examples, practice, and checks to the learner.

Teach me **@{topic}**.

## Learning goal

@{learning_goal}

## My current context

@{learner_context}

## Preferred style

@{preferred_style}

## Time available

@{time_available}

## Desired depth

@{desired_depth}

## Required behavior

- Infer my current level only from the context I supplied.
- If key prerequisites are missing, identify the smallest prerequisite path.
- Explain in layers: intuition, precise concept, worked example, edge cases.
- Use analogies only when they clarify, and say where the analogy breaks.
- Surface likely misconceptions and how to avoid them.
- Check understanding before moving to advanced material.
- If my goal is too broad for the available time, prioritize the highest-value
  learning path.

## Required output

1. **Assumed learner model** — level, goal, constraints, and missing context.
2. **Learning map** — prerequisites and the path through the topic.
3. **Core explanation** — plain-language intuition plus precise terms.
4. **Worked example** — one example carried through step by step.
5. **Misconceptions** — common traps and corrections.
6. **Quick check** — 3 questions to test understanding.
7. **Practice plan** — one warm-up, one applied exercise, and one stretch task.
8. **Next step** — the smallest useful thing to study or try next.
