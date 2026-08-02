# Arcana browser application

This clean-room implementation was written from
`arcana-app-spec.md` against the generated `deck-data.js` and PNG deck. It does
not reuse the previous runtime source.

Serve this directory over HTTP:

```bash
python -m http.server 4197 --bind 127.0.0.1
```

Then open <http://127.0.0.1:4197/>.

## Artifact and privacy boundaries

- `deck-data.js`, `assets/cards/`, and `assets/card-back.png` are authoritative
  generated artifacts.
- Manual play is offline and makes no provider requests.
- OpenAI reflection and narration are separately optional.
- Arcana never persists the API key. A browser/password manager may restore a
  key from protected credential storage; the app identifies that state and lets
  the user keep it or replace it. Once accepted, the key and generated audio
  remain in page memory only.
- Unsaved private questions are not persisted.

## Browser support

Use a current standards-based browser with JavaScript, CSS 3D transforms,
`crypto.getRandomValues`, Web Audio, Blob URLs, and native accessibility
semantics. The app supports keyboard, pointer, touch, reduced motion, forced
colors, 200% zoom, and 320 CSS-pixel viewports.

## Validation

```bash
node --check <(sed -n '/<script>/,/<\/script>/p' index.html | tail -n +2 | sed '$d')
node --check deck-data.js
```

Browser validation covers manual and mocked-provider readings, all five
reflection depths, text/voice glow, TTS retry, card-turn and reflection geometry,
audio transport, final synthesis restoration, drawers/focus, reduced motion,
privacy/storage, and 320-pixel rendering. Per-card AI interpretation arrives
automatically in a shallow sliding top stage; manual Card reflection remains
click-only. Setup and the active OpenAI drawer also provide editable deep-question
presets.

## Limitations

- Provider features require a user-supplied OpenAI key and browser access to the
  configured endpoints.
- Browser autoplay policy may require explicit Play after narration is ready.
- Direct `file://` loading is unsupported; use static HTTP hosting.
