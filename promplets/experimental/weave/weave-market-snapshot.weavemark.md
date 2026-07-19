@promplet version: 0.7

@define fetch_asset_snapshot
  @phase execute
  @scope self
  @returns value

  @param ticker
    Ticker symbol to fetch.

  @effect finance_data read

  @body
    Fetch quote, company profile, financial metrics, and analyst context for
    @{ticker} using the bound finance-data tool implementation.

@define search_asset_context
  @phase execute
  @scope self
  @returns value

  @param ticker
    Ticker symbol to research.

  @param company_name
    Company or asset name to use in web queries.

  @param focus
    Research focus for the search queries.

  @effect web_search read

  @body
    Search recent news, analyst opinion, competitive context, and official
    source material for @{company_name} (@{ticker}) using web-search tools.

@define crawl_asset_sources
  @phase execute
  @scope self
  @returns value

  @param body implicit: true mode: subspec
    Source-selection instructions that may reference prior execution results.

  @effect web_crawl read

  @body
    Crawl the most useful source URLs found in the supplied execution context.

    @{body}

@bind finance_data language: python from: "./companions/market_data.py" symbol: fetch_asset_snapshot
@bind web_search language: python from: "./companions/market_data.py" symbol: search_asset_context
@bind web_crawl language: python from: "./companions/market_data.py" symbol: crawl_asset_sources

@execute functional scheduler: graph-strict
  allow_effects: [finance_data, web_search, web_crawl]

# Executable Stock Learning Snapshot

@fetch_asset_snapshot ticker: "@{ticker}" as: asset_snapshot

@search_asset_context ticker: "@{ticker}" company_name: "@{company_name}" focus: "@{research_focus}" as: web_context uses: asset_snapshot

@crawl_asset_sources as: source_readings uses: web_context
  Read the highest-signal URLs found in @{web_context}. Prioritize official
  company pages, recent news, analyst commentary, and skeptical outside views.

## Draft Report

Use @{asset_snapshot}, @{web_context}, and @{source_readings} to write a concise
learning brief about @{company_name} (@{ticker}).

Cover:

1. What the company does and why the stock is currently interesting.
2. Current market data and business fundamentals from the finance tools.
3. Recent news, analyst opinion, and outside commentary from web search.
4. Evidence from crawled sources, with source URLs.
5. Key uncertainties a learner should investigate next.

Do not make a buy/sell recommendation. Treat this as asset education, not
personal financial advice.
