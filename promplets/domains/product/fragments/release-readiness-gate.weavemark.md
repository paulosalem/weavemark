@promplet version: 0.7

@module weavemark.domains.product.release_readiness_gate

# Release Readiness Gate

@note
  Reusable product layer for turning launch preparation into explicit gates,
  evidence, owners, blockers, and go/no-go decisions.

Use this layer when a product, prompt, workflow, library, or example must become
credible enough for a public release.

## Release gate obligations

- Define release tracks such as product behavior, documentation, examples,
  tests, packaging, security/privacy, performance, support, and rollback.
- Represent each gate with owner, status, evidence, blocker, risk, decision,
  due date, and confidence.
- Distinguish "ready", "ready with caveat", "needs fix", "defer", and
  "not applicable".
- Require objective evidence before a gate can be marked ready.
- Tie every blocker to a concrete action, owner, verification step, and release
  consequence.
- Preserve decisions that intentionally defer work, including rationale and
  revisit trigger.
- Include a final release-readiness review that explains go, no-go, or limited
  release.

## Required release surfaces

When applicable, include:

1. **Gate matrix** - release areas, criteria, evidence, owner, status, and
   blocker.
2. **Evidence ledger** - commands, screenshots, outputs, audits, docs, examples,
   and review notes that support release claims.
3. **Risk register** - severity, likelihood, impact, mitigation, owner, and
   release decision.
4. **Action board** - fixes, docs, validation tasks, packaging tasks, reviews,
   and deferred follow-ups.
5. **Decision record** - why the release is ready, limited, blocked, or deferred.
