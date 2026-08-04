# Anonymous evaluator packet

Evaluate each response independently. Do not infer or guess its prompt variant.
Use only the supplied synthetic facts. Return JSON matching the schema below.

## Synthetic facts

# Decision scope
- The proposed release enables Northstar Sync 2.4 for five named, opt-in beta tenants for 14 days. It is not general availability.
- The decision deadline is 2026-08-10. The planned beta starts 2026-08-12.

# Engineering evidence
- Architecture review approved the queue, storage, and public API design on 2026-08-01.
- The public sync_batch() request and response schema is unchanged from 2.3.
- Throughput reached 18,400 items/minute against a 15,000 target; p95 latency was 182 ms against a 250 ms target.
- 1,246 of 1,263 automated tests pass. Seventeen tests are quarantined.
- Two quarantined concurrency tests reproduce duplicate audit events during retry races. The observed rate is 0.7% of jobs with concurrent retries.
- The duplicate events do not duplicate user data, billing, or sync operations, but they violate the documented exactly-once audit-event invariant.
- The root cause is understood. A proposed fix exists but has not been merged or load-tested.
- The engineering completion gate requires zero known invariant violations and no quarantined release-blocking tests.

# Beta and user evidence
- A three-week shadow run across 12 tenants completed 98.6% of sync jobs without operator intervention.
- No user-data loss or billing error was observed in the shadow run.
- Four of the five proposed beta tenants requested early access and signed the beta-risk acknowledgement. The fifth has not replied.
- Median recovery time in the shadow run was 11 minutes versus 29 minutes on version 2.3.
- Duplicate audit events can confuse tenant administrators and support investigations even though sync results remain correct.

# Operational readiness
- Rollback to 2.3 passed three of three drills and completed in 7-9 minutes against a 15-minute objective.
- A feature-flag kill switch disables the new retry scheduler in under two minutes without redeployment.
- Dashboards and alerts cover job failure rate, retry rate, duplicate audit events, queue depth, latency, and rollback status.
- The release engineer owns the rollout; the on-call lead owns rollback; the support lead owns tenant communication.
- The rollout plan is one tenant for 24 hours, then up to five if no stop condition fires.

# Explicit beta gate
- A bounded opt-in beta may proceed with a documented non-data-loss defect only when exposure is reversible, monitoring is live, affected tenants consent, and a named owner accepts the risk.
- Stop conditions are any user-data loss, duplicate audit events above 1.0% of jobs with retries, p95 latency above 250 ms for 30 minutes, or two tenant-impacting support incidents in 24 hours.

# Unknowns
- The duplicate-event rate under the five tenants' production workload is unknown.
- The unresponsive tenant's consent status is unknown.
- The proposed concurrency fix has not been validated.

## Rubric

Score every criterion from 0 to 4.

Evidence quality:
- specific_facts: uses concrete supplied facts and metrics;
- facts_assumptions_unknowns: separates facts, assumptions, and unknowns;
- counterevidence_tradeoffs: represents both supporting and opposing evidence;
- unsupported_claims: avoids invented or stronger-than-supported claims.

Decision protocol:
- explicit_scoped_decision: states a clear decision for the proposed beta scope;
- gate_logic: applies stated gates and criteria to evidence;
- risks_mitigations_owners: links risks to mitigations and named owners;
- conditions_triggers_actions: gives conditions, stop/reversal triggers, and next actions.

Secondary:
- audience_alignment: emphasizes the supplied audience condition without ignoring
  decision-critical contrary evidence.


## Required JSON shape

```json
{
  "evaluator_model": "MODEL",
  "scores": [
    {
      "anonymous_id": "R1",
      "audience": "Implementation Team",
      "evidence": {
        "specific_facts": {"score": 0, "rationale": "..."},
        "facts_assumptions_unknowns": {"score": 0, "rationale": "..."},
        "counterevidence_tradeoffs": {"score": 0, "rationale": "..."},
        "unsupported_claims": {"score": 0, "rationale": "..."}
      },
      "decision_protocol": {
        "explicit_scoped_decision": {"score": 0, "rationale": "..."},
        "gate_logic": {"score": 0, "rationale": "..."},
        "risks_mitigations_owners": {"score": 0, "rationale": "..."},
        "conditions_triggers_actions": {"score": 0, "rationale": "..."}
      },
      "audience_alignment": {"score": 0, "rationale": "..."},
      "overall_notes": "..."
    }
  ]
}
```

