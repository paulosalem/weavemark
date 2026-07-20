# Example promplets

Use this catalog when you want a real promplet to study, compile, adapt, or use
as a starting point. The root `promplets/` library has a release-facing convention:

- `stdlib/` contains general prelude, definition, and fragment modules;
- `domains/` contains domain-specific reusable modules and fragments;
- `catalog/standalone/` contains complete compile-oriented promplets;
- `catalog/executable/` contains engine, tool, collaborative, and artifact workflows;
- `tutorials/` and `experimental/` make teaching and maturity explicit.

See [`promplets/README.md`](../promplets/README.md) for the directory-level contract.

## How to read this catalog

- Start with **Final promplets** when you want pastable prompt artifacts.
- Browse **Reusable library fragments** when you want shared lenses, policies,
  reasoning patterns, or programming/product layers.
- Use **Executable promplets** when you want the WeaveMark Processor or a trusted
  runtime to run prompt behavior rather than only produce text.

## Final promplets

These complete promplets can be compiled or studied directly.

| WeaveMark | Directives used | Description |
|---|---|---|
| `catalog/standalone/financial-independence-decision.weavemark.md` | `@refine` | README flagship analysis prompt: financial-independence decision using shared financial specs, MECE, optionality, and resilience lenses. |
| `catalog/standalone/financial-independence-goal-plan-prompt.weavemark.md` | `@use`, `@refine`, `@goal_plan` | Advanced tutorial prompt that imports a reusable semantic macro and turns a simple financial-independence goal into a pastable planning prompt. |
| `catalog/standalone/investment-brief.weavemark.md` | `@refine`, `@match`, `@if`, `@output`, `@assert` | Tutorial companion prompt for a sober educational investment brief with evidence, risks, alternatives, watchlist triggers, and finance-safety constraints. |
| `catalog/standalone/live-investment-decision-brief.weavemark.md` | `@refine` | Companion-runtime investment-learning prompt that combines finance safety, context sufficiency, evidence quality, news quality, comparative alternatives, explainability, and risk-free benchmark lenses. |
| `catalog/standalone/messy-notes-action-plan.weavemark.md` | `@refine` | Pastable prompt that turns scattered notes, transcripts, and fragments into a faithful action plan. |
| `catalog/standalone/deep-summary-prompt.weavemark.md` | `@refine` | Pastable prompt for layered summaries with evidence, implications, risks, gaps, and action items. |
| `catalog/standalone/decision-advisor.weavemark.md` | `@refine` | Pastable decision-support prompt combining strategic framing, optionality, alternatives, explainability, and decision gates. |
| `catalog/standalone/learning-tutor.weavemark.md` | `@refine` | Pastable tutor prompt that adapts explanation, examples, practice, and checks to the learner. |
| `catalog/standalone/research-brief.weavemark.md` | `@refine` | Pastable research brief prompt with source-family coverage, evidence grading, web-access limits, and next searches. |
| `catalog/standalone/prompt-refiner.weavemark.md` | `@refine` | Pastable prompt-improvement prompt for turning rough prompts into clear, reusable instructions. |
| `catalog/standalone/iterative-onboarding-prompt.weavemark.md` | `@iterate`, `@ask` | Demonstrates compile-time judge/improve iteration with a leading `@ask` wrapper as the iteration target. |
| `catalog/standalone/program-debugging-assistant.weavemark.md` | `@refine` | Pastable programming-debugging prompt for root-cause hypotheses, diagnostics, minimal fixes, and verification. |
| `catalog/standalone/passive-income-planning-dashboard.weavemark.md` | `@refine` | Local-first passive-income planning dashboard using the same financial fragments in a software context. |
| `catalog/standalone/news-intelligence-board.weavemark.md` | `@refine` | News/events intelligence board that reuses workflow modules and durable memory to suppress duplicate coverage and resurface material updates. |
| `catalog/standalone/mece-structuring.weavemark.md` | `@refine`, `@if`, `@note` | Final MECE structuring prompt built on the reusable MECE core. |
| `catalog/standalone/analysis-of-competing-hypotheses.weavemark.md` | `@refine`, `@if`, `@note` | Final ACH prompt for testing competing explanations against evidence. |
| `catalog/standalone/issue-tree-analysis.weavemark.md` | `@refine`, `@if`, `@note` | Final issue-tree prompt for consulting-style problem decomposition. |
| `catalog/standalone/creative-ideation.weavemark.md` | `@match`, `@refine` | Final ideation prompt that selects one reusable method and semantically mingles it with the caller's concrete subject, objective, and constraints. |
| `catalog/standalone/multi-persona-debate.weavemark.md` | `@refine`, `@expand`, `@revise`, `@match`, `@if`, `@output` | Final debate prompt that composes a reusable multi-persona debate method. |
| `catalog/standalone/adaptive-interview.weavemark.md` | `@refine`, `@match`, `@if`, `@compress`, `@expand`, `@generate_examples`, `@assert` | Deeply nested adaptive interview protocol. |
| `catalog/standalone/prompt-refactoring-pipeline.weavemark.md` | `@refine`, `@extract`, `@normalize`, `@revise`, `@expand`, `@polish`, `@structural_constraints`, `@assert`, `@output` | Treats a messy prompt as a program-like artifact and refactors it through an explicitly nested semantic pipeline. |
| `catalog/standalone/market-research-brief.weavemark.md` | `@refine`, `@match`, `@if`, `@note` | Market research report with depth, competitor toggles, research rigor, evidence grading, and source-quality rules. |
| `catalog/standalone/program-review-checklist.weavemark.md` | `@refine`, `@match`, `@if`, `@note` | Language-specific program review with optional security audit. |
| `catalog/standalone/tutorial-generator.weavemark.md` | `@refine`, `@match`, `@if`, `@@` escaping | Technical tutorial with learner-model adaptation and explainability. |
| `catalog/standalone/consulting-proposal.weavemark.md` | `@refine`, `@match`, `@summarize`, `@polish`, `@assert`, `@output` | Management consulting proposal with nested semantic directives. |
| `catalog/standalone/knowledge-base-article.weavemark.md` | `@extract`, `@summarize`, `@compress`, `@if`, `@structural_constraints`, `@output` | Internal knowledge-base article pipeline. |
| `catalog/standalone/api-docs-generator.weavemark.md` | `@generate_examples`, `@revise`, `@structural_constraints`, `@output` | API reference documentation generator. |
| `catalog/standalone/ai-kanban-board.weavemark.md` | `@refine` | Human-AI task board programming spec. |
| `catalog/standalone/compoundvision-investment-simulator.weavemark.md` | `@refine` | Compound-interest and investment simulator programming spec. |

