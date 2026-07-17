# Study-Local Reusable Template Library

This folder contains the matched reusable-template controls for the WeaveMark
studies. It is intentionally scoped to `studies/` so these template partials do
not become part of the main WeaveMark reusable-spec library.

The controls use a deterministic partial renderer:

```bash
python studies/template-library/render.py \
  studies/<study>/specs/01-control-template-<name>.weavemark.md \
  studies/<study>/inputs/template-vars.json \
  --output studies/<study>/outputs/compiled-prompts/01-control-template-<name>.md
```

Supported syntax:

- `{{ variable_name }}` substitutes a value from the study-local JSON file.
- `{{> path/to/partial }}` includes `studies/template-library/partials/path/to/partial.md`.

These controls are deliberately strong: reusable template partials can carry the
same reusable domain obligations that WeaveMark reusable specs carry. The study
therefore compares deterministic section assembly with WeaveMark semantic
refinement and mingling.
