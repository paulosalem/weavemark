@promplet version: 0.7

# Support Ticket Prompt Pack

This WeaveMark program compiles one source into a small support-triage prompt
pack. The primary output explains the pack, while `@emit` writes each concrete
prompt artifact to its own file.

@emit file: prompts/system.md
  You are a support triage assistant for @{product_name}.

  Work in a @{tone} tone. Separate what is known from what must be confirmed.
  Never promise refunds, security changes, account actions, or delivery dates
  unless the escalation policy explicitly permits them.

  Escalation policy:
  @{escalation_policy}

@emit file: prompts/user.md
  Triage this support scenario for @{product_name}.

  Scenario:
  @{support_scenario}

  Produce:
  1. A one-sentence issue summary
  2. Severity: low, medium, high, or urgent
  3. The most likely customer goal
  4. Clarifying questions, if any
  5. A draft first response to the customer
  6. Whether escalation is required and why

@emit file: review/checklist.md
  Before using the draft response, verify:

  - It follows the requested @{tone} tone.
  - It does not exceed the escalation policy.
  - It asks only necessary clarifying questions.
  - It gives the customer a concrete next step.
