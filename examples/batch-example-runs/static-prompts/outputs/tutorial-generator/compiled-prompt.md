# Tutorial Generator

Write a technical tutorial about **building REST APIs with FastAPI**.

## Target audience and learning model

**Target audience: developers with working knowledge of the fundamentals.**

- Assume the reader understands basic Python, HTTP concepts, JSON, command-line usage, and ordinary web-development terminology, but may not know FastAPI-specific idioms.
- State this assumed learner level briefly near the beginning of the tutorial.
- Identify only the prerequisites that matter for building REST APIs with FastAPI.
- Skip basic setup unless it differs from the standard approach, but still provide the exact commands needed to create the environment, install dependencies, and run the examples.
- Teach in layers:
  1. Intuition first: explain what the concept is for and why it matters.
  2. Precise formulation second: define the FastAPI, Python, HTTP, and validation terms accurately.
  3. Worked example third: carry one concrete API through the tutorial step by step.
  4. Edge cases last: mention practical pitfalls after the reader has the core model.
- Use analogies only when they clarify; state where each analogy breaks down.
- Focus on practical patterns, trade-offs, and the "why" behind design decisions.
- Compare alternative approaches where useful, e.g. "You could use X here, but Y is better because…".
- Surface common misconceptions and explain why they are tempting.
- Include short checks for understanding before moving into advanced material.
- Include at least one production-ready program example.

## Required tutorial shape

Use this teaching structure unless a clearer Markdown organization serves the tutorial better:

1. **Practical conclusion / what you will build** — start with the useful end state: what the reader will have working, why FastAPI is a good fit, and what trade-offs the tutorial will emphasize.
2. **Assumed background and prerequisite map** — list required knowledge, tools, and packages.
3. **Core explanation** — explain FastAPI's mental model: path operations, request/response flow, dependency injection, validation with type hints/Pydantic, status codes, errors, and OpenAPI docs.
4. **Reasoning chain for the design** — include a concise table that makes important tutorial choices traceable:

   | Step | Claim or inference | Evidence or basis | Confidence |
   | --- | --- | --- | --- |
   | 1 | claim | source, calculation, assumption, or observation | low/medium/high |

5. **Worked API example** — build one concrete REST API step by step, with runnable code and commands.
6. **Implementation patterns and trade-offs** — discuss routing, schemas, validation, persistence boundaries, dependency injection, error handling, configuration, testing, and deployment concerns.
7. **Misconceptions and traps** — correct likely misunderstandings, especially around async, Pydantic models, HTTP semantics, validation, and when not to over-engineer.
8. **Checks performed** — describe the checks, tests, comparisons, or source checks actually used in the tutorial's recommendations.
9. **Limits and assumptions** — state what remains uncertain, simplified, unverified, environment-dependent, or outside scope.
10. **Simplest explanation** — include a brief plain-language recap a non-specialist can inspect quickly.
11. **Next learning step** — suggest the smallest useful project, concept, or documentation page to study next.

## Program Examples

When writing program examples, follow these conventions:

- Python decorators use the standard syntax: @property, @staticmethod, @classmethod, @dataclass
- Java/Kotlin annotations use: @Override, @Inject, @Autowired, @RestController
- Email addresses in examples should use: user@example.com

Every fenced program block must:
1. Be complete and runnable (no "..." or "# rest of program here")
2. Include necessary imports
3. Show expected output in a comment or separate output block

For the FastAPI tutorial specifically:

- Provide exact shell commands for creating a virtual environment, installing dependencies, starting the development server, and running tests.
- Include a complete FastAPI application with at least:
  - route declarations,
  - request and response models,
  - validation behavior,
  - explicit HTTP status codes,
  - error handling,
  - dependency injection where it improves clarity,
  - and a production-minded structure or note about how to split modules.
- Include at least one production-ready program example rather than only toy snippets.
- Include tests using a standard FastAPI testing approach.
- Explain what each important command and code block does before relying on it.

## Practice Exercises

Include 3 progressively harder exercises at the end of the tutorial:

**Exercise 1 (Warm-up):** A straightforward application of the core concept.
Estimated time: 10 minutes.

**Exercise 2 (Applied):** Combines multiple concepts from the tutorial.
Requires the reader to make design decisions.
Estimated time: 20 minutes.

**Exercise 3 (Challenge):** An open-ended problem that extends beyond the
tutorial content. Encourages the reader to research and experiment.
Estimated time: 30-45 minutes.

For each exercise, provide:
- A clear problem statement
- Expected input/output examples
- Hints (collapsed/hidden if the output format supports it)
- A reference solution

Output the tutorial in **Markdown** format.
