import {
  ARCHIVE_FORMAT,
  BOOTSTRAP_FILES,
  CONTROL_STATES,
  MAX_ARCHIVE_FILE_BYTES,
  MAX_ARCHIVE_FILES,
  MAX_ARCHIVE_TOTAL_BYTES,
  PROTOCOL_VERSION,
  WORKSPACE_FORMAT,
  WORKSPACE_FORMAT_VERSION,
} from "./constants.js";

const ID_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$/;
const ACTOR_ID_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/;
const RUN_ID_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/;
const SEGMENT_PATTERN = /^(?!\.{1,2}$)[^/\\\0]+$/;
const ISO_TIMESTAMP_PATTERN =
  /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?(Z|([+-])(\d{2}):(\d{2}))$/;
const MAX_COORDINATION_FUTURE_SKEW_MS = 30_000;

export class ValidationError extends Error {
  constructor(message, code = "VALIDATION_ERROR", details = []) {
    super(message);
    this.name = "ValidationError";
    this.code = code;
    this.details = details;
  }
}

export function assertId(value, label = "id") {
  if (typeof value !== "string" || !ID_PATTERN.test(value)) {
    throw new ValidationError(`${label} is invalid.`);
  }
  return value;
}

export function assertActorId(value, label = "actor id") {
  if (typeof value !== "string" || !ACTOR_ID_PATTERN.test(value)) {
    throw new ValidationError(`${label} is invalid or not portable.`);
  }
  return value;
}

export function assertRelativePath(value, label = "path") {
  if (typeof value !== "string" || !value || value.startsWith("/") || value.startsWith("\\")) {
    throw new ValidationError(`${label} must be a relative path.`);
  }
  const parts = value.split("/");
  if (
    parts.some((part) => !SEGMENT_PATTERN.test(part)) ||
    /^[a-zA-Z]:/.test(value) ||
    value.includes("\\")
  ) {
    throw new ValidationError(`${label} escapes the workspace.`);
  }
  return parts;
}

export function validateManifest(value) {
  const errors = [];
  if (!isRecord(value)) return invalid("Manifest must be a JSON object.");
  if (value.format !== WORKSPACE_FORMAT) errors.push(`format must be ${WORKSPACE_FORMAT}.`);
  if (value.format_version !== WORKSPACE_FORMAT_VERSION) {
    errors.push(`format_version must be ${WORKSPACE_FORMAT_VERSION}.`);
  }
  if (value.protocol_version !== PROTOCOL_VERSION) {
    errors.push(`protocol_version must be ${PROTOCOL_VERSION}.`);
  }
  for (const field of ["format_version", "protocol_version", "schema_version", "revision"]) {
    if (!Number.isSafeInteger(value[field]) || value[field] < (field === "revision" ? 0 : 1)) {
      errors.push(`${field} must be a valid integer.`);
    }
  }
  try {
    assertId(value.workspace_id, "workspace_id");
    assertRelativePath(value.primary_state, "primary_state");
  } catch (error) {
    errors.push(error.message);
  }
  if (!Array.isArray(value.reserved_directories)) {
    errors.push("reserved_directories must be an array.");
  } else {
    validatePathArray(value.reserved_directories, "reserved_directories", errors);
  }
  if (!Array.isArray(value.agent_bootstrap_paths)) {
    errors.push("agent_bootstrap_paths must be an array.");
  } else {
    validatePathArray(value.agent_bootstrap_paths, "agent_bootstrap_paths", errors);
  }
  if (!Array.isArray(value.application_files)) {
    errors.push("application_files must be an array.");
  } else {
    const seen = new Set();
    for (const [index, file] of value.application_files.entries()) {
      if (!isRecord(file)) {
        errors.push(`application_files[${index}] must be an object.`);
        continue;
      }
      try {
        assertRelativePath(file.path, `application_files[${index}].path`);
      } catch (error) {
        errors.push(error.message);
      }
      if (typeof file.owner !== "string" || !file.owner) {
        errors.push(`application_files[${index}].owner is required.`);
      }
      if (
        file.fingerprint != null &&
        (
          typeof file.fingerprint !== "string" ||
          !/^[a-f0-9]{64}$/.test(file.fingerprint)
        )
      ) {
        errors.push(`application_files[${index}].fingerprint is invalid.`);
      }
      if (seen.has(file.path)) errors.push(`application_files path is duplicated: ${file.path}.`);
      seen.add(file.path);
    }
    if (!seen.has(value.primary_state)) {
      errors.push("application_files must include primary_state.");
    }
  }
  if (!isRecord(value.content_fingerprints)) {
    errors.push("content_fingerprints must be an object.");
  } else {
    for (const [path, fingerprint] of Object.entries(value.content_fingerprints)) {
      try {
        assertRelativePath(path, "content_fingerprints path");
      } catch (error) {
        errors.push(error.message);
      }
      if (typeof fingerprint !== "string" || !/^[a-f0-9]{64}$/.test(fingerprint)) {
        errors.push(`content_fingerprints value is invalid: ${path}.`);
      }
    }
    if (!(value.primary_state in value.content_fingerprints)) {
      errors.push("content_fingerprints must include primary_state.");
    }
  }
  for (const field of ["created_at", "updated_at"]) {
    if (field in value && !validTimestamp(value[field])) {
      errors.push(`${field} must be strict ISO 8601 with Z or an explicit offset.`);
    }
  }
  return errors.length ? { ok: false, errors } : { ok: true, value };
}

