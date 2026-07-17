@promplet version: 0.7
@refine module:weavemark.domains.programming.foundations.software_spec mingle: true
@refine module:weavemark.domains.programming.stacks.typescript_nextjs_prisma_sqlite mingle: true
@refine module:weavemark.domains.product.release_readiness_gate mingle: true
@refine module:weavemark.domains.product.product_validation_surface mingle: true

# Release readiness workbench

Design @{product_name}, a local-first command center for
release notes, validation runs, screenshots, risks, waivers,
and go/no-go decisions.

Primary users: @{primary_users}
Critical release risk: @{release_risk}

@match release_stage
  "alpha" ==>
    Prioritize pilot feedback, bug capture, and rollback.
  "public" ==>
    Prioritize support readiness, documentation, and observability.

@if include_ai_review
  Add an AI-assisted review queue with human approval gates.

@if include_audit_trail
  Add immutable release events for approvals, waivers, validation runs,
  screenshot evidence, and rollback decisions.

@output enforce: strict
  Return these sections:
  1. Product promise
  2. User roles and permissions
  3. Screens and core workflows
  4. Data model
  5. Local-first persistence rules
  6. AI review behavior
  7. Release gate logic
  8. Acceptance criteria
  9. Validation plan

@assert includes: "Acceptance criteria"
@assert includes: "Local-first persistence"
