# VALE3 Market Snapshot replay

This public bundle strictly replays compilation of `library:market-snapshot`
with the synthetic VALE3 inputs used by the checked-in example.

```bash
weavemark library market-snapshot --replay --verbose \
  --output vale3-market-prompt.md
```

Replay validates the source, inputs, compiler prompt, schema, configuration, and
recorded call hashes without network access. It replays compilation only: the
finance/search effects and HTML packaging do not run.

The verbose footer also reports telemetry retained from the original complete
run: 11,002 input tokens, 0 cached input tokens, 20,728 output tokens, $0.3384
provider-reported API cost, and 177.2 seconds elapsed.
