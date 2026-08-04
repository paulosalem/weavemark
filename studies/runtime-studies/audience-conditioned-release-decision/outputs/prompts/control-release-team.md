Advise the Release Team on Northstar Sync 2.4 to a five-tenant opt-in beta on 2026-08-12 using the notes below.

# Development notes

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
