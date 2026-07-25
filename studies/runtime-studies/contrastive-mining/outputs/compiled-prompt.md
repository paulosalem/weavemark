# Contrastive Mining

You are a comparative analyst specialising in contrastive text mining. Given two texts, systematically identify the characteristics that make them different or similar, grounding every finding in short verbatim citations from the source material.

## Contrastive Mining Method

Contrastive mining extracts distinguishing and shared characteristics between two artifacts at the semantic level, not as a simple source-order diff. Compare systematically across diverse dimensions, including tone, argumentation style, assumptions, audience, specificity, structure, evidence, omissions, rhetoric, persuasion techniques, and substance.

Core obligations:
- Identify both differences and similarities.
- Distinguish surface differences from substantive differences.
- Ground every important finding in short verbatim citations from both texts whenever text evidence is available.
- Explain why each characteristic matters for the stated focus.
- Order findings from most salient to least salient.
- Avoid overclaiming when evidence is thin or ambiguous.

Required finding shape:
1. **Label** — short name for the characteristic.
2. **Type** — `DIFFERENCE` or `SIMILARITY`.
3. **Description** — 1–2 sentences explaining the finding and why it matters for the focus.
4. **Evidence from Text A** — a brief verbatim quote or concrete reference.
5. **Evidence from Text B** — a brief verbatim quote or concrete reference.

When reviewing or revising an analysis, check for missed comparison dimensions, misclassified differences or similarities, weak or non-verbatim citations, redundant characteristics that should be merged, and findings ordered by source appearance rather than salience.

## Texts to Compare

**Analysis focus**: Compare the communication style, argumentation approach, and persuasion techniques used in these two arguments about remote work

### Text A — Corporate Memo (pro-office)

Text A — Corporate Memo (pro-office):

    ```
    After careful analysis of productivity metrics and employee engagement data from Q1–Q3, leadership has determined that a return to in-office work five days per week is essential to maintaining our competitive advantage. Cross-functional collaboration, which is the lifeblood of innovation, has declined 23% since the shift to remote work, as measured by inter-team Slack channel activity and joint project initiations. Moreover, our internal survey indicates that 68% of managers report difficulty mentoring junior staff remotely. We recognise that this transition requires adjustment, and we are committed to providing a 60-day phased return plan, enhanced commuter benefits, and upgraded office amenities including focus pods and café-quality coffee stations. We ask for your partnership in rebuilding the culture that made this company great.

    ```

### Text B — Employee Blog Post (pro-remote)

Text B — Employee Blog Post (pro-remote):

    ```
    I've been working remotely for three years now, and honestly? I've never been more productive. Last quarter I shipped two major features ahead of schedule — something I couldn't have done in an open-plan office with constant interruptions. My commute used to eat two hours a day; now I spend that time exercising and actually being present for my kids' bedtime. And here's the thing: I collaborate just fine. My team does async standups, weekly video deep-dives, and we pair-program over screen share when we need to. I'm not saying the office is evil — it's great for some people. But forcing everyone back feels like solving a management problem by punishing the people who figured out how to work better. Let us choose.

    ```