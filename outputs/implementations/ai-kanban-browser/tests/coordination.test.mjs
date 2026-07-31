import test from "node:test";
import assert from "node:assert/strict";
import {
  CoordinationService,
  isAgentGrantCandidate,
} from "../src/coordination.js";

const record = (sequence, generation = 2) => ({
  workspace_id: "workspace-1",
  protocol_version: 1,
  actor_id: "agent-1",
  holder_id: "agent-1",
  sequence,
  control_generation: generation,
  observed_revision: 5,
  requested_state: "agent",
  timestamp: new Date().toISOString(),
});

test("poll retains accepted records while ignoring unchanged and stale updates", async () => {
  let records = [{ path: ".ai-kanban/coordination/agent-agent-1.json", value: record(4) }];
  const workspace = {
    mode: "connected",
    async readCoordinationRecords() {
      return records;
    },
  };
  const service = new CoordinationService(workspace, "workspace-1");
  const snapshots = [];
  service.addEventListener("status", (event) => snapshots.push(event.detail.agents));

  await service.poll();
  service.stop();
  await service.poll();
  service.stop();
  records = [{ path: ".ai-kanban/coordination/agent-agent-1.json", value: record(3) }];
  await service.poll();
  service.stop();
  records = [{ path: ".ai-kanban/coordination/agent-agent-1.json", value: record(1, 3) }];
  await service.poll();
  service.stop();

  assert.deepEqual(snapshots.map((agents) => agents.length), [1, 1, 1, 1]);
  assert.equal(snapshots[1][0].sequence, 4);
  assert.equal(snapshots[2][0].sequence, 4);
  assert.equal(snapshots[3][0].control_generation, 3);
  assert.equal(snapshots[3][0].sequence, 1);
});

test("human publication continues the durable sequence across service reloads", async () => {
  let human = {
    ...record(41, 7),
    actor_id: "human",
    holder_id: "human",
    requested_state: "human",
  };
  const workspace = {
    mode: "connected",
    async readCoordinationRecords() {
      return [{ path: ".ai-kanban/coordination/human.json", value: human }];
    },
    async writeCoordination(_path, value) {
      human = value;
    },
  };
  const first = new CoordinationService(workspace, "workspace-1");
  const firstRecord = await first.publishHuman({
    holderId: "human",
    generation: 7,
    revision: 9,
    requestedState: "human",
  });
  const reloaded = new CoordinationService(workspace, "workspace-1");
  const secondRecord = await reloaded.publishHuman({
    holderId: "agent-1",
    generation: 8,
    revision: 10,
    requestedState: "agent",
  });
  assert.equal(firstRecord.sequence, 42);
  assert.equal(secondRecord.sequence, 43);
  assert.equal(human.sequence, 43);
});

test("grant candidates must be live current-generation explicit requests", () => {
  const metadata = { control_generation: "3", revision: "12" };
  const candidate = {
    ...record(5, 3),
    observed_revision: 12,
    requested_state: "granting_agent",
    status: "requesting_control",
    stale: false,
  };
  assert.equal(isAgentGrantCandidate(candidate, metadata), true);
  assert.equal(isAgentGrantCandidate({ ...candidate, status: "stopped" }, metadata), false);
  assert.equal(isAgentGrantCandidate({ ...candidate, requested_state: "human" }, metadata), false);
  assert.equal(isAgentGrantCandidate({ ...candidate, stale: true }, metadata), false);
  assert.equal(isAgentGrantCandidate({ ...candidate, control_generation: 2 }, metadata), false);
  assert.equal(isAgentGrantCandidate({ ...candidate, observed_revision: 11 }, metadata), false);
});

test("stop invalidates an in-flight poll without dispatch or reschedule", async () => {
  let resolveRead;
  let reads = 0;
  const workspace = {
    mode: "connected",
    async readCoordinationRecords() {
      reads += 1;
      return new Promise((resolve) => {
        resolveRead = resolve;
      });
    },
  };
  const service = new CoordinationService(workspace, "workspace-1");
  let events = 0;
  service.addEventListener("status", () => {
    events += 1;
  });
  service.start();
  service.stop();
  resolveRead([{ path: ".ai-kanban/coordination/agent-agent-1.json", value: record(1) }]);
  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(events, 0);
  assert.equal(reads, 1);
});
