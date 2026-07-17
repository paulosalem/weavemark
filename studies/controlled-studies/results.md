# WeaveMark Studies Result

[View as HTML](results.html)


## Bottom line

**Criterion-aware blind* scores are now the primary comparative signal wherever available.** WeaveMark's strongest result remains single-output semantic reuse with structural mingling: reusable specifications are adapted into one final artifact instead of appended as deterministic sections. The reports also show failures clearly: matched templates often remain denser, and matched prose can beat `@expand` on raw information yield.

Variant markers are preserved throughout the studies: [C1] is the compact/manual control, [C2] is the strongest matched control, and [T] is the WeaveMark treatment.


## Key insights

- **Exploratory score signal:** +89* aggregate across 9 single-output studies in this corpus (9 positive deltas, 0 neutral, 0 negative deltas).
- **Pattern in positive deltas:** within this corpus, reusable refinements score best when they create **semantic structure** mingled through one final artifact.
- **Largest positive blind deltas:** Learning Tutor (+14), Evidence-to-Decision Workspace (+11), Orbital Drift (+11), Verdant Relay (+11).
- **Negative deltas:** none in the active score source.
- **Best honest claim:** WeaveMark is evidence for **reusable specification refinement and structural mingling**, not a blanket claim that every output is shorter, denser, or behaviorally better.
- **Blindness caveat (*):** Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.

## Study coverage

| Study | What the example is | Study role |
|---|---|---|
| [Release Readiness Workbench](release-readiness-workbench-ablation-study) | A local-first release command center that turns release notes, docs, validation runs, screenshots, package artifacts, risks, waivers, and go/no-go decisions into one auditable workspace. | Headline structural-mingling evidence. |
| [Intelligence-to-Execution Kanban](intelligence-execution-kanban-ablation-study) | A local-first Kanban board for monitoring selected topics, turning signals into cards, deciding actions, delegating work, tracking status, and preserving output lineage. | Headline structural-mingling evidence. |
| [Evidence-to-Decision Workspace](evidence-decision-workspace-ablation-study) | A local-first analyst workspace that turns documents, notes, links, news, claims, contradictions, options, decisions, and follow-up actions into an auditable decision surface. | Headline structural-mingling evidence. |
| [Learning Tutor](learning-tutor-refinement-ablation-study) | A pasteable linear-algebra tutor prompt that teaches through geometric intuition, Socratic questions, misconception diagnosis, adaptive practice, and delayed review. | Supporting refinement evidence. |
| [Research Brief](research-brief-ablation-study) | A concise research-brief instruction for energy-storage strategy that requires source families, context limits, contradictions, alternatives, caveats, and explainable evidence handling. | Supporting refinement evidence. |
| [Orbital Drift](games/orbital-drift-racing-ablation-study) | A browser racing game about piloting a small craft through asteroid fields, gravity wells, orbital gates, lap routing, hazards, scoring, restart, and browser validation. | Supporting game-programming specification evidence. |
| [Verdant Relay](games/verdant-relay-ablation-study) | A browser game about defending a living railway garden from blight by combining tower-defense route pressure, deckbuilder card choices, ecosystem feedback, original assets, and browser validation. | Headline-compatible structural-mingling stress test. |
| [Transit City Swarm](games/transit-city-swarm-ablation-study) | A browser strategy game that combines transit-network drawing, city growth, and ant-colony pathfinding through pheromone-style demand trails and congestion feedback. | Focused expansion evidence with a matched-prose comparison. |
| [Crowd Factory Puzzle](games/crowd-factory-puzzle-ablation-study) | A browser puzzle game about steering autonomous crowds through factory automation, belts, machines, crates, spatial pushing rules, hazards, and readable level constraints. | Focused expansion evidence where source concepts are already concrete. |

## Metric definitions

- **Source words:** Words in the local study source for a variant; this is the local authoring burden.
- **Variable words:** Words in a variant's explicit input payload, when a template or refinement uses one.
- **Output words:** Words in the saved compiled final artifact.
- **Leverage:** Output words divided by local source words; larger means more final artifact per local word, not quality by itself.
- **Fact units:** Novelty-weighted semantic fact units extracted from the output by deterministic rules.
- **Density:** Discounted fact units per 1,000 output words; higher means a more information-dense output.
- **Yield:** Discounted fact units per 1,000 local source words; higher means more semantic material per local authoring word.
- **Contrastive score:** A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.
- **Total score:** The sum of the seven contrastive criterion scores for one study.
- **Score color:** Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.
- **Derived-evidence packet:** An anonymous packet containing automated metrics and extracted fact candidates instead of raw source/output text.
- **Blind absolute score:** An anonymous 1..7 criterion score assigned before applying the derandomization key; higher is better.
- **Blind delta:** Treatment absolute score minus control absolute score, mapped back to the -3..+3 contrastive scale after reveal.
- **Direct marker leaks:** Remaining direct labels such as [C1], [C2], [T], WeaveMark, control/treatment, or directives after masking.

