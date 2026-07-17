@promplet version: 0.7

@module weavemark.experimental.fslm

@define machine
  @phase compile
  @scope document
  @returns machine_spec
  @effect fslm_sugar read
  @param name
    Inline finite-state linguistic machine name.
  @param body implicit: true mode: subspec
    Machine states and transitions.
  @body
    @machine @{name}
      @{body}

@define state
  @phase compile
  @scope body
  @returns state_spec
  @effect fslm_sugar read
  @param name
    State name.
  @param body implicit: true mode: subspec
    State description and transitions.
  @body
    @state @{name}
      @{body}

@define transition
  @phase compile
  @scope body
  @returns transition_spec
  @effect fslm_sugar read
  @param name
    Transition name.
  @param body implicit: true mode: subspec
    Transition description, inputs, guards, and actions.
  @body
    @transition @{name}
      @{body}

@define input
  @phase compile
  @scope body
  @returns input_spec
  @effect fslm_sugar read
  @param name
    Transition input name.
  @param body implicit: true mode: text
    Natural-language input description.
  @body
    @input @{name}
      @{body}

@define guard
  @phase compile
  @scope body
  @returns guard_spec
  @effect fslm_sugar read
  @param name
    Guard id.
  @param body implicit: true mode: text
    Natural-language guard rule.
  @body
    @guard @{name}
      @{body}

@define action
  @phase compile
  @scope body
  @returns action_spec
  @effect fslm_sugar read
  @param name
    Action name.
  @param body implicit: true mode: text
    Action instruction.
  @body
    @action @{name}
      @{body}
