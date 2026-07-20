@promplet version: 0.7


# API Documentation Generator

@note
  This spec generates API documentation with request and response examples.
  It uses @generate_examples for realistic request/response pairs, the @revise
  directive to iteratively improve the docs, @structural_constraints to enforce
  consistent formatting, and @output for the final deliverable structure.

@revise "Review for consistent terminology, complete error codes (400, 401, 403, 404, 500), accurate JSON schemas, and clear parameter descriptions."
  @structural_constraints
    Each API endpoint section must contain:
    1. HTTP method and path
    2. One-line description
    3. Authentication requirements
    4. Request parameters (path, query, body) in a table
    5. Request body schema (JSON, with types and constraints)
    6. Response schema (JSON, with types)
    7. Status codes table (code, meaning, when it occurs)
    8. At least 2 request/response examples (success + error case)
    9. Rate limiting information
    10. Changelog (version where endpoint was added/modified)

  Write comprehensive API reference documentation for the
  **@{api_name}** (version @{api_version}).

  ## Overview

  @{api_description}

  Base URL: `@{base_url}`

  Authentication: @{auth_method}

  ## Endpoints

  Use the endpoint definitions below to create one complete endpoint section per
  endpoint:

  @{endpoints}

  @generate_examples count: 2
    Generate realistic request/response examples for each endpoint above. Include:
    - A successful request with a complete response body
    - An error request that triggers that endpoint's documented error response
    Use realistic data that matches the @{api_name} domain.

  @output "markdown"
    Use developer documentation conventions:
    - Fenced blocks with `json`, `bash`, or `http` language tags
    - Tables for parameters and status codes
    - Inline formatting for field names, paths, and values
    - Collapsible sections (`<details>`) for lengthy response schemas
