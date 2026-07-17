@promplet version: 0.7

@module weavemark.prelude.semantics

@define refine
  @phase compile
  @scope prompt
  @returns replacement

  @param reference mode: promplet
    WeaveMark promplet to compose and merge into the current prompt. Accepts a
    filesystem path, a source-qualified path, or `module:<dotted.name>`.

  @param mingle default: true
    Whether to editorially merge the target spec with surrounding content.

  @param body implicit: true mode: subspec
    Optional guidance for how to perform semantic mingling when mingle is true.

  @effect read_file read
  @effect compose_spec read
  @effect transform_text write
  @effect diagnostics write

  @body
    Load @{reference}, compose it as WeaveMark, and merge the composed result
    into the current prompt. If mingle is true, use optional guidance in @{body}
    to decide how this specific refinement should be integrated. The guidance is
    compiler-facing authoring intent, not output text to copy. Produce a single
    integrated refinement: the result must be more concrete and must imply the
    full public semantic content of the imported spec. Formally, if S' refines S,
    then S' implies S (`S' => S`), but S does not necessarily imply S' (`S => S'`).
    Do not merely concatenate imported sections, but also do not summarize away
    method definitions, workflows, examples, rationale, quality checks,
    constraints, or output contracts. Local content specializes, constrains, and
    may reorganize the imported specification as long as the imported content
    remains operationally present.
    Strip private authoring material such as `@note` blocks and duplicate source
    headings, not public method detail. Preserve exact literal identifiers,
    quoted strings, enum values, API paths, event names, schema field names, and
    fenced content unless the local spec explicitly changes them. Propagate
    cross-cutting requirements into concrete sections so detailed tables, field
    lists, routes, and acceptance criteria do not omit or contradict imported
    content. Do not describe final requirements as inherited from, compatible
    with, or refined from another spec; state the concrete obligation directly.
    If mingle is false, preserve the imported wording and source order as much
    as possible. A `mingle: false` call with a non-empty indented body is an
    authoring error because body guidance only has meaning for semantic
    mingling.

@define inspect
  @phase compile
  @scope metadata
  @returns diagnostics

  @param label default: inspection
    Optional label for the inspected region.

  @param body implicit: true mode: subspec
    Region or instruction to inspect.

  @effect inspect_text read
  @effect diagnostics write

  @body
    Inspect the selected region for composition mistakes, unresolved
    directives, contradictory instructions, missing variables, and unclear
    output contracts. Emit diagnostics under the label @{label}; do not
    change prompt text.

    @{body}

@define ask
  @phase compile
  @scope body
  @returns replacement

  @param question_type default: "clarifying question"
    Sort of question the compiler should ask about the selected body or scope.

  @param detail_level default: 20%
    How deeply the compiler should clarify the selected body before continuing.
    Must be a percentage greater than 0% and no greater than 100%.

  @param body implicit: true mode: subspec
    Optional sub-spec whose ambiguities should be clarified. If omitted, the
    directive applies to the current enclosing specification scope.

  @effect ask_user read
  @effect transform_text write
  @effect diagnostics write

  @body
    While compiling the selected body or enclosing scope, keep this directive
    unresolved until the requested @{question_type}s have been answered deeply
    enough for detail level @{detail_level}. Ask the host user concrete,
    non-redundant questions through the compile-time ask_user effect whenever a
    transformation exposes a new ambiguity or consequential choice. Innermost
    active @ask directives ask first. You may ask across multiple composition
    passes; after all useful questions are answered, remove @ask and compile the
    body using the collected answers as authoritative context.

    @{body}

@define iterate
  @phase compile
  @scope body
  @returns replacement

  @param turns default: config
    Optional positional integer maximum for improvement iterations after
    iteration 0. The host compiler also applies its configured
    max_iterate_turns cap.

  @param body implicit: true mode: subspec
    WeaveMark body whose directive applications should be compiled, traced,
    judged, and rerun when materially improvable.

  @effect compose_spec read
  @effect judge_result read
  @effect transform_text write
  @effect diagnostics write

  @body
    Compile @{body} through explicit inside-out directive-application steps. A
    step may contain one or more sibling directive applications at the same
    scope and nesting level when they can be compiled atomically without
    depending on each other's outputs. Each step emits the standard WeaveMark
    compiler-result object whose directives field records the original
    directive application(s) compiled by that result.

    Iteration 0 records the step trace. Each later iteration judges each
    previous step envelope, producing good points, bad points, concrete
    suggestions, compliance notes, constraint findings, and directive-specific
    feedback. If the judge says a step can be materially improved, rerun the
    exact same directive application(s) using the original directive headers,
    parameters, bodies, local context, prior output, and judge diagnosis. The
    rerun must fully comply with the original directive semantics and
    parameters; it is not a generic edit of the final output.

    Stop when a full iteration has no step needing material improvement. If the
    improvement budget is exhausted while any step still needs improvement,
    return the best available result and emit a warning explaining that more
    improvement opportunities remained.

    A leading, direct-child @ask wrapper may act as an @iterate prelude:

    @iterate 3
      @ask clarifying question detail_level: 40%
        target body

    In that form, @ask keeps its ordinary meaning: it clarifies its own body.
    The body of that @ask is also the iteration target, and the host compiler may
    apply the same @ask wrapper on every iteration. The @ask wrapper must be the
    only top-level child of @iterate when used this way.

    @{body}