## Reusable library fragments

### Reasoning

| Spec | Role |
|---|---|
| `stdlib/fragments/reasoning/base-analyst.weavemark.md` | General analytical persona and standards. |
| `stdlib/fragments/reasoning/chain-of-thought.weavemark.md` | Structured rationale pattern used by execution and strategy specs. |
| `stdlib/fragments/reasoning/unstructured-input-normalization.weavemark.md` | Faithfully normalizes pasted notes, transcripts, fragments, contradictions, and ambiguities. |
| `stdlib/fragments/reasoning/action-planning.weavemark.md` | Converts analysis into concrete actions, owners, dependencies, decisions, risks, and review cadence. |
| `stdlib/fragments/reasoning/deep-summary.weavemark.md` | Layered summary obligations for faithful synthesis, implications, evidence, and gaps. |
| `stdlib/fragments/reasoning/learner-model.weavemark.md` | Teaching layer for learner assumptions, prerequisites, examples, misconceptions, and practice. |
| `stdlib/fragments/reasoning/prompt-refinement-core.weavemark.md` | Reusable method for turning rough prompts into clear, paste-ready instructions. |

### Analysis

| Spec | Role |
|---|---|
| `stdlib/fragments/analysis/mece-core.weavemark.md` | Core MECE discipline. |
| `stdlib/fragments/analysis/ach-core.weavemark.md` | Analysis of Competing Hypotheses obligations. |
| `stdlib/fragments/analysis/issue-tree-core.weavemark.md` | Issue-tree obligations. |
| `stdlib/fragments/analysis/strategic-problem-analysis.weavemark.md` | Strategic problem framing. |
| `stdlib/fragments/analysis/optionality-decision.weavemark.md` | Optionality, reversibility, and timing lens. |

### Decisions

These layers are composed in the
[Evidence-to-Decision Workspace controlled study](../studies/controlled-studies/evidence-decision-workspace-ablation-study/README.md).

| Spec | Role |
|---|---|
| `stdlib/fragments/decision/strategy-selection.weavemark.md` | Selects a reasoning method based on decision shape, reversibility, stakes, and information value. |
| `stdlib/fragments/decision/forecast-uncertainty.weavemark.md` | Scenario ranges, signposts, robust actions, contingent actions, and review cadence. |
| `stdlib/fragments/decision/values-tradeoff.weavemark.md` | Explicit value tensions, regret tests, boundary conditions, experiments, and accepted sacrifices. |

