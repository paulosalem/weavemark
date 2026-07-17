# WeaveMark Example Studies

Example studies evaluate public examples as examples, not as controlled
comparisons. There is no `[C1]`/`[C2]`/`[T]` contrastive score. Each example is
compiled into its own `examples/.../outputs/` folder, then scored with:

- source/variable/output word counts;
- leverage, fact units, density, and yield;
- a five-part rubric for intention fit, completeness, writing/structure, no
  leakage/pathologies, and direct usefulness.

Main reports:

- [`results.md`](results.md)
- [`results.html`](results.html)

Regenerate from saved example outputs:

```bash
python studies/tools/regenerate_example_studies.py --clear
```

Recompile the curated public examples and then regenerate reports:

```bash
python studies/tools/regenerate_example_studies.py --clear --run-examples
```
