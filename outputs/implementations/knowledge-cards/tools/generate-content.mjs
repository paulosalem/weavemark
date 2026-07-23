#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { computeContentChecksum, validateAllPacks } from "./validate-packs.mjs";

const ROOT = process.cwd();
const CREATED_AT = "2026-07-21T00:00:00.000Z";
const CONTENT_VERSION = "2026.07.21";
const CONTENT_REVIEW_DATE = "2026-07-21";
const CATEGORY_NOTES = {
  foundations: "Core language and mental models that later cards assume.",
  mechanisms: "How the system works when parts interact.",
  applications: "Practical reading of real situations without individualized advice.",
  misconceptions: "Common wrong maps that make later reasoning brittle.",
  limitations: "Boundaries, uncertainty, tradeoffs, and professional guidance points.",
  bridges: "Connections across adjacent ideas and real-world contexts.",
  "advanced-horizons": "Beginner-safe previews of ideas learners may study later."
};

const packs = [
  {
    id: "banking-industry-and-central-banks",
    short: "bank",
    title: "Banking Industry and Central Banks",
    description: "A beginner-safe systems map of commercial banks, payments, lending, regulation, and central-bank policy. Examples center on the United States banking system and the Federal Reserve; general concepts noted as international draw on BIS, FinCEN, and cross-border sources, and specifics vary by jurisdiction.",
    audience: "Curious adults who want to understand banking news without technical finance training",
    level: "Beginner",
    purpose: "Build a prerequisite-safe map of how banks and central banks move money, credit, and confidence.",
    accent_color: "#3f6f78",
    boundary: "Educational only. Banking policy and consumer-finance actions can depend on jurisdiction, account terms, and current rules, so use primary regulators or qualified professionals for decisions.",
    source_refs: [
      source("bank-fed-monetary-policy", "Monetary Policy", "Board of Governors of the Federal Reserve System", "https://www.federalreserve.gov/monetarypolicy.htm", "Central-bank mandates, policy tools, and transmission."),
      source("bank-fed-payments", "Payment Systems", "Board of Governors of the Federal Reserve System", "https://www.federalreserve.gov/paymentsystems.htm", "Payments, settlement, and financial-market infrastructure."),
      source("bank-fdic-insurance", "Deposit Insurance", "Federal Deposit Insurance Corporation", "https://www.fdic.gov/resources/deposit-insurance/", "US deposit insurance concepts and limits."),
      source("bank-bis-cpmi", "CPMI glossary and payment system resources", "Bank for International Settlements", "https://www.bis.org/cpmi/publ/d00b.htm", "Payment, clearing, and settlement terminology."),
      source("bank-basel", "Basel Committee on Banking Supervision", "Bank for International Settlements", "https://www.bis.org/bcbs/", "Bank capital, supervision, and financial stability concepts."),
      source("bank-fincen-aml", "FinCEN's Legal Authorities", "Financial Crimes Enforcement Network", "https://www.fincen.gov/resources/fincens-legal-authorities", "Anti-money-laundering and Bank Secrecy Act legal authority, a US-specific AML regime used as an illustrative example."),
      source("bank-fdic-resolutions", "Resolutions", "Federal Deposit Insurance Corporation", "https://www.fdic.gov/resolutions", "US bank failure and resolution process."),
      source("bank-bis-correspondent", "Correspondent banking", "Bank for International Settlements", "https://www.bis.org/cpmi/publ/d147.htm", "Cross-border correspondent banking relationships and risks, an internationally scoped topic."),
      source("bank-fed-cbdc", "Money and Payments: The U.S. Dollar in the Age of Digital Transformation", "Board of Governors of the Federal Reserve System", "https://www.federalreserve.gov/publications/money-and-payments-discussion-paper.htm", "Central bank digital currency design tradeoffs."),
      source("bank-cfpb-consumer", "Bank accounts and services", "Consumer Financial Protection Bureau", "https://www.consumerfinance.gov/consumer-tools/bank-accounts/", "US consumer protection in banking products and services.")
    ],
    rows: [
      r("Money, credit, and trust", "foundations", [], "Money is useful because people expect others to accept it later, while credit extends that trust across time.", "Banks sit between present cash and future repayment, so the banking system is partly plumbing and partly a confidence network.", "A paycheck deposit, a card payment, and a mortgage all rely on promises being recorded and settled.", "Banking starts with trusted records of who can pay whom.", 1, 0.96, 1),
      r("Commercial banks", "foundations", [1], "A commercial bank is a private institution that takes deposits, makes loans, provides payment access, and manages risk.", "It earns by transforming funding into assets while meeting rules, withdrawals, and payment obligations.", "A neighborhood bank account is both a service to the customer and a funding source for the bank.", "A bank is not a vault; it is a regulated balance-sheet business.", 1, 0.95, 0.98),
      r("Deposits as bank liabilities", "foundations", [2], "A deposit feels like your asset, but on the bank balance sheet it is money the bank owes you.", "That liability must be honored through withdrawals, transfers, or payments even though the bank has invested or lent much of the funding.", "When you see 500 dollars in checking, the bank records a matching obligation to let you spend it.", "Deposits are promises by the bank, not labeled bundles of cash in a drawer.", 2, 0.94, 0.96),
      r("Payment systems", "mechanisms", [1], "A payment system is the rulebook and infrastructure that moves claims between people, banks, merchants, and central-bank accounts.", "The visible tap or transfer hides authorization, clearing, settlement, fraud controls, and final record updates.", "Buying groceries with a debit card can involve a merchant bank, card network, your bank, and settlement records.", "Payments are coordinated record changes, not just money flying through wires.", 2, 0.9, 0.9),
      r("Bank balance sheets", "foundations", [2, 3], "A bank balance sheet lists assets such as loans and securities against liabilities such as deposits and wholesale funding.", "Capital is the loss-absorbing cushion between asset values and promises owed to others.", "If loans lose value, capital takes the first hit before depositors or other creditors are threatened.", "Reading bank strength begins with assets, liabilities, and capital.", 2, 0.92, 0.95),
      r("Fractional-reserve banking", "mechanisms", [3, 5], "Fractional-reserve banking means banks keep only part of deposit funding as immediately available reserves or cash.", "The system works when withdrawals are ordinary and confidence holds, but it becomes fragile when many depositors demand liquidity at once.", "A bank can safely serve normal ATM withdrawals while still funding long-term loans.", "Banks need enough liquidity for expected demands, not one-for-one cash for every deposit.", 2, 0.88, 0.88),
      r("How lending creates deposits", "mechanisms", [6], "When a bank makes a loan, it usually credits the borrower's deposit account, creating a new bank deposit alongside a loan asset.", "The loan still requires capital, funding, risk controls, and settlement capacity, so creation is constrained rather than magical.", "A business loan may appear as new spendable balance before anyone else has reduced their checking account.", "Bank lending can expand deposits, but it is limited by risk, regulation, capital, and demand.", 3, 0.93, 0.86),
      r("Credit risk", "mechanisms", [7], "Credit risk is the chance that borrowers do not repay as agreed, reducing the value of the bank's loan assets.", "Banks price, diversify, collateralize, and provision for this risk because bad loans can consume capital.", "A mortgage and an unsecured business loan expose the bank to very different repayment uncertainties.", "Every loan is also a prediction about future repayment.", 2, 0.86, 0.72),
      r("Interest rates as prices of time and risk", "foundations", [7], "An interest rate compensates lenders for waiting, expected inflation, uncertainty, and borrower risk.", "Different rates coexist because loans differ in maturity, collateral, liquidity, tax treatment, and default probability.", "A short Treasury bill and a risky credit-card balance do not carry the same rate because they are not the same promise.", "Interest rates are prices attached to time, risk, and money conditions.", 2, 0.91, 0.88),
      r("Net interest margin", "mechanisms", [9], "Net interest margin is the spread between what a bank earns on assets and what it pays for funding.", "It connects customer rates, central-bank policy, deposit competition, loan quality, and profitability.", "If deposit rates rise faster than loan yields, a bank's margin can shrink even while rates are high.", "A bank's profit depends on the spread, not just whether rates are high.", 3, 0.75, 0.55),
      r("Reserves and settlement balances", "mechanisms", [4, 6], "Reserves are balances banks hold at the central bank and use to settle payments with one another.", "They are not the same as capital or customer deposits; they are a special settlement asset inside the banking system.", "When your bank sends money to another bank, reserve balances may move behind the scenes.", "Reserves are the banking system's settlement money.", 2, 0.89, 0.84),
      r("Interbank settlement", "mechanisms", [4, 11], "Interbank settlement is the final adjustment of obligations between banks after customers make payments.", "Settlement reduces a web of promises to authoritative records, often using central-bank money for finality.", "Thousands of customer transfers can net to a smaller movement between two banks at the end of a cycle.", "Payments become durable when banks settle with each other.", 2, 0.86, 0.78),
      r("Clearing houses and payment finality", "mechanisms", [12], "Clearing houses help participants calculate obligations, manage risk, and prepare transactions for settlement.", "Finality matters because businesses need to know when a payment cannot be unwound except through a new transaction.", "A merchant wants confidence that a paid invoice will not vanish after goods are released.", "Clearing organizes obligations; finality makes payment records dependable.", 3, 0.78, 0.52),
      r("Liquidity versus solvency", "misconceptions", [5], "Liquidity is the ability to meet near-term cash demands, while solvency means assets are worth more than liabilities.", "A solvent institution can fail if it cannot get cash in time, and a liquid institution can still be insolvent if losses are hidden.", "A homeowner with valuable property but no cash for today's bill has a liquidity problem, not necessarily a net-worth problem.", "Do not confuse having cash today with being economically sound.", 2, 0.9, 0.82),
      r("Maturity transformation", "mechanisms", [3, 7], "Maturity transformation means funding long-term assets such as loans with shorter-term liabilities such as deposits.", "It supports useful lending but creates rollover and withdrawal risk because promised payment times do not perfectly match.", "A bank may fund a 30-year mortgage partly with deposits customers can move tomorrow.", "Banking creates value by transforming maturities, and fragility by mismatching them.", 3, 0.88, 0.74),
      r("Bank runs", "applications", [14, 15], "A bank run happens when many funders try to withdraw because each fears being late to the exit.", "Even rumors can become self-reinforcing when depositors believe others will withdraw first.", "A solvent bank can be forced to sell assets quickly at losses if everyone demands cash at once.", "Runs are coordination failures around confidence and liquidity.", 2, 0.91, 0.68),
      r("Deposit insurance", "applications", [16], "Deposit insurance protects eligible deposits up to defined limits and reduces the incentive for small depositors to run.", "It supports confidence but also requires supervision and limits because protection can weaken market discipline.", "An insured household checking account is treated differently from an uninsured corporate balance above the limit.", "Deposit insurance calms runs by making many depositors less exposed.", 2, 0.87, 0.62),
      r("Central bank mandates", "foundations", [9], "A central-bank mandate states the public goals it is expected to pursue, such as price stability, employment, financial stability, or payments safety.", "Mandates differ by country and create tradeoffs when goals point in different directions.", "A rate hike may fight inflation while slowing borrowing and hiring.", "Central banks act through legal mandates, not personal preference alone.", 2, 0.9, 0.8),
      r("Monetary policy transmission", "mechanisms", [18], "Monetary policy transmission is the chain from central-bank tools to financial conditions, spending, hiring, and inflation.", "The chain is indirect because households, banks, firms, markets, and expectations all react with delays.", "A policy-rate change may affect mortgage rates, which affects home buying, construction, and eventually prices.", "Central banks steer through channels, not direct remote control.", 3, 0.9, 0.68),
      r("Policy rates and yield curves", "mechanisms", [9, 19], "A policy rate is a short-term anchor, while a yield curve shows interest rates across maturities.", "Longer rates include expectations about future short rates, inflation, risk, and term premiums.", "Mortgage rates may move even before a meeting if markets expect future policy changes.", "The central bank strongly influences short rates, while markets help price the rest of the curve.", 3, 0.84, 0.58),
      r("Open market operations", "mechanisms", [18], "Open market operations are central-bank purchases or sales of securities used to manage reserves and short-term rates.", "They work by changing the supply of settlement balances and the prices of safe assets in financial markets.", "Buying Treasury securities can add reserves to banks and help keep the overnight rate near target.", "Open market operations are practical plumbing for policy implementation.", 3, 0.78, 0.5),
      r("Reserve requirements", "limitations", [6], "Reserve requirements set a minimum share of certain liabilities banks must hold in reserve-eligible form.", "They are one possible constraint on bank balance sheets, but modern systems often rely more on capital, liquidity rules, and interest on reserves.", "A country may change reserve requirements without that being the main driver of everyday loan supply.", "Reserve requirements matter, but they are not the whole story of credit creation.", 3, 0.72, 0.48),
      r("Standing facilities", "mechanisms", [11, 18], "Standing facilities let banks borrow from or deposit with the central bank under defined terms.", "They form guardrails around short-term interest rates and provide backup liquidity when markets are strained.", "A discount window loan can help a bank meet temporary payment needs without dumping assets.", "Standing facilities are safety valves for short-term money markets.", 3, 0.77, 0.48),
      r("Lender of last resort", "applications", [16, 23], "A lender of last resort provides emergency liquidity to solvent institutions facing panic or market breakdown.", "The idea is to stop contagious runs while avoiding bailouts of institutions that are fundamentally insolvent.", "A central bank may lend against good collateral during a panic so payments keep functioning.", "Last-resort lending is about containing panic without erasing discipline.", 3, 0.86, 0.52),
      r("Inflation and money demand", "bridges", [18], "Inflation is a sustained rise in the general price level, and money demand is the public's desire to hold liquid balances.", "The relationship between money and prices depends on output, velocity, expectations, supply shocks, and policy credibility.", "Prices can rise after supply disruptions even if households are not suddenly richer.", "Money matters for inflation, but the channel is broader than simple printing.", 2, 0.88, 0.62),
      r("Deflation and debt burdens", "bridges", [25], "Deflation can raise the real burden of fixed debts because borrowers repay in money that buys more than expected.", "That pressure can reduce spending, increase defaults, and make downturns harder to escape.", "A business with fixed loan payments may struggle if its selling prices fall across the economy.", "Falling prices can be dangerous when debts are fixed in nominal terms.", 3, 0.74, 0.36),
      r("Quantitative easing", "advanced-horizons", [21], "Quantitative easing is large-scale central-bank asset buying used when ordinary short-term-rate tools are constrained.", "It aims to affect longer-term yields, market functioning, portfolios, and expectations, but its effects are debated and context-dependent.", "Buying long-term government bonds can push investors toward other assets and lower borrowing costs.", "QE is an unconventional policy tool, not a simple cash drop to households.", 4, 0.75, 0.32),
      r("Forward guidance", "advanced-horizons", [20], "Forward guidance is communication about likely future policy used to shape expectations today.", "Because financial prices reflect expected future conditions, credible guidance can affect rates before any tool is changed.", "A central bank statement that rates may stay high longer can move bond yields immediately.", "Expectations are a policy channel when people believe the message.", 4, 0.72, 0.3),
      r("Bank capital", "mechanisms", [5], "Bank capital is the owner's loss-absorbing claim that stands between asset losses and many creditors.", "More capital makes a bank more resilient, but it can also affect returns, lending incentives, and funding costs.", "If a loan portfolio loses value, equity absorbs losses before insured depositors are affected.", "Capital is the banking system's shock absorber.", 2, 0.9, 0.76),
      r("Leverage", "mechanisms", [29], "Leverage means using borrowed or promised funds to hold assets larger than the owner's capital.", "It magnifies gains when assets perform and magnifies losses when they do not, so a small drop in asset value can wipe out a leveraged owner's thin capital cushion.", "A bank with 5 dollars of capital supporting 100 dollars of assets has little room for asset losses.", "Leverage makes banking powerful and fragile at the same time.", 2, 0.86, 0.7),
      r("Capital requirements", "applications", [29], "Capital requirements set minimum loss-absorbing resources banks must hold relative to assets or risk-weighted exposures.", "They force resilience into private balance sheets before stress arrives, though measurement choices matter.", "A riskier loan book generally requires more capital than a portfolio of safer government securities.", "Capital rules turn the idea of resilience into a measurable constraint.", 3, 0.82, 0.5),
      r("Stress tests", "applications", [31], "Stress tests ask whether a bank could survive severe but plausible economic scenarios.", "They reveal vulnerabilities that ordinary good times may hide and can require banks to adjust capital plans.", "A regulator might test what happens if unemployment jumps and housing prices fall together.", "Stress tests are rehearsals for financial weather that has not arrived yet.", 3, 0.76, 0.38),
      r("Macroprudential regulation", "advanced-horizons", [31], "Macroprudential regulation focuses on risks to the financial system as a whole rather than one institution at a time.", "It watches shared exposures, feedback loops, procyclical lending, and contagion channels.", "If many lenders loosen mortgage standards together, each may look fine alone while the system becomes fragile.", "System safety requires seeing connections, not just individual bank health.", 4, 0.72, 0.28),
      r("Shadow banking", "advanced-horizons", [15], "Shadow banking describes credit intermediation outside traditional deposit-taking banks.", "It can provide useful funding but may recreate bank-like run risks without the same protections or visibility.", "Money market funds and securitization vehicles can fund credit while sitting outside ordinary bank deposits.", "Bank-like fragility can appear outside institutions called banks.", 4, 0.7, 0.24),
      r("Securitization", "bridges", [7], "Securitization pools financial assets such as loans and turns their cash flows into tradable securities.", "It can spread risk and funding sources, but complexity can hide who ultimately bears losses.", "A bundle of mortgages can be converted into bonds bought by investors around the world.", "Securitization changes loans from local relationships into market instruments.", 4, 0.68, 0.24),
      r("Central bank independence", "limitations", [18], "Central bank independence means policy decisions are insulated from short-term political pressure within a legal mandate.", "Independence can support credibility, but it must be balanced by accountability, transparency, and democratic legitimacy.", "A central bank may resist pressure to keep rates low before an election if inflation risks are high.", "Independence is a governance design for credibility, not freedom from accountability.", 3, 0.76, 0.34),
      r("Exchange rates and central banks", "bridges", [19], "Exchange rates connect domestic policy to global capital flows, trade prices, and imported inflation.", "Central banks may influence currencies through rates, interventions, or communication, but market forces and foreign policy also matter.", "Higher domestic rates can attract capital and strengthen a currency, all else equal.", "A central bank operates in a world of cross-border money.", 3, 0.7, 0.26),
      r("Correspondent banking", "applications", [12], "Correspondent banking lets one bank provide services for another, often across borders or currencies.", "It expands payment reach but introduces compliance, settlement, and concentration risks.", "A small bank may use a larger international bank to process foreign-currency payments.", "Global payments often rely on bank relationships behind the customer interface.", 3, 0.64, 0.2),
      r("Money laundering controls", "applications", [2], "Money laundering controls aim to prevent financial services from hiding criminal proceeds or sanctioned activity.", "Banks must know customers, monitor suspicious patterns, and report certain activity while avoiding unfair exclusion.", "A bank may ask for business ownership documents before opening an account.", "Compliance is part of banking infrastructure, not just paperwork.", 3, 0.7, 0.24),
      r("Consumer protection", "applications", [3], "Consumer protection rules address disclosure, fairness, error resolution, and abusive practices in financial services.", "They matter because banking products are complex and mistakes can harm household stability.", "A clear fee disclosure helps a customer compare accounts before overdrafts become costly.", "Trust in banking depends on fair treatment as well as financial soundness.", 2, 0.76, 0.34),
      r("Misconception: banks only lend pre-existing deposits", "misconceptions", [6, 7], "The simple story that banks lend only money someone already deposited misses how bank lending can create deposits.", "The better map still includes constraints: capital, risk, demand, regulation, funding, and settlement all limit lending.", "A new business loan can create a deposit balance, but the bank must still manage the resulting risk and payments.", "Credit creation is constrained balance-sheet expansion, not a pile of old cash being passed along.", 3, 0.82, 0.32),
      r("Misconception: central banks directly set every interest rate", "misconceptions", [20], "Central banks directly target or administer some short-term rates, but many market rates are priced by expectations and risk.", "Policy influence travels through curves, spreads, banks, and markets rather than commanding every loan price.", "A credit-card rate can stay high even after a policy cut because default risk and pricing practices differ.", "Central-bank influence is strong but not mechanical control of every rate.", 3, 0.78, 0.28),
      r("Misconception: printing money automatically causes inflation", "misconceptions", [25], "More money can contribute to inflation, but the result depends on output, demand, velocity, expectations, and supply conditions.", "A richer model asks whether new money changes spending pressure relative to the economy's ability to produce.", "Emergency liquidity in a frozen market may not affect prices the same way as sustained deficit monetization during overheating.", "Money growth matters through context, not through an automatic one-step rule.", 3, 0.8, 0.3),
      r("Financial stability versus price stability", "limitations", [18], "Price stability focuses on inflation, while financial stability focuses on resilient institutions and markets.", "The goals often support each other but can conflict when inflation is high and markets are fragile.", "Raising rates may cool prices while also exposing leveraged borrowers or banks with interest-rate losses.", "Central-bank tradeoffs are real when different forms of stability pull apart.", 4, 0.82, 0.24),
      r("Central bank digital currencies", "advanced-horizons", [4], "A central bank digital currency would be a public digital money design, not simply a private payment app.", "Design choices about privacy, bank funding, offline use, and financial inclusion determine its effects.", "A retail CBDC could let households hold a digital claim on the central bank, depending on national design.", "CBDCs are policy designs with tradeoffs, not just new payment technology.", 4, 0.62, 0.12),
      r("Real-time payments", "applications", [4], "Real-time payments move funds and confirmations near instantly, changing expectations for speed and availability.", "They require fraud controls, liquidity management, and clear finality rules because mistakes can also move faster.", "An instant bill payment helps a household avoid a late fee, but a scam transfer may be harder to reverse.", "Faster payments increase convenience and the need for stronger safeguards.", 3, 0.68, 0.22),
      r("Bank profitability cycles", "bridges", [10], "Bank profitability changes with interest-rate cycles, credit losses, competition, and regulation.", "A good lending year can hide future losses because defaults often arrive after economic conditions turn.", "Profits may look strong when loan growth is rapid, then weaken when borrowers struggle.", "Bank earnings are cyclical because credit quality and funding costs move with the economy.", 3, 0.66, 0.18),
      r("Crisis resolution", "applications", [16, 29], "Crisis resolution is the process for handling a failing financial institution while limiting wider damage.", "Tools can include sale, bridge bank, bail-in, liquidation, guarantees, or emergency liquidity depending on law and facts.", "A regulator may transfer insured deposits to another bank over a weekend to preserve access.", "Resolution tries to protect critical functions without pretending losses disappeared.", 4, 0.72, 0.18),
      r("Moral hazard", "limitations", [17, 24], "Moral hazard appears when protection changes behavior by reducing the cost of taking risk.", "Deposit insurance and emergency lending can stabilize the system, but safeguards are needed so risk-takers do not expect rescue.", "If managers believe creditors will always be protected, they may accept more leverage than society wants.", "Safety nets need rules because protection can change incentives.", 3, 0.76, 0.2),
      r("Reading bank news with a systems map", "bridges", [18, 29, 14], "Banking news is easier to read when you separate liquidity, solvency, capital, funding, payments, policy, and confidence.", "The same headline may involve several layers, so a systems map prevents one dramatic detail from becoming the whole explanation.", "A story about emergency lending may be about liquidity support, not necessarily a declaration that every borrower is insolvent.", "Good banking analysis asks which layer of the system is under stress.", 3, 0.88, 0.22)
    ]
  },
  {
    id: "economics",
    short: "econ",
    title: "Economics",
    description: "A beginner-friendly map of scarcity, incentives, markets, macroeconomics, institutions, and model limits.",
    audience: "Learners who want to reason about everyday tradeoffs and economic claims",
    level: "Beginner",
    purpose: "Teach the core shape of economics without turning models into dogma.",
    accent_color: "#8a5a26",
    boundary: "Educational only. Economic models simplify reality and policy choices depend on values, data quality, institutions, and current conditions.",
    source_refs: [
      source("econ-openstax", "Principles of Economics 3e", "OpenStax", "https://openstax.org/details/books/principles-economics-3e", "Introductory economics definitions and model structures."),
      source("econ-bls", "Labor Force Statistics from the Current Population Survey", "US Bureau of Labor Statistics", "https://www.bls.gov/cps/", "Unemployment and labor-market measurement concepts."),
      source("econ-imf-basics", "Back to Basics", "International Monetary Fund", "https://www.imf.org/en/Publications/fandd/issues/Series/Back-to-Basics", "Accessible macroeconomic and policy explainers."),
      source("econ-worldbank-trade", "Trade", "World Bank", "https://www.worldbank.org/en/topic/trade", "Trade, development, and global economic context."),
      source("econ-fed-research", "Economic Research", "Board of Governors of the Federal Reserve System", "https://www.federalreserve.gov/econres.htm", "Economic research and macro-financial context.")
    ],
    rows: [
      r("Scarcity", "foundations", [], "Scarcity means people want more valuable things than available time, attention, resources, or capacity can provide.", "Economics begins here because every choice uses something that could have been used another way.", "Choosing an evening class means not using that same evening for paid work, sleep, or family time.", "Scarcity turns choice into a real problem.", 1, 1, 1),
      r("Opportunity cost", "foundations", [1], "Opportunity cost is the value of the best alternative you give up when choosing one option.", "It makes hidden tradeoffs visible and prevents free-looking choices from being treated as free.", "A free concert still costs the evening you could have spent studying or resting.", "The true cost of a choice includes the best foregone alternative.", 1, 0.98, 0.98),
      r("Tradeoffs and constraints", "foundations", [2], "A tradeoff is a tension between desirable goals under a constraint such as time, money, law, or technology.", "Good economic reasoning names the binding constraint first; arguing only about which option is preferred, without saying what limits the choice, leaves the actual tradeoff unexplained.", "A city budget cannot maximize every service at once if revenue and staff are limited.", "Tradeoffs become clearer when the constraint is explicit.", 1, 0.92, 0.92),
      r("Incentives", "foundations", [1], "An incentive is anything that changes the expected benefit, cost, risk, or social meaning of an action.", "Incentives matter because people and organizations adjust behavior when rules or payoffs change.", "A bottle deposit encourages returns by making recycling financially visible at the moment of choice.", "People respond to incentives, including non-money incentives.", 1, 0.96, 0.96),
      r("Marginal thinking", "foundations", [2], "Marginal thinking compares the extra benefit and extra cost of one more unit or one more step.", "It avoids all-or-nothing reasoning because most real decisions happen at the margin, one added unit or step at a time, not as a single yes-or-no verdict on an entire activity.", "A cafe deciding whether to stay open one extra hour compares extra sales with extra wages and utilities.", "Many choices are about the next increment, not the whole activity.", 2, 0.94, 0.92),
      r("Sunk costs", "misconceptions", [2, 5], "A sunk cost is a past cost that cannot be recovered and should not decide the next choice by itself.", "The hard part is emotional: people often keep investing to avoid admitting an earlier loss.", "Finishing a bad movie because you paid for the ticket confuses past spending with present value.", "Do not let unrecoverable costs command future decisions.", 2, 0.8, 0.7),
      r("Comparative advantage", "mechanisms", [2], "Comparative advantage means a person or country can gain from specializing where its opportunity cost is lower.", "The idea explains why trade can help even when one side is absolutely better at producing everything.", "A surgeon may hire someone to paint the clinic because surgery time has a higher opportunity cost.", "Trade can create gains by reallocating effort toward lower opportunity costs.", 3, 0.88, 0.72),
      r("Specialization", "mechanisms", [7], "Specialization concentrates effort on narrower tasks so people can build skill, tools, and scale.", "It raises productivity but also creates dependence on exchange and coordination.", "A bakery that focuses on bread can justify better ovens and repeated practice.", "Specialization improves output while increasing interdependence.", 2, 0.82, 0.64),
      r("Markets as coordination", "foundations", [4, 8], "A market coordinates many buyers and sellers through prices, rules, information, and property rights.", "It is not just a physical place; it is an ongoing process for discovering prices and terms of exchange as buyers and sellers continuously adjust offers to new information.", "Online ride pricing coordinates drivers, riders, location, and timing without one dispatcher assigning every trip.", "Markets coordinate decentralized plans through signals and rules.", 2, 0.92, 0.78),
      r("Supply", "mechanisms", [5, 9], "Supply describes how much sellers are willing and able to offer at different prices, holding other factors steady.", "It reflects costs, technology, expectations, taxes, inputs, and the opportunity cost of producing.", "If coffee bean costs rise, cafes may offer less coffee at the same price.", "Supply is a schedule of seller behavior, not a single number.", 2, 0.86, 0.7),
      r("Demand", "mechanisms", [5, 9], "Demand describes how much buyers are willing and able to purchase at different prices, holding other factors steady.", "It reflects income, preferences, substitutes, complements, expectations, and the usefulness of the good.", "If bus fares rise, some commuters may shift to walking, cycling, or carpooling.", "Demand is a relationship between price and quantity buyers choose.", 2, 0.86, 0.7),
      r("Equilibrium", "mechanisms", [10, 11], "Equilibrium is a point where planned buying and selling are mutually consistent at a given price.", "It is a model result, not a guarantee that markets are fair, instant, or free of power.", "If many people want concert tickets at a low price, shortage pressure appears until price, quantity, or rules change.", "Equilibrium shows balance between plans, not moral perfection.", 2, 0.84, 0.64),
      r("Elasticity", "mechanisms", [10, 11], "Elasticity measures how strongly quantity responds to a change such as price, income, or another price.", "It matters because the same tax, shortage, or price increase has different effects when people can easily adjust.", "Gasoline demand may be less flexible in the short run than restaurant demand because commuting options are limited.", "Elasticity asks how much behavior moves when conditions change.", 3, 0.8, 0.54),
      r("Consumer surplus", "applications", [12], "Consumer surplus is the gap between what buyers were willing to pay and what they actually pay.", "It gives a way to discuss gains from trade without assuming price equals total value.", "If you would pay 20 dollars for a book and buy it for 12, the extra 8 dollars is surplus to you.", "Value to buyers can exceed the market price they pay.", 3, 0.68, 0.36),
      r("Producer surplus", "applications", [12], "Producer surplus is the gap between the price sellers receive and the minimum they would accept to supply.", "It helps explain why sellers benefit from trades and why cost changes affect participation.", "A farmer willing to sell apples for 2 dollars per bag gains surplus if the market price is 3 dollars.", "Sellers also receive gains from mutually accepted trades.", 3, 0.66, 0.34),
      r("Price controls", "applications", [12], "Price controls are legal limits on prices, such as ceilings that cap how high a price may rise or floors that cap how low it may fall, imposed instead of letting supply and demand set the level.", "They may pursue fairness or stability, but they can create shortages, surpluses, quality changes, or rationing when set far from market-clearing levels.", "A rent ceiling can help current tenants while reducing incentives to add rental housing.", "Changing prices by rule also changes quantities and behavior.", 3, 0.78, 0.44),
      r("Taxes and incidence", "mechanisms", [13], "Tax incidence asks who ultimately bears a tax after prices and quantities adjust.", "The legal payer is not always the economic bearer because burden shifts toward the side less able to adjust.", "A payroll tax charged to employers can still lower wages if labor supply and demand conditions permit.", "Who writes the check is not always who bears the cost.", 3, 0.8, 0.48),
      r("Externalities", "limitations", [9], "An externality is a cost or benefit of an action that affects others outside the transaction.", "Markets can overproduce harmful externalities or underproduce beneficial ones when prices omit spillovers.", "A factory's pollution affects nearby residents even if they never bought the factory's product.", "When side effects are unpriced, private choices can miss social costs or benefits.", 2, 0.9, 0.6),
      r("Public goods", "limitations", [9], "A public good is hard to exclude people from and one person's use does not greatly reduce another's use.", "Those traits create free-rider problems because people can benefit without paying voluntarily.", "National defense protects everyone in a country's territory, including residents who pay no taxes toward it.", "Some valuable goods are undersupplied when payment cannot be limited to users.", 2, 0.84, 0.52),
      r("Common resources", "limitations", [18], "A common resource is one that is difficult to exclude people from using but that can still be depleted, degraded, or crowded as more people draw on it at once.", "The problem is overuse unless rules, norms, ownership, or coordination protect the resource.", "An unmanaged fishery can be exhausted because each boat gains from catching now while depletion is shared.", "Shared access plus depletion creates a governance challenge.", 2, 0.8, 0.48),
      r("Market power", "limitations", [9], "Market power is the ability of a seller or buyer to influence price or terms rather than simply accept them.", "It can reduce output, raise prices, shape wages, or limit innovation depending on context.", "A single broadband provider in a town may charge more than firms facing strong competition.", "Markets need competition or countervailing rules to discipline power.", 3, 0.84, 0.46),
      r("Information asymmetry", "limitations", [9], "Information asymmetry appears when one side of a transaction knows much more than the other.", "It can cause adverse selection, mistrust, costly screening, warranties, certification, or regulation.", "A used-car seller may know defects that a buyer cannot easily observe before purchase.", "Unequal information changes what trades happen and at what terms.", 3, 0.8, 0.44),
      r("Principal-agent problems", "mechanisms", [22], "A principal-agent problem arises when one person acts for another but has different incentives or better information.", "Contracts, monitoring, reputation, and ownership can reduce the problem but rarely remove it entirely.", "A hired manager may prefer short-term bonuses over the owner's long-term health of the firm.", "Delegation needs incentive design because agents have their own goals.", 3, 0.74, 0.36),
      r("Behavioral biases", "bridges", [4], "Behavioral biases are predictable patterns where real choices depart from the simplest rational-choice model.", "They do not mean people are foolish; they show that attention, framing, habits, and emotions affect decisions.", "A default retirement contribution can raise saving because inertia shapes behavior.", "Economic actors are human, not frictionless calculators.", 2, 0.78, 0.42),
      r("Measuring output with GDP", "foundations", [1], "Gross domestic product measures the market value of final goods and services produced within an economy over a period.", "It is useful for output, income, and spending analysis, but it misses unpaid work, distribution, environmental damage, and many quality differences.", "Home childcare counts differently from paid childcare even when the care is similar.", "GDP is a powerful output measure with clear blind spots.", 2, 0.86, 0.58),
      r("Inflation indexes", "mechanisms", [25], "Inflation indexes track price changes for a basket of goods and services over time.", "They require choices about weights, quality adjustments, substitution, and whose spending pattern is represented.", "A retiree and a student may experience different cost changes even under the same national inflation rate.", "Inflation measurement is a designed approximation of changing purchasing power.", 3, 0.82, 0.5),
      r("Unemployment", "foundations", [25], "Unemployment measures people without work who are available and actively looking under a specific statistical definition.", "It excludes some discouraged, underemployed, unpaid, or informal work situations, so interpretation needs context.", "Someone who stopped searching may not count as unemployed even if they want a job.", "Unemployment is a defined labor-market measure, not the whole story of work hardship.", 2, 0.84, 0.54),
      r("Labor markets", "mechanisms", [4, 27], "Labor markets coordinate workers, employers, wages, skills, working conditions, and bargaining power.", "They differ from simple commodity markets because jobs involve identity, location, law, training, and long relationships.", "A nursing shortage may reflect wages, licensing, burnout, training capacity, and regional demand together.", "Work is priced in markets shaped by institutions and human constraints.", 3, 0.8, 0.44),
      r("Productivity", "foundations", [8, 25], "Productivity measures how much output is produced per unit of input, such as goods created per worker hour, machine hour, or unit of capital invested.", "It rises through skills, tools, organization, technology, infrastructure, and better allocation of resources.", "A warehouse scanner can let the same worker accurately fill more orders per hour.", "Long-run living standards depend heavily on productivity growth.", 2, 0.88, 0.56),
      r("Human capital", "bridges", [29], "Human capital is the knowledge, health, skills, and habits that make people more productive or adaptable.", "It is built through education, practice, caregiving, nutrition, safety, and work experience, not only formal degrees.", "Learning to read well changes future job options and civic participation.", "Investing in people is a central economic force.", 2, 0.78, 0.42),
      r("Capital and investment", "foundations", [29], "Capital means produced assets used to make other goods and services, while investment creates or improves those assets.", "It includes machines, buildings, software, and infrastructure, not just financial assets.", "A delivery company buying routing software is investing in productive capital.", "Economic investment builds capacity for future production.", 2, 0.8, 0.48),
      r("Money in macroeconomics", "bridges", [25, 26], "Money supports exchange, accounting, and saving, so macroeconomics studies its link to spending and prices.", "The same quantity of money can have different effects depending on velocity, banking, expectations, and output capacity.", "If people hoard extra cash during panic, spending may not rise much.", "Money is central to macro outcomes but works through behavior and institutions.", 3, 0.78, 0.38),
      r("Interest rates in the economy", "mechanisms", [31, 32], "Interest rates connect present spending with future repayment and influence saving, borrowing, asset prices, and currency values.", "They are not one number; different maturities and risks create a structure of rates.", "A higher mortgage rate can cool housing demand while savings accounts become more attractive.", "Rates are economy-wide prices for time, risk, and liquidity.", 3, 0.82, 0.42),
      r("Aggregate demand and aggregate supply", "mechanisms", [25], "Aggregate demand summarizes planned spending across households, firms, government, and foreigners, while aggregate supply summarizes production capacity and costs.", "The model helps separate demand-driven slowdowns from supply shocks, though real events often mix both.", "A pandemic can reduce supply through closures and demand through lost income at the same time.", "Macroeconomic conditions depend on both spending pressure and productive capacity.", 3, 0.8, 0.38),
      r("Business cycles", "applications", [34], "Business cycles are expansions and contractions in economic activity around longer-run growth.", "They reflect shocks, credit, expectations, policy, inventories, global links, and feedback between spending and income.", "A drop in demand can lead firms to cut hours, which reduces income and further weakens demand.", "The economy can move in self-reinforcing waves, not just straight lines.", 3, 0.82, 0.36),
      r("Fiscal policy", "applications", [34], "Fiscal policy uses government spending, taxation, and transfers to affect demand, distribution, and public goods.", "It operates through budgets and politics, so timing, targeting, debt, and administrative capacity matter.", "A temporary unemployment benefit can support household spending during a downturn.", "Fiscal policy changes economic conditions through the public budget.", 3, 0.78, 0.34),
      r("Monetary policy", "applications", [32, 33], "Monetary policy uses central-bank tools to influence financial conditions and inflation.", "It is powerful but indirect because it works through rates, credit, expectations, asset prices, and exchange rates.", "A rate increase may slow borrowing and reduce inflation pressure after a delay.", "Monetary policy steers the economy through financial channels.", 3, 0.82, 0.34),
      r("Trade and tariffs", "applications", [7], "Trade lets people specialize and exchange across borders, while tariffs tax imports and alter relative prices.", "Tariffs can protect some producers but usually raise costs for consumers or downstream firms and invite retaliation.", "A tariff on imported steel may help steelmakers while raising costs for car manufacturers.", "Trade policy creates winners, losers, and economy-wide ripple effects.", 3, 0.78, 0.32),
      r("Exchange rates", "bridges", [33, 38], "An exchange rate is the price of one currency stated in terms of another, showing how many units of a foreign currency a unit of domestic currency can buy.", "It affects import prices, exports, travel, debts, capital flows, and inflation, while responding to rates, expectations, and risk.", "A weaker domestic currency can make imported electronics more expensive and exports cheaper abroad.", "Currencies connect domestic choices to the world economy.", 3, 0.72, 0.28),
      r("Institutions and property rights", "foundations", [9], "Institutions are formal and informal rules that shape economic behavior, including property rights, courts, norms, and public agencies.", "They determine whether contracts can be trusted, investment is safe, and markets can function beyond personal relationships.", "A land title system can make it easier to borrow, sell, or improve property.", "Economic outcomes depend on rules as well as resources.", 2, 0.86, 0.48),
      r("Inequality and distribution", "limitations", [25], "Distribution asks who receives income, wealth, risk, power, and opportunity across an economy.", "Efficiency gains can coexist with unequal outcomes, so policy debates often combine economics with values.", "A policy can raise total output while leaving some workers worse off without compensation.", "An average gain does not tell you who gained.", 3, 0.84, 0.34),
      r("Welfare and efficiency", "limitations", [14, 15], "Efficiency describes whether resources are arranged to create more total surplus, while welfare asks about wellbeing and social evaluation.", "A situation can be efficient yet unacceptable if distribution, rights, or dignity are ignored.", "A perfectly priced market for a harmful product may still raise welfare questions.", "Efficiency is useful, but it is not the only social criterion.", 3, 0.78, 0.28),
      r("Cost-benefit analysis", "applications", [2, 42], "Cost-benefit analysis compares expected gains and losses from a decision in a structured way.", "It clarifies tradeoffs but depends on measurement choices, discounting, uncertainty, and whose costs count.", "A flood barrier analysis must value construction cost, avoided damage, ecological impact, and risk uncertainty.", "Structured comparison improves decisions, but values and assumptions remain visible.", 3, 0.76, 0.28),
      r("Economic models", "limitations", [1], "An economic model is a simplified representation built to clarify one mechanism or question.", "Models are useful when their assumptions fit the task and dangerous when treated as complete reality.", "A supply-and-demand diagram can explain price pressure without capturing every legal or emotional detail.", "Models are maps; judge them by purpose and limits.", 2, 0.88, 0.52),
      r("Ceteris paribus", "limitations", [44], "Ceteris paribus means holding other things equal so one relationship can be studied clearly.", "The phrase protects reasoning inside a model but should not hide that real variables move together.", "Demand may slope downward holding income constant, even though recessions can change income and prices together.", "Holding other factors constant is a tool, not a claim that the world freezes.", 2, 0.72, 0.34),
      r("Correlation versus causation", "misconceptions", [44], "Correlation means two things move together, while causation means one produces a change in the other.", "Confounders, reverse causality, selection, and timing can make correlations misleading.", "Ice cream sales and drowning rise in summer, but heat and swimming exposure explain the link.", "Economic evidence must ask what caused what.", 2, 0.84, 0.42),
      r("Game theory", "advanced-horizons", [4], "Game theory studies strategic situations where each participant's best choice depends on what others do.", "It helps explain cooperation, competition, bargaining, coordination, and credible commitments.", "Two firms deciding whether to cut prices must consider how the rival will respond.", "Strategy matters when outcomes depend on mutual expectations.", 4, 0.72, 0.22),
      r("Expectations", "bridges", [34], "Expectations are beliefs people hold about future prices, income, or policy that shape the decisions they make today, well before those future events actually occur.", "They influence inflation, investment, hiring, saving, exchange rates, and policy effectiveness because people act before outcomes arrive.", "If firms expect higher future costs, they may raise prices or lock in contracts now.", "The future affects the present through expectations.", 3, 0.8, 0.3),
      r("Growth limits and environment", "advanced-horizons", [29, 18], "Economic growth depends on resources, technology, institutions, and ecological constraints.", "Environmental damage can be an externality, a resource limit, and a distribution issue at the same time.", "A factory may raise GDP while creating pollution costs not reflected in its sale price.", "Prosperity analysis must include the systems that production draws from.", 4, 0.74, 0.2),
      r("Reading economic claims", "bridges", [44, 46], "A strong economic claim names the model, data, mechanism, affected groups, uncertainty, and counterargument.", "This habit prevents single charts or slogans from doing more work than they can support.", "A headline about inflation should prompt questions about time period, measure, cause, and distribution.", "Good economic reading asks what is assumed, measured, and left out.", 3, 0.92, 0.3)
    ]
  },
  {
    id: "children-rearing-development-and-care",
    short: "child",
    title: "Children Rearing, Development and Care",
    description: "A developmentally respectful map of child growth, care, safety, learning, boundaries, and caregiver wellbeing.",
    audience: "Caregivers and learners seeking educational orientation rather than individualized medical advice",
    level: "Beginner",
    purpose: "Build a calm map of child development and care while distinguishing guidance, uncertainty, and professional boundaries.",
    accent_color: "#9a5d74",
    boundary: "Educational only. Child health, safety, disability, nutrition, mental health, and development concerns need qualified professional guidance for individual decisions or urgent risks.",
    source_refs: [
      source("child-cdc-milestones", "Developmental Milestones", "Centers for Disease Control and Prevention", "https://www.cdc.gov/act-early/milestones/index.html", "Developmental milestone orientation and when to seek guidance."),
      source("child-aap-healthychildren", "HealthyChildren.org", "American Academy of Pediatrics", "https://www.healthychildren.org/", "Pediatric health, safety, development, and family guidance."),
      source("child-who-health", "Child health", "World Health Organization", "https://www.who.int/health-topics/child-health", "Global child-health principles and public-health framing."),
      source("child-cdc-safe-sleep", "About Sudden Unexpected Infant Death and Safe Sleep", "Centers for Disease Control and Prevention", "https://www.cdc.gov/sudden-infant-death/about/index.html", "Current AAP-aligned safe-sleep recommendations for reducing infant sleep-related risk."),
      source("child-cdc-passenger-safety", "Child Passenger Safety", "Centers for Disease Control and Prevention", "https://www.cdc.gov/child-passenger-safety/about/", "Car seat, booster seat, and seat belt guidance by age and size."),
      source("child-myplate", "MyPlate for children", "US Department of Agriculture", "https://www.myplate.gov/life-stages/children", "General food-group and nutrition education for children.")
    ],
    rows: [
      r("Development is uneven", "foundations", [], "Children develop across movement, language, cognition, emotion, social connection, and self-care at different rates.", "Milestones are useful signals, not a scoreboard; patterns and context matter more than one isolated date.", "A toddler may talk early and still need ordinary time to build motor confidence.", "Development is a pattern to understand, not a race to win.", 1, 1, 1),
      r("Attachment", "foundations", [1], "Attachment is the child's expectation that caregivers are available, protective, and emotionally responsive.", "Secure attachment grows through repeated repair and responsiveness, not perfect calm every minute.", "A caregiver who returns after frustration and comforts the child teaches that connection can survive stress.", "Reliable responsiveness builds a base for exploration.", 2, 0.96, 0.95),
      r("Temperament", "foundations", [1], "Temperament describes biologically influenced tendencies such as intensity, adaptability, sensitivity, and activity level.", "It shapes what support works; the same routine can calm one child and overwhelm another.", "A highly sensitive child may need quieter transitions than a child who enjoys novelty.", "Care improves when adults adapt to the child in front of them.", 2, 0.9, 0.86),
      r("Serve and return", "mechanisms", [2], "Serve and return means a child signals and an adult responds in a way that continues interaction.", "These small exchanges build language, attention, emotional security, and brain architecture through repetition.", "A baby points at a dog, and an adult says, 'Yes, a brown dog is barking,' turning attention into learning.", "Responsive back-and-forth is a core engine of early development.", 1, 0.94, 0.9),
      r("Language development", "mechanisms", [4], "Language grows through hearing meaningful speech, shared attention, turn-taking, imitation, and chances to communicate.", "Children need interaction more than passive word exposure because language is social as well as cognitive.", "Reading a picture book and pausing for the child to point teaches more than background audio.", "Language develops through responsive communication.", 2, 0.92, 0.82),
      r("Play", "foundations", [1], "Play is serious developmental work because it lets children practice movement, imagination, rules, negotiation, and problem solving.", "Different play forms support different skills, from sensory exploration to pretend stories and cooperative games.", "A cardboard box can become a car, a cave, and a negotiation over whose turn comes next.", "Play is how children test the world safely.", 1, 0.92, 0.84),
      r("Sleep rhythms", "mechanisms", [1], "Sleep supports growth, learning, mood, immune function, and caregiver functioning, but sleep patterns change with age.", "Helpful routines cue the body and reduce negotiation, while persistent concerns may need professional guidance.", "A predictable bath, story, and lights-out pattern can make bedtime less surprising.", "Sleep is biological, developmental, and relational at once.", 2, 0.88, 0.76),
      r("Nutrition boundaries", "limitations", [1], "Nutrition guidance gives broad patterns for growth, energy, and habits, not individualized treatment plans.", "Food needs vary by age, health, culture, access, allergies, and medical conditions, so concerns belong with qualified clinicians.", "Offering varied foods is different from managing a diagnosed feeding disorder.", "Food education should support health without pretending to be medical care.", 2, 0.84, 0.7),
      r("Growth charts", "applications", [1], "Growth charts compare a child's measurements with reference populations over time.", "The trend and clinical context matter more than one percentile, and interpretation belongs with pediatric guidance.", "A child consistently following a lower percentile may be healthy, while a sudden drop may need attention.", "Growth charts are conversation tools, not parental report cards.", 2, 0.78, 0.58),
      r("Safety layers", "foundations", [1], "Safety works best as layers: environment design, supervision, routines, skills, and emergency readiness.", "No single rule catches every risk, so caregivers reduce harm by making safe choices easier and unsafe choices harder.", "A pool fence, locked gate, swim lessons, and attentive adults protect differently.", "Safety is a system, not a single warning.", 1, 0.96, 0.86),
      r("Safe sleep", "applications", [7, 10], "Current guidance for healthy infants is to place a baby on their back for every nap and every night, on a firm, flat sleep surface, with nothing else, no pillows, blankets, bumpers, or soft toys, in the sleep space.", "This combination lowers known sleep-related risks, but recommendations can be updated and individual health conditions can change what applies, so caregivers should confirm current specifics with a pediatric clinician.", "A bare, firm sleep surface follows a different safety logic than a soft adult couch.", "Infant sleep safety is a high-stakes area for current professional guidance.", 2, 0.92, 0.62),
      r("Emotion regulation", "mechanisms", [2], "Emotion regulation is the growing ability to notice, tolerate, express, and recover from feelings.", "Children borrow adult nervous-system support before they can reliably regulate alone.", "A preschooler may need help naming anger and breathing before discussing the broken toy.", "Self-control develops through supported practice, not commands alone.", 2, 0.94, 0.82),
      r("Co-regulation", "mechanisms", [12], "Co-regulation is the adult's active support of a child's emotional state through calm presence, structure, and repair.", "It teaches the nervous system what returning to safety feels like after distress, using a calmer adult's breathing, tone, and pacing as an external anchor before the child can self-soothe.", "Sitting nearby and speaking softly during a meltdown can be more regulating than rapid explanations.", "Children learn regulation first with someone, then increasingly within themselves.", 2, 0.92, 0.8),
      r("Discipline as teaching", "misconceptions", [12, 13], "Discipline is most useful when treated as teaching skills, boundaries, and repair rather than punishing feelings.", "Effective limits are clear, consistent, proportionate, and connected to the behavior being learned.", "Having a child wipe up spilled water teaches responsibility better than shaming the accident.", "Discipline should build capability and connection.", 2, 0.9, 0.72),
      r("Routines", "applications", [7, 14], "Routines reduce cognitive load by making daily expectations visible and repeatable.", "They support sleep, cooperation, transitions, and autonomy while still needing flexibility for real life.", "A picture chart can help a child move from pajamas to teeth brushing without constant adult prompting.", "Predictable routines make independence easier.", 1, 0.84, 0.66),
      r("Executive function", "mechanisms", [12], "Executive function includes working memory, flexible thinking, and inhibitory control.", "These skills develop gradually and are sensitive to sleep, stress, language, scaffolding, and practice.", "A child who forgets multi-step instructions may need one visible step at a time.", "Planning and self-control are developmental skills, not fixed character traits.", 3, 0.86, 0.62),
      r("Social learning", "mechanisms", [4, 6], "Children learn by watching what adults and peers do, not only by hearing what adults say.", "Modeling can teach kindness, coping, curiosity, prejudice, persistence, and conflict habits.", "A caregiver apologizing after snapping demonstrates repair more powerfully than a lecture about respect.", "Children study behavior around them as live curriculum.", 2, 0.86, 0.62),
      r("Screens and attention", "limitations", [6], "Screen use affects children differently depending on age, content, context, sleep, movement, and adult involvement.", "The important question is what screen time displaces and whether it supports or undermines relationships and routines.", "A video call with a grandparent is different from endless autoplay before bed.", "Screens need context-aware boundaries, not panic or indifference.", 3, 0.8, 0.44),
      r("Reading aloud", "applications", [5], "Reading aloud builds vocabulary, attention, background knowledge, bonding, and print awareness.", "The interaction around the book, pointing, pausing, questioning, and reacting together, often matters as much as finishing the text, since dialogue extends what the words alone teach.", "Asking what might happen next invites prediction and conversation.", "Shared reading turns language into relationship and thinking.", 1, 0.86, 0.64),
      r("Fine motor development", "mechanisms", [1], "Fine motor development involves small-muscle control for grasping, drawing, dressing, tools, and writing.", "It grows through play, sensory feedback, strength, coordination, and repeated attempts.", "Stacking blocks and using child-safe tongs both build hand control for later tasks.", "Small movements are built through purposeful practice.", 2, 0.72, 0.46),
      r("Gross motor development", "mechanisms", [1], "Gross motor development involves large-muscle skills such as sitting, crawling, walking, running, climbing, and balance.", "Practice environments should offer safe challenge because strength and coordination grow through movement.", "A playground step that is difficult but supervised can teach balance and judgment.", "Bodies learn by moving through graded challenge.", 2, 0.74, 0.46),
      r("Toilet learning", "applications", [1, 15], "Toilet learning combines body readiness, communication, routine, motivation, and caregiver patience.", "Pressure can create stress; persistent pain, constipation, regression, or concern belongs with medical guidance.", "A child may understand the toilet but not yet recognize body signals reliably.", "Toilet learning is developmental coordination, not a moral test.", 2, 0.7, 0.38),
      r("Separation anxiety", "applications", [2], "Separation anxiety is a common developmental response when children understand caregiver absence but still need reassurance.", "Predictable goodbyes, honest returns, and trusted caregivers help children practice separations safely.", "Sneaking away may avoid tears now but can make future departures less predictable.", "Separation skills grow through trust and repetition.", 2, 0.76, 0.48),
      r("Tantrums", "misconceptions", [12, 13], "Tantrums often reflect overwhelmed regulation, communication, hunger, fatigue, transitions, or limits rather than calculated manipulation.", "Adults can hold boundaries while reducing stimulation and helping the child recover.", "A store meltdown may need calm removal and later teaching, not a public debate.", "A tantrum is a stress signal plus a teaching moment after calm returns.", 2, 0.86, 0.58),
      r("Praise and feedback", "applications", [14], "Feedback shapes what children notice about their own effort, strategy, care, and outcome, since children tend to repeat whatever an adult's comments draw their attention toward.", "Specific feedback teaches better than global labels because it names the behavior the child can repeat.", "Saying 'You kept trying different puzzle pieces' is more informative than only saying 'You're smart.'", "Helpful praise points to process and values.", 2, 0.78, 0.48),
      r("Autonomy", "bridges", [15, 14], "Autonomy is the child's growing sense of agency, the felt experience of having real choices and some control over actions, that develops within boundaries adults still protect.", "Choice helps cooperation when options are real, limited, and developmentally appropriate.", "Letting a preschooler choose between two shirts supports agency without handing over the entire morning schedule.", "Children need chances to choose inside protected limits.", 2, 0.8, 0.48),
      r("Sibling dynamics", "applications", [14, 25], "Sibling dynamics mix love, rivalry, imitation, fairness concerns, and competition for caregiver attention.", "Adults can reduce comparison, protect safety, and teach repair without forcing constant harmony.", "Naming each child's need may work better than declaring one child the winner of a dispute.", "Sibling conflict is relationship practice when adults structure it well.", 3, 0.7, 0.34),
      r("Peer play", "applications", [6, 17], "Peer play teaches negotiation, turn-taking, perspective, boundaries, and social problem solving.", "Children need adult scaffolding when skills are emerging, especially around exclusion or aggression.", "Two children wanting the same truck can practice timers, trading, or building together.", "Peers give children a living laboratory for social skills.", 2, 0.76, 0.42),
      r("Learning differences", "limitations", [1, 16], "Learning differences are variations in how children process information, communicate, attend, move, or demonstrate knowledge.", "Early support can reduce frustration, but labels and interventions should come from qualified evaluation when concerns persist.", "A child who understands stories but struggles to decode print may need targeted reading support.", "Different learning paths need curiosity, not blame.", 3, 0.84, 0.5),
      r("Speech concerns", "limitations", [5], "Speech and language concerns involve communication milestones, clarity, comprehension, social use, or fluency.", "Because early support can matter, caregivers should seek professional screening when concerns or regressions appear.", "A toddler who loses words they once used deserves prompt guidance rather than watchful dismissal.", "Communication concerns are worth checking early.", 3, 0.82, 0.46),
      r("Sensory differences", "bridges", [3], "Sensory differences affect how a child experiences sound, touch, movement, light, taste, or body position.", "Support often begins by changing environments and expectations before assuming defiance.", "A child covering ears in a loud cafeteria may be overwhelmed rather than rude.", "Behavior can be a clue about sensory experience.", 3, 0.78, 0.38),
      r("School readiness", "applications", [16, 19], "School readiness includes social, emotional, language, motor, self-care, curiosity, and attention skills.", "It is broader than early academics and depends on both the child and the school's ability to welcome learners.", "Knowing how to ask for help can matter as much as naming letters on the first day.", "Readiness is a fit between child skills and school supports.", 2, 0.76, 0.38),
      r("Motivation and curiosity", "bridges", [6, 25], "Curiosity grows when children feel safe enough to explore and challenged enough to stay engaged.", "Adults can support motivation by offering meaningful choices, questions, models, and achievable difficulty.", "A child investigating worms after rain is practicing observation, not wasting time.", "Curiosity is attention pulled by meaningful questions.", 2, 0.78, 0.4),
      r("Caregiver wellbeing", "foundations", [2], "Caregiver wellbeing affects patience, responsiveness, safety, and the emotional climate around the child.", "Support for adults is not selfish; it is part of the child's care system, because a caregiver's stress, sleep, and mood directly shape the tone of everyday interactions.", "A rested caregiver may respond to the same spilled juice with teaching instead of explosion.", "Children are supported by supporting the people who care for them.", 2, 0.92, 0.7),
      r("Stress and resilience", "mechanisms", [34], "Stress becomes more or less harmful depending on intensity, duration, predictability, support, and recovery.", "Resilience is built through relationships, routines, coping skills, and reducing avoidable chronic stressors.", "A hard move is easier for a child when adults explain, listen, and preserve familiar rituals.", "Resilience grows in supported recovery, not in endless pressure.", 3, 0.86, 0.5),
      r("Trauma-informed lens", "limitations", [35], "A trauma-informed lens asks what happened to a child and what helps safety, rather than starting with what is wrong with them.", "It does not excuse harmful behavior, but it changes the support plan toward predictability, choice, and repair.", "A child who panics at loud voices may need calm cues before consequences can teach.", "Safety and understanding make learning possible after stress.", 4, 0.8, 0.34),
      r("Culture and family values", "bridges", [14], "Caregiving practices are shaped by culture, family history, community, faith, language, and practical constraints.", "Respecting culture does not remove safety boundaries, but it prevents one narrow style from being mistaken for universal truth.", "A bedtime routine can look different across households while still offering predictability and warmth.", "Good guidance distinguishes core needs from culturally varied practices.", 3, 0.76, 0.34),
      r("Consistency across caregivers", "applications", [15, 37], "Consistency across caregivers helps children predict rules, routines, and responses.", "It does not require identical personalities; it requires shared safety boundaries and repair when adults differ.", "A grandparent and parent can use different bedtime songs while agreeing on screen limits.", "Children feel safer when adults coordinate the important parts.", 2, 0.8, 0.44),
      r("Illness boundaries", "limitations", [8], "Common illness decisions can involve symptoms, age, risk factors, exposures, and local guidance.", "Educational information cannot decide whether an individual child needs urgent care, testing, medication, or isolation.", "A fever in a young infant has a different risk profile than a mild sniffle in an older child.", "Health choices need current professional guidance when risk is real.", 3, 0.88, 0.42),
      r("Medication and medical advice boundaries", "limitations", [39], "Medication choices for children depend on age, weight, diagnosis, interactions, dosing, and clinician advice.", "Caregivers should avoid using general educational content as a dosing or treatment plan.", "An over-the-counter label may still require checking age, concentration, and contraindications.", "Child medication is individualized healthcare, not a generic tip.", 3, 0.9, 0.4),
      r("Food allergies and choking", "applications", [8, 10], "Food allergies and choking hazards are safety-sensitive because consequences can be sudden and severe.", "General education can name risk categories, but individual allergy plans and emergency steps require qualified guidance.", "Whole grapes and hard candies pose choking risks for young children unless prepared safely.", "Food safety combines prevention, preparation, and professional plans when needed.", 2, 0.88, 0.38),
      r("Outdoor risky play", "bridges", [10, 21], "Risky play gives children manageable chances to test height, speed, tools, boundaries, and confidence.", "The goal is not danger; it is calibrated challenge where adults remove hazards while allowing learning.", "Climbing a low tree with supervision teaches judgment differently from banning all climbing.", "Children learn risk by practicing within protected margins.", 3, 0.74, 0.28),
      r("Digital privacy", "advanced-horizons", [18], "Digital privacy for children includes images, location, habits, educational records, and data collected by apps.", "Adults make choices, like sharing photos or enabling location tracking, that can follow a child for years, well before the child is old enough to understand or consent to that record.", "Posting a school uniform photo can reveal more about location and routine than intended.", "A child's digital footprint deserves protective judgment.", 3, 0.76, 0.26),
      r("Emergencies and first aid boundaries", "limitations", [10], "Emergency and first-aid knowledge can help caregivers prepare, but urgent situations require local emergency services and trained guidance.", "Plans, emergency numbers, first-aid supplies, and practiced routines reduce hesitation and wasted seconds when stress is high and clear thinking is hardest to sustain.", "Knowing where the emergency contacts are is part of care, but it is not a substitute for calling for help.", "Preparation supports action; emergencies need real-time professional help.", 3, 0.86, 0.34),
      r("Sleep problems and seeking help", "limitations", [7], "Persistent sleep problems can reflect routines, development, stress, environment, medical issues, or family constraints.", "Professional guidance is appropriate when sleep concerns are severe, unsafe, prolonged, or tied to health symptoms.", "Snoring, breathing pauses, or extreme daytime sleepiness changes the sleep conversation.", "Sleep advice has limits when health or safety signs appear.", 3, 0.78, 0.3),
      r("Behavior patterns and context", "misconceptions", [24], "Behavior makes more sense when adults look for patterns across time, setting, triggers, skills, and recovery.", "A single label like lazy or bad can block useful observation, since it stops adults from asking what skill is missing, what trigger is present, or what support would help.", "A child melting down only after noisy school days may be showing overload rather than attitude.", "Context turns behavior from a verdict into data.", 3, 0.86, 0.42),
      r("Supporting disabled children", "applications", [29, 31], "Supporting disabled children means adapting environments, communication, expectations, and access while respecting dignity.", "The child should not be treated as a problem to normalize; barriers and supports matter.", "A visual schedule can give an autistic child more independence rather than less.", "Support should increase participation and agency.", 3, 0.84, 0.34),
      r("Adolescence bridge", "advanced-horizons", [26, 16], "Adolescence brings rapid changes in identity, peers, sleep timing, autonomy, risk assessment, and future planning.", "Earlier habits of trust, repair, boundaries, and conversation become the platform for later independence.", "A child who practiced small choices is better prepared for larger teen decisions.", "Teen development is a bridge from protection toward guided independence.", 4, 0.72, 0.2),
      r("Advocacy with professionals", "applications", [29, 39], "Advocacy means bringing observations, questions, records, and respect into conversations with clinicians, teachers, or specialists.", "Clear examples help professionals understand patterns without caregivers needing to diagnose alone.", "A note listing when speech frustration happens can make an appointment more useful.", "Caregivers can be informed partners without replacing professionals.", 3, 0.8, 0.3),
      r("Building a family learning map", "bridges", [34, 46, 49], "A family learning map connects development, safety, emotion, routines, culture, and professional guidance into one usable picture.", "The map should reduce shame by asking what skill, support, or boundary is needed next.", "After a hard week, the map may point to sleep, caregiver rest, and transition routines rather than blame.", "Good caregiving maps turn scattered advice into compassionate next steps.", 3, 0.9, 0.28)
    ]
  },
  {
    id: "personal-investments-for-total-beginners",
    short: "invest",
    title: "Personal Investments for Total Beginners",
    description: "A no-hype beginner map of saving, investing, risk, diversification, accounts, behavior, scams, and professional boundaries. Account and tax examples (such as Roth and traditional accounts) are US-focused; other jurisdictions have different rules.",
    audience: "Adults learning investment basics before making individualized decisions",
    level: "Beginner",
    purpose: "Explain investment concepts without recommendations, urgency, fake certainty, or personalized financial advice.",
    accent_color: "#427846",
    boundary: "Educational only. Investing, taxes, insurance, debt, and retirement choices depend on personal circumstances, jurisdiction, risk capacity, and current law; consult qualified professionals for advice.",
    source_refs: [
      source("invest-sec-investor", "Investor.gov", "US Securities and Exchange Commission", "https://www.investor.gov/", "Investor education, risk, products, fees, and fraud awareness."),
      source("invest-finra", "FINRA Investors", "Financial Industry Regulatory Authority", "https://www.finra.org/investors", "Brokerage, product, risk, and scam education."),
      source("invest-cfpb-saving", "Saving and budgeting", "Consumer Financial Protection Bureau", "https://www.consumerfinance.gov/consumer-tools/saving/", "Saving, budgeting, and consumer financial education."),
      source("invest-irs-retirement", "Retirement Plans", "Internal Revenue Service", "https://www.irs.gov/retirement-plans", "US retirement account tax information at a high level."),
      source("invest-sec-alerts", "Investor Alerts and Bulletins", "US Securities and Exchange Commission", "https://www.sec.gov/resources-for-investors/investor-alerts-bulletins", "Fraud, risk, and investor alert education.")
    ],
    rows: [
      r("Saving versus investing", "foundations", [], "Saving protects near-term purchasing power and access, while investing accepts risk in pursuit of future growth.", "Confusing the two can expose rent money to market swings or leave long-term goals stuck in low-return cash.", "An emergency fund and a retirement portfolio serve different jobs even if both are money.", "Match the tool to the time horizon and purpose.", 1, 1, 1),
      r("Emergency fund", "foundations", [1], "An emergency fund is accessible money for unexpected expenses or income disruption.", "It reduces the need to sell long-term investments at bad times or take on high-cost borrowing when an unplanned expense collides with a market downturn.", "A car repair paid from savings does not force a stock sale during a market drop.", "Financial resilience starts with liquidity for surprises.", 1, 0.96, 0.95),
      r("Risk", "foundations", [1], "Investment risk is the possibility that outcomes differ from what you need or expect.", "It includes price swings, inflation, default, liquidity, concentration, behavior, taxes, and fraud, not only losing money today.", "A safe-looking account can still lose purchasing power if inflation is higher than its yield.", "Risk is multi-dimensional and should be named precisely.", 1, 0.98, 0.96),
      r("Return", "foundations", [3], "Return is the gain or loss from an investment after income, price changes, and costs.", "Expected return is uncertain compensation for taking some kind of risk, not a promise.", "A stock may pay dividends and rise in price, but either part can disappoint.", "Return is what you hope to earn for accepting uncertainty.", 1, 0.92, 0.9),
      r("Time horizon", "foundations", [1, 3], "Time horizon is when the money is expected to be needed and how flexible or fixed that date actually is, since a firm deadline changes what risks are tolerable.", "Longer horizons can absorb some volatility better, while short horizons usually need stability and liquidity.", "Money for next semester's tuition has a different horizon than money for retirement decades away.", "Time horizon determines how much uncertainty is tolerable.", 1, 0.96, 0.94),
      r("Inflation", "foundations", [1], "Inflation reduces purchasing power over time, meaning the same amount of money buys fewer goods and services as prices for a typical basket of items rise.", "Investing often aims to outpace inflation, but higher expected returns usually come with more uncertainty.", "A bank balance that grows 1 percent while prices rise 4 percent buys less in real terms.", "The goal is future purchasing power, not just a bigger number.", 1, 0.92, 0.88),
      r("Compounding", "mechanisms", [4, 5], "Compounding happens when investment returns are reinvested and begin earning further returns of their own, so growth builds on growth rather than on the original amount alone.", "Time, contribution consistency, costs, taxes, and volatility all affect how compounding works in practice.", "Interest left in an account can become part of the next period's interest calculation.", "Compounding rewards time and consistency, but it is not magic.", 2, 0.94, 0.88),
      r("Diversification", "foundations", [3], "Diversification spreads exposure across investments so one failure does not dominate the whole plan.", "It cannot remove market-wide risk, but it can reduce avoidable concentration risk.", "Owning many companies through a broad fund is less dependent on one employer or industry.", "Diversification is humility turned into portfolio design.", 1, 0.98, 0.9),
      r("Asset allocation", "mechanisms", [3, 5, 8], "Asset allocation is the mix of broad asset types such as stocks, bonds, and cash.", "It is a major driver of risk and expected return because each asset type behaves differently across conditions.", "A young long-term investor and a near-term home buyer may need very different stock and cash mixes.", "Allocation connects goals and risk capacity to portfolio structure.", 2, 0.9, 0.8),
      r("Stocks", "foundations", [3, 4], "A stock represents ownership in a company and a claim on uncertain future business value.", "Stock returns can be high because owners bear volatility, competition, and business failure risk.", "Buying shares of a company means your outcome depends partly on its profits and market expectations.", "Stocks are ownership claims, not guaranteed savings accounts.", 2, 0.9, 0.76),
      r("Bonds", "foundations", [3, 4], "A bond is a loan-like security where an issuer promises payments under defined terms.", "Bond risk depends on interest rates, inflation, credit quality, maturity, and liquidity.", "A government bond and a risky corporate bond may both pay interest but carry different risks.", "Bonds are promises with terms and risks.", 2, 0.88, 0.76),
      r("Cash", "foundations", [1, 2], "Cash and cash-like accounts prioritize stability and access over long-term growth.", "They are useful for near-term needs but may lose purchasing power after inflation.", "A high-yield savings account can be appropriate for emergency money even if stocks might earn more over decades.", "Cash is a liquidity tool, not a complete long-term plan.", 1, 0.86, 0.8),
      r("Index funds", "applications", [8, 10], "An index fund seeks to track a market index rather than pick individual winners.", "It offers broad diversification and typically low costs, but it still carries the risk of the market it tracks.", "A total stock market index fund rises and falls with the broad stock market.", "Indexing buys a market slice instead of a prediction about one winner.", 2, 0.9, 0.66),
      r("ETFs and mutual funds", "mechanisms", [13], "ETFs and mutual funds pool many investors' money together so each investor owns a proportional share of a diversified basket of stocks, bonds, or other securities.", "They differ in trading mechanics, pricing, taxes, and minimums, so the wrapper matters even when holdings are similar.", "An S&P 500 ETF and mutual fund may hold similar stocks but trade differently during the day.", "Funds are baskets; the wrapper shapes how you buy and hold them.", 2, 0.82, 0.56),
      r("Fees", "mechanisms", [4], "Fees are the costs paid to own, trade, manage, advise on, or administer investments, and they are charged whether or not the underlying investment performs well.", "Small-looking percentages can compound against the investor over long periods, since money paid out in fees each year no longer remains invested to grow further.", "A 1 percent annual advisory fee may seem tiny but can consume a meaningful share of decades of returns.", "Costs are one of the few investment variables you can often see clearly.", 2, 0.9, 0.7),
      r("Expense ratios", "applications", [14, 15], "An expense ratio is the annual operating cost of a fund expressed as a percentage of assets.", "It is deducted directly inside the fund's reported returns, so investors rarely see a separate bill and can easily overlook how much the cost is reducing their gains.", "A fund with a 0.05 percent expense ratio costs far less than one charging 1 percent for similar exposure.", "Expense ratios quietly reduce the return investors keep.", 2, 0.82, 0.56),
      r("Liquidity", "mechanisms", [1, 3], "Liquidity is how quickly and reliably an asset can be turned into spendable money without a major price concession.", "Illiquid assets may be valuable but unsuitable for near-term or emergency needs.", "A house can be valuable and still hard to sell quickly at a fair price.", "Liquidity is about usable access, not just value.", 2, 0.86, 0.64),
      r("Volatility", "mechanisms", [3, 10], "Volatility is the degree to which an investment's price swings up and down over time, whether daily, monthly, or across full market cycles.", "It is uncomfortable but not automatically the same as permanent loss; context and horizon matter.", "A broad stock fund may fall sharply in a month and still fit a decades-long plan.", "Volatility is movement; risk is whether movement harms your goal.", 2, 0.84, 0.58),
      r("Market timing", "misconceptions", [18], "Market timing is the attempt to move money in and out of investments right before prices rise or fall, essentially trying to predict short-term direction.", "It is hard because decisions require being right about direction, timing, taxes, costs, and re-entry under uncertainty.", "Selling after a scary headline may avoid a drop or miss a rebound, and you only know later.", "Consistently timing markets is much harder than it feels in hindsight.", 2, 0.84, 0.5),
      r("Dollar-cost averaging", "applications", [18, 19], "Dollar-cost averaging invests fixed amounts on a schedule, buying more shares when prices are lower and fewer when higher.", "It can reduce regret and automate behavior, though it is not a guarantee of better returns than investing a lump sum.", "A monthly retirement contribution buys at many different market levels.", "Scheduled investing is mainly a behavior and cash-flow tool.", 2, 0.76, 0.44),
      r("Rebalancing", "mechanisms", [9], "Rebalancing brings a portfolio back toward its target allocation after market moves.", "It controls risk drift by selling some overweight assets or directing new money to underweight assets.", "If stocks rise from 60 percent to 75 percent of a portfolio, rebalancing can restore the intended risk mix.", "Rebalancing keeps the plan from being rewritten by market movement.", 3, 0.82, 0.46),
      r("Taxable and tax-advantaged accounts", "bridges", [5], "Accounts are containers with rules; investments are what you hold inside the containers.", "Taxable and tax-advantaged accounts can hold similar assets but differ in taxes, limits, access, and reporting.", "An index fund inside a retirement account has different tax treatment than the same fund in a taxable brokerage account.", "Separate the account wrapper from the investment inside it.", 3, 0.84, 0.5),
      r("Retirement accounts at a high level", "applications", [22], "Retirement accounts are policy-created containers intended to encourage long-term saving.", "Rules about contributions, withdrawals, taxes, penalties, and eligibility are specific and can change, so primary guidance matters.", "In the United States, a traditional account defers taxes until withdrawal while a Roth account is funded with after-tax money; other countries use different retirement-account rules.", "Retirement accounts are powerful wrappers with rulebooks.", 3, 0.84, 0.48),
      r("Employer match", "applications", [23], "An employer match is extra compensation contributed when an employee contributes under plan rules.", "It can be valuable, but vesting, limits, investment choices, and cash-flow needs still matter.", "In the United States, a company might add 50 cents for each dollar an employee contributes up to a percentage of pay; matching rules and tax treatment differ in other countries.", "A match is part of compensation, not a market return.", 2, 0.82, 0.42),
      r("Brokerage accounts", "applications", [14, 22], "A brokerage account is the account that lets an investor buy, sell, and hold securities such as stocks, bonds, or funds through a licensed broker or platform.", "The account provides access, statements, trading, and custody, but it does not make investments safe by itself.", "Opening a brokerage account is like opening a toolbox; what you use it for matters.", "A brokerage is access infrastructure, not an investment plan.", 2, 0.74, 0.36),
      r("Risk tolerance versus risk capacity", "bridges", [3, 5], "Risk tolerance is emotional comfort with uncertainty, while risk capacity is the financial ability to absorb bad outcomes.", "A sound plan considers both because bravery cannot create time or cash that a goal lacks.", "Someone comfortable with volatility still should not invest next month's rent in stocks.", "Willingness and ability to take risk are different.", 2, 0.88, 0.54),
      r("Behavioral mistakes", "misconceptions", [3, 19], "Behavioral mistakes happen when fear, greed, overconfidence, or neglect override the plan.", "The damage often comes from buying high, selling low, chasing stories, or ignoring costs.", "An investor who sells every downturn may turn temporary volatility into permanent loss.", "Your behavior can matter as much as your product choice.", 2, 0.88, 0.48),
      r("Herding", "misconceptions", [27], "Herding is following what others appear to be doing instead of evaluating fit, risk, and evidence.", "Crowds can sometimes reveal useful information through collective behavior, but the same dynamic can also amplify bubbles, panics, and scams far beyond their initial size.", "A friend group all buying a hot token does not prove it belongs in your plan.", "Popularity is not proof of suitability.", 2, 0.78, 0.38),
      r("Loss aversion", "misconceptions", [27], "Loss aversion means that losing a given amount of money often feels more painful than gaining that same amount feels good, distorting how risks are weighed.", "It can make investors sell after declines, avoid useful risk, or hold losers to avoid admitting loss.", "A 10 percent drop may feel urgent even when the long-term goal has not changed.", "Emotions around loss need pre-made rules.", 2, 0.8, 0.4),
      r("Scams", "limitations", [3], "Investment scams use trust, urgency, secrecy, complexity, or guaranteed-return claims to bypass judgment.", "Fraud prevention starts by slowing down, verifying registration, understanding custody, and refusing pressure.", "A stranger promising safe monthly returns far above market rates is selling a warning sign.", "Urgency plus guaranteed riches is a danger signal.", 2, 0.94, 0.52),
      r("Fiduciary", "applications", [15], "A fiduciary is required to act in another person's best interest within the scope of the relationship.", "Not every financial professional has the same obligations, compensation model, or conflicts.", "Asking how an adviser is paid can reveal incentives behind recommendations.", "Advice quality depends partly on duties and incentives.", 3, 0.78, 0.36),
      r("Robo-advisors", "advanced-horizons", [9, 15], "Robo-advisors are automated platforms that use software and algorithms to recommend or manage investment portfolios based on the inputs a user provides.", "They can lower costs and automate rebalancing, but the output is only as appropriate as the assumptions and information entered.", "A questionnaire may not capture unstable income or upcoming major expenses.", "Automation can help execution but does not remove judgment.", 3, 0.68, 0.22),
      r("Target-date funds", "applications", [9, 23], "A target-date fund holds a diversified mix that becomes more conservative as a chosen date approaches.", "It simplifies allocation but still requires checking costs, assumptions, holdings, and whether the date matches the goal.", "A 2060 fund is generally designed for a later retirement horizon than a 2030 fund.", "Target-date funds package an allocation path, not a personalized guarantee.", 2, 0.78, 0.36),
      r("Bonds and interest rates", "mechanisms", [11, 18], "Bond prices generally move opposite interest rates because older fixed payments become more or less attractive.", "Longer-duration bonds usually react more strongly to rate changes than shorter-duration bonds.", "If new bonds pay higher interest, an older low-rate bond may need a lower price to compete.", "Bond safety depends partly on rate sensitivity.", 3, 0.82, 0.42),
      r("Credit risk in bonds", "mechanisms", [11, 34], "Credit risk in bonds is the chance that the issuer cannot make promised payments.", "Higher yields may compensate investors for taking on this risk, but an unusually high yield can also be a warning signal that the market doubts full repayment.", "A distressed company's bond may offer a high yield because investors doubt full repayment.", "Yield is not free money; it often points to risk.", 3, 0.8, 0.38),
      r("Real returns", "bridges", [4, 6], "A real return adjusts investment performance for inflation, showing growth in actual purchasing power rather than in the nominal dollar amount alone.", "It matters because goals are funded with purchasing power, not nominal account statements alone.", "A 5 percent nominal gain with 3 percent inflation is roughly a 2 percent real gain before other costs.", "Real return tells you what your money can buy.", 2, 0.82, 0.42),
      r("Concentration risk", "limitations", [8], "Concentration risk appears when too much depends on one company, sector, country, employer, or asset type.", "It can feel comfortable when the concentrated asset is familiar, but familiarity does not remove risk.", "Holding employer stock and relying on that employer for salary links job and portfolio risk.", "Too much of one thing can quietly dominate the plan.", 2, 0.86, 0.44),
      r("International diversification", "bridges", [8], "International diversification spreads exposure across economies, currencies, sectors, and political environments.", "It adds its own currency and governance risks while reducing dependence on one home market.", "A portfolio holding only domestic companies may miss industries or growth patterns elsewhere.", "Global diversification trades home comfort for broader exposure.", 3, 0.74, 0.26),
      r("Dividends", "mechanisms", [10], "Dividends are company cash distributions to shareholders, usually from profits or reserves.", "They are part of total return but not guaranteed, and a high yield can reflect a falling price or stressed business.", "A company may cut its dividend if earnings weaken.", "Dividends are cash flows, not automatic evidence of safety.", 2, 0.72, 0.3),
      r("Capital gains", "mechanisms", [10, 22], "A capital gain happens when an investment is sold for more than its purchase price.", "Tax rules, holding periods, account type, and realized versus unrealized gains affect the outcome.", "A stock can show an unrealized gain on screen before any taxable sale occurs.", "Gains matter differently before and after they are realized.", 3, 0.74, 0.3),
      r("Taxes basics boundary", "limitations", [22, 40], "Taxes can change what investors keep through income, dividends, gains, account rules, and reporting.", "Because tax law is jurisdiction-specific and changes, general education should not become personal tax advice.", "Selling a fund in a taxable account may have different consequences than selling inside a retirement account.", "Tax awareness is necessary, but individual tax decisions need current guidance.", 3, 0.84, 0.36),
      r("Insurance is not investing", "misconceptions", [1], "Insurance transfers defined risks, while investing accepts risk for potential growth.", "Some products combine features, but confusing protection with growth can hide costs and tradeoffs.", "Term life insurance and an index fund solve different problems.", "Protection products and investment products have different jobs.", 2, 0.78, 0.36),
      r("Debt payoff versus investing", "bridges", [3, 5], "Paying down debt and investing new money both affect future net worth, risk exposure, and financial flexibility, even though they can feel like separate decisions.", "The comparison depends on interest rate, tax treatment, liquidity, employer match, stress, and personal constraints.", "Paying a high-interest credit-card balance can be a clearer return than chasing uncertain investments.", "Debt decisions belong in the same map as investing decisions.", 3, 0.82, 0.42),
      r("Goals and buckets", "applications", [5], "Goals and buckets separate money by purpose, time horizon, and required certainty.", "This reduces the temptation to use one single risky portfolio for every need, since money needed soon should not be exposed to the same swings as money needed decades later.", "A travel fund, emergency fund, and retirement account can each have different investments or savings tools.", "Clear goals keep portfolios from becoming vague piles of money.", 2, 0.8, 0.44),
      r("Investment policy statement", "advanced-horizons", [9, 26], "An investment policy statement is a written rule set for goals, allocation, contributions, rebalancing, and behavior during stress.", "It is useful because calm decisions can guide future moments of fear or excitement.", "A rule to rebalance twice a year can prevent headlines from becoming the strategy.", "A written plan protects the investor from improvising under emotion.", 3, 0.78, 0.28),
      r("Reading performance charts", "applications", [4, 18], "Performance charts show selected time periods, scales, fees, benchmarks, and assumptions.", "They can educate or mislead depending on what is included and what is quietly omitted.", "A chart starting at the bottom of a crash may make returns look smoother than a full-cycle view.", "Always ask what a performance chart chose not to show.", 2, 0.78, 0.36),
      r("Past performance limits", "misconceptions", [46], "Past performance describes what already happened to an investment or fund, not what is guaranteed or even likely to happen again in the future.", "Markets change because prices already reflect expectations, competition, rates, and new information.", "A fund that beat peers for five years can still lag afterward.", "History is evidence, not a guarantee.", 2, 0.86, 0.42),
      r("Recessions and staying with a plan", "applications", [35, 45], "Recessions can bring job risk, market declines, credit stress, and emotional pressure at the same time.", "A resilient plan considers emergency cash, allocation, debt, and rules before panic arrives.", "Someone with a sufficient emergency fund may avoid selling long-term investments after losing income.", "A plan is most valuable when conditions are bad.", 3, 0.84, 0.34),
      r("When to ask a professional", "limitations", [41, 43], "Professional guidance can be important when stakes, complexity, taxes, legal issues, disability, inheritance, debt, or conflicting goals are significant.", "The goal is not to outsource all thinking but to know when general education is insufficient.", "A cross-border inheritance is not a beginner blog problem.", "Knowing the boundary of self-education is part of good financial judgment.", 2, 0.88, 0.42),
      r("A beginner's investment system", "bridges", [1, 3, 8, 26, 45], "A beginner's system connects emergency savings, time horizon, diversification, costs, behavior rules, and fraud avoidance.", "It should be boring enough to follow consistently and explicit enough in its rules to resist hype, headlines, and the pull of chasing whatever is currently popular.", "A one-page checklist can say what money is for, where it sits, how risk is limited, and when to get help.", "A simple investment system beats scattered product chasing.", 3, 0.94, 0.38)
    ]
  }
];

