@promplet version: 0.7


@refine module:weavemark.std.guidelines.prompt_quality mingle: true
@refine module:weavemark.std.reasoning.prompt_refinement_core mingle: true

# Prompt Refactoring Pipeline

@note
  This spec demonstrates the most distinctive capability of our system:
  treating prompts AS PROGRAMS that can be refactored. No template engine
  can do what happens here — we take a messy, organically-grown prompt,
  and apply a pipeline of semantic transformations that UNDERSTAND the
  meaning of the text:

  1. @extract pulls out the hard requirements (like extracting an interface)
  2. @normalize transforms its indented target body into consistent formatting
  3. @normalize with semantic scope resolves cross-references and contradictions
  4. @revise transforms its indented target body to add or remove requirements
  5. @expand turns compact missing-section notes into fuller sections
  6. @revise can remove unwanted parts surgically when its target is explicit
  7. @assert validates the result (like a type checker)

  This is "prompt refactoring" — the same discipline as program refactoring,
  but applied to natural-language constraint sets.

@note
  The messy prompt below simulates what happens after months of ad-hoc
  edits by multiple team members. It has inconsistent formatting,
  contradictory instructions, redundant sections, and missing pieces.
  The directive pipeline below it refactors it into a clean, consistent,
  correct prompt — automatically.

@extract "All hard requirements (MUST, SHOULD, ALWAYS, NEVER) and all output format constraints; preserve the exact obligation level." format: bullets
  @{raw_prompt}

@normalize "Normalize headings, lists, and terminology without changing meaning." scope: syntactic
  @{raw_prompt}

@normalize "Resolve cross-references and contradictions while preserving the prompt's intent." scope: semantic
  @{raw_prompt}

@revise "@{revision_instruction}" mode: editorial
  @{raw_prompt}

@if add_section
  @expand mode: intention length: 70%
    @{new_section_content}

@if remove_section
  @revise "@{contraction_instruction}" mode: editorial
    @{raw_prompt}

@structural_constraints strict: true
  Required sections in order:
  1. Role and Identity
  2. Core Requirements
  3. Constraints and Prohibitions
  4. Output Format
  5. Examples (if any)
  6. Edge Cases

@assert The prompt contains no contradictory instructions. severity: error
@assert The prompt specifies what to do when input is ambiguous. severity: warning
@assert Every MUST requirement has a clear success criterion. severity: warning

@output enforce: strict
  The refactored prompt must be ready to use as-is with an LLM.
  No meta-commentary, no "here's what I changed" notes — just
  the clean, final prompt.
  When the prompt includes JSON schemas or examples, render them as proper
  fenced `json` blocks. Do not write a standalone `json` label.

@revise "Remove standalone format labels such as `json`, `text`, or `markdown`; describe JSON fields as bullets or a table instead." mode: editorial
  @{raw_prompt}

@polish "Harmonize the assembled sections into one coherent final prompt without adding or removing requirements."

@assert The final prompt contains no standalone `json`, `text`, or `markdown` labels. severity: warning
