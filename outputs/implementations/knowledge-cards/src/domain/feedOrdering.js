import { DEFAULT_SESSION_SEED } from "../config.js";

export function normalizeSignals(cards) {
  return cards.map((card) => ({
    ...card,
    _normalized: {
      importance: clamp01(card.importance),
      foundational_priority: clamp01(card.foundational_priority)
    }
  }));
}

export function scoreCard(card, context = {}) {
  const normalized = card._normalized ?? {
    importance: clamp01(card.importance),
    foundational_priority: clamp01(card.foundational_priority)
  };
  const coverageGap = coverageGapFor(card, context.categoryCounts ?? new Map());
  const diversity = recentCategoryDiversity(card, context.recentCategories ?? []);
  const jitter = seededJitter(`${context.seed ?? DEFAULT_SESSION_SEED}:${card.id}`);
  return {
    total:
      0.5 * normalized.importance +
      0.2 * normalized.foundational_priority +
      0.15 * coverageGap +
      0.1 * diversity +
      0.05 * jitter,
    parts: {
      importance: normalized.importance,
      foundational_priority: normalized.foundational_priority,
      coverage_gap: coverageGap,
      recent_category_diversity: diversity,
      seeded_jitter: jitter
    }
  };
}

export function planSessionOrder(cards, options = {}) {
  const mode = options.mode ?? "adaptive";
  const seed = options.seed ?? DEFAULT_SESSION_SEED;
  const completed = new Set(options.completedCardIds ?? []);
  const unseen = new Map(normalizeSignals(cards).filter((card) => !completed.has(card.id)).map((card) => [card.id, card]));

  if (mode === "ordered") return cards.map((card) => card.id);
  if (mode === "shuffled") return stableShuffle(cards.map((card) => card.id), seed);

  const order = [];
  const categoryCounts = new Map();
  const recentCategories = [];
  while (unseen.size > 0) {
    const eligible = [...unseen.values()].filter((card) => card.prerequisites.every((id) => completed.has(id)));
    if (eligible.length === 0) {
      const remaining = [...unseen.keys()].sort();
      throw new Error(`No prerequisite-safe card is eligible; remaining cards: ${remaining.join(", ")}`);
    }
    eligible.sort((a, b) => {
      const scoreA = scoreCard(a, { seed, categoryCounts, recentCategories }).total;
      const scoreB = scoreCard(b, { seed, categoryCounts, recentCategories }).total;
      if (scoreB !== scoreA) return scoreB - scoreA;
      return a.id.localeCompare(b.id);
    });
    const next = eligible[0];
    order.push(next.id);
    unseen.delete(next.id);
    completed.add(next.id);
    categoryCounts.set(next.category, (categoryCounts.get(next.category) ?? 0) + 1);
    recentCategories.unshift(next.category);
    recentCategories.length = Math.min(recentCategories.length, 4);
  }
  return order;
}

export function chooseRevisitCard(cards, cardStates, interactionsSinceLastRevisit = 0) {
  if (interactionsSinceLastRevisit < 5) return null;
  const due = cards
    .filter((card) => card.review_prompts?.length > 0)
    .map((card) => ({ card, state: cardStates.get(card.id) }))
    .filter(({ state }) => state?.revisitRequested || state?.understanding === "low")
    .sort((a, b) => String(a.state?.updated_at ?? "").localeCompare(String(b.state?.updated_at ?? "")));
  return due[0]?.card ?? null;
}

function coverageGapFor(card, counts) {
  const values = [...counts.values()];
  if (values.length === 0) return 1;
  const max = Math.max(...values, 1);
  const current = counts.get(card.category) ?? 0;
  return clamp01(1 - current / (max + 1));
}

function recentCategoryDiversity(card, recentCategories) {
  if (recentCategories.length === 0) return 1;
  return recentCategories.includes(card.category) ? 0.2 : 1;
}

function stableShuffle(ids, seed) {
  return ids
    .map((id) => ({ id, value: seededJitter(`${seed}:${id}`) }))
    .sort((a, b) => (a.value === b.value ? a.id.localeCompare(b.id) : a.value - b.value))
    .map((item) => item.id);
}

function seededJitter(input) {
  let hash = 2166136261;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0) / 4294967295;
}

function clamp01(value) {
  return Math.max(0, Math.min(1, Number(value) || 0));
}
