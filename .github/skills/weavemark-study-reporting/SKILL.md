---
name: weavemark-study-reporting
description: Update WeaveMark study reports, metrics, Markdown/HTML companions, contrastive scores, snippets, and validation checks.
---

# WeaveMark Study Reporting

Use this skill whenever changing files under `studies/`, changing
`studies/tools/regenerate_reports.py`, adding/removing study variants, changing
study metrics, or updating study presentation.

## Core contract

WeaveMark studies are self-supporting quality/property studies. They are not
release-positioning artifacts and should not refer to public-release, internal,
or audience framing.

There are two report classes:

1. `studies/controlled-studies/` contains matched control-versus-treatment
   studies. They compare `[C1]` compact/manual controls, `[C2]` strongest matched
   reusable-template or matched-prose controls, and `[T]` WeaveMark treatments.
2. `studies/examples-studies/` contains absolute quality checks for public
   examples. They have no controls and no contrastive scores.

Controlled reports must keep `[C1]`, `[C2]`, and `[T]` everywhere variants appear
in study-facing text, tables, badges, and comparisons.

## Study artifacts

Every kept controlled study has:

```text
studies/controlled-studies/<study-name>/
  README.md
  specs/
  inputs/
  outputs/compiled-prompts/
  results/
    ablation-summary.md
    ablation-summary.html
    final-quality-analysis.md
    final-quality-analysis.html
```

The consolidated report lives at:

```text
studies/controlled-studies/results.md
studies/controlled-studies/results.html
studies/examples-studies/results.md
studies/examples-studies/results.html
```

Markdown and HTML reports are synchronized companions. Do not hand-edit one
without updating `studies/tools/regenerate_reports.py` and writing the matching
companion.

## Evaluation criteria

Controlled studies use exactly these seven criteria:

1. authoring leverage;
2. information yield;
3. grounded expressiveness;
4. input readability;
5. output readability;
6. constraint integration;
7. reusable abstraction quality.

Report both wins and failures. In particular, call out when `[T]` loses
information density, information yield, leverage, readability, or raw fact
units.

Example studies use absolute metrics plus a rubric: intention fit, completeness,
writing/structure, no leakage/pathologies, and direct usefulness. They should
compile examples into their own `examples/.../outputs/` folders and put study
reports under `studies/examples-studies/`.

## Contrastive gain/loss scale

Every controlled per-study and consolidated report must include -3..+3
contrastive gain/loss scoring:

| Score | Meaning |
|---:|---|
| -3 | WeaveMark is dramatically worse. |
| -2 | WeaveMark is much worse. |
| -1 | WeaveMark is slightly worse. |
| 0 | Similar. |
| +1 | WeaveMark is slightly better. |
| +2 | WeaveMark is much better. |
| +3 | WeaveMark is dramatically better. |

Scores compare `[T]` with the strongest relevant control, normally `[C2]`.
Include criterion rationales and a total score.

Keep reusable-element parity across the strongest control and treatment. If the
matched control gets reusable implementation, stack, workspace, domain, game,
asset, validation, or presentation layers, the WeaveMark treatment should get
the closest corresponding `@refine` layers. It may use those layers more
abstractly because mingling specializes them during compilation, but do not omit
reusable capabilities on the treatment side unless the study explicitly calls out
the asymmetry.

Use `@iterate` selectively. The current syntax is `@iterate n`; there is no
criteria string. It is best for directive-dense treatment regions where
individual directive applications may improve through judge/improve reruns, such
as multi-mechanic `@expand` blocks or large mingled `@refine` bodies. Keep
budgets small (`1` or `2`), because each turn adds model calls. If improvement
remains after the budget, compilation returns the best available result with a
warning. Report whether the pilot helped, degraded, changed nothing, or was
impractical against the previous blind* baseline.

## Blind analysis workflow

When checking whether contrastive or qualitative conclusions are biased by
knowing which variant is WeaveMark, run the blind-analysis workflow:

```bash
python studies/tools/blind_analysis.py metric-pass
```

Use the default `derived-evidence` mode unless raw text is explicitly needed.
That mode randomizes variant identities, writes automated metric and extracted
fact evidence under `outputs/studies/blind-analysis/<run>/derived-evidence/`,
writes anonymous evaluator packets under `packets/`, records anonymous scores,
validates artifact/score coverage, and reveals identities only in the final
derandomized Markdown/HTML/JSON reports.

Do not open `private/key.json` until anonymous scoring is complete. Raw-text
modes (`compiled-output` and `source-and-output`) are identity-blinded but can
still leak framework syntax or authoring style. Prefer derived evidence because
it lets scripts read source/output first, so the evaluator mostly sees counts,
measurements, and extracted fact candidates.

For final comparative reports, prefer criterion-aware hybrid blinding:

- authoring leverage and information yield can use derived metric scoring;
- grounded expressiveness, input readability, output readability, constraint
  integration, and reusable abstraction quality require masked source/output
  review by a context that does not know the intended treatment/control story.

The hybrid flow is:

```bash
python studies/tools/blind_analysis.py prepare --run-id <run> --mode source-and-output --force
# write blinded_scores.qualitative.json from anonymous masked packets
python studies/tools/blind_analysis.py score-hybrid outputs/studies/blind-analysis/<run> \
  --qualitative-scores outputs/studies/blind-analysis/<run>/blinded_scores.qualitative.json
python studies/tools/blind_analysis.py reveal outputs/studies/blind-analysis/<run> \
  --scores outputs/studies/blind-analysis/<run>/blinded_scores.hybrid.json
python studies/tools/regenerate_reports.py --clear
```

