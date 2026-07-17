@promplet version: 0.7

@module weavemark.domains.programming.assets.generative_2d_sprites

# Generative 2D Sprite Production

@note
  Reusable programming fragment distilled from practical sprite-generation
  experiments. The reference implementation used a spec-first wrapper around
  image-generation API calls, deterministic frame packing, metadata export, and
  optional vision-model validation. This fragment captures the method as
  specification obligations rather than code.

Use this layer when a 2D game needs sprites, sprite sheets, animation frames, or
game-ready character/object assets generated through image-generation models such
as OpenAI image APIs.

## Core method

This software specification treats sprite generation as an asset pipeline,
not as a one-off art request. It defines:

- the sprite's game role, name, scale, collision footprint, readable silhouette,
  and gameplay states;
- the target frame size in pixels, such as 16x16, 32x32, 64x64, or 128x128;
- the intended art style, palette, outline treatment, lighting, view angle, and
  camera orientation;
- the required animations, each with a stable name, frame count, frames per
  second, loop flag, and pose/motion description;
- whether a transparent background is required;
- the sprite-sheet packing layout and metadata format needed by the engine.

The pipeline should generate or request individual frames first, then pack them
deterministically into a sprite sheet. Do not rely on an image model to create an
entire exact sprite sheet grid with perfectly aligned cells unless the output is
only a rough concept sheet.

## Sprite specification contract

For every generated sprite, require a structured sprite spec with this shape:

```json
{
  "name": "hero_knight",
  "description": "Brave knight with silver armor, blue cape, readable sword silhouette",
  "style": "pixel_art",
  "frame_width": 64,
  "frame_height": 64,
  "background_color": "transparent",
  "animations": [
    {
      "name": "idle",
      "frame_count": 4,
      "fps": 8,
      "loop": true,
      "description": "Standing still with subtle breathing motion"
    },
    {
      "name": "walk",
      "frame_count": 6,
      "fps": 12,
      "loop": true,
      "description": "Walking cycle with cape and sword moving consistently"
    }
  ],
  "additional_prompt": "Centered in frame, no text, no UI, no scene background"
}
```

Animation names must be stable identifiers, for example `idle`, `walk`, `run`,
`jump`, `attack`, `hit`, `die`, `cast`, `spin`, or `open`. Frame counts should
start small and purposeful. Prefer 2-4 frames for idle, hit, blink, or simple
effects; 4-8 frames for walk/run/cast/spin; and only use more frames when the
game genuinely needs smoother animation.

## Frame prompt construction

Each image-generation API call should receive one frame prompt. The prompt must
combine:

1. fixed frame constraints: "A single {width}x{height} 2D game sprite frame";
2. the full sprite identity and appearance, repeated every time for consistency;
3. the chosen visual style in concrete terms;
4. the animation name and frame index;
5. the pose or motion-progress instruction;
6. background requirements;
7. quality and usability constraints.

A good frame prompt has this form:

```text
A single 64x64 pixel sprite frame of a brave knight with silver armor, blue cape,
readable sword silhouette, in pixel art style, retro game aesthetic, crisp
pixels, limited color palette, walk animation frame 3 of 6, approximately 40%
through a left-to-right walking cycle, same character proportions and palette as
the other frames, centered in frame, feet aligned to the same baseline, on a
transparent background, game asset quality, no text, no UI, no extra characters,
no scene background.
```

For pixel art, be explicit about crisp edges, limited palette, readable
silhouette, small-canvas legibility, and no painterly blur. For cartoon or vector
sprites, be explicit about bold outlines, clean shapes, flat colors, and
consistent proportions. For realistic styles, be careful: they often produce
noisy details that are hard to read at game scale.

## Animation consistency

Animated sprites need temporal coherence. The final spec must require:

- one canonical appearance description repeated in every frame prompt;
- a consistent view angle, lighting direction, outline style, color palette,
  weapon/tool placement, and scale;
- stable body proportions and anchor points across frames;
- aligned feet or contact points for grounded characters;
- center placement unless the engine intentionally expects offsets;
- smooth progression between frames, with no duplicate poses unless deliberate;
- loop checks for looping animations, especially first-to-last frame continuity.

For walk and run cycles, describe progress through the cycle as a percentage or
phase and specify which foot/limb is forward when important. For idle animations,
keep movement subtle: breathing, blink, hair/cape sway, sparkle, or small bob.
For attacks or casts, define anticipation, contact/release, follow-through, and
recovery frames. For death or one-shot effects, set `loop: false`.

## What works well

