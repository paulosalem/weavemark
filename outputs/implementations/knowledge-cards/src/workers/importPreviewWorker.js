self.onmessage = (event) => {
  try {
    const payload = JSON.parse(event.data.text);
    if (!payload || typeof payload !== "object") throw new Error("Import must be a JSON object.");
    const stores = payload.stores && typeof payload.stores === "object" ? payload.stores : {};
    const counts = Object.fromEntries(Object.entries(stores).map(([key, value]) => [key, Array.isArray(value) ? value.length : 0]));
    self.postMessage({ ok: true, payload, counts });
  } catch (error) {
    self.postMessage({ ok: false, error: error.message });
  }
};
