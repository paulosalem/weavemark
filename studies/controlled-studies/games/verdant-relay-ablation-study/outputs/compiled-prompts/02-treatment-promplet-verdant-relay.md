# Verdant Relay: Dense Browser-Game Implementation Spec

Build **Verdant Relay**, a playable first-build browser game where the player protects a living railway corridor from blight waves by placing and upgrading ecological defenses, playing deckbuilder cards, and maintaining ecosystem health. The specification is the source of truth for implementation, validation, tuning, assets, and acceptance.

## 1. Product intent and first-build scope

- **User value:** a compact strategy game that combines lane defense, card choices, and living-system feedback into one readable loop.
- **Target session:** 8–15 minutes, playable from first load through win/loss/restart without page reload.
- **Core fantasy:** a restoration conductor routes a verdant rail line through threatened biomes, using plants, habitats, workers, and interventions to stop blight leaks while keeping the ecosystem resilient.
- **First build includes:** one map, 3 rail lanes, 8 waves, 18 cards, 4 defense types, 4 blight types, 5 ecosystem metrics, upgrades, deterministic seeded draw/wave/event rules, original/placeholder 2D sprites, sound-ready hooks, pause/resume/restart, local progress/high-score storage, and Playwright browser validation.
- **Out of scope for first build:** multiplayer, procedural maps, account systems, monetization, network save sync, licensed IP, large content campaigns, complex pathfinding, and opaque ecological simulation.

## 2. Objective, win/loss, and core loop

### Objective

Protect the **Heartwood Station** at the end of the railway while restoring ecosystem stability.

### Win condition

The player wins after surviving wave 8 with:

- `heartwood_hp > 0`
- `ecosystem_health >= 35`
- no unresolved collapse event active

### Loss conditions

The run ends in loss when any occurs:

- `heartwood_hp <= 0`
- `ecosystem_health <= 0`
- `collapse_meter >= 100`

### Core loop

1. **Plan phase:** preview next wave, inspect lanes, draw cards, view ecosystem overlays, choose placements/upgrades/card plays.
2. **Commit phase:** spend seeds/energy, place defenses, upgrade towers, play route/intervention/habitat/recovery cards, confirm wave start.
3. **Wave phase:** blight entities move along rail lanes; defenses attack or modify lanes; cards with wave timing trigger; leaks damage Heartwood and ecosystem.
4. **Ecosystem tick:** health, diversity, resilience, fertility, and blight pressure update from wave results, cards, towers, and leaks.
5. **Reward phase:** gain seeds, choose 1 of 3 reward cards or upgrade/remove a card at milestone waves.
6. **Progression phase:** unlock next wave preview, reshuffle deck if needed, display failure/success causes, continue or end.

## 3. Readability and first-run teaching

### First 30 seconds

- Show title, Start, brief objective: “Stop blight trains from reaching Heartwood Station. Grow defenses, play cards, keep the biome healthy.”
- On Start, show a stable 16:9 game board with 3 horizontal railway lanes, Heartwood Station on the right, blight spawn side on the left, HUD at top, hand at bottom.
- Highlight one lane preview arrow and one valid tower tile.

### First minute teaching script

| Step | What appears | Player action | Feedback |
|---|---|---|---|
| 1 | Wave 1 preview: 5 Spores on Lane A | hover/click Seed Turret card or build button | range overlay, cost, valid tiles |
| 2 | One starter card glows: `Sprout Turret` | place defense | seeds decrease, tower grows animation, coverage tint |
| 3 | Start Wave button pulses | click Start Wave | train bell, wave timer, enemies spawn |
| 4 | Turret attacks Spores | observe | hit flash, hp chips, leaf particles |
| 5 | Wave cleared | choose reward | card draft, ecosystem delta summary |

### Feedback vocabulary

| Event | Visual cue | Text/audio cue |
|---|---|---|
| valid placement | green tile ring and range circle | soft chime |
| invalid placement | red crossed tile, reason tooltip | muted thud |
| attack hit | brief enemy flash, leaf projectile impact | tick sound |
| slow/root | blue-green tether and reduced speed icon | low rustle |
| leak | enemy exits right, Heartwood shake, red damage number | warning bell |
| ecosystem recovery | biome saturation increases, sprouts appear | rising chord |
| ecosystem stress | palette desaturates, cracks/vines darken | low rumble |
| synergy | linked card/tower glow, tag icon pulse | sparkle |
| collapse risk | collapse meter flashes at 75+ | alarm pulse |

