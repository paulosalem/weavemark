@promplet version: 0.7

@module weavemark.domains.programming.modules.adaptive_workspace_shell

# Module: Adaptive Workspace Shell

@note
  Reusable shell for web applications and games that begin with setup or
  onboarding, then need a quieter active workspace without losing access to
  global tools.

Use this module when configuration, guidance, history, settings, or other global
utilities should remain available without competing with the primary active
surface.

## State-aware shell

- Define at least `setup` and `active` shell states. Setup MAY foreground
  onboarding, permissions, connection, configuration, and the primary start
  action. Active state MUST foreground the user's main canvas, document, game,
  media, or workspace.
- Transition existing controls between states rather than presenting unrelated
  duplicates. When setup content becomes compact navigation or a drawer, preserve
  its values, validation, status, and semantic ownership.
- Make the destination of moved controls visually understandable. The View
  Transitions API MAY provide continuity when available; provide a calm CSS and
  instant reduced-motion fallback. Motion MUST never be required to understand
  where controls went.
- Preserve the primary surface across shell-state changes. Do not reset selection,
  scroll, focus, entered text, running work, or local state unless the initiating
  action explicitly requires it.

## Compact persistent navigation

- In active state, expose only a slim sticky top or side navigation surface. Keep
  product identity and the few globally useful outcomes reachable; do not turn it
  into a dense toolbar.
- Use labels or accessible names that remain understandable without hover.
  Icons MAY supplement but MUST NOT replace ambiguous labels.
- Respect safe-area insets, text zoom, small viewports, dynamic viewport changes,
  and content scrolling. The compact shell MUST NOT obscure anchored content or
  consume disproportionate space.
- Global navigation state is secondary to domain state. Persist only meaningful
  user preferences, never credentials or transient secrets.

## Drawer destinations

- Secondary global surfaces SHOULD open as one mutually exclusive drawer, sheet,
  or popover over the active workspace rather than navigate away from it.
- Opening a destination preserves the workspace's selection and scroll. Closing
  returns focus to the invoker and reveals the unchanged workspace.
- Provide an explicit close control, Escape behavior, and a backdrop or outside
  activation path where platform conventions permit. Never make pointer gestures
  the only close path.
- While modal, trap focus inside the drawer, mark or make the background inert,
  and prevent background pointer activation. Restore prior focus robustly even if
  the original invoker was rerendered.
- Avoid nested drawers and multiple simultaneous backdrops. Switching global
  destinations replaces the open drawer without flashing or returning through an
  intermediate empty state.
- Drawer content MAY scroll internally when necessary, but its header and close
  action remain reachable. The underlying workspace MUST NOT scroll in response to
  drawer content.

## Responsive and lifecycle behavior

- Desktop MAY use a side drawer; narrow screens MAY use a near-full-width sheet.
  Both forms preserve the same labels, order, actions, and accessibility model.
- Background refresh, asynchronous completion, resize, and orientation changes
  MUST NOT close a user-opened drawer, move focus, or reset its internal state.
- Back/forward history integration is optional. If implemented, it MUST not create
  duplicate domain actions or make browser Back discard unsaved work.
- Reduced motion uses direct state changes. High contrast, forced colors, keyboard,
  touch, 200% zoom, and 320 CSS-pixel layouts remain fully usable.

## Acceptance criteria

The shell is complete when setup can transition into an uncluttered active
workspace; every global utility remains discoverable in compact navigation;
drawers open and close without disturbing workspace state; focus, Escape,
backdrop, responsive, and reduced-motion behavior are correct; and no secondary
surface becomes a competing application page.

