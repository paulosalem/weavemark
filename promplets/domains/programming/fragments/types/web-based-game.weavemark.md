@promplet version: 0.7

@module weavemark.domains.programming.types.web_based_game

# Software Type: Web-Based Game

@note
  Reusable product-type layer for games that run in the browser. It captures the
  basic qualities expected from a good browser game without committing to a
  specific genre, engine, framework, or art style.

Use this layer when the software is a game played in a web browser.

## Core game obligations

- Define the player's objective, core action, challenge, and win/loss or scoring
  condition.
- Make the core loop immediately understandable: learn, act, receive feedback,
  improve, and try again.
- Keep input responsive and predictable across keyboard, mouse, touch, or
  gamepad where those controls are supported.
- Provide clear feedback for player actions through motion, sound, visual state,
  score changes, messages, or animation.
- Balance challenge so the first minute is approachable and later play can
  become deeper, faster, or more strategic.
- Include pause, restart, and clear failure/retry paths.

## Browser experience obligations

- Load quickly enough for casual play; defer or compress heavy assets.
- Run smoothly on ordinary laptops and modern mobile browsers when mobile play is
  in scope.
- Preserve aspect ratio and readable UI across common viewport sizes.
- Avoid layout shifts during play; the game area should feel stable.
- Handle focus loss, tab switching, and page visibility changes by pausing or
  safely suspending gameplay.
- Persist only appropriate local state, such as settings, progress, unlocked
  levels, or high scores.

## Game feel and presentation

- Establish a coherent visual style, even if minimal.
- Use animation timing, easing, hit pauses, particles, screen shake, sound, or
  other feedback only when they improve legibility and feel.
- Keep HUD information readable and limited to what the player needs now.
- Make onboarding playable where possible: teach through the first interaction
  rather than relying only on instructions.

## Required implementation considerations

- Specify the game state model: loading, menu, playing, paused, win/lose, and
  restart states as applicable.
- Specify collision, timing, randomness, physics, scoring, progression, and
  persistence rules when they affect gameplay.
- Define asset ownership boundaries: no unlicensed copyrighted art, music, sound,
  fonts, names, or characters.
- Define performance checks, browser compatibility checks, and at least one
  playable smoke test.

## Acceptance criteria

A good first build is complete when a player can open the browser page, learn the
goal, play a complete round, understand why they succeeded or failed, restart
without reloading, and experience stable performance without console errors.
