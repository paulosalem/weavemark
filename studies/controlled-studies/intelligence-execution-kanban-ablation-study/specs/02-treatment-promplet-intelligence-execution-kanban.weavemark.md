# @{app_name}: WeaveMark Work-Intelligence Treatment

@compress "Produce a dense implementation spec; preserve structure and every hard requirement."
  @refine programming/foundations/software-spec
  @refine programming/stacks/stack-typescript-nextjs-prisma-sqlite
  @refine programming/types/type-local-first-webapp
  @refine domains/work-intelligence/topic-intelligence-monitor mingle: true
  @refine domains/work-intelligence/signal-to-action-workflow mingle: true
  @refine domains/work-intelligence/idea-execution-workspace mingle: true
  @refine programming/modules/module-local-sqlite-storage mingle: true
  @refine programming/modules/module-card mingle: true
  @refine programming/modules/module-workflow-board mingle: true
  @refine programming/modules/module-output-surfaces mingle: true
  @refine programming/modules/module-activity-stream mingle: true
  @refine programming/modules/module-dashboard mingle: true
  @refine programming/modules/module-notifications mingle: true
  @refine programming/modules/module-ai-features mingle: true
  @refine programming/modules/module-rest-api mingle: true
  @refine programming/modules/module-realtime mingle: true
  @refine programming/validation/playwright-mcp-browser-validation

  Design @{app_name}: a focused local-first Kanban that converts monitored
  signals into reviewed cards, decisions, actions, delegations, outputs, alerts,
  and updated watch rules.

  Monitor: @{topic_families}

  @expand mode: intention focus: "one product-shaped signal -> card -> decision/action/delegation -> output -> alert/watch-rule loop"
    Specify the first-build workflow, not a generic platform anthology. Every
    architecture, schema, UI, AI, API, realtime, and validation detail must name
    the exact work-intelligence entity or transition it supports. Prefer dense
    tables and concrete field/state lists over broad platform prose. Reusable
    storage, card, board, output, activity, dashboard, notification, AI, API,
    realtime, and browser-validation layers must be transformed into this
    lifecycle rather than appended as standalone reusable-module sections.

  Required output: one concise implementation specification with sections for
  first-build scope, local workspace/storage, signal/card/decision/delegation/
  output domain model, board lifecycle, monitoring triage, UI surfaces,
  automation guardrails, failure states, and acceptance proof for a complete
  signal-to-output session.
