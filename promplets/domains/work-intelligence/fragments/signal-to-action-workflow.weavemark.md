@promplet version: 0.7

@module weavemark.domains.work_intelligence.signal_to_action_workflow

# Signal-to-Action Workflow

@note
  Reusable bridge layer for applications that transform incoming information
  signals into concrete ideas, decisions, delegations, and project outputs.

Use this layer when neither "news monitor" nor "task board" is sufficient on its
own: the product must preserve the path from information input to work output.

## Unified flow

- Model the flow from signal intake to triage, interpretation, idea creation,
  decision, delegation, execution, review, output, and archival.
- A signal may become an insight, idea, task, question, watch item, warning,
  decision input, delegation, project risk, or output artifact.
- An idea may link back to many signals and forward to many actions or outputs.
- A completed output SHOULD record which signals, ideas, decisions, and actions
  contributed to it.

## Structural mingling obligations

- When mingled with a board or card interface, reinterpret cards as mixed work
  intelligence objects rather than generic tasks.
- Board stages SHOULD reflect the information-to-execution lifecycle: intake,
  triage, investigate, decide, execute, waiting, review, shipped, watch later,
  and archived.
- Card metadata SHOULD include relevance, novelty, confidence, source family,
  actionability, owner, next step, status evidence, and output linkage where
  meaningful.
- Board metrics SHOULD include signal volume, conversion rate, stale ideas,
  delegated work awaiting response, high-confidence warnings, decisions pending,
  and outputs produced from monitored topics.

## Suggestions and automation

- Suggest next actions from signals, but label suggestions separately from
  committed work.
- Suggest merging duplicates, linking related items, escalating warnings,
  creating follow-up reminders, or converting insights into project outputs.
- Automation MUST remain inspectable: show trigger, inputs, confidence, action
  proposed or taken, and how the user can undo or tune it.

## Output accountability

- The system SHOULD answer: "What came in?", "Why did it matter?", "What did I
  decide?", "Who is doing what?", "What is blocked?", "What changed because of
  this?", and "Which outputs did this produce?"
- Summary views SHOULD connect input monitoring with project execution instead
  of presenting news, ideas, and tasks as isolated modules.
- Acceptance criteria MUST include end-to-end proof that at least one monitored
  signal becomes an idea, then an action or delegation, then a visible output or
  deliberate archive decision.
