# Knowledge Base Article

Write a complete internal engineering knowledge base article about **Event-Driven Architecture with Apache Kafka**.

The article must use this structure, in order:

1. `# Event-Driven Architecture with Apache Kafka`
2. `## TL;DR` — one paragraph, maximum 3 sentences.
3. `## Overview` — 2–3 paragraphs explaining the context, when event-driven architecture is useful, and why Apache Kafka is commonly used for it.
4. `## Key Concepts` — include one H2 or H3 subsection per concept below.
5. `## Technology Comparison` — compare Kafka with RabbitMQ, Apache Pulsar, AWS Kinesis, and Redis Streams.
6. `## Migration Guide` — concise checklist-oriented guidance for moving from a monolithic REST API with synchronous database calls to Kafka-based event-driven architecture.
7. `## Practical Examples` — at least 2 concrete examples with code, architecture sketches, or event-flow descriptions.
8. `## Common Pitfalls` — bulleted list of mistakes, risks, and mitigations.
9. `## Related Topics` — links or anchor references.
10. `## Changelog` — include when the article was last updated.

## Key Concepts to Cover

Cover these concepts precisely and practically:

### Events and Event Contracts

Define an event as an immutable fact that something meaningful happened in the business or system domain, such as `OrderPlaced`, `PaymentAuthorized`, or `InventoryReserved`. Explain how event contracts define the event name, schema, required fields, versioning rules, ownership, compatibility expectations, and semantic meaning. Show why stable event contracts matter for independently deployable producers and consumers.

Example: an order service publishes an `OrderCreated` event with `order_id`, `customer_id`, `created_at`, and line-item data; billing, fulfillment, and analytics consume the event without calling the order service synchronously.

### Kafka Topics, Partitions, Offsets, and Consumer Groups

Explain that Kafka stores events in topics, splits topics into partitions for scale and ordering, assigns each record an offset, and lets consumer groups coordinate parallel consumption. Clarify that ordering is guaranteed within a partition, not globally across a topic. Explain why partition-key design affects throughput, ordering, hot spots, and downstream correctness.

Example: keying `payment-events` by `account_id` preserves per-account ordering while allowing different accounts to be processed in parallel.

### Producers, Consumers, and Delivery Semantics

Explain producer responsibilities: choosing topics, keys, schemas, retries, idempotence, acknowledgements, batching, and error handling. Explain consumer responsibilities: offset commits, retries, dead-letter handling, idempotent processing, backpressure, and observability. Distinguish at-most-once, at-least-once, and effectively-once processing, and emphasize that business idempotency is usually required even when Kafka features reduce duplicates.

Example: a notification consumer records processed `event_id` values before sending email so a retried message does not send duplicate notifications.

### Schema Evolution and Compatibility

Explain why schema evolution is central in event-driven systems: producers and consumers deploy independently, so events must remain readable across versions. Cover backward compatibility, forward compatibility, additive changes, deprecated fields, required-field risks, and schema registry usage. Mention Avro, Protobuf, or JSON Schema as common options.

Example: adding an optional `promotion_code` field to `OrderCreated` is safer than renaming `customer_id` or changing its type.

### Reliability, Observability, and Failure Recovery

Explain durability, replication, retention, replay, lag monitoring, dead-letter topics, poison messages, and operational alerting. Show why Kafka enables replay-based recovery but also requires careful controls to avoid reprocessing side effects incorrectly.

Example: after fixing a bug in a fraud-detection consumer, the team replays retained `PaymentAuthorized` events from a known offset into the corrected consumer while monitoring lag, duplicate suppression, and downstream side effects.

## Technology Comparison Requirements

In the `Technology Comparison` section, include a table comparing Apache Kafka with RabbitMQ, Apache Pulsar, AWS Kinesis, and Redis Streams. For each alternative, evaluate:

- Performance characteristics: latency, throughput, scaling model, resource usage, and ordering behavior.
- Developer experience: learning curve, operational complexity, tooling, documentation, and local development ergonomics.
- Ecosystem maturity: community, library support, managed-service availability, enterprise adoption, and integration options.
- When to choose the alternative over Kafka.