### Readability budget

- Max simultaneous enemies visible: 36.
- Max simultaneous floating numbers: 8; aggregate excess.
- Max hand size: 6.
- Max card text: title, 2 tags, cost, 1–2 concise effect lines.
- Max active overlays at once: one selected overlay plus hover tooltip.
- Particles must not obscure lanes or card text.
- HUD must remain readable at 1280×720 and 1366×768; mobile is responsive but not required as primary tuning target.

## 4. Game states and UX flows

| State | Required behavior |
|---|---|
| `Loading` | show progress, preload required textures/sounds/fonts or placeholders |
| `MainMenu` | title, Start, Options, Credits, latest best score/progress |
| `PlayingPlan` | simulation paused except UI; cards/placement/upgrades available |
| `PlayingWave` | wave systems active; limited instant cards allowed |
| `Paused` | freeze gameplay timers/systems; overlay Resume, Restart, Main Menu |
| `Reward` | show rewards, deck changes, wave summary, ecosystem delta |
| `Win` | show victory summary, score, restart/main menu |
| `GameOver` | show cause, recovery lesson, score, restart/main menu |

Focus loss, tab visibility change, or Escape must pause safely. Restart must reset run state from seed without reloading the page.

## 5. Domain model and state fields

Use field lists or tables for game data; do not require fenced JSON examples.

### Global run state

| Field | Type | Notes |
|---|---|---|
| `run_id` | string | generated per run |
| `seed` | integer | controls draw order, rewards, minor ecosystem events |
| `state` | enum | `Loading`, `MainMenu`, `PlayingPlan`, `PlayingWave`, `Paused`, `Reward`, `Win`, `GameOver` |
| `wave_index` | integer | 1–8 |
| `heartwood_hp` | integer | starts 20 |
| `seeds` | integer | build/resource currency |
| `energy` | integer | card play resource per plan phase |
| `score` | integer | wave clears, health, biodiversity, unused leak buffer |
| `time_scale` | number | 0, 1, or 2 |
| `rng_cursor` | integer | deterministic seeded sequence position |

### Ecosystem state

| Field | Range | Meaning |
|---|---:|---|
| `ecosystem_health` | 0–100 | overall biome viability; loss at 0, win gate at 35 |
| `diversity` | 0–100 | improves mixed defenses/cards; prevents monoculture penalties |
| `resilience` | 0–100 | reduces damage from leaks and collapse spikes |
| `fertility` | 0–100 | affects seed income and plant-tower growth |
| `blight_pressure` | 0–100 | increases enemy strength and collapse risk |
| `collapse_meter` | 0–100 | loss at 100 |
| `biome_state` | enum | `lush`, `stable`, `stressed`, `collapsing` |

Biome state thresholds:

| State | Condition | Presentation |
|---|---|---|
| `lush` | health ≥ 75 and pressure ≤ 30 | saturated greens, flowers, brighter track |
| `stable` | health 45–74 | normal palette |
| `stressed` | health 20–44 or pressure 60–79 | brown patches, warning icons |
| `collapsing` | health < 20 or pressure ≥ 80 | dark vines, alarm, collapse meter emphasis |

### Lane state

| Field | Type | Notes |
|---|---|---|
| `lane_id` | string | `A`, `B`, `C` |
| `path_points` | list | simple straight or gently curved rail points; no complex pathfinding |
| `tile_slots` | list | buildable positions with coordinates |
| `soil_quality` | integer 0–100 | affects plant tower reload/growth |
| `blight_residue` | integer 0–100 | accumulates from leaks/deaths; raises pressure |
| `route_modifier` | enum/list | temporary card effects such as detour, cleanse, overgrowth |
| `preview_threats` | list | next wave spawn summary |

### ECS-style entities and components

All gameplay state should be componentized; avoid hidden mutable singletons. Required components include:

