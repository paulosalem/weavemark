# WeaveMark Study Agent Guide

This file is the operational contract for maintaining and regenerating the
WeaveMark study corpus.

## Study purpose

WeaveMark has two study classes:

1. `controlled-studies/` compare source-to-output behavior across:
   - compact manual sources;
   - matched reusable-template or matched-prose controls;
   - WeaveMark treatments using directives such as `@refine`, `@expand`,
     `@iterate`, and scoped `@compress`.
2. `examples-studies/` evaluate public examples in absolute terms. They compile
   examples into their own `examples/.../outputs/` folders, then inspect the
   output with semantic metrics and a quality rubric. They do not have controls,
   `[C1]`/`[C2]`/`[T]` markers, or contrastive gain/loss scores.

The controlled corpus is single-output. Do not add prompt-pack or multi-output
branching studies to that evidence set without creating a separate evidence
class and report section.

## Study corpus

Controlled realistic studies:

- `controlled-studies/release-readiness-workbench-ablation-study/`
- `controlled-studies/intelligence-execution-kanban-ablation-study/`
- `controlled-studies/evidence-decision-workspace-ablation-study/`
- `controlled-studies/learning-tutor-refinement-ablation-study/`
- `controlled-studies/research-brief-ablation-study/`

Controlled game studies live under `controlled-studies/games/`, one folder per
named game:

- `controlled-studies/games/orbital-drift-racing-ablation-study/`
- `controlled-studies/games/verdant-relay-ablation-study/`
- `controlled-studies/games/transit-city-swarm-ablation-study/`
- `controlled-studies/games/crowd-factory-puzzle-ablation-study/`

Example studies live under `examples-studies/` and currently cover curated
plain public examples.

## Folder contract

Each controlled study should keep this shape:

```text
studies/controlled-studies/<study-name>/
  README.md
  specs/
    00-control-...
    01-control-...
    02-treatment-...
  inputs/
    ...
  outputs/compiled-prompts/
    ...
  results/
    ablation-summary.md
    ablation-summary.html
    final-quality-analysis.md
    final-quality-analysis.html
```

Game studies use `studies/controlled-studies/games/<study-name>/` with the same
inner shape.

Example-study outputs use this shape:

```text
studies/examples-studies/
  results.md
  results.html
  metrics/example-quality.json
  <example-id>/
    results.md
    results.html
```

The compiled examples themselves stay under their example folders, e.g.
`examples/terminal-output-only/research-brief/outputs/compiled-prompt.md`.

## Evaluation criteria

For controlled studies, use the criteria in
[controlled-studies/method.md](controlled-studies/method.md):

1. authoring leverage;
2. information yield;
3. grounded expressiveness;
4. input readability;
5. output readability;
6. constraint integration;
7. reusable abstraction quality.

Report failures as first-class findings. In particular, call out when the
WeaveMark treatment loses information density, information yield, leverage,
readability, or raw fact units.

Reusable-element parity is required for fair comparisons. The strongest control
and treatment should have comparable reusable building blocks wherever feasible:
if a matched template uses implementation-spec, stack, workspace, domain, game,
asset, validation, or presentation layers, the WeaveMark treatment should use
the closest corresponding `@refine` layers. The treatment may keep those layers
more abstract because mingling transforms them during compilation, but it should
not omit a reusable capability that the strongest control receives unless the
study explicitly explains why that asymmetry is intentional.

Use `@iterate` selectively. It has no criteria string; write `@iterate n` around
directive-dense treatment regions whose own directive applications may benefit
from judge/improve reruns. Good candidates are multi-mechanic `@expand` blocks or
large mingled `@refine` bodies. Keep pilot budgets small (`1` or `2`) because
each turn adds model calls. If a step still needs material improvement when the
budget is exhausted, compilation returns the best available result with a
warning. Always compare against the previous blind* baseline and classify the
pilot as helped, degraded, unchanged, or impractical.

Each report must include the contrastive gain/loss scale:

| Score | Meaning |
|---:|---|
| -3 | WeaveMark is dramatically worse. |
| -2 | WeaveMark is much worse. |
| -1 | WeaveMark is slightly worse. |
| 0 | Similar. |
| +1 | WeaveMark is slightly better. |
| +2 | WeaveMark is much better. |
| +3 | WeaveMark is dramatically better. |

Use this scale for all seven criteria: authoring leverage, information yield,
grounded expressiveness, input readability, output readability, constraint
integration, and reusable abstraction quality.

