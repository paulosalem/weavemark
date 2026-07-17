@promplet version: 0.7

@module weavemark.std.ideation.scamper

# SCAMPER

@note
  SCAMPER is a structured creativity technique for generating new ideas by
  applying seven directed transformations to an existing subject — a product,
  service, process, system, concept, or design. Each letter is a deliberate
  cognitive trigger that breaks default thinking:

  - **S — Substitute**: replace a component, material, person, rule, or step.
  - **C — Combine**: merge with another offering, function, audience, or idea.
  - **A — Adapt**: borrow from analogous domains; adjust to fit a new context.
  - **M — Modify (Magnify / Minify)**: change an attribute — size, frequency,
    intensity, shape, tone, scope; amplify or shrink it.
  - **P — Put to another use**: apply the subject, or part of it, to a
    different purpose, market, user, or context.
  - **E — Eliminate**: remove a component, step, constraint, feature, or
    assumption; simplify aggressively.
  - **R — Reverse / Rearrange**: flip the order, invert the roles, swap
    cause and effect, mirror the layout, run the process in reverse.

  SCAMPER is most useful when there is already a concrete subject and an
  ideation team needs to escape incremental thinking. Each lens is forced,
  not optional — that is the point. The technique is judged by the diversity
  and novelty of the ideas it produces, not by their immediate feasibility.

  This is a **pure method definition**. It assumes a subject, objective, and
  constraints when they are available; otherwise it provides a generic SCAMPER
  framing.

  Reference:
  - Bob Eberle (1971). "SCAMPER: Games for Imagination Development."
    (Derived from Alex Osborn's "Applied Imagination" idea checklists.)

You are applying the SCAMPER creativity method.

Your objective is to generate a broad and genuinely diverse set of new ideas
about the subject defined by the source context by deliberately applying
each of the seven SCAMPER lenses: **Substitute, Combine, Adapt, Modify, Put
to another use, Eliminate, Reverse / Rearrange**.

Use SCAMPER as a disciplined ideation method, not as decorative formatting.
Every lens must produce at least one idea that could not have been generated
by simply describing the subject. Push past the obvious first answer for each
lens before stopping.

## Core SCAMPER Principles

- Frame the subject precisely before applying the lenses. State what it is,
  who it serves, what job it does, and which parts make it up. Vague subjects
  produce vague ideas.
- Treat each lens as a forcing function. Do not skip a lens because it "does
  not apply"; if a lens feels awkward, that is usually where the novel ideas
  live.
- Generate before judging. In the ideation pass, prioritize quantity, range,
  and boldness. Evaluation comes afterwards.
- Aim for diversity within each lens. Two ideas that differ only in surface
  detail count as one. Push for ideas that target different components, users,
  steps, or attributes of the subject.
- Make each idea concrete enough to be discussed. "Add AI" is not an idea;
  "replace the manual triage step with an AI classifier that routes tickets
  by intent" is.
- Distinguish the **transformation** (what SCAMPER move was made) from the
  **resulting idea** (what the subject would now be or do). Both should be
  visible in the output.
- Respect any stated constraints, but also surface ideas that violate them
  when the violation reveals a useful question (e.g., "this only works if
  regulation X changes — is that worth lobbying for?").
- After generating, evaluate. Cluster, prioritize, and recommend a small
  number of ideas worth developing further. Unfiltered SCAMPER output is
  ideation, not a recommendation.

## Required SCAMPER Workflow

1. **Frame the subject.** Restate the subject in one or two sentences.
   Identify:
   - core function or job-to-be-done
   - main components, steps, or features
   - primary users or stakeholders
   - key attributes (size, speed, cost, format, tone, frequency, etc.)
   - implicit assumptions that "everyone knows" about how it works
2. **Clarify the ideation objective.** What kind of improvement is wanted —
   cost reduction, new market, differentiation, sustainability, delight,
   accessibility, defensibility? The objective biases which lenses produce
   the most useful ideas, but does not let you skip any lens.
3. **Apply each of the seven lenses in order.** For each lens:
   - Ask the lens-specific prompting questions (see next section).
   - Generate at least 3 distinct ideas; aim for 4–6 when the subject is rich.
   - For each idea, capture: the transformation made, the resulting concept,
     and a one-line note on why it might matter.
4. **Cross-pollinate.** After all seven passes, look for ideas that combine
   well across lenses (e.g., an Eliminate idea plus a Combine idea may form
   a stronger third idea). Add these as explicit hybrids.
5. **Evaluate and cluster.** Group similar ideas. For each cluster, briefly
   assess:
   - potential impact relative to the objective
   - feasibility under any stated constraints
   - novelty relative to what the subject already does or what competitors do
6. **Prioritize.** Recommend 3–5 ideas (or clusters) worth developing further,
   with the reasoning for each choice. Flag any high-impact ideas that
   require a constraint to be revisited.
7. **State next steps.** For the top ideas, suggest a concrete next action:
   a small experiment, a prototype, a customer conversation, a calculation,
   or a decision that would unlock further work.

## Lens-by-Lens Prompting Questions

Use these as starting points; extend them to fit the subject. They are
illustrative, not exhaustive.

- **Substitute** — What component, material, person, rule, channel, or
  step could be replaced? What would happen if a different ingredient,
  technology, supplier, audience, or business model were used?
- **Combine** — What could this be merged with — another product, service,
  feature, dataset, audience, brand, or workflow? Could two separate steps
  become one? Could two user roles be served by the same interface?
- **Adapt** — What works elsewhere — in another industry, era, culture,
  discipline, or natural system — that could be adapted here? What analogy
  reframes the subject?
- **Modify (Magnify / Minify)** — What attribute could be amplified, shrunk,
  exaggerated, softened, sped up, slowed down, made denser, made lighter,
  more personal, more anonymous, more frequent, more rare?
- **Put to another use** — Who else could use this, or a part of it? What
  other problem could this solve? What if the same capability were sold to
  a different segment, repackaged for a different context, or repurposed
  internally?
- **Eliminate** — What part could be removed without breaking the core value?
  What step, feature, role, constraint, or assumption is actually optional?
  What is the minimum viable version? What gets simpler if we drop it?
- **Reverse / Rearrange** — What if the order of steps were inverted? What
  if the customer became the supplier, or the supplier the customer? What
  if the "outcome" came first and the "input" last? What if the layout,
  hierarchy, or causality were flipped?

## Common Failure Modes

- Generating only one bland idea per lens and moving on. SCAMPER is about
  pushing through the obvious to reach the useful.
- Producing ideas that are really the same idea reworded across multiple
  lenses (e.g., "use AI" under Substitute, Combine, and Adapt). Each lens
  must contribute a genuinely different angle.
- Skipping awkward lenses (often Reverse or Eliminate) because no idea
  comes immediately to mind. These lenses frequently produce the most
  original output once you push past the initial blank.
- Drifting into evaluation during ideation — killing ideas before they are
  fully formed. Keep generation and evaluation as separate phases.
- Stopping at vague abstractions ("make it more modern") instead of
  concrete moves ("split the onboarding flow into a 60-second guest path
  and a deeper signed-in path").
- Treating SCAMPER output as a recommendation. It is raw ideation; the
  recommendation comes from the evaluation and prioritization step.
- Ignoring stated constraints entirely, or, conversely, refusing to surface
  ideas that violate them. Both fail the caller.

## Presentation Rules

- If the source task already specifies a deliverable format, honor it,
  but still make all seven SCAMPER lenses visible and clearly separated.
- Within each lens, number the ideas and keep them parallel in form
  (transformation → resulting idea → why it might matter).
- Use the subject's own vocabulary; do not retreat into generic ideation
  jargon.
- Make the evaluation and prioritization step visibly distinct from the
  generation step.
- If a lens genuinely produced weaker results than the others, say so and
  explain why — do not pad it with filler.

## Default Response Structure

### Subject Frame

Restate the subject, its core function, main components, primary users, key
attributes, and the implicit assumptions you will deliberately challenge.

### Ideation Objective

State the kind of improvement or innovation being sought, and any constraints
that will shape evaluation.

### SCAMPER Ideation

For each of the seven lenses, in order — **Substitute, Combine, Adapt,
Modify, Put to another use, Eliminate, Reverse / Rearrange** — present:

- a brief framing of how the lens applies to this subject
- 3-6 distinct ideas, each with:
  - the transformation made
  - the resulting concept
  - a one-line note on why it might matter

### Cross-Lens Hybrids

Surface any ideas formed by combining moves from two or more lenses. Name
the parent lenses and describe the combined idea.

### Evaluation and Clusters

Group similar ideas. For each cluster, briefly assess impact, feasibility
under constraints, and novelty.

### Prioritized Recommendations

Identify 3-5 ideas (or clusters) worth developing further. For each, state
why it was chosen and what makes it stronger than the alternatives. Flag
any high-impact ideas that depend on revisiting a constraint.

### Next Steps

For each prioritized idea, suggest a concrete next action — an experiment,
prototype, customer conversation, calculation, or decision — that would
materially advance it.

### Assumptions and Open Questions

State the assumptions you made about the subject, the objective, or the
constraints, and any open questions whose answers would meaningfully change
the prioritization.
