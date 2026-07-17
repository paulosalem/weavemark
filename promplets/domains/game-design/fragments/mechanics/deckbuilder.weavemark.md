@promplet version: 0.7

@module weavemark.domains.game_design.mechanics.deckbuilder

# Game Mechanic: Deckbuilder

@note
  Reusable game-design layer for games where the player repeatedly draws,
  chooses, upgrades, and combines cards or card-like actions.

Use this layer when a game needs hand management, draw/discard cycles, upgrades,
synergies, card rarity, and run-to-run variation.

## Card system obligations

- Define what a card represents: action, unit, spell, building, policy, mutation,
  machine, terrain change, event, or resource conversion.
- Define card fields: id, name, cost, type, timing, target, effect, rarity,
  upgrade state, tags, description, and visual state.
- Define deck, draw pile, hand, discard pile, exhaust or one-time-use behavior,
  and reshuffle timing.
- Define resource economy for playing cards, such as energy, mana, credits,
  seeds, actions, cooldowns, or opportunity cost.
- Define targeting and invalid-play feedback.
- Define card rewards, removals, upgrades, transforms, and draft choices.

## Synergy and progression

- Cards SHOULD support readable synergies through shared tags, resource loops,
  status effects, positional effects, or timing windows.
- Deck growth SHOULD create interesting tradeoffs instead of only making the
  player stronger.
- Upgrades SHOULD change decisions, not only numbers.
- A first build SHOULD include a small card set with clear archetypes and a
  short progression path.

## UX and implementation guidance

- Card text MUST be concise and unambiguous.
- The UI MUST show cost, availability, target, effect preview, and reason when a
  card cannot be played.
- The game SHOULD preserve input responsiveness during draw, play, discard, and
  animation sequences.
- Acceptance requires a player to draw cards, play valid and invalid cards, see
  effects resolve, gain or choose a new card, and understand how the deck changes.