| Component | Key fields |
|---|---|
| `Transform` | `x`, `y`, `rotation`, `scale` |
| `Velocity` | `vx`, `vy`, `speed_multiplier` |
| `Sprite` | `asset_id`, `animation`, `frame`, `tint`, `visible` |
| `Health` | `hp`, `max_hp`, `armor`, `resistance_tags` |
| `LanePosition` | `lane_id`, `distance`, `normalized_progress` |
| `Collider` | `shape`, `radius_or_rect`, `active` |
| `Defense` | `tower_id`, `range`, `targeting`, `reload_ms`, `cooldown_ms`, `effect_type` |
| `Enemy` | `blight_type`, `reward_seeds`, `leak_damage`, `specials` |
| `ProjectileOrBeam` | `source_id`, `target_id`, `effect`, `ttl_ms` |
| `StatusEffect` | `status_id`, `duration_ms`, `stacks`, `magnitude` |
| `CardInstance` | `card_id`, `zone`, `upgraded`, `temporary_mods` |
| `EcosystemEmitter` | `metric`, `delta`, `trigger`, `source_id` |
| `PlayerInput` | selected card/tower/tile, pointer state, keyboard shortcuts |

### Persistence

Store only appropriate local browser state:

| Item | Storage | Notes |
|---|---|---|
| options | `localStorage` | volume, reduced motion, display scale |
| best score | `localStorage` | top 10 JSON-like records |
| tutorial seen | `localStorage` | boolean |
| unlocked variants | `localStorage` | optional first-build milestone flags |

## 6. Lane defense mechanics

### Protected objective

Heartwood Station sits at lane exits. Each leak deals `leak_damage` to `heartwood_hp`, increases `blight_pressure`, and may reduce ecosystem health.

### Threat movement

- Enemies follow deterministic lane paths from left to right.
- Before each wave, show lane arrows, enemy icons, counts, and notable specials.
- Movement must be readable during wave via spacing, progress, hp chips, and status icons.

### Tower/defense types

| Defense | Cost | Range | Targeting | Base effect | Upgrade path |
|---|---:|---:|---|---|---|
| `Sprout Turret` | 4 seeds | 120 px | first | 1 nature damage every 650 ms | `Rapid Leaves`: −120 ms reload; `Deep Roots`: +20% damage if soil ≥ 60 |
| `Moss Snare` | 5 seeds | 95 px aura | strongest in range | 35% slow for 1.5 s every 900 ms | `Sticky Carpet`: +15% slow; `Compost Moss`: defeated slowed enemies add fertility |
| `Pollinator Hive` | 6 seeds | 150 px | support aura | buffs nearby plant reload by 12%; raises diversity | `Swarm`: periodic 1 damage; `Cross-Pollinate`: synergy with flower cards |
| `Mycelium Relay` | 7 seeds | lane-wide node link | nearest leak-risk | chains 2 damage to residue-heavy enemies; cleans residue | `Networked`: extra chain; `Remediator`: converts residue to seeds |

### Placement rules

- Towers may be placed only on buildable slots adjacent to lanes.
- Show attack range, affected lane segments, cost, and blocked reason before placement.
- Invalid reasons: insufficient seeds, occupied slot, slot blighted, wrong phase, card requires target type.
- Selling is optional first-build; if included, refund 50% rounded down and only in plan phase.
- Repositioning is not included except via specific cards.

### Targeting modes

| Mode | Meaning |
|---|---|
| `first` | enemy closest to station |
| `strongest` | highest current hp |
| `nearest` | smallest distance to tower |
| `residue-heavy` | highest blight residue/status |

### Waves and blight types

| Blight type | HP | Speed | Leak damage | Special | Reward |
|---|---:|---:|---:|---|---:|
| `Spore` | 3 | 55 | 1 | none; teaching enemy | 1 |
| `Bramble` | 7 | 38 | 2 | armored: −1 incoming hit, min 1 | 2 |
| `Mite Swarm` | 2 | 80 | 1 | appears in clusters; vulnerable to aura | 1 |
| `Rot Cart` | 12 | 30 | 3 | leaves residue on death/leak | 3 |

Wave table:

| Wave | Lanes | Spawns | Teaches/tests | Reward |
|---:|---|---|---|---|
| 1 | A | 5 Spore | place Sprout Turret | card draft |
| 2 | A,B | 6 Spore, 2 Bramble | coverage choice | seeds + card |
| 3 | B,C | 8 Spore, 4 Mite | fast enemies and slow value | upgrade |
| 4 | A,C | 4 Bramble, 6 Spore | armor counterplay | card draft |
| 5 | A,B,C | 8 Mite, 2 Rot Cart | aura and residue | remove/upgrade card |
| 6 | B | 6 Bramble, 4 Rot Cart | single-lane pressure | card draft |
| 7 | A,B,C | mixed 24 enemies | combined threats | upgrade |
| 8 | all | 3 Rot Cart, 8 Bramble, 12 Mite, 10 Spore | final resilience test | win |

