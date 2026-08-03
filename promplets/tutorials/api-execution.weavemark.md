@promplet version: 0.7

@execute single-call

# Decision note

Write a concise decision note about @{topic}.

Context:

@{context}

@output enforce: strict
  Return exactly these sections:
  1. Decision
  2. Evidence
  3. Uncertainty
  4. Next action

@assert contains: "Uncertainty"
@assert contains: "Next action"
