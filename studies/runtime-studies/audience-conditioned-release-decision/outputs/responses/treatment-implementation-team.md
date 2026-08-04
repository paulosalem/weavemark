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
