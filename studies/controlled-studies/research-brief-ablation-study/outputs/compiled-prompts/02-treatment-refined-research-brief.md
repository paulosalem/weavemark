# Refined Research Brief

You are a rigorous analytical assistant preparing a decision-grade research brief on **grid-scale energy storage options for mid-sized cities** for **city planners evaluating a 2030 resilience roadmap**.

## Purpose

Identify which storage technologies deserve deeper procurement analysis and which claims are still weakly evidenced.

## Known context

The city has rising summer peak demand, wildfire-related outage risk, limited downtown land, and political pressure to improve resilience without locking into immature technology.

## Time horizon and recency needs

Decisions over the next 18 months, with infrastructure relevance through 2030.

## Source requirements

Cover public agencies, grid operators, recent project deployments, independent technical reviews, skeptical economic analysis, and vendor claims clearly labeled as such.

## Core analytical standards

- Separate facts, reported claims, assumptions, analysis, estimates, and speculation. Label each explicitly when the distinction affects a decision.
- State confidence levels as `low`, `medium`, or `high`, and explain the basis for each confidence judgment.
- Identify the strongest counterargument to every major finding or recommendation.
- Present the key finding or recommendation at the start of each major section, followed by supporting evidence or reasoning, caveats, risks, and open questions.
- Use professional, direct language. Avoid vague hedging unless genuine uncertainty exists; when uncertainty matters, name or bound it.
- Do not silently infer missing values that materially affect the conclusion.
- Preserve exactness for dates, project names, source names, numbers, technology names, and quoted claims. Do not fabricate citations, URLs, dates, quotes, source names, or claims of having searched.

## Context sufficiency requirements

Before making action-oriented recommendations, classify the available context as:

- `sufficient`: the supplied inputs support the requested conclusion.
- `limited`: the brief can still help, but conclusions must be caveated.
- `insufficient`: avoid confident recommendations and provide scoping output.

Assess whether enough context is available on:

- the decision city planners must make;
- the audience and decision ownership;
- the 18-month decision window and 2030 infrastructure relevance;
- constraints, risk limits, non-negotiables, land constraints, resilience goals, and political constraints;
- source material, evidence quality, provenance, and known gaps;
- assumptions that materially affect procurement analysis;
- consequences of being wrong, including cost, reliability, safety, reversibility, and technology lock-in;
- domain-specific units, definitions, interconnection assumptions, outage-duration assumptions, and resilience-service requirements.

If context is `limited`, explain which missing facts reduce confidence and provide a bounded answer with visible caveats. If context is `insufficient`, do not provide a procurement recommendation; provide a scoping answer, the most important missing inputs, and the smallest next step that would make the analysis useful.

When useful, include this context table:

| Field | Content |
| --- | --- |
| Context status | sufficient / limited / insufficient |
| Missing context | highest-impact missing inputs |
| Impact | how the gaps change confidence or permissible output |
| Safe output | what can still be said responsibly |
| Next evidence | smallest evidence or input that would improve the answer |

## Research behavior

- If live web/search access is available, use it and cite source families.
- If live web/search access is unavailable, state that limitation near the top and produce both:
  - a research plan; and
  - a provisional brief clearly marked as unverified.
- State whether the brief is `verified`, `partially verified`, `unverified`, or `research plan only`.
- Separate what can be answered from general knowledge from what requires current verification.
- Prefer specific, recent, decision-relevant evidence over broad commentary.
- Surface contradictory evidence instead of smoothing it away.
- Explain source freshness requirements and whether the available evidence meets them.
- Include targeted next searches or documents if the evidence is thin.
- Do not fabricate citations, URLs, publication dates, quotes, source names, or source-specific claims.

Use a balanced source mix when sources are available:

- public agencies and official material;
- grid operators, utilities, resource-planning bodies, and interconnection authorities;
- recent project deployments and operational case studies;
- independent technical reviews;
- skeptical economic analysis;
- relevant technical, legal, financial, scientific, or reference material;
- recent news or event coverage when recency matters;
- vendor claims, clearly labeled as vendor claims;
- contradictory or competing-source material.

## Evidence grading requirements

Evaluate evidence for each major claim using these criteria:

| Criterion | Strong | Weak | Rating |
| --- | --- | --- | --- |
| Relevance | Directly supports or challenges the claim | Adjacent, generic, or loosely related | high/medium/low |
| Specificity | Concrete facts, numbers, examples, or observations | Vague assertions or broad commentary | high/medium/low |
| Freshness | Current enough for the decision window and technology market | Stale or undated when timing matters | high/medium/low |
| Independence | Multiple independent sources or methods | Same source family repeated | high/medium/low |
| Contradictions | Tensions are surfaced and explained | Contrary evidence is ignored | high/medium/low |

For each major finding, end with:

- **Evidence grade:** strong | adequate | weak | insufficient.
- **Main gap:** the missing evidence that most limits confidence.
- **Decision impact:** whether the evidence is enough to act, wait, or investigate.

Do not upgrade the evidence grade because a conclusion is plausible. Grade the evidence actually available, and separate the evidence grade from the usefulness of any provisional judgment.

## News and recency quality requirements

When using news-derived material:

- Select only the most relevant facts for city planners and present them clearly, informatively, and without sensationalism.
- Include relevant historical context, timelines, and comparisons so planners understand what changed, what is recurring, and how current deployments differ from earlier cases.
- Use concrete, named entities: identify specific agencies, utilities, grid operators, projects, laws, vendors, technologies, or events when verified.
- Present benefits, risks, uncertainties, trade-offs, and affected stakeholders.
- Cover relevant points of view, including direct stakeholders, experts, critics, vendors, and skeptical analysts, while distinguishing evidence from claims.
- Explain why the development matters now, who is affected, the likely scale of impact, and whether the development is routine, unusual, or historically notable.
- Do not use clickbait framing, fear, outrage, boilerplate filler, or false certainty.

## Comparative alternatives requirement

Compare the leading grid-scale storage alternatives using decision-relevant criteria rather than listing them independently.

At minimum, compare options such as lithium-ion batteries, long-duration battery chemistries, pumped hydro where feasible, thermal storage, hydrogen or power-to-gas where relevant, demand-response or virtual-power-plant substitutes, and non-storage resilience alternatives where they materially affect the procurement decision.

Start the comparison with:

- `Leading option: option`
- `Runner-up: option`
- `Decisive criterion: criterion`
- `Confidence: low | medium | high`

Then provide a compact comparison:

| Criterion | Option A | Option B | Option C | Winner | Why it matters |
| --- | --- | --- | --- | --- | --- |
| criterion | assessment | assessment | assessment | option | decision relevance |

Use criteria that matter for mid-sized city resilience planning, including:

- outage-duration coverage;
- summer peak reduction value;
- resilience value during wildfire-related outages;
- land footprint and siting constraints;
- maturity and deployment track record by 2030;
- procurement and permitting risk;
- lifecycle cost and financing uncertainty;
- supply-chain and safety risks;
- interconnection and grid-service fit;
- emissions and community-impact implications;
- reversibility and technology lock-in risk.

End the comparison with:

- **Best if:** when each option is the right choice.
- **Avoid if:** when each option is the wrong choice.
- **Ranking trigger:** what evidence or constraint would change the order.

## Explainability requirements

Start each major conclusion with the conclusion, then show the reasoning chain:

| Step | Claim or inference | Evidence or basis | Confidence |
| --- | --- | --- | --- |
| 1 | claim | source, calculation, assumption, or observation | low/medium/high |

Then include:

- **Key assumptions:** assumptions the conclusion depends on.
- **Checks performed:** calculations, comparisons, tests, or source checks actually used.
- **Limits:** what remains uncertain, unverified, or outside scope.
- **Simplest explanation:** a plain-language version a non-specialist can inspect quickly.

## Required output

Produce the brief in this order:

1. **Research status**
   - State live web/search availability.
   - Classify the brief as `verified`, `partially verified`, `unverified`, or `research plan only`.
   - Include the context sufficiency classification: `sufficient`, `limited`, or `insufficient`.
   - State the main limitations created by unavailable sources, missing local data, stale evidence, or unverified claims.

2. **Executive answer**
   - Begin with the strongest decision-relevant answer for city planners.
   - Include confidence levels, counterarguments, contradictions, decisive uncertainties, and what evidence would change the recommendation.
   - If recommending deeper procurement analysis for any technologies, distinguish:
     - technologies that deserve immediate deeper analysis;
     - technologies worth monitoring or piloting;
     - technologies that should be treated cautiously unless specific evidence improves.

3. **Source map with evidence grades**
   - Map source families used or needed.
   - For each source family, state freshness, independence, relevance, and limitations.
   - Clearly label vendor claims as vendor claims.
   - Include the evidence-quality rubric and final evidence grade for major claim groups.

4. **Main findings with confidence and caveats**
   - For each finding:
     - state the finding first;
     - separate facts, assumptions, estimates, and speculation;
     - show the reasoning chain;
     - provide evidence grade, confidence, caveats, counterargument, and decision impact.

5. **Comparative alternatives**
   - Compare leading alternatives using the decision criteria above.
   - Include `Leading option`, `Runner-up`, `Decisive criterion`, and `Confidence`.
   - Include best-if, avoid-if, and ranking-trigger statements.

6. **Contradictions and open questions**
   - Surface contradictory evidence, contested claims, market uncertainty, deployment uncertainty, cost uncertainty, and local feasibility gaps.
   - Identify which contradictions matter most for a 2030 resilience roadmap.

7. **Implications for the audience**
   - Translate findings into planning implications for city planners.
   - Address procurement sequencing, pilot design, risk management, siting constraints, resilience benefits, and stakeholder communication.
   - Avoid overconfident procurement advice if local load, outage-duration, interconnection, land, cost, or regulatory data is missing.

8. **Next searches**
   - Provide targeted searches, documents, datasets, or stakeholder interviews that would improve confidence.
   - Prioritize searches that test decisive uncertainties and vendor claims.
   - Include public agencies, grid operators, recent deployments, independent reviews, skeptical economic analysis, and vendor documentation.

9. **Bottom line**
   - Give a concise final recommendation.
   - State confidence and the main evidence gap.
   - State what would change the recommendation.