### Lenses

| Spec | Role |
|---|---|
| `stdlib/fragments/lenses/comparative-alternatives.weavemark.md` | Compares options by decisive criteria, tradeoffs, and ranking triggers. |
| `stdlib/fragments/lenses/decision-gate.weavemark.md` | Classifies a decision as go, no-go, wait, or investigate against explicit thresholds. |
| `stdlib/fragments/lenses/explainability.weavemark.md` | Makes conclusions traceable through reasoning, evidence, assumptions, checks, and limits. |
| `domains/finance/fragments/investment-decision.weavemark.md` | Frames investment decisions against a matched risk-free benchmark with scenario-conditional deltas. |

### Guidelines

| Spec | Role |
|---|---|
| `domains/research/fragments/news-quality.weavemark.md` | News selection and reporting quality: relevance, context, named entities, balance, and non-clickbait discipline. |
| `domains/finance/fragments/finance-safety.weavemark.md` | Finance-domain safety and evidence rules for advisory, market-data, calculation, and technical-analysis prompts. |
| `stdlib/fragments/guidelines/context-sufficiency.weavemark.md` | General context-status classification for confident, caveated, or scoping-only answers. |
| `domains/finance/fragments/finance-context-sufficiency.weavemark.md` | Finance-specific context checks for action-oriented investment or portfolio analysis. |
| `stdlib/fragments/guidelines/evidence-quality.weavemark.md` | Rubric for judging relevance, specificity, freshness, independence, and contradictions in evidence. |
| `stdlib/fragments/guidelines/research-rigor.weavemark.md` | Research-source coverage, search-access limits, contradiction handling, and next-search discipline. |
| `stdlib/fragments/guidelines/prompt-quality.weavemark.md` | Quality rubric for prompts meant for ChatGPT, Gemini, Claude, or other assistants. |
| `stdlib/fragments/guidelines/release-evidence-quality.weavemark.md` | Release-readiness evidence states for verified, partial, proxy, waived, missing, and stale claims. |

### Ideation

| Spec | Role |
|---|---|
| `stdlib/fragments/ideation/scamper.weavemark.md` | SCAMPER ideation method. |
| `stdlib/fragments/ideation/six-thinking-hats.weavemark.md` | Six Thinking Hats ideation method. |
| `stdlib/fragments/ideation/reverse-brainstorming.weavemark.md` | Reverse brainstorming method. |
| `stdlib/fragments/ideation/contrastive-mining-core.weavemark.md` | Reusable semantic comparison/mining obligations. |
| `stdlib/fragments/ideation/multi-persona-debate-core.weavemark.md` | Reusable balanced debate obligations. |

### Financial

| Spec | Role |
|---|---|
| `domains/finance/fragments/passive-income-capital-growth.weavemark.md` | Passive income, safe-to-spend amounts, principal drawdown, and capital growth. |
| `domains/finance/fragments/passive-income-forecasting.weavemark.md` | Passive-income scenarios, reserve handling, reinvestment, and evidence review. |
| `domains/finance/fragments/financial-resilience-lens.weavemark.md` | Household financial-resilience thresholds, calculations, and transition guardrails. |

### Game design

These mechanics are composed and evaluated in the
[Verdant Relay controlled study](../studies/controlled-studies/games/verdant-relay-ablation-study/README.md);
the [quality analysis](../studies/controlled-studies/games/verdant-relay-ablation-study/results/final-quality-analysis.md)
records both the integration gains and the study's length and synthetic-domain
caveats.

| Spec | Role |
|---|---|
| `domains/game-design/fragments/mechanics/tower-defense.weavemark.md` | Tower-defense route pressure, threat waves, defensive placement, targeting, previews, rewards, leaks, and tuning obligations. |
| `domains/game-design/fragments/mechanics/deckbuilder.weavemark.md` | Deck, hand, discard, card economy, targeting, upgrades, synergies, and card-reward obligations. |
| `domains/game-design/fragments/mechanics/ecosystem-simulation.weavemark.md` | Ecosystem entities, resource flows, feedback loops, indicators, time progression, and recovery obligations. |
| `domains/game-design/fragments/production/playability-readability.weavemark.md` | First-run teaching, feedback vocabulary, readability budget, failure explanations, and feel checks. |
| `domains/game-design/fragments/production/progression-balance-model.weavemark.md` | Progression ladder, balance table, synergy/counterplay matrix, playtest questions, and release balance gates. |

