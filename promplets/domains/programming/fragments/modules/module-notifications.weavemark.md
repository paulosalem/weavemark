@promplet version: 0.7

@module weavemark.domains.programming.modules.notifications

# Notifications & Alerts Engine

## Alert rules

- Users define rules with a triggering event or state transition, optional scope,
  condition, threshold, comparison operator, severity, recipients, channel, and
  cooldown.
- Example: "Notify the release owner when a critical gate becomes blocked."
- Evaluate rules after every relevant domain event and on scheduled checks when
  time or aggregation affects the condition.
- Numeric conditions may use `>`, `>=`, `<`, `<=`, `==`, and `between`; state
  rules may match transitions such as `open -> blocked`.
- Record which rule version, event, values, and evaluation time produced each
  notification.

## Notification channels

- **In-app:** transient feedback plus a persistent notification center.
- **Email:** immediate delivery for critical alerts and configurable digests for
  lower-priority updates.
- **Push (optional):** web push through a Service Worker and VAPID keys.
- Respect recipient preferences, quiet hours, disabled channels, and verified
  delivery destinations.

## Deduplication and delivery

- The same semantic event MUST NOT notify the same recipient and channel more
  than once within its cooldown or evaluation period.
- Track stable deduplication keys, last-fired time, delivery state, attempts, and
  terminal failure reason.
- Retries MUST be bounded and MUST NOT create duplicate notifications.
- Digests group related updates rather than replaying one message per event.

## Templates

- Templates use typed runtime fields such as subject, current state, threshold,
  observed value, period, reason, and action URL.
- Render only fields allowed for the chosen channel; never expose secrets or
  sensitive attachment contents in previews.
- Support locale-aware dates and numbers, plus currency formatting only when the
  consuming domain supplies a currency.
- Missing required fields fail validation instead of producing malformed
  messages.
