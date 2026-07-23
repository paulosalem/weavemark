export function parseImportInWorker(text) {
  if (!("Worker" in globalThis)) return Promise.resolve(JSON.parse(text));
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL("../workers/importPreviewWorker.js", import.meta.url), { type: "module" });
    worker.onmessage = (event) => {
      worker.terminate();
      if (event.data.ok) resolve(event.data.payload);
      else reject(new Error(event.data.error));
    };
    worker.onerror = (event) => {
      worker.terminate();
      reject(new Error(event.message || "Import worker failed."));
    };
    worker.postMessage({ text });
  });
}
