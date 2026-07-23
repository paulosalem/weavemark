export function parseRoute(hash = window.location.hash) {
  const parts = hash.replace(/^#\/?/, "").split("/").filter(Boolean).map(decodeURIComponent);
  if (parts[0] === "pack" && parts[1]) return { view: "pack", packId: parts[1], cardId: parts[2] ?? null };
  if (parts[0] === "panel" && parts[1]) return { view: "panel", panel: parts[1] };
  return { view: "library" };
}

export function packUrl(packId, cardId = null) {
  return `#/pack/${encodeURIComponent(packId)}${cardId ? `/${encodeURIComponent(cardId)}` : ""}`;
}

export function panelUrl(panel) {
  return `#/panel/${encodeURIComponent(panel)}`;
}
