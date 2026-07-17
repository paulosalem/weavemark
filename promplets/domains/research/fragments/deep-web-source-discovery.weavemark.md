@promplet version: 0.7

@module weavemark.domains.research.deep_web_source_discovery

# Deep Web Source Discovery

@note
  Reusable method for multi-pass web search and crawling that goes beyond one
  shallow search result page.

Use this method when research should deliberately search broad source families,
read selected pages, and follow high-signal links for second-level context.

## Discovery obligations

- Start with diverse query families instead of one query.
- Search for primary or official sources, recent reporting, expert analysis,
  local or domain-specific listings, skeptical viewpoints, and source-rich
  roundups when relevant.
- Deduplicate repeated syndicated stories, mirrored event listings, reposts, and
  low-signal aggregator pages.
- Crawl selected first-level sources to inspect full context rather than relying
  on snippets.
- Extract useful links from crawled pages and crawl selected second-level sources
  when they are likely to add original evidence.
- Stop crawling when additional pages are redundant, stale, inaccessible, or
  lower value than the sources already read.
- Preserve provenance for every material claim: source title, URL, date if
  available, and whether the evidence came from search snippets or crawled text.

## Search families

Use these families as appropriate:

1. **Recent / breaking** — newest material within the lookback window.
2. **Primary / official** — official organizations, calendars, filings,
   announcements, venue pages, or project pages.
3. **Expert / practitioner** — analysis from credible specialists.
4. **Local / domain-specific** — especially for events, activities, venues, and
   practical availability.
5. **Skeptical / contrary** — risks, criticism, cancellation, safety concerns,
   limitations, or counter-evidence.
6. **Roundup / index** — source-rich pages that point to many relevant items.

## Crawl-depth discipline

- `depth 1`: crawl selected search results.
- `depth 2`: crawl selected links found inside first-level crawls.
- `depth 3`: crawl only if the second-level source points to an original source
  that materially improves evidence quality.

The goal is deeper evidence, not more pages.
