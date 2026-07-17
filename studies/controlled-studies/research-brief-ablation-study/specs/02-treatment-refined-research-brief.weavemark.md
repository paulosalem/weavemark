@promplet version: 0.7

@refine reasoning/base-analyst mingle: true
@refine guidelines/context-sufficiency mingle: true
@refine guidelines/evidence-quality mingle: true
@refine guidelines/research-rigor mingle: true
@refine guidelines/news-quality mingle: true
@refine lenses/comparative-alternatives mingle: true
@refine lenses/explainability mingle: true

# Refined Research Brief

Prepare a research brief on **@{research_topic}** for **@{audience}**.

## Purpose

@{purpose}

## Known context

@{known_context}

## Time horizon and recency needs

@{time_horizon}

## Source requirements

@{source_requirements}

## Depth

@match depth
  "brief" ==>
    Keep the executive answer under 5 bullets and limit the main findings to
    the 5 highest-value findings.
  "decision-grade" ==>
    Include confidence levels, counterarguments, contradictions, decisive
    uncertainties, and what evidence would change the recommendation.

@if compare_alternatives
  Compare the leading alternatives using decision-relevant criteria rather than
  listing them independently.

## Required behavior

- If live web/search access is available, use it and cite source families.
- If live web/search access is unavailable, state that limitation and produce a
  research plan plus a provisional brief clearly marked as unverified.
- Do not fabricate citations, URLs, dates, quotes, source names, or claims of
  having searched.

## Required output

1. Research status.
2. Executive answer.
3. Source map with evidence grades.
4. Main findings with confidence and caveats.
5. Contradictions and open questions.
6. Implications for the audience.
7. Next searches.
8. Bottom line.