### Wave tuning rules

- Early waves teach one decision at a time.
- Later waves combine threats that require target priority, slow, cleanup, and ecosystem recovery.
- Difficulty knobs: enemy hp, speed, spawn count, lane count, spawn spacing, tower cost, reload, resource income, upgrade strength, wave reward, leak damage.
- Failure should reveal a cause: insufficient coverage, poor slow/armor response, overgrown deck, ignored ecosystem, residue collapse.

## 7. Deckbuilder system

### Card zones and economy

| Zone | Rule |
|---|---|
| `draw_pile` | shuffled deterministically from seed |
| `hand` | draw to 5 at start of plan phase; max 6 |
| `discard_pile` | played and unplayed non-exhaust cards go here after wave/reward |
| `exhaust` | one-time or run-long cards remain out until combat/run end |
| reshuffle | when draw pile empty, shuffle discard into draw using seeded RNG |

- Start each plan phase with `energy = 3`; unused energy does not carry over unless card says so.
- Cards cost energy; towers cost seeds unless card modifies.
- Card plays must show cost, valid target, previewed effect, and invalid-play reason.
- Reward: choose 1 of 3 cards after selected waves; upgrade/remove at milestones.

### Card fields

| Field | Type/values |
|---|---|
| `id` | stable identifier |
| `name` | display name |
| `cost` | 0–3 energy |
| `type` | `plant`, `habitat`, `intervention`, `route`, `resource`, `upgrade`, `recovery` |
| `timing` | `plan`, `instant_wave`, `reward`, `passive` |
| `target` | `lane`, `slot`, `tower`, `enemy`, `deck`, `ecosystem`, `none` |
| `effect` | concise rules text + implementation callback |
| `rarity` | `starter`, `common`, `uncommon`, `rare` |
| `upgrade_state` | `base`, `upgraded` |
| `tags` | e.g. `root`, `pollinator`, `cleanse`, `draw`, `slow`, `diversity` |
| `description` | 1–2 readable lines |
| `visual_state` | playable, unplayable, targeted, previewed, resolving |

### Starting deck

| Card | Count | Cost | Type | Effect |
|---|---:|---:|---|---|
| `Sprout Turret` | 2 | 1 | plant | place a discounted Sprout Turret: pay 3 seeds instead of 4 |
| `Root Snare` | 2 | 1 | intervention | slow enemies in one lane by 25% for 4 s |
| `Compost` | 1 | 0 | resource | gain 2 seeds; if lane residue ≥ 20, cleanse 5 residue |
| `Survey Route` | 1 | 0 | route | preview next wave lane details; draw 1 |
| `Wildflower Patch` | 1 | 1 | habitat | +8 diversity; nearby Pollinator Hive buff +5% |
| `Emergency Renewal` | 1 | 2 | recovery | restore 8 ecosystem health; exhaust |

### Reward card pool

| Card | Cost | Tags | Effect |
|---|---:|---|---|
| `Moss Carpet` | 1 | slow, habitat | lane slow zone + fertility if enemies die inside |
| `Mycelium Map` | 1 | cleanse, draw | cleanse 12 residue; draw 1 |
| `Pollinator Bloom` | 1 | pollinator, diversity | +12 diversity; next plant placement −1 seed |
| `Detour Switch` | 2 | route | move next 4 spawns from selected lane to least-threatened lane |
| `Rapid Germination` | 1 | upgrade, plant | selected plant tower reload −15% this wave |
| `Seed Bank` | 0 | resource | gain 1 seed now and +1 seed next reward |
| `Biochar` | 1 | cleanse, resilience | −15 pressure; +6 resilience |
| `Canopy Shield` | 2 | recovery | next 3 leaks deal −1 damage and −50% ecosystem harm |
| `Symbiosis` | 2 | diversity, upgrade | if 3 defense types exist, buff all reload by 10% |
| `Cull the Blight` | 2 | intervention | deal 4 to all enemies in one lane; +5 pressure |
| `Careful Pruning` | 1 | deck | remove a card; +4 health |
| `Railside Nursery` | 2 | plant, resource | after each wave, +1 seed if no leak in chosen lane |

### Synergy and counterplay matrix

