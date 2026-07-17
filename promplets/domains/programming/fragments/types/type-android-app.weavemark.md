@promplet version: 0.7

@module weavemark.domains.programming.types.android_app

# Software Type: Native Android App

Use this specification for a phone-first native Android application.

### Product Surface

- Primary interaction happens on Android phones, with tablet layouts only when
  they improve clarity.
- The app must feel useful in short sessions: open, understand the current
  state, adjust one assumption, and leave with a clear next action.
- Use Android platform conventions for navigation, back behavior, permissions,
  system share sheets, notifications, biometrics, accessibility, dark theme, and
  locale-aware formatting.
- Prefer local-first behavior for sensitive personal data. The user must retain
  useful read access when offline.
- Avoid unnecessary account creation. Require sign-in only for optional sync,
  backup, sharing, or paid cloud features.

### Privacy and Trust

- Store sensitive financial data encrypted at rest on device.
- Explain every external connection before it is enabled.
- Let the user export and delete their data.
- Do not imply guaranteed financial outcomes. Treat calculations as planning
  aids based on visible assumptions.

### Mobile UX Obligations

- Use a calm home screen with the most important current answer above the fold.
- Make editing assumptions lightweight and reversible.
- Show uncertainty plainly with ranges, confidence labels, or scenario bands.
- Provide accessible color contrast, large tap targets, screen-reader labels, and
  reduced-motion support.
- Persist UI state across rotation, process death, and app restarts.