function r(title, category, prereq, idea, mechanism, example, takeaway, difficulty, importance, foundational) {
  return { title, category, prereq, idea, mechanism, example, takeaway, difficulty, importance, foundational };
}

function source(id, title, publisher, url, claim_scope) {
  return { id, title, publisher, url, accessed_at: CREATED_AT, claim_scope };
}

function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 54);
}

function rowText(row) {
  return `${row.title} ${row.idea} ${row.mechanism} ${row.example}`;
}

// Per-card source selection: every pack has a broad relevant baseline, plus targeted
// sources added only when a card's own text or title matches that source's scope.
// This keeps each card's source_refs an honest, auditable subset instead of the full
// pack source list, so a card only cites sources that actually speak to its content.

const ECON_BLS_TITLES = new Set(["Unemployment", "Labor markets"]);
const ECON_WORLDBANK_TITLES = new Set(["Comparative advantage", "Trade and tariffs", "Exchange rates"]);
const ECON_MACRO_TITLES = new Set([
  "Measuring output with GDP",
  "Inflation indexes",
  "Money in macroeconomics",
  "Interest rates in the economy",
  "Aggregate demand and aggregate supply",
  "Business cycles",
  "Fiscal policy",
  "Monetary policy",
  "Expectations",
  "Growth limits and environment",
  "Exchange rates"
]);