| Synergy | Works because | Counter-risk | Guardrail |
|---|---|---|---|
| Pollinator + plant towers | reload buffs scale with multiple plants | one-tower spam | diversity bonus requires different defense types |
| Moss + Mite Swarm | aura slow handles clusters | too strong vs all enemies | Bramble armor still needs damage/cleanup |
| Mycelium + residue | cleans Rot Cart aftermath | infinite seed conversion | conversion capped per wave |
| Detour + lane towers | route choice rewards planning | trivializes waves | limited spawn count and higher cost |
| Recovery cards + leaks | comeback path | intentional leaking dominant | score penalty and pressure spike remain |

## 8. Ecosystem simulation

### Tick timing

- Ecosystem updates after each wave and from immediate card/tower effects.
- Use deterministic formulas and visible deltas; avoid hidden opaque math.
- Display a summary: health delta, pressure delta, diversity/resilience/fertility changes, and cause.

### Core formulas

| Trigger | Effect |
|---|---|
| enemy leak | `heartwood_hp -= leak_damage`; `ecosystem_health -= leak_damage * (2 - resilience/100)`; `blight_pressure += leak_damage * 3` |
| wave clear no leaks | `ecosystem_health += 4`; `fertility += 3`; score bonus |
| tower diversity count ≥ 3 | `diversity += 5` after wave |
| repeated same tower type ≥ 4 | `diversity -= 4`; monoculture warning |
| residue > 50 on a lane | `blight_pressure += 5`; lane shows stress |
| resilience ≥ 60 | reduce collapse gain by 25% |
| blight_pressure ≥ 80 | `collapse_meter += 8` after wave |
| health < 20 | `collapse_meter += 10` after wave |
| recovery card | direct health/resilience/fertility delta shown |

### Feedback loops

- **Positive recovery:** diverse towers + habitat cards raise diversity, which improves resilience, which reduces leak harm, which keeps health stable.
- **Negative collapse:** leaks and Rot Cart residue raise blight pressure; high pressure accelerates collapse and makes future waves harsher.
- **Resource loop:** fertility improves seed income; overusing extractive cards can solve a wave but lower long-term health.
- **Comeback loop:** recovery and cleanse cards can stabilize a stressed biome but cost deck tempo and energy.

### Failure explanation table

| Failure | Likely cause | Player-readable clue | Recovery lesson |
|---|---|---|---|
| Heartwood destroyed | too many leaks | lane exit flashes and leak log | add coverage/slow on weakest lane |
| ecosystem collapsed | ignored health/pressure | dark palette, collapse meter | play cleanse/recovery before pressure spikes |
| overwhelmed by Mites | no aura/slow | many fast icons bypass single-target tower | use Moss, Pollinator, lane effects |
| Brambles survive | low damage vs armor | armor icon and small hit numbers | upgrade damage or use intervention |
| deck stalls | too many expensive/narrow cards | unplayable hand tint | draft lower-cost/draw/remove cards |

## 9. Progression, balance, and tuning

### Content ladder

| Stage | New concept | Required content |
|---|---|---|
| Menu/tutorial | objective, controls | Start, short instruction, first placement highlight |
| Wave 1 | tower placement | Sprout Turret, Spore |
| Wave 2 | lane choice | second lane, Bramble preview |
| Wave 3 | speed/slow | Mite Swarm, Root Snare value |
| Wave 4 | upgrades | first tower upgrade |
| Wave 5 | residue/ecology | Rot Cart, Mycelium cleanse |
| Wave 6 | deck pressure | expensive vs cheap card decisions |
| Wave 7 | combined systems | all three lanes, mixed threats |
| Wave 8 | mastery | final mixed wave and ecosystem win gate |

### Balance table

| Parameter | Initial | Safe range | Player-facing effect | Too low | Too high | Adjustment rule |
|---|---:|---:|---|---|---|---|
| `heartwood_hp` | 20 | 15–30 | leak forgiveness | harsh early losses | leaks meaningless | tune after wave 4 leak rate |
| start seeds | 8 | 6–12 | opening build freedom | no real choice | trivial first waves | ensure 1–2 viable builds |
| energy/turn | 3 | 2–4 | card tempo | dead hands | spam combos | keep average playable cards 2–3 |
| Sprout reload | 650 ms | 500–850 | baseline DPS | too strong | feels weak | Wave 1 clear with 1 tower, some tension |
| Mite speed | 80 | 65–95 | fast pressure | indistinct | unreadable | maintain visible reaction time |
| residue pressure gain | 5 | 3–8 | ecology stakes | ignored | death spiral | allow cleanse recovery within 2 waves |
| reward card count | 3 | 2–4 | draft agency | narrow choices | analysis paralysis | keep first build at 3 |
| max enemies | 36 | 24–45 | spectacle/load | sparse | clutter/jank | cap by readability/performance |

