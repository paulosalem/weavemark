# Knowledge Base Article: Event-Driven Architecture with Apache Kafka

Write a GitHub-Flavored Markdown knowledge base article for an internal engineering team about **Event-Driven Architecture with Apache Kafka**.

The article must follow this structure:

1. H1 title
2. TL;DR: one paragraph, maximum 3 sentences
3. Overview: 2-3 paragraphs of context
4. Key Concepts: H2 subsections, one per concept
5. Practical Examples: at least 2 concrete examples
6. Common Pitfalls: bulleted list
7. Related Topics: links or references with anchor links
8. Changelog: include when the article was last updated

Cover these key concepts in operational detail:

- **Events and event contracts**: Define an event as an immutable record that something meaningful happened in a domain. Explain why stable event schemas, naming, versioning, and compatibility rules matter for independent service evolution. Include an example such as `OrderCreated`, `PaymentAuthorized`, or `InventoryReserved` and show how producers and consumers rely on the schema.
- **Kafka topics, partitions, offsets, and consumer groups**: Explain how topics organize event streams, partitions provide scale and ordering boundaries, offsets track read position, and consumer groups coordinate parallel processing. Clarify that ordering is guaranteed within a partition, not globally across all partitions. Include an architecture example for partitioning by `customer_id`, `order_id`, or another stable key.
- **Producers, consumers, and delivery semantics**: Explain how producers publish records and consumers process them asynchronously. Cover retries, idempotency, duplicates, at-least-once processing, exactly-once capabilities, and why downstream handlers must usually be idempotent. Include a concrete processing example with a service publishing an event and another service updating a read model or triggering a workflow.
- **Schema management and compatibility**: Explain how Avro, Protobuf, JSON Schema, and a schema registry help teams evolve event contracts safely. Cover backward and forward compatibility, required versus optional fields, default values, and validation in CI/CD. Include an example of adding a nullable field without breaking existing consumers.
- **Operational reliability and observability**: Explain replication, retention, compaction, consumer lag, dead-letter topics, replay, monitoring, alerting, and capacity planning. Show why Kafka is both an application integration layer and an operational system that needs ownership, runbooks, and SLOs.

Include a Technology Comparison section comparing **Event-Driven Architecture with Apache Kafka** against: RabbitMQ, Apache Pulsar, AWS Kinesis, and Redis Streams.

Use a concise comparison table that evaluates each alternative by:
- Performance characteristics: latency, throughput, resource usage
- Developer experience: learning curve, tooling, documentation
- Ecosystem maturity: community size, library support, enterprise adoption
- When to choose that alternative over Kafka

Include a Migration Guide for teams moving from **a monolithic REST API with synchronous database calls** to **Event-Driven Architecture with Apache Kafka**. Keep it concise but preserve these details:
- Pre-migration checklist and risk assessment
- Domain event identification and ownership
- Data migration and backfill strategy
- API stability and breaking-change handling
- Incremental rollout plan
- Rollback plan
- Validation, smoke tests, and observability checks
- Expected timeline for a team of 4-6 engineers

Formatting requirements:
- Use GitHub-Flavored Markdown.
- Use fenced code blocks with language identifiers.
- Use tables for comparison data.
- Use admonition-style callouts formatted as `> **Note:** ...` for important points.
- Use anchor links in the Related Topics section.
- Include practical code or architecture examples where they clarify implementation choices.