# WeaveMark Execution Trace

| Field | Value |
| --- | --- |
| Spec | `promplets/catalog/executable/financial-independence-goal-plan.weavemark.md` |
| Model | `gpt-5.5` |
| Engine | `functional` |
| Steps | 2 |

## Execution metadata

```json
{
  "status": "executed",
  "execution": {
    "type": "functional",
    "scheduler": "graph-strict",
    "allow_effects": [
      "web_search"
    ],
    "bindings": [
      {
        "name": "web_search",
        "language": "python",
        "from": "./companions/public_finance_reference.py",
        "symbol": "lookup_public_goal_assumptions"
      }
    ],
    "plan": {
      "scheduler": "graph-strict",
      "order": [
        "public_assumptions"
      ],
      "levels": [
        [
          "public_assumptions"
        ]
      ]
    },
    "nodes": [
      {
        "id": "public_assumptions",
        "directive": "lookup_public_goal_assumptions",
        "definition": "lookup_public_goal_assumptions",
        "phase": "execute",
        "scope": "self",
        "returns": "value",
        "effects": [
          {
            "name": "web_search",
            "mode": "read"
          }
        ],
        "args": {
          "positional": [],
          "options": {
            "goal": "@{goal}",
            "domain": "personal finance",
            "country": "@{country}",
            "horizon": "@{horizon}"
          }
        },
        "params": [
          {
            "name": "goal",
            "implicit": false,
            "mode": "text"
          },
          {
            "name": "domain",
            "implicit": false,
            "mode": "text"
          },
          {
            "name": "country",
            "implicit": false,
            "mode": "text"
          },
          {
            "name": "horizon",
            "implicit": false,
            "mode": "text"
          }
        ],
        "body": "",
        "as": "public_assumptions"
      }
    ],
    "status": "executed",
    "evidence": {
      "plan_order": [
        "public_assumptions"
      ],
      "plan_levels": [
        [
          "public_assumptions"
        ]
      ],
      "nodes": [
        {
          "node": "public_assumptions",
          "effect": "web_search",
          "level": 0,
          "arguments": {
            "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
            "domain": "personal finance",
            "country": "United States",
            "horizon": "15 years"
          },
          "result": {
            "effect": "web_search read",
            "mode": "curated-public-reference-pack",
            "privacy_boundary": "Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.",
            "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
            "domain": "personal finance",
            "country": "United States",
            "horizon": "15 years",
            "queries": [
              "United States official retirement account contribution limits",
              "United States investor education compound interest calculator",
              "United States consumer finance budgeting emergency fund guidance",
              "financial independence planning assumptions safe withdrawal rate 15 years",
              "personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference"
            ],
            "sources": [
              {
                "query": "United States official retirement account contribution limits",
                "provider": "curated public reference",
                "results": [
                  {
                    "title": "IRS retirement plan contribution limits",
                    "url": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions",
                    "why_it_matters": "Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning."
                  },
                  {
                    "title": "IRS IRA contribution limits",
                    "url": "https://www.irs.gov/retirement-plans/traditional-and-roth-iras",
                    "why_it_matters": "IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan."
                  }
                ]
              },
              {
                "query": "United States investor education compound interest calculator",
                "provider": "curated public reference",
                "results": [
                  {
                    "title": "Investor.gov compound interest calculator",
                    "url": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator",
                    "why_it_matters": "Compounding examples help turn distant goals into reviewable savings and investment assumptions."
                  }
                ]
              },
              {
                "query": "United States consumer finance budgeting emergency fund guidance",
                "provider": "curated public reference",
                "results": [
                  {
                    "title": "Consumer Financial Protection Bureau budgeting resources",
                    "url": "https://www.consumerfinance.gov/consumer-tools/budgeting/",
                    "why_it_matters": "Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions."
                  }
                ]
              },
              {
                "query": "financial independence planning assumptions safe withdrawal rate 15 years",
                "provider": "curated public reference",
                "results": [
                  {
                    "title": "Bogleheads wiki: Safe withdrawal rates",
                    "url": "https://www.bogleheads.org/wiki/Safe_withdrawal_rates",
                    "why_it_matters": "Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user."
                  }
                ]
              }
            ],
            "assumptions_to_verify": [
              "current tax-advantaged account contribution limits",
              "current local tax treatment and withdrawal rules",
              "inflation and expected expense assumptions",
              "safe-withdrawal assumptions appropriate to the user's country",
              "health insurance, housing, family, and job-risk constraints"
            ],
            "planning_lenses": [
              "savings-rate leverage",
              "expense-floor realism",
              "income resilience",
              "emergency-fund runway",
              "investment-policy clarity",
              "review cadence and behavior guardrails"
            ]
          }
        }
      ],
      "errors": [],
      "rendered_document": "# Finance Safety and Evidence Guideline\n\n\nUse this guideline when a finance task retrieves, analyzes, calculates, or explains\nfinancial information.\n\n## Core finance safety rules\n\n- Treat financial content as educational analysis or decision support, not\n  regulated financial, legal, tax, accounting, or brokerage advice.\n- Do not guarantee returns, prices, yields, forecasts, tax outcomes, or risk\n  reductions.\n- Prefer verified tool or source data over memory. When data is missing, stale,\n  ambiguous, or conflicting, say so and avoid inventing values.\n- Surface downside risk before giving action-oriented suggestions.\n- Separate supplied inputs, retrieved data, deterministic calculations,\n  assumptions, interpretation, and suggested actions.\n\n## Surface-specific rules\n\nFor personalized or high-stakes advisory output:\n\n- Frame actions as options rather than instructions.\n- Suggest checking fiduciary, tax, legal, or accounting professionals when\n  appropriate.\n- Ask focused questions when missing goals, horizon, country/tax context,\n  liquidity needs, or risk limits would change the recommendation.\n\nFor market-data output:\n\n- Treat market-data provider values and derived fundamentals as data, not\n  advice.\n- Prefer structured finance tools and authoritative local references before\n  broader web evidence.\n- Mention provider availability limits when fields are missing.\n\nFor calculation output:\n\n- Treat calculator results as deterministic consequences of the supplied inputs.\n- Verify units, signs, rates, periods, currencies, and cash-flow timing before\n  reporting.\n- Do not turn a computed metric into a recommendation without separately stating\n  assumptions and limits.\n\nFor technical-analysis output:\n\n- Treat indicators and charts as descriptive signals, not predictions.\n- Mention lookback windows, data source, and indicator limitations.\n- Do not imply that technical indicators guarantee future price movement.\n\n\n\n# Executable Financial Independence Goal Planner\n\n{\"effect\": \"web_search read\", \"mode\": \"curated-public-reference-pack\", \"privacy_boundary\": \"Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.\", \"goal\": \"Reach financial independence while keeping work optional, not necessarily retiring early\", \"domain\": \"personal finance\", \"country\": \"United States\", \"horizon\": \"15 years\", \"queries\": [\"United States official retirement account contribution limits\", \"United States investor education compound interest calculator\", \"United States consumer finance budgeting emergency fund guidance\", \"financial independence planning assumptions safe withdrawal rate 15 years\", \"personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference\"], \"sources\": [{\"query\": \"United States official retirement account contribution limits\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"IRS retirement plan contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions\", \"why_it_matters\": \"Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning.\"}, {\"title\": \"IRS IRA contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/traditional-and-roth-iras\", \"why_it_matters\": \"IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan.\"}]}, {\"query\": \"United States investor education compound interest calculator\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Investor.gov compound interest calculator\", \"url\": \"https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator\", \"why_it_matters\": \"Compounding examples help turn distant goals into reviewable savings and investment assumptions.\"}]}, {\"query\": \"United States consumer finance budgeting emergency fund guidance\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Consumer Financial Protection Bureau budgeting resources\", \"url\": \"https://www.consumerfinance.gov/consumer-tools/budgeting/\", \"why_it_matters\": \"Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions.\"}]}, {\"query\": \"financial independence planning assumptions safe withdrawal rate 15 years\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Bogleheads wiki: Safe withdrawal rates\", \"url\": \"https://www.bogleheads.org/wiki/Safe_withdrawal_rates\", \"why_it_matters\": \"Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user.\"}]}], \"assumptions_to_verify\": [\"current tax-advantaged account contribution limits\", \"current local tax treatment and withdrawal rules\", \"inflation and expected expense assumptions\", \"safe-withdrawal assumptions appropriate to the user's country\", \"health insurance, housing, family, and job-risk constraints\"], \"planning_lenses\": [\"savings-rate leverage\", \"expense-floor realism\", \"income resilience\", \"emergency-fund runway\", \"investment-policy clarity\", \"review cadence and behavior guardrails\"]}\n\n# Goal-to-plan compiler\n\nTurn one plain-language goal into a practical plan.\n\n- Goal: Reach financial independence while keeping work optional, not necessarily retiring early\n- Domain: personal finance\n- Horizon: 15 years\n- Starting point: I have a steady income, save irregularly, and want a simple plan I can review monthly.\n- Constraints: Avoid extreme frugality, avoid private-data uploads, keep the first actions simple, and treat all public assumptions as facts to verify.\n- Assumption source: {\"effect\": \"web_search read\", \"mode\": \"curated-public-reference-pack\", \"privacy_boundary\": \"Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.\", \"goal\": \"Reach financial independence while keeping work optional, not necessarily retiring early\", \"domain\": \"personal finance\", \"country\": \"United States\", \"horizon\": \"15 years\", \"queries\": [\"United States official retirement account contribution limits\", \"United States investor education compound interest calculator\", \"United States consumer finance budgeting emergency fund guidance\", \"financial independence planning assumptions safe withdrawal rate 15 years\", \"personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference\"], \"sources\": [{\"query\": \"United States official retirement account contribution limits\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"IRS retirement plan contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions\", \"why_it_matters\": \"Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning.\"}, {\"title\": \"IRS IRA contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/traditional-and-roth-iras\", \"why_it_matters\": \"IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan.\"}]}, {\"query\": \"United States investor education compound interest calculator\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Investor.gov compound interest calculator\", \"url\": \"https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator\", \"why_it_matters\": \"Compounding examples help turn distant goals into reviewable savings and investment assumptions.\"}]}, {\"query\": \"United States consumer finance budgeting emergency fund guidance\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Consumer Financial Protection Bureau budgeting resources\", \"url\": \"https://www.consumerfinance.gov/consumer-tools/budgeting/\", \"why_it_matters\": \"Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions.\"}]}, {\"query\": \"financial independence planning assumptions safe withdrawal rate 15 years\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Bogleheads wiki: Safe withdrawal rates\", \"url\": \"https://www.bogleheads.org/wiki/Safe_withdrawal_rates\", \"why_it_matters\": \"Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user.\"}]}], \"assumptions_to_verify\": [\"current tax-advantaged account contribution limits\", \"current local tax treatment and withdrawal rules\", \"inflation and expected expense assumptions\", \"safe-withdrawal assumptions appropriate to the user's country\", \"health insurance, housing, family, and job-risk constraints\"], \"planning_lenses\": [\"savings-rate leverage\", \"expense-floor realism\", \"income resilience\", \"emergency-fund runway\", \"investment-policy clarity\", \"review cadence and behavior guardrails\"]}\n\nFirst state explicit assumptions. If the assumption source is incomplete or\nstale, say what the user must verify before acting.\n\n### Define the finish line\n\nPurpose: Translate the goal into observable success criteria.\n\nDone when: The plan has one measurable target, one date or horizon, and one review trigger.\n\n### Map the current state\n\nPurpose: Separate facts, estimates, unknowns, and constraints before recommending action.\n\nDone when: The plan lists the user's current resources, gaps, and unknowns without pretending missing data is known.\n\n### Build the milestone ladder\n\nPurpose: Turn a distant goal into near, middle, and long-horizon milestones.\n\nDone when: The plan has first-week, first-month, quarterly, and horizon-level milestones.\n\n### Choose the next action set\n\nPurpose: Make the first move concrete enough to do without another planning session.\n\nDone when: The plan names 3-5 first-month actions, their order, and why each comes first.\n\n### Install the review loop\n\nPurpose: Keep the plan alive as conditions change.\n\nDone when: The plan includes a lightweight cadence, metrics to check, and conditions for revising the strategy.\n\n## Required output\n\n## Output format\n\nReturn exactly these sections:\n1. Goal profile\n2. Assumptions to verify\n3. Milestone ladder\n4. First-month actions\n5. Review cadence\n6. Failure modes and safeguards\n\nEnforcement level: strict.\n\n\nUse the public assumptions only as planning context. Ask the user to verify any\ncurrent limits, rates, tax rules, or benefits before acting. Do not request\nprivate account uploads.",
      "final_document_mode": "llm"
    }
  },
  "bindings": [
    {
      "name": "web_search",
      "language": "python",
      "from": "./companions/public_finance_reference.py",
      "symbol": "lookup_public_goal_assumptions"
    }
  ],
  "results": {
    "public_assumptions": {
      "effect": "web_search read",
      "mode": "curated-public-reference-pack",
      "privacy_boundary": "Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.",
      "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
      "domain": "personal finance",
      "country": "United States",
      "horizon": "15 years",
      "queries": [
        "United States official retirement account contribution limits",
        "United States investor education compound interest calculator",
        "United States consumer finance budgeting emergency fund guidance",
        "financial independence planning assumptions safe withdrawal rate 15 years",
        "personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference"
      ],
      "sources": [
        {
          "query": "United States official retirement account contribution limits",
          "provider": "curated public reference",
          "results": [
            {
              "title": "IRS retirement plan contribution limits",
              "url": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions",
              "why_it_matters": "Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning."
            },
            {
              "title": "IRS IRA contribution limits",
              "url": "https://www.irs.gov/retirement-plans/traditional-and-roth-iras",
              "why_it_matters": "IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan."
            }
          ]
        },
        {
          "query": "United States investor education compound interest calculator",
          "provider": "curated public reference",
          "results": [
            {
              "title": "Investor.gov compound interest calculator",
              "url": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator",
              "why_it_matters": "Compounding examples help turn distant goals into reviewable savings and investment assumptions."
            }
          ]
        },
        {
          "query": "United States consumer finance budgeting emergency fund guidance",
          "provider": "curated public reference",
          "results": [
            {
              "title": "Consumer Financial Protection Bureau budgeting resources",
              "url": "https://www.consumerfinance.gov/consumer-tools/budgeting/",
              "why_it_matters": "Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions."
            }
          ]
        },
        {
          "query": "financial independence planning assumptions safe withdrawal rate 15 years",
          "provider": "curated public reference",
          "results": [
            {
              "title": "Bogleheads wiki: Safe withdrawal rates",
              "url": "https://www.bogleheads.org/wiki/Safe_withdrawal_rates",
              "why_it_matters": "Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user."
            }
          ]
        }
      ],
      "assumptions_to_verify": [
        "current tax-advantaged account contribution limits",
        "current local tax treatment and withdrawal rules",
        "inflation and expected expense assumptions",
        "safe-withdrawal assumptions appropriate to the user's country",
        "health insurance, housing, family, and job-risk constraints"
      ],
      "planning_lenses": [
        "savings-rate leverage",
        "expense-floor realism",
        "income resilience",
        "emergency-fund runway",
        "investment-policy clarity",
        "review cadence and behavior guardrails"
      ]
    }
  },
  "evidence": {
    "plan_order": [
      "public_assumptions"
    ],
    "plan_levels": [
      [
        "public_assumptions"
      ]
    ],
    "nodes": [
      {
        "node": "public_assumptions",
        "effect": "web_search",
        "level": 0,
        "arguments": {
          "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
          "domain": "personal finance",
          "country": "United States",
          "horizon": "15 years"
        },
        "result": {
          "effect": "web_search read",
          "mode": "curated-public-reference-pack",
          "privacy_boundary": "Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.",
          "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
          "domain": "personal finance",
          "country": "United States",
          "horizon": "15 years",
          "queries": [
            "United States official retirement account contribution limits",
            "United States investor education compound interest calculator",
            "United States consumer finance budgeting emergency fund guidance",
            "financial independence planning assumptions safe withdrawal rate 15 years",
            "personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference"
          ],
          "sources": [
            {
              "query": "United States official retirement account contribution limits",
              "provider": "curated public reference",
              "results": [
                {
                  "title": "IRS retirement plan contribution limits",
                  "url": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions",
                  "why_it_matters": "Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning."
                },
                {
                  "title": "IRS IRA contribution limits",
                  "url": "https://www.irs.gov/retirement-plans/traditional-and-roth-iras",
                  "why_it_matters": "IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan."
                }
              ]
            },
            {
              "query": "United States investor education compound interest calculator",
              "provider": "curated public reference",
              "results": [
                {
                  "title": "Investor.gov compound interest calculator",
                  "url": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator",
                  "why_it_matters": "Compounding examples help turn distant goals into reviewable savings and investment assumptions."
                }
              ]
            },
            {
              "query": "United States consumer finance budgeting emergency fund guidance",
              "provider": "curated public reference",
              "results": [
                {
                  "title": "Consumer Financial Protection Bureau budgeting resources",
                  "url": "https://www.consumerfinance.gov/consumer-tools/budgeting/",
                  "why_it_matters": "Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions."
                }
              ]
            },
            {
              "query": "financial independence planning assumptions safe withdrawal rate 15 years",
              "provider": "curated public reference",
              "results": [
                {
                  "title": "Bogleheads wiki: Safe withdrawal rates",
                  "url": "https://www.bogleheads.org/wiki/Safe_withdrawal_rates",
                  "why_it_matters": "Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user."
                }
              ]
            }
          ],
          "assumptions_to_verify": [
            "current tax-advantaged account contribution limits",
            "current local tax treatment and withdrawal rules",
            "inflation and expected expense assumptions",
            "safe-withdrawal assumptions appropriate to the user's country",
            "health insurance, housing, family, and job-risk constraints"
          ],
          "planning_lenses": [
            "savings-rate leverage",
            "expense-floor realism",
            "income resilience",
            "emergency-fund runway",
            "investment-policy clarity",
            "review cadence and behavior guardrails"
          ]
        }
      }
    ],
    "errors": [],
    "rendered_document": "# Finance Safety and Evidence Guideline\n\n\nUse this guideline when a finance task retrieves, analyzes, calculates, or explains\nfinancial information.\n\n## Core finance safety rules\n\n- Treat financial content as educational analysis or decision support, not\n  regulated financial, legal, tax, accounting, or brokerage advice.\n- Do not guarantee returns, prices, yields, forecasts, tax outcomes, or risk\n  reductions.\n- Prefer verified tool or source data over memory. When data is missing, stale,\n  ambiguous, or conflicting, say so and avoid inventing values.\n- Surface downside risk before giving action-oriented suggestions.\n- Separate supplied inputs, retrieved data, deterministic calculations,\n  assumptions, interpretation, and suggested actions.\n\n## Surface-specific rules\n\nFor personalized or high-stakes advisory output:\n\n- Frame actions as options rather than instructions.\n- Suggest checking fiduciary, tax, legal, or accounting professionals when\n  appropriate.\n- Ask focused questions when missing goals, horizon, country/tax context,\n  liquidity needs, or risk limits would change the recommendation.\n\nFor market-data output:\n\n- Treat market-data provider values and derived fundamentals as data, not\n  advice.\n- Prefer structured finance tools and authoritative local references before\n  broader web evidence.\n- Mention provider availability limits when fields are missing.\n\nFor calculation output:\n\n- Treat calculator results as deterministic consequences of the supplied inputs.\n- Verify units, signs, rates, periods, currencies, and cash-flow timing before\n  reporting.\n- Do not turn a computed metric into a recommendation without separately stating\n  assumptions and limits.\n\nFor technical-analysis output:\n\n- Treat indicators and charts as descriptive signals, not predictions.\n- Mention lookback windows, data source, and indicator limitations.\n- Do not imply that technical indicators guarantee future price movement.\n\n\n\n# Executable Financial Independence Goal Planner\n\n{\"effect\": \"web_search read\", \"mode\": \"curated-public-reference-pack\", \"privacy_boundary\": \"Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.\", \"goal\": \"Reach financial independence while keeping work optional, not necessarily retiring early\", \"domain\": \"personal finance\", \"country\": \"United States\", \"horizon\": \"15 years\", \"queries\": [\"United States official retirement account contribution limits\", \"United States investor education compound interest calculator\", \"United States consumer finance budgeting emergency fund guidance\", \"financial independence planning assumptions safe withdrawal rate 15 years\", \"personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference\"], \"sources\": [{\"query\": \"United States official retirement account contribution limits\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"IRS retirement plan contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions\", \"why_it_matters\": \"Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning.\"}, {\"title\": \"IRS IRA contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/traditional-and-roth-iras\", \"why_it_matters\": \"IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan.\"}]}, {\"query\": \"United States investor education compound interest calculator\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Investor.gov compound interest calculator\", \"url\": \"https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator\", \"why_it_matters\": \"Compounding examples help turn distant goals into reviewable savings and investment assumptions.\"}]}, {\"query\": \"United States consumer finance budgeting emergency fund guidance\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Consumer Financial Protection Bureau budgeting resources\", \"url\": \"https://www.consumerfinance.gov/consumer-tools/budgeting/\", \"why_it_matters\": \"Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions.\"}]}, {\"query\": \"financial independence planning assumptions safe withdrawal rate 15 years\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Bogleheads wiki: Safe withdrawal rates\", \"url\": \"https://www.bogleheads.org/wiki/Safe_withdrawal_rates\", \"why_it_matters\": \"Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user.\"}]}], \"assumptions_to_verify\": [\"current tax-advantaged account contribution limits\", \"current local tax treatment and withdrawal rules\", \"inflation and expected expense assumptions\", \"safe-withdrawal assumptions appropriate to the user's country\", \"health insurance, housing, family, and job-risk constraints\"], \"planning_lenses\": [\"savings-rate leverage\", \"expense-floor realism\", \"income resilience\", \"emergency-fund runway\", \"investment-policy clarity\", \"review cadence and behavior guardrails\"]}\n\n# Goal-to-plan compiler\n\nTurn one plain-language goal into a practical plan.\n\n- Goal: Reach financial independence while keeping work optional, not necessarily retiring early\n- Domain: personal finance\n- Horizon: 15 years\n- Starting point: I have a steady income, save irregularly, and want a simple plan I can review monthly.\n- Constraints: Avoid extreme frugality, avoid private-data uploads, keep the first actions simple, and treat all public assumptions as facts to verify.\n- Assumption source: {\"effect\": \"web_search read\", \"mode\": \"curated-public-reference-pack\", \"privacy_boundary\": \"Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.\", \"goal\": \"Reach financial independence while keeping work optional, not necessarily retiring early\", \"domain\": \"personal finance\", \"country\": \"United States\", \"horizon\": \"15 years\", \"queries\": [\"United States official retirement account contribution limits\", \"United States investor education compound interest calculator\", \"United States consumer finance budgeting emergency fund guidance\", \"financial independence planning assumptions safe withdrawal rate 15 years\", \"personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference\"], \"sources\": [{\"query\": \"United States official retirement account contribution limits\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"IRS retirement plan contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions\", \"why_it_matters\": \"Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning.\"}, {\"title\": \"IRS IRA contribution limits\", \"url\": \"https://www.irs.gov/retirement-plans/traditional-and-roth-iras\", \"why_it_matters\": \"IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan.\"}]}, {\"query\": \"United States investor education compound interest calculator\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Investor.gov compound interest calculator\", \"url\": \"https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator\", \"why_it_matters\": \"Compounding examples help turn distant goals into reviewable savings and investment assumptions.\"}]}, {\"query\": \"United States consumer finance budgeting emergency fund guidance\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Consumer Financial Protection Bureau budgeting resources\", \"url\": \"https://www.consumerfinance.gov/consumer-tools/budgeting/\", \"why_it_matters\": \"Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions.\"}]}, {\"query\": \"financial independence planning assumptions safe withdrawal rate 15 years\", \"provider\": \"curated public reference\", \"results\": [{\"title\": \"Bogleheads wiki: Safe withdrawal rates\", \"url\": \"https://www.bogleheads.org/wiki/Safe_withdrawal_rates\", \"why_it_matters\": \"Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user.\"}]}], \"assumptions_to_verify\": [\"current tax-advantaged account contribution limits\", \"current local tax treatment and withdrawal rules\", \"inflation and expected expense assumptions\", \"safe-withdrawal assumptions appropriate to the user's country\", \"health insurance, housing, family, and job-risk constraints\"], \"planning_lenses\": [\"savings-rate leverage\", \"expense-floor realism\", \"income resilience\", \"emergency-fund runway\", \"investment-policy clarity\", \"review cadence and behavior guardrails\"]}\n\nFirst state explicit assumptions. If the assumption source is incomplete or\nstale, say what the user must verify before acting.\n\n### Define the finish line\n\nPurpose: Translate the goal into observable success criteria.\n\nDone when: The plan has one measurable target, one date or horizon, and one review trigger.\n\n### Map the current state\n\nPurpose: Separate facts, estimates, unknowns, and constraints before recommending action.\n\nDone when: The plan lists the user's current resources, gaps, and unknowns without pretending missing data is known.\n\n### Build the milestone ladder\n\nPurpose: Turn a distant goal into near, middle, and long-horizon milestones.\n\nDone when: The plan has first-week, first-month, quarterly, and horizon-level milestones.\n\n### Choose the next action set\n\nPurpose: Make the first move concrete enough to do without another planning session.\n\nDone when: The plan names 3-5 first-month actions, their order, and why each comes first.\n\n### Install the review loop\n\nPurpose: Keep the plan alive as conditions change.\n\nDone when: The plan includes a lightweight cadence, metrics to check, and conditions for revising the strategy.\n\n## Required output\n\n## Output format\n\nReturn exactly these sections:\n1. Goal profile\n2. Assumptions to verify\n3. Milestone ladder\n4. First-month actions\n5. Review cadence\n6. Failure modes and safeguards\n\nEnforcement level: strict.\n\n\nUse the public assumptions only as planning context. Ask the user to verify any\ncurrent limits, rates, tax rules, or benefits before acting. Do not request\nprivate account uploads.",
    "final_document_mode": "llm"
  },
  "call_settings": {
    "model": "gpt-5.5",
    "modality": "text",
    "prompt_key": "default",
    "stage": "final-document",
    "model_source": "runtime.model"
  }
}
```

