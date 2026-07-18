@promplet version: 0.7
@compile format: markdown

@emit file: "product-brief.md"
  # @{product_name} product brief

  Product promise:
  Help @{primary_users} make safer release decisions.

  The brief must explain:
  - the release readiness problem
  - the user roles
  - the go/no-go decision moment
  - the evidence each decision must cite
  - the top risk: @{release_risk}

@emit file: "implementation-spec.md"
  @refine module:weavemark.domains.programming.foundations.software_spec mingle: true
  @refine module:weavemark.domains.programming.stacks.typescript_nextjs_prisma_sqlite mingle: true
  @refine module:weavemark.domains.programming.validation.release_validation_matrix mingle: true

  # @{product_name} implementation specification

  Build a local-first web app with:
  - release dashboard
  - validation run detail page
  - risk and waiver queue
  - screenshot evidence gallery
  - go/no-go decision record

  @match release_stage
    "alpha" ==>
      Optimize for pilot users, fast correction, and visible defects.
    "public" ==>
      Optimize for support readiness, auditability, and release confidence.

  @if include_ai_review
    Add an AI review assistant that proposes issues, never approves release,
    and always requires human confirmation.

  @if include_audit_trail
    Persist immutable audit events for approvals, waivers, validation runs,
    comments, attachments, and decision changes.

@emit file: "acceptance-checklist.md"
  # Acceptance checklist

  The implementation is ready when:
  - every release has a visible readiness state
  - every failed validation links to evidence
  - every waiver records owner, reason, and expiry
  - go/no-go decisions cite risks and validation runs
  - local data survives restart and can be exported
  - no AI-suggested review can bypass human approval
