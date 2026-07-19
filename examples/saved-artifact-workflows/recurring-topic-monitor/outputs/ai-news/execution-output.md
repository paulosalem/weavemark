# 1. Monitor snapshot

**Topic:** LLM and generative AI product, research, safety, policy, legal, and developer-tooling news
**Run date:** 2026-07-18
**Cadence / lookback:** Weekly; intended lookback is roughly 2026-07-11 through 2026-07-18, global scope.
**Mode:** News, source-grounded, practical/technical audience.

**Actual search/crawl coverage:** Used the bound tools before synthesis. I ran searches across product/model releases, AI safety/evaluation, regulation/legal, developer tooling/open source, benchmarks/independent analysis, and official vendor release notes. I crawled primary and reporting pages from OpenAI, Anthropic, Capital One, GitHub, VentureBeat, the International Publishers Association, and the European Commission. The 30-call search/crawl budget was exhausted before all selected follow-up crawls completed.

**Source families used:**

- **Primary/vendor:** OpenAI release notes; OpenAI Help Center; Anthropic announcement; Capital One announcement; GitHub repository.
- **Independent/reporting:** VentureBeat article on VulnHunter.
- **Industry/legal advocacy:** International Publishers Association post summarizing the Google/Gemini copyright complaint.
- **Policy/regulatory:** European Commission GPAI Code page was crawled but proved stale for this week.
- **Search-only leads:** CNBC/China Daily/Moonshot Kimi K3, Reuters Indonesia copyright-law rewrite, TechCrunch/Guardian Google lawsuit coverage, benchmark leaderboard sites.

**Context status:** `limited`
A bounded digest is possible, but the run is **not comprehensive enough for confident global ranking**. Several potentially important leads were snippet-only or inaccessible before the budget was exhausted, especially Moonshot AI’s reported Kimi K3 launch, Reuters legal/regulatory reporting, and independent benchmark analysis.

**Evidence grade:** **adequate**
- **Strongest evidence:** Crawled primary sources for OpenAI, Anthropic, Capital One, GitHub, and plaintiff-side legal claims against Google.
- **Weakest evidence:** Model-release and policy leads found only in snippets, plus an inaccessible Reuters crawl.
- **Main gap:** Lack of crawled primary/independent evidence for reported Moonshot Kimi K3 details and for Google’s response to the Gemini copyright lawsuit.
- **Action posture:** **Act on tactical product/dev-tool items; investigate before making strategic model/vendor or legal-policy conclusions.**

---

# 2. Top findings

## 1. OpenAI expanded ChatGPT enterprise administration, search, EKM support, and EEA WhatsApp availability

**Status:** Material update

### What happened

OpenAI’s release notes and Enterprise/Edu help-center release notes show several ChatGPT product updates during the lookback window:

- **July 16, 2026:** “Expanded Admin APIs and analytics” for ChatGPT Enterprise and Edu. Admins can create and manage workspace-scoped Admin keys in the Global Admin Console for supported ChatGPT and Codex administration APIs, including group management, Spend Controls API, cost reporting, and analytics. OpenAI says Admin keys cannot be used for model inference.
- **July 15, 2026:** Apps with sync now support Enterprise and Edu workspaces with **Enterprise Key Management — EKM** enabled.
- **July 15, 2026:** ChatGPT custom instructions limit increased to **5,000 characters**, up from **1,500**, for Plus, Pro, Enterprise, Business, and Education users.
- **July 14, 2026:** ChatGPT search now covers chats, projects, images, and documents across web, iOS, and Android, available globally on all ChatGPT plans.
- **July 13, 2026:** ChatGPT returned to WhatsApp in the **European Economic Area — EEA**, using the verified 1-800-CHATGPT contact at **+1-800-242-8478**, with optional account linking and usage limits.

### Why it matters for a technical AI reader

This is less about a new frontier model and more about OpenAI making ChatGPT operationally easier to govern and use inside organizations. The Admin APIs and analytics matter for enterprise AI platform teams because they move ChatGPT/Codex administration closer to programmable identity, spend, and usage governance. EKM compatibility for apps with sync is also important for regulated organizations that previously avoided sync features because of encryption-key requirements.

