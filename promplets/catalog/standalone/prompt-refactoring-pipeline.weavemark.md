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
  4. @revise transforms the normalized body to add requirements
  5. @expand turns compact missing-section notes into fuller sections
  6. @revise removes unwanted parts surgically
  7. @polish harmonizes the fully transformed body
  8. @assert validates the result (like a type checker)

  This is "prompt refactoring" — the same discipline as program refactoring,
  but applied to natural-language constraint sets.

@note
  The messy prompt below simulates what happens after months of ad-hoc
  edits by multiple team members. It has inconsistent formatting,
  contradictory instructions, redundant sections, and missing pieces.
  The directive pipeline below it refactors it into a clean, consistent,
  correct prompt — automatically. The transformation directives are nested
  deliberately: WeaveMark evaluates nested directive bodies inside-out, so the
  raw prompt flows through one pass at a time instead of being rewritten by
  independent sibling directives.

@polish "Harmonize the fully transformed prompt into one coherent final prompt without adding or removing requirements."
  @revise "Remove standalone format labels such as `json`, `text`, or `markdown`; describe JSON fields as bullets or a table instead. Preserve fenced code block language tags such as ```json." mode: editorial
    @structural_constraints strict: true
      Required sections in order:
      1. Role and Identity
      2. Core Requirements
      3. Constraints and Prohibitions
      4. Output Format
      5. Examples (if any)
      6. Edge Cases

      @revise "If a Removal instruction block appears after the draft, apply it to the draft. If no Removal instruction block appears, preserve the draft." mode: editorial
        @revise "If an Additional section block appears after the draft, integrate it into the draft as a normal prompt section. If no Additional section block appears, preserve the draft." mode: editorial
          @revise "@{revision_instruction}" mode: editorial
            @normalize "Resolve cross-references and contradictions while preserving the prompt's intent. Use the requirements inventory below as a preservation checklist; do not emit the inventory as a separate section in the final prompt." scope: semantic
              Requirements inventory:
              @extract "All hard requirements (MUST, SHOULD, ALWAYS, NEVER) and all output format constraints; preserve the exact obligation level." format: bullets
                @{raw_prompt}

              Draft to normalize:
              @normalize "Normalize headings, lists, and terminology without changing meaning." scope: syntactic
                @{raw_prompt}

          @if add_section
            Additional section block:
            @expand mode: intention length: 70%
              @{new_section_content}

        @if remove_section
          Removal instruction block:
          @{contraction_instruction}

@output enforce: strict
  The refactored prompt must be ready to use as-is with an LLM.
  No meta-commentary, no "here's what I changed" notes — just
  the clean, final prompt.
  Resolve cross-references and contradictory instructions.
  Specify what to do when input is ambiguous.
  Give every MUST requirement a clear success criterion.
  When the prompt includes JSON schemas or examples, render them as proper
  fenced `json` blocks. Do not write standalone `json`, `text`, or `markdown`
  labels.

@assert contains: "Resolve cross-references and contradictory instructions."
@assert contains: "Specify what to do when input is ambiguous." severity: warning
@assert contains: "every MUST requirement a clear success criterion." severity: warning
@assert contains: "Do not write standalone `json`, `text`, or `markdown`" severity: warning