function economicsSources(row) {
  const ids = new Set(["econ-openstax"]);
  if (ECON_BLS_TITLES.has(row.title)) ids.add("econ-bls");
  if (ECON_WORLDBANK_TITLES.has(row.title)) ids.add("econ-worldbank-trade");
  if (ECON_MACRO_TITLES.has(row.title)) {
    ids.add("econ-imf-basics");
    ids.add("econ-fed-research");
  }
  return [...ids];
}

function matchesAny(text, patterns) {
  return patterns.some((pattern) => pattern.test(text));
}

const INVEST_SAVING_PATTERNS = [/\bsavings?\b/i, /\bbudget(ing)?\b/i, /\bdebt\b/i, /\bemergency fund\b/i, /\bcash[- ]flow\b/i];
const INVEST_RETIREMENT_TAX_PATTERNS = [/\bretirement\b/i, /\broth\b/i, /\bemployer match\b/i, /\bcapital gains?\b/i, /\btax(es|able|-advantaged)?\b/i];
const INVEST_FRAUD_PATTERNS = [/\bscams?\b/i, /\bfraud\b/i, /\bherding\b/i, /\bguaranteed[- ]returns?\b/i];

function investingSources(row) {
  const ids = new Set(["invest-sec-investor", "invest-finra"]);
  const text = rowText(row);
  if (matchesAny(text, INVEST_SAVING_PATTERNS)) ids.add("invest-cfpb-saving");
  if (matchesAny(text, INVEST_RETIREMENT_TAX_PATTERNS)) ids.add("invest-irs-retirement");
  if (matchesAny(text, INVEST_FRAUD_PATTERNS)) ids.add("invest-sec-alerts");
  return [...ids];
}

