@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst mingle: true

# Adaptive Interview Protocol

@note
  This spec demonstrates something only possible with LLM-powered
  composition: a deeply nested adaptive structure where the OUTER
  directives (audience, style, compress) semantically transform the
  INNER directive results.

  For example, @compress nested inside @match won't just truncate
  text — it will intelligently condense the already-selected branch
  while preserving the critical constraints. And @style guidance at the
  top level reshapes the ENTIRE result, including the compressed
  and matched content, for the target reader.

  A traditional template engine cannot do this because the transforms
  are semantic, not syntactic.

Design a structured interview protocol for evaluating candidates
for the role of **@{role_title}** at @{company}.

Adapt all questions, probing strategies, and evaluation criteria to
@{interviewer_profile}'s level of expertise.

## Core Competencies

Assess the following competencies, in priority order:
@{competencies}

@match interview_format
  "technical_deep_dive" ==>
    ## Technical Deep Dive Protocol

    @match seniority
      "junior" ==>
        ### Fundamentals Assessment (45 min)

        Focus on demonstrating foundational understanding:
        1. Two concept-explanation questions (can they teach it?)
        2. One live programming problem (straightforward, tests basics)
        3. One debugging exercise (read an existing program, find the bug)

        @if include_system_design
          ### Mini System Design (15 min)
          @compress "Keep this mini-design exercise under roughly 300 tokens while preserving all evaluation constraints."
            Ask the candidate to design a simple system relevant
            to @{company}'s domain. Focus on whether they can
            identify the main components and explain data flow.
            Do not expect distributed systems knowledge — evaluate
            clarity of thought, ability to ask clarifying questions,
            and awareness of trade-offs even at a basic level.
            Provide scaffolding: give them a whiteboard template
            with pre-drawn boxes for "Client", "Server", "Database"
            and ask them to fill in the interactions.

      "senior" ==>
        Use this exact 60-minute allocation. Do not add overlapping or
        unallocated interview sections:

        - Opening and calibration: 5 minutes
        - Architecture and problem decomposition: 25 minutes
        @if include_system_design
          - System design: 25 minutes
        @else
          - Applied architecture deep dive: 25 minutes
        - Candidate questions and close: 5 minutes

        ### Opening & Calibration (5 min)

        Set expectations, introduce the company context, and invite clarifying
        questions.

        ### Architecture & Problem Decomposition (25 min)

        1. Present a real @{company} challenge (anonymized) and
           ask them to decompose it into sub-problems
        2. Probe: "What would you do differently at 10x scale?"
        3. Ask them to critique their own design

        @if include_system_design
          ### System Design (25 min)
          Design a production system from scratch. Evaluate:
          - Ability to navigate ambiguity (do they ask good questions?)
          - Trade-off articulation (consistency vs. availability, etc.)
          - Operational awareness (monitoring, deployment, failure modes)
          - Breadth vs. depth balance

        @else
          ### Applied Architecture Deep Dive (25 min)

          Extend the candidate's decomposition with one production incident,
          one changing requirement, and one explicit cost or operability
          constraint. Ask them to revise their design, explain which decisions
          remain reversible, and identify the evidence that would change their
          approach. Evaluate trade-off clarity, debugging method, testing depth,
          and ability to adapt without turning this into a second system-design
          exercise.

        ### Candidate Questions & Close (5 min)

        Reserve the final five minutes for the candidate's questions and a
        concise explanation of next steps.

      "staff_plus" ==>
        ### Technical Vision & Influence (30 min)

        1. "Describe a technical decision you made that affected
           multiple teams. What was the process?"
        2. Present a cross-cutting @{company} challenge and ask
           them to define the problem before solving it
        3. Probe organizational and technical trade-offs

        @if include_system_design
          ### System Design at Scale (30 min)
          @expand mode: intention length: 70%
            Beyond the standard system design evaluation, also assess:
            - Ability to make decisions under uncertainty and articulate
              what they would need to learn to increase confidence
            - How they balance innovation against operational risk
            - Whether they think about human/organizational systems
              alongside technical systems

  "behavioral" ==>
    ## Behavioral Interview Protocol

    Use the STAR method (Situation, Task, Action, Result) for all
    questions. Ask follow-up probing questions to verify depth.

    @match seniority
      "junior" ==>
        Focus on: learning ability, collaboration, handling feedback.
        - "Tell me about a time you had to learn something completely
          new under a deadline."
        - "Describe a situation where you received critical feedback.
          What did you do?"

      "senior" ==>
        Focus on: technical leadership, mentoring, cross-team impact.
        - "Tell me about a time you had to convince a skeptical
          stakeholder to adopt your technical recommendation."
        - "Describe a situation where you had to balance technical
          debt against feature delivery."

      "staff_plus" ==>
        Focus on: organizational influence, strategy, ambiguity.
        - "Tell me about a time you changed how your organization
          approaches a technical problem."
        - "Describe a situation where you had to make a decision
          with incomplete information that affected multiple teams."

@if include_scorecard
  ## Evaluation Scorecard

  @generate_examples count: 1 style: realistic
    Generate a filled-in example scorecard showing how to rate a
    "strong hire" candidate for the @{role_title} role. Use the
    competencies listed above as evaluation dimensions. Score each
    on a 1-5 scale with brief justification.

Use this final tone: @{tone}.
Avoid illegal or discriminatory interview questions.

@assert contains: "evaluation criteria" severity: warning
@assert contains: "illegal or discriminatory interview questions" severity: warning
