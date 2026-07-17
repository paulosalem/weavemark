@promplet version: 0.7


@refine module:weavemark.std.reasoning.base_analyst mingle: true
@refine module:weavemark.std.guidelines.context_sufficiency mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true
@refine module:weavemark.std.guidelines.research_rigor mingle: true
@refine module:weavemark.domains.research.news_quality mingle: true
@refine module:weavemark.std.lenses.comparative_alternatives mingle: true
@refine module:weavemark.std.lenses.explainability mingle: true

# Research Brief Prompt

@note
  Final prompt for a paste-ready research brief instruction for ChatGPT, Gemini,
  Claude, or another assistant, with or without web access.

Prepare a research brief on **@{research_topic}**.

## Purpose

@{purpose}

## Audience

@{audience}

## Time horizon and recency needs

@{time_horizon}

## Known context

@{known_context}

## Required source families

@{source_requirements}

## Required behavior

- If you have live web/search access, use it and cite the source families used.
- If you do not have live web/search access, state that limitation and produce a
  research plan plus a provisional brief clearly marked as unverified.
- Do not fabricate citations, URLs, dates, quotes, source names, or claims of
  having searched.
- Separate facts, reported claims, analysis, estimates, and speculation.
- Cover primary/official, recent news, independent expert, reference, and
  skeptical or competing sources when relevant and available.
- Surface contradictions and weak evidence instead of smoothing them away.

## Required output

Use labeled lines directly for compact snapshots. Do not add standalone format
labels such as `text`, `markdown`, or `json`.

1. **Research status** — verified, partially verified, unverified, or research
   plan only.
2. **Executive answer** — the current best answer in 3-5 bullets.
3. **Source map** — source families used or needed, with evidence grade.
4. **Main findings** — each finding with evidence, confidence, and caveat.
5. **Contradictions and open questions**.
6. **Implications for @{audience}**.
7. **Next searches** — targeted queries, source types, or documents that would
   most improve confidence.
8. **Bottom line** — what can responsibly be concluded now.
