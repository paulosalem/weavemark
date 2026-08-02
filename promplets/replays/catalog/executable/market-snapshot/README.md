# VALE3 Market Snapshot replay

This public bundle strictly replays `library:market-snapshot` with the synthetic
VALE3 inputs used by the checked-in example, then restores the final artifacts
retained from the original compile-and-execute run.

```bash
weavemark library market-snapshot --replay --verbose --open
```

Replay validates the source, inputs, compiler prompt, schema, configuration,
recorded call hashes, and artifact hashes without network access. The finance
and search effects are not called again: their recorded execution output, trace,
and standalone HTML dashboard are restored byte-for-byte. `--open` opens the
restored `market-dashboard.html`.

The verbose footer also reports telemetry retained from the original complete
run: 11,002 input tokens, 0 cached input tokens, 20,728 output tokens, $0.3384
provider-reported API cost, and 177.2 seconds elapsed.
