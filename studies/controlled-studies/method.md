# WeaveMark Study Method

This file is the compact method and evaluation guide for WeaveMark controlled
studies. Keep it synchronized with [../AGENTS.md](../AGENTS.md),
[results.md](results.md), and the generated individual study summaries.

## Study folder contract

Each controlled study should live under
`studies/controlled-studies/<topic>-ablation-study/`. Game studies live under
`studies/controlled-studies/games/<topic>-ablation-study/` with the same inner
shape:

```text
studies/controlled-studies/<topic>-ablation-study/
  specs/
    00-control-manual-<topic>.weavemark.md
    01-control-template-<topic>.weavemark.md
    02-treatment-promplet-<topic>.weavemark.md
    ...
  outputs/
    ...
  results/
    ablation-summary.md
    final-quality-analysis.md
```

Variant files should sort in experimental order, name the ablated capability, and
include `control` or `treatment` in the filename. Reports should label variants
with `[C]`/`[T]` when there is one control and one treatment, or
`[C1]`/`[C2]`/.../`[T]` when there are multiple controls.

## Generated report contract

Report Markdown is generated. After changing source specs, saved outputs,
metrics, or study metadata, run:

```bash
python studies/tools/regenerate_reports.py --clear
```

This clears and rewrites every per-study `results/*.md`, the consolidated
[results.md](results.md), and
[metrics/semantic-information.json](metrics/semantic-information.json). Do not
hand-edit generated reports unless the generator is updated too.

## Evidence levels

| Level | Meaning |
|---|---|
| Structural | Source metrics, directive counts, scans, line counts, reusable-fragment references. |
| Saved-output semantic | Compiled outputs are checked in and inspected with the contrastive criteria. |
| Repeated semantic | Multiple model runs, repeated compiles, or independent reviewers. |
| Behavioral | A downstream human, researcher, or programming agent uses each variant and outcomes are compared. |

Most current studies are structural plus saved-output semantic evidence.

## Optional implementation follow-up

For studies whose compiled output is a software specification, an optional final
step can ask a programming agent to implement the compiled spec. The repository ships
one generic command:

```bash
weavemark implement COMPILED_SPEC --name <name>
```

By default this runs GitHub Copilot CLI in non-interactive mode inside a fresh
implementation directory. The meaning of implementation profiles, path names,
and agent commands is configurable in `weavemark.json`. It is not part of
baseline compilation, because it mutates files, depends on an external agent,
and can vary by model and date.

When using implementation results as study evidence:

1. implement controls and treatment with the same agent, model, continuation
   budget, permissions, and time window;
2. use fresh output directories and keep the original compiled prompts unchanged;
3. save the implementation transcript, generated files, run/test commands, and
   observed failures;
4. record the evidence level as behavioral only after the generated app is run or
   tested, not merely because files were created.

## Baseline rules

Use honest baselines:

1. **Manual prompt:** concise human-written prompt with no directives.
2. **Matched reusable-template control:** deterministic template source plus
   study-local reusable partials under
   [template-library/](template-library/). Reusable template partials should be
   comparable in purpose to the WeaveMark reusable specs used by the treatment.
   Count only the local template shell as local authored material; report
   activated reusable partial size and study variable payloads separately.
3. **WeaveMark source:** use directives only when the study is testing their
   contribution.

Do not prove WeaveMark wins by making the baseline artificially weak. Template
reuse belongs in `studies/template-library/` only; do not add these matched
template partials to the main WeaveMark reusable-spec library.

## Contrastive evaluation

WeaveMark studies use **contrastive evaluation**. The question is not whether an
output can be made large and complete. A reusable template system can also carry
validation rules, failure handling, domain details, and output contracts. The
question is whether WeaveMark gives the author a better source-to-output
relationship than a matched reusable-template or matched-prose control.

Use the strongest fair control as the comparison point:

- for single-output studies, compare against the matched reusable-template
  control;
- for `@expand` studies, compare against both compact no-expand and matched-prose
  no-expand controls.

### Criteria

1. **Authoring leverage**
   Objective ratio: `final output words / local authored source words`, excluding
   reusable assets and variable payloads. Report both control and WeaveMark
   ratios plus activated reusable asset size and variable payload size.

2. **Information yield**
   Compare discounted semantic fact units per 1,000 local authored source words,
   excluding reusable assets and variable payloads. This measures how much
   distinct semantic content the author gets for each local authored source word.

3. **Grounded expressiveness**
   Contrastively judge whether the final WeaveMark output is richer, more
   detailed, and more nuanced than the control because of source/reusable-spec
   semantics, not generic filler.

