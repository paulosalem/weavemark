# Blind Study Analysis

Run: `20260710T1404-iterate-pilot`
Mode: `source-and-output`
Score source: `hybrid-derived-metrics-and-masked-review`

Procedure: variant identities were randomized into anonymous packets, scores were recorded on anonymous IDs, and the private key was applied only for this report.

Caveat: Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.

## Metric definitions

- **Derived-evidence packet:** An anonymous packet containing automated metrics and extracted fact candidates instead of raw source/output text.
- **Blind absolute score:** An anonymous 1..7 criterion score assigned before applying the derandomization key; higher is better.
- **Blind delta:** Treatment absolute score minus control absolute score, mapped back to the -3..+3 contrastive scale after reveal.
- **Direct marker leaks:** Remaining direct labels such as [C1], [C2], [T], WeaveMark, control/treatment, or directives after masking.
- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Criterion-specific blindness

| Criterion | Blindness level | Method | Leakage risk |
|---|---|---|---|
| Authoring leverage | derived-evidence | Ranked from local leverage without exposing variant identity. | Low: uses automated counts and ratios only. |
| Constraint integration | masked-source-output review | Independent review reads masked source/output to judge whether constraints are woven into the artifact. | Moderate: domain content and artifact structure may leak. |
| Grounded expressiveness | masked-source-output review | Independent review reads masked source/output because richness and grounding are semantic judgments. | Moderate: domain content and style may leak even after identity masking. |
| Information yield | derived-evidence | Ranked from discounted fact units per local source word. | Low-to-moderate: fact extraction reads artifacts, but scoring uses derived counts. |
| Input readability | masked-source review | Independent review reads masked source text because readability is not reducible to source length. | Moderate: source syntax/style may reveal the authoring approach. |
| Output readability | masked-output review | Independent review reads masked output text because readability is not reducible to density or brevity. | Moderate: output style/domain content may leak. |
| Reusable abstraction quality | masked-source review | Independent review reads masked source to judge abstraction clarity and reuse. | Moderate-to-high: abstraction syntax can leak authoring style, but reading it is necessary for reliability. |

## Crowd Factory Puzzle

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Compact no-expand control | `B` | 3.86 |
| [C2] Matched-prose no-expand control | `A` | 3.14 |
| [T] Expanded WeaveMark treatment | `C` | 6.00 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 1 | 7 | +3 |
| Information yield | 1 | 7 | +3 |
| Grounded expressiveness | 3 | 6 | +2 |
| Input readability | 6 | 5 | -1 |
| Output readability | 5 | 6 | +1 |
| Constraint integration | 3 | 6 | +2 |
| Reusable abstraction quality | 3 | 5 | +1 |
| **Total** |  |  | **+11** |

## Evidence-to-Decision Workspace

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `B` | 1.71 |
| [C2] Matched reusable-template control | `C` | 4.86 |
| [T] WeaveMark treatment | `A` | 6.29 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 6 | 5 | -1 |
| Output readability | 5 | 5 | +0 |
| Constraint integration | 5 | 7 | +1 |
| Reusable abstraction quality | 6 | 6 | +0 |
| **Total** |  |  | **+6** |

## Learning Tutor

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Compact manual | `C` | 1.71 |
| [C2] Matched prose control | `B` | 3.29 |
| [T] WeaveMark treatment | `A` | 6.57 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 1 | 7 | +3 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 3 | 6 | +2 |
| Input readability | 6 | 6 | +0 |
| Output readability | 4 | 7 | +2 |
| Constraint integration | 3 | 7 | +2 |
| Reusable abstraction quality | 2 | 6 | +2 |
| **Total** |  |  | **+13** |

## Orbital Drift

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `C` | 1.71 |
| [C2] Matched reusable-template control | `A` | 4.71 |
| [T] WeaveMark treatment | `B` | 6.43 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 6 | 5 | -1 |
| Output readability | 5 | 6 | +1 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 6 | 6 | +0 |
| **Total** |  |  | **+8** |

## Release Readiness Workbench

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `B` | 1.71 |
| [C2] Matched reusable-template control | `A` | 5.29 |
| [T] WeaveMark treatment | `C` | 6.00 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 7 | 4 | -2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 6 | 5 | -1 |
| Output readability | 5 | 6 | +1 |
| Constraint integration | 5 | 7 | +1 |
| Reusable abstraction quality | 6 | 6 | +0 |
| **Total** |  |  | **+3** |

## Research Brief

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual request | `A` | 2.14 |
| [C2] Matched reusable-template control | `B` | 4.57 |
| [T] WeaveMark treatment | `C` | 6.14 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 6 | +1 |
| Input readability | 6 | 5 | -1 |
| Output readability | 5 | 6 | +1 |
| Constraint integration | 4 | 6 | +1 |
| Reusable abstraction quality | 5 | 6 | +1 |
| **Total** |  |  | **+7** |

## Transit City Swarm

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Compact no-expand control | `A` | 3.86 |
| [C2] Matched-prose no-expand control | `C` | 3.29 |
| [T] Expanded WeaveMark treatment | `B` | 5.29 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 1 | 7 | +3 |
| Information yield | 1 | 7 | +3 |
| Grounded expressiveness | 3 | 4 | +1 |
| Input readability | 6 | 6 | +0 |
| Output readability | 5 | 5 | +0 |
| Constraint integration | 4 | 4 | +0 |
| Reusable abstraction quality | 3 | 4 | +1 |
| **Total** |  |  | **+8** |

## Verdant Relay

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `B` | 1.71 |
| [C2] Matched reusable-template control | `C` | 4.86 |
| [T] WeaveMark treatment | `A` | 6.43 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 6 | 5 | -1 |
| Output readability | 5 | 6 | +1 |
| Constraint integration | 5 | 7 | +1 |
| Reusable abstraction quality | 6 | 6 | +0 |
| **Total** |  |  | **+7** |

## Intelligence-to-Execution Kanban

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `C` | 2.00 |
| [C2] Matched reusable-template control | `A` | 5.29 |
| [T] WeaveMark treatment | `B` | 6.00 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 7 | 4 | -2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 6 | 5 | -1 |
| Output readability | 5 | 6 | +1 |
| Constraint integration | 5 | 7 | +1 |
| Reusable abstraction quality | 6 | 6 | +0 |
| **Total** |  |  | **+3** |

## Aggregate blind contrastive signal

Total blind contrastive delta across studies: **+66**.
