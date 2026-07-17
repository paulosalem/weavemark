# Blind Study Analysis

Run: `20260709T2106-derived-evidence`
Mode: `derived-evidence`
Score source: `metric-only`

Procedure: variant identities were randomized into anonymous packets, scores were recorded on anonymous IDs, and the private key was applied only for this report.

Caveat: this pass is derived-evidence-blinded. Automated extraction reads raw artifacts first, then the evaluator sees anonymous counts, measurements, and fact candidates. The fact candidates may still carry domain content, but direct variant identity is masked.

## Metric definitions

- **Derived-evidence packet:** An anonymous packet containing automated metrics and extracted fact candidates instead of raw source/output text.
- **Blind absolute score:** An anonymous 1..7 criterion score assigned before applying the derandomization key; higher is better.
- **Blind delta:** Treatment absolute score minus control absolute score, mapped back to the -3..+3 contrastive scale after reveal.
- **Direct marker leaks:** Remaining direct labels such as [C1], [C2], [T], WeaveMark, control/treatment, or directives after masking.
- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.

## Crowd Factory Puzzle

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Compact no-expand control | `A` | 4.86 |
| [C2] Matched-prose no-expand control | `B` | 4.43 |
| [T] Expanded WeaveMark treatment | `C` | 2.71 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 1 | 4 | +2 |
| Information yield | 4 | 1 | -2 |
| Grounded expressiveness | 7 | 4 | -2 |
| Input readability | 4 | 1 | -2 |
| Output readability | 7 | 1 | -3 |
| Constraint integration | 7 | 4 | -2 |
| Reusable abstraction quality | 1 | 4 | +2 |
| **Total** |  |  | **-7** |

## Evidence-to-Decision Workspace

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `C` | 2.71 |
| [C2] Matched reusable-template control | `A` | 4.00 |
| [T] WeaveMark treatment | `B` | 5.29 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 4 | 1 | -2 |
| Output readability | 4 | 1 | -2 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 4 | 7 | +2 |
| **Total** |  |  | **+6** |

## Learning Tutor

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Compact manual | `A` | 2.29 |
| [C2] Matched prose control | `B` | 3.14 |
| [T] WeaveMark treatment | `C` | 5.71 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 1 | 7 | +3 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 1 | 4 | +2 |
| Output readability | 7 | 1 | -3 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 1 | 7 | +3 |
| **Total** |  |  | **+11** |

## Orbital Drift

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `C` | 2.71 |
| [C2] Matched reusable-template control | `A` | 4.00 |
| [T] WeaveMark treatment | `B` | 5.29 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 4 | 1 | -2 |
| Output readability | 4 | 1 | -2 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 4 | 7 | +2 |
| **Total** |  |  | **+6** |

## Release Readiness Workbench

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `A` | 2.29 |
| [C2] Matched reusable-template control | `C` | 4.86 |
| [T] WeaveMark treatment | `B` | 4.86 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 7 | 4 | -2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 4 | 1 | -2 |
| Output readability | 7 | 1 | -3 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 4 | 7 | +2 |
| **Total** |  |  | **+1** |

## Research Brief

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual request | `C` | 2.29 |
| [C2] Matched reusable-template control | `B` | 4.43 |
| [T] WeaveMark treatment | `A` | 5.29 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 7 | 1 | -3 |
| Output readability | 4 | 1 | -2 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 4 | 7 | +2 |
| **Total** |  |  | **+5** |

## Transit City Swarm

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Compact no-expand control | `A` | 5.29 |
| [C2] Matched-prose no-expand control | `B` | 4.86 |
| [T] Expanded WeaveMark treatment | `C` | 1.86 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 1 | -2 |
| Information yield | 4 | 1 | -2 |
| Grounded expressiveness | 7 | 4 | -2 |
| Input readability | 4 | 1 | -2 |
| Output readability | 4 | 1 | -2 |
| Constraint integration | 7 | 4 | -2 |
| Reusable abstraction quality | 4 | 1 | -2 |
| **Total** |  |  | **-14** |

## Verdant Relay

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `C` | 2.71 |
| [C2] Matched reusable-template control | `A` | 4.00 |
| [T] WeaveMark treatment | `B` | 5.29 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 4 | 7 | +2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 4 | 1 | -2 |
| Output readability | 4 | 1 | -2 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 4 | 7 | +2 |
| **Total** |  |  | **+6** |

## Intelligence-to-Execution Kanban

| Variant | Anonymous ID | Mean absolute score |
|---|---:|---:|
| [C1] Manual brief | `A` | 1.86 |
| [C2] Matched reusable-template control | `C` | 5.29 |
| [T] WeaveMark treatment | `B` | 4.86 |

| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |
|---|---:|---:|---:|
| Authoring leverage | 4 | 7 | +2 |
| Information yield | 7 | 4 | -2 |
| Grounded expressiveness | 4 | 7 | +2 |
| Input readability | 7 | 1 | -3 |
| Output readability | 7 | 1 | -3 |
| Constraint integration | 4 | 7 | +2 |
| Reusable abstraction quality | 4 | 7 | +2 |
| **Total** |  |  | **+0** |

## Aggregate blind contrastive signal

Total blind contrastive delta across studies: **+14**.