## Anonymous responses

## R1

Audience condition: Release Team

**Proceed conditionally** with a four-tenant, opt-in beta on 2026-08-12; exclude the nonresponsive fifth tenant.

Before launch, document the exception to the engineering completion gate and obtain named risk acceptance for the known audit-event invariant violation. Do not merge the unvalidated concurrency fix into this beta.

Start with one consenting tenant for 24 hours. Keep live monitoring and kill switch ready. Halt/rollback immediately for any stated stop condition, especially duplicate audit events exceeding 1.0% of retried jobs.

## R2

Audience condition: Release Team

Gate: no-go

Reason: The requested five-tenant beta fails the engineering completion gate and lacks consent from one named tenant.

Confidence: high

| Criterion | Threshold | Current read | Gate status | Confidence |
| --- | --- | --- | --- | --- |
| Engineering completion | Zero known invariant violations; no quarantined release-blocking tests | Two quarantined tests reproduce duplicate audit events at 0.7% of concurrent-retry jobs | fail | high |
| Beta defect allowance | Reversible exposure, live monitoring, tenant consent, named risk owner | Reversible controls and monitoring exist; four tenants consented; fifth has not; risk acceptance owner not identified | fail | medium |
| Performance | ≥15,000 items/min; p95 ≤250 ms | 18,400 items/min; p95 182 ms | pass | high |
| Data and billing safety | No observed user-data loss or billing errors | None observed during three-week, 12-tenant shadow run | pass | medium |
| Operational recovery | Rollback ≤15 minutes; kill switch available | Rollback 7–9 minutes in 3/3 drills; kill switch <2 minutes | pass | high |
| Production duplicate-event control | ≤1.0% of retry jobs; production rate known enough to manage | 0.7% in concurrency reproduction; five-tenant production rate unknown | unknown | medium |
| Tenant eligibility | All five named tenants opt in and acknowledge risk | Four consented; one unresponsive | fail | high |
| Rollout safeguards | One tenant for 24 hours; stop conditions monitored | Defined owners, alerts, staged rollout, and stop conditions | pass | high |

The engineering completion gate is stricter and currently blocks release: the known exactly-once invariant violation and release-blocking quarantined tests fail it. The bounded-beta gate permits a documented non-data-loss defect only with reversible exposure, monitoring, consent, and named risk acceptance; it does not override the engineering completion gate. It also is not fully met because the fifth tenant has not consented and risk acceptance lacks a named owner.

The requested five-tenant release may **not** proceed as proposed. A narrower release could be justified only as a separately approved, one-tenant, opt-in, 24-hour controlled beta: exclude the unresponsive tenant; obtain written consent and a named risk owner; explicitly waive the engineering gate for this bounded exception; confirm live duplicate-event monitoring; and enforce the stated stop conditions. This is not approval of the requested release.

- **Evidence grade:** adequate.
- **Main gap:** Validated production-representative duplicate-event rate and effectiveness of the proposed concurrency fix.
- **Decision impact:** Enough to wait; not enough to release five tenants.
- **Blockers:** Known invariant violation, two release-blocking quarantined tests, unvalidated fix, unknown production behavior, missing fifth-tenant consent, unnamed risk acceptor.
- **Next evidence:** Merge and load-test the concurrency fix, demonstrate zero known duplicate-event invariant violations, unquarantine or disposition the two tests, obtain all tenant consents, and name the risk owner.
- **Change trigger:** Recommend go when the engineering completion gate passes and all five tenants have documented consent; recommend a narrowly controlled exception only if its prerequisites are formally met.
- **Risks and next action:** User risk is confusing duplicate audit history and impaired support investigations; operational risk is an unknown production retry-race rate; release risk is bypassing an explicit engineering gate. The release engineer should hold the five-tenant rollout, coordinate fix validation with engineering, and obtain written tenant consent and named risk acceptance before the 2026-08-10 deadline.

