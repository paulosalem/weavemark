# Product design direction

## Calm workspaces, not an operations console

AI Kanban follows the user's mental model: a board of workspaces that may
contain a plan, decision, bounded agent turns, durable memory, and results.
Implementation concepts such as SQLite metadata, fingerprints, coordination
records, and raw payloads stay behind About, diagnostics, history, or explicit
handoff views.

The first run has one promise and exactly three choices. After activation,
Needs you, AI working, and AI updated are the strongest status signals. Amber
always pairs an icon with “Needs you”; violet/teal always pairs an icon with an
AI status. The board remains the spatial overview while a large modal gives
selected work enough room.

## Visual language

- restrained navy for authority and primary action;
- mineral teal for progress and local trust;
- warm paper and white surfaces for calm depth;
- coral for destructive attention;
- violet/teal for AI-authored change;
- amber for human input needed.

Georgia display type gives workspaces a humane editorial identity; system sans
type keeps controls compact and platform-native. Soft borders, low shadows,
small radii, and sparse motion prioritize clarity over decoration.

## State-aware behavior

- **First run:** local-data promise, three actions, support disclosure.
- **Quiet board:** useful invitation rather than empty columns competing.
- **Active board:** attention counts, search, progressive filters, six columns.
- **Detail:** Overview first; advanced history is one tab away.
- **Read-only/agent:** mutations disable without hiding context.
- **Conflict/recovery:** foreground draft safety and concrete next actions.
- **Narrow mode:** horizontally scrollable board inside a non-overflowing
  document; full-height card workspace with reachable footer actions.

Selection, focus, board scroll, and modal state are not replaced by background
coordination polling. Native `hidden` remains authoritative.
