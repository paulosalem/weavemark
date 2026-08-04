# Audience-Conditioned Release Decision Study

This focused synthetic study tests whether two reusable WeaveMark refinements
improve evidence use and decision protocol in a release decision:

- `module:weavemark.std.guidelines.evidence_quality`
- `module:weavemark.std.lenses.decision_gate`

It is a small behavioral case study, not a statistical estimate of average model
performance.

## Question

Given identical synthetic release facts and the same downstream model, does a
compiled WeaveMark treatment produce a better-evidenced and better-structured
decision than a one-sentence manual control?

The study also explores whether `@match` produces meaningfully different
emphasis for:

1. **Implementation Team** - architecture, interfaces, failure modes, and tests;
2. **Release Team** - readiness, user impact, operational risk, and rollback.

## Design

| Factor | Levels |
|---|---|
| Prompt condition | `[C]` one-sentence manual control; `[T]` compiled WeaveMark treatment |
| Audience | Implementation Team; Release Team |
| Synthetic facts | Identical in every cell |
| Downstream model | `gpt-5.6-terra` in every cell |
| Responses | One separately launched subagent response per cell |
| Evaluation | `claude-opus-5` anonymous blind* rubric scoring before variant reveal |

The control task sentence is at most 20 words. The factual payload below that
sentence is identical to the treatment's `@{dev_notes}` value.

## Synthetic tension

Northstar Sync 2.4 is technically incomplete by its engineering gate: a known
concurrency defect violates an audit-event invariant and 17 tests remain
quarantined. The proposed release is nevertheless a narrow, opt-in five-tenant
beta with tested rollback, a fast kill switch, explicit consent, monitoring,
support ownership, and no observed data loss.

This tension is intentional. A defensible response may reject engineering
completion while allowing a bounded beta, provided it states scope, evidence,
conditions, and reversal triggers precisely.

## Primary rubric

Each anonymous response receives 0-4 points on four evidence-quality dimensions
and four decision-protocol dimensions:

### Evidence quality

1. Uses specific facts and metrics.
2. Separates facts, assumptions, and unknowns.
3. Includes counterevidence and tradeoffs.
4. Avoids unsupported claims.

### Decision protocol

1. States an explicit, scoped decision.
2. Applies gates and criteria to evidence.
3. Connects risks to mitigations and owners.
4. Gives conditions, reversal triggers, and next actions.

Audience alignment is a secondary 0-4 score. The two primary subtotals are each
out of 16.

## Files

- [`promplets/treatment.weavemark.md`](promplets/treatment.weavemark.md) - exact
  treatment program.
- [`inputs/scenario.json`](inputs/scenario.json) - canonical synthetic facts.
- [`study.py`](study.py) - deterministic preparation, blinding, reveal, and
  report generation.
- [`run.sh`](run.sh) - direct compilation transcript for both audiences.
- `outputs/prompts/` - controls and compiled treatments.
- `outputs/responses/` - downstream model responses.
- `outputs/provenance/generation-manifest.json` - downstream prompt/response
  hashes, shared generation settings, and publication-normalization disclosure.
- `outputs/blind/` - anonymous evaluator packet and score file.
- `outputs/private/key.json` - reveal key; do not inspect before scoring.
- `results/` - final JSON, Markdown, and HTML comparison.

## Reproduce

From the repository root:

```bash
python studies/runtime-studies/audience-conditioned-release-decision/study.py prepare
zsh -lc 'source ~/.zshenv >/dev/null 2>&1; source ~/.zshrc >/dev/null 2>&1; studies/runtime-studies/audience-conditioned-release-decision/run.sh'
```

After saving the four downstream responses:

```bash
python studies/runtime-studies/audience-conditioned-release-decision/study.py generation-manifest
python studies/runtime-studies/audience-conditioned-release-decision/study.py blind
```

Score only `outputs/blind/packet.md`, save the evaluator JSON to
`outputs/blind/scores.json`, and then reveal:

```bash
python studies/runtime-studies/audience-conditioned-release-decision/study.py report
```

## Interpretation boundary

This is one synthetic fact pattern with one response per cell. It can reveal
mechanisms, omissions, and useful contrasts. It cannot establish a causal
average treatment effect, model-wide reliability, or general superiority of
WeaveMark.

Several rubric dimensions correspond directly to sections mandated by the
treatment's output contract, so scores partly measure format compliance.
Treatment responses are also 4.3x and 6.4x as long. The anonymous IDs
reduce expectation bias, but the distinctive format and length make treatment
identity inferable.

The two treatment prompts came from separate semantic-compilation calls and
differ beyond the explicit audience branch. Compilation ran at temperature 0.3.
The Release Team prompt is about 22% longer and additionally mandates a
five-tenant-versus-narrower adjudication and a risks-and-next-action section
corresponding to a scored rubric dimension. Implementation uniquely frames the
decision as bounded-beta-only; Release asks whether the requested five-tenant
release may proceed. Both assess material claims, but Release expands the
criteria into a definitional table. Audience-specific differences are therefore
exploratory and cannot be attributed solely to `@match`.

One evaluator scored all four responses in one shared packet. The scores have no
repeat or inter-rater reliability estimate.

## Saved result

| Audience | Variant | Reported label* | Words | Evidence /16 | Protocol /16 | Alignment /4 | Total /36 |
|---|---|---|---:|---:|---:|---:|---:|
| Implementation Team | `[C]` Control | conditional go | 105 | 10 | 12 | 3 | 25 |
| Implementation Team | `[T]` Treatment | wait | 453 | 15 | 14 | 3 | 32 |
| Release Team | `[C]` Control | proceed conditionally | 77 | 9 | 12 | 3 | 24 |
| Release Team | `[T]` Treatment | no-go | 493 | 16 | 15 | 4 | 35 |

*Treatment mandated `Gate: go | no-go | wait | investigate`; control did not.
Reported labels are descriptive transcripts, not a comparable scored outcome.
The Release control and treatment both describe a conditioned one-tenant,
24-hour path despite different approval framing; the control also pre-authorizes
expansion to four tenants, while the treatment does not.*

The treatment improved blind* evidence-quality scores by 5 and 7 points and
decision-protocol scores by 2 and 3 points for the Implementation and Release
audiences respectively. Treatment responses were 4.3x and 6.4x as long.
The gain is therefore stronger formulation in this saved case, not a
length-independent or average causal effect.

The exact user-provided treatment source produced a non-fatal mixed-indentation
diagnostic in the live console during both compilations; that console transcript
was not archived. Structural scan and compiled outputs confirmed that the
intended audience branch was selected in each condition. The source remains
unchanged so this study tests the exact program.

See [results/results.md](results/results.md) or
[results/results.html](results/results.html).