@define assert
  @phase compile
  @scope metadata
  @returns diagnostics

  @param condition default: unspecified
    Natural-language invariant to check.

  @param severity default: error
    Diagnostic severity: error or warning.

  @param body implicit: true mode: text
    Optional assertion explanation.

  @effect inspect_text read
  @effect diagnostics write

  @body
    Check that the composed prompt satisfies the requested invariant.
    Deterministic structural assertions may be evaluated directly; semantic
    assertions should emit diagnostics according to severity @{severity}.

    @{condition}
    @{body}

@define revise
  @phase compile
  @scope body
  @returns replacement

  @param instruction default: ""
    Revision instruction to apply.

  @param mode default: minimal
    Revision mode: minimal or editorial.

  @param body implicit: true mode: subspec
    Optional WeaveMark target to revise. If omitted, the directive applies to
    the current enclosing specification scope.

  @effect transform_text write
  @effect diagnostics write

  @body
    Revise the selected prompt text according to @{instruction}. The body is the
    target sub-spec to revise; if @{body} is omitted, apply the revision to the
    current enclosing specification scope. Mode @{mode} controls aggressiveness:
    minimal means make only the required change; editorial means rewrite enough
    surrounding text to remove contradictions and preserve coherence. Return
    only the revised prompt text. Do not emit this policy, operation labels, or
    change notes.

@define expand
  @phase compile
  @scope body
  @returns replacement

  @param mode default: definition
    Expansion mode: definition, intention, or context.

  @param length default: 100%
    Desired expansion depth/detail as a percentage. 100% means as complete as usefully possible.

  @param cap default: none
    Optional maximum character count. Use none for no explicit cap.

  @param focus default: ""
    Free-form description of what aspect of the body should be expanded.

  @param body implicit: true mode: subspec
    Term, phrase, sentence, query, instruction, or short passage to expand.

  @effect transform_text write
  @effect diagnostics write

  @body
    Expand @{body} into coherent standalone prompt prose. Mode @{mode} means:
    definition expands meaning and useful distinctions; intention expands the
    underlying task, criteria, assumptions, and expected answer shape; context
    preserves the original information while enriching background, stakes, and
    implications. When @{focus} is non-empty, expand specifically along that
    user-specified focus; treat it as free-form authoring guidance, not as an
    enum. Use detail level @{length}; obey character cap @{cap} when it is not
    none. Return only the expanded prose integrated into the prompt. Do not emit
    this policy or label the result as an expansion.

@define normalize
  @phase compile
  @scope body
  @returns replacement

  @param guidance default: ""
    Normalization guidance to apply.

  @param scope default: both
    Normalization scope: syntactic, semantic, or both.

  @param headings default: normalize
    Heading handling: keep or normalize.

  @param lists default: normalize
    List handling: keep or normalize.

  @param terminology default: normalize
    Terminology handling: keep or normalize.

  @param intensity default: medium
    Semantic rewrite intensity: low, medium, or high.

  @param body implicit: true mode: subspec
    Optional WeaveMark target to normalize. If omitted, the directive applies
    to the current enclosing specification scope.

  @effect transform_text write
  @effect diagnostics write

  @body
    Normalize the selected prompt text using this guidance: @{guidance}. The
    body is the target sub-spec to normalize; if @{body} is omitted, apply the
    normalization to the current enclosing specification scope. Scope @{scope}
    controls syntactic, semantic, or combined normalization. Headings:
    @{headings}; lists: @{lists}; terminology: @{terminology}; intensity:
    @{intensity}. Resolve contradictions when scope includes semantic. Return
    only the normalized prompt text, without this policy.

@define style
  @phase compile
  @scope body
  @returns replacement

  @param description default: ""
    Style guidance: tone, voice, register, formatting, audience, or other
    presentation constraints to follow.

  @param body implicit: true mode: subspec
    Optional WeaveMark content governed by the style guidance. If omitted, the
    directive applies to the current enclosing specification scope.

  @effect transform_text write
  @effect diagnostics write

  @body
    Rewrite or constrain the selected prompt text so it follows this style
    guidance: @{description}. Integrate the guidance directly into the prompt's
    requirements. If @{body} is omitted, apply the style to the current enclosing
    specification scope. Return only the styled prompt text; do not emit this
    policy or operation labels.

