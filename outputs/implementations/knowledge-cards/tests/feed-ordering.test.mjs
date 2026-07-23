import assert from "node:assert/strict";
import test from "node:test";
import { planSessionOrder, scoreCard } from "../src/domain/feedOrdering.js";

const baseCard = (id, patch = {}) => ({
  id,
  category: patch.category ?? "foundations",
  prerequisites: patch.prerequisites ?? [],
  importance: patch.importance ?? 0.5,
  foundational_priority: patch.foundational_priority ?? 0.5,
  ...patch
});

test("importance dominates seeded jitter in adaptive scoring", () => {
  const important = baseCard("important", { importance: 1, foundational_priority: 0 });
  const randomish = baseCard("randomish", { importance: 0, foundational_priority: 0 });
  assert.ok(scoreCard(important, { seed: "x" }).total > scoreCard(randomish, { seed: "x" }).total);
});

test("adaptive order respects prerequisites and stable ties", () => {
  const cards = [
    baseCard("b-card", { importance: 0.9, prerequisites: ["a-card"] }),
    baseCard("a-card", { importance: 0.6 }),
    baseCard("c-card", { importance: 0.6 })
  ];
  const order = planSessionOrder(cards, { seed: "same" });
  assert.ok(order.indexOf("a-card") < order.indexOf("b-card"));
  assert.deepEqual(new Set(order), new Set(["a-card", "b-card", "c-card"]));
});

test("ordered and shuffled modes are deterministic", () => {
  const cards = [baseCard("a"), baseCard("b"), baseCard("c")];
  assert.deepEqual(planSessionOrder(cards, { mode: "ordered" }), ["a", "b", "c"]);
  assert.deepEqual(planSessionOrder(cards, { mode: "shuffled", seed: "s" }), planSessionOrder(cards, { mode: "shuffled", seed: "s" }));
});
