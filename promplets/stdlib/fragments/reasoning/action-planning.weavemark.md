@promplet version: 0.7

@module weavemark.std.reasoning.action_planning

# Action Planning

@note
  Reusable layer for converting analysis or normalized notes into an executable,
  reviewable action plan.

Use this layer when the final answer should help someone decide what to do next,
who should do it, what depends on what, and how progress will be checked.

## Action-planning obligations

- Separate tasks, decisions, risks, open questions, and background information.
- Prefer concrete next actions over vague intentions.
- Attach an owner, sequence, due window, dependency, or trigger whenever the
  source material supports it.
- Distinguish committed actions from suggested actions.
- Flag actions that need confirmation before execution.
- Keep the first next step small enough to start immediately.
- Include validation: how the user will know the action worked.
- Include escalation or review points for high-risk or blocked work.

## Required action-plan shape

When applicable, include:

1. **Immediate next step** — the smallest useful action to take now.
2. **Action table** with columns for action, owner, priority, timing,
   dependency, and definition of done.
3. **Decision list** — decisions needed, decision owner, deadline, and input
   needed.
4. **Risk register** — risk, impact, mitigation, and trigger.
5. **Open questions** — questions that block or materially change the plan.
6. **Review cadence** — when to revisit the plan and what evidence to inspect.