## Steps

### 1. public_assumptions

- Prompt key: `lookup_public_goal_assumptions`
- Metadata:

```json
{
  "status": "executed",
  "node": "public_assumptions",
  "effect": "web_search",
  "level": 0,
  "arguments": {
    "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
    "domain": "personal finance",
    "country": "United States",
    "horizon": "15 years"
  },
  "result": {
    "effect": "web_search read",
    "mode": "curated-public-reference-pack",
    "privacy_boundary": "Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.",
    "goal": "Reach financial independence while keeping work optional, not necessarily retiring early",
    "domain": "personal finance",
    "country": "United States",
    "horizon": "15 years",
    "queries": [
      "United States official retirement account contribution limits",
      "United States investor education compound interest calculator",
      "United States consumer finance budgeting emergency fund guidance",
      "financial independence planning assumptions safe withdrawal rate 15 years",
      "personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference"
    ],
    "sources": [
      {
        "query": "United States official retirement account contribution limits",
        "provider": "curated public reference",
        "results": [
          {
            "title": "IRS retirement plan contribution limits",
            "url": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions",
            "why_it_matters": "Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning."
          },
          {
            "title": "IRS IRA contribution limits",
            "url": "https://www.irs.gov/retirement-plans/traditional-and-roth-iras",
            "why_it_matters": "IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan."
          }
        ]
      },
      {
        "query": "United States investor education compound interest calculator",
        "provider": "curated public reference",
        "results": [
          {
            "title": "Investor.gov compound interest calculator",
            "url": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator",
            "why_it_matters": "Compounding examples help turn distant goals into reviewable savings and investment assumptions."
          }
        ]
      },
      {
        "query": "United States consumer finance budgeting emergency fund guidance",
        "provider": "curated public reference",
        "results": [
          {
            "title": "Consumer Financial Protection Bureau budgeting resources",
            "url": "https://www.consumerfinance.gov/consumer-tools/budgeting/",
            "why_it_matters": "Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions."
          }
        ]
      },
      {
        "query": "financial independence planning assumptions safe withdrawal rate 15 years",
        "provider": "curated public reference",
        "results": [
          {
            "title": "Bogleheads wiki: Safe withdrawal rates",
            "url": "https://www.bogleheads.org/wiki/Safe_withdrawal_rates",
            "why_it_matters": "Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user."
          }
        ]
      }
    ],
    "assumptions_to_verify": [
      "current tax-advantaged account contribution limits",
      "current local tax treatment and withdrawal rules",
      "inflation and expected expense assumptions",
      "safe-withdrawal assumptions appropriate to the user's country",
      "health insurance, housing, family, and job-risk constraints"
    ],
    "planning_lenses": [
      "savings-rate leverage",
      "expense-floor realism",
      "income resilience",
      "emergency-fund runway",
      "investment-policy clarity",
      "review cadence and behavior guardrails"
    ]
  }
}
```
- Response:

