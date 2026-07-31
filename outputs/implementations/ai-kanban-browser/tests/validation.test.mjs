import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  assertRelativePath,
  validateArchive,
  validateCoordinationRecord,
  validateManifest,
  validTimestamp,
} from "../src/validation.js";

const manifest = {
  format: "ai-kanban-workspace",
  format_version: 1,
  protocol_version: 1,
  schema_version: 4,
  workspace_id: "workspace-1",
  revision: 0,
  primary_state: "board.sqlite",
  reserved_directories: ["attachments", ".ai-kanban/coordination"],
  application_files: [{ path: "board.sqlite", owner: "ai-kanban" }],
  agent_bootstrap_paths: [".agents/skills/ai-kanban/SKILL.md"],
  content_fingerprints: { "board.sqlite": "0".repeat(64) },
};

test("accepts the versioned portable manifest", () => {
  assert.equal(validateManifest(manifest).ok, true);
});

test("rejects malformed nested manifest application files before use", () => {
  for (const applicationFiles of [
    [null],
    [{}],
    [{ path: "../escape", owner: "ai-kanban" }],
    [{ path: "board.sqlite", owner: "", fingerprint: "bad" }],
    [
      { path: "board.sqlite", owner: "ai-kanban" },
      { path: "board.sqlite", owner: "ai-kanban" },
    ],
  ]) {
    const result = validateManifest({
      ...manifest,
      application_files: applicationFiles,
    });
    assert.equal(result.ok, false);
  }
});

test("rejects absolute, traversal, drive, and backslash paths", () => {
  for (const path of ["/etc/passwd", "../escape", "a/../../escape", "C:/escape", "a\\b"]) {
    assert.throws(() => assertRelativePath(path), /path|escape|relative/i);
  }
});

test("rejects mismatched, stale-shaped coordination records", () => {
  const result = validateCoordinationRecord({
    workspace_id: "other",
    protocol_version: 1,
    actor_id: "agent-1",
    holder_id: "agent-1",
    sequence: -1,
    control_generation: 2,
    observed_revision: 8,
    requested_state: "agent",
    timestamp: "not-a-date",
  }, "workspace-1");
  assert.equal(result.ok, false);
  assert.match(result.errors.join(" "), /workspace_id/);
  assert.match(result.errors.join(" "), /sequence/);
  assert.match(result.errors.join(" "), /timestamp/);
});

test("coordination actors are portable and timestamps require an offset", () => {
  const base = {
    workspace_id: "workspace-1",
    protocol_version: 1,
    actor_id: "agent-1",
    holder_id: "agent-1",
    sequence: 1,
    control_generation: 2,
    observed_revision: 8,
    requested_state: "agent",
    timestamp: "2026-07-31T03:00:00Z",
  };
  assert.equal(validateCoordinationRecord(base, "workspace-1").ok, true);
  assert.equal(validateCoordinationRecord({
    ...base,
    actor_id: "agent:windows-stream",
  }, "workspace-1").ok, false);
  assert.equal(validateCoordinationRecord({
    ...base,
    run_id: "run;touch-owned",
  }, "workspace-1").ok, false);
  assert.equal(validateCoordinationRecord({
    ...base,
    timestamp: "2026-07-31T03:00:00",
  }, "workspace-1").ok, false);
  assert.equal(validTimestamp("2026-07-31T03:00:00-03:00"), true);
  assert.equal(validTimestamp("2026-02-30T03:00:00Z"), false);
  assert.equal(validTimestamp("2026-07-31 03:00:00Z"), false);
});

test("coordination records reject timestamps beyond the bounded future skew", () => {
  const result = validateCoordinationRecord({
    workspace_id: "workspace-1",
    protocol_version: 1,
    actor_id: "agent-1",
    holder_id: "agent-1",
    sequence: 1,
    control_generation: 0,
    observed_revision: 0,
    requested_state: "agent",
    timestamp: new Date(Date.now() + 31_000).toISOString(),
  }, "workspace-1");
  assert.equal(result.ok, false);
  assert.match(result.errors.join(" "), /future/);
});

test("validates a portable archive without trusting file paths", () => {
  const attachment = Buffer.from([1, 2, 3]);
  const fingerprint = createHash("sha256").update(attachment).digest("hex");
  const valid = validateArchive({
    format: "ai-kanban-archive/v1",
    manifest,
    board_base64: "AA==",
    files: {
      "AGENTS.md": "content",
      "attachments/photo.bin": {
        encoding: "base64",
        data: attachment.toString("base64"),
        size: attachment.length,
        fingerprint,
        kind: "attachment",
      },
    },
  });
  assert.equal(valid.ok, true);

  const invalid = validateArchive({
    format: "ai-kanban-archive/v1",
    manifest,
    board_base64: "AA==",
    files: { "../AGENTS.md": "content" },
  });
  assert.equal(invalid.ok, false);

  const mismatched = validateArchive({
    format: "ai-kanban-archive/v1",
    manifest,
    board_base64: "AA==",
    files: {
      "attachments/photo.bin": {
        encoding: "base64",
        data: attachment.toString("base64"),
        size: attachment.length + 1,
        fingerprint,
        kind: "attachment",
      },
    },
  });
  assert.equal(mismatched.ok, false);
  assert.match(mismatched.errors.join(" "), /size does not match/);
});
