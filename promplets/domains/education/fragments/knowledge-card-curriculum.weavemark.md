@promplet version: 0.7

@module weavemark.domains.education.knowledge_card_curriculum

# Curriculum: Progressive Knowledge Cards

Use this module to create a coherent field-level learning sequence delivered one
high-density concept card at a time.

## Curriculum map

- Before writing cards, construct a concept map for the domain: foundations,
  mechanisms, applications, misconceptions, limitations, bridges, and advanced
  horizons.
- Assign every candidate concept an importance, prerequisite depth, difficulty,
  novelty, and relationship set. Coverage MUST be broad enough that the complete
  pack teaches the important shape of the field rather than a bag of trivia.
- Select concepts by importance before randomness. Favor foundations early, then
  interleave mechanisms, applications, misconceptions, and occasional surprising
  bridges so the sequence remains varied without becoming incoherent.
- Never duplicate a concept. A deliberate revisit MUST deepen, connect, contrast,
  or test recall and MUST name the earlier card relationship.
- Validate the complete pack for concept coverage, prerequisite violations,
  accidental repetition, unsupported claims, difficulty distribution, and useful
  cross-links before publication.

## One-card contract

Each card teaches exactly one meaningful concept and contains:

- `id`: stable identifier within the pack.
- `title`: short descriptive title.
- `core_idea`: two to five concise paragraphs emphasizing intuition, mechanism,
  importance, limitations, and relationships.
- `example`: a short practical example, analogy, diagram description, or thought
  experiment when it improves understanding.
- `key_takeaway`: one memorable sentence capturing the concept.
- `connections`: zero or more related concepts, prepared-for topics, common
  misconceptions, or real-world applications, preferably using stable card IDs.
- `difficulty`: a small declared scale centered on educated beginners.
- `prerequisites`: stable IDs of cards whose ideas are assumed.
- `source_refs`: references supporting factual or safety-sensitive claims.
- `media`: optional local image or illustration metadata only when it materially
  clarifies the idea.
- `review_prompts`: optional checked-in recall, comparison, application, or
  connection questions for a deliberate revisit without a runtime model.

Every sentence MUST teach. Avoid filler, motivational copy, encyclopedic detail,
long biography, excessive jargon, and disconnected definitions.
Do not pad repeated sentence templates merely to satisfy paragraph-length checks.

## Teaching style

- Be concise, insightful, approachable, conversational without being casual, and
  intellectually honest.
- Prefer intuition and mechanisms over memorization. Explain why the idea matters,
  where it fails, and what common belief it corrects.
- Introduce advanced ideas briefly only when they are explained intuitively. The
  learner should finish slightly stretched, not overwhelmed.
- Use concrete, memorable examples. Images clarify; they never decorate.

## Evidence and safety

- Use a declared source policy for each pack and retain pack-level references with
  stable IDs. Do not invent citations or imply that a source supports more than it
  does.
- Curate each card's `source_refs` to sources whose declared claim scope fits that
  card; pack-wide source fan-out is not evidence.
- Date claims that can become stale. Distinguish consensus, useful simplification,
  debated interpretation, and uncertainty.
- Health, child-development, financial, legal, or safety-sensitive cards MUST state
  their educational boundary, avoid individualized advice, and point to qualified
  professional or primary guidance when action could cause harm.
- Review the whole pack for bias, stereotypes, age/culture assumptions, financial
  promises, medical overreach, and examples that confuse correlation with cause.

## Progressive use

- Default to one card at a time. The app MAY choose among eligible unseen cards
  using the default deterministic policy below:
  1. Exclude cards with unsatisfied prerequisites.
  2. Normalize each eligible card's declared signals to `[0, 1]`.
  3. Score `0.50 * importance + 0.20 * foundational_priority + 0.15 *
     coverage_gap + 0.10 * recent_category_diversity + 0.05 * seeded_jitter`.
  4. Choose the highest score; break exact ties by stable card ID.
  The refining spec MAY replace these weights explicitly, but importance MUST
  remain greater than random jitter.
- A user signal such as "revisit" MAY schedule a concept again, but the repeated
  interaction should use recall, comparison, application, or a deeper connection
  from `review_prompts` rather than replaying identical text without explanation.
- Schedule at most one revisit among five new-card interactions by default, unless
  the user explicitly opens a review-only session.
- Track seen, liked, saved, revisit, notes, and self-rated understanding separately;
  none of these alone proves mastery.
