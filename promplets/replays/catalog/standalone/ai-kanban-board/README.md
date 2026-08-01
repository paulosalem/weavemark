# AI Kanban replay

This public bundle records the real semantic compilation call that turned
`library:ai-kanban-board` and its reusable modules into the checked-in software
specification.

```bash
weavemark library ai-kanban-board --replay
```

The command validates the source, compiler prompt, schema, configuration,
imported modules, tool results, and recorded call hashes, then prints the
compiled specification without network access.