function validatePathArray(values, label, errors) {
  const seen = new Set();
  for (const [index, path] of values.entries()) {
    try {
      assertRelativePath(path, `${label}[${index}]`);
    } catch (error) {
      errors.push(error.message);
    }
    if (seen.has(path)) errors.push(`${label} contains duplicate path: ${path}.`);
    seen.add(path);
  }
}

export function validateCoordinationRecord(value, expectedWorkspaceId) {
  const errors = [];
  if (!isRecord(value)) return invalid("Coordination record must be an object.");
  if (value.workspace_id !== expectedWorkspaceId) errors.push("workspace_id does not match.");
  if (value.protocol_version !== PROTOCOL_VERSION) errors.push("protocol_version is unsupported.");
  try {
    assertActorId(value.actor_id, "actor_id");
    if (value.holder_id != null) assertActorId(value.holder_id, "holder_id");
  } catch (error) {
    errors.push(error.message);
  }
  if (
    value.run_id != null &&
    (
      typeof value.run_id !== "string" ||
      !RUN_ID_PATTERN.test(value.run_id)
    )
  ) {
    errors.push("run_id is invalid or not portable.");
  }
  if (!Number.isSafeInteger(value.sequence) || value.sequence < 0) {
    errors.push("sequence must be a non-negative integer.");
  }
  if (!Number.isSafeInteger(value.control_generation) || value.control_generation < 0) {
    errors.push("control_generation must be a non-negative integer.");
  }
  if (!Number.isSafeInteger(value.observed_revision) || value.observed_revision < 0) {
    errors.push("observed_revision must be a non-negative integer.");
  }
  if (!CONTROL_STATES.includes(value.requested_state)) errors.push("requested_state is invalid.");
  if (!validTimestamp(value.timestamp)) {
    errors.push("timestamp must be an ISO 8601 timestamp.");
  } else if (Date.parse(value.timestamp) > Date.now() + MAX_COORDINATION_FUTURE_SKEW_MS) {
    errors.push("timestamp is untrustworthily far in the future.");
  }
  return errors.length ? { ok: false, errors } : { ok: true, value };
}

