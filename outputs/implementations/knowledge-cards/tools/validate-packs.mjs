#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { validateCardsDocument, validateManifest } from "../src/domain/curriculumValidator.js";

const ROOT = process.cwd();
const PACKS_DIR = path.join(ROOT, "content", "packs");
const INDEX_PATH = path.join(PACKS_DIR, "index.json");
const ALLOWED_MANIFEST_KEYS = new Set([
  "schema_version",
  "id",
  "title",
  "description",
  "language",
  "audience",
  "level",
  "purpose",
  "content_version",
  "card_count",
  "ordered_content_files",
  "optional_media_root",
  "authors",
  "provenance",
  "source_policy",
  "license",
  "accent_color",
  "content_checksum",
  "created_at",
  "updated_at",
  "curriculum_map_path",
  "validation_report_path"
]);

const ALLOWED_CARD_DOC_KEYS = new Set(["schema_version", "pack_id", "source_refs", "cards"]);
const ALLOWED_CARD_KEYS = new Set([
  "id",
  "title",
  "core_idea",
  "example",
  "key_takeaway",
  "connections",
  "difficulty",
  "importance",
  "foundational_priority",
  "category",
  "prerequisites",
  "source_refs",
  "media",
  "review_prompts",
  "boundary_note"
]);

export async function validateAllPacks({ writeIndex = false, rootDir = ROOT } = {}) {
  const packsDir = path.join(rootDir, "content", "packs");
  const entries = await fs.readdir(packsDir, { withFileTypes: true });
  const packDirs = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort();
  const errors = [];
  const indexEntries = [];

  for (const dir of packDirs) {
    const packDir = path.join(packsDir, dir);
    const manifestPath = path.join(packDir, "manifest.json");
    const manifest = await loadJson(manifestPath, errors);
    if (!manifest) continue;
    collectUnknownKeys(manifest, ALLOWED_MANIFEST_KEYS, `${dir}/manifest.json`, errors);
    errors.push(...validateManifest(manifest).map((error) => `${dir}: ${error}`));
    if (manifest.id !== dir) errors.push(`${dir}: directory name must match manifest id.`);

    const allowedJson = new Set(["manifest.json", manifest.curriculum_map_path, manifest.validation_report_path, ...manifest.ordered_content_files]);
    for (const file of await listJsonFiles(packDir)) {
      const relative = toPosix(path.relative(packDir, file));
      if (!allowedJson.has(relative)) errors.push(`${dir}: orphan or undeclared JSON file ${relative}.`);
    }

    const checksum = await computeContentChecksum(packDir, manifest.ordered_content_files);
    if (manifest.content_checksum !== checksum) {
      errors.push(`${dir}: checksum drift. manifest has ${manifest.content_checksum}, computed ${checksum}.`);
    }

    let cardCount = 0;
    const seenCardIds = new Set();
    const seenSourceIds = new Set();
    for (const file of manifest.ordered_content_files) {
      const resolved = resolveInside(packDir, file);
      if (!resolved) {
        errors.push(`${dir}: unsafe content path ${file}.`);
        continue;
      }
      const document = await loadJson(resolved, errors);
      if (!document) continue;
      collectUnknownKeys(document, ALLOWED_CARD_DOC_KEYS, `${dir}/${file}`, errors);
      for (const source of document.source_refs ?? []) {
        seenSourceIds.add(source.id);
        validateSource(source, `${dir}/${file}`, errors);
      }
      for (const card of document.cards ?? []) {
        collectUnknownKeys(card, ALLOWED_CARD_KEYS, `${dir}/${file}:${card.id}`, errors);
        if (seenCardIds.has(card.id)) errors.push(`${dir}: duplicate card id across files ${card.id}.`);
        seenCardIds.add(card.id);
        validateNoExecutableText(card, `${dir}/${card.id}`, errors);
        validateMedia(packDir, card, `${dir}/${card.id}`, errors);
      }
      errors.push(...validateCardsDocument(document, manifest).map((error) => `${dir}: ${error}`));
      cardCount += document.cards?.length ?? 0;
    }
    if (cardCount !== 50) errors.push(`${dir}: expected 50 cards, found ${cardCount}.`);
    if (seenSourceIds.size < 2) errors.push(`${dir}: expected multiple source references for reviewability.`);
    await validateSidecars(packDir, manifest, errors);

    indexEntries.push({
      id: manifest.id,
      title: manifest.title,
      description: manifest.description,
      language: manifest.language,
      audience: manifest.audience,
      level: manifest.level,
      purpose: manifest.purpose,
      card_count: manifest.card_count,
      content_version: manifest.content_version,
      checksum,
      accent_color: manifest.accent_color,
      manifest_path: `content/packs/${manifest.id}/manifest.json`
    });
  }

  if (packDirs.length === 0) errors.push("No pack directories found.");
  indexEntries.sort((a, b) => a.id.localeCompare(b.id));
  const index = {
    schema_version: "knowledge-cards.pack-index.v1",
    generated_by: "tools/validate-packs.mjs",
    packs: indexEntries
  };

  if (writeIndex && errors.length === 0) await fs.writeFile(path.join(packsDir, "index.json"), stableJson(index), "utf8");
  return { ok: errors.length === 0, errors, index };
}

