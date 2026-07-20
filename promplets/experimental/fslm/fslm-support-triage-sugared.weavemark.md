@promplet version: 0.7

@use weavemark.experimental.fslm exposing machine state transition input guard action

@execute fslm
  machine: support_triage
  max_steps: 4
  prompt_contract: strict

@bind search_docs language: python from: "./companions/support_triage.py" symbol: search_docs
@bind send_message language: python from: "./companions/support_triage.py" symbol: send_message

# FSLM Support Triage with Inline Machine

You are the language layer for a finite-state support triage machine.
Use the current state, transition description, guards, action results, tool
plans, and event payload as the source of truth.

@tool search_docs
  Search product documentation.
  - query: string (required) - Search query.
  - max_results: integer default: 5 - Maximum results.

@tool send_message
  Send a message to the user.
  - text: string (required) - Message body.

@machine support_triage initial: triage
  Prompt-backed support workflow with explicit event-driven transitions.

  @state triage
    The machine has received a user request. It must decide whether it has
    enough evidence to answer, needs documentation, or needs clarification.

    @transition gather_evidence event: user_message target: triage internal: true external: false
      Search documentation when the current evidence is insufficient.

      @input query
        Search query that captures the missing support information.

      @input max_results default: 5
        Maximum number of documentation results.

      @guard needs_more_evidence
        Choose this transition only when the current context lacks enough
        evidence to answer safely and accurately.

      @action search_product_docs tool: search_docs
        Search docs using matching transition inputs.

      @action summarize_evidence
        Summarize the planned search and explain what evidence should be used
        in the next answer draft.

    @transition ask_clarification event: user_message target: waiting_for_user internal: true external: false
      Ask the user for missing information that cannot be found in docs.

      @input text
        Clarification question to send.

      @guard user_input_required
        Choose this transition only when the missing information must come from
        the user.

      @action send_question tool: send_message
        Send the clarification question.

    @transition draft_answer event: user_message target: drafting internal: true external: false
      Draft an answer from available evidence.

      @guard has_enough_evidence
        Choose this transition only when the context is sufficient for a
        grounded draft.

      @action draft_answer
        Draft a concise answer using the request, gathered evidence, and
        machine history.

  @state drafting
    The machine has a draft answer. It must either deliver it or revise it.

    @transition deliver_answer target: answered internal: true external: false
      Deliver the draft answer to the user.

      @input text
        Final answer text to send.

      @guard answer_is_good
        Choose this transition only when the answer is grounded, complete
        enough, safe to send, directly useful, and free of unsupported
        account-specific claims.

      @action send_answer tool: send_message
        Send the final answer.

      @action summarize_resolution
        Summarize why this support request is now resolved.

    @transition revise_answer target: drafting internal: true external: false
      Revise the draft before delivery.

      @guard answer_needs_revision
        Choose this transition when the draft is incomplete, unsupported,
        unclear, unsafe, or not directly useful.

      @action revise_draft
        Explain what must change and produce a better draft.

  @state waiting_for_user
    The machine is waiting for more user input before it can continue.

    @transition receive_user_reply event: user_message target: triage internal: false external: true
      Resume triage when the user replies.

  @state answered terminal: true
    The user has received a final answer grounded in the request, evidence,
    action results, and machine history.
