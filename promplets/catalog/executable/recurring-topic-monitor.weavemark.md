@promplet version: 0.7

@execute single-call
  max_iterations: 20
  max_tool_calls: 30

@refine module:weavemark.std.reasoning.base_analyst mingle: true
@refine module:weavemark.std.guidelines.context_sufficiency mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true
@refine module:weavemark.std.guidelines.research_rigor mingle: true
@refine module:weavemark.domains.research.news_quality mingle: true
@refine module:weavemark.domains.research.recurring_topic_monitor mingle: true
@refine module:weavemark.domains.research.deep_web_source_discovery mingle: true
@refine module:weavemark.domains.research.news_event_triage mingle: true
@refine module:weavemark.std.lenses.explainability mingle: true

@bind search_web language: python from: "./companions/recurring_topic_monitor.py" symbol: search_web
@bind search_news language: python from: "./companions/recurring_topic_monitor.py" symbol: search_news
@bind crawl_url language: python from: "./companions/recurring_topic_monitor.py" symbol: crawl_url

@tool search_web
  Search the web. Use for official sources, technical analysis, source discovery,
  event calendars, and targeted follow-up queries.
  - query: string (required) - Focused search query.
  - max_results: integer - Maximum result count, normally 5 to 7.
  - time_range: string - Recency window: d, w, m, y, or any.

@tool search_news
  Search current news. Use for fresh announcements, reporting, changes,
  cancellations, and independent coverage.
  - query: string (required) - Focused news query.
  - max_results: integer - Maximum result count, normally 5 to 7.
  - time_range: string - Recency window: d, w, m, y, or any.

@tool crawl_url
  Crawl one selected source URL and return its readable page content.
  - url: string (required) - Exact URL selected from search results or a seed.

# Recurring Topic Monitor

Run a source-grounded recurring monitor.

## Monitor brief

- Topic: @{topic}
- Mode: @{monitor_mode}
- Cadence: @{cadence}
- Lookback window: @{lookback_window}
- Region or location: @{region}
- Audience: @{audience}
- Depth: @{research_depth}
- Run date: @{run_date}
- User constraints: @{user_constraints}
- User-supplied source seeds: @{seed_urls}

@if use_previous_reports
  ## Compact memory from previous reports

  @summarize
    Summarize only the event/story identity, decisive facts, dates, prior status,
    confidence, and latest known material change. Merge duplicate mentions across
    reports. Omit prose, generic advice, and source-map detail. This memory exists
    only to classify current findings as new, repeated, or materially changed.

    @embed folder: "@{previous_reports}" label: "Previous monitor reports"

## Required tool workflow

You MUST use the bound tools before writing the digest. Do not answer from model
memory.

1. Translate the monitor brief into focused query families. For AI/technology
   news, cover model/product releases, safety/research, policy/enterprise,
   independent technical analysis, and open-source/developer tooling. For events,
   cover official calendars, local-language discovery, practical eligibility,
   booking/cost, and cancellations or changes.
2. Run several focused searches rather than one broad query. Keep the requested
   lookback window and region in each query where they matter.
3. Reject obvious evergreen explainers, SEO pages, social posts, generic
   roundups, stale results, and off-topic cultural commentary unless they provide
   indispensable context.
4. Select the strongest primary sources and independent sources from the search
   results. Crawl individual announcement, article, report, model-card,
   benchmark, calendar, or booking pages—not only index pages.
5. Diversify crawls across organizations and source families. Do not spend all
   crawl calls on one provider. Use follow-up searches when a primary document or
   independent confirmation is missing.
6. For each candidate, establish the underlying story/event identity, decisive
   facts, date, source provenance, relevance, confidence, and material change.
7. Cluster duplicate coverage of the same underlying story/event. One event gets
   one finding with several sources, not several findings.
8. If previous-report memory is present, classify each cluster:
   - **new** — no prior cluster represents it;
   - **repeated/no material change** — suppress from top findings;
   - **material update** — resurface with a precise “What changed” statement;
   - **uncertain match** — disclose uncertainty instead of guessing.
9. Stop searching when added queries are low-yield or the tool-iteration budget
   is needed to synthesize the final answer. The complete run has a 30-call
   search-and-crawl budget.

## Quality boundaries

- Prefer crawled evidence over snippets. A snippet-only item may be a watchlist
  lead but not a high-confidence headline.
- Separate confirmed facts, reported claims, opinions, forecasts, vendor claims,
  and speculation.
- Do not infer article details from a title.
- Preserve exact names, dates, locations, costs, age guidance, and URLs.
- Explain inaccessible, stale, conflicting, or missing evidence.
- Rank by relevance and actionability for @{audience}, not by sensationalism.
- Respect the exact topic. A related item belongs only when its consequence for
  the topic is explicit.

@match monitor_mode
  "news" ==>
    Prioritize material developments, announcements, primary documents,
    independent verification, technical implications, and skeptical context.
  "events" ==>
    Prioritize upcoming/current activities. Include date, time, place, booking
    URL, cost, eligibility or age fit, practical notes, and cancellation risk.
    Exclude past events unless a future occurrence is confirmed.

@match research_depth
  "quick" ==>
    Use at least three focused searches and crawl the strongest two or three
    sources. Return at most five findings.
  "standard" ==>
    Use at least four query families and crawl at least four diverse sources.
    Return at most seven findings.
  "deep" ==>
    Use at least five query families, targeted follow-ups, and at least six
    diverse source crawls when useful. Return at most eight findings.

@output enforce: strict
  Return Markdown with:

  1. **Monitor snapshot** — brief, run date, actual search/crawl coverage,
     context status, and evidence grade.
  2. **Top findings** — ranked, deduplicated clusters. Each includes status
     (new/material update), what happened, why it matters, what changed when
     applicable, date, strongest primary and independent sources, confidence,
     caveat, and next action.
  3. **Suppressed repeats** — prior or within-run duplicates omitted because
     nothing material changed.
  4. **Source map and gaps** — query families, crawled sources, rejected/weak
     sources, inaccessible pages, and important missing coverage.
  5. **Watchlist for next run** — concrete organizations, sources, queries, and
     unresolved signals.
  6. **Action checklist** — read, verify, subscribe, book, monitor, or ignore.
