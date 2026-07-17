@promplet version: 0.7

# Computational Ablation Study Method

@note
  Reusable method fragment for computational ablation research. This is
  intentionally domain-general: it can guide machine-learning experiments,
  software-engineering research, systems studies, algorithm comparisons,
  human-computer interaction prototypes, prompt-language studies, or other
  computational artifacts. A refining spec supplies the artifact family, domain
  hypotheses, variants, measurements, tools, and success criteria.

Use this method to design, execute, and report an ablation study that isolates
which component, mechanism, representation, data source, optimization, interface,
or workflow choice creates measurable value.

## Study objective

- State the central hypothesis in falsifiable form.
- Define the computational artifact under study: model, system, algorithm,
  dataset, interface, program transformation, workflow, language feature, prompt
  system, or product prototype.
- Define the task, environment, workload, user scenario, benchmark, or dataset the
  artifact is meant to improve.
- Define what counts as a positive effect, no meaningful effect, regression, and
  evidence against the hypothesis.
- Separate structural effects from behavioral effects:
  - Structural effects include source size, model size, parameter count, latency,
    memory, dependency surface, implementation complexity, maintenance burden, or
    reusable components.
  - Behavioral effects include accuracy, quality, robustness, completion rate,
    defect rate, usability, reliability, output usefulness, or task success.

## Ablation variants

Construct variants that remove, replace, or isolate one source of capability at a
time:

1. **Reference baseline** — the simplest honest version of the artifact or the
   current accepted baseline.
2. **Naive or conventional baseline** — a common simpler technique, template,
   heuristic, default model, minimal UI, unoptimized algorithm, or standard
   workflow.
3. **Single-factor ablations** — remove or replace one component, feature,
   dataset, optimization, prompt directive, model layer, tool, interaction, or
   process step at a time.
4. **Incremental additions** — add one major mechanism at a time to identify
   marginal gains and interactions.
5. **Full system** — the strongest intended version with all selected mechanisms.
6. **Transfer or stress variant** — apply the same mechanism to a nearby task,
   dataset, workload, user scenario, or domain to test generality.

Each variant MUST preserve the same evaluation target unless it is explicitly a
transfer, robustness, or stress test.

## Measurements

Choose metrics that match the artifact family. Consider these metric families:

- **Effectiveness**: accuracy, F1, pass rate, benchmark score, user task success,
  defect reduction, output completeness, or human rating.
- **Efficiency**: latency, throughput, memory, disk usage, energy, cost, token
  usage, engineering effort, or build/runtime complexity.
- **Quality and robustness**: failure modes, variance across seeds, sensitivity
  to inputs, edge-case coverage, reliability under degraded conditions, or
  reproducibility.
- **Expressiveness and capability**: number and diversity of supported tasks,
  constraints, behaviors, generated artifacts, interactions, or concrete
  requirements.
- **Maintainability and reuse**: centralized logic, reusable components, repeated
  prose or implementation removed, dependency clarity, or ease of adapting to a
  nearby task.
- **Human-facing value**: usability, interpretability, cognitive load, confidence,
  trust calibration, clarity, or decision usefulness.
- **Evidence strength**: number of runs, confidence intervals, statistical tests
  when appropriate, qualitative inspection, logs, traces, screenshots, saved
  artifacts, and reproducible commands.

Do not use one convenient metric as the whole conclusion. State which metrics are
primary, which are secondary, and what tradeoffs are acceptable.

## Experimental controls

- Keep workloads, inputs, seeds, prompts, datasets, environment, hardware,
  versions, and evaluation procedures fixed across variants unless deliberately
  testing sensitivity.
- Run enough repetitions to distinguish signal from noise when the system is
  stochastic.
- Preserve raw outputs, logs, traces, random seeds, configuration, and scripts
  needed to reproduce claims.
- Identify confounders such as data leakage, benchmark contamination, prompt
  leakage, user-selection bias, warm caches, hidden retries, changing
  dependencies, or evaluator drift.
- Use paired comparisons when variants process the same inputs.

## Experiment loop

For each candidate study:

1. Define the hypothesis, artifact, workload, and primary metrics.
2. Build the reference and conventional baselines.
3. Add or remove one mechanism at a time.
4. Execute or simulate every variant with comparable inputs.
5. Measure primary metrics, secondary metrics, costs, and failure modes.
6. Inspect outputs qualitatively to catch metric blind spots.
7. Revise weak experimental design, not the conclusion.
8. Record which component created the largest gain, largest regression, and most
   interesting tradeoff.
9. Preserve commands, inputs, configs, outputs, logs, and interpretation so
   readers can rerun or audit the study.

## Domain-specific specialization

A refining spec MUST specialize this generic method by naming:

- artifact family and domain;
- baseline variants;
- ablated mechanisms;
- primary and secondary metrics;
- acceptable tradeoffs;
- reproducibility artifacts;
- evaluation commands or procedures;
- reporting format.

Examples of specializations:

- ML research: ablate model architecture, training data, loss terms,
  augmentation, retrieval, fine-tuning, decoding, or evaluation criteria.
- Software-engineering research: ablate static-analysis rules, test-generation
  strategies, agent tools, program transformations, review policies, or
  debugging workflows.
- Systems research: ablate cache policy, scheduler, protocol, storage layout,
  replication strategy, batching, or backpressure.
- Prompt-language research: ablate directives, reusable fragments, branching,
  clarification, tool declarations, emitted artifacts, or execution strategies.

## Guardrails against misleading results

- Do not compare a weak straw baseline against an over-engineered full system.
- Do not change multiple factors at once unless explicitly studying an
  interaction.
- Do not count copied material, duplicated implementation, or repeated manual
  effort as reusable leverage.
- Do not claim a mechanism matters merely because it is present; identify the
  concrete measurable effect it contributes.
- Do not overclaim from one dataset, prompt, workload, seed, or user scenario.
- Report weak, mixed, neutral, and negative results honestly.

## Output contract

Produce a study guide or report with:

1. Hypothesis and scope.
2. Artifact family and task/workload.
3. Variant matrix.
4. Primary and secondary metrics.
5. Experimental controls.
6. Reproducible commands or procedures.
7. Results and observations.
8. Largest gains, regressions, and tradeoffs.
9. Validity threats and limitations.
10. Why the winning mechanism is computationally meaningful.
11. Next experiments.
