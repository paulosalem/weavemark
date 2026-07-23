import { nowIso, minutesBetween } from "./time.js";

export function createProgress(packId) {
  const timestamp = nowIso();
  return {
    packId,
    started_at: timestamp,
    updated_at: timestamp,
    viewed_count: 0,
    session_viewed_card_ids: [],
    completed_count: 0,
    active_card_id: null,
    last_session_started_at: timestamp,
    interactions_since_revisit: 0,
    last_revisit_at: null
  };
}

export function recordCardViewed(progress, cardId) {
  const viewed = new Set(progress.session_viewed_card_ids ?? []);
  if (viewed.has(cardId)) return progress;
  viewed.add(cardId);
  const timestamp = nowIso();
  return {
    ...progress,
    active_card_id: cardId,
    viewed_count: viewed.size,
    session_viewed_card_ids: [...viewed],
    updated_at: timestamp
  };
}

export function recordCardCompleted(progress, cardId, alreadyCompleted = false) {
  const timestamp = nowIso();
  return {
    ...progress,
    active_card_id: cardId,
    completed_count: Math.max(progress.completed_count ?? 0, 0) + (alreadyCompleted ? 0 : 1),
    interactions_since_revisit:
      Math.max(progress.interactions_since_revisit ?? 0, 0) + (alreadyCompleted ? 0 : 1),
    updated_at: timestamp
  };
}

export function shouldOfferStoppingPoint(progress, preferences, now = new Date()) {
  const cardLimit = preferences.sessionCardLimit ?? 10;
  const minuteLimit = preferences.sessionMinuteLimit ?? 10;
  return (progress.viewed_count ?? 0) >= cardLimit || minutesBetween(progress.last_session_started_at, now) >= minuteLimit;
}

export function summarizeProgress(progress, totalCards) {
  const completed = Math.min(progress.completed_count ?? 0, totalCards);
  return {
    completed,
    total: totalCards,
    percent: totalCards === 0 ? 0 : Math.round((completed / totalCards) * 100)
  };
}
