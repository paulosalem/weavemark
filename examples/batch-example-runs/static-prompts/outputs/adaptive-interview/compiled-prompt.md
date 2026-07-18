# Adaptive Interview Protocol

Design a structured interview protocol for evaluating candidates for the role of **Senior Backend Engineer** at a Series B fintech startup processing 50K transactions/day.

Adapt all questions, probing strategies, and evaluation criteria to an Engineering manager with 8 years of backend experience, conducting the technical screen. Make the protocol practical for a knowledgeable technical interviewer: include enough depth to calibrate senior-level backend judgment, but avoid academic trivia and avoid requiring specialist knowledge outside the candidate’s likely role scope.

Use a professional, warm tone. Treat the interview as a two-way conversation, not an interrogation. The candidate should feel respected and challenged.

## Analyst and Interviewing Standards

Apply rigorous analytical standards throughout the protocol:

- Separate observable evidence from assumptions. In the scorecard, label what the interviewer directly observed versus what they inferred.
- Use clear sections with headings. Each section should state the decision-relevant point first, then provide supporting reasoning, caveats, and follow-up questions.
- When rating a candidate, state confidence level as high, medium, or low and explain the basis for that confidence.
- For each positive or negative signal, identify the strongest counter-argument before making a recommendation.
- Prefer concrete behavioral and technical evidence over impressions, charisma, pedigree, or communication style alone.
- Avoid illegal or discriminatory questions. Do not ask about age, family status, marital status, disability, medical history, religion, nationality, immigration status beyond lawful work authorization handling, race, gender identity, sexual orientation, pregnancy, military status, or other protected characteristics.

## Core Competencies

Assess the following competencies in priority order:

1. Distributed systems design and operational awareness
2. API design and data modeling
3. Testing strategy: unit, integration, contract, and load testing
4. Incident response and debugging under pressure

## Technical Deep Dive Protocol

Total recommended time: 60 minutes.

### Opening and Calibration — 5 minutes

Set expectations warmly and clearly:

- Explain that the interview will focus on backend engineering judgment, trade-offs, and operational thinking.
- Invite clarifying questions and tell the candidate they may state assumptions explicitly.
- Give a short description of the company context: a Series B fintech startup processing roughly 50K transactions/day, where correctness, reliability, and operational discipline matter.
- Remind the candidate that perfect answers are not expected; the goal is to understand how they reason.

Evaluation focus:

- Does the candidate ask useful clarifying questions?
- Do they separate facts from assumptions?
- Do they communicate trade-offs clearly and respectfully?

### Architecture and Problem Decomposition — 30 minutes

Present an anonymized fintech backend challenge:

> We process approximately 50K financial transactions per day. Design or improve a backend service that ingests transaction events from partners, validates them, persists them, exposes APIs for internal consumers, and supports investigation when something goes wrong.

Ask the candidate to decompose the problem before solving it.

Required probes:

1. What are the main components and responsibilities?
2. What data model would you start with, and what are the most important entities?
3. What APIs would internal services or operational users need?
4. What happens if a partner sends duplicate, malformed, delayed, or out-of-order events?
5. What would you do differently at 10x scale?
6. How would you monitor this system in production?
7. What failure modes worry you most?
8. Ask the candidate to critique their own design: what is the strongest argument against their approach?

Evaluation criteria by competency:

| Competency | Strong evidence | Weak evidence | Follow-up probes |
|---|---|---|---|
| Distributed systems design and operational awareness | Defines service boundaries; handles retries, idempotency, backpressure, ordering, observability, failure modes, deployment risk, and rollback; makes explicit consistency and availability trade-offs. | Jumps to tools without explaining responsibilities; ignores duplicate processing, partial failure, latency, monitoring, or operational recovery. | “How do you prevent double-processing?” “What happens if the database is slow?” “How would on-call know this is failing?” |
| API design and data modeling | Models transactions, accounts or counterparties as appropriate, statuses, audit/history, external IDs, idempotency keys, timestamps, and error states; designs stable APIs with validation, pagination, versioning, and clear error semantics. | Produces vague tables or endpoints; omits lifecycle states, idempotency, auditability, or validation rules. | “What fields are required?” “How would clients retry safely?” “How would you evolve this API?” |
| Testing strategy | Covers unit tests for business rules, integration tests for persistence and partner interactions, contract tests for partner/internal APIs, load tests for throughput and latency, and failure-mode tests for retries and duplicates. | Mentions only unit tests or generic QA; does not tie tests to risk. | “Which tests would catch duplicate partner events?” “What would you load test first?” |
| Incident response and debugging under pressure | Describes logs, metrics, traces, dashboards, alerts, runbooks, feature flags, safe rollback, data reconciliation, and communication during incidents. | Focuses only on local debugging or code inspection; lacks production triage process. | “A partner reports missing transactions. What do you check first?” “How do you restore trust in the data?” |

