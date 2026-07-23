const SCHEMA_VERSIONS = Object.freeze({
  index: "knowledge-cards.pack-index.v1",
  manifest: "knowledge-cards.pack-manifest.v1",
  cards: "knowledge-cards.cards.v1"
});

const CARD_CATEGORIES = new Set([
  "foundations",
  "mechanisms",
  "applications",
  "misconceptions",
  "limitations",
  "bridges",
  "advanced-horizons"
]);

export function validatePackIndex(index) {
  const errors = [];
  if (!index || typeof index !== "object") errors.push("Pack index must be an object.");
  if (index?.schema_version !== SCHEMA_VERSIONS.index) errors.push("Unsupported pack-index schema version.");
  if (!Array.isArray(index?.packs)) errors.push("Pack index must include packs array.");
  const ids = new Set();
  for (const entry of index?.packs ?? []) {
    if (!isSafeId(entry.id)) errors.push(`Invalid pack id: ${entry.id}`);
    if (ids.has(entry.id)) errors.push(`Duplicate pack id in index: ${entry.id}`);
    ids.add(entry.id);
    for (const key of ["title", "description", "language", "audience", "level", "purpose", "content_version", "checksum", "accent_color", "manifest_path"]) {
      if (typeof entry[key] !== "string" || !entry[key].trim()) errors.push(`Pack ${entry.id} missing ${key}.`);
    }
    if (entry.card_count !== 50) errors.push(`Pack ${entry.id} must advertise exactly 50 cards.`);
  }
  return errors;
}

export function validateManifest(manifest) {
  const errors = [];
  if (!manifest || typeof manifest !== "object") return ["Pack manifest must be an object."];
  if (manifest.schema_version !== SCHEMA_VERSIONS.manifest) errors.push("Unsupported pack-manifest schema version.");
  for (const key of [
    "id",
    "title",
    "description",
    "language",
    "audience",
    "level",
    "purpose",
    "content_version",
    "optional_media_root",
    "provenance",
    "source_policy",
    "license",
    "accent_color",
    "content_checksum",
    "created_at",
    "updated_at",
    "curriculum_map_path",
    "validation_report_path"
  ]) {
    if (typeof manifest[key] !== "string" || !manifest[key].trim()) errors.push(`Manifest missing ${key}.`);
  }
  if (!isSafeId(manifest.id)) errors.push(`Invalid manifest id: ${manifest.id}`);
  if (manifest.card_count !== 50) errors.push("Manifest card_count must be exactly 50.");
  if (!Array.isArray(manifest.ordered_content_files) || manifest.ordered_content_files.length === 0) {
    errors.push("Manifest ordered_content_files must list at least one file.");
  }
  if (!Array.isArray(manifest.authors) || manifest.authors.length === 0) errors.push("Manifest authors must be non-empty.");
  for (const file of manifest.ordered_content_files ?? []) {
    if (!isSafeRelativePath(file)) errors.push(`Unsafe content path: ${file}`);
  }
  for (const file of [manifest.curriculum_map_path, manifest.validation_report_path]) {
    if (!isSafeRelativePath(file)) errors.push(`Unsafe manifest sidecar path: ${file}`);
  }
  if (!isIsoUtc(manifest.created_at) || !isIsoUtc(manifest.updated_at)) {
    errors.push("Manifest timestamps must be UTC ISO 8601 strings.");
  }
  return errors;
}

export function validateCardsDocument(document, manifest) {
  const errors = [];
  if (!document || typeof document !== "object") return ["Cards document must be an object."];
  if (document.schema_version !== SCHEMA_VERSIONS.cards) errors.push("Unsupported cards schema version.");
  if (document.pack_id !== manifest.id) errors.push("Cards document pack_id must match manifest id.");
  if (!Array.isArray(document.source_refs) || document.source_refs.length === 0) errors.push("Cards document must include source_refs.");
  if (!Array.isArray(document.cards)) errors.push("Cards document must include cards array.");
  if ((document.cards ?? []).length !== manifest.card_count) errors.push(`Cards document must contain ${manifest.card_count} cards.`);

  const sourceIds = new Set((document.source_refs ?? []).map((source) => source.id));
  const ids = new Set();
  const titles = new Set();
  const categoryCounts = new Map();

  for (const source of document.source_refs ?? []) {
    for (const key of ["id", "title", "publisher", "url", "accessed_at", "claim_scope"]) {
      if (typeof source[key] !== "string" || !source[key].trim()) errors.push(`Source reference missing ${key}.`);
    }
    if (!isSafeId(source.id)) errors.push(`Invalid source id: ${source.id}`);
  }

  for (const card of document.cards ?? []) {
    validateCard(card, sourceIds, errors);
    if (ids.has(card.id)) errors.push(`Duplicate card id: ${card.id}`);
    ids.add(card.id);
    const titleKey = normalizeConcept(card.title);
    if (titles.has(titleKey)) errors.push(`Duplicate concept title: ${card.title}`);
    titles.add(titleKey);
    categoryCounts.set(card.category, (categoryCounts.get(card.category) ?? 0) + 1);
  }

  for (const card of document.cards ?? []) {
    for (const prerequisite of card.prerequisites ?? []) {
      if (!ids.has(prerequisite)) errors.push(`Card ${card.id} has unsatisfied prerequisite ${prerequisite}.`);
    }
  }

  errors.push(...findPrerequisiteCycles(document.cards ?? []));
  for (const category of CARD_CATEGORIES) {
    if (!categoryCounts.has(category)) errors.push(`Pack lacks required curriculum category: ${category}.`);
  }
  return errors;
}

