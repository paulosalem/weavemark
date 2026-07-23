import { PACK_INDEX_URL } from "../config.js";
import { assertValidPack, validateCardsDocument, validateManifest, validatePackIndex } from "./curriculumValidator.js";

export async function loadPackIndex(indexUrl = PACK_INDEX_URL) {
  const index = await fetchJson(indexUrl);
  assertValidPack(validatePackIndex(index), "Pack index");
  return index;
}

export async function loadPack(entry) {
  const manifest = await fetchJson(entry.manifest_path);
  assertValidPack(validateManifest(manifest), `Manifest ${entry.id}`);
  const baseUrl = entry.manifest_path.split("/").slice(0, -1).join("/");
  const contentDocuments = [];
  for (const file of manifest.ordered_content_files) {
    contentDocuments.push(await fetchJson(`${baseUrl}/${file}`));
  }
  const cards = [];
  const sourceRefs = [];
  for (const document of contentDocuments) {
    assertValidPack(validateCardsDocument(document, manifest), `Cards ${manifest.id}`);
    cards.push(...document.cards);
    sourceRefs.push(...document.source_refs);
  }
  return {
    entry,
    manifest,
    cards,
    sourceRefs,
    byId: new Map(cards.map((card) => [card.id, card]))
  };
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-cache" });
  if (!response.ok) throw new Error(`Could not load ${url}: ${response.status} ${response.statusText}`);
  return response.json();
}
