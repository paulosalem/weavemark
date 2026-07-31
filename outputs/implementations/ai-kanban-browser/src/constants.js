export const APP_VERSION = "2.0.0";
export const SCHEMA_VERSION = 6;
export const WORKSPACE_FORMAT = "ai-kanban-workspace";
export const WORKSPACE_FORMAT_VERSION = 1;
export const PROTOCOL_VERSION = 1;
export const MANIFEST_FILE = "manifest.json";
export const STATE_FILE = "board.sqlite";
export const ARCHIVE_FORMAT = "ai-kanban-archive/v1";

export const RESERVED_DIRECTORIES = Object.freeze([
  "attachments",
  "artifacts",
  "exports",
  ".ai-kanban/coordination",
  ".agents/skills/ai-kanban",
]);

export const BOOTSTRAP_FILES = Object.freeze([
  "AGENTS.md",
  "CLAUDE.md",
  ".agents/skills/ai-kanban/SKILL.md",
  ".agents/skills/ai-kanban/ai_kanban.py",
  ".agents/skills/ai-kanban/ai-kanban.sh",
  ".agents/skills/ai-kanban/ai-kanban.ps1",
]);

export const APPLICATION_FILES = Object.freeze([
  MANIFEST_FILE,
  STATE_FILE,
  ...BOOTSTRAP_FILES,
  ".ai-kanban/coordination/human.json",
]);

export const COLUMN_IDS = Object.freeze([
  "inbox",
  "planning",
  "in_progress",
  "review",
  "blocked",
  "done",
]);

export const TURN_STATUSES = Object.freeze([
  "queued",
  "claimed",
  "running",
  "needs_input",
  "review",
  "complete",
  "failed",
  "cancelled",
]);

export const ACTIVE_TURN_STATUSES = Object.freeze([
  "queued",
  "claimed",
  "running",
  "needs_input",
  "review",
]);

export const OUTPUT_TYPES = Object.freeze([
  "text",
  "status",
  "link",
  "program",
  "table",
  "diff",
  "image",
  "file",
]);

export const OUTPUT_STATUSES = Object.freeze([
  "draft",
  "streaming",
  "complete",
  "failed",
  "stale",
  "superseded",
  "approved",
]);

export const CONTROL_STATES = Object.freeze([
  "human",
  "granting_agent",
  "agent",
  "reclaim_requested",
  "recovering",
]);

export const MAX_WORKSPACE_BYTES = 250 * 1024 * 1024;
export const MAX_ARCHIVE_FILE_BYTES = 50 * 1024 * 1024;
export const MAX_ARCHIVE_TOTAL_BYTES = 250 * 1024 * 1024;
export const MAX_ARCHIVE_ENCODED_BYTES =
  Math.ceil((MAX_ARCHIVE_TOTAL_BYTES * 4) / 3) + 32 * 1024 * 1024;
export const MAX_ARCHIVE_FILES = 5_000;