The cross-content search feature is practically useful but raises expected enterprise questions: what is indexed, how permissions are enforced, how deleted files/chats are handled, and whether search results expose project/file metadata.

### What changed

OpenAI’s enterprise surface is moving from a chat product toward a governed workspace/agent platform. Some context from the same help-center page, dated **July 9, 2026**, is just outside the strict lookback but relevant: OpenAI introduced **ChatGPT Work**, **ChatGPT Sites**, a new desktop app combining Chat, Work, and Codex, and announced **Atlas** deprecation scheduled for **August 9, 2026**. I treat those July 9 items as context, not this week’s main change.

### Date and timing basis

- Publication/update evidence: crawled OpenAI release notes and OpenAI Help Center.
- Relevant dates: **July 13, July 14, July 15, and July 16, 2026**.

### Strongest sources

- **Primary:** OpenAI Release Notes — `https://openai.com/products/release-notes/` — crawled.
- **Primary:** “ChatGPT Enterprise & Edu - Release Notes” — `https://help.openai.com/en/articles/10128477-chatgpt-enterprise-edu-release-notes` — crawled.

**Independent/skeptical source:** None crawled for this item.

### Reasoning trace

| Step | Claim or inference | Evidence or basis | Confidence |
|---|---|---|---|
| 1 | OpenAI shipped enterprise/admin/search/availability updates this week. | Crawled OpenAI release notes and Enterprise/Edu release notes dated July 13–16, 2026. | High |
| 2 | The updates matter for governance and practical enterprise deployment. | Admin keys, analytics, EKM support, and cross-surface search directly affect enterprise AI operations. | Medium-high |
| 3 | Caveat: benefits and risks are mostly vendor-stated; no independent audit was crawled. | Source family is OpenAI only. | High |

### Confidence and evidence grade

**Confidence:** High that the updates were announced; medium on practical impact until admins test behavior.
**Evidence grade:** Adequate.

### Caveat / missing evidence

No independent confirmation or practitioner testing was crawled. The exact API scope, audit logging behavior, permission boundaries, and search-index retention details need verification in docs or tenant testing.

### Next action

If you administer ChatGPT Enterprise/Edu, test:

1. Admin-key creation and least-privilege permissions.
2. Whether Admin keys are logged and revocable as expected.
3. Whether cross-chat/project/file search respects workspace permissions and deletion policies.
4. Whether EKM-enabled sync apps meet your data-governance requirements.

---

## 2. Capital One open-sourced VulnHunter, an agentic AI code-security tool built around attacker-first analysis and falsification

**Status:** New

### What happened

Capital One announced **VulnHunter** on **July 16, 2026**, describing it as an open-source, agentic AI security tool that analyzes source code from an attacker’s perspective, maps prospective exploit paths, and proposes targeted remediations. The project is available on GitHub under the **Apache License 2.0**.

Capital One’s announcement says VulnHunter has three notable ideas:

1. **Falsification engine:** After surfacing a finding, it tries to disprove its own exploit argument before sending the issue to developers.
2. **Attacker-first forward analysis:** It starts from attacker-accessible entry points such as APIs, network messages, or file uploads, then reasons forward through code.
3. **Evidence-backed remediation modeling:** It gathers supporting evidence and proposes targeted code changes for review.

The GitHub repository describes VulnHunter as “From pattern-matching to provability” and says it is built and optimized for **Claude Opus** running in **Claude Code**. Capital One’s announcement specifies **Claude Opus 4.8** and a working **Claude Code** environment.

### Why it matters for a technical AI reader

This is a concrete developer-tooling release, not generic AI-security commentary. If the approach works, it targets a major problem in static analysis: high false-positive rates. The self-falsification design is practically interesting because it attempts to make an LLM agent challenge its own vulnerability claim before creating developer work.

It is also a good example of the emerging dependency between AI security tools and frontier coding/reasoning models. VulnHunter may be open source, but useful operation appears to require access to a specific high-end model class and coding harness.

