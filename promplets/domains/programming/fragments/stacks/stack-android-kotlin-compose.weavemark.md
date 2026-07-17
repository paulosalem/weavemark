@promplet version: 0.7

@module weavemark.domains.programming.stacks.android_kotlin_compose

# Tech Stack: Android + Kotlin + Jetpack Compose

Use this stack for a modern native Android application with a maintainable
offline-capable architecture.

### Application Stack

- Language: Kotlin.
- UI: Jetpack Compose with Material 3 components and adaptive layouts.
- State: ViewModel plus Kotlin coroutines and Flow/StateFlow.
- Persistence: Room for structured local data and DataStore for preferences.
- Background work: WorkManager for scheduled refreshes, reminders, imports, and
  recurring calculations.
- Dependency injection: Hilt or another explicit dependency-injection mechanism.
- Navigation: Jetpack Navigation for Compose.

### Architecture

- Use a layered architecture with UI, presentation/state, domain, and data
  layers.
- Keep financial calculations in deterministic domain services that can be
  tested without Android UI dependencies.
- Keep platform integrations behind small interfaces so forecasting, import, and
  notification behavior can be tested directly.
- Handle time, currency, locale, and rounding explicitly. Do not hide these
  decisions inside UI formatting.

### Testing and Quality

- Unit-test financial calculations, date handling, and scenario comparisons.
- Add Compose UI tests for the primary dashboard, assumption editing, and empty
  states.
- Use fake clocks and fake repositories in tests for deterministic projections.
- Include migration tests for persisted local data.
- Treat accessibility checks as part of the release checklist.
