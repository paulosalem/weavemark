@promplet version: 0.7

@module weavemark.std.ideation.reverse_brainstorming

# Reverse Brainstorming

@note
  Reverse brainstorming is a creativity technique that attacks a problem
  by deliberately inverting it. Instead of asking *"How do we solve this?"*
  or *"How do we improve this?"*, the team asks the opposite:

  - *"How could we cause this problem?"*
  - *"How could we make this outcome worse?"*
  - *"What would guarantee failure?"*

  The team then brainstorms answers to the inverted question, often with
  surprising ease — finding ways to break, sabotage, or worsen something
  is psychologically less inhibited than proposing positive solutions, and
  it surfaces hidden assumptions about what the "normal" or "correct"
  state of the system actually is. Each reverse idea is then **flipped
  back** into a candidate solution, improvement, or safeguard.

  Reverse brainstorming is most useful when:

  - the group is stuck on a problem and conventional brainstorming feels
    forced or repetitive
  - failures are happening that nobody can fully explain
  - the team is too close to the subject and is unconsciously assuming
    that current practice is the only sensible baseline
  - the goal is to harden a system against failure (e.g., reliability,
    safety, security, user-experience pitfalls)

  It is related to **pre-mortem analysis** (Klein, 2007), to **inversion**
  as used by Charlie Munger, and to the engineering practice of
  **failure-mode brainstorming**. All share the same core move: imagine
  the bad outcome vividly, then work in reverse.

  This is a **pure method definition**. It assumes a problem, desired outcome,
  and constraints when they are available; otherwise it provides a generic
  reverse-brainstorming framing.

  References:
  - Alex Osborn (1953). "Applied Imagination." (Origin of brainstorming.)
  - Gary Klein (2007). "Performing a Project Premortem." HBR.

You are applying the Reverse Brainstorming method.

Your objective is to generate improvements, solutions, or safeguards for the
subject defined by the source context by **first inverting the problem**,
brainstorming ways to cause or worsen the bad outcome, and then flipping
each reverse idea back into a positive proposal.

Use reverse brainstorming as a disciplined ideation method, not as a
rhetorical flourish. The discipline is in *fully* committing to the
inversion before flipping back — generating the reverse ideas seriously,
specifically, and in volume, even when they feel uncomfortable.

## Core Reverse-Brainstorming Principles

- **Invert the goal, not the topic.** "How do we improve onboarding?" inverts
  to "How could we make onboarding fail / frustrate users / be abandoned?",
  not to "Tell me about onboarding in general."
- **Generate reverse ideas seriously.** Treat the inverted question as a
  real design problem. Aim for ideas that are specific, mechanical, and
  plausible — things that genuinely would worsen the outcome.
- **Quantity first, judgment second.** In the reverse-ideation pass,
  prioritize range and volume. Do not filter or moralise during generation.
- **Hunt for hidden assumptions.** Many reverse ideas will describe
  practices that are already happening — that is the point. Reverse
  brainstorming exposes the failure modes a team has normalised.
- **Flip each reverse idea deliberately.** A flip is not a simple negation
  ("do the opposite"). It is a positive proposal that *prevents,
  counteracts, or removes the conditions for* the reverse idea. The flip
  must be concrete enough to be acted on.
- **Distinguish three kinds of flipped output:** **fixes** (remove an
  existing harm the reverse idea revealed), **safeguards** (prevent the
  reverse idea from being introduced), and **improvements** (use the
  inversion as inspiration for a stronger positive design).
- **Evaluate after flipping, not before.** Some reverse ideas flip into
  ordinary improvements; some flip into surprising and valuable ones; a
  few do not flip cleanly at all. Note the latter — they often point at
  deeper structural issues.

## Required Reverse-Brainstorming Workflow

1. **Frame the original problem precisely.** State the subject, the
   desired outcome, the users or stakeholders, and any constraints. Vague
   problems produce vague reverse ideas.
2. **Invert the problem.** Construct one or more *reverse questions* by
   negating the goal. Prefer questions that ask how to cause the bad
   outcome actively, not merely how to fail to achieve the good one:
   - "How could we guarantee that users abandon onboarding?"
   - "How could we maximise customer churn this quarter?"
   - "How could we cause this incident to recur every month?"
   Pick the reverse question (or two) that will produce the most useful
   ideation.
3. **Reverse-brainstorm.** Generate a substantial list of reverse ideas —
   aim for 10–20 if the problem is rich. Push for specificity and for
   diversity across categories (product, process, people, communication,
   incentives, environment, timing, data, edge cases, external actors).
   Do not censor; uncomfortable ideas are often the most revealing.
4. **Cluster the reverse ideas.** Group similar ideas. A cluster usually
   names a single underlying failure mechanism. Naming the cluster makes
   the flip step much more productive.
5. **Flip each cluster (or idea) into a positive proposal.** For each
   one, write a fix, safeguard, or improvement that directly addresses
   the reverse mechanism. Be explicit about which kind of flip it is.
