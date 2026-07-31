import { SQLiteClient } from "./sqlite-client.js";

export class BoardRepository {
  #client;
  #snapshot = null;

  constructor(client = new SQLiteClient()) {
    this.#client = client;
  }

  get snapshotValue() {
    return this.#snapshot;
  }

  async create({ demo = false, workspaceId = null } = {}) {
    this.#snapshot = await this.#client.open(null, { seed: demo, workspaceId });
    return this.#snapshot;
  }

  async open(bytes) {
    this.#snapshot = await this.#client.open(bytes);
    return this.#snapshot;
  }

  async openVerified(bytes, validate) {
    if (typeof validate !== "function") {
      throw new TypeError("A candidate validation function is required.");
    }
    const previousSnapshot = this.#snapshot;
    const previousBytes = previousSnapshot ? await this.exportBytes() : null;
    try {
      const candidate = await this.#client.open(bytes);
      await validate(candidate);
      this.#snapshot = candidate;
      return candidate;
    } catch (error) {
      if (previousBytes) {
        this.#snapshot = await this.#client.open(previousBytes);
      } else {
        await this.#client.close().catch(() => {});
        this.#snapshot = null;
      }
      throw error;
    }
  }

  async health() {
    return this.#client.health();
  }

  async snapshot() {
    this.#snapshot = await this.#client.snapshot();
    return this.#snapshot;
  }

  card(cardId) {
    return this.#client.query("card", { cardId });
  }

  archivedCards() {
    return this.#client.query("archivedCards");
  }

  search(filters) {
    return this.#client.query("search", filters);
  }

  archiveReferences() {
    return this.#client.query("archiveReferences");
  }

  async mutate(operation, parameters = {}, contextOverrides = {}) {
    if (!this.#snapshot) throw new Error("Open a workspace before mutating it.");
    const meta = this.#snapshot.meta;
    const context = {
      actorId: "human",
      holderId: meta.control_holder || "human",
      generation: Number(meta.control_generation),
      expectedRevision: Number(meta.revision),
      ...contextOverrides,
    };
    const result = await this.#client.mutate(operation, parameters, context);
    this.#snapshot = result.snapshot;
    return result;
  }

  exportBytes() {
    return this.#client.exportBytes();
  }

  async close() {
    this.#snapshot = null;
    return this.#client.close();
  }

  terminate() {
    this.#client.terminate();
  }
}
