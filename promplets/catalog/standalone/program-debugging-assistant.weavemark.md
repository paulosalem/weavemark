@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst mingle: true
@refine module:weavemark.std.guidelines.context_sufficiency mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true
@refine module:weavemark.std.analysis.ach_core mingle: true
@refine module:weavemark.domains.programming.debugging.root_cause_debugging mingle: true

# Program Debugging Assistant Prompt

@note
  Final prompt for a paste-ready programming debugging instruction that drives a
  chat assistant toward root cause, targeted diagnostics, and verification.

Help me debug this programming problem.

## Language or stack

@{language_or_stack}

## Problem summary

@{problem_summary}

## Expected behavior

@{expected_behavior}

## Observed behavior

@{observed_behavior}

## Error output

Preserve this exact error output as a fenced text block in the prompt:

```text
@{error_output}
```

## Relevant program text

Preserve this exact program text as a fenced text block in the prompt:

```text
@{relevant_program_text}
```

## Environment and recent changes

@{environment_and_recent_changes}

## Attempts so far

@{attempts_so_far}

## Constraints

@{constraints}

## Required behavior

- Restate expected and observed behavior separately.
- Classify the failure surface before proposing fixes.
- If context is insufficient, ask only the highest-value missing questions and
  still provide a bounded diagnostic path.
- Generate competing root-cause hypotheses and rank them by evidence.
- Identify what evidence would confirm or disconfirm each hypothesis.
- Prefer the smallest diagnostic step that reduces uncertainty.
- Propose a minimal fix only after explaining why it is likely.
- Include a verification step that proves the original symptom is gone.

## Required output

When quoting error output or program text, use proper fenced blocks. Do not add
standalone format labels such as `text`, `python`, `markdown`, or `json`.

1. **Triage** — failure type, severity, and context status.
2. **Evidence summary** — facts from the error, behavior, environment, and
   attempts.
3. **Ranked hypotheses** — likely root causes with supporting and contrary
   evidence.
4. **Next diagnostic step** — exact inspection, command, or experiment to run.
5. **Likely fix** — smallest change to try, with caveats if not confirmed.
6. **Verification plan** — how to prove the fix worked.
7. **Prevention** — test, guardrail, or monitoring improvement if relevant.
