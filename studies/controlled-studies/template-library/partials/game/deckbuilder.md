## Deckbuilding mechanic template

- Define deck, draw pile, hand, discard pile, exhausted cards, reshuffle, energy
  or action budget, card cost, timing, target, effect, rarity, tags, and upgrade
  state.
- Cards should support placement, intervention, recovery, resource conversion,
  tactical events, upgrades, route manipulation, and emergency actions.
- The first card set should include clear archetypes, synergies, counters,
  invalid-play cases, and readable effect previews.
- The UI should show card cost, target, effect preview, invalid-play reason,
  draw/discard counts, reshuffle state, and what will happen before confirmation.
- Card effects must update the game state deterministically and be testable.