### What changed

The tool moved from internal Capital One use to public open-source availability. Capital One claims it ran VulnHunter across thousands of internal repositories before release, but that is a vendor claim and was not independently validated in the crawled sources.

### Date and timing basis

- **Capital One announcement:** July 16, 2026.
- **VentureBeat coverage:** July 17, 2026.
- **GitHub repository:** crawled during this run; visible repository metadata showed public repo, stars/forks, files, Apache-2.0 license, and README.

### Strongest sources

- **Primary:** Capital One, “Announcing VulnHunter” — `https://www.capitalone.com/tech/open-source/announcing-vulnhunter/` — crawled.
- **Primary repository:** GitHub `capitalone/VulnHunter` — `https://github.com/capitalone/vulnhunter` — crawled.
- **Independent/reporting:** VentureBeat, “Capital One releases VulnHunter, an open-source AI tool that finds software flaws before hackers do” — `https://venturebeat.com/technology/capital-one-releases-vulnhunter-an-open-source-ai-tool-that-finds-software-flaws-before-hackers-do` — crawled.

### Reasoning trace

| Step | Claim or inference | Evidence or basis | Confidence |
|---|---|---|---|
| 1 | Capital One released VulnHunter as open source. | Crawled Capital One announcement and GitHub repository. | High |
| 2 | It matters because it applies agentic reasoning to vulnerability triage and remediation. | Capital One’s technical description and GitHub README describe attacker-first analysis, falsification, and remediation. | Medium-high |
| 3 | Caveat: real-world effectiveness is unproven outside Capital One’s own claims. | No independent benchmark or third-party audit was crawled. | High |

### Confidence and evidence grade

**Confidence:** High that the release happened; medium on security efficacy.
**Evidence grade:** Strong for release facts; adequate for claimed capabilities.

### Caveat / missing evidence

The strongest caveat is that Capital One’s validation claims are internal. The repository itself also warns that VulnHunter performs dual-use cybersecurity work and may trigger Anthropic cyber safeguards unless users are enrolled in Anthropic’s Cyber Verification Program. That dependency may limit adoption and reproducibility.

### Next action

Security engineers should clone only into a controlled test environment and evaluate on known-vulnerable codebases before production use. Verify:

- false-positive/false-negative behavior versus your current SAST tools;
- prompt/data leakage risks when sending code to Claude;
- compatibility with your model provider and cyber-safeguard requirements;
- whether generated remediations compile and preserve behavior.

---

## 3. Anthropic launched Claude for Teachers, a free US K-12 educator offering with standards/curriculum connectors and privacy commitments

**Status:** New

### What happened

Anthropic announced **Claude for Teachers** on **July 14, 2026**. The offering gives verified **K-12 educators in the US** free access to premium Claude capabilities, teaching skills, and a connection to **Learning Commons**, which Anthropic says maps academic standards across all 50 states and underlying learning competencies.

Anthropic lists integrations or ecosystem connections including:

- ASSISTments
- Brisk Teaching
- Canva Education
- Coteach
- Diffit
- Eedi
- MagicSchool
- Snorkl
- TeachFX

Anthropic says Claude for Teachers includes **Claude Code** and **Cowork**, and gives examples such as analyzing class data, planning instruction, and scheduling recurring tasks.

Anthropic also says:

- Claude for Teachers is for educators only and is consistent with Claude’s **18-and-over policy**.
- Data shared in Claude for Teachers is **not used for model training purposes**.
- Student information is protected by a K-12 Data Processing Addendum written to comply with **FERPA**.
- Anthropic is working with the **American Federation of Teachers** on safety and privacy principles.
- It is releasing an open-source repository of teaching skills at `https://github.com/anthropics/k12-teacher-skills`.
- It will pilot an evaluation in the **Detroit Public Schools Community District**.

### Why it matters for a technical AI reader

This is a concrete vertical deployment of a general-purpose LLM into a regulated, sensitive domain. It matters because Anthropic is bundling the model with curriculum standards, workflow skills, connectors, and data-privacy commitments rather than just offering a generic chatbot.

