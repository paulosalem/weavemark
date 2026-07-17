import assert from "node:assert/strict";
import test from "node:test";

import {
  attemptPlaceStation,
  beginRound,
  createGameState,
  endRound,
  eraseLastStation,
  getSnapshot,
  updateGame,
  upgradeStation
} from "../src/simulation.js";

test("a round can start, build a readable line, upgrade, and prune", () => {
  const state = beginRound(createGameState());

  const first = attemptPlaceStation(state, 160, 152);
  const second = attemptPlaceStation(state, 424, 160);
  const third = attemptPlaceStation(state, 688, 272);

  assert.equal(first.ok, true);
  assert.equal(second.ok, true);
  assert.equal(third.ok, true);
  assert.equal(getSnapshot(state).stops, 3);
  assert.ok(state.budget < 260);

  const upgrade = upgradeStation(state, second.station.id);
  assert.equal(upgrade.ok, true);
  assert.equal(upgrade.station.level, 2);

  const pruned = eraseLastStation(state);
  assert.equal(pruned.ok, true);
  assert.equal(getSnapshot(state).stops, 2);
});

test("simulation produces swarm demand, trip feedback, and city growth", () => {
  const state = beginRound(createGameState());
  attemptPlaceStation(state, 160, 152);
  attemptPlaceStation(state, 424, 160);
  attemptPlaceStation(state, 688, 272);
  const startingPopulation = state.population;

  for (let i = 0; i < 720; i += 1) {
    updateGame(state, 1 / 30);
  }

  const trailTotal = state.trail.reduce((total, value) => total + value, 0);
  assert.ok(trailTotal > 0, "demand trails should be reinforced by moving agents");
  assert.ok(state.served + state.missed > 0, "trips should complete during active simulation");
  assert.ok(state.population >= startingPopulation * 0.98, "city population should remain stable or grow");
  assert.ok(Number.isFinite(state.reliability));
});

test("a round can finish and produce restart-safe result data", () => {
  const state = beginRound(createGameState());
  attemptPlaceStation(state, 160, 152);
  attemptPlaceStation(state, 424, 160);
  updateGame(state, 1);

  const result = endRound(state, "complete");
  assert.equal(state.status, "results");
  assert.ok(["win", "loss"].includes(result.outcome));
  assert.equal(result.score, Math.round(state.score));
});
