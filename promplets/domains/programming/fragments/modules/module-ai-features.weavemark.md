@promplet version: 0.7

@module weavemark.domains.programming.modules.ai_features

# Module: Inspectable AI Features

Use this module when a product delegates classification, extraction, synthesis,
ranking, drafting, or recommendation work to a model.

## Capability contract

- Define each AI feature as a bounded user outcome with explicit inputs, output
  schema, confidence/evidence expectations, and failure behavior.
- Keep provider/model selection in host configuration, not in user data.
- Send only parameters supported by the resolved model and provider.
- Centralize retries, timeouts, budgets, and rate limits in the LLM client layer;
  feature code MUST NOT invent independent retry loops.
- Prefer deterministic parsing, filtering, retrieval, and exact matching before
  asking a model to make a subjective judgment.

## Evidence and review

- Classification, ranking, and recommendations MUST retain the evidence or
  rationale needed for human review.
- Distinguish model output from verified facts and deterministic calculations.
- High-impact actions require explicit confirmation; a model suggestion never
  silently approves, publishes, deletes, spends, or changes permissions.
- Record model identity, request purpose, timestamps, latency, token usage, and
  provider-reported cost where available.
- Let users correct a result and preserve the correction as product state rather
  than quietly retraining or rewriting history.

## Data and privacy

- Minimize model input to fields required for the feature.
- Detect or redact sensitive fields according to an explicit product policy;
  never claim generic sanitization makes arbitrary user data safe.
- Do not use customer content for training unless the user has explicitly opted
  into a documented provider/data policy.
- Keep secrets, credentials, private attachments, and unrelated historical data
  out of prompts.
- Make remote processing visible and provide a non-AI or local-only path when the
  core product can reasonably degrade.

## Reliability

- Validate structured responses against a closed schema and reject malformed,
  incomplete, or out-of-policy output.
- Set an explicit tool/call/iteration budget and surface partial state when the
  budget is exhausted.
- Show useful loading, unavailable, timeout, blocked-policy, and retry states.
- Cache only when the request inputs, relevant configuration, and source data
  identify an equivalent task.
- Avoid duplicate model work when a deterministic fingerprint or prior accepted
  result already satisfies the request.

## Acceptance criteria

An AI feature is complete when its purpose, inputs, outputs, evidence,
permissions, budgets, privacy boundary, correction path, degraded behavior, and
observability are all testable without relying on hidden provider behavior.