For builders, it is a signal that AI education products are moving toward domain-specific skills, connectors, and evaluation claims. For safety/privacy reviewers, it is a live test case for student-data handling, FERPA alignment, teacher-only access, and whether AI-generated instructional materials are pedagogically reliable.

### What changed

Anthropic moved from general education positioning to a US K-12 teacher-specific product with free access for verified educators and a stated sign-up window: **sign up by June 30, 2027, for a full year of access**.

### Date and timing basis

- **July 14, 2026** publication date on crawled Anthropic announcement.

### Strongest sources

- **Primary:** Anthropic, “Introducing Claude for Teachers” — `https://www.anthropic.com/news/claude-for-teachers` — crawled.

**Independent/skeptical source:** None crawled for the product launch. Anthropic itself links to research and partners, but those were not crawled in this run.

### Reasoning trace

| Step | Claim or inference | Evidence or basis | Confidence |
|---|---|---|---|
| 1 | Anthropic launched Claude for Teachers for verified US K-12 educators. | Crawled Anthropic announcement dated July 14, 2026. | High |
| 2 | It matters because it embeds LLMs into education workflows with curriculum and student-data implications. | The product includes standards/curriculum connectors, class-data analysis examples, privacy claims, and district evaluation plans. | Medium-high |
| 3 | Caveat: efficacy and privacy claims are not independently verified here. | Only Anthropic’s announcement was crawled. | High |

### Confidence and evidence grade

**Confidence:** High on launch facts; medium on educational impact and privacy efficacy.
**Evidence grade:** Adequate.

### Caveat / missing evidence

No independent evaluation of Claude for Teachers’ instructional quality, bias, privacy controls, or FERPA implementation was crawled. The Detroit pilot is prospective; it does not yet establish impact.

### Next action

Educators and district technologists should verify:

- the actual teacher-verification process;
- FERPA/DPA terms and data-retention settings;
- whether student PII is required for useful workflows;
- alignment quality against local standards;
- whether the open-source teaching skills can be inspected and adapted.

---

## 4. Publishers and authors filed a putative class action against Google over alleged Gemini training on copyrighted works

**Status:** Material legal update

### What happened

The International Publishers Association reported on **July 14, 2026** that **Hachette Book Group, Cengage Learning Inc., Elsevier Inc., and author Scott Turow** filed a putative class action lawsuit against Google on **July 10, 2026**. The complaint alleges willful infringement of millions of textual works to develop Google’s **Gemini** large language models.

The IPA post summarizes allegations that Google:

- copied books and journal articles obtained for limited purposes in Google Books and other services;
- downloaded unauthorized web scrapes, including allegedly from pirate sources and behind paywalls;
- copied works multiple times to train Gemini;
- stripped copyright management information;
- deployed a service that allegedly generates substitutes for original works.

The post links to the full complaint PDF hosted by the Association of American Publishers.

### Why it matters for a technical AI reader

This is part of the legal pressure shaping generative AI training data. If publishers succeed, it could affect model-training practices, licensing markets, dataset documentation, opt-out mechanisms, and indemnity terms for enterprise AI customers.

For developers and buyers, the practical question is whether a model provider can document training-data provenance and legal risk well enough for regulated or IP-sensitive use cases.

### What changed

The material change is the filing of a new publisher/author suit against Google, distinct from but related to broader generative-AI copyright litigation. The filing date, **July 10**, is slightly before the strict weekly window, but the IPA publication and broader coverage appeared during the monitoring period.

### Date and timing basis

- **Lawsuit filing date:** July 10, 2026, as reported by IPA.
- **IPA article publication date:** July 14, 2026.
- Search results also showed TechCrunch and Guardian coverage from roughly four days before the run, and a Reuters AI/legal result, but those pages were not successfully crawled.

### Strongest sources

