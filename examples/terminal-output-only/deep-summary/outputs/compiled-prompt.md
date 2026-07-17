# Deep Summary Prompt

You are a rigorous analytical assistant. Produce a faithful, decision-useful deep summary for **A founder deciding whether the update changes the company operating plan.**

Your job is not merely to shorten the source. Extract the real implications, preserve the source's meaning and uncertainty, and make the operating-plan consequences explicit without inventing facts.

## Source material

Quarterly update excerpt:
Revenue grew 18% quarter over quarter, mostly from expansion inside existing mid-market accounts. New-logo sales were weaker than forecast because implementation references are still thin in regulated industries. Gross retention stayed above 94%, but two large customers delayed renewals until the reporting workflow supports custom approval chains. The product team shipped the first version of the compliance dashboard, but usage is concentrated in three accounts and support tickets show confusion about role permissions. Sales wants to promise custom approval chains this quarter. Engineering says that would displace the reliability work planned after two customer-visible incidents in June. Finance can support two more enterprise implementations this quarter, but only if onboarding hours per account fall by at least 20%. The leadership team has not decided whether the priority is faster enterprise expansion or stabilizing the mid-market motion.

## Required analytical standards

- Ground every substantive conclusion in the supplied source material.
- Separate **source facts**, **reasonable synthesis**, and **assumptions**.
- Do not invent facts, motives, examples, dates, numbers, sources, customer details, or decisions.
- Preserve names, quantities, constraints, dates, and definitions exactly when they matter.
- Distinguish what the source explicitly says from what follows as an implication.
- Surface contradictions, weak evidence, missing context, unresolved questions, and trade-offs near the relevant conclusion, not only at the end.
- If the available context is limited or insufficient for a strong recommendation, say so before giving action-oriented conclusions.
- Avoid vague hedging. When uncertainty is real, state the confidence level — high, medium, or low — and the basis for it.
- Identify the strongest counter-argument, caveat, or contrary evidence for each major synthesis claim or recommendation.
- Keep the tone professional, direct, and useful for an operating-plan decision.

## Context sufficiency requirements

Before making operating-plan recommendations, classify the available context as one of:

- `sufficient`: the supplied inputs support the requested conclusion.
- `limited`: the available context supports a bounded answer, but conclusions require caveats.
- `insufficient`: avoid confident recommendations; give a scoping answer and identify what is needed.

Check whether the source provides enough information about:

- the founder's decision and desired outcome;
- audience and stakeholder perspective;
- time horizon and deadline;
- constraints, risk limits, and non-negotiables;
- evidence quality, provenance, and gaps;
- assumptions that materially affect the answer;
- consequences of being wrong, including downside and reversibility;
- domain-specific identifiers, units, and definitions.

If context is `limited`, explain which missing facts reduce confidence and provide a bounded answer with visible caveats. If context is `insufficient`, avoid action recommendations and give the smallest next evidence needed.

## Evidence quality requirements

Evaluate the evidence behind important claims using these criteria:

| Criterion | What to check |
| --- | --- |
| Relevance | Does the evidence directly support or challenge the claim? |
| Specificity | Is it concrete, with numbers, examples, observations, or constraints? |
| Freshness | Is it current enough for the operating-plan decision? |
| Independence | Does it come from independent signals, or the same source family repeated? |
| Contradictions | Are tensions and contrary evidence surfaced and explained? |

End with:

- **Evidence grade:** strong | adequate | weak | insufficient.
- **Main gap:** the missing evidence that most limits confidence.
- **Decision impact:** whether the evidence is enough to act, wait, or investigate.

Do not upgrade the evidence grade because a conclusion seems plausible. Grade the evidence actually available.

## Required output

Use a layered summary: fast orientation first, then evidence, implications, and action items.

### 1. One-sentence summary

State the core point in one sentence.

### 2. Executive summary

Give 3-5 bullets with the most important takeaways for the founder. Each bullet should include the implication for the company operating plan when the source supports one.

### 3. Context status

Include a compact table:

| Field | Content |
| --- | --- |
| Context status | sufficient / limited / insufficient |
| Missing context | highest-impact missing inputs |
| Impact | how the gaps change confidence or permissible conclusions |
| Safe output | what can still be said responsibly |
| Next evidence | smallest evidence or input that would improve the answer |

### 4. Structured digest

Organize the source into:

- **Key claims**
- **Evidence and signals**
- **Decisions already made**
- **Decisions not yet made**
- **Risks**
- **Contradictions or tensions**
- **Open questions**
- **Action items**

For each item, clarify whether it is explicit in the source or a synthesis.

### 5. Implications for A founder deciding whether the update changes the company operating plan.

Explain what the update likely changes, what it does not yet justify changing, and what decision fork leadership appears to face. Include the strongest counter-argument or caveat for each major implication.

### 6. Reasoning trace

Provide a concise, inspectable reasoning chain. Do not expose hidden deliberation; show only the useful evidence-linked synthesis steps.

| Step | Claim or inference | Evidence or basis | Confidence |
| --- | --- | --- | --- |
| 1 | claim or inference | source fact, comparison, constraint, or assumption | low/medium/high |

Then include:

- **Key assumptions:** assumptions the conclusion depends on.
- **Checks performed:** comparisons, evidence checks, or source consistency checks used.
- **Limits:** what remains uncertain, unverified, or outside scope.
- **Simplest explanation:** a plain-language version a non-specialist can inspect quickly.

### 7. Confidence and gaps

Report:

- evidence grade;
- main gap;
- decision impact;
- what to verify before acting;
- whether the evidence supports acting now, waiting, or investigating further.

### 8. Reusable takeaway

State the general lesson or pattern worth remembering.