const CHILD_MILESTONE_PATTERNS = [/\bmilestones?\b/i, /\bdevelopments?\b/i, /\bdevelopmental\b/i];
const CHILD_NUTRITION_PATTERNS = [/\bnutrition\b/i, /\bfoods?\b/i];
const CHILD_WHO_TITLES = new Set(["Development is uneven", "Safety layers", "Illness boundaries", "Building a family learning map"]);
const CHILD_SAFE_SLEEP_TITLES = new Set(["Safe sleep"]);
const CHILD_PASSENGER_SAFETY_TITLES = new Set(["Safety layers"]);

function childrenSources(row) {
  const ids = new Set(["child-aap-healthychildren"]);
  const text = rowText(row);
  if (matchesAny(text, CHILD_MILESTONE_PATTERNS)) ids.add("child-cdc-milestones");
  if (matchesAny(text, CHILD_NUTRITION_PATTERNS)) ids.add("child-myplate");
  if (CHILD_WHO_TITLES.has(row.title)) ids.add("child-who-health");
  if (CHILD_SAFE_SLEEP_TITLES.has(row.title)) ids.add("child-cdc-safe-sleep");
  if (CHILD_PASSENGER_SAFETY_TITLES.has(row.title)) ids.add("child-cdc-passenger-safety");
  return [...ids];
}