For example studies, do not use contrastive scores. Report the same source,
variable, output, leverage, fact-unit, density, and yield metrics, plus a rubric:
intention fit, completeness, writing/structure, no leakage/pathologies, and
direct usefulness.

## Blind analysis workflow

When auditing qualitative or contrastive conclusions for bias, prefer the blind
analysis tool:

```bash
python studies/tools/blind_analysis.py metric-pass
```

The default mode is `derived-evidence`, not raw text. It:

1. randomizes each study variant behind anonymous IDs;
2. writes derived metric and extracted-fact evidence under
   `outputs/studies/blind-analysis/<run>/derived-evidence/`;
3. writes evaluator packets under `outputs/studies/blind-analysis/<run>/packets/`
   that contain metrics and extracted fact candidates, not raw source/output;
4. writes anonymous score templates before revealing any variant identity;
5. keeps the derandomization key under
   `outputs/studies/blind-analysis/<run>/private/key.json`;
6. validates manifest/key/template/score coverage before reveal;
7. writes public derandomized Markdown, HTML, and JSON reports only after
   anonymous scores exist.

Do not open `private/key.json` until blinded scoring is complete. Use
`--mode compiled-output` or `--mode source-and-output` only when raw-text review
is explicitly needed. Raw-text modes are identity-blinded but can still leak
authoring style or framework syntax; the derived-evidence mode minimizes that
exposure by letting automated extraction read the artifacts first.

For final comparative scores, use criterion-aware blinding rather than forcing
every criterion into the same packet type:

- **Derived-evidence / metric-only:** authoring leverage and information yield.
  These can be scored from counts, ratios, and extracted fact-unit proxies
  without direct source/output reading.
- **Masked source/output review:** grounded expressiveness, input readability,
  output readability, constraint integration, and reusable abstraction quality.
  These require actual reading to be reliable. Use a separate context or reviewer
  that only sees anonymous masked packets, not project history or the private
  key. Mark the resulting scores as `blind*` because source syntax, domain
  content, or style can still leak.

Hybrid scoring flow:

```bash
python studies/tools/blind_analysis.py prepare \
  --run-id <run> --mode source-and-output --force
# collect an anonymous masked-review JSON for reading-dependent criteria
python studies/tools/blind_analysis.py score-hybrid \
  outputs/studies/blind-analysis/<run> \
  --qualitative-scores outputs/studies/blind-analysis/<run>/blinded_scores.qualitative.json
python studies/tools/blind_analysis.py reveal \
  outputs/studies/blind-analysis/<run> \
  --scores outputs/studies/blind-analysis/<run>/blinded_scores.hybrid.json
python studies/tools/regenerate_reports.py --clear
```

When a compatible derandomized blind JSON report exists, generated study reports
must use its revealed contrastive deltas as the primary score source wherever
feasible. Mark such scores as `blind*` and include the leakage-risk caveat:
derived metrics minimize identity exposure, while masked source/output review is
less blind but necessary for reliable readability and integration judgments.

Deterministic metric races, source/output links, snippets, and qualitative prose
are post-reveal explanatory context. Keep them labeled or positioned so readers
do not mistake post-reveal interpretation for the blind scoring step.

## Metric and report update

Update controlled-study report artifacts from the repository root:

```bash
python studies/tools/regenerate_reports.py --clear
```

This command:

1. clears every per-study `results/*.md` file;
2. clears `studies/controlled-studies/results.md`;
3. updates `studies/controlled-studies/metrics/semantic-information.json`;
4. extracts verbatim snippets from saved source/output files;
5. rewrites each `results/ablation-summary.md` and `results/ablation-summary.html`;
6. rewrites each `results/final-quality-analysis.md` and
   `results/final-quality-analysis.html`;
7. rewrites the consolidated `studies/controlled-studies/results.md` and
   `studies/controlled-studies/results.html`.

Update example-study report artifacts from saved example outputs:

```bash
python studies/tools/regenerate_example_studies.py --clear
```

Recompile curated examples first when the example outputs themselves should be
refreshed:

```bash
python studies/tools/regenerate_example_studies.py --clear --run-examples
```

Do not hand-edit generated report files unless you also update
`studies/tools/regenerate_reports.py` so the next run preserves the change.

Markdown and HTML reports are synchronized companions. Every generated `.md`
report must have a same-stem `.html` report, and every generated `.html` report
must link back to its `.md` companion.

## HTML presentation contract

HTML reports are the glanceable visual surface. They do not need to mirror the
Markdown structure exactly; they should use the layout that best communicates
the result quickly. They must be self-contained, professional, and easy to read
without any build step:

