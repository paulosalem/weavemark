## Release-readiness domain template

- The product should transform messy release material into release candidates,
  gates, evidence items, validation checks, docs/example readiness, risks,
  blockers, waivers, actions, release notes, decisions, exports, and post-launch
  monitoring records.
- Release gates should cover product behavior, documentation, examples, tests,
  build/package/install, security/privacy, accessibility, performance, rollback,
  support, migration notes, and release communication.
- Gate states should include not started, collecting evidence, ready, ready with
  caveat, blocked, waived, deferred, and not applicable.
- Evidence items should record type, source path or URL, command or flow,
  environment, artifact reference, freshness, scope, reviewer, quality,
  limitations, linked claim, and release impact.
- Critical gates should block release unless explicitly waived with rationale,
  owner, approver, expiry, accepted risk, and revisit trigger.
- Validation checks need expected proof, owner, status, last run, failure meaning,
  rerun requirement, release impact, and supersession history.
- Failed validation should create actions while preserving failed evidence until
  a passing rerun supersedes it.
- Release decisions should support ship, ship with caveat, wait, fix first,
  defer scope, rollback, or cancel.
- Release notes should distinguish verified behavior, known limitations,
  deferred work, migration notes, support guidance, and rollback/monitoring
  expectations.
- Apply release readiness to these surfaces: {{release_surfaces}}