6. **Audit the flips against current practice.** For each positive
   proposal, note whether it is:
   - **already in place** (good — confirm and reinforce)
   - **partially in place** (gap to close)
   - **absent** (real opportunity)
   - **structurally hard** (worth deeper analysis)
7. **Prioritize.** Recommend 3–5 positive proposals worth acting on,
   with the reasoning for each choice. Flag any reverse ideas that did
   not flip cleanly and explain what deeper question they suggest.
8. **State next steps.** For each prioritized proposal, suggest a
   concrete next action: a small experiment, a process change, a
   measurement to add, or a decision that would unlock further work.

## Prompting Questions

Use these as starting points; extend them to fit the subject.

For the **inversion** step:
- What is the worst plausible outcome here? How would we describe it in
  one sentence?
- If a competitor wanted to sabotage this, what would they do?
- If we wanted this initiative to fail without anyone realising we were
  responsible, how would we engineer it?
- What would it look like if we did the cruellest, laziest, or most
  short-sighted version of this?

For the **reverse ideation** step, push across multiple dimensions:
- **Product / artefact** — what features, behaviours, or defaults would
  worsen the outcome?
- **Process** — what steps, hand-offs, approvals, or timings would
  introduce friction or failure?
- **People** — who could be excluded, overloaded, mis-trained, or
  mis-incentivised?
- **Communication** — what messages, omissions, or tone choices would
  confuse, alienate, or mislead?
- **Incentives** — what rewards or penalties would push behaviour in
  the wrong direction?
- **Environment** — what physical, digital, or social context would
  make the bad outcome more likely?
- **Data / feedback** — what metrics could be hidden, gamed, or
  measured at the wrong cadence?
- **Edge cases** — which users, scenarios, or failure modes are easy
  to forget?

For the **flip** step:
- What is the smallest, most concrete change that would directly
  prevent this reverse idea from being possible?
- If this reverse idea is *already happening*, what would removing it
  look like?
- Does this flip belong as a fix, a safeguard, or a positive
  improvement?

## Common Failure Modes

- Inverting the topic instead of the goal ("brainstorm about onboarding"
  rather than "brainstorm how to make onboarding fail"). The result is
  ordinary brainstorming with extra steps.
- Producing reverse ideas that are jokes, exaggerations, or moral
  caricatures. Some humour is fine, but the bulk of the list must be
  serious, specific, and plausible.
- Stopping at a small list. Reverse brainstorming pays off in volume —
  the most useful ideas are usually somewhere past the first ten.
- Flipping each reverse idea by simply negating its wording ("do not do
  X"). The flip must be a concrete positive proposal.
- Skipping the audit step. Without it, the output is a list of
  proposals with no signal about which are new versus which are
  already in place but unrecognised.
- Treating reverse ideas that mirror current practice as embarrassing
  and quietly dropping them. These are the most valuable findings.
- Forgetting that some reverse ideas will *not* flip cleanly. That
  failure is itself information about a deeper structural problem.

## Presentation Rules

- If the source task already specifies a deliverable format, honor
  it, but still make the inversion, reverse ideas, and flipped proposals
  clearly separated.
- Show the chosen reverse question(s) explicitly.
- Keep the reverse-ideation list distinct from the flipped proposals.
  The reader should be able to see both.
- For each flipped proposal, label its type (fix / safeguard /
  improvement) and its audit verdict (already in place / partial /
  absent / structurally hard).
- Surface the cases where a reverse idea did not flip cleanly. Do not
  hide them.

## Default Response Structure

### Problem Frame

Restate the subject, the desired outcome, the users or stakeholders,
and any stated constraints.

### Inverted Question(s)

State the reverse question(s) chosen for ideation, and briefly explain
why each was chosen.

### Reverse Ideas

Present the brainstormed list of reverse ideas, grouped into clusters
that name an underlying failure mechanism. Aim for breadth across the
dimensions listed in the prompting questions.

### Flipped Proposals

For each cluster (or notable idea), give the flipped positive proposal.
Label each proposal:

- **Type**: fix / safeguard / improvement
- **Audit verdict**: already in place / partially in place / absent /
  structurally hard
- **Brief rationale**: how the flip addresses the underlying failure
  mechanism

### Reverse Ideas That Did Not Flip Cleanly

List any reverse ideas that resisted a clean flip, and describe the
deeper question or structural issue each one suggests.

### Prioritized Recommendations

Identify 3–5 proposals worth acting on. For each, state why it was
chosen and what makes it stronger than the alternatives.

### Next Steps

For each prioritized proposal, suggest a concrete next action — an
experiment, a process change, a measurement to add, or a decision —
that would materially advance it.

### Assumptions and Open Questions

State the assumptions you made about the problem, the desired outcome,
or the constraints, and any open questions whose answers would
meaningfully change the prioritization.
