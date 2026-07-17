# Changelog

## 0.8.0

WeaveMark 0.8 is the first unified processor, language, extension, and
provenance release.

### Added

- Optional compilation provenance manifests.
- Sensitive, explicit run recording and strict offline replay.
- Provider-reported token, latency, and cost aggregation.
- Typed diagnostics with stable codes and JSON rendering.
- Per-surface debug logging policy with binary omission, rotation, retention,
  and restrictive permissions.
- `weavemark --version` and `weavemark.__version__`.
- Experimental default-on promplet protection boundaries.

### Changed

- The current language version is 0.8.
- `CompositionResult` is now owned by the compilation result layer rather than
  the controller.
- Invalid variables files, output formats, runtime configuration, and numeric
  FSLM options fail explicitly instead of producing tracebacks or fallbacks.
- `lm-eval` moved from the core install to the `benchmarking` extra.
- Core and optional dependencies now have explicit compatible upper bounds.
- Full-resolution showcase PNG/PDF outputs moved to narrowly scoped Git LFS
  tracking; lightweight site previews remain in ordinary Git.
- Repository and distribution artifact/size gates reject generated dependency
  trees, caches, package binaries, oversized ordinary files, and leaked LFS
  pointers.

### Compatibility

Promplets declaring language version 0.7 remain supported. An omitted
`@promplet` declaration means “use the current processor language,” currently
0.8. See [Migrating to 0.8](docs/migrating-to-0.8.md).