const BANK_MONETARY_PATTERNS = [
  /\bmonetary policy\b/i,
  /\bcentral banks?\b/i,
  /\bpolicy rates?\b/i,
  /\binterest rates?\b/i,
  /\bopen market\b/i,
  /\breserves?\b/i,
  /\bstanding facilit\w*\b/i,
  /\bforward guidance\b/i,
  /\bquantitative easing\b/i,
  /\byield curves?\b/i,
  /\binflation\b/i,
  /\bdeflation\b/i
];
const BANK_PAYMENTS_PATTERNS = [/\bpayments?\b/i, /\bsettlement\b/i, /\bclearing\b/i, /\binterbank\b/i];
const BANK_CAPITAL_PATTERNS = [
  /\bcapital\b/i,
  /\bsolvency\b/i,
  /\bstress tests?\b/i,
  /\bmacroprudential\b/i,
  /\bleverage\b/i,
  /\bsecuritization\b/i,
  /\bshadow banking\b/i,
  /\bfinancial stability\b/i
];
const BANK_DEPOSIT_INSURANCE_PATTERNS = [/\bdeposit insurance\b/i, /\bbank runs?\b/i];
const BANK_AML_PATTERNS = [/\bmoney laundering\b/i];
const BANK_RESOLUTION_PATTERNS = [/\bcrisis resolution\b/i];
const BANK_CORRESPONDENT_PATTERNS = [/\bcorrespondent banking\b/i];
const BANK_CBDC_PATTERNS = [/\bcentral bank digital currenc\w*\b/i, /\bcbdc\b/i];
const BANK_CONSUMER_PATTERNS = [/\bconsumer protection\b/i];

