export class AIProviderAdapter {
  #credential = null;

  setCredential(value) {
    this.#credential = String(value || "");
  }

  clearCredential() {
    this.#credential = null;
  }

  preview({ provider, endpoint, model, content, purpose }) {
    const url = validateEndpoint(endpoint);
    return {
      provider: String(provider || "Custom provider"),
      endpoint: url.href,
      model: String(model || ""),
      content: String(content || ""),
      purpose: String(purpose || ""),
    };
  }

  async send(preview) {
    if (!this.#credential) throw new Error("Enter a session-only credential before sending.");
    const response = await fetch(validateEndpoint(preview.endpoint), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.#credential}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: preview.model,
        purpose: preview.purpose,
        content: preview.content,
      }),
    });
    if (!response.ok) throw new Error(`Provider returned HTTP ${response.status}.`);
    return response.json();
  }
}

function validateEndpoint(value) {
  const url = new URL(value);
  if (url.protocol !== "https:" && !(
    url.protocol === "http:" && ["127.0.0.1", "[::1]"].includes(url.hostname)
  )) {
    throw new Error("Provider endpoint must use HTTPS (loopback HTTP is allowed).");
  }
  return url;
}
