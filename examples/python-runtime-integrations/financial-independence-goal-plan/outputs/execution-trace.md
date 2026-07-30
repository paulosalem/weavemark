# WeaveMark Execution Trace

| Field | Value |
| --- | --- |
| Spec | `promplets/catalog/executable/financial-independence-goal-plan.weavemark.md` |
| Model | `gpt-5.6-terra` |
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
    "model": "gpt-5.6-terra",
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
    "model": "gpt-5.6-terra",
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

**Goal:** Build enough financial resilience and invested assets over the next **15 years (by July 2041)** that continuing to work is a choice rather than a necessity—without extreme frugality.

**Measurable target:**
Create a personal “work-optional number”:

\[
\text{Target portfolio} = \frac{\text{annual spending you want investments to cover}}{\text{planning withdrawal rate}}
\]

For planning only, a **3%–4% initial withdrawal-rate range** is commonly discussed; it is not a guarantee of portfolio longevity, returns, or future spending power. A more flexible work-optional life—where part-time, consulting, or occasional income remains possible—may require less than a fully no-work target.

**Example only:** If future baseline spending is $60,000/year:
- At 4%: $60,000 ÷ 0.04 = **$1.50 million**
- At 3%: $60,000 ÷ 0.03 = **$2.00 million**

Use your own spending estimate rather than this example.

**Success by July 2041 means:**
1. You have a documented annual “comfortable minimum” spending level.
2. Your invested assets, reliable nonportfolio income, and accessible cash runway support that spending under conservative assumptions.
3. You have a practical plan for health insurance, taxes, housing, and work-income changes.
4. You review progress monthly and reset the plan when material assumptions change.

**Current-state map**

| Category | Known | Unknown / to establish |
|---|---|---|
| Income | You have steady income | Net monthly income, income stability, employer benefits |
| Saving | You save irregularly | Current saving rate and automatic contribution amount |
| Spending | You do not want extreme frugality | Essential, flexible, and discretionary monthly spending |
| Assets | Not provided | Cash, retirement accounts, taxable investments, debt |
| Time horizon | 15 years | Desired age/work pattern at the end of the horizon |
| Constraints | Privacy-first; simple monthly review | Health, family, housing, insurance, and tax constraints |

This is educational planning support, not individualized investment, tax, legal, or brokerage advice.

## 2. Assumptions to verify

The supplied public-reference pack is useful context but does **not** confirm current-year limits, your eligibility, your tax treatment, or your employer-plan rules. Verify the following before taking account-specific actions:

