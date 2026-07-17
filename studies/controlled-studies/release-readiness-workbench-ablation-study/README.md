# Release Readiness Workbench Ablation Study

This study compares three **single-final-specification** variants for a local-first
release-readiness workbench:

1. a compact manual prompt;
2. a matched reusable-template control rendered from study-local partials;
3. a WeaveMark treatment that uses `@refine` and `@expand` to mingle release
   gates, evidence quality, validation matrices, docs/example readiness, risk,
   decisions, actions, dashboards, notifications, local storage, AI assistance,
   and browser validation into one implementation specification.

The treatment deliberately avoids `@prompt`, `@emit`, and prompt packs. The point
is to test whether WeaveMark can produce a dramatically stronger **single
compiled file** while keeping release-readiness obligations reusable.

## Files

- [`specs/00-control-manual-release-readiness-workbench.weavemark.md`](specs/00-control-manual-release-readiness-workbench.weavemark.md)
- [`specs/01-control-template-release-readiness-workbench.weavemark.md`](specs/01-control-template-release-readiness-workbench.weavemark.md)
- [`specs/02-treatment-promplet-release-readiness-workbench.weavemark.md`](specs/02-treatment-promplet-release-readiness-workbench.weavemark.md)
- [`inputs/template-vars.json`](inputs/template-vars.json)
- [`inputs/promplet-vars.json`](inputs/promplet-vars.json)
- [`outputs/compiled-prompts/`](outputs/compiled-prompts/)
- [`results/ablation-summary.md`](results/ablation-summary.md)
- [`results/final-quality-analysis.md`](results/final-quality-analysis.md)

## Result

The matched reusable-template control is strong and explicit; it uses study-local
partials for release readiness, local-first storage, workspace modules, and
browser validation. The WeaveMark treatment activates reusable release,
evidence, validation, programming, dashboard, notification, decision, and
product-validation layers, then compiles them into one coherent 4,762-word
implementation specification from 241 local authored source words.

The contrastive analysis reports:

- WeaveMark treatment versus matched reusable-template control: **+9 / +21**.
- Authoring leverage: **19.8x** for WeaveMark versus **15.7x** for the template.

See [the consolidated result](../results.md) for the cross-study interpretation.
