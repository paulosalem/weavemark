# WeaveMark Studies

The study corpus is split into two evidence classes:

| Folder | Purpose | Main report |
|---|---|---|
| [`controlled-studies/`](controlled-studies/) | Matched control-versus-treatment studies with `[C1]`, `[C2]`, `[T]`, contrastive blind* scores, and per-study ablation/quality reports. | [`controlled-studies/results.md`](controlled-studies/results.md) / [`controlled-studies/results.html`](controlled-studies/results.html) |
| [`examples-studies/`](examples-studies/) | Absolute quality checks for public examples. These inspect compiled example outputs without controls, using semantic metrics plus a rubric for intention fit, writing, leakage/pathology avoidance, completeness, and direct usefulness. | [`examples-studies/results.md`](examples-studies/results.md) / [`examples-studies/results.html`](examples-studies/results.html) |

Read [`AGENTS.md`](AGENTS.md) for the operational contract before changing
studies, examples, reports, or evaluation scripts.

## Updating reports

Controlled studies are regenerated from checked-in study sources and saved
compiled outputs:

```bash
python studies/tools/regenerate_reports.py --clear
```

Example studies can be regenerated from the current saved example outputs:

```bash
python studies/tools/regenerate_example_studies.py --clear
```

To also refresh the compiled public examples before reporting, run:

```bash
python studies/tools/regenerate_example_studies.py --clear --run-examples
```

Structural WeaveMark scans require no model calls:

```bash
find studies specs examples -name '*.weavemark.md' -print0 |
  xargs -0 -n1 weavemark --scan >/dev/null
```