export async function computeContentChecksum(packDir, orderedFiles) {
  const hash = crypto.createHash("sha256");
  for (const file of orderedFiles) {
    const resolved = resolveInside(packDir, file);
    if (!resolved) continue;
    hash.update(file);
    hash.update("\n");
    hash.update(await fs.readFile(resolved));
    hash.update("\n");
  }
  return `sha256-${hash.digest("hex")}`;
}

function validateSource(source, context, errors) {
  const allowed = new Set(["id", "title", "publisher", "url", "accessed_at", "claim_scope"]);
  collectUnknownKeys(source, allowed, `${context}:source:${source.id}`, errors);
  try {
    const url = new URL(source.url);
    if (!["https:"].includes(url.protocol)) errors.push(`${context}: source ${source.id} must use https.`);
  } catch {
    errors.push(`${context}: source ${source.id} has malformed URL.`);
  }
}

function validateNoExecutableText(card, context, errors) {
  const strings = [
    card.title,
    card.example,
    card.key_takeaway,
    card.boundary_note,
    ...(card.core_idea ?? []),
    ...(card.connections ?? []).map((connection) => connection.label),
    ...(card.review_prompts ?? []).flatMap((prompt) => [prompt.prompt, prompt.answer_hint])
  ];
  for (const value of strings) {
    if (/<\s*script|javascript:/i.test(String(value ?? ""))) errors.push(`${context}: executable text is not allowed.`);
  }
}

function validateMedia(packDir, card, context, errors) {
  if (card.media == null) return;
  if (typeof card.media !== "object" || typeof card.media.path !== "string") {
    errors.push(`${context}: media must be null or an object with path.`);
    return;
  }
  const resolved = resolveInside(packDir, card.media.path);
  if (!resolved) {
    errors.push(`${context}: media path escapes pack root.`);
    return;
  }
  fs.access(resolved).catch(() => errors.push(`${context}: media file missing ${card.media.path}.`));
}

async function validateSidecars(packDir, manifest, errors) {
  const curriculum = await loadJson(path.join(packDir, manifest.curriculum_map_path), errors);
  const report = await loadJson(path.join(packDir, manifest.validation_report_path), errors);
  for (const [label, document] of [["curriculum map", curriculum], ["validation report", report]]) {
    if (!document) continue;
    if (document.pack_id !== manifest.id) errors.push(`${manifest.id}: ${label} pack_id mismatch.`);
    if (!Array.isArray(document.categories) || document.categories.length < 7) {
      errors.push(`${manifest.id}: ${label} must cover all curriculum categories.`);
    }
  }
}

function collectUnknownKeys(object, allowed, context, errors) {
  for (const key of Object.keys(object ?? {})) {
    if (!allowed.has(key)) errors.push(`${context}: unknown field ${key}.`);
  }
}

async function listJsonFiles(dir) {
  const found = [];
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) found.push(...await listJsonFiles(full));
    else if (entry.name.endsWith(".json")) found.push(full);
  }
  return found;
}

async function loadJson(file, errors) {
  try {
    return JSON.parse(await fs.readFile(file, "utf8"));
  } catch (error) {
    errors.push(`${toPosix(path.relative(ROOT, file))}: ${error.message}`);
    return null;
  }
}

function resolveInside(base, relative) {
  if (path.isAbsolute(relative) || relative.includes("\\")) return null;
  const resolved = path.resolve(base, relative);
  return resolved.startsWith(path.resolve(base) + path.sep) || resolved === path.resolve(base) ? resolved : null;
}

function stableJson(value) {
  return `${JSON.stringify(sortKeys(value), null, 2)}\n`;
}

function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, sortKeys(item)]));
  }
  return value;
}

function toPosix(value) {
  return value.split(path.sep).join("/");
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const writeIndex = process.argv.includes("--write-index");
  const result = await validateAllPacks({ writeIndex });
  if (!result.ok) {
    console.error(result.errors.join("\n"));
    process.exitCode = 1;
  } else {
    console.log(`Validated ${result.index.packs.length} packs (${result.index.packs.reduce((sum, pack) => sum + pack.card_count, 0)} cards).`);
    if (writeIndex) console.log(`Wrote ${path.relative(ROOT, INDEX_PATH)}.`);
  }
}