function bankingSources(row) {
  const ids = new Set();
  const text = rowText(row).replace(/-/g, " ");
  if (matchesAny(text, BANK_MONETARY_PATTERNS)) ids.add("bank-fed-monetary-policy");
  if (matchesAny(text, BANK_PAYMENTS_PATTERNS)) {
    ids.add("bank-fed-payments");
    ids.add("bank-bis-cpmi");
  }
  if (matchesAny(text, BANK_CAPITAL_PATTERNS)) ids.add("bank-basel");
  if (matchesAny(text, BANK_DEPOSIT_INSURANCE_PATTERNS)) ids.add("bank-fdic-insurance");
  if (matchesAny(text, BANK_AML_PATTERNS)) ids.add("bank-fincen-aml");
  if (matchesAny(text, BANK_RESOLUTION_PATTERNS)) ids.add("bank-fdic-resolutions");
  if (matchesAny(text, BANK_CORRESPONDENT_PATTERNS)) ids.add("bank-bis-correspondent");
  if (matchesAny(text, BANK_CBDC_PATTERNS)) ids.add("bank-fed-cbdc");
  if (matchesAny(text, BANK_CONSUMER_PATTERNS)) ids.add("bank-cfpb-consumer");
  // Every banking card should ground its systems-map claims in at least one declared
  // source; foundational cards without a stronger topical match fall back to the
  // Fed's payments overview, since money and settlement are common to all of them.
  if (ids.size === 0) ids.add("bank-fed-payments");
  return [...ids];
}

