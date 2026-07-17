# @{app_name}: WeaveMark Single-Output Release Readiness Spec

@compress "Produce a dense implementation spec; preserve structure and every hard requirement."
  @refine programming/foundations/software-spec
    Mingle refinements into one release workspace; no appendices.

  @refine programming/stacks/stack-typescript-nextjs-prisma-sqlite
  @refine programming/types/type-local-first-webapp

  Design @{app_name}: a local-first release command center that turns messy
  release material into gates, evidence, validation, risks, actions, notes, and
  go/no-go records. Produce one implementation spec only.

  @expand mode: intention focus: "gate -> evidence -> validation -> decision -> launch audit"
    Release notes, docs, examples, validation commands, screenshots, package
    artifacts, risks, waivers, and confidence.

  ## Gates and evidence

  @refine product/release-readiness-gate
    Release readiness is the central domain model.
  @refine guidelines/release-evidence-quality
  @refine programming/validation/release-validation-matrix
  @refine programming/validation/playwright-mcp-browser-validation

  ## Inputs and artifacts

  @refine reasoning/unstructured-input-normalization
    Messy material becomes structured release facts.
  @refine product/release-artifact-readiness
    Apply to @{release_surfaces}.
  @refine guidelines/prompt-quality
  @refine guidelines/context-sufficiency
  @refine guidelines/evidence-quality

  ## Decisions and actions

  @refine decision/strategy-selection
  @refine decision/forecast-uncertainty
  @refine decision/values-tradeoff
  @refine lenses/decision-gate
  @refine reasoning/action-planning
    Gaps, failed checks, risks, blockers, and waivers become owned actions.

  ## Workspace and UI

  @refine programming/modules/module-card
  @refine programming/modules/module-workflow-board
  @refine programming/modules/module-output-surfaces
  @refine programming/modules/module-dashboard
  @refine programming/modules/module-notifications
  @refine programming/modules/module-activity-stream
  @refine programming/modules/module-local-sqlite-storage
  @refine programming/modules/module-ai-features
    Evidence-link every material AI claim.
  @refine programming/modules/module-rest-api
  @refine programming/modules/module-realtime
  @refine programming/debugging/root-cause-debugging
    Failed checks become diagnose, fix, retest, and prevention loops.
  @refine product/product-validation-surface
    Prove messy import -> gate -> validation -> fix/rerun -> note -> decision
    -> audit export.

  ## Required output

  Produce one implementation spec covering architecture, local storage, release
  gates, validation, evidence, artifacts, risks, waivers, decisions, board,
  outputs, dashboards, notifications, APIs, events, AI rules, privacy,
  root-cause loops, release notes, rollback/monitoring, failures, scripts, and
  acceptance.