4. **Input readability**
   Contrastively judge whether the original WeaveMark source is easier to read
   and understand before compilation than the control source and variable
   payload.

5. **Output readability**
   Contrastively judge whether the final compiled output is easier to read,
   navigate, and use than the control output. Longer is not automatically better.

6. **Constraint integration**
   Contrastively judge whether requirements are woven through the whole final
   output or merely appended as isolated notes.

7. **Reusable abstraction quality**
   Judge whether reusable specs are genuine portable abstractions, comparable to
   or better than the template partials, rather than bespoke hidden treatment
   text written only to win one study.

### Sibling refinement behavior

For `@refine` calls whose `mingle` option is absent or true, the compiler sends
the calling spec and all surviving sibling refinement references into one
semantic composition round. The compiler requires the model to read every
referenced spec and produce one coherent final artifact, so sibling refinements
can be integrated with each other in the final output.

This is semantic integration, not deterministic pairwise composition: the
compiler does not first compose refinement A with refinement B and then compose
that result with the caller. Study sources should therefore make cross-sibling
mingling intent explicit when the expected result depends on multiple reusable
layers shaping the same entity, workflow, or validation surface.

### Semantic information metrics

The studies use a deterministic semantic-information proxy saved in
[metrics/semantic-information.json](metrics/semantic-information.json). For each
final output:

1. split the output into chunks;
2. extract atomic actionable/domain-relevant fact candidates from bullets,
   table rows, and sentences;
3. normalize each fact into content tokens;
4. compare each fact to the closest previously counted fact;
5. assign a 0-4 novelty score;
6. sum discounted fact units.

| Difference score | Meaning | Weight |
|---:|---|---:|
| 0 | Identical | 0.00 |
| 1 | Near identical | 0.25 |
| 2 | Similar | 0.50 |
| 3 | Somewhat different | 0.75 |
| 4 | Very different | 1.00 |

Report:

| Metric | Formula | Meaning |
|---|---|---|
| Discounted fact units | Sum of fact weights | Approximate semantic information content |
| Information density | `discounted fact units / 1,000 output words` | How dense the final output is |
| Information yield | `discounted fact units / 1,000 local authored source words` | How much semantic content source authoring buys |

### Contrastive score scale

Scores compare the WeaveMark treatment with the strongest relevant control:

| Score | Meaning |
|---:|---|
| -3 | WeaveMark is dramatically worse. |
| -2 | WeaveMark is much worse. |
| -1 | WeaveMark is slightly worse. |
| 0 | Similar. |
| +1 | WeaveMark is slightly better. |
| +2 | WeaveMark is much better. |
| +3 | WeaveMark is dramatically better. |

Authoring leverage and semantic-information metrics are reported as objective
or deterministic-proxy measurements. Contrastive scores summarize the practical
meaning of those metrics plus qualitative inspection.

These evaluations are still saved-output inspections. They do **not** prove that
downstream users or programming agents perform better. Behavioral proof requires
running downstream implementations or user tasks.

## Single-output structural-mingling checks

Use these checks when a study claims `@refine` or `@expand` improves one final
specification:

1. name the semantic trace that should propagate through the output;
2. inspect objective, entities, workflow or mechanics, data model, UI,
   validation, risks, and acceptance criteria;
3. separate mere mention from operational propagation;
4. reject appendix wins where reusable material appears as an unrelated block;
5. compare against a matched reusable-template control.

## Density and reproducibility checks

Longer outputs are useful only when added text introduces new operational
obligations. A longer treatment should add fields, states, workflows, validation
probes, risks, acceptance criteria, or cross-section consequences.

Before publishing a study claim, record:

1. source variants compared;
2. command or compile mode used;
3. model, date, and whether semantic compilation made live model calls;
4. output paths inspected;
5. contrastive score scale, semantic-information script version, reviewer count,
   and confidence;
6. evidence type: single-output comparison or method guide;
7. whether downstream artifacts were executed or only prepared for later use.

## Update checklist

When changing or adding a study:

1. scan all changed `.weavemark.md` files;
2. save meaningful compiled outputs under the study's `outputs/` folder;
3. run `python studies/tools/regenerate_reports.py --clear`;
4. run Markdown link checks for touched study docs;
5. run `git diff --check` or an explicit whitespace check for untracked study files.

Useful structural check:

```bash
find studies -name '*.weavemark.md' -print0 |
  xargs -0 -n1 weavemark --scan >/dev/null
```