const PACK_SOURCE_SELECTORS = {
  econ: economicsSources,
  bank: bankingSources,
  child: childrenSources,
  invest: investingSources
};

function sourcesForRow(pack, row) {
  const selector = PACK_SOURCE_SELECTORS[pack.short];
  if (!selector) throw new Error(`No source selector registered for pack "${pack.short}".`);
  const ids = selector(row);
  const declared = new Set(pack.source_refs.map((sourceRef) => sourceRef.id));
  for (const id of ids) {
    if (!declared.has(id)) throw new Error(`Card "${row.title}" references undeclared source "${id}".`);
  }
  return ids;
}

function materializeCards(pack) {
  const ids = pack.rows.map((row, index) => `${pack.short}-${String(index + 1).padStart(2, "0")}-${slugify(row.title)}`);
  // Reverse index of the real prerequisite graph: for each row number (1-based), which
  // later rows actually declare it as a prerequisite. This drives "prepares-for" edges
  // instead of blindly pointing at the next row in the list.
  const dependentsOf = new Map();
  pack.rows.forEach((row, index) => {
    for (const prereqNumber of row.prereq) {
      const dependents = dependentsOf.get(prereqNumber) ?? [];
      dependents.push(index);
      dependentsOf.set(prereqNumber, dependents);
    }
  });

  return pack.rows.map((row, index) => {
    const prior = [...new Set(row.prereq)].map((number) => ids[number - 1]);
    const connections = [];
    const usedTargets = new Set();
    for (const id of prior) {
      if (usedTargets.has(id)) continue;
      usedTargets.add(id);
      connections.push({ type: "prerequisite", card_id: id, label: `Builds on ${titleForId(pack, ids, id)}.` });
    }
    for (const dependentIndex of dependentsOf.get(index + 1) ?? []) {
      const id = ids[dependentIndex];
      if (usedTargets.has(id)) continue;
      usedTargets.add(id);
      connections.push({ type: "prepares-for", card_id: id, label: `Prepares for ${pack.rows[dependentIndex].title}.` });
    }
    return {
      id: ids[index],
      title: row.title,
      core_idea: [row.idea, row.mechanism],
      example: row.example,
      key_takeaway: row.takeaway,
      connections,
      difficulty: row.difficulty,
      importance: row.importance,
      foundational_priority: row.foundational,
      category: row.category,
      prerequisites: prior,
      source_refs: sourcesForRow(pack, row),
      media: null,
      review_prompts: [
        {
          kind: "recall",
          prompt: `In your own words, explain "${row.title}" and name one way someone could misunderstand it.`,
          answer_hint: row.takeaway
        },
        {
          kind: "application",
          prompt: `Look at the example for "${row.title}". What detail does it show that the definition alone would miss?`,
          answer_hint: row.example
        }
      ],
      boundary_note: pack.boundary
    };
  });
}

