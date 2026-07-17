@promplet version: 0.7

@module weavemark.domains.programming.foundations.software_spec

# Software Specification

@note
  Reusable foundation for software specifications: detailed descriptions of
  systems to be developed, including implementation constraints and guidance for
  human programmers or AI programming agents.

A **software specification** describes the system to be built. It states product
behavior, implementation constraints, validation expectations, and acceptance
criteria. The resulting implementation must satisfy everything required by the
specification and may add further details when they are consistent with it.

## Core obligations

- Present the specification as the source of truth for building the software.
- Prefer concrete requirements over exploratory questions.
- State assumptions and open decisions explicitly, but do not turn the
  specification into a conversation with the user.
- Separate product behavior from implementation details, while making both
  precise enough for a developer to act.
- Use MUST/SHOULD/MAY carefully for requirements, recommendations, and optional
  enhancements.
- Define what is in scope and out of scope for the first build.

## Required specification shape

Include the sections that apply:

1. **Product intent** - user job, target user, and value delivered.
2. **Functional scope** - concrete features, workflows, screens, commands,
   integrations, or APIs.
3. **Domain model** - key entities, state transitions, identifiers, and
   persistence needs.
4. **User experience** - primary flows, empty states, errors, loading states,
   accessibility, and responsive behavior.
5. **Architecture and implementation notes** - major components, data flow,
   important libraries or platform constraints, and extension points.
6. **Non-functional requirements** - performance, reliability, security,
   privacy, observability, portability, and maintainability where relevant.
7. **Acceptance criteria** - testable conditions that indicate the build is
   complete.
8. **Verification plan** - unit, integration, end-to-end, manual, or visual
   checks the implementing agent should run.

## Quality bar

The specification should be clear enough that a competent programming agent can
start implementation without asking basic product-shape questions. If critical
information is missing, provide safe assumptions and mark the smallest set of
open decisions that genuinely block implementation.
