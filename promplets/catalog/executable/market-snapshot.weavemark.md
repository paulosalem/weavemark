@promplet version: 0.7

@use weavemark.domains.finance.market_research exposing fetch_asset_snapshot search_asset_context

@execute functional
  scheduler: graph-strict
  allow_effects: [finance_data, web_search]

# Executable Market Learning Snapshot

@fetch_asset_snapshot ticker: "@{provider_ticker}" as: asset_snapshot

@search_asset_context ticker: "@{display_ticker}" company_name: "@{company_name}" focus: "@{research_focus}" as: web_context uses: asset_snapshot

## Draft Report

Use @{asset_snapshot} and @{web_context} to write a rigorous market-learning
brief about @{company_name} (@{display_ticker}). Ground news and outside-context
claims only in the web-search result titles, snippets, source labels, and URLs.
Clearly label snippets as search-result evidence rather than full-page readings.

Cover:

1. An executive snapshot with the most decision-relevant facts and caveats.
2. What the company does, its economic drivers, and why the stock is currently
   interesting.
3. Current market data and business fundamentals from the finance tools,
   preserving provider units, periods, and missing-value signals.
4. Recent news, analyst opinion, official context, and skeptical outside
   commentary from web search, with source URLs.
5. Agreements, tensions, and evidence gaps across the source-grounded results.
6. A balanced bull/base/bear scenario frame without price targets unless the
   evidence explicitly supplies them.
7. Key uncertainties, watchlist signals, and primary sources a learner should
   investigate next.

Do not make a buy/sell recommendation. Treat this as asset education, not
personal financial advice.

@package instructions: module:weavemark.std.presentation.information_dashboard_html file: vale3-market-dashboard.html
  Title the deliverable "VALE3 Market Learning Dashboard" and identify the
  analyzed security as Vale S.A. on B3 under ticker VALE3. The finance provider
  may label the instrument VALE3.SA; explain that notation once, compactly.

  Give the dashboard an extractive-industry research character without adding
  decorative imagery: make commodity exposure, operational drivers, balance
  sheet signals, evidence quality, cyclical risks, and watchlist items easy to
  scan. Use the current company name, Vale S.A.; mention the historical
  Companhia Vale do Rio Doce name only if useful for identification.

  Retain Portuguese-real amounts and Brazilian-market terminology exactly when
  supplied. Never convert currencies or infer missing values. Keep the final
  educational, non-recommendation disclaimer visible but quiet.