export function validateArchive(value) {
  const errors = [];
  if (!isRecord(value)) return invalid("Archive must be a JSON object.");
  if (value.format !== ARCHIVE_FORMAT) errors.push(`format must be ${ARCHIVE_FORMAT}.`);
  const manifest = validateManifest(value.manifest);
  if (!manifest.ok) errors.push(...manifest.errors.map((error) => `manifest: ${error}`));
  let totalBytes = 0;
  if (typeof value.board_base64 !== "string" || !value.board_base64) {
    errors.push("board_base64 is required.");
  } else {
    try {
      totalBytes += decodedBase64Length(value.board_base64);
    } catch (error) {
      errors.push(`board_base64: ${error.message}`);
    }
  }
  if (!isRecord(value.files)) errors.push("files must be an object.");
  if (isRecord(value.files)) {
    const entries = Object.entries(value.files);
    let contentFileCount = 0;
    for (const [path, entry] of entries) {
      try {
        const parts = assertRelativePath(path, "archive file path");
        if (typeof entry === "string") {
          if (!BOOTSTRAP_FILES.includes(path)) {
            throw new ValidationError("Text archive entries must be recognized bootstrap files.");
          }
          totalBytes += new TextEncoder().encode(entry).byteLength;
          continue;
        }
        contentFileCount += 1;
        if (!isRecord(entry) || entry.encoding !== "base64" || typeof entry.data !== "string") {
          throw new ValidationError("Binary archive entries must use base64 encoding.");
        }
        if (!["attachments", "artifacts"].includes(parts[0])) {
          throw new ValidationError("Binary archive entries must stay under attachments/ or artifacts/.");
        }
        if (
          !Number.isSafeInteger(entry.size) ||
          entry.size < 0 ||
          entry.size > MAX_ARCHIVE_FILE_BYTES
        ) {
          throw new ValidationError("Binary archive entry size is invalid.");
        }
        if (
          typeof entry.fingerprint !== "string" ||
          !/^[a-f0-9]{64}$/.test(entry.fingerprint)
        ) {
          throw new ValidationError("Binary archive entry fingerprint is invalid.");
        }
        const decodedSize = decodedBase64Length(entry.data);
        if (decodedSize !== entry.size) {
          throw new ValidationError("Binary archive entry size does not match its payload.");
        }
        totalBytes += decodedSize;
      } catch (error) {
        errors.push(error.message);
      }
    }
    if (contentFileCount > MAX_ARCHIVE_FILES) {
      errors.push(`Archive content exceeds the ${MAX_ARCHIVE_FILES} file limit.`);
    }
    if (totalBytes > MAX_ARCHIVE_TOTAL_BYTES) {
      errors.push("Archive content exceeds the 250 MB total limit.");
    }
  }
  return errors.length ? { ok: false, errors } : { ok: true, value };
}

function decodedBase64Length(value) {
  if (
    value.length % 4 !== 0 ||
    !/^[A-Za-z0-9+/]*={0,2}$/.test(value)
  ) {
    throw new ValidationError("Base64 payload is malformed.");
  }
  const padding = value.endsWith("==") ? 2 : value.endsWith("=") ? 1 : 0;
  return (value.length / 4) * 3 - padding;
}

export function cleanText(value, label, maximum = 10_000, required = false) {
  if (typeof value !== "string") throw new ValidationError(`${label} must be text.`);
  const normalized = value.trim();
  if (required && !normalized) throw new ValidationError(`${label} is required.`);
  if (normalized.length > maximum) throw new ValidationError(`${label} is too long.`);
  return normalized;
}

export function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function validTimestamp(value) {
  if (typeof value !== "string") return false;
  const match = value.match(ISO_TIMESTAMP_PATTERN);
  if (!match) return false;
  const [, year, month, day, hour, minute, second, , zone, , offsetHour, offsetMinute] = match;
  const components = [year, month, day, hour, minute, second].map(Number);
  const [numericYear, numericMonth, numericDay, numericHour, numericMinute, numericSecond] = components;
  if (
    numericMonth < 1 ||
    numericMonth > 12 ||
    numericHour > 23 ||
    numericMinute > 59 ||
    numericSecond > 59
  ) return false;
  const date = new Date(Date.UTC(
    numericYear,
    numericMonth - 1,
    numericDay,
    numericHour,
    numericMinute,
    numericSecond,
  ));
  if (
    date.getUTCFullYear() !== numericYear ||
    date.getUTCMonth() !== numericMonth - 1 ||
    date.getUTCDate() !== numericDay
  ) return false;
  if (zone !== "Z") {
    const offsetHours = Number(offsetHour);
    const offsetMinutes = Number(offsetMinute);
    if (
      offsetHours > 14 ||
      offsetMinutes > 59 ||
      (offsetHours === 14 && offsetMinutes !== 0)
    ) return false;
  }
  return Number.isFinite(Date.parse(value));
}

function invalid(message) {
  return { ok: false, errors: [message] };
}
