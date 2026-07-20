@promplet version: 0.7

@module weavemark.domains.programming.modules.rest_api

# REST API Design Standards

### URL Structure
- Resources are plural nouns: `/users`, `/accounts`, `/transactions`.
- Nesting limited to one level: `/users/{id}/accounts` — never deeper.
- Use query parameters for filtering, sorting, pagination:
  `?status=active&sort=-created_at&page=1&per_page=20`

### Request/Response Format
- Successful JSON resource responses use `Content-Type: application/json`.
- Success envelope: collections MUST use `{"data": [...], "meta": {...}}`;
  single resources MUST use `{"data": ...}`. Problem responses do not use this
  success envelope.
- Pagination meta: `{"total": N, "page": P, "per_page": S, "total_pages": T}`.
- Empty collections return `{"data": [], "meta": {"total": 0, ...}}` — never 404.

### Error Responses
- Errors MUST follow RFC 7807 Problem Details and use
  `Content-Type: application/problem+json`:
  ```json
  {
    "type": "https://api.example.com/errors/validation",
    "title": "Validation Error",
    "status": 422,
    "detail": "field 'amount' must be a positive integer",
    "errors": [{"field": "amount", "message": "must be a positive integer"}]
  }
  ```
- Status codes: 400 (bad input), 401 (not authenticated), 403 (forbidden),
  404 (not found), 409 (conflict), 422 (validation), 429 (rate limit), 500 (server error).

### Idempotency
- POST requests that create resources MUST accept an `Idempotency-Key` header.
- If the same key is resubmitted within 24 hours, return the original response.
- GET, PUT, DELETE are inherently idempotent.

### Versioning
- Version in URL path: `/api/v1/...`
- Breaking changes MUST increment the version; additive changes MAY stay on current version.