Calibration guidance:

- A strong senior candidate should navigate ambiguity, ask clarifying questions, and make trade-offs explicit without needing heavy scaffolding.
- They do not need to design an extremely complex distributed system for 50K transactions/day, but they should show operational maturity and understand correctness risks in fintech.
- Watch for over-engineering. A candidate who proposes Kafka, event sourcing, CQRS, distributed tracing, and multiple databases must justify why each is needed at the current scale.
- Watch for under-engineering. A candidate who proposes a single synchronous endpoint without retries, idempotency, monitoring, or reconciliation is missing important senior-level concerns.

### System Design — 30 minutes

Ask the candidate to design a production backend system from scratch for a fintech transaction-processing workflow.

Required evaluation areas:

- Ambiguity navigation: Do they ask about transaction volume, latency requirements, partner behavior, consistency needs, compliance constraints, data retention, and operational ownership?
- Trade-off articulation: Can they explain consistency versus availability, synchronous versus asynchronous processing, schema flexibility versus validation strictness, and build-versus-buy choices?
- Operational awareness: Do they cover monitoring, alerting, deployments, rollback, failure modes, incident handling, reconciliation, and data repair?
- Breadth versus depth balance: Do they cover the full system at a useful level and then go deeper on the riskiest components?

Suggested system design prompt:

> Design a backend service that receives transaction events from external partners, validates and stores them, exposes transaction status through an internal API, and supports investigation when a transaction appears missing, duplicated, or incorrect.

Guide the discussion through these phases:

1. Requirements and assumptions
   - Functional requirements: ingest, validate, persist, expose status, support investigation.
   - Non-functional requirements: correctness, availability, observability, latency, throughput, auditability, security.
   - Explicit assumptions: expected traffic, retry behavior, partner reliability, data retention, consistency needs.

2. High-level architecture
   - Ingestion endpoint or message consumer.
   - Validation and normalization layer.
   - Transaction store with clear lifecycle states.
   - Idempotency and deduplication mechanism.
   - Internal API for querying status and investigation data.
   - Observability and alerting.
   - Reconciliation or repair workflow.

3. Data model
   - Transaction identifier and external partner identifier.
   - Idempotency key or deduplication key.
   - Status lifecycle, timestamps, amount, currency, partner/source, validation errors, retry count, and audit history.
   - Indexing/query patterns for support and internal services.
   - Data integrity constraints and migration strategy.

4. API design
   - Safe ingestion semantics for retries.
   - Clear validation errors.
   - Query endpoint for transaction status.
   - Pagination, filtering, versioning, authorization, and rate limiting.
   - Backward compatibility strategy for internal consumers.

5. Testing strategy
   - Unit tests for validation and status transitions.
   - Integration tests for database, queues, and external partner adapters.
   - Contract tests for partner payloads and internal APIs.
   - Load tests around ingestion throughput, latency, and database contention.
   - Fault-injection or scenario tests for duplicates, delayed events, malformed payloads, queue backlog, and database slowness.

6. Operations and incident response
   - Metrics: ingestion rate, validation failures, duplicate rate, processing latency, queue depth, error rate, reconciliation mismatch count.
   - Logs/traces: correlation IDs, transaction IDs, partner IDs, retry attempts, failure reasons.
   - Alerts: sustained processing failures, backlog growth, missing partner feed, abnormal duplicate spike, reconciliation drift.
   - Runbook: triage steps, customer or partner impact assessment, rollback, data repair, and post-incident learning.

Senior-level scoring guidance:

- 5: Builds a coherent, appropriately scoped design; identifies correctness and operational risks; makes explicit trade-offs; explains testing and incident response with practical detail; critiques their own approach.
- 4: Strong design with minor gaps; covers most operational and testing concerns; trade-offs are mostly explicit.
- 3: Reasonable design but uneven depth; may need prompting for idempotency, observability, testing, or incident response.
- 2: Fragmented or tool-driven answer; misses important correctness or operational concerns.
- 1: Cannot decompose the problem or reason about production backend risks.

