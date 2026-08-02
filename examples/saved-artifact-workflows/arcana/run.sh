#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

CARDS_SPEC="promplets/catalog/arcana/cards.weavemark.md"
APP_SPEC="promplets/catalog/arcana/app.weavemark.md"
VARS="examples/saved-artifact-workflows/arcana/inputs/vars.json"
OUT="examples/saved-artifact-workflows/arcana/outputs"
CARD_STAMP="$OUT/cards-build.sha256"
CARD_ARTIFACT_MANIFEST="$OUT/cards-artifacts.sha256"
CARD_COMPILE_OUTPUT="$OUT/cards-compile.tmp.json"
TEXT_MODEL="gpt-5.6-terra"
IMAGE_MODEL="gpt-image-2"
FORCE_CARDS=false
trap 'rm -f "$CARD_COMPILE_OUTPUT" "$CARD_ARTIFACT_MANIFEST.tmp" "$CARD_ARTIFACT_MANIFEST.current"' EXIT

if [[ "${1:-}" == "--regenerate-cards" ]]; then
  FORCE_CARDS=true
elif [[ $# -gt 0 ]]; then
  printf 'Usage: %s [--regenerate-cards]\n' "$0" >&2
  exit 2
fi

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n\n' "$1"
}

hash_stream() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | awk '{print $1}'
  else
    shasum -a 256 | awk '{print $1}'
  fi
}

generation_fingerprint() {
  {
    printf 'text-model=%s\nimage-model=%s\n' "$TEXT_MODEL" "$IMAGE_MODEL"
    cat "$CARDS_SPEC"
    printf '\0'
    # App-only configuration must not force expensive card/image regeneration.
    jq -cS '{deck: (.deck | del(.ai_guide))}' "$VARS"
  } | hash_stream
}

is_hydrated_png() {
  local signature
  [[ -s "$1" ]] || return 1
  signature="$(od -An -tx1 -N8 "$1" | tr -d '[:space:]')"
  [[ "$signature" == "89504e470d0a1a0a" ]]
}

non_prototype_count() {
  jq -er '.deck.production.non_prototype_count
           | select(type == "number" and . >= 1)
           | floor' "$VARS"
}

png_artifacts_complete() {
  local count index
  count="$(non_prototype_count)"
  [[ -n "$count" ]]
  [[ -s "$OUT/deck-data.js" ]]
  is_hydrated_png "$OUT/assets/cards/prototype.png"
  is_hydrated_png "$OUT/assets/card-back.png"
  for ((index = 1; index <= count; index++)); do
    is_hydrated_png "$OUT/assets/cards/card-$index.png"
  done
}

hash_artifact_files() {
  local count index
  count="$(non_prototype_count)"
  local files=("assets/cards/prototype.png")
  for ((index = 1; index <= count; index++)); do
    files+=("assets/cards/card-$index.png")
  done
  files+=("assets/card-back.png")
  (
    cd "$OUT"
    if command -v sha256sum >/dev/null 2>&1; then
      sha256sum "${files[@]}"
    else
      shasum -a 256 "${files[@]}"
    fi
  )
}

write_artifact_manifest() {
  local temporary="$CARD_ARTIFACT_MANIFEST.tmp"
  hash_artifact_files >"$temporary"
  if awk '{print $1}' "$temporary" | sort | uniq -d | grep -q .; then
    rm -f "$temporary"
    printf 'Generated Arcana card artifacts contain duplicate PNG content.\n' >&2
    return 1
  fi
  mv "$temporary" "$CARD_ARTIFACT_MANIFEST"
}

artifact_manifest_matches() {
  [[ -s "$CARD_ARTIFACT_MANIFEST" ]] || return 1
  local current temporary
  temporary="$CARD_ARTIFACT_MANIFEST.current"
  hash_artifact_files >"$temporary"
  current=true
  cmp -s "$CARD_ARTIFACT_MANIFEST" "$temporary" || current=false
  rm -f "$temporary"
  $current
}

card_artifacts_complete() {
  png_artifacts_complete && artifact_manifest_matches
}

