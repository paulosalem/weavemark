import test from "node:test";
import assert from "node:assert/strict";
import { SerializedSaveQueue } from "../src/save-queue.js";

test("coalesces rapid schedules without losing the final committed state", async () => {
  const calls = [];
  const queue = new SerializedSaveQueue(async () => {
    calls.push("save");
  });
  queue.schedule(10_000);
  queue.schedule(10_000);
  queue.schedule(10_000);
  await queue.flush();
  assert.deepEqual(calls, ["save"]);
  assert.equal(queue.pending, false);
});

test("serializes a change scheduled during an in-flight save", async () => {
  const calls = [];
  let release;
  const first = new Promise((resolve) => {
    release = resolve;
  });
  const queue = new SerializedSaveQueue(async () => {
    calls.push(calls.length + 1);
    if (calls.length === 1) await first;
  });
  queue.schedule(10_000);
  const flush = queue.flush();
  await Promise.resolve();
  queue.schedule(10_000);
  release();
  await flush;
  await queue.flush();
  assert.deepEqual(calls, [1, 2]);
});

test("separates explicit flush scheduling from workspace save options", async () => {
  const received = [];
  const queue = new SerializedSaveQueue(async (options) => {
    received.push(options);
  });
  await queue.flush({ runIfClean: true });
  await queue.flush({
    runIfClean: true,
    saveOptions: { force: true, recovery: true },
  });
  assert.deepEqual(received, [{}, { force: true, recovery: true }]);
});

test("a rejected save fails its caller without poisoning later saves", async () => {
  let attempts = 0;
  const queue = new SerializedSaveQueue(async () => {
    attempts += 1;
    if (attempts === 1) throw new Error("disk unavailable");
  });
  queue.schedule(10_000);
  await assert.rejects(queue.flush(), /disk unavailable/);
  assert.equal(queue.pending, true);
  await queue.flush();
  assert.equal(attempts, 2);
  assert.equal(queue.pending, false);
});

test("serialized custom writes flush pending state before running", async () => {
  const order = [];
  const queue = new SerializedSaveQueue(async () => {
    order.push("save");
  });
  queue.schedule(10_000);
  await queue.run(async () => {
    order.push("repair");
  });
  assert.deepEqual(order, ["save", "repair"]);
});

test("reset waits for the old epoch and cannot flush a new workspace token", async () => {
  const calls = [];
  let releaseOld;
  let oldStarted;
  const started = new Promise((resolve) => {
    oldStarted = resolve;
  });
  const oldGate = new Promise((resolve) => {
    releaseOld = resolve;
  });
  const queue = new SerializedSaveQueue(async () => {
    calls.push(calls.length === 0 ? "old" : "new");
    if (calls.length === 1) {
      oldStarted();
      await oldGate;
    }
  });
  queue.schedule(10_000);
  const oldFlush = queue.flush();
  await started;
  const reset = queue.reset();
  queue.schedule(10_000);
  const newFlush = queue.flush();
  releaseOld();
  await Promise.all([oldFlush, reset, newFlush]);
  assert.deepEqual(calls, ["old", "new"]);
  assert.equal(queue.pending, false);
});

test("older save completion cannot clear a newer pending token", async () => {
  let releaseFirst;
  let firstStarted;
  const gate = new Promise((resolve) => {
    releaseFirst = resolve;
  });
  const started = new Promise((resolve) => {
    firstStarted = resolve;
  });
  const currentChecks = [];
  const queue = new SerializedSaveQueue(async (_options, context) => {
    if (!currentChecks.length) {
      firstStarted();
      await gate;
    }
    currentChecks.push(context.isCurrent());
  });
  queue.schedule(10_000);
  const flush = queue.flush();
  await started;
  queue.schedule(10_000);
  releaseFirst();
  await flush;
  assert.deepEqual(currentChecks, [false, true]);
  assert.equal(queue.pending, false);
});

test("explicit recovery bypasses a failed ordinary token and clears it only on success", async () => {
  let saves = 0;
  let recoveries = 0;
  const queue = new SerializedSaveQueue(async () => {
    saves += 1;
    throw new Error("known ordinary save conflict");
  });
  queue.schedule(10_000);
  await assert.rejects(queue.flush(), /known ordinary save conflict/);
  assert.equal(queue.pending, true);
  await queue.recover(async () => {
    recoveries += 1;
  });
  assert.equal(saves, 1);
  assert.equal(recoveries, 1);
  assert.equal(queue.pending, false);

  queue.schedule(10_000);
  await assert.rejects(
    queue.recover(async () => {
      throw new Error("recovery failed");
    }),
    /recovery failed/,
  );
  assert.equal(queue.pending, true);
});