### Live Technical Probes — Optional if Time Remains

Use one or two targeted probes if the system design discussion leaves uncertainty:

- Debugging probe: “Transactions from one partner dropped by 30% in the last hour, but no deploy happened. Walk me through your investigation.”
- API probe: “Design the request and response shape for an internal transaction-status endpoint. What errors should it return?”
- Testing probe: “Which tests would you require before launching partner retry support?”
- Data modeling probe: “How would you represent transaction state transitions and audit history?”

Evaluate whether the candidate reasons from evidence, identifies assumptions, and narrows the problem under uncertainty.

## Interviewer Probing Strategy

Use these patterns throughout:

- Ask “What assumptions are you making?” when the candidate jumps ahead.
- Ask “What evidence would tell you this design is working?” to test observability.
- Ask “What would fail first?” to test operational realism.
- Ask “What is the strongest argument against this design?” to test self-critique.
- Ask “How would you test that?” whenever they propose a business rule, API behavior, or failure-handling mechanism.
- Ask “What would you simplify for our current scale?” to distinguish pragmatism from over-engineering.

Avoid turning the interview into a trivia quiz. Prefer realistic trade-offs and evidence of judgment.

## Evaluation Scorecard

Use a 1–5 scale for each competency. Record observed evidence, assumptions, counter-evidence, and confidence.

### Example: Strong Hire Scorecard

Candidate: Example senior backend candidate
Role: Senior Backend Engineer
Recommendation: Strong hire
Overall confidence: High, based on consistent senior-level reasoning across architecture, API design, testing, and incident response.

| Competency | Score | Evidence | Caveats and counter-arguments |
|---|---:|---|---|
| Distributed systems design and operational awareness | 5 | Decomposed ingestion, validation, persistence, status API, observability, and reconciliation cleanly. Identified idempotency, duplicate partner events, queue backlog, delayed events, database slowness, alerting, rollback, and runbook needs. Chose asynchronous processing only where it reduced partner coupling and explained the consistency trade-off. | Could have quantified latency targets earlier. Strongest counter-argument: the design may be slightly more complex than needed for 50K transactions/day, but the candidate explicitly identified simplifications for the current stage. |
| API design and data modeling | 4 | Proposed transaction lifecycle states, external partner IDs, idempotency keys, audit history, validation errors, timestamps, and status query APIs with pagination and versioning. Explained retry-safe ingestion and clear error semantics. | Did not initially discuss authorization boundaries for internal APIs until prompted. Confidence remains high because the candidate incorporated it well after the prompt. |
| Testing strategy | 5 | Mapped tests to risk: unit tests for validation and state transitions, integration tests for persistence and queues, contract tests for partner payloads, load tests for ingestion throughput, and scenario tests for duplicate, malformed, delayed, and out-of-order events. | Strongest counter-argument: load-test thresholds were approximate. This is acceptable because they stated assumptions and described how they would calibrate thresholds from production targets. |
| Incident response and debugging under pressure | 5 | Gave a structured triage plan for missing transactions: check partner feed health, ingestion rate, validation failures, queue depth, processing latency, recent config changes, transaction-level logs, traces, and reconciliation output. Included customer/partner communication, rollback criteria, data repair, and post-incident follow-up. | Could have mentioned severity classification sooner. Confidence is high because their process was evidence-driven and operationally mature. |

Overall rationale:

- Facts observed: The candidate consistently asked clarifying questions, labeled assumptions, reasoned about failure modes, and connected design choices to operational evidence.
- Assumptions inferred: They are likely effective in production backend ownership and on-call environments.
- Strongest counter-argument: They may initially design for a slightly larger scale than the company currently needs.
- Mitigation: They showed good judgment when asked what they would simplify for the current business stage.
- Final recommendation: Strong hire for Senior Backend Engineer.

## Final Output Requirements for the Interviewer

When using this protocol, produce a structured interview write-up with:

1. Summary recommendation: strong hire, hire, lean hire, lean no-hire, or no-hire.
2. Confidence level: high, medium, or low, with basis.
3. Competency scores from 1–5.
4. Evidence observed for each competency.
5. Assumptions and uncertainties.
6. Strongest counter-argument to the recommendation.
7. Any follow-up areas for onsite or reference checks.

Keep the final write-up professional, direct, evidence-grounded, and respectful.
