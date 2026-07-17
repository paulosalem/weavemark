@promplet version: 0.7

@module weavemark.domains.product.release_artifact_readiness

# Release Artifact Readiness

@note
  Reusable product layer for treating public-facing release materials as
  evidence-bearing artifacts rather than informal launch prose.

Use this layer when documentation, examples, generated outputs, prompts,
packages, demos, release notes, screenshots, traces, or support materials must be
ready for a public release.

## Artifact readiness obligations

- Represent every public artifact with audience, purpose, owner, status,
  evidence, freshness, risk, dependency, and release impact.
- Distinguish drafts, verified artifacts, stale artifacts, waived artifacts,
  deferred artifacts, and blocked artifacts.
- Tie each artifact claim to validation evidence, reviewer notes, screenshots,
  traces, command output, inspected generated output, or an explicit waiver.
- Track docs gaps, example readiness, prompt quality, generated-output quality,
  packaging status, demo readiness, release-note accuracy, and support guidance.
- Prevent public claims from being marked ready when context is insufficient,
  evidence is stale, or validation covers only a proxy path.
- Preserve known limitations and deferred work so release notes do not turn
  caveats into success language.

## Required artifact surfaces

When applicable, include:

1. **Artifact inventory** - each public artifact, owner, audience, status,
   evidence, and release impact.
2. **Docs and examples readiness** - gaps, validation proof, screenshots/traces,
   and first-user success criteria.
3. **Public-claim ledger** - release-note and README claims with evidence,
   caveats, and reviewer sign-off.
4. **Artifact action queue** - missing evidence, stale docs, broken examples,
   weak prompts, package problems, and follow-up owners.
5. **Release-note guardrails** - verified behavior, known limitations, deferred
   work, migration notes, and support guidance.
