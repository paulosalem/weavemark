@promplet version: 0.7

@module weavemark.std.guidelines.release_evidence_quality

# Release Evidence Quality

@note
  Reusable guideline for judging whether release claims are backed by concrete,
  inspectable evidence instead of optimism.

Use this guideline when release work must assess release readiness,
public-launch quality, demo credibility, or validation completeness.

## Evidence obligations

- Separate claimed readiness from verified readiness.
- Link every readiness claim to evidence type: passing command, inspected output,
  screenshot, trace, source review, user-flow run, package artifact, security
  check, documentation review, or explicit waiver.
- Record evidence freshness, environment, scope, and limitations.
- Treat "not checked", "not reproducible", "unknown", and "waived" as distinct
  states.
- Flag evidence that is stale, partial, proxy-only, manually asserted, or tied to
  a different version.
- Preserve failed checks and unresolved caveats rather than smoothing them into
  success language.
- Require release notes to distinguish verified behavior from known limitations.

## Evidence quality levels

- **Verified:** current artifact or command directly proves the claim.
- **Partial:** evidence covers only some paths, platforms, or scenarios.
- **Proxy:** evidence is related but does not directly prove the release claim.
- **Waived:** decision-maker accepted the risk explicitly.
- **Missing:** no evidence yet.
- **Stale:** evidence exists but predates relevant changes.