## Post-reveal treatment-control metrics

| Study | Control | Treatment | Control leverage | Treatment leverage | Control fact units | Treatment fact units | Control yield | Treatment yield | Main failure |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| [Release Readiness Workbench](release-readiness-workbench-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | 15.72x | 19.2x | 97.75 | 322 | 1,437.5 | 1,298.4 | [T] WeaveMark treatment loses information density: 67.6 versus 91.4 for [C2] Matched reusable-template control. |
| [Intelligence-to-Execution Kanban](intelligence-execution-kanban-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | 16.4x | 19.07x | 96.75 | 137.75 | 1,488.5 | 629 | [T] WeaveMark treatment loses information density: 33 versus 90.8 for [C2] Matched reusable-template control. |
| [Evidence-to-Decision Workspace](evidence-decision-workspace-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | 16.3x | 26.63x | 96.5 | 396.5 | 1,440.3 | 1,592.4 | [T] WeaveMark treatment loses information density: 59.8 versus 88.4 for [C2] Matched reusable-template control. |
| [Learning Tutor](learning-tutor-refinement-ablation-study) | [C2] Matched prose control | [T] WeaveMark treatment | 1x | 12.6x | 18 | 141.25 | 76.3 | 861.3 | [T] WeaveMark treatment loses information density: 68.4 versus 76.3 for [C2] Matched prose control. |
| [Research Brief](research-brief-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | 8.1x | 8.34x | 22 | 113.5 | 536.6 | 551 | [T] WeaveMark treatment loses information density: 66.1 versus 66.3 for [C2] Matched reusable-template control. |
| [Orbital Drift](games/orbital-drift-racing-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | 11.02x | 22.81x | 55 | 228.25 | 901.6 | 1,501.6 | [T] WeaveMark treatment loses information density: 65.8 versus 81.8 for [C2] Matched reusable-template control. |
| [Verdant Relay](games/verdant-relay-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | 11.36x | 18.37x | 83 | 289.5 | 988.1 | 955.4 | [T] WeaveMark treatment loses information density: 52 versus 87 for [C2] Matched reusable-template control. |
| [Transit City Swarm](games/transit-city-swarm-ablation-study) | [C2] Matched-prose no-expand control | [T] Expanded WeaveMark treatment | 7.83x | 16.36x | 95 | 213.5 | 527.8 | 1,206.2 | The matched-prose control remains the fairness baseline because it spells out the same inspiration set without `@expand`. |
| [Crowd Factory Puzzle](games/crowd-factory-puzzle-ablation-study) | [C2] Matched-prose no-expand control | [T] Expanded WeaveMark treatment | 7.22x | 17.46x | 89.25 | 244.75 | 490.4 | 1,281.4 | The source concepts are concrete enough that manual prose can unpack them very effectively. |

## Contrastive gain/loss scores (primary blind*)

Scores compare each [T] WeaveMark treatment against the strongest listed control on the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better). Where a revealed blind run is available, these are criterion-aware blind* scores.

| Study | Control | Treatment | Authoring leverage | Information yield | Grounded expressiveness | Input readability | Output readability | Constraint integration | Reusable abstraction | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Release Readiness Workbench](release-readiness-workbench-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | +2 | -2 | +2 | +1 | +1 | +2 | +1 | +7 |
| [Intelligence-to-Execution Kanban](intelligence-execution-kanban-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | +2 | -2 | +2 | +1 | +1 | +2 | +1 | +7 |
| [Evidence-to-Decision Workspace](evidence-decision-workspace-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | +2 | +2 | +2 | +1 | +1 | +2 | +1 | +11 |
| [Learning Tutor](learning-tutor-refinement-ablation-study) | [C2] Matched prose control | [T] WeaveMark treatment | +3 | +2 | +3 | -1 | +2 | +3 | +2 | +14 |
| [Research Brief](research-brief-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | +2 | +2 | +1 | +1 | +1 | +1 | +1 | +9 |
| [Orbital Drift](games/orbital-drift-racing-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | +2 | +2 | +2 | +1 | +1 | +2 | +1 | +11 |
| [Verdant Relay](games/verdant-relay-ablation-study) | [C2] Matched reusable-template control | [T] WeaveMark treatment | +2 | +2 | +2 | +1 | +1 | +2 | +1 | +11 |
| [Transit City Swarm](games/transit-city-swarm-ablation-study) | [C2] Matched-prose no-expand control | [T] Expanded WeaveMark treatment | +3 | +3 | +1 | -1 | +0 | +1 | +1 | +8 |
| [Crowd Factory Puzzle](games/crowd-factory-puzzle-ablation-study) | [C2] Matched-prose no-expand control | [T] Expanded WeaveMark treatment | +3 | +3 | +2 | -1 | +1 | +2 | +1 | +11 |

## Aggregate signal

### Headline subset

- Strongest controls: 284 local source words, 4,181 output words, 374 discounted fact units.
- Treatments: 1,019 local source words, 21,138 output words, 1,145.75 discounted fact units.

### Full study corpus

- Strongest controls: 984 local source words, 8,145 output words, 653.25 discounted fact units.
- Treatments: 1,909 local source words, 34,618 output words, 2,087 discounted fact units.

## Primary blind* score source

The contrastive score tables above use this criterion-aware blind* result wherever a compatible revealed score exists. Mechanical criteria use derived evidence; criteria that require reading use masked source/output review. Identities are revealed only after scores are frozen.

- Run: [20260710T1416-iterate-final](../../outputs/studies/blind-analysis/20260710T1416-iterate-final/derandomized-report.md)
- Mode: `source-and-output`; score source: `hybrid-derived-metrics-and-masked-review`.
- Anonymous packets checked for direct marker leaks: 27.
- Direct marker leaks after masking: 0.
- Aggregate blind contrastive delta*: **+89**.
- **Leakage-risk note (*):** Hybrid blind* scoring uses derived metrics for mechanical criteria and masked source/output review for criteria that require actual reading. The masked review is less blind because domain content, source syntax, or style can leak, but this is necessary to avoid replacing readability and integration judgments with weak length/density proxies.

| Study | Primary blind* delta |
|---|---:|
| Crowd Factory Puzzle | +11 |
| Evidence-to-Decision Workspace | +11 |
| Learning Tutor | +14 |
| Orbital Drift | +11 |
| Release Readiness Workbench | +7 |
| Research Brief | +9 |
| Transit City Swarm | +8 |
| Verdant Relay | +11 |
| Intelligence-to-Execution Kanban | +7 |

### Criterion-specific blindness

| Criterion | Blindness level | Why this method is used | Leakage risk |
|---|---|---|---|
| Authoring leverage | derived-evidence | Ranked from local leverage without exposing variant identity. | Low: uses automated counts and ratios only. |
| Constraint integration | masked-source-output review | Independent review reads masked source/output to judge whether constraints are woven into the artifact. | Moderate: domain content and artifact structure may leak. |
| Grounded expressiveness | masked-source-output review | Independent review reads masked source/output because richness and grounding are semantic judgments. | Moderate: domain content and style may leak even after identity masking. |
| Information yield | derived-evidence | Ranked from discounted fact units per local source word. | Low-to-moderate: fact extraction reads artifacts, but scoring uses derived counts. |
| Input readability | masked-source review | Independent review reads masked source text because readability is not reducible to source length. | Moderate: source syntax/style may reveal the authoring approach. |
| Output readability | masked-output review | Independent review reads masked output text because readability is not reducible to density or brevity. | Moderate: output style/domain content may leak. |
| Reusable abstraction quality | masked-source review | Independent review reads masked source to judge abstraction clarity and reuse. | Moderate-to-high: abstraction syntax can leak authoring style, but reading it is necessary for reliability. |

## Post-reveal qualitative gains and failures

### Release Readiness Workbench

- **What it is:** A local-first release command center that turns release notes, docs, validation runs, screenshots, package artifacts, risks, waivers, and go/no-go decisions into one auditable workspace.
- **Best gain:** [T] WeaveMark treatment wins source-only leverage: 19.2 versus 15.72 for [C2] Matched reusable-template control.
- **Important failure/caveat:** [T] WeaveMark treatment loses information density: 67.6 versus 91.4 for [C2] Matched reusable-template control.
- **Conclusion:** A strong headline study, with the honest caveat that the template remains denser and more source-efficient on the yield proxy.

### Intelligence-to-Execution Kanban

- **What it is:** A local-first Kanban board for monitoring selected topics, turning signals into cards, deciding actions, delegating work, tracking status, and preserving output lineage.
- **Best gain:** [T] WeaveMark treatment wins source-only leverage: 19.07 versus 16.4 for [C2] Matched reusable-template control.
- **Important failure/caveat:** [T] WeaveMark treatment loses information density: 33 versus 90.8 for [C2] Matched reusable-template control.
- **Conclusion:** A strong realistic study for semantic propagation, with a measured density/yield loss that should stay visible.

### Evidence-to-Decision Workspace

- **What it is:** A local-first analyst workspace that turns documents, notes, links, news, claims, contradictions, options, decisions, and follow-up actions into an auditable decision surface.
- **Best gain:** [T] WeaveMark treatment wins source-only leverage: 26.63 versus 16.3 for [C2] Matched reusable-template control.
- **Important failure/caveat:** [T] WeaveMark treatment loses information density: 59.8 versus 88.4 for [C2] Matched reusable-template control.
- **Conclusion:** The strongest realistic application result on total semantic content and yield, though not on compactness.

### Learning Tutor

- **What it is:** A pasteable linear-algebra tutor prompt that teaches through geometric intuition, Socratic questions, misconception diagnosis, adaptive practice, and delayed review.
- **Best gain:** [T] WeaveMark treatment wins source-only leverage: 12.6 versus 1 for [C2] Matched prose control.
- **Important failure/caveat:** [T] WeaveMark treatment loses information density: 68.4 versus 76.3 for [C2] Matched prose control.
- **Conclusion:** A strong supporting non-programming result, especially on leverage and yield versus matched prose.

### Research Brief

- **What it is:** A concise research-brief instruction for energy-storage strategy that requires source families, context limits, contradictions, alternatives, caveats, and explainable evidence handling.
- **Best gain:** [T] WeaveMark treatment wins source-only leverage: 8.34 versus 8.1 for [C2] Matched reusable-template control.
- **Important failure/caveat:** [T] WeaveMark treatment loses information density: 66.1 versus 66.3 for [C2] Matched reusable-template control.
- **Conclusion:** A modest but realistic supporting win whose value is quality-lens integration more than raw metric dominance.

### Orbital Drift

- **What it is:** A browser racing game about piloting a small craft through asteroid fields, gravity wells, orbital gates, lap routing, hazards, scoring, restart, and browser validation.
- **Best gain:** [T] WeaveMark treatment wins source-only leverage: 22.81 versus 11.02 for [C2] Matched reusable-template control.
- **Important failure/caveat:** [T] WeaveMark treatment loses information density: 65.8 versus 81.8 for [C2] Matched reusable-template control.
- **Conclusion:** A strong game-specification result, best used as supporting implementation-spec evidence rather than the main claim.

### Verdant Relay

- **What it is:** A browser game about defending a living railway garden from blight by combining tower-defense route pressure, deckbuilder card choices, ecosystem feedback, original assets, and browser validation.
- **Best gain:** [T] WeaveMark treatment wins source-only leverage: 18.37 versus 11.36 for [C2] Matched reusable-template control.
- **Important failure/caveat:** [T] WeaveMark treatment loses information density: 52 versus 87 for [C2] Matched reusable-template control.
- **Conclusion:** A strong structural-mingling stress test, with length/density and synthetic-domain caveats.

### Transit City Swarm

- **What it is:** A browser strategy game that combines transit-network drawing, city growth, and ant-colony pathfinding through pheromone-style demand trails and congestion feedback.
- **Best gain:** [T] Expanded WeaveMark treatment wins source-only leverage: 16.36 versus 7.83 for [C2] Matched-prose no-expand control.
- **Important failure/caveat:** The matched-prose control remains the fairness baseline because it spells out the same inspiration set without `@expand`.
- **Conclusion:** A useful `@expand` study where compact named inspirations now produce stronger deterministic proxy metrics than matched prose, while still needing behavioral proof.

### Crowd Factory Puzzle

- **What it is:** A browser puzzle game about steering autonomous crowds through factory automation, belts, machines, crates, spatial pushing rules, hazards, and readable level constraints.
- **Best gain:** [T] Expanded WeaveMark treatment wins source-only leverage: 17.46 versus 7.22 for [C2] Matched-prose no-expand control.
- **Important failure/caveat:** The source concepts are concrete enough that manual prose can unpack them very effectively.
- **Conclusion:** A positive `@expand` result: useful for clarity and framing, and currently ahead of matched prose on deterministic proxy metrics.

## What not to claim yet

- Do not claim downstream users or programming agents perform better; that has not been measured.
- Do not treat contrastive scores or semantic-information proxies as behavioral proof.
- Do not treat output length as quality unless added text introduces operational obligations.
- Do not hide negative results: lower density, lower yield, weaker readability, and matched-prose wins are part of the study evidence.

## Reproducibility

Update this report, per-study reports, and the metric snapshot with:

```bash
python studies/tools/blind_analysis.py metric-pass
python studies/tools/regenerate_reports.py --clear
```

Then run structural scans and link checks as described in [AGENTS.md](AGENTS.md).
