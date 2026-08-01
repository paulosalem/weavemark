# Arcana WeaveMark example

Arcana deliberately separates generated game artifacts from software
specification and implementation.

## Two catalog sources

- [`cards.weavemark.md`](../../../promplets/catalog/arcana/cards.weavemark.md) is
  executable. It validates the nested deck, renders the titled prototype,
  remaining fronts, and common back, and emits `deck-data.js`. Run it only when
  this source or `inputs/vars.json` changes.
- [`app.weavemark.md`](../../../promplets/catalog/arcana/app.weavemark.md) is not
  executable. It always recompiles the complete Markdown browser-application
  specification for an interactive programming agent. It generates no images and
  implements no code.

The files sit side by side because they are two first-class Arcana sources with
different lifecycles. All Arcana-specific requirements remain in the catalog;
the app source refines only the reusable software-spec, static-browser,
adaptive-shell, focus-preserving-inspection, and Playwright-validation modules.

[`inputs/vars.json`](./inputs/vars.json) is the complete concrete 55-card deck.
Replace its nested `deck` value to create another compatible deck.

## Build artifacts and compile the app specification

From the WeaveMark repository:

```bash
examples/saved-artifact-workflows/arcana/run.sh
```

The runner contains two explicit WeaveMark invocations:

1. It first validates the deck deterministically with `jq`, then fingerprints
   `cards.weavemark.md` plus `inputs/vars.json`. If the
   source/input/model fingerprint, hydrated PNG signatures, and the SHA-256
   manifest for all 56 generated images match, it compiles without execution to
   refresh `deck-data.js` while reusing the images. Otherwise, or with
   `--regenerate-cards`, the same invocation executes the card pipeline under the
   output directory; WeaveMark streams every PNG and materializes `deck-data.js`,
   then the runner validates unique content and atomically records the artifact
   manifest and new fingerprint.
2. It always recompiles `app.weavemark.md` into
   `outputs/arcana-app-spec.md`.

No Python or JavaScript orchestration script is used.

## Clean-room implementation

Open an interactive programming-agent session in
`examples/saved-artifact-workflows/arcana/outputs/` and give it
`arcana-app-spec.md`. The agent must create `index.html` and `README.md` from an
empty implementation source, without copying or editing a previous runtime.

The generated PNGs and `deck-data.js` are authoritative inputs and must be reused
unchanged. The agent then serves the actual directory and iterates with Playwright
over manual play, every reflection depth, AI/TTS success and failure, card motion,
audio transport, responsive layouts, accessibility, privacy, and final synthesis.

The checked-in `outputs/index.html` is the clean-room implementation produced from
the freshly compiled specification. Manual play remains offline. Optional
`gpt-5.4-mini` reflection and `gpt-4o-mini-tts` narration require explicit consent
and a page-memory-only key.