### Teaching

These layers are composed in the
[Learning Tutor controlled study](../studies/controlled-studies/learning-tutor-refinement-ablation-study/README.md).

| Spec | Role |
|---|---|
| `stdlib/fragments/teaching/socratic-tutoring.weavemark.md` | Focused questioning that probes and advances the learner's current model. |
| `stdlib/fragments/teaching/misconception-diagnosis.weavemark.md` | Diagnoses tempting errors and repairs the underlying reasoning. |
| `stdlib/fragments/teaching/mastery-practice-loop.weavemark.md` | Recognition, application, transfer, remediation, delayed review, and mastery checks. |

### Programming

| Folder | Contents |
|---|---|
| `domains/programming/fragments/foundations/` | Base authoring obligations for implementation-ready software specs, including `software-spec.weavemark.md`. |
| `domains/programming/fragments/types/` | Maintained product-type layers for local-first web applications and browser-based games. |
| `domains/programming/fragments/stacks/` | Maintained local-first TypeScript/Next.js/Prisma/SQLite implementation stack. |
| `domains/programming/fragments/modules/` | Reusable product/program modules such as local SQLite storage, cards, workflow boards, activity streams, context attachments, typed output surfaces, auth, REST APIs, decision-oriented dashboards, realtime, notifications, and inspectable AI features. |
| `domains/programming/fragments/models/` | Reusable domain models used by programming specs. |
| `domains/programming/fragments/assets/` | Reusable game-asset production layers such as generative 2D sprite specs, animation-frame prompts, sheet packing, metadata, and validation. |
| `domains/programming/fragments/debugging/` | Reusable debugging layers such as root-cause hypotheses, diagnostics, minimal fixes, and verification. |
| `domains/programming/fragments/validation/` | Reusable validation layers such as release matrices, Playwright MCP browser testing, and iterative improvement loops for web-based software. |

### Product

| Spec | Role |
|---|---|
| `domains/product/fragments/product-validation-surface.weavemark.md` | Product validation obligations for first-session scripts, state coverage, evidence checklists, failure probes, and release gates. |
| `domains/product/fragments/release-artifact-readiness.weavemark.md` | Public release artifact readiness for docs, examples, generated outputs, prompts, packages, demos, release notes, screenshots, and traces. |
| `domains/product/fragments/release-readiness-gate.weavemark.md` | Release gate, evidence ledger, risk register, action board, and decision-record obligations. |

### Research

| Spec | Role |
|---|---|
| `domains/research/fragments/recurring-topic-monitor-core.weavemark.md` | Recurring monitor obligations for daily, weekly, monthly, or custom topic runs. |
| `domains/research/fragments/deep-web-source-discovery.weavemark.md` | Multi-query, first-level crawl, and second-level crawl discovery method. |
| `domains/research/fragments/news-event-triage.weavemark.md` | Mode-specific triage rules for recurring news digests and event/activity monitors. |

### Work intelligence

These fragments are composed and evaluated in the
[Intelligence-to-Execution Kanban controlled study](../studies/controlled-studies/intelligence-execution-kanban-ablation-study/README.md).

| Spec | Role |
|---|---|
| `domains/work-intelligence/fragments/topic-intelligence-monitor.weavemark.md` | Monitored-topic intent, signal provenance and triage, alert discipline, and user-feedback memory. |
| `domains/work-intelligence/fragments/idea-execution-workspace.weavemark.md` | Connects captured ideas to decisions, delegation, execution, artifacts, and review. |
| `domains/work-intelligence/fragments/signal-to-action-workflow.weavemark.md` | Converts selected signals into traceable decisions and bounded follow-up work. |

### Strategy

| Spec | Role |
|---|---|
| `stdlib/fragments/strategy/indirect-strategy-principles.weavemark.md` | General indirect-strategy lens for competitive and crisis analysis. |

## Reusable modules

Modules declare `@module`, export definitions with `@define`, and are imported
with `@use`.

| Module | Exports | Role |
|---|---|---|
| `stdlib/definitions/planning/goals.weavemark.md` | `@goal_plan`, `@planning_checkpoint`, `@lookup_public_goal_assumptions` | Reusable goal-to-plan semantic macros plus an effectful public-reference lookup function used by the advanced financial-independence tutorial. |

## Executable prompts