- use a compact masthead instead of a space-consuming decorative hero, plus
  at-a-glance KPI cards, grouped metric tables, score chips, gain/loss callouts,
  and snippet cards;
- lead with outcomes, variant-marker chips, and the main treatment-control
  comparisons before catalog-style study coverage;
- use semantic color: green for gains, red for losses, amber/yellow for neutral,
  caveats, or similar scores, and blue/purple for neutral focus;
- make contrastive score color intensity proportional to the score magnitude
  (`+3` much greener than `+1`, `-3` much redder than `-1`);
- keep score/result columns visually dominant; compress repeated study/control/
  treatment names into compact context cells rather than wide table columns;
- render consolidated contrastive scores as a compact heatmap-style matrix when
  possible, with short headers and compact study labels; keep full comparison
  names available elsewhere rather than widening the table;
- use metric race cards or other HTML-native layouts when tables would cram
  prose into tall rows; metric-race numbers must not overflow or wrap awkwardly
  inside tiny cells;
- bold or otherwise strongly emphasize the winning numeric value in direct
  comparisons, and keep losing values visible but visually secondary;
- move long caveats/findings into compact callout cards rather than putting them
  in dense metric columns;
- visually group related columns with spacing or divider lines, especially
  authoring-size metrics, semantic-information metrics, and contrastive scores;
- preserve `[C1]`, `[C2]`, and `[T]` markers in badges and table cells;
- show the -3..+3 contrastive score scale in a form that is scannable at a
  glance;
- include verbatim snippets with enough typographic contrast to separate quoted
  source/output material from analysis;
- remain static HTML with no external assets, no JavaScript requirement, and no
  hidden network dependency.

## Source and output regeneration

The report generator uses saved compiled outputs. It does not call an LLM and it
does not recompile WeaveMark sources.

To structurally scan sources without LLM calls:

```bash
find studies -name '*.weavemark.md' -print0 |
  xargs -0 -n1 weavemark --scan >/dev/null
```

To update a compiled output, run the corresponding `weavemark` command for
that study and then update the reports:

```bash
python studies/tools/regenerate_reports.py --clear
```

If a command needs model access, source the local shell environment without
printing secrets:

```bash
zsh -lc 'source ~/.zshrc >/dev/null 2>&1; promplet ...'
```

## Validation checklist

Before finishing a study change, run:

```bash
python studies/tools/regenerate_reports.py --clear
find studies -name '*.weavemark.md' -print0 |
  xargs -0 -n1 weavemark --scan >/dev/null
```

Then verify:

- Markdown links under `studies/` resolve;
- no deleted study folder names remain in reports or tools;
- `studies/controlled-studies/metrics/semantic-information.json` contains all registered controlled variants;
- `studies/examples-studies/metrics/example-quality.json` contains all registered example rows;
- every generated Markdown report has a same-stem HTML report and vice versa;
- no `__pycache__/` folders remain under `studies/`;
- study text files have final newlines and no trailing whitespace.

## Wording rules

- Program and game artifacts are implementation specifications, not prompts that
  ask another model to produce specifications.
- Non-programming prompt studies may use "prompt" when the artifact really is a
  prompt, as in the Learning Tutor and Research Brief studies.
- Reports and results must read as standalone study artifacts. Do not say that
  results were recomputed, regenerated, refreshed, revised, or rerun; those are
  process details, not study conclusions.
- Qualitative analysis must include verbatim snippets from the compared source
  and output artifacts.
- Always preserve explicit variant markers in study-facing text and tables:
  `[C1]`, `[C2]`, and `[T]` for controls and treatment.
- Per-study summaries, final quality analyses, and consolidated results must
  include the -3..+3 contrastive gain/loss scores, criterion rationales where
  applicable, and total score. Prefer criterion-aware blind* scores over
  visible-review scores when the current blind reveal artifact covers that study.
- reports must define the metrics they show. In particular, HTML reports should
  include a compact, collapsed metric glossary explaining source words, variable
  words, output words, leverage, fact units, density, yield, contrastive scores,
  and blind-analysis fields when those appear.
- Do not frame studies as being for a public release, public corpus, public
  narrative, or internal/public audience. They are simply studies of WeaveMark
  quality and properties.
- Use concrete example names in study titles: Orbital Drift, Verdant Relay,
  Transit City Swarm, and Crowd Factory Puzzle.
- Use "program", "programming", and "implementation" terminology where relevant.