- **Industry/legal source:** International Publishers Association, “Publishers and Authors File Class Action Lawsuit Against Google for Willful Copyright Infringement to Develop Gemini AI Models” — `https://internationalpublishers.org/publishers-and-authors-file-class-action-lawsuit-against-google-for-willful-copyright-infringement-to-develop-gemini-ai-models/` — crawled.
- **Linked primary legal document:** Complaint PDF linked from the IPA article — `https://publishers.org/wp-content/uploads/2026/07/Hachette-v.-Google-Dkt.-1-Complaint2.pdf` — link observed but not separately crawled.

**Independent/skeptical source:** No crawled independent or Google-response source. Reuters crawl returned blank/inaccessible content.

### Reasoning trace

| Step | Claim or inference | Evidence or basis | Confidence |
|---|---|---|---|
| 1 | A publisher/author class-action complaint was filed against Google over Gemini training. | Crawled IPA article states named plaintiffs, filing date, and claims; links to complaint. | Medium-high |
| 2 | It matters because copyright litigation can change training-data licensing and enterprise risk. | Direct relevance to LLM training and generative AI outputs. | Medium-high |
| 3 | Caveat: allegations are plaintiff-side claims, not established facts. | No Google response or court docket crawl was obtained. | High |

### Confidence and evidence grade

**Confidence:** Medium-high that the filing exists and alleges the described claims; low on merits.
**Evidence grade:** Adequate for legal-news awareness; weak for legal conclusions.

### Caveat / missing evidence

The biggest caveat is source provenance: the crawled source is an industry association aligned with publishers/rightsholders. I did not obtain Google’s response, the full court docket, or a neutral legal analysis within the tool budget.

### Next action

Before drawing conclusions, verify:

1. the complaint PDF and docket metadata;
2. Google’s response or motion practice;
3. whether claims overlap with or differ from existing Google generative-AI copyright litigation;
4. implications for enterprise indemnity and data-provenance commitments in Google AI contracts.

---

# 3. Suppressed repeats

These items were found but not promoted to top findings because evidence was stale, snippet-only, duplicate, generic, or outside the strict lookback.

1. **Moonshot AI / Kimi K3 reported launch**
   - Search results from CNBC, China Daily, and other sites claimed Moonshot AI released **Kimi K3**, with snippets mentioning a **2.8-trillion-parameter** model, **1-million-token context**, and comparison to OpenAI/Anthropic.
   - **Suppression reason:** No primary Moonshot source or model card was crawled before the tool budget was exhausted. Per the monitor rules, snippet-only model-release claims are watchlist leads, not high-confidence findings.

2. **Anthropic Fable 5 cyber safeguards and jailbreak severity framework**
   - Crawled Anthropic’s July 2, 2026 post proposing a **Cyber Jailbreak Severity — CJS** framework and describing Fable 5 cyber classifiers.
   - **Suppression reason:** Important safety context, but outside the past-week window and not a new update this week.

3. **European Commission General-Purpose AI Code of Practice**
   - Crawled EC page titled “General-Purpose AI Code of Practice now available.”
   - **Suppression reason:** Publication date was **10 July 2025**, last update **24 September 2025**. It is stale for this weekly cycle despite appearing in fresh-looking search results.

4. **Reuters Indonesia copyright rewrite lead**
   - Search result claimed Indonesia is preparing copyright changes affecting AI platforms.
   - **Suppression reason:** Reuters page crawl returned no readable content; no primary Indonesian draft bill was crawled.

5. **Benchmark leaderboard sites**
   - Search results included BenchLM, LM Market Cap, Traictory, and similar leaderboard pages.
   - **Suppression reason:** Not crawled and likely require methodology inspection. No independent benchmark finding was promoted without source-level review.

6. **Generic Grok AI review / AI tool reviews / SEO pages**
   - Results included general reviews and AI-tool pages.
   - **Suppression reason:** Too generic, not clearly a material product/research/policy update.

7. **VulnHunter duplicate reposts**
   - Search results included reposts/mirrors of VentureBeat coverage.
   - **Suppression reason:** Deduplicated into the Capital One/VentureBeat/GitHub finding.

---

# 4. Source map and gaps

## Query families used