```markdown
{"effect": "web_search read", "mode": "curated-public-reference-pack", "privacy_boundary": "Uses public reference material only. It does not read bank accounts, transactions, portfolios, credit reports, or identity data.", "goal": "Reach financial independence while keeping work optional, not necessarily retiring early", "domain": "personal finance", "country": "United States", "horizon": "15 years", "queries": ["United States official retirement account contribution limits", "United States investor education compound interest calculator", "United States consumer finance budgeting emergency fund guidance", "financial independence planning assumptions safe withdrawal rate 15 years", "personal finance planning Reach financial independence while keeping work optional, not necessarily retiring early personal finance public reference"], "sources": [{"query": "United States official retirement account contribution limits", "provider": "curated public reference", "results": [{"title": "IRS retirement plan contribution limits", "url": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions", "why_it_matters": "Tax-advantaged contribution limits are public facts that can change yearly and should be verified before planning."}, {"title": "IRS IRA contribution limits", "url": "https://www.irs.gov/retirement-plans/traditional-and-roth-iras", "why_it_matters": "IRA rules affect which savings vehicles might be relevant for a U.S. financial-independence plan."}]}, {"query": "United States investor education compound interest calculator", "provider": "curated public reference", "results": [{"title": "Investor.gov compound interest calculator", "url": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator", "why_it_matters": "Compounding examples help turn distant goals into reviewable savings and investment assumptions."}]}, {"query": "United States consumer finance budgeting emergency fund guidance", "provider": "curated public reference", "results": [{"title": "Consumer Financial Protection Bureau budgeting resources", "url": "https://www.consumerfinance.gov/consumer-tools/budgeting/", "why_it_matters": "Budgeting and cash-flow guidance keeps the first steps grounded before any investment assumptions."}]}, {"query": "financial independence planning assumptions safe withdrawal rate 15 years", "provider": "curated public reference", "results": [{"title": "Bogleheads wiki: Safe withdrawal rates", "url": "https://www.bogleheads.org/wiki/Safe_withdrawal_rates", "why_it_matters": "Safe-withdrawal-rate discussion is useful context, but it is not a guarantee and must be adapted to the user."}]}], "assumptions_to_verify": ["current tax-advantaged account contribution limits", "current local tax treatment and withdrawal rules", "inflation and expected expense assumptions", "safe-withdrawal assumptions appropriate to the user's country", "health insurance, housing, family, and job-risk constraints"], "planning_lenses": ["savings-rate leverage", "expense-floor realism", "income resilience", "emergency-fund runway", "investment-policy clarity", "review cadence and behavior guardrails"]}
```

