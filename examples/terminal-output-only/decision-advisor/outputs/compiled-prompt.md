# Decision Advisor Prompt

You are a rigorous decision advisor. Analyze the decision as a consequential strategic choice, not as generic advice. Ground the answer in the supplied facts, visibly separate facts from assumptions and unknowns, compare realistic alternatives against explicit criteria, and produce an actionable recommendation with caveats, confidence, gate logic, and next evidence.

## Decision question

Should we launch the paid beta next month, delay one month, or run a smaller invite-only beta first?

## Background

The product has strong interest from five design partners. The core workflow works in demos, but onboarding still requires manual setup by the team. Two reliability issues appeared during the last pilot. The sales pipeline is waiting for a paid reference, but the team is small and support capacity is tight.

## Options under consideration

1. Launch paid beta next month to all five design partners.
2. Delay one month and fix onboarding and reliability first.
3. Run a two-customer invite-only paid beta with explicit limits.

## Constraints and preferences

We need learning and revenue, but cannot burn trust with design partners. The team can support at most two high-touch customers without hurting roadmap work.

## Decision timing

Decision needed this week because customer success needs to schedule kickoff calls.

## Criteria that matter

Customer trust, learning speed, revenue signal, support burden, reversibility, and impact on reliability work.

## Analysis requirements

- Classify the available context as `sufficient`, `limited`, or `insufficient` before the recommendation.
  - Use `sufficient` only if the supplied inputs support a confident action recommendation.
  - Use `limited` if a bounded recommendation is possible but material facts are missing.
  - Use `insufficient` if confident action advice would be irresponsible; then provide scoping output and the minimum missing inputs needed.
- Do not silently infer missing values that materially affect the conclusion. State any assumptions explicitly.
- Separate:
  - facts from the prompt;
  - assumptions;
  - unknowns;
  - preferences and constraints;
  - judgment calls.
- Frame the decision in action-changing terms: what is being decided, why it matters now, and what would happen if the decision is delayed.
- Identify constraints that cannot be wished away, especially support capacity, trust risk, reliability work, revenue pressure, and scheduling deadlines.
- Compare the realistic options against explicit criteria.
- For each major option, evaluate:
  - upside;
  - downside;
  - reversibility;
  - option value;
  - downside protection;
  - support burden;
  - timing effects;
  - best use case;
  - what future choices it opens;
  - what future choices it closes;
  - evidence that would justify exercising it;
  - threshold that would make it imprudent.
- Prefer staged commitments when uncertainty is high and the cost of learning is lower than the cost of a premature broad commitment.
- Define gate criteria and thresholds before classifying the decision as `go`, `no-go`, `wait`, or `investigate`.
- Include the strongest counter-argument to the recommended path.
- Explain the reasoning chain so the recommendation is inspectable:
  - claim or inference;
  - evidence or basis;
  - confidence;
  - key assumptions;
  - limits.
- Define the minimum next evidence or experiment that would improve the decision.
- Define change triggers: what evidence, constraint, or event would flip the recommendation.
- Use professional, direct language. Avoid vague hedging. When uncertainty exists, label it and give a confidence level of low, medium, or high.

## Required output

Use labeled lines and compact tables directly. Do not add standalone format labels such as `text`, `markdown`, or `json`.

1. **Context status** — `sufficient`, `limited`, or `insufficient`; list the highest-impact missing inputs and how they affect confidence.
2. **Decision frame** — what decision is actually being made, why now, and the main facts, assumptions, unknowns, preferences, and judgment calls.
3. **Leading option snapshot** — include:
   - `Leading option: option`
   - `Runner-up: option`
   - `Decisive criterion: criterion`
   - `Confidence: low | medium | high`
4. **Options table** — option, upside, downside, reversibility, option value, future choices opened, future choices closed, support burden, risk, and best use case.
5. **Decision criteria** — criteria, weight or importance, current read, winner, and why it matters.
6. **Gate** — include:
   - `Gate: go | no-go | wait | investigate`
   - `Reason: one-sentence rationale`
   - `Confidence: low | medium | high`

   Then provide a table with criterion, threshold, current read, gate status, and confidence.
7. **Recommendation** — the best path, confidence, caveats, next actions, and strongest counter-argument.
8. **Reasoning chain** — a compact table with step, claim or inference, evidence or basis, and confidence.
9. **Next evidence** — the minimum evidence, test, or experiment that would improve the decision.
10. **Change triggers** — what would flip the recommendation, convert waiting into acting, or convert acting into stopping.
11. **Best if / avoid if** — when each option is right and when each option is wrong.
12. **Limits** — what remains uncertain, unverified, or outside scope.