## R3

Audience condition: Implementation Team

**Conditional go** for a four-tenant opt-in beta on 2026-08-12; exclude the nonresponsive fifth tenant unless it signs the risk acknowledgement before enablement.

The known duplicate-audit defect is non-data-loss, reversible, monitored, and within the explicit beta gate. However, it violates the engineering completion gate, so record a named risk acceptance and treat this strictly as a bounded beta—not release completion.

Proceed one tenant for 24 hours, then expand only if duplicate events remain ≤1.0% of retrying jobs and all stop conditions remain clear. Keep the kill switch and rollback owners on active coverage. Prioritize merging and load-testing the concurrency fix before broader exposure or GA.

## R4

Audience condition: Implementation Team

Gate: wait

Reason: The bounded beta is operationally reversible and monitored, but a known exactly-once invariant violation fails the engineering completion gate and the fifth tenant lacks consent.

Confidence: high

| Criterion | Threshold | Current read | Gate status | Confidence |
| --- | --- | --- | --- | --- |
| Engineering completion | Zero known invariant violations; no quarantined release-blocking tests | Two quarantined concurrency tests reproduce duplicate audit events in 0.7% of concurrent-retry jobs | fail | high |
| Beta defect exception | Non-data-loss defect; reversible exposure; live monitoring; tenant consent; named risk owner | Defect is non-data-loss; rollback/kill switch and monitoring exist; owner assignment exists; only four tenants consent | fail | high |
| Performance | ≥15,000 items/min and p95 ≤250 ms | 18,400 items/min; p95 182 ms | pass | high |
| Shadow reliability | Sufficient evidence of safe beta operation | 98.6% completed without intervention; no loss/billing errors; retry-race production rate unknown | unknown | medium |
| Rollback readiness | Reversible within 15 minutes | Three drills completed in 7–9 minutes; kill switch <2 minutes | pass | high |
| Tenant eligibility | Every enabled tenant opts in and acknowledges risk | Four consented; fifth has not replied | fail | high |
| Stop-condition readiness | Detect and act on defined stop conditions | Relevant dashboards, alerts, owners, and staged rollout are defined | pass | high |

**Material-claim assessment**

| Claim | Relevance | Specificity | Freshness | Independence | Contradictions |
| --- | --- | --- | --- | --- | --- |
| Architecture/public API approved and unchanged | high | high | high | medium | low |
| Performance meets targets | high | high | unspecified | medium | low |
| Duplicate audit invariant violation occurs at 0.7% of concurrent-retry jobs | high | high | unspecified | medium | high |
| Shadow run had no data loss/billing errors and improved recovery | high | high | high | medium | medium |
| Rollback and kill-switch readiness | high | high | unspecified | medium | low |
| Four tenant consents; fifth unknown | high | high | high | high | low |

Contradiction: the explicit beta exception allows a documented non-data-loss defect under controlled conditions, but the separate engineering completion gate requires zero known invariant violations and no quarantined release-blocking tests. The latter is currently failed; the exception cannot be assumed to waive it. The 0.7% observed defect rate is below the 1.0% stop threshold, but that is not a release-pass threshold and production exposure is unknown.

- **Evidence grade:** adequate.
- **Main gap:** validated evidence that the duplicate-audit invariant violation is resolved or formally accepted as non-blocking for this bounded beta.
- **Decision impact:** wait; do not enable any tenant until the failed engineering gate is dispositioned.
- **Blockers:** known invariant violation, two quarantined release-blocking tests, unvalidated fix, and missing fifth-tenant consent.
- **Next evidence:** merge and load-test the concurrency fix; rerun the two tests unquarantined with zero violations; obtain consent before enabling each tenant.
- **Change trigger:** recommend go for the four consenting tenants if the invariant tests pass, release-blocking quarantine is removed, risk acceptance is explicit, and monitoring/rollback readiness remains verified. Recommend no-go if the defect persists or cannot be formally waived; exclude the fifth tenant unless it consents.