function validateCard(card, sourceIds, errors) {
  if (!card || typeof card !== "object") {
    errors.push("Card must be an object.");
    return;
  }
  for (const key of ["id", "title", "example", "key_takeaway", "category", "boundary_note"]) {
    if (typeof card[key] !== "string" || !card[key].trim()) errors.push(`Card ${card.id ?? "(unknown)"} missing ${key}.`);
  }
  if (!isSafeId(card.id)) errors.push(`Invalid card id: ${card.id}`);
  if (!Array.isArray(card.core_idea) || card.core_idea.length < 2 || card.core_idea.length > 5) {
    errors.push(`Card ${card.id} core_idea must contain two to five paragraphs.`);
  }
  for (const paragraph of card.core_idea ?? []) {
    if (typeof paragraph !== "string" || paragraph.length < 80) errors.push(`Card ${card.id} has an underdeveloped core paragraph.`);
    if (containsUnsafeMarkup(paragraph)) errors.push(`Card ${card.id} contains unsafe markup.`);
  }
  if (!CARD_CATEGORIES.has(card.category)) errors.push(`Card ${card.id} has unsupported category ${card.category}.`);
  if (!Number.isFinite(card.difficulty) || card.difficulty < 1 || card.difficulty > 5) errors.push(`Card ${card.id} difficulty must be 1-5.`);
  for (const key of ["importance", "foundational_priority"]) {
    if (!Number.isFinite(card[key]) || card[key] < 0 || card[key] > 1) errors.push(`Card ${card.id} ${key} must be 0-1.`);
  }
  if (!Array.isArray(card.prerequisites)) errors.push(`Card ${card.id} prerequisites must be an array.`);
  if (!Array.isArray(card.connections)) errors.push(`Card ${card.id} connections must be an array.`);
  if (!Array.isArray(card.source_refs) || card.source_refs.length === 0) errors.push(`Card ${card.id} must include source refs.`);
  for (const ref of card.source_refs ?? []) {
    if (!sourceIds.has(ref)) errors.push(`Card ${card.id} references unknown source ${ref}.`);
  }
  if (!Array.isArray(card.review_prompts) || card.review_prompts.length === 0) errors.push(`Card ${card.id} needs review prompts.`);
  for (const prompt of card.review_prompts ?? []) {
    if (!["recall", "comparison", "application", "connection"].includes(prompt.kind)) {
      errors.push(`Card ${card.id} has unsupported review prompt kind.`);
    }
    if (typeof prompt.prompt !== "string" || typeof prompt.answer_hint !== "string") {
      errors.push(`Card ${card.id} review prompt is incomplete.`);
    }
  }
}

function findPrerequisiteCycles(cards) {
  const byId = new Map(cards.map((card) => [card.id, card]));
  const visiting = new Set();
  const visited = new Set();
  const errors = [];

  function visit(id, path) {
    if (visiting.has(id)) {
      errors.push(`Prerequisite cycle detected: ${[...path, id].join(" -> ")}`);
      return;
    }
    if (visited.has(id)) return;
    visiting.add(id);
    for (const next of byId.get(id)?.prerequisites ?? []) visit(next, [...path, id]);
    visiting.delete(id);
    visited.add(id);
  }

  for (const card of cards) visit(card.id, []);
  return errors;
}

export function assertValidPack(indexOrManifestErrors, context) {
  if (indexOrManifestErrors.length > 0) {
    throw new Error(`${context} failed validation:\n${indexOrManifestErrors.join("\n")}`);
  }
}

export function isSafeId(value) {
  return typeof value === "string" && /^[a-z0-9][a-z0-9-]{1,80}$/.test(value);
}

export function isSafeRelativePath(value) {
  return typeof value === "string" && value.length > 0 && !value.startsWith("/") && !value.includes("\\") && !value.split("/").includes("..");
}

function isIsoUtc(value) {
  return typeof value === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(value);
}

function normalizeConcept(value) {
  return String(value ?? "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function containsUnsafeMarkup(value) {
  return /<\s*\/?\s*[a-z][^>]*>/i.test(value);
}
