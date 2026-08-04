# Audience-Conditioned Release Decision Results

[Open the self-contained HTML report](results.html).

## Design

One synthetic release case, two audience conditions, and one response per
control/treatment cell. Every downstream response used `gpt-5.6-terra`. Anonymous
blind* rubric scoring used `claude-opus-5`.

## Metric definitions

- **Words:** lexical tokens in the saved response, used only to expose the
  treatment-control length difference.
- **Evidence /16:** sum of four 0-4 scores for specific facts, separation of
  facts/assumptions/unknowns, counterevidence/tradeoffs, and unsupported claims.
- **Protocol /16:** sum of four 0-4 scores for an explicit scoped decision, gate
  logic, risks/mitigations/owners, and conditions/triggers/actions.
- **Alignment /4:** secondary score for useful emphasis on the assigned audience
  without suppressing decision-critical contrary evidence.
- **Total /36:** evidence, protocol, and alignment scores added together.
- **blind\*:** identities were randomized before scoring, but response length and
  formatting could still reveal the prompt condition.

## Scores

| Audience | Variant | Reported label* | Words | Evidence /16 | Protocol /16 | Alignment /4 | Total /36 |
|---|---|---|---:|---:|---:|---:|---:|
| Implementation Team | [C] Control | conditional go | 105 | 10 | 12 | 3 | 25 |
| Implementation Team | [T] Treatment | wait | 453 | 15 | 14 | 3 | 32 |
| Release Team | [C] Control | proceed conditionally | 77 | 9 | 12 | 3 | 24 |
| Release Team | [T] Treatment | no-go | 493 | 16 | 15 | 4 | 35 |

## Treatment-control differences

- **Implementation Team:** treatment-control evidence +5; protocol +2; total +7.
- **Release Team:** treatment-control evidence +7; protocol +3; total +11.

## Decision behavior

- **Implementation Team / control:** reported `conditional go` (105 words; [response](../outputs/responses/control-implementation-team.md)).
- **Implementation Team / treatment:** reported `wait` (453 words; [response](../outputs/responses/treatment-implementation-team.md)).
- **Release Team / control:** reported `proceed conditionally` (77 words; [response](../outputs/responses/control-release-team.md)).
- **Release Team / treatment:** reported `no-go` (493 words; [response](../outputs/responses/treatment-release-team.md)).

*The treatment prompt mandated `Gate: go | no-go | wait | investigate`; the
control did not. Reported labels are therefore descriptive transcripts, not a
comparable outcome measure.*

The Release control and treatment converge more than their labels suggest: both
describe a conditioned one-tenant, 24-hour path. They differ mainly on whether
that path is approved now or requires separate approval; the control additionally
pre-authorizes expansion to four tenants, while the treatment does not. No common
behavioral decision outcome was pre-specified, so this study does not score
decision direction.

The two compiled treatment prompts differ beyond their explicit audience
branches because they were produced by separate semantic-compilation calls. The
Release Team prompt is about 22% longer and additionally mandates an explicit
five-tenant-versus-narrower adjudication and a risks-and-next-action section
corresponding to a scored rubric dimension. The Implementation prompt uniquely
frames the decision as bounded-beta-only, while Release asks whether the requested
five-tenant release may proceed. Both assess material claims, but Release expands
the criteria into a definitional table. Therefore, differences between treatment
audiences cannot be attributed solely to `@match`.

## Anonymous evaluator notes

- **Implementation Team / control:** Well-scoped, honest, and readable, with a defensible resolution of the gate conflict, but it argues from conclusions rather than evidence: no metrics, no explicit unknowns, and no named owners behind the risk acceptance it requires.
- **Implementation Team / treatment:** Analytically the sharpest treatment of the gate contradiction and of the 1.0% threshold's meaning, with excellent unknown-handling. Held back by unowned risk assignments and a claim-assessment table that rates independence and freshness dimensions the supplied facts do not support.
- **Release Team / control:** Operationally sound and correctly scoped decision with clean, non-inflated claims, but evidentially thin: almost no supplied metrics, no explicit unknowns, no named owners, and no acknowledgement of the strong supporting evidence that would justify the exception it requests.
- **Release Team / treatment:** The most rigorous submission on the decision-protocol axis. Gate arbitration is exemplary and the evidence base is broad and accurately quantified; the only real gap is that named ownership is partial, resting on the release engineer alone.

## Interpretation

Treatment-control evidence-quality differences were
+5 for the Implementation Team and
+7 for the Release Team; protocol differences
were +2 and
+3. This is a four-response synthetic case
study. Several rubric dimensions directly correspond to sections mandated by the
treatment output contract, so scores partly measure format compliance. Response
format and length made variant identity inferable despite anonymous IDs.
Differences describe these saved outputs only; they do not estimate an average
causal effect, a length-independent effect, or general model-wide superiority.
One evaluator scored all four responses in one shared packet; there is no repeat
or inter-rater reliability estimate.

## Artifacts

- [Study protocol](../README.md)
- [Anonymous evaluator packet](../outputs/blind/packet.md)
- [Machine-readable results](results.json)