@define polish
  @phase compile
  @scope body
  @returns replacement

  @param guidance default: ""
    Optional final-pass presentation and organization guidance.

  @param body implicit: true mode: subspec
    Optional WeaveMark target to polish. If omitted, the directive applies to
    the current enclosing specification scope.

  @effect transform_text write
  @effect diagnostics write

  @body
    Polish the selected prompt text using this guidance: @{guidance}. The body
    is the target sub-spec to polish; if @{body} is omitted, apply the polish to
    the current enclosing specification scope. Do not add new substantive
    information. Do not remove existing substantive information. Preserve all
    obligations, constraints, examples-as-rules, output contracts, exact
    identifiers, field names, API paths, validation gates, and important
    distinctions. Improve only presentation and organization: unify structure,
    smooth transitions, remove duplication without losing content, harmonize
    terminology, make section order more coherent, and give the existing
    information unity and final-readiness. Return only the polished prompt text;
    do not emit this policy or operation labels.

@define summarize
  @phase compile
  @scope body
  @returns replacement

  @param goal default: ""
    Optional inline summary goal.

  @param length default: medium
    Summary length: short, medium, or long.

  @param focus default: requirements
    Summary focus: requirements, rationale, or mixed.

  @param body implicit: true mode: subspec
    Content or goal to summarize.

  @effect transform_text write
  @effect diagnostics write

  @body
    Summarize @{body} for goal @{goal}. Use length @{length} and focus
    @{focus}. Preserve obligations, constraints, and output contracts that remain
    decision-useful. Return only the summarized prompt text integrated into the
    surrounding prompt. Do not emit this policy or operation labels.

@define compress
  @phase compile
  @scope body
  @returns replacement

  @param goal default: ""
    Optional inline compression goal.

  @param target default: tokens
    Compression target: tokens, chars, or structure.

  @param budget default: unspecified
    Optional target budget. Treat it as a target, not permission to discard hard
    requirements.

  @param preserve default: hard
    Preservation mode: hard or balanced. Hard means information-preserving:
    exceed the budget rather than dropping operational requirements, exact
    literals, field names, API paths, validation gates, or output contracts.
    Balanced may remove low-value rationale, examples, or repetition first.

  @param body implicit: true mode: subspec
    Sub-spec or content to compress. Put the specification content here; put
    compression preferences in parameters such as goal, target, budget, and
    preserve.

  @effect transform_text write
  @effect diagnostics write

  @body
    Compress @{body} for goal @{goal}. Target @{target}; budget @{budget};
    preserve mode @{preserve}. Preserve all distinct operational information,
    hard requirements, constraints, exact literals, field names, API paths,
    event names, validation gates, and output contracts unless explicitly told
    otherwise. Remove filler, duplicated rationale, generic preambles, repeated
    section framing, and restatements. Prefer dense bullets, tables, merged
    clauses, and direct imperative wording. If the requested budget conflicts
    with hard preservation, exceed the budget and, if useful, emit a diagnostic;
    never silently drop important information to satisfy length. Return only
    compressed prompt text. Do not emit this policy or operation labels.

@define extract
  @phase compile
  @scope body
  @returns replacement

  @param spec default: ""
    Optional inline extraction specification.

  @param format default: bullets
    Output format: bullets, json, yaml, or markdown.

  @param body implicit: true mode: subspec
    Extraction spec or source content.

  @effect transform_text write
  @effect diagnostics write

  @body
    Extract the information requested by @{spec} from @{body}. Format the result
    as @{format}. Return only the extracted prompt content integrated into the
    surrounding prompt. Do not emit this policy or operation labels.

@define generate_examples
  @phase compile
  @scope body
  @returns replacement

  @param spec default: ""
    Optional inline example-generation specification.

  @param count default: 2
    Number of examples.

  @param style default: realistic
    Example style: minimal or realistic.

  @param body implicit: true mode: subspec
    Example-generation guidance or context.

  @effect transform_text write
  @effect diagnostics write

  @body
    Generate @{count} @{style} examples that satisfy @{spec} and are consistent
    with @{body}. Return only the examples as prompt content. Do not emit this
    policy or operation scaffolding.

@define example
  @param content default: ""
    Optional inline example content.

  @param label default: Example
    Example label.

  @param placement default: integrate
    Placement preference: append or integrate.

  @param body implicit: true mode: subspec
    Author-provided example content.

  @body
    Example (@{label}; placement: @{placement}):
    @{content}

    @{body}

@define structural_constraints
  @phase compile
  @scope body
  @returns replacement

  @param constraints default: ""
    Optional inline structural constraints.

  @param strict default: false
    Whether constraints are mandatory.

  @param body implicit: true mode: subspec
    Structural constraints.

  @effect transform_text write
  @effect diagnostics write

  @body
    Integrate these structural constraints into the selected prompt text:
    @{constraints}
    @{body}
    Strict mode is @{strict}. Return only final prompt text with the structure
    made operational. Do not emit raw strictness labels unless the user
    explicitly requested that literal wording.
