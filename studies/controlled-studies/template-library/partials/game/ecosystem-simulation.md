## Ecosystem-simulation mechanic template

- Model living tiles, resources, hazards, growth, decay, spread, resilience,
  recovery, and stress.
- Feedback loops should be simple and readable: beneficial states improve
  defenses or resources, harmful states spread or reduce effectiveness, and
  recovery actions visibly change future outcomes.
- Use deterministic or seeded ticks so players can reason about cause and effect.
- Provide overlays and tooltips for health, stress, abundance, shortage, spread,
  resilience, and looming failure.
- Ecosystem state should change tactical value, not remain decorative.
- Validation should test resource flow, spread, recovery, failure thresholds, and
  player-readable feedback.
