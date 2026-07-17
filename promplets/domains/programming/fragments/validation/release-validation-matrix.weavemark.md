@promplet version: 0.7

@module weavemark.domains.programming.validation.release_validation_matrix

# Release Validation Matrix

@note
  Reusable programming-validation layer for turning a release candidate into a
  matrix of commands, user flows, artifacts, environments, and gates.

Use this layer when an implementation specification should make release-readiness proof obligations explicit for the implementation agent.

## Validation matrix obligations

- Define validation rows for unit, integration, type, lint, build, packaging,
  install, browser or UI, example, documentation, migration, import/export,
  performance, accessibility, security/privacy, and rollback checks as relevant.
- For each row, record command or manual flow, environment, expected evidence,
  owner, status, failure meaning, and fix loop.
- Include first-run, repeated-run, upgrade, downgrade/rollback, offline, corrupt
  state, missing dependency, and partial-failure cases when applicable.
- Require validation evidence to be saved or referenced in the release workspace.
- Include a release-blocking rule for critical checks and an explicit waiver path
  for accepted non-critical risks.
- Require rerunning affected checks after fixes and preserving history of failed
  and passed attempts.

## Required validation output

When applicable, include:

1. **Validation matrix** with check, scope, command or flow, expected proof,
   current status, owner, and release impact.
2. **Failure triage loop** that turns failed checks into root-cause hypotheses,
   fixes, retests, and prevention tasks.
3. **Evidence retention rules** for logs, screenshots, traces, reports, package
   artifacts, and generated outputs.
4. **Release decision rules** that define when the candidate can ship, ship with
   caveats, or must stop.
