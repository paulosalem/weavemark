export class SQLiteClient {
  #worker;
  #pending = new Map();
  #requestId = 0;

  constructor(workerUrl = new URL("./sqlite-worker.js", import.meta.url)) {
    this.#worker = new Worker(workerUrl);
    this.#worker.addEventListener("message", ({ data }) => {
      const pending = this.#pending.get(data.id);
      if (!pending) return;
      this.#pending.delete(data.id);
      if (data.ok) pending.resolve(data.result);
      else {
        const error = new Error(data.error?.message || "SQLite worker failed.");
        error.code = data.error?.code || "WORKER_ERROR";
        pending.reject(error);
      }
    });
    this.#worker.addEventListener("error", (event) => {
      for (const pending of this.#pending.values()) {
        pending.reject(new Error(event.message || "SQLite worker crashed."));
      }
      this.#pending.clear();
    });
  }

  request(type, payload = {}, transfer = []) {
    const id = ++this.#requestId;
    return new Promise((resolve, reject) => {
      this.#pending.set(id, { resolve, reject });
      this.#worker.postMessage({ id, type, payload }, transfer);
    });
  }

  async open(bytes, { seed = false } = {}) {
    const buffer = bytes?.buffer
      ? bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
      : null;
    return this.request("open", { buffer, seed }, buffer ? [buffer] : []);
  }

  snapshot() {
    return this.request("snapshot");
  }

  card(cardId) {
    return this.request("card", { cardId });
  }

  createCard(input) {
    return this.request("createCard", input);
  }

  updateCard(input) {
    return this.request("updateCard", input);
  }

  moveCard(input) {
    return this.request("moveCard", input);
  }

  archiveCard(cardId) {
    return this.request("archiveCard", { cardId });
  }

  addPlanItem(input) {
    return this.request("addPlanItem", input);
  }

  updatePlanItem(input) {
    return this.request("updatePlanItem", input);
  }

  addOutput(input) {
    return this.request("addOutput", input);
  }

  applyResponse(input) {
    return this.request("applyResponse", input);
  }

  async exportBytes() {
    const result = await this.request("export");
    return new Uint8Array(result.buffer);
  }

  close() {
    return this.request("close");
  }

  terminate() {
    this.#worker.terminate();
  }
}
