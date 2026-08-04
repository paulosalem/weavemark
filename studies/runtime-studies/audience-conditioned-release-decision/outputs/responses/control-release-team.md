**Proceed conditionally** with a four-tenant, opt-in beta on 2026-08-12; exclude the nonresponsive fifth tenant.

Before launch, document the exception to the engineering completion gate and obtain named risk acceptance for the known audit-event invariant violation. Do not merge the unvalidated concurrency fix into this beta.

Start with one consenting tenant for 24 hours. Keep live monitoring and kill switch ready. Halt/rollback immediately for any stated stop condition, especially duplicate audit events exceeding 1.0% of retried jobs.
