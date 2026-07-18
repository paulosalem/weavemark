@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst mingle: true

# Creative Ideation

@note
  Single user-facing entry point for applying a structured creativity /
  ideation method to a defined subject. The caller picks the method via the
  `method` variable; the spec dispatches to the matching method definition
  using `@match method ==> @refine ...`.

  Each method is defined in its own pure-method spec under `promplets/stdlib/fragments/ideation/`:

  - `module:weavemark.std.ideation.scamper` — Substitute, Combine, Adapt, Modify, Put to
    another use, Eliminate, Reverse / Rearrange (Eberle 1971; Osborn 1953).
  - `module:weavemark.std.ideation.six_thinking_hats` — White, Red, Black, Yellow, Green,
    Blue parallel-thinking modes (de Bono 1985).
  - `module:weavemark.std.ideation.reverse_brainstorming` — invert the goal, brainstorm
    ways to cause failure, then flip each reverse idea into a positive
    proposal (Osborn 1953; Klein 2007 for the pre-mortem variant).

  To add a new method:
    1. Author `promplets/stdlib/fragments/ideation/<method>.weavemark.md` as a pure method definition
       (no caller-facing variables, no `@if input` scaffolding).
    2. Add a branch to the `@match method` block below.

  This split keeps method specs reusable in isolation (e.g., refined into
  domain-specific applications) while keeping the caller's surface area
  small: a single spec, a single set of variables, and a method selector.

  The `@match method ==> @refine ...` dispatch (including the wildcard
  `_` fallback) selects exactly one reusable method. That method is then
  semantically mingled with the caller's subject, objective, constraints,
  and seed ideas, demonstrating `@refine` as specification refinement rather
  than source inclusion.

## Subject

@{subject}

## Ideation Objective

@{objective}

@if additional_context
  ## Additional Context

  @{additional_context}

@if constraints
  ## Constraints

  Hard limits the resulting ideas must respect (budget, regulation,
  timeline, brand, ethics, technology, audience). Ideas that violate
  these should be flagged rather than silently dropped, so the constraint
  itself can be examined.

  @{constraints}

@if seed_ideas
  ## Seed Ideas Provided by the Caller

  Use these as raw material if they help, but improve, recombine, sharpen,
  or discard them whenever that produces stronger output from the chosen
  method.

  @{seed_ideas}

## Method

Apply the creativity method selected by the caller. Use the method as
defined in its own spec; do not improvise a different one.

@match method
  "scamper" ==>
    @refine module:weavemark.std.ideation.scamper mingle: true
  "six-thinking-hats" ==>
    @refine module:weavemark.std.ideation.six_thinking_hats mingle: true
  "six-hats" ==>
    @refine module:weavemark.std.ideation.six_thinking_hats mingle: true
  "reverse-brainstorming" ==>
    @refine module:weavemark.std.ideation.reverse_brainstorming mingle: true
  "reverse" ==>
    @refine module:weavemark.std.ideation.reverse_brainstorming mingle: true
  _ ==>
    @refine module:weavemark.std.ideation.scamper mingle: true