1. **Model and product releases**
   - “LLM generative AI model release OR API launch July 2026”
   - `site:openai.com July 2026 OpenAI release model API`
   - `site:anthropic.com/news July 2026 Claude release`
   - `site:deepmind.google/discover/blog July 2026 Gemini model release`
   - `site:ai.meta.com/blog July 2026 Llama release`
   - `site:mistral.ai/news July 2026 model release`
   - “Moonshot AI Kimi K3 official July 17 2026 model card”

2. **Safety, evaluations, incidents, jailbreaks**
   - “AI safety evaluation incident generative AI July 2026”
   - “July 2026 AI safety evaluation report jailbreak severity framework generative AI”
   - “Anthropic jailbreak severity framework Amazon Microsoft Google Glasswing July 2026”

3. **Policy, legal, regulatory**
   - “AI regulation policy generative AI July 2026 EU US China”
   - “July 2026 generative AI policy regulation official AI Act code practice”
   - `site:ec.europa.eu artificial intelligence GPAI code of practice July 2026`
   - “July 2026 generative AI lawsuit copyright model policy Reuters”

4. **Open-source, developer tooling, APIs, frameworks**
   - “open source AI developer tools LLM API framework release July 2026”
   - “July 2026 LLM developer tools release notes open source GitHub AI coding agent”
   - “Capital One VulnHunter GitHub July 2026”

5. **Independent technical analysis / benchmarks**
   - “LLM benchmark independent analysis generative AI July 2026”
   - “July 2026 frontier AI benchmark evaluation independent LLM”

## Crawled sources

1. OpenAI Release Notes — `https://openai.com/products/release-notes/`
2. OpenAI Help Center, ChatGPT Enterprise & Edu release notes — `https://help.openai.com/en/articles/10128477-chatgpt-enterprise-edu-release-notes`
3. Anthropic, “Introducing Claude for Teachers” — `https://www.anthropic.com/news/claude-for-teachers`
4. International Publishers Association, Google/Gemini lawsuit post — `https://internationalpublishers.org/publishers-and-authors-file-class-action-lawsuit-against-google-for-willful-copyright-infringement-to-develop-gemini-ai-models/`
5. VentureBeat on VulnHunter — `https://venturebeat.com/technology/capital-one-releases-vulnhunter-an-open-source-ai-tool-that-finds-software-flaws-before-hackers-do`
6. Capital One, “Announcing VulnHunter” — `https://www.capitalone.com/tech/open-source/announcing-vulnhunter/`
7. GitHub `capitalone/VulnHunter` — `https://github.com/capitalone/vulnhunter`
8. Anthropic, “More details on Fable 5’s cyber safeguards and our jailbreak framework” — `https://www.anthropic.com/news/fable-safeguards-jailbreak-framework`
9. European Commission, “General-Purpose AI Code of Practice now available” — `https://digital-strategy.ec.europa.eu/en/news/general-purpose-ai-code-practice-now-available`

## Inaccessible or incomplete

- Reuters Indonesia copyright-law rewrite page: crawl returned blank/no readable content.
- European Commission GPAI contents page and CNBC Kimi K3 page were selected but not crawled because the 30-call budget was exhausted.

## Rejected or weak sources

- SEO-style Kimi K3 explainers and model-review pages.
- Generic Grok review content.
- Leaderboard pages without crawled methodology.
- Duplicate reposts of VentureBeat VulnHunter coverage.
- European Commission GPAI page for this cycle because it was from 2025, not this week.

## Important missing coverage

- Primary Moonshot AI Kimi K3 announcement/model card/API docs/weights/license.
- Independent Kimi K3 benchmark testing.
- Google’s response to the Gemini copyright complaint.
- Court docket or complaint PDF crawl for the Google case.
- Primary source for reported Indonesian copyright-law changes.
- More independent enterprise-user analysis of OpenAI’s Admin APIs, EKM sync, and search behavior.
- Broader global policy coverage beyond EU/US-facing search results.

---

# 5. Watchlist for next run

## Organizations / vendors

