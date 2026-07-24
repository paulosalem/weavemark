# Orion storybook demo

A lightweight web reader for the checked-in generated storybook **Orion and the
Hunt for His Spark**.

The original 1536x1024 PNG pages remain the authoritative generated artifacts
under `examples/saved-artifact-workflows/childrens-book-orion-en/outputs/` and
use Git LFS. This demo contains 960px JPEG derivatives for fast static hosting.

## Provenance

- Source promplet:
  `promplets/catalog/executable/childrens-book.weavemark.md`
- Reusable core:
  `promplets/domains/creative/fragments/illustrated-story-core.weavemark.md`
- Compiled chain:
  `examples/saved-artifact-workflows/childrens-book-orion-en/outputs/compiled-chain.json`
- Tutorial: `docs/tutorial-illustrated.html`

## Run locally

Serve the repository root over HTTP and open:

`http://127.0.0.1:4173/outputs/implementations/orion-storybook/`