### Dominant-strategy risks

- Tower spam must be checked by diversity and lane-specific threats.
- Recovery spam must cost tempo and cannot erase bad wave defense.
- Detour effects must be limited so route manipulation does not replace defense.
- Damage-only builds must struggle with Mites/residue.
- Slow-only builds must struggle with Bramble/Rot Cart health.

### Playtest questions

- Does a new player know where enemies travel before clicking Start Wave?
- Can players explain why a card is unplayable?
- Do wave results clearly tie actions to ecosystem deltas?
- Are reward choices meaningful or is one card always correct?
- Is any loss perceived as unfair hidden math?
- Can the player recover from one early leak without the run becoming trivial?

### Release balance gate

A credible first vertical slice should have at least 3 tested runs where:

- a first-time player or tester reaches wave 3 without external explanation;
- an experienced tester can win with 2 distinct deck/defense approaches;
- average frame rate remains stable on ordinary laptop browser;
- no unavoidable wave exists under reasonable play;
- no single dominant strategy wins while ignoring ecosystem and deck decisions.

## 10. UI, controls, accessibility, and feel

### Layout

- Center: 3-lane railway map with build slots and visible Heartwood Station.
- Top HUD: wave, Heartwood HP, seeds, energy, score, ecosystem bars, pause.
- Left/right side panel: selected tower/card details, next wave preview, ecosystem overlay toggle.
- Bottom: hand of cards, draw/discard/exhaust counts, end/Start Wave button.
- Reward overlay: 3 cards plus skip/remove/upgrade when applicable.

### Controls

| Input | Action |
|---|---|
| mouse/touch click | select card/tower/tile/button |
| drag card to target | play targeted card |
| hover/focus | tooltip and preview |
| `Space` | start wave or confirm safe prompt |
| `Esc` | pause/resume/cancel selection |
| `1`–`6` | select hand card |
| `Tab` | keyboard focus traversal |

### Accessibility

- Keyboard-accessible buttons/cards with visible focus.
- Text contrast meets readable standards against game board.
- Reduced motion option disables shake/large particles while preserving feedback.
- Tooltips available by focus, not hover only.
- Important cues use shape/text/icon in addition to color.

### Feel checks

- Card hover/select response under 50 ms.
- Placement preview updates immediately.
- Attack animation cadence matches reload.
- Pause freezes enemies, projectiles, timers, and card resolution queues.
- Hit feedback is legible but does not hide lanes.
- Screen shake limited to leak/damage, amplitude up to 4 px, decay about 0.3 s.

## 11. Architecture and implementation notes

### Technology expectations

- Browser-first implementation using the project’s existing stack if present; otherwise minimal Vite/TypeScript/Canvas or HTML5 Canvas setup is acceptable.
- Keep simulation deterministic and inspectable.
- Separate simulation, rendering, input, assets, UI state, and persistence.

### Main modules

| Module | Responsibilities |
|---|---|
| `GameApp` | boot, state transitions, main loop, pause/resume/restart |
| `Simulation` | wave ticks, enemy movement, tower targeting, card effects, ecosystem updates |
| `ECSStore` | entities, components, queries, lifecycle |
| `DeckSystem` | draw, hand, discard, exhaust, rewards, upgrades/removals |
| `WaveSystem` | deterministic spawn schedule and wave completion |
| `TowerSystem` | placement, upgrades, targeting, attack cadence |
| `EcosystemSystem` | metric formulas, biome state, collapse checks |
| `Renderer` | canvas drawing, sprites, overlays, particles, HUD hooks |
| `InputController` | pointer/keyboard/touch mapping and accessibility focus |
| `AssetManager` | load placeholders/sprites/sounds/fonts, manifest metadata |
| `Persistence` | local options, best scores, tutorial flag |
| `ValidationHarness` | deterministic shortcuts/helpers for Playwright smoke tests |

### Update loop

1. Process input events and UI commands.
2. If playing and not paused, advance fixed simulation step.
3. Run systems: wave spawn, movement, targeting, attacks, statuses, card queues, ecosystem triggers, win/loss checks.
4. Render frame from immutable-ish snapshot.
5. Record debug counters for validation: enemies spawned/defeated/leaked, cards played, towers placed/upgraded, ecosystem deltas.

