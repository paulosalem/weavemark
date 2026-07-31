export class SQLiteClient {
  #worker;
  #pending = new Map();
  #requestId = 0;
  #failure = null;

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
      const error = new Error(event.message || "SQLite worker crashed.");
      error.code = "WORKER_CRASHED";
      this.#fail(error);
    });
  }

  #fail(error) {
    if (this.#failure) return;
    this.#failure = error;
    for (const pending of this.#pending.values()) pending.reject(error);
    this.#pending.clear();
  }

  request(type, payload = {}, transfer = []) {
    if (this.#failure) return Promise.reject(this.#failure);
    const id = ++this.#requestId;
    return new Promise((resolve, reject) => {
      this.#pending.set(id, { resolve, reject });
      try {
        this.#worker.postMessage({ id, type, payload }, transfer);
      } catch (error) {
        this.#pending.delete(id);
        reject(error);
      }
    });
  }

  async open(bytes, { seed = false, workspaceId = null } = {}) {
    const buffer = bytes?.buffer
      ? bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
      : null;
    return this.request(
      bytes ? "open" : "create",
      { buffer, seed, workspaceId },
      buffer ? [buffer] : [],
    );
  }

  health() {
    return this.request("health");
  }

  snapshot() {
    return this.request("snapshot");
  }

  query(name, parameters = {}) {
    return this.request("query", { name, parameters });
  }

  mutate(operation, parameters = {}, context = {}) {
    return this.request("mutate", { operation, parameters, context });
  }

  async exportBytes() {
    const result = await this.request("export");
    return new Uint8Array(result.buffer);
  }

  close() {
    return this.request("close");
  }

  terminate() {
    const error = new Error("SQLite worker was terminated.");
    error.code = "WORKER_TERMINATED";
    this.#fail(error);
    this.#worker.terminate();
  }
}
