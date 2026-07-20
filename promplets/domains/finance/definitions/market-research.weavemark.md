@promplet version: 0.7

@module weavemark.domains.finance.market_research

@bind finance_data language: python from: "./companions/market_data.py" symbol: fetch_asset_snapshot
@bind web_search language: python from: "./companions/market_data.py" symbol: search_asset_context

@define fetch_asset_snapshot
  @phase execute
  @scope self
  @returns value

  @param ticker
    Provider-compatible ticker symbol to fetch.

  @effect finance_data read

  @body
    Fetch quote, company profile, financial metrics, and analyst context for
    @{ticker} using the bound finance-data implementation.

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