When a compatible derandomized blind JSON report exists, generated reports should
use its revealed criterion-aware blind* scores as the primary contrastive score source
wherever feasible. Mark these as `blind*` and explain the leakage-risk caveat:
derived metrics minimize identity exposure, while masked source/output review is
less blind but necessary for reliable readability and integration judgments.

Deterministic metric races, source/output links, snippets, and qualitative prose
are post-reveal explanatory context. Label or position them accordingly so the
reader can distinguish blind scoring from post-reveal interpretation.

## Markdown content requirements

Markdown reports must:

- read as standalone study artifacts;
- avoid process history such as "recomputed", "regenerated", "refreshed",
  "revised", or "rerun";
- include a link to the same-stem HTML report;
- include variant metrics, treatment-control comparisons, contrastive scores,
  gains, failures/caveats, and conclusions;
- define the metrics shown, including source words, variable words, output
  words, leverage, fact units, density, yield, contrastive scores, and
  blind-analysis fields when they appear;
- lead consolidated reports with key insights that summarize the main wins,
  losses, and honest claim boundaries;
- include verbatim snippets in final quality analyses;
- avoid compiler-aware wording inside reusable study specs.

Program and game artifacts are implementation specifications: they should be
ready for a human programmer or AI programming agent to implement, not prompts
that ask another model to produce a specification.

## HTML presentation requirements

HTML reports are the glanceable visual surface. HTML reports do not need to mirror the Markdown structure exactly.
They should use whatever HTML-native layout best communicates the result quickly.
They must be very polished, static, self-contained, and readable without any
build step.

Required presentation patterns:

- compact masthead with a concise bottom line; avoid space-consuming decorative
  hero banners;
- at-a-glance KPI cards for the main result;
- compact collapsed metric glossary cards so readers can inspect every displayed
  metric without letting definitions dominate prime report space;
- top insight cards immediately after the KPI row, including both WeaveMark wins
  and losses;
- first-screen variant-marker chips and main treatment-control comparisons
  before catalog-style study coverage;
- semantic color should remain consistent: green gain, red loss, amber/yellow neutral or caveat, and blue/purple neutral focus;
- metric race cards or grouped metric tables that keep numeric comparisons
  compact, prevent long prose from making rows tall, and avoid overflowing or
  awkwardly wrapped numbers in tiny cells;
- bold winner numbers and subdued losing numbers for each direct metric
  comparison;
- compact caveat cards for long findings instead of cramming prose into dense
  metric tables;
- `[C1]`, `[C2]`, and `[T]` badges;
- color-coded score chips whose intensity is proportional to -3..+3 magnitude:
  +3 must read much greener than +1, and -3 much redder than -1;
- result-dominant score tables where score columns get the visual width and
  repeated study/control/treatment names are compact context, not wide columns;
- consolidated score tables should use compact heatmap-style cells when possible:
  short headers, compact study labels, and full comparison names outside the
  width-critical matrix;
- gain/loss callout cards;
- verbatim snippet cards with quoted source/output material;
- links back to the same-stem Markdown report;
- no external assets, no JavaScript dependency, and no hidden network calls.

The HTML should make the main result understandable at a glance while keeping
the detailed evidence inspectable.

## Update command

From the repository root:

```bash
python studies/tools/regenerate_reports.py --clear
python studies/tools/regenerate_example_studies.py --clear
```

This updates controlled metrics/reports and example-study metrics/reports from
saved source and compiled-output artifacts. It does not call an LLM and it does
not compile WeaveMark sources.

To refresh example outputs before reporting, run:

```bash
python studies/tools/regenerate_example_studies.py --clear --run-examples
```

## Validation checklist

Run:

```bash
python studies/tools/regenerate_reports.py --clear
find studies -name '*.weavemark.md' -print0 |
  xargs -0 -n1 weavemark --scan >/dev/null
python -m pytest tests/test_studies.py tests/test_weavemark.py::TestWeaveMarkImports::test_specs_exist
```

For the broader non-integration suite, include the local FSLM checkout when it
is available:

```bash
PYTHONPATH='../ellements/ellements-core/src:../ellements/ellements-execution/src:../ellements/ellements-fslm/src:src' \
  python -m pytest -m 'not integration'
```

Also run the existing style checks for touched Python files:

```bash
python -m ruff check studies/tools/regenerate_reports.py tests/test_studies.py tests/test_weavemark.py
python -m black --check studies/tools/regenerate_reports.py tests/test_studies.py tests/test_weavemark.py
```

Finally verify:

- metric row count matches registered variants;
- every generated Markdown report has a same-stem HTML report and vice versa;
- generated reports contain `[C1]`, `[C2]`, `[T]`, -3..+3 scores, total scores,
  and verbatim snippets where applicable;
- generated reports do not contain process-history wording;
- Markdown links resolve;
- no `__pycache__/` folders remain under `studies/`;
- study text files have final newlines and no trailing whitespace.

## Copilot CLI behavioral follow-up

Structural reports do not prove implementation behavior. When a software or
game specification needs behavioral evidence, run the compiled `[T]`
specification in a fresh implementation directory with GitHub Copilot CLI and
record the command, Copilot version, model, date, generated files, and
verification output.

Minimal availability check:

```bash
copilot --version
```

Do not treat a Copilot implementation pass as part of deterministic report
generation. It is a separate behavioral follow-up.