1. **Retirement-account contribution limits and eligibility**
   - Confirm current IRS limits for workplace plans and IRAs, including catch-up rules if applicable.
   - Confirm whether your employer offers a match, vesting schedule, and plan-specific investment choices.
   - Confirm income limits and eligibility rules for deductible traditional IRA or Roth IRA contributions.
   - References: [IRS retirement-plan contributions](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions) and [IRS traditional and Roth IRAs](https://www.irs.gov/retirement-plans/traditional-and-roth-iras).

2. **Your spending floor**
   - Estimate monthly spending in three buckets:
     **essential** (housing, food, insurance, minimum debt payments),
     **important/flexible** (transport, subscriptions, travel), and
     **optional** (discretionary upgrades).
   - Do not assume today’s spending is your future work-optional spending. Housing, health insurance, dependents, taxes, and location may change it.

3. **Emergency-fund target**
   - A reasonable planning range is often several months of essential expenses, adjusted upward for variable income, dependents, single-income households, health needs, or job risk.
   - Keep this money accessible and avoid treating volatile investments as emergency cash.
   - CFPB budgeting resources: [consumerfinance.gov/budgeting](https://www.consumerfinance.gov/consumer-tools/budgeting/).

4. **Investment-return and inflation assumptions**
   - Do not plan around a single optimistic return forecast. Use a range of nominal and inflation-adjusted outcomes.
   - Investor.gov’s calculator can illustrate compounding from your chosen inputs, but calculator output is not a forecast: [Compound Interest Calculator](https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator).

5. **Withdrawal-rate and flexibility assumptions**
   - A 3%–4% range is a planning lens, not a safe promise. Actual sustainability depends on market returns, inflation, taxes, fees, spending flexibility, sequence-of-returns risk, and the length of time you need the portfolio to last.
   - If work remains optional rather than ending permanently, model scenarios with some earned income rather than relying only on portfolio withdrawals.
   - Background reading: [Bogleheads safe withdrawal rates](https://www.bogleheads.org/wiki/Safe_withdrawal_rates).

6. **Tax, insurance, and legal context**
   - Verify federal and state tax treatment, account withdrawal rules, health-insurance options, disability coverage, estate documents, and any debt obligations.
   - A fiduciary financial planner, CPA, or tax professional may be useful if these decisions are complex.

## 3. Milestone ladder

### First week: establish the baseline

**Milestone:** One-page private summary created without uploading account statements or sharing sensitive data.

Record only rounded totals if preferred:
- Monthly take-home income
- Average monthly essential spending
- Average monthly total spending
- Minimum debt payments and interest rates
- Cash reserves
- Approximate retirement and taxable-investment balances
- Current employer match, if any
- Current automatic savings amount

**Output:**
A preliminary savings rate:

\[
\text{Savings rate} =
\frac{\text{monthly saving and investing}}{\text{monthly take-home income}}
\]

The initial number is a baseline, not a judgment.

### First month: make saving regular

**Milestone:** Convert irregular saving into one automatic, repeatable system.

Targets:
- Set a recurring payday transfer to emergency savings and/or investments.
- Capture any employer match for which you are eligible, subject to confirming plan terms.
- Build a spending-floor estimate.
- Choose a modest initial automatic savings amount that does not require extreme cutbacks.

**Output:** A written monthly cash-flow plan and a scheduled transfer.

### First quarter: build resilience and an investment policy

**Milestone:** Establish a cash runway and simple investing rules.

Targets:
- Progress toward your personally chosen emergency-fund range.
- Review high-interest debt; if present, compare repayment with investing while considering guaranteed interest cost, liquidity, and employer-match opportunities.
- Write a one-page investment policy stating:
  - Purpose: work-optional financial independence by July 2041
  - Time horizon: 15 years
  - Target contribution amount and intended annual increases
  - Diversification approach
  - Rebalancing rule
  - Conditions under which you will not make reactive changes after market declines

**Output:** A plan that remains usable during a stressful month or market downturn.

### Years 1–3: stabilize the system

**Milestone:** Savings occurs automatically, emergency reserves are appropriate for your circumstances, and annual contributions rise with income.

Possible measures:
- Maintain a consistent monthly savings rate.
- Direct a defined share of raises, bonuses, or windfalls to long-term goals while preserving room for present-life priorities.
- Keep lifestyle expansion intentional rather than automatic.
- Reassess insurance, debt, and job resilience annually.

### Years 4–10: accelerate optionality

**Milestone:** Increase the gap between essential spending and dependable resources.

Possible measures:
- Increase automatic contributions as income grows.
- Maintain diversified investments aligned with the written policy and risk capacity.
- Develop income resilience: transferable skills, professional network, certifications, side work only if desired, or an updated résumé.
- Test a lower-cost or reduced-work lifestyle with short, planned experiments rather than abruptly quitting.

### Years 11–15: validate the work-optional plan

**Milestone:** By July 2041, maintain a current work-optional projection using several scenarios.

Review:
- Current annual essential and desired spending
- Invested assets by account type
- Accessible cash runway
- Pension, Social Security, rental, or other potential income—if applicable and verified
- Health-insurance and tax estimates
- A conservative, base, and adverse market/spending scenario
- Whether part-time income would materially improve resilience

**Decision trigger:** Consider reducing work only after the plan works under a conservative scenario, not merely after a favorable market period.

## 4. First-month actions

1. **Create a 30-minute spending snapshot — first**
   - Review the last one to three months yourself; no account upload is needed.
   - Write rounded monthly totals for essential, flexible, and discretionary spending.
   - **Why first:** Your expense floor determines emergency-cash needs, savings capacity, and the eventual work-optional number.

2. **Set a starter automatic transfer — second**
   - Schedule it for shortly after payday, beginning with an amount you can sustain for six months.
   - If you have an employer match, verify the plan rules and consider contributing enough to receive the available match before evaluating other account options.
   - Split the transfer between emergency savings and long-term investing if your cash reserves are thin.
   - **Why second:** Consistency matters more than finding a perfect amount at the beginning.

3. **Choose and label two savings buckets — third**
   - **Near-term resilience:** emergency fund in an appropriate accessible cash vehicle.
   - **Long-term work optionality:** retirement and/or taxable investing accounts selected after verifying current IRS rules, employer benefits, fees, and your tax situation.
   - **Why third:** Mixing emergency money with long-term market investments can force sales at unfavorable times.

4. **Write a one-page “minimum viable” investment policy — fourth**
   - State your 15-year horizon, purpose, contribution schedule, broad diversification preference, and rule against changing course based solely on recent market headlines.
   - Keep the policy simple enough to reread monthly.
   - **Why fourth:** It creates a behavior guardrail before volatility tests your resolve.

5. **Put a 20-minute monthly review on your calendar — fifth**
   - Use the same date each month.
   - Track spending, automatic contributions, emergency-fund months, debt changes, and whether your plan still fits your life.
   - **Why fifth:** A review process makes correction routine instead of emotionally driven.

## 5. Review cadence

### Monthly: 20 minutes

Check:
- Net income received
- Essential and total spending versus your estimate
- Automatic savings/investing completed
- Emergency-fund balance expressed as months of essential expenses
- High-interest debt balance, if applicable
- One friction point to fix next month

Avoid:
- Changing long-term investments because of a single month’s market performance.
- Treating a market increase as permission for permanent spending increases.
- Treating a market decline as proof that the long-term plan failed.

### Quarterly: 45–60 minutes

Check:
- Savings rate over the prior three months
- Whether automatic contributions should rise modestly
- Progress toward emergency-fund target
- Debt payoff progress and interest rates
- Employer match and benefit changes
- Whether your spending floor has changed
- Whether your investment allocation still matches your written policy

### Annually: 1–2 hours

Update:
- Work-optional spending target
- Portfolio target range using at least two withdrawal assumptions, such as 3% and 4%
- Tax-advantaged account limits and eligibility using current IRS sources
- Insurance, beneficiaries, and estate-plan needs where relevant
- Career, location, family, housing, and health-care assumptions
- Contributions after raises or changes in income

### Revise the strategy promptly if any of these occur

- Job loss, reduced income, or a major change in job stability
- New dependent, separation, caregiving duty, or health issue
- Housing change or major recurring expense increase
- Material high-interest debt
- Emergency fund is used
- A sustained reduction in income or major change in tax/benefit rules
- Your desired work-optional lifestyle becomes materially more or less expensive

## 6. Failure modes and safeguards

| Failure mode | Why it matters | Safeguard |
|---|---|---|
| Irregular saving continues | Long-term projections become unreliable if contributions depend on motivation each month. | Use automated payday transfers and begin with a sustainable amount. |
| Overestimating future returns | A favorable assumed return can make a 15-year plan look safer than it is. | Model conservative, base, and adverse scenarios; do not rely on one forecast. |
| Underestimating spending | Missing health care, housing repairs, taxes, travel, or family costs understates the work-optional number. | Separate essential from discretionary expenses and revisit the estimate annually. |
| Investing emergency money | A market decline can coincide with job loss or an unexpected expense. | Keep a defined emergency reserve separate and accessible. |
| Ignoring employer match or account rules | You could miss benefits or make ineligible contributions. | Verify current plan documents and IRS guidance before acting. |
| Extreme cuts cause burnout | A plan that removes all enjoyment may not last 15 years. | Prioritize large, recurring costs and automate moderate progress; preserve intentional spending. |
| Lifestyle inflation absorbs raises | More income may not translate into more optionality. | Pre-commit part of raises and bonuses to savings or debt reduction. |
| Concentrated investments or frequent trading | Concentration and reactive decisions can amplify loss risk. | Use a written diversification and rebalancing policy appropriate to your circumstances. |
| Treating a withdrawal rate as guaranteed | Actual market paths, inflation, taxes, and longevity can differ sharply from assumptions. | Treat the target as a range, maintain flexibility, and revisit it before reducing work. |
| Ignoring health insurance and taxes | These can be major work-optional expenses in the United States. | Include them explicitly in annual spending estimates; obtain professional help if needed. |
| Over-sharing financial information | Privacy risk is unnecessary for this planning stage. | Keep personal records local; use rounded totals in your own worksheet and avoid uploading statements or account credentials. |
```

## Final output

```markdown
## 1. Goal profile

**Goal:** Build enough financial resilience and invested assets over the next **15 years (by July 2041)** that continuing to work is a choice rather than a necessity—without extreme frugality.

**Measurable target:**
Create a personal “work-optional number”:

\[
\text{Target portfolio} = \frac{\text{annual spending you want investments to cover}}{\text{planning withdrawal rate}}
\]

For planning only, a **3%–4% initial withdrawal-rate range** is commonly discussed; it is not a guarantee of portfolio longevity, returns, or future spending power. A more flexible work-optional life—where part-time, consulting, or occasional income remains possible—may require less than a fully no-work target.

**Example only:** If future baseline spending is $60,000/year:
- At 4%: $60,000 ÷ 0.04 = **$1.50 million**
- At 3%: $60,000 ÷ 0.03 = **$2.00 million**

Use your own spending estimate rather than this example.

**Success by July 2041 means:**
1. You have a documented annual “comfortable minimum” spending level.
2. Your invested assets, reliable nonportfolio income, and accessible cash runway support that spending under conservative assumptions.
3. You have a practical plan for health insurance, taxes, housing, and work-income changes.
4. You review progress monthly and reset the plan when material assumptions change.

**Current-state map**

| Category | Known | Unknown / to establish |
|---|---|---|
| Income | You have steady income | Net monthly income, income stability, employer benefits |
| Saving | You save irregularly | Current saving rate and automatic contribution amount |
| Spending | You do not want extreme frugality | Essential, flexible, and discretionary monthly spending |
| Assets | Not provided | Cash, retirement accounts, taxable investments, debt |
| Time horizon | 15 years | Desired age/work pattern at the end of the horizon |
| Constraints | Privacy-first; simple monthly review | Health, family, housing, insurance, and tax constraints |

This is educational planning support, not individualized investment, tax, legal, or brokerage advice.

## 2. Assumptions to verify

The supplied public-reference pack is useful context but does **not** confirm current-year limits, your eligibility, your tax treatment, or your employer-plan rules. Verify the following before taking account-specific actions:

1. **Retirement-account contribution limits and eligibility**
   - Confirm current IRS limits for workplace plans and IRAs, including catch-up rules if applicable.
   - Confirm whether your employer offers a match, vesting schedule, and plan-specific investment choices.
   - Confirm income limits and eligibility rules for deductible traditional IRA or Roth IRA contributions.
   - References: [IRS retirement-plan contributions](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions) and [IRS traditional and Roth IRAs](https://www.irs.gov/retirement-plans/traditional-and-roth-iras).

2. **Your spending floor**
   - Estimate monthly spending in three buckets:
     **essential** (housing, food, insurance, minimum debt payments),
     **important/flexible** (transport, subscriptions, travel), and
     **optional** (discretionary upgrades).
   - Do not assume today’s spending is your future work-optional spending. Housing, health insurance, dependents, taxes, and location may change it.

3. **Emergency-fund target**
   - A reasonable planning range is often several months of essential expenses, adjusted upward for variable income, dependents, single-income households, health needs, or job risk.
   - Keep this money accessible and avoid treating volatile investments as emergency cash.
   - CFPB budgeting resources: [consumerfinance.gov/budgeting](https://www.consumerfinance.gov/consumer-tools/budgeting/).

4. **Investment-return and inflation assumptions**
   - Do not plan around a single optimistic return forecast. Use a range of nominal and inflation-adjusted outcomes.
   - Investor.gov’s calculator can illustrate compounding from your chosen inputs, but calculator output is not a forecast: [Compound Interest Calculator](https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator).

5. **Withdrawal-rate and flexibility assumptions**
   - A 3%–4% range is a planning lens, not a safe promise. Actual sustainability depends on market returns, inflation, taxes, fees, spending flexibility, sequence-of-returns risk, and the length of time you need the portfolio to last.
   - If work remains optional rather than ending permanently, model scenarios with some earned income rather than relying only on portfolio withdrawals.
   - Background reading: [Bogleheads safe withdrawal rates](https://www.bogleheads.org/wiki/Safe_withdrawal_rates).

6. **Tax, insurance, and legal context**
   - Verify federal and state tax treatment, account withdrawal rules, health-insurance options, disability coverage, estate documents, and any debt obligations.
   - A fiduciary financial planner, CPA, or tax professional may be useful if these decisions are complex.

## 3. Milestone ladder

### First week: establish the baseline

**Milestone:** One-page private summary created without uploading account statements or sharing sensitive data.

Record only rounded totals if preferred:
- Monthly take-home income
- Average monthly essential spending
- Average monthly total spending
- Minimum debt payments and interest rates
- Cash reserves
- Approximate retirement and taxable-investment balances
- Current employer match, if any
- Current automatic savings amount

**Output:**
A preliminary savings rate:

\[
\text{Savings rate} =
\frac{\text{monthly saving and investing}}{\text{monthly take-home income}}
\]

The initial number is a baseline, not a judgment.

### First month: make saving regular

**Milestone:** Convert irregular saving into one automatic, repeatable system.

Targets:
- Set a recurring payday transfer to emergency savings and/or investments.
- Capture any employer match for which you are eligible, subject to confirming plan terms.
- Build a spending-floor estimate.
- Choose a modest initial automatic savings amount that does not require extreme cutbacks.

**Output:** A written monthly cash-flow plan and a scheduled transfer.

### First quarter: build resilience and an investment policy

**Milestone:** Establish a cash runway and simple investing rules.

Targets:
- Progress toward your personally chosen emergency-fund range.
- Review high-interest debt; if present, compare repayment with investing while considering guaranteed interest cost, liquidity, and employer-match opportunities.
- Write a one-page investment policy stating:
  - Purpose: work-optional financial independence by July 2041
  - Time horizon: 15 years
  - Target contribution amount and intended annual increases
  - Diversification approach
  - Rebalancing rule
  - Conditions under which you will not make reactive changes after market declines

**Output:** A plan that remains usable during a stressful month or market downturn.

### Years 1–3: stabilize the system

**Milestone:** Savings occurs automatically, emergency reserves are appropriate for your circumstances, and annual contributions rise with income.

Possible measures:
- Maintain a consistent monthly savings rate.
- Direct a defined share of raises, bonuses, or windfalls to long-term goals while preserving room for present-life priorities.
- Keep lifestyle expansion intentional rather than automatic.
- Reassess insurance, debt, and job resilience annually.

### Years 4–10: accelerate optionality

**Milestone:** Increase the gap between essential spending and dependable resources.

Possible measures:
- Increase automatic contributions as income grows.
- Maintain diversified investments aligned with the written policy and risk capacity.
- Develop income resilience: transferable skills, professional network, certifications, side work only if desired, or an updated résumé.
- Test a lower-cost or reduced-work lifestyle with short, planned experiments rather than abruptly quitting.

### Years 11–15: validate the work-optional plan

**Milestone:** By July 2041, maintain a current work-optional projection using several scenarios.

Review:
- Current annual essential and desired spending
- Invested assets by account type
- Accessible cash runway
- Pension, Social Security, rental, or other potential income—if applicable and verified
- Health-insurance and tax estimates
- A conservative, base, and adverse market/spending scenario
- Whether part-time income would materially improve resilience

**Decision trigger:** Consider reducing work only after the plan works under a conservative scenario, not merely after a favorable market period.

## 4. First-month actions

1. **Create a 30-minute spending snapshot — first**
   - Review the last one to three months yourself; no account upload is needed.
   - Write rounded monthly totals for essential, flexible, and discretionary spending.
   - **Why first:** Your expense floor determines emergency-cash needs, savings capacity, and the eventual work-optional number.

2. **Set a starter automatic transfer — second**
   - Schedule it for shortly after payday, beginning with an amount you can sustain for six months.
   - If you have an employer match, verify the plan rules and consider contributing enough to receive the available match before evaluating other account options.
   - Split the transfer between emergency savings and long-term investing if your cash reserves are thin.
   - **Why second:** Consistency matters more than finding a perfect amount at the beginning.

3. **Choose and label two savings buckets — third**
   - **Near-term resilience:** emergency fund in an appropriate accessible cash vehicle.
   - **Long-term work optionality:** retirement and/or taxable investing accounts selected after verifying current IRS rules, employer benefits, fees, and your tax situation.
   - **Why third:** Mixing emergency money with long-term market investments can force sales at unfavorable times.

4. **Write a one-page “minimum viable” investment policy — fourth**
   - State your 15-year horizon, purpose, contribution schedule, broad diversification preference, and rule against changing course based solely on recent market headlines.
   - Keep the policy simple enough to reread monthly.
   - **Why fourth:** It creates a behavior guardrail before volatility tests your resolve.

5. **Put a 20-minute monthly review on your calendar — fifth**
   - Use the same date each month.
   - Track spending, automatic contributions, emergency-fund months, debt changes, and whether your plan still fits your life.
   - **Why fifth:** A review process makes correction routine instead of emotionally driven.

## 5. Review cadence

### Monthly: 20 minutes

Check:
- Net income received
- Essential and total spending versus your estimate
- Automatic savings/investing completed
- Emergency-fund balance expressed as months of essential expenses
- High-interest debt balance, if applicable
- One friction point to fix next month

Avoid:
- Changing long-term investments because of a single month’s market performance.
- Treating a market increase as permission for permanent spending increases.
- Treating a market decline as proof that the long-term plan failed.

### Quarterly: 45–60 minutes

Check:
- Savings rate over the prior three months
- Whether automatic contributions should rise modestly
- Progress toward emergency-fund target
- Debt payoff progress and interest rates
- Employer match and benefit changes
- Whether your spending floor has changed
- Whether your investment allocation still matches your written policy

### Annually: 1–2 hours

Update:
- Work-optional spending target
- Portfolio target range using at least two withdrawal assumptions, such as 3% and 4%
- Tax-advantaged account limits and eligibility using current IRS sources
- Insurance, beneficiaries, and estate-plan needs where relevant
- Career, location, family, housing, and health-care assumptions
- Contributions after raises or changes in income

### Revise the strategy promptly if any of these occur

- Job loss, reduced income, or a major change in job stability
- New dependent, separation, caregiving duty, or health issue
- Housing change or major recurring expense increase
- Material high-interest debt
- Emergency fund is used
- A sustained reduction in income or major change in tax/benefit rules
- Your desired work-optional lifestyle becomes materially more or less expensive

## 6. Failure modes and safeguards

| Failure mode | Why it matters | Safeguard |
|---|---|---|
| Irregular saving continues | Long-term projections become unreliable if contributions depend on motivation each month. | Use automated payday transfers and begin with a sustainable amount. |
| Overestimating future returns | A favorable assumed return can make a 15-year plan look safer than it is. | Model conservative, base, and adverse scenarios; do not rely on one forecast. |
| Underestimating spending | Missing health care, housing repairs, taxes, travel, or family costs understates the work-optional number. | Separate essential from discretionary expenses and revisit the estimate annually. |
| Investing emergency money | A market decline can coincide with job loss or an unexpected expense. | Keep a defined emergency reserve separate and accessible. |
| Ignoring employer match or account rules | You could miss benefits or make ineligible contributions. | Verify current plan documents and IRS guidance before acting. |
| Extreme cuts cause burnout | A plan that removes all enjoyment may not last 15 years. | Prioritize large, recurring costs and automate moderate progress; preserve intentional spending. |
| Lifestyle inflation absorbs raises | More income may not translate into more optionality. | Pre-commit part of raises and bonuses to savings or debt reduction. |
| Concentrated investments or frequent trading | Concentration and reactive decisions can amplify loss risk. | Use a written diversification and rebalancing policy appropriate to your circumstances. |
| Treating a withdrawal rate as guaranteed | Actual market paths, inflation, taxes, and longevity can differ sharply from assumptions. | Treat the target as a range, maintain flexibility, and revisit it before reducing work. |
| Ignoring health insurance and taxes | These can be major work-optional expenses in the United States. | Include them explicitly in annual spending estimates; obtain professional help if needed. |
| Over-sharing financial information | Privacy risk is unnecessary for this planning stage. | Keep personal records local; use rounded totals in your own worksheet and avoid uploading statements or account credentials. |
```
