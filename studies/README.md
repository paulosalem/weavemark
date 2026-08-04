# WeaveMark Studies

The study corpus is split into two evidence classes:

| Folder | Purpose | Main report |
|---|---|---|
| [`controlled-studies/`](controlled-studies/) | Matched control-versus-treatment studies with `[C1]`, `[C2]`, `[T]`, contrastive blind* scores, and per-study ablation/quality reports. | [`controlled-studies/results.md`](controlled-studies/results.md) / [`controlled-studies/results.html`](controlled-studies/results.html) |
| [`runtime-studies/`](runtime-studies/) | Focused engine, reasoning-strategy, benchmark, and specialized executable investigations kept outside the curated public examples. | Each study owns its runner and saved outputs. |

Focused runtime studies include the
[audience-conditioned release decision study](runtime-studies/audience-conditioned-release-decision/),
which compares one-sentence controls with compiled evidence-quality and
decision-gate treatments using saved downstream responses.

Read [`AGENTS.md`](AGENTS.md) for the operational contract before changing
studies, examples, reports, or evaluation scripts.

## Updating reports

Controlled studies are regenerated from checked-in study sources and saved
compiled outputs:

```bash
python studies/tools/regenerate_reports.py --clear
```

Structural WeaveMark scans require no model calls:

```bash
find studies specs examples -name '*.weavemark.md' -print0 |
  xargs -0 -n1 weavemark --scan >/dev/null
```
