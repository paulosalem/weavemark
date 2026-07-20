@promplet version: 0.7

@module weavemark.domains.programming.modules.realtime

# Real-Time Communication Module

### WebSocket Protocol
- Production endpoint: `wss://host/ws`; plaintext `ws://` is permitted only for
  explicitly local development with no production credentials.
- Never place JWTs, access tokens, refresh tokens, or other bearer credentials in
  a URL or query string. Authenticate with a short-lived token in the first
  application message or a reviewed WebSocket subprotocol flow, or with a
  `Secure`, `HttpOnly`, appropriately `SameSite` cookie for a same-site browser
  deployment. Do not accept application messages before authentication succeeds.
- For browser clients, validate the `Origin` header against an explicit allowlist
  before upgrading. Do not treat CORS as WebSocket origin protection.
- On connection and before each privileged join/action, validate token signature,
  issuer, audience, expiry, and subject, then enforce current channel/resource
  authorization server-side. Close expired, revoked, or unauthorized sessions.
- Redact credentials, cookies, authentication frames, and sensitive payloads from
  application, proxy, tracing, and error logs.
- Message format: JSON with `{"type": "...", "payload": {...}, "id": "uuid"}`.
- Server sends `{"type": "ack", "id": "..."}` for every client message.
- Heartbeat: server sends `{"type": "ping"}` every 30 seconds; client MUST
  respond with `{"type": "pong"}` within 10 seconds or connection is closed.

### Presence
- Server tracks connected users per channel/room.
- On join/leave, broadcast `{"type": "presence", "payload": {"user_id": "...", "status": "online|offline"}}`.
- Client can request current presence list via `{"type": "presence_list", "payload": {"channel": "..."}}`.

### Message Types
- `chat`: text message with `sender_id`, `content`, `timestamp`.
- `state_update`: game/app state delta with `entity_id`, `changes` (JSON patch).
- `error`: server error with `code` and `message`.

### Reconnection
- Client MUST implement exponential backoff: 1s, 2s, 4s, 8s, max 30s.
- Before reconnecting, refresh an expired or near-expiry access token through the
  normal secure refresh flow; never replay a stale credential or put the refreshed
  token in the reconnect URL.
- On reconnect, client sends `{"type": "resume", "payload": {"last_event_id": "..."}}`.
- Server replays missed events since `last_event_id` (up to 1000 events or 5 minutes).
