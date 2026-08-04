**Conditional go** for a four-tenant opt-in beta on 2026-08-12; exclude the nonresponsive fifth tenant unless it signs the risk acknowledgement before enablement.

The known duplicate-audit defect is non-data-loss, reversible, monitored, and within the explicit beta gate. However, it violates the engineering completion gate, so record a named risk acceptance and treat this strictly as a bounded beta—not release completion.

Proceed one tenant for 24 hours, then expand only if duplicate events remain ≤1.0% of retrying jobs and all stop conditions remain clear. Keep the kill switch and rollback owners on active coverage. Prioritize merging and load-testing the concurrency fix before broader exposure or GA.
