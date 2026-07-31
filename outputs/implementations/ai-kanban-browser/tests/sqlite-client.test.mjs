import assert from "node:assert/strict";
import test from "node:test";

import { SQLiteClient } from "../src/sqlite-client.js";

class WorkerStub {
  static instance;

  listeners = new Map();

  constructor() {
    WorkerStub.instance = this;
  }

  addEventListener(type, listener) {
    this.listeners.set(type, listener);
  }

  postMessage() {}

  terminate() {}

  emit(type, event) {
    this.listeners.get(type)?.(event);
  }
}

test("worker failure rejects pending and subsequent requests", async () => {
  const originalWorker = globalThis.Worker;
  globalThis.Worker = WorkerStub;
  try {
    const client = new SQLiteClient("worker.js");
    const pending = client.health();
    WorkerStub.instance.emit("error", { message: "boom" });

    await assert.rejects(pending, { code: "WORKER_CRASHED", message: "boom" });
    await assert.rejects(client.snapshot(), {
      code: "WORKER_CRASHED",
      message: "boom",
    });
  } finally {
    globalThis.Worker = originalWorker;
  }
});

test("terminated client rejects later requests", async () => {
  const originalWorker = globalThis.Worker;
  globalThis.Worker = WorkerStub;
  try {
    const client = new SQLiteClient("worker.js");
    client.terminate();

    await assert.rejects(client.health(), {
      code: "WORKER_TERMINATED",
      message: "SQLite worker was terminated.",
    });
  } finally {
    globalThis.Worker = originalWorker;
  }
});
