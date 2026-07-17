@promplet version: 0.7

@module weavemark.std.ideation.contrastive_mining_core

# Contrastive Mining Core

Contrastive mining extracts the distinguishing and shared characteristics
between two artifacts. Unlike a simple diff, it works at the semantic level:
tone, argumentation style, assumptions, audience, specificity, structure,
evidence, omissions, and substance.

## Core contrastive obligations

- Compare artifacts systematically across diverse dimensions, not merely in
  source order.
- Identify both differences and similarities.
- Ground every important finding in short verbatim citations from the compared
  artifacts whenever text evidence is available.
- Distinguish surface differences from substantive differences.
- Explain why each characteristic matters for the stated focus.
- Order findings from most salient to least salient.
- Avoid overclaiming when evidence is thin or ambiguous.

## Required finding shape

For each characteristic, include:

1. **Label** — short name for the characteristic.
2. **Type** — `DIFFERENCE` or `SIMILARITY`.
3. **Description** — 1-2 sentences explaining the finding.
4. **Evidence from Artifact A** — a brief quote or concrete reference.
5. **Evidence from Artifact B** — a brief quote or concrete reference.

## Review obligations

When revising a contrastive analysis, check for:

- missed comparison dimensions
- misclassified differences or similarities
- weak, inaccurate, or non-verbatim citations
- redundant characteristics that should be merged
- findings ordered by source appearance rather than salience