### Performance

- Use fixed timestep with interpolation or stable delta clamping.
- Cap enemy/projectile counts.
- Pool short-lived projectiles/particles.
- Avoid layout shifts during play; canvas/game area size stable.
- Defer heavy assets; placeholders must allow full gameplay before final art.
- No console errors in validated flows.

## 12. Asset and sprite production

### Originality and licensing

Do not request, imitate, or include unlicensed copyrighted characters, logos, sprites, names, music, fonts, or distinctive owned styles. Use original nature-railway pixel/cartoon art direction.

### Art direction

- Style: readable 2D pixel-art-inspired or crisp cartoon sprites, limited palette, strong silhouettes, no painterly blur.
- View: slight top-down/side hybrid suitable for horizontal lanes.
- Palette: verdant greens, warm rail browns, cream UI, blight purples/charcoal.
- Minimum: placeholders may be geometric but must preserve gameplay readability.

### Required first-build assets

| Asset | Size | Animations/states | Notes |
|---|---:|---|---|
| Heartwood Station | 128×128 | stable, damaged, critical | visible protected objective |
| rail lane tiles | 64×64 | normal, blighted, restored | tileable |
| Sprout Turret | 64×64 | idle 4f, attack 4f, upgrade glow | plant silhouette |
| Moss Snare | 64×64 | idle 4f, pulse 4f | ground aura readable |
| Pollinator Hive | 64×64 | idle 4f, swarm 6f | support identity |
| Mycelium Relay | 64×64 | idle 4f, chain 4f | network effect |
| Spore enemy | 48×48 | move 4f, hit 2f, die 4f | basic |
| Bramble enemy | 48×48 | move 4f, hit 2f, die 4f | armor icon |
| Mite Swarm | 48×48 | move 4f, scatter 4f | fast cluster |
| Rot Cart | 64×48 | roll 4f, leak 4f, die 4f | residue source |
| card frames/icons | variable | playable/unplayable/targeted | tags/costs readable |
| particles | small | hit, heal, leak, cleanse | optional but useful |

### Sprite specification fields

For each generated sprite, maintain:

| Field | Required content |
|---|---|
| `name` | stable asset identifier |
| `description` | role, silhouette, palette, gameplay state |
| `style` | concrete style phrase |
| `frame_width` / `frame_height` | target pixel size |
| `background_color` | `transparent` for reusable sprites |
| `animations` | name, frame count, FPS, loop flag, pose/motion description |
| `additional_prompt` | no text, no UI, no scene background, centered, consistent palette |

### Frame prompt rules

Generate or request individual frames first, then pack deterministically. Each frame prompt must include frame size, sprite identity, style, animation name, frame index, pose/progress, transparent background, consistency constraints, and “no text, no UI, no extra characters, no scene background.” Repeat canonical appearance in every frame prompt.

### Packing and metadata

| Requirement | Rule |
|---|---|
| frame order | sorted by animation and frame index |
| packing | horizontal strip or grid atlas |
| padding | include if scaling causes bleeding |
| metadata | sheet image, frame size, frame rectangles `x`, `y`, `w`, `h`, animation definitions |
| filenames | stable paths such as `assets/sprites/sprout_turret.png` and `assets/sprites/sprout_turret.json` |
| provenance | store prompts, model/settings if generated, selected/rejected frames, refinement notes |

### Asset quality checks

- Readable at actual in-game scale.
- Transparent backgrounds where required.
- Consistent proportions, palette, outline, lighting, and view angle.
- Stable feet/contact points and centers.
- Animation plays smoothly at declared FPS and loops cleanly when `loop: true`.
- Collision footprint matches silhouette.
- No text, watermark, UI, background remnants, stray pixels, cropped limbs, or unintended props.

## 13. Validation plan with Playwright MCP

### Tool setup

- Before claiming browser validation, check whether Playwright MCP or equivalent browser automation is available.
- If unavailable and Node/npm can be used, configure the official MCP server, commonly with `npx @playwright/mcp@latest`.
- If project tests need Playwright, add it through the project package manager and install browsers with the project-appropriate command.
- If MCP setup cannot be completed, state the exact blocker; do not claim real browser validation.

### Browser-grounded build loop

The implementing agent must repeat:

1. Inspect spec, repository, scripts, framework conventions, and tests.
2. Implement the smallest visible playable slice.
3. Start the app with existing dev/preview command, or add the minimal appropriate command.
4. Open the URL through Playwright MCP.
5. Interact as a real player: start, place, draw/play cards, upgrade, run waves, pause/resume, leak/win/lose, restart.
6. Observe rendered page, accessibility tree, console, screenshots/traces, network, and persisted state.
7. Compare observations to this spec; fix clarity, responsiveness, stability, accessibility, polish, and console/runtime errors.
8. Repeat until no high-value visible defect remains.

### Required smoke flows

| Flow | Steps | Expected evidence |
|---|---|---|
| load/menu | open app, inspect title/menu/options | screenshot, no console errors |
| start/tutorial | click Start, observe lanes/HUD/hand | screenshot, first-run cues visible |
| card draw/play | select valid and invalid cards | hand changes, invalid reason, effect preview |
| placement/upgrade | place tower, attempt invalid placement, upgrade | range/cost/blocked feedback |
| wave resolution | start wave, observe attacks/leaks/clear | enemy movement, hp/status, reward |
| ecosystem feedback | cause health/pressure/recovery delta | overlay and summary explain cause |
| pause/resume | pause during wave, resume | timers freeze and continue |
| restart | restart from GameOver/Win/Pause | run resets without page reload |
| win/loss | force or play to win/loss path | result summary and recovery lesson |

### Evidence checklist

Record command, tested URL, browser/device viewport, flows exercised, screenshots/traces, console/network/runtime errors found/resolved, persisted state checked, and remaining limitations. Final reporting must distinguish verified behavior from assumptions.

## 14. Acceptance criteria

The first build is complete only when all must-have criteria pass:

### Product/gameplay

- Player can load the page, understand the goal, start a run, play a complete round, win or lose, and restart without page reload.
- Lane paths, wave previews, tower ranges, card costs, invalid actions, leaks, rewards, and ecosystem deltas are visible and understandable.
- Tower defense, deckbuilder, and ecosystem systems all materially affect decisions; none is decorative.
- Deterministic waves and seeded draws/events produce reproducible validation runs.
- Failure summaries identify a plausible broken relationship and recovery lesson.

### Implementation

- Game state model includes loading/menu/playing/paused/reward/win/loss/restart.
- Simulation, rendering, input, card/deck, wave, tower, ecosystem, asset, and persistence responsibilities are separated.
- ECS-style entities/components represent gameplay objects; no hidden global mutable singleton drives core logic.
- Browser performance remains stable under max first-build enemy/effect counts.
- Pause/resume and focus loss safely suspend gameplay.
- Local settings/progress storage works and does not corrupt restart.

### Assets

- All required sprites have either final original assets or readable placeholders.
- Sprite specs, frame prompts, sprite sheets/individual PNGs, metadata, and provenance are stored or stubbed in a maintainable asset folder.
- Game loads, displays, animates, and restarts with the assets.
- No unlicensed copyrighted art, music, fonts, names, or distinctive styles are included.

### Validation

- Playwright MCP or equivalent browser validation has exercised the required smoke flows.
- The validation pass includes real interaction, not only build success or static screenshots.
- Console/runtime errors in required flows are fixed or explicitly documented with blocker severity.
- Release report includes command, URL, viewport, tested flows, screenshots/traces when available, and verified/unverified distinction.

## 15. Risks and mitigation

| Risk | Mitigation |
|---|---|
| systems become unreadable | enforce readability budget, first-run script, overlays, concise cards |
| ecology feels arbitrary | show formulas/deltas/causes; keep simple deterministic rules |
| deckbuilder dominates defense | card effects support/modify lane decisions; require towers for reliable damage |
| tower defense ignores ecology | leaks/residue/health/pressure directly affect win/loss and rewards |
| dominant strategy emerges | use synergy/counterplay matrix and balance table |
| asset generation delays implementation | placeholders are acceptable; preserve sprite specs and metadata pipeline |
| browser validation unavailable | document blocker; do not claim validation; provide manual fallback checklist |
| performance jank | cap entities/particles, pool objects, stable canvas, fixed timestep |

## 16. Required final implementation report

The implementing agent’s final response should include:

- files changed and how to run;
- gameplay summary and controls;
- content implemented: waves, towers, cards, ecosystem metrics, assets;
- validation evidence: command, URL, Playwright/browser flows, screenshots/traces if available;
- known limitations and follow-up opportunities;
- explicit release-gate status: pass/fail for gameplay, implementation, assets, and validation.