function titleForId(pack, ids, id) {
  const index = ids.indexOf(id);
  return index >= 0 ? pack.rows[index].title : id;
}

function curriculumMap(pack, cards) {
  const categories = Object.entries(CATEGORY_NOTES).map(([id, note]) => ({
    id,
    note,
    count: cards.filter((card) => card.category === id).length,
    cards: cards.filter((card) => card.category === id).map((card) => card.id)
  }));
  const edges = cards.flatMap((card) => card.prerequisites.map((from) => ({ from, to: card.id, relationship: "prerequisite" })));
  return {
    schema_version: "knowledge-cards.curriculum-map.v1",
    pack_id: pack.id,
    categories,
    prerequisite_graph: { nodes: cards.map((card) => card.id), edges },
    difficulty_distribution: countBy(cards, (card) => `difficulty-${card.difficulty}`),
    source_policy: pack.source_refs.map((sourceRef) => sourceRef.id),
    bias_safety_review: `${pack.title} uses educational boundaries, official or educational source families, no individualized advice, no fabricated citations, and no engagement metrics as mastery signals.`,
    progression_note: "Foundations are introduced early; mechanisms, applications, misconceptions, limitations, bridges, and advanced horizons are interleaved after prerequisites become available."
  };
}

function detectPrerequisiteCycles(cards) {
  const byId = new Map(cards.map((card) => [card.id, card]));
  const visiting = new Set();
  const resolved = new Set();
  const cycles = [];
  function visit(id, path) {
    if (visiting.has(id)) {
      const start = path.indexOf(id);
      cycles.push([...path.slice(start), id]);
      return;
    }
    if (resolved.has(id)) return;
    visiting.add(id);
    for (const prereqId of byId.get(id)?.prerequisites ?? []) visit(prereqId, [...path, id]);
    visiting.delete(id);
    resolved.add(id);
  }
  for (const card of cards) visit(card.id, []);
  return cycles;
}

function validationReport(pack, cards) {
  const cycles = detectPrerequisiteCycles(cards);
  return {
    schema_version: "knowledge-cards.validation-report.v2",
    pack_id: pack.id,
    review_date: CONTENT_REVIEW_DATE,
    categories: Object.keys(CATEGORY_NOTES).map((category) => ({ id: category, count: cards.filter((card) => card.category === category).length })),
    card_count: cards.length,
    automated_checks: {
      description: "Checks below are computed by tools/generate-content.mjs and tools/validate-packs.mjs at build time. They confirm structure, not factual correctness.",
      unique_card_ids: cards.length === new Set(cards.map((card) => card.id)).size ? "pass" : "fail",
      prerequisite_ids_resolve: cards.every((card) => card.prerequisites.every((id) => cards.some((other) => other.id === id))) ? "pass" : "fail",
      prerequisite_graph_acyclic: cycles.length === 0 ? "pass" : "fail",
      connections_have_no_duplicate_targets: cards.every((card) => card.connections.length === new Set(card.connections.map((connection) => connection.card_id)).size) ? "pass" : "fail",
      core_idea_entries_meet_min_length: cards.every((card) => card.core_idea.every((entry) => entry.length >= 80)) ? "pass" : "fail",
      source_refs_reference_declared_sources: cards.every((card) => card.source_refs.every((id) => pack.source_refs.some((sourceRef) => sourceRef.id === id))) ? "pass" : "fail",
      category_coverage: Object.keys(CATEGORY_NOTES).every((category) => cards.some((card) => card.category === category)) ? "pass" : "fail"
    },
    prerequisite_cycles: cycles,
    editorial_review: {
      status: "source-aware editorial pass completed",
      reviewed_at: CONTENT_REVIEW_DATE,
      scope: "Each card's source_refs were chosen to match that specific card's topic rather than citing every pack source on every card, and card text was drafted and read against the scope of its declared sources.",
      limitation: "Automated checks above verify structure only (ids, cycles, lengths, category coverage, source-reference resolution). They cannot prove that any sentence is factually correct, that a cited source actually supports every claim on the card, or that no relevant nuance was omitted. Confirming claim-level accuracy requires ongoing human subject-matter and source review; passing the automated checks above is not evidence of that review."
    },
    duplicate_concepts_check: "Not automated. No tooling currently detects overlapping or duplicated concepts across cards; this would require editorial reading, not software comparison.",
    unsupported_claims_check: "Not automated. Whether a claim is adequately supported by its declared sources is an editorial judgment, not something tools/validate-packs.mjs or this generator can verify.",
    safety_review: pack.boundary,
    validation_summary: "Generated from explicit authored concept rows, materialized as static JSON, then checked by tools/validate-packs.mjs for the automated_checks above. See editorial_review for what human review has and has not covered."
  };
}

function countBy(items, keyFn) {
  const counts = {};
  for (const item of items) counts[keyFn(item)] = (counts[keyFn(item)] ?? 0) + 1;
  return counts;
}

function stableJson(value) {
  return `${JSON.stringify(sortKeys(value), null, 2)}\n`;
}

function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, sortKeys(item)]));
  }
  return value;
}

async function writePack(pack) {
  if (pack.rows.length !== 50) throw new Error(`${pack.id} has ${pack.rows.length} rows, expected 50.`);
  const packDir = path.join(ROOT, "content", "packs", pack.id);
  const cardsDir = path.join(packDir, "cards");
  const mediaDir = path.join(packDir, "media");
  await fs.rm(packDir, { recursive: true, force: true });
  await fs.mkdir(cardsDir, { recursive: true });
  await fs.mkdir(mediaDir, { recursive: true });
  const cards = materializeCards(pack);
  const cardsDocument = {
    schema_version: "knowledge-cards.cards.v1",
    pack_id: pack.id,
    source_refs: pack.source_refs,
    cards
  };
  await fs.writeFile(path.join(cardsDir, "cards.json"), stableJson(cardsDocument), "utf8");
  await fs.writeFile(path.join(packDir, "curriculum-map.json"), stableJson(curriculumMap(pack, cards)), "utf8");
  await fs.writeFile(path.join(packDir, "validation-report.json"), stableJson(validationReport(pack, cards)), "utf8");
  const checksum = await computeContentChecksum(packDir, ["cards/cards.json"]);
  const manifest = {
    schema_version: "knowledge-cards.pack-manifest.v1",
    id: pack.id,
    title: pack.title,
    description: pack.description,
    language: "en",
    audience: pack.audience,
    level: pack.level,
    purpose: pack.purpose,
    content_version: CONTENT_VERSION,
    card_count: 50,
    ordered_content_files: ["cards/cards.json"],
    optional_media_root: "media",
    authors: ["Knowledge Cards editorial build"],
    provenance: "Authored as static educational content for the compiled Knowledge Cards implementation.",
    source_policy: "Use declared official, educational, or primary guidance source families; do not invent citations or imply individualized advice.",
    license: "CC-BY-4.0 for app example content",
    accent_color: pack.accent_color,
    content_checksum: checksum,
    created_at: CREATED_AT,
    updated_at: CREATED_AT,
    curriculum_map_path: "curriculum-map.json",
    validation_report_path: "validation-report.json"
  };
  await fs.writeFile(path.join(packDir, "manifest.json"), stableJson(manifest), "utf8");
}

for (const pack of packs) await writePack(pack);
const result = await validateAllPacks({ writeIndex: true });
if (!result.ok) {
  console.error(result.errors.join("\n"));
  process.exitCode = 1;
} else {
  const digest = crypto.createHash("sha256").update(JSON.stringify(result.index)).digest("hex").slice(0, 12);
  console.log(`Generated ${result.index.packs.length} packs and ${result.index.packs.reduce((sum, pack) => sum + pack.card_count, 0)} cards. Index ${digest}.`);
}