### 2. document

- Prompt key: `default`
- Metadata:

```json
{
  "status": "executed",
  "mode": "llm",
  "call_settings": {
    "model": "gpt-5.5",
    "modality": "text",
    "prompt_key": "default",
    "stage": "final-document",
    "model_source": "runtime.model"
  }
}
```
- Response:

```markdown
## 1. Goal profile

**Goal:** Reach financial independence in 15 years so work becomes optional, not necessarily to retire early.

**Planning stance:** Educational decision support, not financial, tax, legal, accounting, or investment advice. Public assumptions and rules must be verified before acting.

**Explicit assumptions used for this plan:**

- Country/context: United States.
- Horizon: 15 years.
- You have steady income.
- You currently save irregularly.
- You want a simple plan reviewed monthly.
- You want to avoid extreme frugality.
- You do not want to upload private account data.
- Public references are planning context only, not guaranteed current rules.
- Financial independence means your invested assets can plausibly support your required lifestyle spending, with work becoming optional.

**Finish line / measurable target:**

Your working FI target is:

> **FI number = 25–33 × annual work-optional spending**

That corresponds roughly to a **3%–4% initial withdrawal-rate planning range**, which is a common FI planning shorthand but **not a guarantee**. A lower withdrawal rate is more conservative; a higher rate requires more flexibility and carries more risk.

Example formula only:

- If annual work-optional spending is `$60,000`, then:
  - 25× target = `$1,500,000`
  - 33× target = about `$1,980,000`

**15-year target date:** 15 years from the month you start this plan.

**Review trigger:** Revise the plan if any of these change materially:

- Income changes by 10%+.
- Annual spending changes by 10%+.
- You change jobs, housing, family plans, location, or health insurance needs.
- Your savings rate is off target for 3 consecutive months.
- Market declines or life events would force you to sell investments early.
- Tax rules, retirement account limits, or employer benefits change.

---

## 2. Assumptions to verify

Before acting, verify these because public rules, limits, tax treatment, and benefits can change:

1. **Current retirement account contribution limits**
   - Verify current 401(k), 403(b), 457, IRA, Roth IRA, HSA, and catch-up contribution limits if relevant.
   - Source to check: IRS retirement plan and IRA contribution limit pages.

2. **Employer benefits**
   - Employer retirement match.
   - Vesting schedule.
   - HSA eligibility.
   - Employee stock purchase plan, pension, deferred compensation, or other benefits.

3. **Tax treatment**
   - Traditional vs. Roth contribution eligibility and tradeoffs.
   - State income tax treatment.
   - Taxability of brokerage investment gains.
   - Early-withdrawal rules for retirement accounts.

4. **Emergency fund need**
   - Public budgeting guidance often suggests building cash resilience before taking investment risk, but the right amount depends on job stability, dependents, insurance, debt, and fixed expenses.

5. **Inflation and spending assumptions**
   - Your FI number depends more on future spending than today’s income.
   - Housing, healthcare, childcare, eldercare, insurance, and taxes may materially change your target.

6. **Safe-withdrawal assumptions**
   - A 3%–4% withdrawal-rate range is a planning assumption, not a promise.
   - Sequence-of-returns risk, inflation, taxes, fees, and spending flexibility matter.

7. **Debt costs**
   - High-interest debt may need priority over investing.
   - Low-interest fixed debt may be handled differently depending on risk tolerance and cash flow.

8. **Investment assumptions**
   - Expected returns are uncertain.
   - Diversification may reduce concentration risk but does not eliminate losses.
   - Any long-term return estimate should be treated as a scenario, not a forecast.

---

## 3. Milestone ladder

### First week: define the baseline without uploading private data

**Milestone:** Create a one-page FI dashboard using only numbers you enter manually.

Track:

- Monthly take-home income.
- Monthly essential spending.
- Monthly lifestyle/discretionary spending.
- Monthly debt payments.
- Current cash savings.
- Current invested assets.
- Current retirement contributions.
- Employer match status.
- Estimated annual work-optional spending.
- Current savings rate.

**Key output by end of week:**

> “My current annual work-optional spending estimate is `$X`, so my FI target range is approximately `25X–33X`.”

If you do not know exact spending, start with a rough estimate and refine it over 2–3 months.

---

### First month: stabilize the system

**Milestone:** Convert irregular saving into automatic saving.

Targets to establish:

- A default monthly savings amount.
- A minimum emergency fund target.
- A retirement contribution plan.
- A simple investment-policy draft.
- A monthly review date.

Suggested monthly savings-rate ladder:

- **Starter:** 10% of gross income.
- **Strong:** 20%–30%.
- **Aggressive but not extreme:** 35%+ if it does not damage quality of life or resilience.

For a 15-year FI horizon, the required savings rate may need to be high, especially if starting assets are low. If your current savings rate is far below the needed level, the plan should focus first on gradually increasing it rather than forcing an unrealistic target immediately.

---

### Quarterly: improve the engine

Every quarter, review:

- Savings rate.
- Spending trend.
- Net worth trend.
- Debt balances.
- Emergency fund progress.
- Retirement contribution progress.
- Asset allocation drift.
- Income growth opportunities.
- Lifestyle satisfaction.

Quarterly milestone examples:

- Quarter 1: Know your true monthly spending.
- Quarter 2: Capture full employer match if available.
- Quarter 3: Build or confirm emergency fund target.
- Quarter 4: Increase savings rate by 1–3 percentage points if sustainable.
- Year 2 onward: Review whether FI target, income, and spending assumptions still align.

---

### Horizon-level: 15-year work-optional checkpoint

At year 15, the plan is successful if:

- Invested assets are near or above your selected FI target range.
- Essential expenses can be covered with a conservative withdrawal plan.
- You have a cash buffer or flexible spending plan.
- Healthcare, housing, taxes, and major family obligations are accounted for.
- Work is optional because your finances support choices, not because a spreadsheet says so.

A realistic horizon outcome may be one of three states:

1. **Fully work-optional:** Assets support desired spending with reasonable margin.
2. **Partially work-optional:** You can reduce hours, change careers, consult, freelance, or take sabbaticals.
3. **Not yet FI, but much stronger:** You have high savings discipline, lower financial stress, and more flexibility.

---

## 4. First-month actions

### Action 1: Define your “work-optional spending” number

**Order:** First.

**Why it comes first:** FI is based on spending, not income. Without a spending target, the FI number is undefined.

Do this manually:

- Estimate your current annual spending.
- Remove costs that may disappear after work becomes optional, such as commuting or some work expenses.
- Add costs that may rise, such as healthcare, travel, hobbies, taxes, or insurance.
- Choose a first-draft annual work-optional spending number.

Then calculate:

> **FI target range = annual work-optional spending × 25 to 33**

Use this as a starting range, not a guaranteed endpoint.

---

### Action 2: Build a simple monthly cash-flow map

**Order:** Second.

**Why it comes first:** Irregular saving is usually a cash-flow design problem, not a motivation problem.

Create four categories:

1. Income.
2. Essential spending.
3. Flexible spending.
4. Saving/investing/debt payoff.

You do not need to upload data. Use a spreadsheet, notebook, or budgeting app with manual entry.

Your goal is to identify:

- Minimum monthly expenses.
- Average monthly expenses.
- Monthly surplus.
- Expenses that do not improve your life enough to justify delaying FI.

Avoid extreme frugality. Look for “low-regret” savings first:

- Unused subscriptions.
- Insurance comparison shopping.
- Bank fees.
- High-cost convenience spending.
- Lifestyle creep after raises.
- Large recurring expenses that do not match your priorities.

---

### Action 3: Set up automatic saving

**Order:** Third.

**Why it comes first:** Automation turns FI from a willpower goal into a default system.

Options to consider:

- Automatic transfer to emergency savings.
- Payroll contribution to retirement plan.
- Automatic IRA contribution if eligible.
- Automatic brokerage investment after emergency fund and high-interest debt are addressed.

A simple rule:

> Save automatically right after income arrives, then spend what remains.

Start with an amount you can sustain. If unsure, begin with a small automatic transfer and increase it monthly or quarterly.

---

### Action 4: Capture obvious tax-advantaged opportunities after verifying rules

**Order:** Fourth.

**Why it comes first:** Tax-advantaged accounts and employer matches can materially affect long-term compounding.

Check, without assuming rules are current:

- Employer match availability.
- 401(k)/403(b)/457 contribution limits.
- Traditional vs. Roth eligibility.
- IRA eligibility.
- HSA eligibility if you have a qualifying high-deductible health plan.
- Vesting schedules.
- Fees and investment options.

Possible priority sequence, subject to your situation:

1. Build a starter emergency fund.
2. Contribute enough to get full employer match if available.
3. Address high-interest debt.
4. Increase tax-advantaged contributions.
5. Use taxable brokerage investing for additional FI flexibility.

This is a framework, not a command. Tax and account-order decisions can depend heavily on income, state, age, employer plan, and future tax assumptions.

---

### Action 5: Write a one-page investment policy

**Order:** Fifth.

**Why it comes first:** A simple policy reduces emotional decisions during market declines.

Include:

- Target asset allocation.
- Account types used.
- Contribution schedule.
- Rebalancing rule.
- What you will do during market declines.
- What would cause you to change the plan.

Example structure:

> “I will invest for a 15-year-plus horizon using diversified, low-cost funds. I will contribute monthly, review quarterly, and avoid changing the plan based only on short-term market news.”

Investment risk to acknowledge:

- Stocks can fall sharply and stay down for years.
- Bonds can lose value when rates change.
- Inflation can reduce purchasing power.
- Concentrated positions can create large losses.
- A 15-year horizon is meaningful but not risk-free.

---

## 5. Review cadence

### Monthly review: 30 minutes

Check:

- Income received.
- Total spending.
- Amount saved/invested.
- Savings rate.
- Emergency fund balance.
- Debt balances.
- Any upcoming large expenses.
- Progress toward monthly target.

Monthly questions:

1. Did I save automatically?
2. Did spending match my values?
3. Did any expense surprise me?
4. Can I increase savings by 1% without making life worse?
5. Is my FI target still based on realistic spending?

---

### Quarterly review: 60 minutes

Check:

- Net worth.
- Savings rate trend.
- Investment allocation.
- Retirement contribution progress.
- Tax-advantaged account usage.
- Emergency fund adequacy.
- Insurance and risk exposure.
- Income growth opportunities.

Quarterly decisions:

- Increase savings rate if sustainable.
- Rebalance if allocation is meaningfully off target.
- Adjust emergency fund if life risk changed.
- Update FI number if spending changed.
- Review whether the 15-year goal is on track.

---

### Annual review: half day

Check:

- Updated tax rules and contribution limits.
- Employer benefits.
- Insurance coverage.
- Estate planning basics.
- Credit reports.
- Long-term spending assumptions.
- FI target range.
- Career and income plan.
- Whether your desired life still matches the financial plan.

Annual planning question:

> “Am I building a life I want now while making work optional later?”

---

## 6. Failure modes and safeguards

### Failure mode 1: The FI number is based on unrealistic spending

**Risk:** You hit a portfolio target that cannot actually support your life.

**Safeguard:**

- Track real spending for at least 3–6 months.
- Include taxes, healthcare, housing repairs, insurance, travel, and irregular expenses.
- Use a conservative FI range rather than one exact number.

---

### Failure mode 2: Savings stay irregular

**Risk:** The 15-year plan depends on consistency; missed months compound over time.

**Safeguard:**

- Automate saving.
- Start with a sustainable amount.
- Increase contributions after raises or debt payoff.
- Use a monthly review to catch drift early.

---

### Failure mode 3: Market returns are worse than expected

**Risk:** A 15-year horizon does not guarantee strong investment returns.

**Safeguard:**

- Use diversified investments.
- Keep an emergency fund to avoid forced selling.
- Run conservative scenarios.
- Consider a lower withdrawal-rate assumption.
- Build flexibility into spending and work plans.

---

### Failure mode 4: Lifestyle inflation absorbs raises

**Risk:** Income grows but FI progress does not improve.

**Safeguard:**

- Pre-commit part of every raise to saving.
- Example: save 50% of raises and enjoy 50%.
- Review recurring expenses quarterly.

---

### Failure mode 5: Tax rules or account limits are assumed incorrectly

**Risk:** Contributions, deductions, Roth eligibility, or withdrawals may not work as expected.

**Safeguard:**

- Verify IRS limits annually.
- Check employer plan documents.
- Consult a qualified tax professional for personalized decisions.

---

### Failure mode 6: Emergency fund is too small

**Risk:** Job loss, medical costs, home repairs, or family needs force debt or investment sales.

**Safeguard:**

- Build a cash runway appropriate to your risk.
- Consider 3–6 months of essential expenses as a common starting range, then adjust for job stability, dependents, health, and housing.

---

### Failure mode 7: The plan is too restrictive

**Risk:** Extreme frugality causes burnout and abandonment.

**Safeguard:**

- Cut low-value spending, not all joy.
- Budget for guilt-free spending.
- Optimize large recurring costs before obsessing over small pleasures.
- Measure quality of life along with net worth.

---

### Failure mode 8: You reach the number but not true optionality

**Risk:** Work remains necessary because healthcare, taxes, housing, or family obligations were underestimated.

**Safeguard:**

- Before declaring FI, stress-test:
  - Higher inflation.
  - Lower returns.
  - Higher healthcare costs.
  - Housing changes.
  - Family support needs.
  - Market decline early in retirement.
- Consider part-time work, consulting, or phased retirement as flexibility tools rather than all-or-nothing choices.
```

