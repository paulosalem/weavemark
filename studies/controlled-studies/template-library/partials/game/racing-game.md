## Browser racing game template

- Design {{game_title}} as a complete single-page browser racing game.
- Product intent: {{game_brief}}
- Include one playable course, start/finish line, ordered checkpoints or gates,
  at least one lap, visible hazards, recovery aids, timer, progress feedback,
  pause, restart, and completion/failure states.
- Vehicle movement should use deterministic 2D vectors with acceleration,
  velocity, damping, rotation, stable frame-time handling, and clear collision or
  penalty behavior.
- Gates must be passed in order; wrong gates should not advance progress; lap
  count increments only after the full gate sequence and finish crossing.
- Show title, one-sentence objective, concise controls, start instruction, HUD,
  next-gate indicator, timer, checkpoint progress, collision/penalty feedback,
  and restart guidance.
- Validation should exercise first load, start, movement, checkpoint progress,
  hazard interaction, scoring/timer feedback, pause/resume, restart without page
  reload, and console-error inspection.