| Spec | Role |
|---|---|
| `catalog/executable/react-agent.weavemark.md` | ReAct agent with search/read/calculate tools. |
| `catalog/executable/reflection-solver.weavemark.md` | Reflection loop for problem solving. |
| `catalog/executable/reflection-writer.weavemark.md` | Reflection loop for writing. |
| `catalog/executable/self-consistency-solver.weavemark.md` | Self-consistency strategy with majority vote / synthesis. |
| `catalog/executable/simplified-tree-of-thought-solver.weavemark.md` | Compact tree-of-thought example. |
| `catalog/executable/tree-of-thought-solver.weavemark.md` | Full tree-of-thought strategy. |
| `catalog/executable/recurring-topic-monitor.weavemark.md` | Native executable recurring monitor: the promplet plans and runs bounded search/crawl calls, deduplicates findings, and optionally compares a folder of prior reports. |
| `catalog/executable/contrastive-mining.weavemark.md` | Reflection-powered contrastive text-mining workflow with embedded samples. |
| `catalog/executable/collaborative-writer.weavemark.md` | Human-in-the-loop writing workflow; the demo runner can hand each editor turn to the surrounding AI agent. |
| `catalog/executable/collaborative-investment-strategy.weavemark.md` | Human-in-the-loop investment-strategy drafting workflow; the demo runner can hand each client turn to the surrounding AI agent. |
| `catalog/executable/crisis-strategy-analyzer.weavemark.md` | Tool-enabled strategy-analysis prompt using reusable reasoning and strategy lenses. |
| `catalog/executable/financial-independence-goal-plan.weavemark.md` | Weave prompt that imports the reusable goal-planning module and binds `web_search read` to a public-reference companion. |
| `catalog/executable/market-snapshot.weavemark.md` | Flagship VALE3 functional workflow: reusable finance capabilities gather market/search evidence, a grounded Markdown brief is drafted, and reusable plus local `@package` instructions produce a standalone HTML dashboard. |

## Experimental executable prompts

These are intentionally separated from the stable executable catalog.

| Spec | Why experimental |
|---|---|
| `experimental/fslm/fslm-support-triage.weavemark.md` | Finite-state language-machine execution is still an advanced, changing mechanism. |
| `experimental/fslm/fslm-support-triage-sugared.weavemark.md` | Inline FSLM sugar is useful but not stable enough for the main public surface. |

## Running selected specs

```bash
# Final analysis prompt
weavemark library builtin:catalog/standalone/mece-structuring \
  --vars-file promplets/catalog/standalone/mece-structuring.vars.json \
  --batch-only --verbose

# Final programming prompt
weavemark library builtin:catalog/standalone/passive-income-planning-dashboard \
  --var app_name="Income Horizon" \
  --batch-only --verbose

# Final prompt-refactoring prompt
weavemark library builtin:catalog/standalone/prompt-refactoring-pipeline \
  --vars-file examples/batch-example-runs/static-prompts/inputs/prompt-refactoring-example.yaml \
  --batch-only --verbose

# News intelligence board with durable event memory
weavemark library builtin:catalog/standalone/news-intelligence-board \
  --vars-file examples/batch-example-runs/static-prompts/inputs/news-intelligence-board.yaml \
  --batch-only --verbose

# Executable prompt
weavemark library builtin:catalog/executable/tree-of-thought-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/tree-of-thought-solver-example.json \
  --run --batch-only

# Live news monitor through the regular WeaveMark CLI
weavemark library builtin:catalog/executable/recurring-topic-monitor \
  --vars-file examples/batch-example-runs/execution-engines/inputs/recurring-topic-monitor-ai-news.json \
  --run

# Collaborative executable prompts with AI-agent-authored human/editor turns
./examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run-agent-handoff.sh
```

For collaborative examples, `--agent-collaborator` does not invent a fake user
inside WeaveMark. Instead, the runner writes each turn to
`examples/interactive-ui-and-handoff-demos/<example>/outputs/agent-turns/turn-NNN-request.md`, prints the matching
response path, and waits for the surrounding AI agent to write the full edited
document to `turn-NNN-response.md`.

```bash
python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py \
  --spec promplets/catalog/executable/collaborative-writer.weavemark.md \
  --vars examples/interactive-ui-and-handoff-demos/collaborative-writer/inputs/vars.json \
  --output-dir examples/interactive-ui-and-handoff-demos/collaborative-writer/outputs \
  --agent-collaborator
```

The response contract is deliberately the same as the human editing callback:
write the complete edited document, copy it unchanged to approve, add a final
line containing only `DONE` to finish, or create an empty response file to abort.
