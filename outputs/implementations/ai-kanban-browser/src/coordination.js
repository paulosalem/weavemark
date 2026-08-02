import { CONTROL_STATES, PROTOCOL_VERSION } from "./constants.js";
import { validateCoordinationRecord } from "./validation.js";

const HEARTBEAT_STALE_MS = 75_000;

export class CoordinationService extends EventTarget {
  #workspace;
  #workspaceId;
  #sequence = 0;
  #timer = null;
  #active = false;
  #pollEpoch = 0;
  #lastByActor = new Map();

  constructor(workspace, workspaceId) {
    super();
    this.#workspace = workspace;
    this.#workspaceId = workspaceId;
  }

  get available() {
    return this.#workspace?.mode === "connected";
  }

  start() {
    if (!this.available || this.#active) return;
    this.#active = true;
    const epoch = ++this.#pollEpoch;
    this.poll(epoch);
  }

  stop() {
    this.#active = false;
    this.#pollEpoch += 1;
    clearTimeout(this.#timer);
    this.#timer = null;
  }

  async poll(epoch = null) {
    if (!this.available) return;
    if (epoch == null) {
      this.#active = true;
      epoch = ++this.#pollEpoch;
    }
    try {
      const raw = await this.#workspace.readCoordinationRecords();
      if (!this.#active || epoch !== this.#pollEpoch) return;
      for (const item of raw) {
        if (item.path.endsWith("/human.json")) {
          const human = validateCoordinationRecord(item.value, this.#workspaceId);
          if (human.ok && human.value.actor_id === "human") {
            this.#sequence = Math.max(this.#sequence, human.value.sequence);
          }
          continue;
        }
        const validation = validateCoordinationRecord(item.value, this.#workspaceId);
        if (!validation.ok) continue;
        const record = validation.value;
        const previous = this.#lastByActor.get(record.actor_id);
        if (
          previous &&
          (record.control_generation < previous.control_generation ||
            (record.control_generation === previous.control_generation &&
              record.sequence <= previous.sequence))
        ) {
          continue;
        }
        this.#lastByActor.set(record.actor_id, record);
      }
      const agents = [...this.#lastByActor.values()].map((record) => ({
        ...record,
        stale: Date.now() - Date.parse(record.timestamp) > HEARTBEAT_STALE_MS,
      }));
      this.dispatchEvent(new CustomEvent("status", { detail: { agents } }));
    } catch (error) {
      if (!this.#active || epoch !== this.#pollEpoch) return;
      this.dispatchEvent(new CustomEvent("error", { detail: error }));
    } finally {
      if (!this.#active || epoch !== this.#pollEpoch) return;
      const hidden = typeof document !== "undefined" && document.hidden;
      this.#timer = setTimeout(
        () => this.poll(epoch),
        hidden ? 15_000 : 3_500,
      );
    }
  }

  async publishHuman({
    holderId,
    generation,
    revision,
    requestedState,
    note = null,
  }) {
    if (!CONTROL_STATES.includes(requestedState)) throw new TypeError("Invalid control state.");
    const raw = await this.#workspace.readCoordinationRecords();
    const durable = raw.find((item) => item.path.endsWith("/human.json"));
    if (durable) {
      const validation = validateCoordinationRecord(durable.value, this.#workspaceId);
      if (validation.ok && validation.value.actor_id === "human") {
        this.#sequence = Math.max(this.#sequence, validation.value.sequence);
      }
    }
    this.#sequence += 1;
    const record = {
      workspace_id: this.#workspaceId,
      protocol_version: PROTOCOL_VERSION,
      actor_id: "human",
      holder_id: holderId,
      sequence: this.#sequence,
      control_generation: generation,
      observed_revision: revision,
      requested_state: requestedState,
      timestamp: new Date().toISOString(),
      note,
    };
    await this.#workspace.writeCoordination(
      ".ai-kanban/coordination/human.json",
      record,
    );
    return record;
  }

  latestAgent(actorId = null) {
    if (actorId) return this.#lastByActor.get(actorId) || null;
    return [...this.#lastByActor.values()]
      .sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp))[0] || null;
  }
}

export function agentStateLabel(agent) {
  if (!agent) return "Waiting for agent";
  if (agent.requested_state === "human" && agent.status === "stopped") {
    return "Agent yielded control";
  }
  if (agent.stale) return "Agent heartbeat is stale";
  if (agent.requested_state === "granting_agent") {
    return "Agent is requesting control";
  }
  if (agent.current_turn_id) return `Working on turn ${agent.current_turn_id}`;
  return agent.requested_state === "agent" ? "Agent connected and watching" : "Agent connected";
}

export function isAgentGrantCandidate(agent, metadata) {
  return Boolean(
    agent &&
    !agent.stale &&
    !["stopped", "crashed"].includes(agent.status) &&
    agent.requested_state === "granting_agent" &&
    Number(agent.control_generation) === Number(metadata?.control_generation) &&
    Number(agent.observed_revision) === Number(metadata?.revision),
  );
}

export function selectRelevantAgent(agents, metadata) {
  const ordered = [...agents].sort(
    (left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp),
  );
  const holder = metadata?.control_holder;
  if (holder && holder !== "human") {
    return ordered.find((agent) => agent.actor_id === holder) || null;
  }
  return ordered.find((agent) => isAgentGrantCandidate(agent, metadata))
    || ordered[0]
    || null;
}