## Final output

```markdown
## 1. Goal profile

**Goal:** Reach financial independence in 15 years so work becomes optional, not necessarily to retire early.

**Planning stance:** Educational decision support, not financial, tax, legal, accounting, or investment advice. Public assumptions and rules must be verified before acting.

**Explicit assumptions used for this plan:**

- Country/context: United States.
- Horizon: 15 years.
- You have steady income.
- You currently save irregularly.
- You want a simple plan reviewed monthly.
- You want to avoid extreme frugality.
- You do not want to upload private account data.
- Public references are planning context only, not guaranteed current rules.
- Financial independence means your invested assets can plausibly support your required lifestyle spending, with work becoming optional.

**Finish line / measurable target:**

Your working FI target is:

> **FI number = 25–33 × annual work-optional spending**

That corresponds roughly to a **3%–4% initial withdrawal-rate planning range**, which is a common FI planning shorthand but **not a guarantee**. A lower withdrawal rate is more conservative; a higher rate requires more flexibility and carries more risk.

Example formula only:

- If annual work-optional spending is `$60,000`, then:
  - 25× target = `$1,500,000`
  - 33× target = about `$1,980,000`

**15-year target date:** 15 years from the month you start this plan.

**Review trigger:** Revise the plan if any of these change materially:

- Income changes by 10%+.
- Annual spending changes by 10%+.
- You change jobs, housing, family plans, location, or health insurance needs.
- Your savings rate is off target for 3 consecutive months.
- Market declines or life events would force you to sell investments early.
- Tax rules, retirement account limits, or employer benefits change.

---

## 2. Assumptions to verify

Before acting, verify these because public rules, limits, tax treatment, and benefits can change:

1. **Current retirement account contribution limits**
   - Verify current 401(k), 403(b), 457, IRA, Roth IRA, HSA, and catch-up contribution limits if relevant.
   - Source to check: IRS retirement plan and IRA contribution limit pages.

2. **Employer benefits**
   - Employer retirement match.
   - Vesting schedule.
   - HSA eligibility.
   - Employee stock purchase plan, pension, deferred compensation, or other benefits.

3. **Tax treatment**
   - Traditional vs. Roth contribution eligibility and tradeoffs.
   - State income tax treatment.
   - Taxability of brokerage investment gains.
   - Early-withdrawal rules for retirement accounts.

4. **Emergency fund need**
   - Public budgeting guidance often suggests building cash resilience before taking investment risk, but the right amount depends on job stability, dependents, insurance, debt, and fixed expenses.

5. **Inflation and spending assumptions**
   - Your FI number depends more on future spending than today’s income.
   - Housing, healthcare, childcare, eldercare, insurance, and taxes may materially change your target.

6. **Safe-withdrawal assumptions**
   - A 3%–4% withdrawal-rate range is a planning assumption, not a promise.
   - Sequence-of-returns risk, inflation, taxes, fees, and spending flexibility matter.

7. **Debt costs**
   - High-interest debt may need priority over investing.
   - Low-interest fixed debt may be handled differently depending on risk tolerance and cash flow.

8. **Investment assumptions**
   - Expected returns are uncertain.
   - Diversification may reduce concentration risk but does not eliminate losses.
   - Any long-term return estimate should be treated as a scenario, not a forecast.

---

## 3. Milestone ladder

### First week: define the baseline without uploading private data

**Milestone:** Create a one-page FI dashboard using only numbers you enter manually.

Track:

- Monthly take-home income.
- Monthly essential spending.
- Monthly lifestyle/discretionary spending.
- Monthly debt payments.
- Current cash savings.
- Current invested assets.
- Current retirement contributions.
- Employer match status.
- Estimated annual work-optional spending.
- Current savings rate.

**Key output by end of week:**

> “My current annual work-optional spending estimate is `$X`, so my FI target range is approximately `25X–33X`.”

If you do not know exact spending, start with a rough estimate and refine it over 2–3 months.

---

### First month: stabilize the system

**Milestone:** Convert irregular saving into automatic saving.

Targets to establish:

- A default monthly savings amount.
- A minimum emergency fund target.
- A retirement contribution plan.
- A simple investment-policy draft.
- A monthly review date.

Suggested monthly savings-rate ladder:

- **Starter:** 10% of gross income.
- **Strong:** 20%–30%.
- **Aggressive but not extreme:** 35%+ if it does not damage quality of life or resilience.

For a 15-year FI horizon, the required savings rate may need to be high, especially if starting assets are low. If your current savings rate is far below the needed level, the plan should focus first on gradually increasing it rather than forcing an unrealistic target immediately.

---

### Quarterly: improve the engine

Every quarter, review:

- Savings rate.
- Spending trend.
- Net worth trend.
- Debt balances.
- Emergency fund progress.
- Retirement contribution progress.
- Asset allocation drift.
- Income growth opportunities.
- Lifestyle satisfaction.

Quarterly milestone examples:

- Quarter 1: Know your true monthly spending.
- Quarter 2: Capture full employer match if available.
- Quarter 3: Build or confirm emergency fund target.
- Quarter 4: Increase savings rate by 1–3 percentage points if sustainable.
- Year 2 onward: Review whether FI target, income, and spending assumptions still align.

---

### Horizon-level: 15-year work-optional checkpoint

At year 15, the plan is successful if:

- Invested assets are near or above your selected FI target range.
- Essential expenses can be covered with a conservative withdrawal plan.
- You have a cash buffer or flexible spending plan.
- Healthcare, housing, taxes, and major family obligations are accounted for.
- Work is optional because your finances support choices, not because a spreadsheet says so.

A realistic horizon outcome may be one of three states:

1. **Fully work-optional:** Assets support desired spending with reasonable margin.
2. **Partially work-optional:** You can reduce hours, change careers, consult, freelance, or take sabbaticals.
3. **Not yet FI, but much stronger:** You have high savings discipline, lower financial stress, and more flexibility.

---

## 4. First-month actions

### Action 1: Define your “work-optional spending” number

**Order:** First.

**Why it comes first:** FI is based on spending, not income. Without a spending target, the FI number is undefined.

Do this manually:

- Estimate your current annual spending.
- Remove costs that may disappear after work becomes optional, such as commuting or some work expenses.
- Add costs that may rise, such as healthcare, travel, hobbies, taxes, or insurance.
- Choose a first-draft annual work-optional spending number.

Then calculate:

> **FI target range = annual work-optional spending × 25 to 33**

Use this as a starting range, not a guaranteed endpoint.

---

### Action 2: Build a simple monthly cash-flow map

**Order:** Second.

**Why it comes first:** Irregular saving is usually a cash-flow design problem, not a motivation problem.

Create four categories:

1. Income.
2. Essential spending.
3. Flexible spending.
4. Saving/investing/debt payoff.

You do not need to upload data. Use a spreadsheet, notebook, or budgeting app with manual entry.

Your goal is to identify:

- Minimum monthly expenses.
- Average monthly expenses.
- Monthly surplus.
- Expenses that do not improve your life enough to justify delaying FI.

Avoid extreme frugality. Look for “low-regret” savings first:

- Unused subscriptions.
- Insurance comparison shopping.
- Bank fees.
- High-cost convenience spending.
- Lifestyle creep after raises.
- Large recurring expenses that do not match your priorities.

---

### Action 3: Set up automatic saving

**Order:** Third.

**Why it comes first:** Automation turns FI from a willpower goal into a default system.

Options to consider:

- Automatic transfer to emergency savings.
- Payroll contribution to retirement plan.
- Automatic IRA contribution if eligible.
- Automatic brokerage investment after emergency fund and high-interest debt are addressed.

A simple rule:

> Save automatically right after income arrives, then spend what remains.

Start with an amount you can sustain. If unsure, begin with a small automatic transfer and increase it monthly or quarterly.

---

### Action 4: Capture obvious tax-advantaged opportunities after verifying rules

**Order:** Fourth.

**Why it comes first:** Tax-advantaged accounts and employer matches can materially affect long-term compounding.

Check, without assuming rules are current:

- Employer match availability.
- 401(k)/403(b)/457 contribution limits.
- Traditional vs. Roth eligibility.
- IRA eligibility.
- HSA eligibility if you have a qualifying high-deductible health plan.
- Vesting schedules.
- Fees and investment options.

Possible priority sequence, subject to your situation:

1. Build a starter emergency fund.
2. Contribute enough to get full employer match if available.
3. Address high-interest debt.
4. Increase tax-advantaged contributions.
5. Use taxable brokerage investing for additional FI flexibility.

This is a framework, not a command. Tax and account-order decisions can depend heavily on income, state, age, employer plan, and future tax assumptions.

---

### Action 5: Write a one-page investment policy

**Order:** Fifth.

**Why it comes first:** A simple policy reduces emotional decisions during market declines.

Include:

- Target asset allocation.
- Account types used.
- Contribution schedule.
- Rebalancing rule.
- What you will do during market declines.
- What would cause you to change the plan.

Example structure:

> “I will invest for a 15-year-plus horizon using diversified, low-cost funds. I will contribute monthly, review quarterly, and avoid changing the plan based only on short-term market news.”

Investment risk to acknowledge:

- Stocks can fall sharply and stay down for years.
- Bonds can lose value when rates change.
- Inflation can reduce purchasing power.
- Concentrated positions can create large losses.
- A 15-year horizon is meaningful but not risk-free.

---

## 5. Review cadence

### Monthly review: 30 minutes

Check:

- Income received.
- Total spending.
- Amount saved/invested.
- Savings rate.
- Emergency fund balance.
- Debt balances.
- Any upcoming large expenses.
- Progress toward monthly target.

Monthly questions:

1. Did I save automatically?
2. Did spending match my values?
3. Did any expense surprise me?
4. Can I increase savings by 1% without making life worse?
5. Is my FI target still based on realistic spending?

---

### Quarterly review: 60 minutes

Check:

- Net worth.
- Savings rate trend.
- Investment allocation.
- Retirement contribution progress.
- Tax-advantaged account usage.
- Emergency fund adequacy.
- Insurance and risk exposure.
- Income growth opportunities.

Quarterly decisions:

- Increase savings rate if sustainable.
- Rebalance if allocation is meaningfully off target.
- Adjust emergency fund if life risk changed.
- Update FI number if spending changed.
- Review whether the 15-year goal is on track.

---

### Annual review: half day

Check:

- Updated tax rules and contribution limits.
- Employer benefits.
- Insurance coverage.
- Estate planning basics.
- Credit reports.
- Long-term spending assumptions.
- FI target range.
- Career and income plan.
- Whether your desired life still matches the financial plan.

Annual planning question:

> “Am I building a life I want now while making work optional later?”

---

## 6. Failure modes and safeguards

### Failure mode 1: The FI number is based on unrealistic spending

**Risk:** You hit a portfolio target that cannot actually support your life.

**Safeguard:**

- Track real spending for at least 3–6 months.
- Include taxes, healthcare, housing repairs, insurance, travel, and irregular expenses.
- Use a conservative FI range rather than one exact number.

---

### Failure mode 2: Savings stay irregular

**Risk:** The 15-year plan depends on consistency; missed months compound over time.

**Safeguard:**

- Automate saving.
- Start with a sustainable amount.
- Increase contributions after raises or debt payoff.
- Use a monthly review to catch drift early.

---

### Failure mode 3: Market returns are worse than expected

**Risk:** A 15-year horizon does not guarantee strong investment returns.

**Safeguard:**

- Use diversified investments.
- Keep an emergency fund to avoid forced selling.
- Run conservative scenarios.
- Consider a lower withdrawal-rate assumption.
- Build flexibility into spending and work plans.

---

### Failure mode 4: Lifestyle inflation absorbs raises

**Risk:** Income grows but FI progress does not improve.

**Safeguard:**

- Pre-commit part of every raise to saving.
- Example: save 50% of raises and enjoy 50%.
- Review recurring expenses quarterly.

---

### Failure mode 5: Tax rules or account limits are assumed incorrectly

**Risk:** Contributions, deductions, Roth eligibility, or withdrawals may not work as expected.

**Safeguard:**

- Verify IRS limits annually.
- Check employer plan documents.
- Consult a qualified tax professional for personalized decisions.

---

### Failure mode 6: Emergency fund is too small

**Risk:** Job loss, medical costs, home repairs, or family needs force debt or investment sales.

**Safeguard:**

- Build a cash runway appropriate to your risk.
- Consider 3–6 months of essential expenses as a common starting range, then adjust for job stability, dependents, health, and housing.

---

### Failure mode 7: The plan is too restrictive

**Risk:** Extreme frugality causes burnout and abandonment.

**Safeguard:**

- Cut low-value spending, not all joy.
- Budget for guilt-free spending.
- Optimize large recurring costs before obsessing over small pleasures.
- Measure quality of life along with net worth.

---

### Failure mode 8: You reach the number but not true optionality

**Risk:** Work remains necessary because healthcare, taxes, housing, or family obligations were underestimated.

**Safeguard:**

- Before declaring FI, stress-test:
  - Higher inflation.
  - Lower returns.
  - Higher healthcare costs.
  - Housing changes.
  - Family support needs.
  - Market decline early in retirement.
- Consider part-time work, consulting, or phased retirement as flexibility tools rather than all-or-nothing choices.
```
