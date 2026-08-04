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
