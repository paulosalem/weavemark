export class SerializedSaveQueue {
  #save;
  #chain = Promise.resolve();
  #scheduled = null;
  #latestToken = 0;
  #flushedToken = 0;
  #epoch = 0;

  constructor(save) {
    if (typeof save !== "function") throw new TypeError("A save function is required.");
    this.#save = save;
  }

  get pending() {
    return this.#latestToken > this.#flushedToken;
  }

  schedule(delay = 500) {
    const epoch = this.#epoch;
    this.#latestToken += 1;
    clearTimeout(this.#scheduled);
    this.#scheduled = setTimeout(() => {
      if (epoch !== this.#epoch) return;
      this.flush().catch(() => {
        // Scheduled saves report through the owning workspace UI.
      });
    }, delay);
    return this.#latestToken;
  }

  flush({ runIfClean = false, saveOptions = {} } = {}) {
    clearTimeout(this.#scheduled);
    this.#scheduled = null;
    const epoch = this.#epoch;
    const requestedToken = this.#latestToken;
    if (requestedToken <= this.#flushedToken && !runIfClean) return this.#chain;
    const operation = this.#chain.then(async () => {
      let token = Math.max(requestedToken, this.#latestToken);
      if (token <= this.#flushedToken && !runIfClean) return;
      do {
        const savingToken = token;
        await this.#save(saveOptions, {
          token: savingToken,
          isCurrent: () =>
            epoch === this.#epoch &&
            savingToken === this.#latestToken,
        });
        if (epoch !== this.#epoch) return;
        this.#flushedToken = Math.max(this.#flushedToken, savingToken);
        token = this.#latestToken;
      } while (token > this.#flushedToken);
    });
    this.#chain = operation.catch(() => {});
    return operation;
  }

  run(operation) {
    if (typeof operation !== "function") {
      throw new TypeError("A serialized operation function is required.");
    }
    const execution = this.flush().then(operation);
    this.#chain = execution.catch(() => {});
    return execution;
  }

  recover(operation) {
    if (typeof operation !== "function") {
      throw new TypeError("A recovery operation function is required.");
    }
    clearTimeout(this.#scheduled);
    this.#scheduled = null;
    const epoch = this.#epoch;
    const recoveredToken = this.#latestToken;
    const execution = this.#chain.then(async () => {
      const result = await operation();
      if (epoch === this.#epoch) {
        this.#flushedToken = Math.max(this.#flushedToken, recoveredToken);
      }
      return result;
    });
    this.#chain = execution.catch(() => {});
    return execution;
  }

  async reset() {
    clearTimeout(this.#scheduled);
    this.#scheduled = null;
    this.#epoch += 1;
    this.#latestToken = 0;
    this.#flushedToken = 0;
    const inFlight = this.#chain.catch(() => {});
    this.#chain = inFlight;
    await inFlight;
  }
}
