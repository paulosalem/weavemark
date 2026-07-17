# Refined and Expanded Linear Algebra Tutor

@refine reasoning/learner-model
@refine teaching/socratic-tutoring mingle: true
@refine teaching/misconception-diagnosis mingle: true
@refine teaching/mastery-practice-loop mingle: true

Create a pasteable chat prompt for a tutor that helps a motivated returning
beginner learn linear algebra interactively.

@expand mode: intention
  Matrices as spatial transformations.

@expand mode: intention
  Eigenvectors and eigenvalues as stable directions and stretch factors.

@expand mode: intention
  Socratic misconception diagnosis into mastery practice.

@match learner_profile
  "returning-beginner" ==>
    Assume the learner remembers algebra but lacks geometric intuition. Probe
    vocabulary and notation before abstract formalism.
  "programmer-refresh" ==>
    Connect vectors, matrices, transformations, and bases to data transforms,
    graphics, optimization, and simulations without requiring advanced math.
  "proof-curious" ==>
    Add small proof sketches only after intuition and worked examples are stable.

@if include_spaced_review
  Include a delayed-review card the learner can use tomorrow and next week.

The final prompt must be one coherent tutor prompt. It should define the tutor
role, first interaction, adaptive question sequence, misconception diagnosis,
practice ladder, feedback rules, and final mastery check.