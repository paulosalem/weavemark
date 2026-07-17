import { test } from "node:test";
import assert from "node:assert/strict";

import {
  createGame,
  getRemainingSeconds,
  setMode,
  startRun,
  stepGame,
  tryBuildStation,
  tryDeleteAt,
  tryUpgradeAt
} from "../src/simulation.js";

test("a round starts with deterministic city totals", () => {
  const first = createGame(1234);
  const second = createGame(1234);

  assert.equal(first.population, second.population);
  assert.equal(first.jobs, second.jobs);
  assert.equal(first.buildings.length, 60);
  startRun(first);
  assert.equal(first.phase, "playing");
  assert.equal(Math.ceil(getRemainingSeconds(first)), 210);
});

test("player can build, select, upgrade, and prune network elements", () => {
  const game = startRun(createGame(9));

  let outcome = tryBuildStation(game, 155, 150);
  assert.equal(outcome.ok, true);
  assert.equal(game.stations.length, 1);

  outcome = tryBuildStation(game, 345, 250);
  assert.equal(outcome.ok, true);
  assert.equal(game.stations.length, 2);
  assert.equal(game.segments.length, 1);
  assert.ok(game.budget < 420);

  outcome = tryUpgradeAt(game, 155, 150);
  assert.equal(outcome.ok, true);
  assert.equal(game.stations[0].level, 2);

  outcome = tryDeleteAt(game, 345, 250);
  assert.equal(outcome.ok, true);
  assert.equal(game.stations.length, 1);
  assert.equal(game.segments.length, 0);
});

test("invalid placement protects blockers and readability", () => {
  const game = startRun(createGame(12));

  const blocked = tryBuildStation(game, 460, 90);
  assert.equal(blocked.ok, false);
  assert.match(blocked.message, /water|garden/i);

  assert.equal(tryBuildStation(game, 100, 100).ok, true);
  const tooClose = tryBuildStation(game, 122, 112);
  assert.equal(tooClose.ok, false);
  assert.match(tooClose.message, /too close|readable/i);
});

test("simulation produces agents, demand trails, trips, and feedback", () => {
  const game = startRun(createGame(42));
  assert.equal(tryBuildStation(game, 180, 140).ok, true);
  assert.equal(tryBuildStation(game, 388, 245).ok, true);
  assert.equal(tryBuildStation(game, 620, 240).ok, true);

  for (let i = 0; i < 420; i += 1) {
    stepGame(game, 0.2);
    if (game.phase === "results") {
      break;
    }
  }

  const trailTotal = game.trails.reduce((sum, value) => sum + value, 0);
  const congestionTotal = game.congestion.reduce((sum, value) => sum + value, 0);
  assert.ok(game.deliveredTrips > 0, "expected delivered trips");
  assert.ok(trailTotal > 0, "expected visible demand trails");
  assert.ok(congestionTotal > 0, "expected congestion feedback");
  assert.ok(game.score > 0, "expected score feedback");
  assert.ok(game.reliability >= 0 && game.reliability <= 1);
});

test("mode selection rejects unknown modes", () => {
  const game = createGame(1);
  assert.equal(setMode(game, "upgrade").ok, true);
  assert.equal(game.mode, "upgrade");
  assert.equal(setMode(game, "teleport").ok, false);
  assert.equal(game.mode, "upgrade");
});
