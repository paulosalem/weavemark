import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  COURSE,
  GAME_STATE,
  PHYSICS,
  computeGravityAcceleration,
  createInitialGameState,
  restartGame,
  setPaused,
  startRace,
  updateGame,
} from "../src/engine.js";

describe("Orbital Drift engine", () => {
  it("advances only when the active checkpoint is crossed", () => {
    const state = createInitialGameState();
    startRace(state);

    moveCraftTo(state, COURSE.checkpoints[1]);
    updateGame(state, {}, 1 / 60);
    assert.equal(state.progress.nextCheckpoint, 0);

    moveCraftTo(state, COURSE.checkpoints[0]);
    updateGame(state, {}, 1 / 60);
    assert.equal(state.progress.nextCheckpoint, 1);
  });

  it("increments laps only after the full gate sequence and finish gate", () => {
    const state = createInitialGameState();
    startRace(state);

    completeGateSequence(state);
    moveCraftTo(state, COURSE.startGate);
    updateGame(state, {}, 1 / 60);

    assert.equal(state.state, GAME_STATE.PLAYING);
    assert.equal(state.progress.lap, 2);
    assert.equal(state.progress.nextCheckpoint, 0);

    completeGateSequence(state);
    moveCraftTo(state, COURSE.startGate);
    updateGame(state, {}, 1 / 60);

    assert.equal(state.state, GAME_STATE.FINISHED);
    assert.equal(typeof state.timer.final, "number");
  });

  it("does not advance timer or physics while paused", () => {
    const state = createInitialGameState();
    startRace(state);
    updateGame(state, { thrust: true }, 1);
    const elapsedAfterPlay = state.timer.elapsed;
    const xAfterPlay = state.craft.x;

    setPaused(state, true);
    updateGame(state, { thrust: true }, 1);

    assert.equal(state.timer.elapsed, elapsedAfterPlay);
    assert.equal(state.craft.x, xAfterPlay);
  });

  it("restarts transient race state while preserving local best time", () => {
    const state = createInitialGameState({ bestTime: 42.2 });
    startRace(state);
    moveCraftTo(state, COURSE.checkpoints[0]);
    updateGame(state, {}, 1 / 60);

    const restarted = restartGame(state);

    assert.equal(restarted.state, GAME_STATE.READY);
    assert.equal(restarted.progress.lap, 1);
    assert.equal(restarted.progress.nextCheckpoint, 0);
    assert.equal(restarted.timer.elapsed, 0);
    assert.equal(restarted.bestTime, 42.2);
  });

  it("caps gravity acceleration so wells remain recoverable", () => {
    const well = COURSE.gravityWells[0];
    const acceleration = computeGravityAcceleration({ x: well.x + 1, y: well.y }, well);
    const magnitude = Math.hypot(acceleration.ax, acceleration.ay);

    assert.ok(magnitude <= PHYSICS.MAX_GRAVITY_ACCELERATION);
    assert.ok(magnitude > 0);
  });

  it("applies a deterministic collision penalty and bounce", () => {
    const state = createInitialGameState();
    startRace(state);
    moveCraftTo(state, COURSE.asteroids[0]);

    updateGame(state, {}, 1 / 60);

    assert.ok(state.timer.elapsed >= PHYSICS.COLLISION_PENALTY_SECONDS);
    assert.ok(state.effects.collision > 0);
    assert.ok(Math.hypot(state.craft.vx, state.craft.vy) > 0);
  });
});

function completeGateSequence(state) {
  for (const checkpoint of COURSE.checkpoints) {
    moveCraftTo(state, checkpoint);
    updateGame(state, {}, 1 / 60);
  }
}

function moveCraftTo(state, point) {
  state.craft.x = point.x;
  state.craft.y = point.y;
  state.craft.vx = 0;
  state.craft.vy = 0;
}
