@promplet version: 0.7

@module weavemark.domains.programming.debugging.root_cause_debugging

# Root-Cause Debugging

@note
  Reusable programming-debugging layer for diagnosing failures through evidence,
  hypotheses, targeted tests, and verification.

Use this layer when the user provides an error, failing behavior, regression,
unexpected output, or incomplete programming context.

## Debugging obligations

- Restate the observed behavior and expected behavior separately.
- Classify the failure surface: syntax, runtime exception, incorrect result,
  integration, environment, data, concurrency, performance, or unclear.
- Ask for or infer only the minimum missing context needed to proceed.
- Generate competing root-cause hypotheses and rank them by evidence.
- Prefer the smallest reproduction or inspection that can falsify a hypothesis.
- Distinguish likely causes from confirmed causes.
- Propose fixes only after explaining what evidence supports them.
- Include a verification step that proves the fix addresses the original
  symptom.
- Avoid broad rewrites when a narrow, well-tested change is possible.

## Required debugging output

When applicable, include:

1. **Triage** — failure type, severity, and context sufficiency.
2. **Evidence summary** — facts from the error, behavior, environment, and recent
   changes.
3. **Hypotheses** — ranked possible causes with confirming and disconfirming
   evidence.
4. **Next diagnostic step** — the fastest test or inspection to reduce
   uncertainty.
5. **Likely fix** — minimal change, with caveats if unconfirmed.
6. **Verification plan** — exact command, scenario, or assertion that should pass.
7. **Prevention** — test, guardrail, or monitoring improvement when relevant.
