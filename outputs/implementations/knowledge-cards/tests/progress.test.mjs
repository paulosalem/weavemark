import assert from "node:assert/strict";
import test from "node:test";
import {
  createProgress,
  recordCardCompleted,
  recordCardViewed,
  shouldOfferStoppingPoint
} from "../src/domain/progress.js";

test("view progress counts unique cards within a session", () => {
  const initial = createProgress("pack");
  const first = recordCardViewed(initial, "card-1");
  const repeated = recordCardViewed(first, "card-1");
  const second = recordCardViewed(repeated, "card-2");

  assert.equal(first.viewed_count, 1);
  assert.equal(repeated.viewed_count, 1);
  assert.equal(second.viewed_count, 2);
  assert.deepEqual(second.session_viewed_card_ids, ["card-1", "card-2"]);
});

test("completion progress increments once per card", () => {
  const initial = createProgress("pack");
  const first = recordCardCompleted(initial, "card-1", false);
  const repeated = recordCardCompleted(first, "card-1", true);

  assert.equal(first.completed_count, 1);
  assert.equal(repeated.completed_count, 1);
  assert.equal(repeated.interactions_since_revisit, 1);
});

test("stopping point respects either cards or elapsed minutes", () => {
  const initial = createProgress("pack");
  const preferences = { sessionCardLimit: 10, sessionMinuteLimit: 10 };
  const tenCards = { ...initial, viewed_count: 10 };
  const elevenMinutes = {
    ...initial,
    last_session_started_at: new Date(Date.now() - 11 * 60_000).toISOString()
  };

  assert.equal(shouldOfferStoppingPoint(tenCards, preferences), true);
  assert.equal(shouldOfferStoppingPoint(elevenMinutes, preferences), true);
  assert.equal(shouldOfferStoppingPoint(initial, preferences), false);
});