- **OpenAI**
  - Release notes, Help Center, developer changelog, Codex changelog.
  - Watch: ChatGPT Work, Sites, Atlas shutdown on **August 9, 2026**, Admin APIs, EKM sync behavior, enterprise search permissions.

- **Anthropic**
  - Claude product/news pages, Claude for Teachers support terms, `anthropics/k12-teacher-skills`, HackerOne cyber-jailbreak program.
  - Watch: Detroit Public Schools pilot, teacher privacy terms, CJS framework updates.

- **Capital One / VulnHunter**
  - GitHub `capitalone/VulnHunter` issues, pull requests, releases, security advisories.
  - Watch: model-provider support beyond Claude, independent tests, CVE-like benchmark datasets, false-positive reports.

- **Google / Gemini legal**
  - Google legal/newsroom response, court docket, complaint PDF, AAP/publisher filings.
  - Watch: motions to dismiss, class-certification arguments, fair-use defenses, licensing settlements.

- **Moonshot AI**
  - Official Kimi/Moonshot blog, API docs, model card, GitHub/Hugging Face weights if released.
  - Watch: Kimi K3 context-window claims, license, API pricing, independent benchmarks.

- **European Commission / AI Office**
  - AI Act GPAI implementation, codes of practice, AI Office enforcement guidance.
  - Watch: current 2026 updates rather than stale 2025 pages.

## Concrete queries for next run

- `Moonshot AI Kimi K3 official model card API weights license`
- `Kimi K3 independent benchmark Artificial Analysis Epoch AI July 2026`
- `Google response Hachette Cengage Elsevier Scott Turow Gemini lawsuit`
- `Hachette v Google Gemini complaint docket July 2026`
- `VulnHunter independent evaluation false positives Claude Code`
- `OpenAI ChatGPT Work Sites enterprise security review`
- `ChatGPT Admin APIs documentation workspace scoped admin keys`
- `Anthropic Claude for Teachers FERPA data processing addendum`
- `Indonesia copyright AI draft bill Reuters July 2026 primary source`
- `AI Office GPAI Code Practice 2026 enforcement guidance`

---

# 6. Action checklist

## Read

- OpenAI Enterprise/Edu release notes for Admin APIs, EKM sync, search, and desktop/workspace changes.
- Capital One’s VulnHunter announcement and GitHub README.
- Anthropic’s Claude for Teachers announcement and linked teacher terms.
- The complaint PDF in the Google/Gemini publisher lawsuit, if legal risk matters to you.

## Verify

- Whether OpenAI Admin keys have the exact permissions, logs, and revocation controls your organization needs.
- Whether ChatGPT search respects workspace permissions, file deletion, project boundaries, and retention settings.
- Whether VulnHunter can run safely on your repositories without exposing sensitive code to an external model provider.
- Whether Claude for Teachers’ privacy/DPA terms meet district or institutional requirements.
- Whether Google has filed a response to the publisher lawsuit.

## Test

- Run VulnHunter on intentionally vulnerable sample repositories before using it on proprietary code.
- Test ChatGPT’s new cross-content search with deleted, restricted, and shared project files.
- If eligible, test Claude for Teachers with non-sensitive sample lesson-planning workflows before using student data.

## Subscribe / monitor

- OpenAI Release Notes RSS.
- Anthropic News and support/legal pages.
- GitHub releases/issues for `capitalone/VulnHunter`.
- Court/legal trackers for Google/Gemini copyright litigation.
- Moonshot AI official channels for Kimi K3 primary documentation.

## Ignore for now

- Generic AI model review pages and SEO explainers unless they link to primary model cards, API docs, or reproducible benchmarks.
- Leaderboards that do not expose methodology, benchmark versions, pricing assumptions, and source provenance.

## Follow up

- Prioritize a next-run deep dive on **Kimi K3** only after crawling Moonshot’s primary documentation and at least one independent benchmark source.
- Revisit **Anthropic’s CJS jailbreak framework** if partners publish updates or if governments/regulators reference it.
- Recheck **EU AI Office** sources for genuinely new 2026 enforcement or GPAI compliance updates.