validate_deck_input() {
  if ! command -v jq >/dev/null 2>&1; then
    printf 'Arcana build requires jq for deterministic deck validation.\n' >&2
    return 1
  fi
  jq -e '
    .deck as $deck
    | ([ $deck.prototype_card ]
       + ($deck.cards | to_entries | sort_by(.key | tonumber) | map(.value))) as $cards
    | ($deck.card_count == ($cards | length))
      and ($deck.production.non_prototype_count == ($deck.cards | length))
      and (($deck.cards | keys_unsorted)
           == [range(1; $deck.production.non_prototype_count + 1) | tostring])
      and (($cards | map(.id) | unique | length) == $deck.card_count)
      and (($cards | map(.number) | sort) == [range(1; $deck.card_count + 1)])
      and (($cards | map(select(.category == "major")) | length)
           == $deck.arcana.major.count)
      and (($cards | map(select(.category == "minor")) | length)
           == $deck.arcana.minor.count)
      and (($deck.arcana.major.count * 2) < $deck.arcana.minor.count)
      and all($cards[];
        (.title | type == "string" and length > 0)
        and (.concept_source.domains | type == "array" and length > 0)
        and (.concept_source.factual_anchor | type == "string" and length > 0)
        and (.concept_source.reflective_bridge | type == "string" and length > 0)
        and (.concept_source.epistemic_boundary | type == "string" and length > 0)
        and (.motifs | type == "array" and length > 0)
        and all(.motifs[]; $deck.motifs[.] != null)
        and (if .category == "minor"
             then ($deck.suits[.suit] != null and $deck.ranks[.rank] != null)
             else (.suit == null and .rank == null)
             end))
      and all($deck.formations[];
        (.positions | type == "array" and length > 0)
        and all(.positions[]; (.draw_from == "any"
                               or .draw_from == "major"
                               or .draw_from == "minor"))
        and (([.positions[] | select(.draw_from == "major")] | length)
             <= $deck.arcana.major.count)
        and (([.positions[] | select(.draw_from == "minor")] | length)
             <= $deck.arcana.minor.count))
      and ($deck.ai_guide.endpoint == "https://api.openai.com/v1/responses")
      and ($deck.ai_guide.model == "gpt-5.4-mini")
      and ($deck.ai_guide.speech.endpoint
           == "https://api.openai.com/v1/audio/speech")
      and ($deck.ai_guide.speech.model == "gpt-4o-mini-tts")
      and ($deck.ai_guide.speech.voice == "onyx")
      and ($deck.ai_guide.reflection_depth.minimum == 1)
      and ($deck.ai_guide.reflection_depth.maximum == 5)
      and ($deck.ai_guide.reflection_depth.default >= 1)
      and ($deck.ai_guide.reflection_depth.default <= 5)
  ' "$VARS" >/dev/null || {
    printf 'Arcana deck input failed deterministic validation.\n' >&2
    return 1
  }
}

validate_deck_input
mkdir -p "$OUT"
current_fingerprint="$(generation_fingerprint)"
recorded_fingerprint=""
if [[ -f "$CARD_STAMP" ]]; then
  recorded_fingerprint="$(tr -d '[:space:]' <"$CARD_STAMP")"
fi

if $FORCE_CARDS ||
  [[ "$recorded_fingerprint" != "$current_fingerprint" ]] ||
  ! card_artifacts_complete; then
  section "Arcana cards: generate content and artwork"
  # Streaming generation may replace files incrementally. Invalidate the prior
  # proof before the first write so a failed run can never bless a mixed deck.
  rm -f "$CARD_STAMP" "$CARD_ARTIFACT_MANIFEST"
  weavemark "$CARDS_SPEC" \
    --vars-file "$VARS" \
    --model "$TEXT_MODEL" \
    --image-model "$IMAGE_MODEL" \
    --run \
    --output-dir "$OUT" \
    --batch-only \
    --verbose
  png_artifacts_complete
  write_artifact_manifest
  printf '%s\n' "$current_fingerprint" >"$CARD_STAMP"
else
  section "Arcana cards: reuse validated generated artifacts"
  printf 'Generation fingerprint unchanged: %s\n' "$current_fingerprint"
  # Compile without --run to refresh deck-data.js while leaving the validated
  # PNG artifacts untouched. The primary compile document is transient.
  weavemark "$CARDS_SPEC" \
    --vars-file "$VARS" \
    --model "$TEXT_MODEL" \
    --format json \
    --output "$CARD_COMPILE_OUTPUT" \
    --batch-only \
    --no-file-summary
fi

section "Arcana app: always compile implementation specification"
weavemark "$APP_SPEC" \
  --vars-file "$VARS" \
  --model "$TEXT_MODEL" \
  --output "$OUT/arcana-app-spec.md" \
  --batch-only \
  --no-file-summary

section "Arcana artifacts"
printf '%s\n' \
  "- $OUT/deck-data.js" \
  "- $CARD_ARTIFACT_MANIFEST" \
  "- $OUT/assets/cards/" \
  "- $OUT/assets/card-back.png" \
  "- $OUT/arcana-app-spec.md"