Use these comparison points:

- **RabbitMQ**: often better for traditional message queues, request/reply workflows, complex routing, lower operational footprint, and workloads where broker-managed acknowledgements and per-message routing matter more than replayable logs.
- **Apache Pulsar**: strong for multi-tenancy, geo-replication, tiered storage, separate compute/storage architecture, and teams willing to operate a more complex distributed system for those capabilities.
- **AWS Kinesis**: strong when the organization is deeply committed to AWS and wants a managed streaming service with tight AWS integrations, but with different shard, throughput, retention, and ecosystem tradeoffs.
- **Redis Streams**: useful for simpler lightweight streaming or queue-like workloads close to existing Redis infrastructure, but usually not a substitute for Kafka-scale durable event streaming across many teams.

## Migration Guide Requirements

In the `Migration Guide` section, provide concise, checklist-oriented steps for moving from a monolithic REST API with synchronous database calls to Event-Driven Architecture with Apache Kafka. Preserve these details:

- Pre-migration checklist and risk assessment:
  - Identify bounded contexts and candidate events.
  - Map synchronous call chains and database coupling.
  - Define event owners, consumers, SLAs, data classification, and failure modes.
  - Choose initial pilot workflow with limited blast radius.
- Data migration strategy:
  - Introduce event schemas and topic naming conventions.
  - Use an outbox pattern or change data capture where appropriate.
  - Backfill historical events carefully and mark replay/backfill events when needed.
- API stability and breaking changes:
  - Keep existing REST APIs during transition.
  - Add Kafka producers behind current write paths before forcing consumers to migrate.
  - Version event schemas and avoid breaking field changes.
- Rollback plan:
  - Feature-flag producers and consumers.
  - Keep synchronous fallback paths until the new flow is validated.
  - Document offset reset, consumer disablement, and replay procedures.
- Validation and smoke tests:
  - Verify event publication, schema compatibility, consumer idempotency, lag, dead-letter handling, and business reconciliation.
  - Compare results from old synchronous paths and new event-driven paths during a parallel-run period.
- Expected timeline for a team of 4–6 engineers:
  - Discovery and design: 1–2 weeks.
  - Platform/topic/schema setup: 1–2 weeks.
  - Pilot producer and consumers: 2–4 weeks.
  - Parallel run, validation, and hardening: 2–3 weeks.
  - Gradual rollout and deprecation of synchronous paths: 2–6+ weeks depending on risk and number of integrations.

## Practical Examples Requirements

Include at least two examples. Prefer examples like:

1. **Order processing flow**: `OrderCreated` triggers payment, inventory, fulfillment, notifications, and analytics consumers.
2. **Audit or analytics pipeline**: domain events are streamed to a warehouse or lakehouse without adding synchronous dependencies to production services.
3. **Migration outbox example**: a REST write persists business data and an outbox record in one transaction; a relay publishes the event to Kafka.

Include fenced code blocks with language identifiers where useful, such as JSON event examples, pseudocode, SQL outbox schema, or consumer logic.

## Common Pitfalls Requirements

Include pitfalls such as:

- Treating Kafka as a drop-in replacement for synchronous RPC.
- Ignoring schema evolution and compatibility.
- Assuming global ordering across partitions.
- Choosing poor partition keys that create hot partitions or break ordering requirements.
- Forgetting idempotency and duplicate handling.
- Committing offsets before side effects are safely handled.
- Underinvesting in lag, dead-letter, replay, and consumer-health observability.
- Publishing events that expose sensitive data unnecessarily.
- Allowing event ownership to become unclear across teams.

## Formatting Requirements

Use GitHub-Flavored Markdown with:

- Fenced blocks with language identifiers.
- Tables for comparison data.
- Admonition blocks using this style: `> **Note:** ...` for important callouts.
- Anchor links in the `Related Topics` section.
