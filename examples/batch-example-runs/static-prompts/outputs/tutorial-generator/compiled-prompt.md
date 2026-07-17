# Tutorial Generator

Write a technical tutorial about **building REST APIs with FastAPI**.

The tutorial must teach, coach, and explain—not merely list facts. Assume the reader is an **intermediate developer with working knowledge of web and programming fundamentals**, and state that assumption briefly near the beginning.

Begin with a concise conclusion or takeaway: what the reader will be able to build and why FastAPI is a strong fit for this task. Then make the reasoning behind the tutorial traceable by including a short explanation table early in the tutorial:

| Step | Claim or inference | Evidence or basis | Confidence |
| --- | --- | --- | --- |
| 1 | claim | source, calculation, assumption, observation, framework feature, or implementation constraint | low/medium/high |

Also include:
- **Key assumptions:** assumptions the tutorial depends on, such as reader background, Python familiarity, and environment expectations.
- **Checks performed:** commands, tests, comparisons, or validation steps the reader can actually run.
- **Limits:** what the tutorial does not cover, what remains environment-dependent, and which production concerns need deeper treatment.
- **Simplest explanation:** a plain-language summary a non-specialist can quickly inspect.

## Teaching and learning requirements

Structure the tutorial so the learner can build understanding in layers:

1. **Orientation** — what REST APIs are used for, what FastAPI provides, and what the final project will do.
2. **Prerequisite map** — what the reader should already know and what will be introduced as needed.
3. **Core explanation** — explain the intuitive model first, then precise terms, then code.
4. **Worked example** — carry one concrete FastAPI API through step by step.
5. **Misconceptions** — call out likely traps and why they are tempting.
6. **Practice** — include the exercises specified below.
7. **Next learning step** — recommend the smallest useful next topic or improvement after finishing.

For each important concept:
- Start with intuition.
- Then give the precise formulation.
- Then show a worked example.
- Then discuss edge cases or production implications when relevant.

Use analogies only when they clarify the concept, and explicitly state where each analogy breaks. For example, if comparing a REST API to a restaurant menu, explain that the analogy helps with request/response intuition but does not capture statelessness, schemas, authentication, or failure handling.

Surface common misconceptions, including:
- REST means “any HTTP endpoint.”
- FastAPI automatically makes an application production-ready.
- Type hints validate all business rules.
- Async always makes code faster.
- HTTP status codes are interchangeable as long as the response body is clear.

Include short checks for understanding before advanced material.

## Audience-specific requirements

**Target audience: developers with working knowledge of the fundamentals.**

- Skip basic setup unless it differs from the standard approach.
- Focus on practical patterns, trade-offs, and the “why” behind design decisions.
- Compare alternative approaches, such as “You could use X here, but Y is better because…”.
- Include at least one production-ready program example.

## Required tutorial content

Cover at minimum:

- What a REST API is and how resources, routes, methods, status codes, headers, request bodies, and response bodies fit together.
- Why FastAPI is useful for REST APIs: type hints, automatic validation, dependency injection, OpenAPI documentation, async support, and developer ergonomics.
- Project setup, including exact commands to create an environment, install dependencies, run the app, and test endpoints.
- A coherent example domain, such as a task tracker, notes service, inventory API, or book catalog.
- Defining Pydantic models for request and response validation.
- Implementing routes for create, read, update, delete, and list operations.
- Choosing correct HTTP methods and status codes.
- Handling validation and application errors cleanly.
- Organizing code so the API can grow beyond a single-file demo.
- Testing the API with either `pytest` and FastAPI’s test client or equivalent tooling.
- Explaining where in-memory examples stop being realistic and what changes when adding a database.
- Production considerations: configuration, logging, authentication, CORS, pagination, versioning, deployment, and observability.

## Explainability requirements

For every major design choice, explain:
- The chosen approach.
- At least one alternative.
- Why the chosen approach is appropriate for this tutorial.
- What trade-off it introduces.

When presenting code, explain why each important part exists. Do not rely on “this is standard” as the only justification.

When making claims about performance, async behavior, validation, or production readiness:
- State the assumption behind the claim.
- Identify whether the claim is generally true, conditionally true, or context-dependent.
- Avoid implying certainty where the result depends on workload, deployment environment, or infrastructure.

## Program Examples

When writing program examples, follow these conventions:

- Python decorators use the standard syntax: @property, @staticmethod, @classmethod, @dataclass
- Java/Kotlin annotations use: @Override, @Inject, @Autowired, @RestController
- Email addresses in examples should use: user@example.com

Every fenced program block must:
1. Be complete and runnable; do not use `...` or comments such as `# rest of program here`.
2. Include necessary imports.
3. Show expected output in a comment or separate output block.

At least one example must be production-ready enough to demonstrate:
- Clear app structure.
- Pydantic request and response models.
- Route functions with appropriate status codes.
- Error handling.
- Tests or testable behavior.
- Commands to run and verify the API.

## Practice Exercises

Include 3 progressively harder exercises at the end of the tutorial:

**Exercise 1 (Warm-up):** A straightforward application of the core concept.
Estimated time: 10 minutes.

**Exercise 2 (Applied):** Combines multiple concepts from the tutorial. Requires the reader to make design decisions.
Estimated time: 20 minutes.

**Exercise 3 (Challenge):** An open-ended problem that extends beyond the tutorial content. Encourages the reader to research and experiment.
Estimated time: 30-45 minutes.

For each exercise, provide:
- A clear problem statement.
- Expected input/output examples.
- Hints, collapsed or hidden if Markdown output supports it.
- A reference solution.

## Output requirements

Output the tutorial in **Markdown** format.

Use clear headings, runnable code blocks, command blocks, output examples, tables where helpful, and concise explanations. The final tutorial should read as a complete, practical learning resource for an intermediate developer who wants to build REST APIs with FastAPI and understand the reasoning behind each step.
