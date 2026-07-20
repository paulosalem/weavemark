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

@bind finance_data language: python from: "./companions/market_data.py" symbol: fetch_asset_snapshot
@bind web_search language: python from: "./companions/market_data.py" symbol: search_asset_context

@execute functional scheduler: graph-strict
  allow_effects: [finance_data, web_search]

# Executable Stock Learning Snapshot

@fetch_asset_snapshot ticker: "@{ticker}" as: asset_snapshot

@search_asset_context ticker: "@{ticker}" company_name: "@{company_name}" focus: "@{research_focus}" as: web_context uses: asset_snapshot

## Draft Report

Use @{asset_snapshot} and @{web_context} to write a concise learning brief about
@{company_name} (@{ticker}). Ground news and outside-context claims only in the
web-search result titles, snippets, source labels, and URLs. Clearly label search
snippets as search-result evidence rather than full-page readings.

Cover:

1. What the company does and why the stock is currently interesting.
2. Current market data and business fundamentals from the finance tools.
3. Recent news, analyst opinion, official context, and skeptical outside
   commentary from web search, with source URLs.
4. Agreements, tensions, and evidence gaps across the source-grounded results.
5. Key uncertainties and primary sources a learner should investigate next.

Do not make a buy/sell recommendation. Treat this as asset education, not
personal financial advice.
