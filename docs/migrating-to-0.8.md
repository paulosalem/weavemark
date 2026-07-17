# Migrating to WeaveMark 0.8

## Version policy

The WeaveMark release family is **0.8**:

- Python processor/package: `0.8.0`;
- current language: `0.8`;
- VS Code extension: `0.8.0`.

| Component | 0.8 release | Compatibility contract |
| --- | --- | --- |
| Processor / Python package | `0.8.0` | Implements language 0.8 and accepts maintained 0.7 promplets. |
| WeaveMark language | `0.8` | Defined by the canonical system prompt. |
| VS Code extension | `0.8.0` | Catalog and diagnostics target language 0.8. |
| Ellements | `>=0.2.0` | First compatible release with the required FSLM surface. |
| Desktop | Separate private preview | Versioned and released independently from WeaveMark core. |

Patch releases may fix implementation defects without changing language
semantics. A language change increments the shared minor release family. The
optional `@promplet version:` declaration pins the language contract a promplet
targets; declarations are not package-version requirements.

Promplets that declare `version: 0.7` remain supported by the 0.8 processor.
Maintained promplets should declare a version when they rely on a specific
language contract. Omitting the declaration intentionally targets the current
language version.

## Behavioral changes

- Protections are enabled by default. Use `--no-protections` only for a
  deliberately trusted promplet.
- Invalid `--var`, variables JSON, runtime configuration, output formats, and
  numeric inline-FSLM options now fail with stable diagnostics.
- Debug logging is independently configurable; binary/base64 payloads are
  omitted by default while normal text and variables remain available.
- Provenance and run recording are optional and off by default.
- `lm-eval` is no longer installed with core WeaveMark; install
  `weavemark[benchmarking]` for the strategy-comparison example.
- Full-resolution comic/storybook outputs use Git LFS. Normal source use does
  not require them; run `git lfs pull` when you want the originals.

No semantic compilation mode was removed or replaced: WeaveMark 0.8 continues
to combine deterministic structural support with LLM-based semantic
compilation.

## Optional traceability and replay

```bash
# Metadata and hashes only.
weavemark example.weavemark.md --provenance outputs/example.provenance.json

# Sensitive full-call recording.
weavemark example.weavemark.md --record-run outputs/example-run

# Strict offline replay; never falls back to a provider.
weavemark example.weavemark.md --replay-run outputs/example-run
```

Run recordings can contain full source, variable values, imported content,
tool results, and model responses. Treat them as sensitive artifacts.