- Generate frames individually, then pack them with deterministic tooling.
- Preview all frame prompts before spending API calls.
- Keep the first pass small: one sprite, one or two animations, modest frame
  counts.
- Use a consistent sprite spec as the source of truth rather than hand-written
  one-off prompts.
- Request transparent backgrounds for game objects and characters.
- Generate at a supported model size, then resize or crop to the target frame
  size with a deterministic image step.
- Store the exact generation prompt, model, revised prompt if available, seed or
  request metadata if available, and selected frame dimensions.
- Export sprite-sheet metadata for the target engine instead of relying on manual
  coordinate slicing.
- Validate visual quality with both human inspection and structured checks.

## What usually fails

- Asking the model for a complete production-ready sprite sheet with exact rows,
  columns, padding, and frame boundaries.
- Asking for too many frames or too many poses in a single image.
- Using vague descriptions such as "cool hero" without silhouette, palette,
  equipment, orientation, and style constraints.
- Mixing style vocabularies such as pixel art, watercolor, 3D render, and vector
  in the same sprite.
- Expecting independent API calls to preserve character details unless every
  prompt repeats the canonical appearance.
- Letting the model add backgrounds, shadows, text labels, UI panels, extra
  characters, or scene context to a frame that should be a reusable game asset.
- Trusting nominal pixel dimensions from the model without deterministic
  resizing, cropping, and frame-bound validation.
- Skipping metadata, which makes animation playback brittle in the game.

## Packing and metadata requirements

After frames are selected, the final software spec must define how they become
usable assets:

- frame order: all frames sorted by animation and frame index;
- packing strategy: horizontal strip, vertical strip, grid, or engine-specific
  atlas;
- padding between frames when texture bleeding or scaling may occur;
- sheet dimensions derived from frame size, count, padding, and grid columns;
- per-frame rectangles with `x`, `y`, `w`, and `h`;
- animation metadata with frame names, frame count, FPS, and loop flag;
- target metadata format, such as native JSON, TexturePacker JSON/hash, Pygame
  XML, Phaser/Pixi-compatible atlas metadata, or Godot SpriteFrames resource;
- stable asset filenames and paths.

For browser games, TexturePacker-style JSON or a simple native JSON manifest is
usually enough. The manifest should name the sheet image, frame size, all frame
rectangles, and all animation definitions.

## Quality checks

Every generated sprite set must be checked before integration. Require:

- clarity: the sprite remains readable at actual in-game scale;
- style match: the frame matches the chosen style and the rest of the game;
- consistency: proportions, palette, outline, and view angle remain coherent
  across frames;
- transparency: transparent assets actually have an alpha background when
  required;
- alignment: feet, ground contact, center point, and attack/effect origin are
  stable enough for gameplay;
- animation: frame order plays smoothly at the declared FPS and loops cleanly
  when `loop` is true;
- collision fit: the visual silhouette matches the planned collider or hitbox;
- artifact cleanup: no text, watermarks, UI elements, unwanted shadows, stray
  pixels, cropped limbs, merged props, or background remnants.

If a frame fails, refine the prompt with specific corrective language. Examples:

- "Render with sharp, crisp edges and no blur."
- "Strictly follow pixel art style with a limited palette."
- "Use the same character proportions, cape color, armor shape, and sword size
  as the other frames."
- "Must have a transparent background with alpha; no scene or floor."
- "Keep feet on the same baseline and center the sprite in the frame."

## Integration obligations

A game refined with this fragment should include an asset-production section that
states:

- which sprites are needed for the first playable version;
- which can be placeholder shapes until later;
- which sprite specs and frame prompts will be used for image-generation API
  calls;
- which frames are required before the game is considered playable;
- where generated PNGs, sprite sheets, metadata, and provenance are stored;
- how the build loads frame rectangles and animation definitions;
- how assets are regenerated safely without breaking filenames or animation
  keys;
- the licensing and originality constraint: do not request, imitate, or include
  unlicensed copyrighted characters, logos, sprites, or distinctive art styles
  owned by others.

## Acceptance criteria

The sprite pipeline is good enough for a first game build when:

- each required sprite has a written sprite spec;
- each frame has a concrete image-generation prompt;
- frames are generated or represented by placeholders;
- the selected frames are packed into a sheet or stored as individual PNGs;
- metadata can drive animation playback without manual coordinate guessing;
- the game can load, display, animate, and restart with the assets;
- failed or rejected frames have documented issues and refinement prompts;
- the artifact folder preserves prompts, model settings, generated images,
  selected frames, final sheets, metadata, and provenance.
