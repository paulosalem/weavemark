/* global initSqlJs */
importScripts("../vendor/sql-wasm.js");

const SCHEMA_VERSION = 6;
const PROTOCOL_VERSION = 1;
const DEFAULT_COLUMNS = [
  ["inbox", "Inbox", 100, "#64757a"],
  ["planning", "Planning", 200, "#547c86"],
  ["in_progress", "In Progress", 300, "#22746b"],
  ["review", "Review", 400, "#9a6b35"],
  ["blocked", "Blocked", 500, "#b55249"],
  ["done", "Done", 600, "#52735e"],
];
const ACTIVE_TURNS = ["queued", "claimed", "running", "needs_input", "review"];
const TURN_STATUSES = [...ACTIVE_TURNS, "complete", "failed", "cancelled"];
const OUTPUT_TYPES = ["text", "status", "link", "program", "table", "diff", "image", "file"];
const OUTPUT_STATUSES = [
  "draft",
  "streaming",
  "complete",
  "failed",
  "stale",
  "superseded",
  "approved",
];
const PLAN_STATES = ["pending", "active", "done", "skipped", "blocked", "failed"];
const DECISION_PHASES = [
  "briefing",
  "exploring",
  "needs_feedback",
  "committed",
  "deep_work",
  "review",
  "accepted",
];
const MEMORY_STATES = [
  "new",
  "materially_updated",
  "unchanged_context",
  "duplicate_coverage",
  "corrected",
  "no_longer_current",
  "dismissed",
  "forgotten",
];
const OBSERVATION_STATES = [
  "new",
  "materially_updated",
  "unchanged_context",
  "duplicate_coverage",
  "no_longer_current",
];

let SQL;
let db = null;
let originalBytes = null;

const ready = (async () => {
  SQL = await initSqlJs({
    locateFile: () => new URL("../vendor/sql-wasm.wasm", self.location.href).href,
  });
})();

self.addEventListener("message", async ({ data }) => {
  const id = data?.id;
  try {
    await ready;
    validatePacket(data);
    const result = await dispatch(data.type, data.payload || {});
    const transfer = result?.buffer instanceof ArrayBuffer ? [result.buffer] : [];
    self.postMessage({ id, ok: true, result }, transfer);
  } catch (error) {
    self.postMessage({
      id,
      ok: false,
      error: {
        code: error.code || "SQLITE_ERROR",
        message: error.message || String(error),
        details: error.details || null,
      },
    });
  }
});

function dispatch(type, payload) {
  switch (type) {
    case "create":
      return createDatabase(Boolean(payload.seed), payload.workspaceId);
    case "open":
      return openDatabase(payload.buffer);
    case "health":
      return health();
    case "snapshot":
      requireDatabase();
      return getSnapshot();
    case "query":
      requireDatabase();
      return query(payload.name, payload.parameters || {});
    case "mutate":
      return mutate(payload.operation, payload.parameters || {}, payload.context || {});
    case "export": {
      requireDatabase();
      const bytes = db.export();
      const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
      return { buffer, revision: Number(meta("revision")) };
    }
    case "close":
      db?.close();
      db = null;
      originalBytes = null;
      return { closed: true };
    default:
      throw typedError("UNKNOWN_OPERATION", `Unsupported worker operation: ${type}`);
  }
}

function createDatabase(seed, workspaceId) {
  db?.close();
  db = new SQL.Database();
  configureDatabase();
  createSchema(workspaceId);
  if (seed) seedDemo();
  return getSnapshot();
}

function openDatabase(buffer) {
  if (!(buffer instanceof ArrayBuffer)) {
    throw typedError("INVALID_PACKET", "Opening a workspace requires database bytes.");
  }
  const bytes = new Uint8Array(buffer);
  const previous = db;
  const previousOriginalBytes = originalBytes;
  let candidate;
  try {
    candidate = new SQL.Database(bytes);
    db = candidate;
    configureDatabase();
    migrateDatabase();
    validateLoadedDatabase();
    const integrity = scalar("PRAGMA integrity_check");
    if (integrity !== "ok") throw typedError("CORRUPT_DATABASE", `Integrity check failed: ${integrity}`);
    const foreignKeyViolations = rows("PRAGMA foreign_key_check");
    if (foreignKeyViolations.length) {
      throw typedError(
        "FOREIGN_KEY_VIOLATION",
        `Foreign-key check found ${foreignKeyViolations.length} violation(s).`,
      );
    }
    const opened = db;
    if (previous && previous !== opened) previous.close();
    originalBytes = bytes.slice();
    return getSnapshot();
  } catch (error) {
    const failed = db;
    if (failed && failed !== previous) {
      try {
        failed.close();
      } catch {
        // Preserve the prior connection even when candidate cleanup fails.
      }
    }
    if (candidate && candidate !== failed && candidate !== previous) {
      try {
        candidate.close();
      } catch {
        // Candidate migration may already have closed the original candidate.
      }
    }
    db = previous;
    originalBytes = previousOriginalBytes;
    if (error.code) throw error;
    throw typedError(
      "CORRUPT_DATABASE",
      "This file is unreadable or is not a valid SQLite database.",
    );
  }
}

function configureDatabase() {
  db.run("PRAGMA foreign_keys = ON");
  db.run("PRAGMA journal_mode = DELETE");
  db.run("PRAGMA synchronous = FULL");
  db.run("PRAGMA busy_timeout = 5000");
}

function createSchema(workspaceId = null, stableCreatedAt = null) {
  db.run("BEGIN");
  try {
    db.run(SCHEMA_SQL);
    const stableWorkspaceId = workspaceId
      ? requireId(workspaceId, "workspaceId")
      : crypto.randomUUID();
    const createdAt = stableCreatedAt || now();
    const metadata = {
      schema_version: String(SCHEMA_VERSION),
      protocol_version: String(PROTOCOL_VERSION),
      workspace_format: "ai-kanban-workspace",
      format_version: "1",
      workspace_id: stableWorkspaceId,
      revision: "0",
      control_state: "human",
      control_owner: "human",
      control_holder: "human",
      control_generation: "0",
      control_lease_until: "",
      created_at: createdAt,
      updated_at: createdAt,
    };
    const statement = db.prepare("INSERT INTO metadata(key,value) VALUES(?,?)");
    for (const [key, value] of Object.entries(metadata)) statement.run([key, value]);
    statement.free();
    const columnStatement = db.prepare(
      "INSERT INTO columns(id,title,position,color) VALUES(?,?,?,?)",
    );
    for (const column of DEFAULT_COLUMNS) columnStatement.run(column);
    columnStatement.free();
    db.run("COMMIT");
  } catch (error) {
    db.run("ROLLBACK");
    throw error;
  }
}

function migrateDatabase() {
  const hasMetadata = Boolean(
    scalar("SELECT name FROM sqlite_master WHERE type='table' AND name='metadata'"),
  );
  const hasLegacyMeta = Boolean(
    scalar("SELECT name FROM sqlite_master WHERE type='table' AND name='meta'"),
  );
  if (!hasMetadata && hasLegacyMeta) {
    migrateLegacyV1();
    return;
  }
  if (!hasMetadata) throw typedError("INVALID_SCHEMA", "This is not an AI Kanban workspace.");
  let version = Number(meta("schema_version"));
  if (!Number.isInteger(version)) throw typedError("INVALID_SCHEMA", "Schema version is missing.");
  if (version > SCHEMA_VERSION) {
    throw typedError(
      "FUTURE_SCHEMA",
      `Workspace schema ${version} is newer than supported schema ${SCHEMA_VERSION}.`,
    );
  }
  if (version < 2) throw typedError("UNSUPPORTED_SCHEMA", `Workspace schema ${version} is unsupported.`);
  if (version === 2) {
    migrateV2ToV3();
    version = 3;
  }
  if (version === 3) {
    migrateV3ToV4();
    version = 4;
  }
  if (version === 4) {
    migrateV4ToV5();
    version = 5;
  }
  if (version === 5) migrateV5ToV6();
  validateRequiredTables();
}

function migrateLegacyV1() {
  const legacy = {
    workspaceId: scalar("SELECT value FROM meta WHERE key='workspace_id'"),
    columns: rows("SELECT id,title,position,color FROM columns ORDER BY position"),
    cards: rows("SELECT * FROM cards ORDER BY id"),
    plan: rows("SELECT * FROM plan_items ORDER BY card_id,position,id"),
    outputs: rows("SELECT * FROM outputs ORDER BY card_id,created_at,id"),
    activity: rows("SELECT * FROM activity ORDER BY created_at,id"),
    dependencies: tableExists("dependencies")
      ? rows("SELECT * FROM dependencies ORDER BY card_id,depends_on_id")
      : [],
    handoffs: tableExists("handoffs") ? rows("SELECT * FROM handoffs ORDER BY id") : [],
  };
  const legacyTimestamp = stableMigrationTimestamp(legacy);
  legacy.workspaceId ||= stableDerivedId("workspace", JSON.stringify(legacy));
  const migrated = new SQL.Database();
  const old = db;
  db = migrated;
  try {
    configureDatabase();
    createSchema(legacy.workspaceId, legacyTimestamp);
    setMeta("workspace_id", legacy.workspaceId);
    db.run("DELETE FROM columns");
    for (const column of legacy.columns) {
      run("INSERT INTO columns(id,title,position,color) VALUES(?,?,?,?)", [
        column.id === "progress" ? "in_progress" : column.id,
        column.title,
        column.position,
        column.color,
      ]);
    }
    for (const card of legacy.cards) {
      run(
        `INSERT INTO cards(
          id,column_id,position,title,description,priority,assignee,kind,attention,
          created_at,updated_at,archived,last_change_actor,provenance
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
        [
          card.id,
          card.column_id === "progress" ? "in_progress" : card.column_id,
          card.position,
          card.title,
          card.description || "",
          card.priority || "P2",
          card.assignee || "",
          "task",
          "none",
          card.created_at,
          card.updated_at,
          card.archived || 0,
          "migration",
          '{"origin":"legacy-v1"}',
        ],
      );
    }
    for (const item of legacy.plan) {
      run(
        "INSERT INTO plan_items(id,card_id,position,text,state,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
        [
          item.id,
          item.card_id,
          item.position,
          item.text,
          item.status === "running" ? "active" : item.status,
          item.created_at,
          item.updated_at,
        ],
      );
    }
    for (const output of legacy.outputs) {
      insertOutput({
        id: output.id,
        cardId: output.card_id,
        type: output.type,
        title: output.title,
        content: output.content,
        status: output.status,
        owner: "migration",
        createdAt: output.created_at,
        updatedAt: output.updated_at,
        versionId: stableDerivedId("output-version", output.id, "1"),
        surfaceId: stableDerivedId("output-surface", output.id, "1"),
      }, false);
    }
    for (const event of legacy.activity) {
      run(
        `INSERT INTO activity_events(id,card_id,type,actor,summary,payload,created_at)
         VALUES(?,?,?,?,?,?,?)`,
        [
          event.id,
          event.card_id,
          event.type,
          event.actor,
          event.summary,
          event.payload || "{}",
          event.created_at,
        ],
      );
    }
    for (const dependency of legacy.dependencies) {
      run("INSERT INTO dependencies(card_id,depends_on_id,created_at) VALUES(?,?,?)", [
        dependency.card_id,
        dependency.depends_on_id,
        dependency.created_at || legacyTimestamp,
      ]);
    }
    for (const handoff of legacy.handoffs) {
      run(
        `INSERT INTO handoff_packets(
          id,card_id,direction,format,payload,status,created_at,approved_at
        ) VALUES(?,?,?,?,?,?,?,?)`,
        [
          handoff.id,
          handoff.card_id,
          handoff.direction,
          handoff.direction === "import" ? "ai-kanban-response/v1" : "ai-kanban-handoff/v1",
          handoff.payload,
          "approved",
          handoff.created_at,
          handoff.created_at,
        ],
      );
    }
    db.run(`
      UPDATE cards
         SET latest_output_id=(
               SELECT o.id FROM outputs o
                WHERE o.card_id=cards.id
                  AND o.status IN ('complete','approved')
                ORDER BY o.updated_at DESC,o.id DESC LIMIT 1
             ),
             latest_successful_output_version_id=(
               SELECT v.id
                 FROM output_versions v
                 JOIN outputs o ON o.id=v.output_id
                WHERE o.card_id=cards.id
                  AND v.status IN ('complete','approved')
                ORDER BY o.updated_at DESC,v.version DESC,v.id DESC LIMIT 1
             )
    `);
    setMeta("revision", "1");
    old.close();
  } catch (error) {
    migrated.close();
    db = old;
    throw typedError("MIGRATION_FAILED", `Legacy migration failed: ${error.message}`);
  }
}

function migrateV2ToV3() {
  db.run("BEGIN");
  try {
    db.run(SCHEMA_SQL);
    if (!columnExists("cards", "last_change_actor")) {
      db.run("ALTER TABLE cards ADD COLUMN last_change_actor TEXT NOT NULL DEFAULT 'migration'");
    }
    setMeta("schema_version", "3");
    db.run("COMMIT");
  } catch (error) {
    db.run("ROLLBACK");
    throw typedError("MIGRATION_FAILED", `Schema migration failed: ${error.message}`);
  }
}

function migrateV3ToV4() {
  db.run("BEGIN");
  try {
    if (!columnExists("cards", "latest_successful_output_version_id")) {
      db.run("ALTER TABLE cards ADD COLUMN latest_successful_output_version_id TEXT");
    }

    db.run(`
      UPDATE cards
         SET latest_successful_output_version_id=(
           SELECT v.id
             FROM output_versions v
             JOIN outputs o ON o.id=v.output_id
            WHERE o.card_id=cards.id
              AND v.status IN ('complete','approved')
            ORDER BY o.updated_at DESC,v.version DESC,v.created_at DESC,v.id DESC
            LIMIT 1
         )
       WHERE latest_successful_output_version_id IS NULL
    `);
    if (!columnExists("idempotency_keys", "request_fingerprint")) {
      db.run("ALTER TABLE idempotency_keys ADD COLUMN request_fingerprint TEXT NOT NULL DEFAULT ''");
    }
    db.run(`
      CREATE TABLE IF NOT EXISTS coordination_outbox (
        idempotency_key TEXT NOT NULL,
        scope TEXT NOT NULL,
        actor TEXT NOT NULL,
        run_id TEXT NOT NULL,
        generation INTEGER NOT NULL,
        revision INTEGER NOT NULL,
        current_turn_id TEXT,
        status TEXT NOT NULL,
        requested_state TEXT NOT NULL,
        holder_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        PRIMARY KEY(idempotency_key,scope)
      )
    `);
    setMeta("schema_version", "4");
    db.run("COMMIT");
  } catch (error) {
    db.run("ROLLBACK");
    throw typedError("MIGRATION_FAILED", `Schema migration failed: ${error.message}`);
  }
}

function migrateV4ToV5() {
  db.run("BEGIN");
  try {
    if (!columnExists("coordination_outbox", "sequence")) {
      db.run("ALTER TABLE coordination_outbox ADD COLUMN sequence INTEGER NOT NULL DEFAULT 0");
    }
    if (!columnExists("coordination_outbox", "marker_json")) {
      db.run("ALTER TABLE coordination_outbox ADD COLUMN marker_json TEXT NOT NULL DEFAULT ''");
    }
    db.run(`
      CREATE TABLE IF NOT EXISTS coordination_state (
        actor TEXT PRIMARY KEY,
        sequence INTEGER NOT NULL,
        marker_json TEXT NOT NULL,
        revision INTEGER NOT NULL,
        generation INTEGER NOT NULL,
        updated_at TEXT NOT NULL
      )
    `);
    setMeta("schema_version", "5");
    setMeta("workspace_format", "ai-kanban-workspace");
    setMeta("format_version", "1");
    db.run("COMMIT");
  } catch (error) {
    db.run("ROLLBACK");
    throw typedError("MIGRATION_FAILED", `Schema migration failed: ${error.message}`);
  }
}

function migrateV5ToV6() {
  db.run("BEGIN");
  try {
    if (!columnExists("research_memory", "observation_state")) {
      db.run(
        `ALTER TABLE research_memory ADD COLUMN observation_state TEXT NOT NULL
         DEFAULT 'unchanged_context'
         CHECK(observation_state IN (
           'new','materially_updated','unchanged_context',
           'duplicate_coverage','no_longer_current'
         ))`,
      );
      db.run(`
        UPDATE research_memory
           SET observation_state=CASE
             WHEN state IN ('new','materially_updated','unchanged_context',
                            'duplicate_coverage','no_longer_current')
             THEN state
             ELSE 'unchanged_context'
           END
      `);
    }
    db.run("CREATE INDEX IF NOT EXISTS plan_items_card_state ON plan_items(card_id,state)");
    db.run("CREATE INDEX IF NOT EXISTS outputs_card ON outputs(card_id)");
    setMeta("schema_version", "6");
    db.run("COMMIT");
  } catch (error) {
    db.run("ROLLBACK");
    throw typedError("MIGRATION_FAILED", `Schema migration failed: ${error.message}`);
  }
}

function validateRequiredTables() {
  for (const table of [
    "metadata",
    "columns",
    "cards",
    "dependencies",
    "plan_items",
    "execution_turns",
    "turn_checkpoints",
    "outputs",
    "output_versions",
    "output_surfaces",
    "decision_threads",
    "decision_options",
    "decision_feedback",
    "decision_gates",
    "research_cycles",
    "research_memory",
    "research_coverage",
    "activity_events",
    "attachments",
    "artifacts",
    "handoff_packets",
    "agent_runs",
    "agent_questions",
    "agent_answers",
    "idempotency_keys",
    "coordination_outbox",
    "coordination_state",
  ]) {
    if (!tableExists(table)) throw typedError("INVALID_SCHEMA", `Workspace table is missing: ${table}.`);
  }
}

function validateLoadedDatabase() {
    const requiredColumns = {
      metadata: ["key", "value"],
      columns: ["id", "title", "position", "color"],
      cards: [
        "id", "column_id", "position", "title", "description", "priority",
        "assignee", "kind", "attention", "recurring", "archived",
      ],
      plan_items: ["id", "card_id", "position", "text", "state"],
      execution_turns: [
        "id", "card_id", "display_number", "status", "trigger", "requester",
        "actor", "instruction_snapshot",
      ],
      outputs: ["id", "card_id", "position", "type", "title", "owner", "status"],
      output_versions: ["id", "output_id", "version", "title", "payload", "status"],
      output_surfaces: ["id", "output_version_id", "type", "title", "payload"],
      decision_threads: ["id", "card_id", "phase", "briefing"],
      decision_options: ["id", "decision_id", "position", "title", "status"],
      decision_feedback: ["id", "decision_id", "actor", "action"],
      research_memory: [
        "id", "card_id", "subject", "summary", "state", "observation_state", "pinned",
      ],
      research_coverage: ["id", "cycle_id", "source_family", "status"],
      activity_events: ["id", "type", "actor", "summary", "created_at"],
      handoff_packets: ["id", "card_id", "direction", "format", "status"],
      agent_runs: ["id", "actor_id", "status", "control_generation", "observed_revision"],
      agent_questions: ["id", "turn_id", "question", "status"],
      agent_answers: ["id", "question_id", "actor", "answer"],
    };
    for (const [table, expected] of Object.entries(requiredColumns)) {
      const actual = new Set(rows(`PRAGMA table_info(${table})`).map((item) => item.name));
      const missing = expected.filter((column) => !actual.has(column));
      if (missing.length) {
        throw typedError(
          "INVALID_SCHEMA",
          `Workspace table ${table} is missing required columns: ${missing.join(", ")}.`,
        );
    }

    const enumRules = [
      ["cards", "priority", ["P0", "P1", "P2", "P3"]],
      ["cards", "kind", ["task", "question", "result"]],
      ["cards", "attention", ["none", "needs_you", "ai_working", "ai_updated"]],
      ["plan_items", "state", PLAN_STATES],
      ["execution_turns", "status", TURN_STATUSES],
      ["outputs", "type", OUTPUT_TYPES],
      ["outputs", "status", OUTPUT_STATUSES],
      ["output_versions", "status", OUTPUT_STATUSES],
      ["output_surfaces", "type", OUTPUT_TYPES],
      ["decision_threads", "phase", DECISION_PHASES],
      ["decision_options", "status", ["active", "shortlisted", "rejected", "selected"]],
      ["decision_feedback", "action", ["rank", "shortlist", "reject", "restore", "note"]],
      ["research_memory", "state", MEMORY_STATES],
      ["research_memory", "observation_state", OBSERVATION_STATES],
      ["research_coverage", "status", ["covered", "gap", "unavailable"]],
      ["handoff_packets", "direction", ["export", "import"]],
      ["handoff_packets", "status", ["draft", "previewed", "approved", "rejected"]],
      ["agent_runs", "status", ["registered", "watching", "working", "waiting", "stopped", "crashed"]],
      ["agent_questions", "status", ["open", "answered", "withdrawn"]],
    ];
    for (const [table, column, allowed] of enumRules) {
      const placeholders = allowed.map(() => "?").join(",");
      if (scalar(
        `SELECT 1 FROM ${table}
          WHERE typeof(${column})<>'text' OR ${column} NOT IN (${placeholders})
          LIMIT 1`,
        allowed,
      )) {
        throw typedError(
          "INVALID_DATABASE_CONTENT",
          `Workspace contains an invalid ${table}.${column} value.`,
        );
      }
    }

    const textColumns = {
      metadata: ["key", "value"],
      columns: ["id", "title", "color"],
      cards: [
        "id", "column_id", "title", "description", "priority", "assignee", "kind",
        "attention", "cadence", "lookback_window", "created_at", "updated_at",
        "provenance", "last_change_actor",
      ],
      plan_items: ["id", "card_id", "text", "state", "created_at", "updated_at"],
      execution_turns: [
        "id", "card_id", "status", "trigger", "requester", "actor", "agent_run_id",
        "idempotency_key", "instruction_snapshot", "queued_at", "result", "error",
        "cancellation_reason", "memory_lineage",
      ],
      outputs: [
        "id", "card_id", "type", "title", "owner", "status", "source", "lineage",
        "created_at", "updated_at",
      ],
      output_versions: [
        "id", "output_id", "title", "payload", "status", "source", "created_at",
      ],
      output_surfaces: [
        "id", "output_version_id", "type", "title", "payload", "reference",
        "alt_text", "created_at",
      ],
      agent_questions: ["id", "turn_id", "question", "context", "status", "created_at"],
      agent_answers: ["id", "question_id", "actor", "answer", "created_at"],
      activity_events: ["id", "type", "actor", "summary", "payload", "created_at"],
    };
    for (const [table, columns] of Object.entries(textColumns)) {
      for (const column of columns) {
        if (scalar(
          `SELECT 1 FROM ${table}
            WHERE ${column} IS NOT NULL AND typeof(${column})<>'text'
            LIMIT 1`,
        )) {
          throw typedError(
            "INVALID_DATABASE_CONTENT",
            `Workspace contains a non-text ${table}.${column} value.`,
          );
        }
      }
    }

    for (const [table, column] of [
      ["cards", "position"],
      ["plan_items", "position"],
      ["execution_turns", "display_number"],
      ["outputs", "position"],
      ["output_versions", "version"],
      ["decision_options", "position"],
      ["research_cycles", "cycle_number"],
    ]) {
      if (scalar(
        `SELECT 1 FROM ${table} WHERE typeof(${column})<>'integer' LIMIT 1`,
      )) {
        throw typedError(
          "INVALID_DATABASE_CONTENT",
          `Workspace contains a non-integer ${table}.${column} value.`,
        );
      }
    }
    for (const [table, column] of [
      ["cards", "recurring"],
      ["cards", "archived"],
      ["research_memory", "pinned"],
    ]) {
      if (scalar(
        `SELECT 1 FROM ${table}
          WHERE typeof(${column})<>'integer' OR ${column} NOT IN (0,1)
          LIMIT 1`,
      )) {
        throw typedError(
          "INVALID_DATABASE_CONTENT",
          `Workspace contains an invalid ${table}.${column} flag.`,
        );
      }
    }

    for (const column of rows("SELECT id,title,color FROM columns")) {
      if (
        !DEFAULT_COLUMNS.some(([id]) => id === column.id) ||
        typeof column.title !== "string" ||
        typeof column.color !== "string" ||
        !/^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i.test(column.color)
      ) {
        throw typedError(
          "INVALID_DATABASE_CONTENT",
          "Workspace contains an invalid board column definition.",
        );
      }
    }
  }
}

function health() {
  requireDatabase();
  const quickCheck = scalar("PRAGMA quick_check");
  const foreignKeyViolations = rows("PRAGMA foreign_key_check").length;
  return {
    ok: quickCheck === "ok" && foreignKeyViolations === 0,
    foreignKeys: Number(scalar("PRAGMA foreign_keys")) === 1,
    foreignKeyViolations,
    schemaVersion: Number(meta("schema_version")),
    revision: Number(meta("revision")),
    originalBytesRetained: Boolean(originalBytes),
  };
}

function query(name, parameters) {
  switch (name) {
    case "card":
      return getCard(requireId(parameters.cardId, "cardId"));
    case "archivedCards":
      return rows(
        `SELECT id,title,priority,kind,updated_at AS updatedAt
           FROM cards WHERE archived=1 ORDER BY updated_at DESC`,
      );
    case "search":
      return searchCards(parameters);
    case "readyTurns":
      return rows(
        `SELECT t.id,t.card_id AS cardId,t.display_number AS displayNumber,c.title,t.status
           FROM execution_turns t JOIN cards c ON c.id=t.card_id
          WHERE t.status='queued' ORDER BY t.queued_at,t.id`,
      );
    case "activity":
      return rows(
        `SELECT id,card_id AS cardId,type,actor,summary,payload,created_at AS createdAt
           FROM activity_events ORDER BY created_at DESC,rowid DESC LIMIT ?`,
        [boundedInteger(parameters.limit, 1, 500, 100)],
      ).map(parsePayload);
    case "archiveReferences":
      return [
        ...rows(
          `SELECT relative_path AS relativePath,size,fingerprint,'attachment' AS kind
             FROM attachments ORDER BY relative_path`,
        ),
        ...rows(
          `SELECT relative_path AS relativePath,NULL AS size,fingerprint,'artifact' AS kind
             FROM artifacts ORDER BY relative_path`,
        ),
      ];
    default:
      throw typedError("UNKNOWN_QUERY", `Unsupported repository query: ${name}`);
  }
}

function mutate(operation, parameters, context) {
  requireDatabase();
  validateContext(context, operation);
  db.run("BEGIN IMMEDIATE");
  try {
    verifyControl(context, operation);
    let result;
    switch (operation) {
      case "createCard":
        result = createCard(parameters, context);
        break;
      case "updateCard":
        result = updateCard(parameters, context);
        break;
      case "moveCard":
        result = moveCard(parameters, context);
        break;
      case "archiveCard":
        result = archiveCard(parameters, context);
        break;
      case "restoreCard":
        result = restoreCard(parameters, context);
        break;
      case "addDependency":
        result = addDependency(parameters, context);
        break;
      case "removeDependency":
        result = removeDependency(parameters, context);
        break;
      case "addPlanItem":
        result = addPlanItem(parameters, context);
        break;
      case "updatePlanItem":
        result = updatePlanItem(parameters, context);
        break;
      case "queueTurn":
        result = queueTurn(parameters, context);
        break;
      case "claimReadyTurn":
        result = claimReadyTurn(parameters, context);
        break;
      case "transitionTurn":
        result = transitionTurn(parameters, context);
        break;
      case "askQuestion":
        result = askQuestion(parameters, context);
        break;
      case "answerQuestion":
        result = answerQuestion(parameters, context);
        break;
      case "addOutput":
        result = addOutput(parameters, context);
        break;
      case "approveOutput":
        result = approveOutput(parameters, context);
        break;
      case "versionOutput":
        result = versionOutput(parameters, context);
        break;
      case "applyResponse":
        result = applyResponse(parameters, context);
        break;
      case "saveDecisionBriefing":
        result = saveDecisionBriefing(parameters, context);
        break;
      case "addDecisionOption":
        result = addDecisionOption(parameters, context);
        break;
      case "feedbackDecisionOption":
        result = feedbackDecisionOption(parameters, context);
        break;
      case "setDecisionGate":
        result = setDecisionGate(parameters, context);
        break;
      case "setDecisionPhase":
        result = setDecisionPhase(parameters, context);
        break;
      case "requestDecisionRevision":
        result = requestDecisionRevision(parameters, context);
        break;
      case "memoryAction":
        result = memoryAction(parameters, context);
        break;
      case "recordResearchMemory":
        result = recordResearchMemory(parameters, context);
        break;
      case "setControl":
        result = setControl(parameters, context);
        break;
      default:
        throw typedError("UNKNOWN_MUTATION", `Unsupported repository mutation: ${operation}`);
    }
    if (!result?.idempotent && !result?.noMutation) incrementRevision();
    db.run("COMMIT");
    return { ...result, snapshot: getSnapshot() };
  } catch (error) {
    db.run("ROLLBACK");
    throw error;
  }
}

function createCard(input, context) {
  const title = requireText(input.title, "title", 160);
  const columnId = input.columnId || "inbox";
  requireColumn(columnId);
  const priority = oneOf(input.priority || "P2", ["P0", "P1", "P2", "P3"], "priority");
  const kind = oneOf(input.kind || "task", ["task", "question", "result"], "kind");
  const id = crypto.randomUUID();
  const timestamp = now();
  run(
    `INSERT INTO cards(
      id,column_id,position,title,description,priority,assignee,kind,attention,
      recurring,cadence,lookback_window,created_at,updated_at,provenance,last_change_actor
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    [
      id,
      columnId,
      nextPosition("cards", "column_id", columnId),
      title,
      cleanText(input.description, 50_000),
      priority,
      cleanText(input.assignee, 100),
      kind,
      oneOf(input.attention || "none", ["none", "needs_you", "ai_working", "ai_updated"], "attention"),
      input.recurring ? 1 : 0,
      cleanText(input.cadence, 80),
      cleanText(input.lookbackWindow, 80),
      timestamp,
      timestamp,
      JSON.stringify({ origin: input.origin || "human", source: input.source || null }),
      context.actorId,
    ],
  );
  if (input.decision) {
    run(
      `INSERT INTO decision_threads(
        id,card_id,phase,briefing,created_at,updated_at
      ) VALUES(?,?,?,?,?,?)`,
      [crypto.randomUUID(), id, "briefing", "{}", timestamp, timestamp],
    );
  }
  appendActivity(id, "card_created", context.actorId, "Card created.", { columnId });
  return { cardId: id };
}

function updateCard(input, context) {
  const card = requireCard(input.cardId);
  const title = requireText(input.title, "title", 160);
  run(
    `UPDATE cards SET title=?,description=?,priority=?,assignee=?,kind=?,attention=?,
       recurring=?,cadence=?,lookback_window=?,updated_at=?,last_change_actor=? WHERE id=?`,
    [
      title,
      cleanText(input.description, 50_000),
      oneOf(input.priority || card.priority, ["P0", "P1", "P2", "P3"], "priority"),
      cleanText(input.assignee, 100),
      oneOf(input.kind || card.kind, ["task", "question", "result"], "kind"),
      oneOf(input.attention || card.attention, ["none", "needs_you", "ai_working", "ai_updated"], "attention"),
      input.recurring ? 1 : 0,
      cleanText(input.cadence, 80),
      cleanText(input.lookbackWindow, 80),
      now(),
      context.actorId,
      card.id,
    ],
  );
  appendActivity(card.id, "card_updated", context.actorId, "Card details updated.");
  return { cardId: card.id };
}

function moveCard(input, context) {
  const card = requireCard(input.cardId);
  const columnId = requireColumn(input.columnId);
  if (card.columnId === "done" && columnId === "inbox" && !input.confirmRunAgain) {
    throw typedError(
      "RUN_AGAIN_CONFIRMATION_REQUIRED",
      "Moving Done to Inbox creates a fresh linked turn. Confirm Run again to continue.",
    );
  }
  if (columnId === "done" && hasIncompleteDependencies(card.id)) {
    throw typedError("DEPENDENCIES_INCOMPLETE", "Complete this card's dependencies before moving it to Done.");
  }
  if (columnId === "done") {
    const active = activeTurn(card.id);
    if (active && active.status !== "queued") {
      throw typedError(
        "ACTIVE_TURN_BLOCKS_DONE",
        "Claimed or running work must finish or be cancelled before moving to Done.",
      );
    }
    if (active?.status === "queued") {
      run(
        `UPDATE execution_turns
            SET status='cancelled',cancelled_at=?,
                cancellation_reason='Card moved to Done before claim'
          WHERE id=?`,
        [now(), active.id],
      );
      run("UPDATE cards SET current_turn_id=NULL WHERE id=?", [card.id]);
      appendActivity(
        card.id,
        "turn_cancelled",
        context.actorId,
        "Queued turn cancelled because the card moved to Done.",
        { turnId: active.id },
      );
    }
  }
  if (card.columnId === "planning" && columnId === "in_progress") {
    const decision = decisionForCard(card.id);
    if (decision && !decision.selectedOptionId) {
      throw typedError(
        "DECISION_GATE_REQUIRED",
        "Select an option and confirm the deep-work gate before moving to In Progress.",
      );
    }
  }
  let position = nextPosition("cards", "column_id", columnId);
  if (input.beforeCardId) {
    const before = requireCard(input.beforeCardId);
    if (before.columnId !== columnId) throw typedError("INVALID_MOVE", "Drop target is in another column.");
    position = before.position - 1;
  }
  run(
    `UPDATE cards SET column_id=?,position=?,updated_at=?,last_change_actor=? WHERE id=?`,
    [columnId, position, now(), context.actorId, card.id],
  );
  normalizePositions(columnId);
  if (card.columnId !== columnId) normalizePositions(card.columnId);
  if (card.columnId === "done" && columnId === "inbox") {
    queueTurn(
      {
        cardId: card.id,
        instruction: input.instruction || card.description,
        trigger: "run_again",
        linkedTurnId: latestSuccessfulTurn(card.id)?.id || null,
      },
      context,
    );
  }
  if (card.columnId === "planning" && columnId === "in_progress") {
    const decision = decisionForCard(card.id);
    if (decision) {
      setDecisionPhase({ cardId: card.id, phase: "deep_work" }, context);
      queueTurn(
        {
          cardId: card.id,
          instruction: `Deep work for selected option ${decision.selectedOptionTitle}.`,
          trigger: "decision_gate",
        },
        context,
      );
    }
  }
  appendActivity(card.id, "card_moved", context.actorId, `Moved to ${columnTitle(columnId)}.`, {
    from: card.columnId,
    to: columnId,
  });
  return { cardId: card.id, columnId };
}

function archiveCard(input, context) {
  const card = requireCard(input.cardId);
  run(
    "UPDATE cards SET archived=1,updated_at=?,last_change_actor=? WHERE id=?",
    [now(), context.actorId, card.id],
  );
  appendActivity(card.id, "card_archived", context.actorId, "Card archived.");
  return { cardId: card.id };
}

function restoreCard(input, context) {
  const cardId = requireId(input.cardId, "cardId");
  if (!scalar("SELECT id FROM cards WHERE id=? AND archived=1", [cardId])) {
    throw typedError("CARD_NOT_FOUND", "Archived card was not found.");
  }
  run(
    "UPDATE cards SET archived=0,column_id='inbox',updated_at=?,last_change_actor=? WHERE id=?",
    [now(), context.actorId, cardId],
  );
  appendActivity(cardId, "card_restored", context.actorId, "Card restored to Inbox.");
  return { cardId };
}

function addDependency(input, context) {
  const card = requireCard(input.cardId);
  const dependency = requireCard(input.dependsOnId);
  if (card.id === dependency.id) throw typedError("INVALID_DEPENDENCY", "A card cannot depend on itself.");
  const createsCycle = Boolean(
    scalar(
      `WITH RECURSIVE reachable(id) AS (
         SELECT ?
         UNION
         SELECT d.depends_on_id
           FROM dependencies d JOIN reachable r ON d.card_id=r.id
       )
       SELECT 1 FROM reachable WHERE id=? LIMIT 1`,
      [dependency.id, card.id],
    ),
  );
  if (createsCycle) {
    throw typedError(
      "DEPENDENCY_CYCLE",
      `Adding ${dependency.title} would create a transitive dependency cycle.`,
    );
  }
  run(
    "INSERT OR IGNORE INTO dependencies(card_id,depends_on_id,created_at) VALUES(?,?,?)",
    [card.id, dependency.id, now()],
  );
  appendActivity(card.id, "dependency_added", context.actorId, `Depends on ${dependency.title}.`);
  return { cardId: card.id, dependsOnId: dependency.id };
}

function removeDependency(input, context) {
  const card = requireCard(input.cardId);
  const dependency = requireCard(input.dependsOnId);
  const existed = Boolean(
    scalar(
      "SELECT 1 FROM dependencies WHERE card_id=? AND depends_on_id=?",
      [card.id, dependency.id],
    ),
  );
  if (!existed) {
    throw typedError("DEPENDENCY_NOT_FOUND", "The dependency no longer exists.");
  }
  run(
    "DELETE FROM dependencies WHERE card_id=? AND depends_on_id=?",
    [card.id, dependency.id],
  );
  appendActivity(
    card.id,
    "dependency_removed",
    context.actorId,
    `Dependency removed: ${dependency.title}.`,
  );
  return { cardId: card.id, dependsOnId: dependency.id };
}

function addPlanItem(input, context) {
  const card = requireCard(input.cardId);
  const id = crypto.randomUUID();
  const timestamp = now();
  run(
    `INSERT INTO plan_items(id,card_id,position,text,state,created_at,updated_at)
     VALUES(?,?,?,?,?,?,?)`,
    [
      id,
      card.id,
      nextPosition("plan_items", "card_id", card.id),
      requireText(input.text, "text", 500),
      oneOf(input.state || "pending", PLAN_STATES, "state"),
      timestamp,
      timestamp,
    ],
  );
  appendActivity(card.id, "plan_updated", context.actorId, `Plan step added: ${cleanText(input.text, 500)}`);
  return { cardId: card.id, planItemId: id };
}

function updatePlanItem(input, context) {
  const card = requireCard(input.cardId);
  const id = requireId(input.planItemId, "planItemId");
  if (!scalar("SELECT id FROM plan_items WHERE id=? AND card_id=?", [id, card.id])) {
    throw typedError("PLAN_ITEM_NOT_FOUND", "Plan item was not found.");
  }
  run("UPDATE plan_items SET text=?,state=?,updated_at=? WHERE id=?", [
    requireText(input.text, "text", 500),
    oneOf(input.state, PLAN_STATES, "state"),
    now(),
    id,
  ]);
  appendActivity(card.id, "plan_updated", context.actorId, `Plan step marked ${input.state}.`);
  return { cardId: card.id, planItemId: id };
}

function queueTurn(input, context) {
  const card = requireCard(input.cardId);
  const idempotencyKey = requireText(
    input.idempotencyKey || crypto.randomUUID(),
    "idempotencyKey",
    200,
  );
  const instruction = requireText(
    input.instruction || card.description || card.title,
    "instruction",
    50_000,
  );
  const requestFingerprint = JSON.stringify({
    operation: "queue_turn",
    cardId: card.id,
    actorId: context.actorId,
    generation: Number(context.generation),
    trigger: input.trigger || "ready_for_agent",
    requester: input.requester || context.actorId,
    instruction,
    linkedTurnId: input.linkedTurnId || null,
    memoryLineage: input.memoryLineage || [],
  });
  const prior = rows(
    `SELECT result_id AS resultId,actor,request_fingerprint AS requestFingerprint
       FROM idempotency_keys WHERE key=? AND scope='queue_turn'`,
    [idempotencyKey],
  )[0];
  if (prior) {
    if (
      prior.actor !== context.actorId ||
      prior.requestFingerprint !== requestFingerprint
    ) {
      throw typedError(
        "IDEMPOTENCY_CONFLICT",
        "Queue idempotency key was reused with a different request.",
      );
    }
    return { cardId: card.id, turnId: prior.resultId, idempotent: true };
  }
  const existing = activeTurn(card.id);
  if (existing) throw typedError("ACTIVE_TURN_EXISTS", "This card already has an active turn.");
  const id = crypto.randomUUID();
  const displayNumber = Number(
    scalar("SELECT COALESCE(MAX(display_number),0)+1 FROM execution_turns WHERE card_id=?", [card.id]),
  );
  const timestamp = now();
  registerIdempotency(
    idempotencyKey,
    "queue_turn",
    id,
    context.actorId,
    requestFingerprint,
  );
  run(
    `INSERT INTO execution_turns(
      id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
      idempotency_key,instruction_snapshot,linked_turn_id,queued_at,memory_lineage
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    [
      id,
      card.id,
      displayNumber,
      "queued",
      input.trigger || "ready_for_agent",
      input.requester || context.actorId,
      "",
      "",
      idempotencyKey,
      instruction,
      input.linkedTurnId || null,
      timestamp,
      JSON.stringify(input.memoryLineage || []),
    ],
  );
  run(
    `UPDATE cards SET current_turn_id=?,attention='ai_working',updated_at=?,last_change_actor=?
      WHERE id=?`,
    [id, timestamp, context.actorId, card.id],
  );
  appendActivity(card.id, "turn_queued", context.actorId, `Turn ${displayNumber} is ready for an agent.`, {
    turnId: id,
  });
  return { cardId: card.id, turnId: id };
}

function claimReadyTurn(input, context) {
  const idempotencyKey = requireText(input.idempotencyKey, "idempotencyKey", 200);
  const requestFingerprint = JSON.stringify({
    operation: "claim_turn",
    actorId: context.actorId,
    generation: Number(context.generation),
    runId: input.runId || "",
  });
  const existing = rows(
    `SELECT result_id AS resultId,actor,request_fingerprint AS requestFingerprint
       FROM idempotency_keys WHERE key=? AND scope='claim_turn'`,
    [idempotencyKey],
  )[0];
  if (existing) {
    if (
      existing.actor !== context.actorId ||
      existing.requestFingerprint !== requestFingerprint
    ) {
      throw typedError(
        "IDEMPOTENCY_CONFLICT",
        "Claim idempotency key was reused with a different request.",
      );
    }
    const original = rows(
      `SELECT t.id AS turnId,t.card_id AS cardId,t.instruction_snapshot AS instruction,
              c.title
         FROM execution_turns t JOIN cards c ON c.id=t.card_id
        WHERE t.id=?`,
      [existing.resultId],
    )[0];
    if (!original) {
      throw typedError("IDEMPOTENCY_RESULT_MISSING", "Claim result no longer exists.");
    }
    return { ...original, idempotent: true };
  }
  const turn = rows(
    `SELECT t.id,t.card_id AS cardId,t.display_number AS displayNumber,
            t.instruction_snapshot AS instruction,c.title
       FROM execution_turns t JOIN cards c ON c.id=t.card_id
      WHERE t.status='queued' AND c.archived=0 AND c.column_id<>'done'
        AND NOT EXISTS (
          SELECT 1 FROM dependencies d JOIN cards dependency ON dependency.id=d.depends_on_id
           WHERE d.card_id=c.id AND dependency.column_id<>'done'
        )
      ORDER BY t.queued_at,t.id LIMIT 1`,
  )[0];
  if (!turn) return { turnId: null, noMutation: true };
  run(
    `UPDATE execution_turns SET status='claimed',actor=?,agent_run_id=?,claimed_at=?
      WHERE id=? AND status='queued'`,
    [context.actorId, input.runId || "", now(), turn.id],
  );
  registerIdempotency(
    idempotencyKey,
    "claim_turn",
    turn.id,
    context.actorId,
    requestFingerprint,
  );
  appendActivity(turn.cardId, "turn_claimed", context.actorId, `Turn ${turn.displayNumber} claimed.`);
  return {
    turnId: turn.id,
    cardId: turn.cardId,
    title: turn.title,
    instruction: turn.instruction,
  };
}

function transitionTurn(input, context) {
  const turn = requireTurn(input.turnId);
  const target = oneOf(input.status, TURN_STATUSES, "status");
  const turnDecision = decisionForCard(turn.cardId);
  const allowed = {
    queued: ["cancelled"],
    claimed: ["running", "cancelled", "failed"],
    running: ["needs_input", "review", "complete", "failed", "cancelled"],
    needs_input: ["cancelled"],
    review: ["complete", "running", "cancelled"],
    complete: [],
    failed: [],
    cancelled: [],
  };
  if (!allowed[turn.status].includes(target)) {
    throw typedError("INVALID_TURN_TRANSITION", `Cannot change ${turn.status} to ${target}.`);
  }
  if (target === "complete" && turnDecision) {
    throw typedError(
      "DECISION_ACCEPTANCE_REQUIRED",
      "Decision turns enter review and complete only when the proposal is accepted.",
    );
  }
  const timestamp = now();
  const fields = ["status=?"];
  const values = [target];
  const timestampColumns = {
    claimed: "claimed_at",
    running: "started_at",
    needs_input: "input_requested_at",
    review: "reviewed_at",
    complete: "completed_at",
    failed: "failed_at",
    cancelled: "cancelled_at",
  };
  fields.push(`${timestampColumns[target]}=?`);
  values.push(timestamp);
  if (input.result != null) {
    fields.push("result=?");
    values.push(cleanText(input.result, 100_000));
  }
  if (input.error != null) {
    fields.push("error=?");
    values.push(cleanText(input.error, 20_000));
  }
  if (input.reason != null) {
    fields.push("cancellation_reason=?");
    values.push(cleanText(input.reason, 2_000));
  }
  values.push(turn.id);
  run(`UPDATE execution_turns SET ${fields.join(",")} WHERE id=?`, values);
  let attention = target === "needs_input" ? "needs_you" : target === "review" ? "ai_updated" : "ai_working";
  if (["complete", "failed", "cancelled"].includes(target)) {
    attention = target === "complete" ? "ai_updated" : "needs_you";
    run("UPDATE cards SET current_turn_id=NULL WHERE id=?", [turn.cardId]);
    run(
      "UPDATE agent_questions SET status='withdrawn' WHERE turn_id=? AND status='open'",
      [turn.id],
    );
  }
  run(
    "UPDATE cards SET attention=?,updated_at=?,last_change_actor=? WHERE id=?",
    [attention, timestamp, context.actorId, turn.cardId],
  );
  if (target === "review") {
    run("UPDATE cards SET column_id='review' WHERE id=?", [turn.cardId]);
    if (turnDecision) {
      run(
        "UPDATE decision_threads SET phase='review',updated_at=? WHERE id=?",
        [timestamp, turnDecision.id],
      );
    }
  }
  if (target === "complete") {
    run(
      `UPDATE cards SET column_id=?,position=? WHERE id=?`,
      [
        input.moveToDone ? "done" : "review",
        nextPosition("cards", "column_id", input.moveToDone ? "done" : "review"),
        turn.cardId,
      ],
    );
  }
  if (target === "failed") {
    run(
      "UPDATE cards SET column_id='blocked',position=? WHERE id=?",
      [nextPosition("cards", "column_id", "blocked"), turn.cardId],
    );
  }
  appendActivity(turn.cardId, `turn_${target}`, context.actorId, `Turn ${turn.displayNumber} ${target}.`, {
    turnId: turn.id,
    partialOutputsRetained: target === "cancelled",
  });
  return { cardId: turn.cardId, turnId: turn.id };
}

function askQuestion(input, context) {
  const turn = requireTurn(input.turnId);
  if (turn.status !== "running") {
    throw typedError("INVALID_TURN_TRANSITION", "Questions can be asked only while a turn is running.");
  }
  const id = crypto.randomUUID();
  const timestamp = now();
  run(
    `INSERT INTO agent_questions(id,turn_id,question,context,status,created_at)
     VALUES(?,?,?,?,?,?)`,
    [
      id,
      turn.id,
      requireText(input.question, "question", 5_000),
      cleanText(input.context, 10_000),
      "open",
      timestamp,
    ],
  );
  run(
    "UPDATE execution_turns SET status='needs_input',input_requested_at=? WHERE id=?",
    [timestamp, turn.id],
  );
  run(
    "UPDATE cards SET attention='needs_you',updated_at=?,last_change_actor=? WHERE id=?",
    [timestamp, context.actorId, turn.cardId],
  );
  appendActivity(turn.cardId, "turn_needs_input", context.actorId, "Agent asked a focused question.", {
    questionId: id,
  });
  return { cardId: turn.cardId, turnId: turn.id, questionId: id };
}

function answerQuestion(input, context) {
  const questionId = requireId(input.questionId, "questionId");
  const question = rows(
    `SELECT q.id,q.turn_id AS turnId,t.card_id AS cardId
       FROM agent_questions q JOIN execution_turns t ON t.id=q.turn_id
      WHERE q.id=? AND q.status='open'`,
    [questionId],
  )[0];
  if (!question) throw typedError("QUESTION_NOT_FOUND", "Open question was not found.");
  const id = crypto.randomUUID();
  run(
    "INSERT INTO agent_answers(id,question_id,actor,answer,created_at) VALUES(?,?,?,?,?)",
    [id, question.id, context.actorId, requireText(input.answer, "answer", 20_000), now()],
  );
  run("UPDATE agent_questions SET status='answered',answered_at=? WHERE id=?", [now(), question.id]);
  const turn = requireTurn(question.turnId);
  if (turn.status === "needs_input") {
    run("UPDATE cards SET attention='ai_working' WHERE id=?", [question.cardId]);
  }
  appendActivity(question.cardId, "question_answered", context.actorId, "Agent question answered.");
  return { questionId, answerId: id, cardId: question.cardId };
}

function addOutput(input, context) {
  const card = requireCard(input.cardId);
  const outputId = insertOutput({
    ...input,
    owner: input.owner || context.actorId,
    createdAt: now(),
    updatedAt: now(),
  });
  appendActivity(card.id, "output_created", context.actorId, `Output added: ${input.title}`);
  return { cardId: card.id, outputId };
}

function insertOutput(input, updateCard = true) {
  const card = requireCard(input.cardId);
  const id = input.id || crypto.randomUUID();
  const timestamp = input.createdAt || now();
  const type = oneOf(input.type || "text", OUTPUT_TYPES, "type");
  const status = oneOf(input.status || "complete", OUTPUT_STATUSES, "status");
  const title = requireText(input.title, "title", 200);
  const content = ["program", "diff"].includes(type)
    ? exactText(input.content, 1_000_000)
    : cleanText(input.content, 1_000_000);
  const versionId = input.versionId || crypto.randomUUID();
  run(
    `INSERT INTO outputs(
      id,card_id,turn_id,position,type,title,owner,status,source,lineage,
      created_at,updated_at,current_version
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1)`,
    [
      id,
      card.id,
      input.turnId || null,
      nextPosition("outputs", "card_id", card.id),
      type,
      title,
      input.owner || "workspace",
      status,
      input.source || "workspace",
      JSON.stringify(input.lineage || []),
      timestamp,
      input.updatedAt || timestamp,
    ],
  );
  run(
    `INSERT INTO output_versions(
      id,output_id,version,title,payload,status,source,created_at
    ) VALUES(?,?,?,?,?,?,?,?)`,
    [
      versionId,
      id,
      1,
      title,
      content,
      status,
      input.source || "workspace",
      timestamp,
    ],
  );
  run(
    `INSERT INTO output_surfaces(
      id,output_version_id,type,title,payload,reference,schema_version,alt_text,created_at
    ) SELECT ?,id,?,?,?,?,?,?,? FROM output_versions WHERE output_id=? AND version=1`,
    [
      input.surfaceId || crypto.randomUUID(),
      type,
      title,
      content,
      input.reference || "",
      1,
      cleanText(input.altText, 500),
      timestamp,
      id,
    ],
  );
  if (updateCard && ["complete", "approved"].includes(status)) {
    run(
      `UPDATE cards SET latest_output_id=?,latest_successful_output_version_id=?,
       updated_at=?,attention='ai_updated' WHERE id=?`,
      [id, versionId, timestamp, card.id],
    );
  }
  return id;
}

function approveOutput(input, context) {
  const outputId = requireId(input.outputId, "outputId");
  const output = rows(
    `SELECT id,card_id AS cardId,type,current_version AS currentVersion
       FROM outputs WHERE id=?`,
    [outputId],
  )[0];
  if (!output) throw typedError("OUTPUT_NOT_FOUND", "Output was not found.");
  const timestamp = now();
  const versionId = scalar(
    "SELECT id FROM output_versions WHERE output_id=? AND version=?",
    [output.id, output.currentVersion],
  );
  run("UPDATE outputs SET status='approved',updated_at=? WHERE id=?", [timestamp, output.id]);
  run("UPDATE output_versions SET status='approved' WHERE id=?", [versionId]);
  run(
    `UPDATE cards SET latest_output_id=?,latest_successful_output_version_id=?,
     attention='ai_updated',updated_at=? WHERE id=?`,
    [output.id, versionId, timestamp, output.cardId],
  );
  appendActivity(output.cardId, "output_approved", context.actorId, "Output approved.");
  return { cardId: output.cardId, outputId };
}

function versionOutput(input, context) {
  const outputId = requireId(input.outputId, "outputId");
  const output = rows(
    "SELECT id,card_id AS cardId,type,current_version AS currentVersion FROM outputs WHERE id=?",
    [outputId],
  )[0];
  if (!output) throw typedError("OUTPUT_NOT_FOUND", "Output was not found.");
  const version = Number(output.currentVersion) + 1;
  const timestamp = now();
  const versionId = crypto.randomUUID();
  const title = requireText(input.title, "title", 200);
  const content = ["program", "diff"].includes(output.type)
    ? exactText(input.content, 1_000_000)
    : cleanText(input.content, 1_000_000);
  const status = oneOf(input.status || "complete", OUTPUT_STATUSES, "status");
  run(
    `INSERT INTO output_versions(id,output_id,version,title,payload,status,source,created_at)
     VALUES(?,?,?,?,?,?,?,?)`,
    [versionId, output.id, version, title, content, status, input.source || context.actorId, timestamp],
  );
  run(
    `INSERT INTO output_surfaces(
      id,output_version_id,type,title,payload,reference,schema_version,alt_text,created_at
    ) VALUES(?,?,?,?,?,?,?,?,?)`,
    [
      crypto.randomUUID(),
      versionId,
      output.type,
      title,
      content,
      cleanText(input.reference, 2_000),
      1,
      cleanText(input.altText, 500),
      timestamp,
    ],
  );
  run(
    "UPDATE outputs SET title=?,status=?,updated_at=?,current_version=? WHERE id=?",
    [title, status, timestamp, version, output.id],
  );
  if (["complete", "approved"].includes(status)) {
    run(`UPDATE cards SET latest_output_id=?,latest_successful_output_version_id=?,
         attention='ai_updated',updated_at=? WHERE id=?`, [
      output.id,
      versionId,
      timestamp,
      output.cardId,
    ]);
  }
  appendActivity(output.cardId, "output_versioned", context.actorId, `Output updated to version ${version}.`);
  return { cardId: output.cardId, outputId: output.id, version };
}

function applyResponse(input, context) {
  const card = requireCard(input.cardId);
  const packet = input.packet;
  if (!packet || packet.cardId !== card.id) throw typedError("INVALID_PACKET", "Response packet targets another card.");
  const handoffId = crypto.randomUUID();
  run(
    `INSERT INTO handoff_packets(
      id,card_id,direction,format,payload,status,created_at,approved_at
    ) VALUES(?,?,?,?,?,?,?,?)`,
    [
      handoffId,
      card.id,
      "import",
      packet.schema,
      JSON.stringify(packet),
      "approved",
      now(),
      now(),
    ],
  );
  for (const item of packet.plan || []) addPlanItem({ cardId: card.id, ...item, state: item.state || item.status }, context);
  for (const output of packet.outputs || []) addOutput({ cardId: card.id, ...output, source: "handoff" }, context);
  for (const event of packet.activity || []) {
    appendActivity(
      card.id,
      cleanText(event.type || "ai", 100) || "ai",
      "AI handoff",
      requireText(event.summary, "activity summary", 5_000),
      {
        handoffId,
        packetSchema: packet.schema,
        provenance: "approved-response-packet",
      },
    );
  }
  appendActivity(card.id, "handoff_imported", context.actorId, packet.summary || "Approved response applied.", {
    handoffId,
    packetSchema: packet.schema,
  });
  return { cardId: card.id, handoffId };
}

function saveDecisionBriefing(input, context) {
  const card = requireCard(input.cardId);
  const briefing = {
    goals: cleanText(input.briefing?.goals, 5_000),
    suggestions: cleanText(input.briefing?.suggestions, 5_000),
    constraints: cleanText(input.briefing?.constraints, 5_000),
    preferences: cleanText(input.briefing?.preferences, 5_000),
    exclusions: cleanText(input.briefing?.exclusions, 5_000),
    bounds: cleanText(input.briefing?.bounds, 2_000),
    criteria: cleanText(input.briefing?.criteria, 5_000),
    unknowns: cleanText(input.briefing?.unknowns, 5_000),
  };
  let decision = decisionForCard(card.id);
  if (!decision) {
    const id = crypto.randomUUID();
    run(
      "INSERT INTO decision_threads(id,card_id,phase,briefing,created_at,updated_at) VALUES(?,?,?,?,?,?)",
      [id, card.id, "briefing", JSON.stringify(briefing), now(), now()],
    );
    decision = { id };
  } else {
    run("UPDATE decision_threads SET briefing=?,updated_at=? WHERE id=?", [
      JSON.stringify(briefing),
      now(),
      decision.id,
    ]);
  }
  appendActivity(card.id, "decision_briefing", context.actorId, "Decision briefing updated.");
  return { cardId: card.id, decisionId: decision.id };
}

function addDecisionOption(input, context) {
  const card = requireCard(input.cardId);
  const decision = requireDecision(card.id);
  const id = crypto.randomUUID();
  run(
    `INSERT INTO decision_options(
      id,decision_id,position,title,summary,evidence,fit,tradeoffs,uncertainty,
      practical_constraints,status,created_at,updated_at
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    [
      id,
      decision.id,
      nextPosition("decision_options", "decision_id", decision.id),
      requireText(input.title, "title", 200),
      cleanText(input.summary, 10_000),
      cleanText(input.evidence, 20_000),
      cleanText(input.fit, 5_000),
      cleanText(input.tradeoffs, 10_000),
      cleanText(input.uncertainty, 5_000),
      cleanText(input.practicalConstraints, 5_000),
      "active",
      now(),
      now(),
    ],
  );
  run("UPDATE decision_threads SET phase='exploring',updated_at=? WHERE id=?", [now(), decision.id]);
  appendActivity(card.id, "decision_option_added", context.actorId, `Option added: ${input.title}`);
  return { cardId: card.id, optionId: id };
}

function feedbackDecisionOption(input, context) {
  const card = requireCard(input.cardId);
  const decision = requireDecision(card.id);
  const option = rows(
    "SELECT id,title FROM decision_options WHERE id=? AND decision_id=?",
    [requireId(input.optionId, "optionId"), decision.id],
  )[0];
  if (!option) throw typedError("OPTION_NOT_FOUND", "Decision option was not found.");
  const action = oneOf(input.action, ["rank", "shortlist", "reject", "restore", "note"], "action");
  run(
    `INSERT INTO decision_feedback(
      id,decision_id,option_id,actor,action,value,note,created_at
    ) VALUES(?,?,?,?,?,?,?,?)`,
    [
      crypto.randomUUID(),
      decision.id,
      option.id,
      context.actorId,
      action,
      input.value == null ? "" : String(input.value),
      cleanText(input.note, 5_000),
      now(),
    ],
  );
  if (action === "reject") run("UPDATE decision_options SET status='rejected',updated_at=? WHERE id=?", [now(), option.id]);
  if (action === "restore") run("UPDATE decision_options SET status='active',updated_at=? WHERE id=?", [now(), option.id]);
  appendActivity(card.id, "decision_feedback", context.actorId, `${action} feedback recorded for ${option.title}.`);
  return { cardId: card.id, optionId: option.id };
}

function setDecisionGate(input, context) {
  const card = requireCard(input.cardId);
  const decision = requireDecision(card.id);
  const option = rows(
    "SELECT id,title FROM decision_options WHERE id=? AND decision_id=? AND status<>'rejected'",
    [requireId(input.optionId, "optionId"), decision.id],
  )[0];
  if (!option) throw typedError("OPTION_NOT_FOUND", "Selected option is unavailable.");
  const snapshot = {
    option: { id: option.id, title: option.title },
    constraints: cleanText(input.constraints, 10_000),
    unresolvedQuestions: cleanText(input.unresolvedQuestions, 10_000),
    confirmedAt: now(),
  };
  const gateId = crypto.randomUUID();
  run(
    `INSERT INTO decision_gates(
      id,decision_id,option_id,constraints_snapshot,evidence_snapshot,
      feedback_snapshot,unresolved_questions,confirmed_by,confirmed_at
    ) VALUES(?,?,?,?,?,?,?,?,?)`,
    [
      gateId,
      decision.id,
      option.id,
      snapshot.constraints,
      cleanText(input.evidence, 20_000),
      JSON.stringify(feedbackForDecision(decision.id)),
      snapshot.unresolvedQuestions,
      context.actorId,
      snapshot.confirmedAt,
    ],
  );
  run(
    "UPDATE decision_threads SET phase='committed',selected_option_id=?,gate_id=?,updated_at=? WHERE id=?",
    [option.id, gateId, now(), decision.id],
  );
  appendActivity(card.id, "decision_committed", context.actorId, `Deep-work gate confirmed: ${option.title}.`);
  return { cardId: card.id, optionId: option.id, gateId };
}

function setDecisionPhase(input, context) {
  const card = requireCard(input.cardId);
  const decision = requireDecision(card.id);
  const phase = oneOf(input.phase, DECISION_PHASES, "phase");
  if (phase === "deep_work" && !decision.selectedOptionId) {
    throw typedError("DECISION_GATE_REQUIRED", "Select an option before deep work.");
  }

  const timestamp = now();
  if (phase === "accepted") {
    if (decision.phase !== "review" || !card.currentTurnId) {
      throw typedError(
        "REVIEW_TURN_REQUIRED",
        "Accepting a decision requires its active review turn.",
      );
    }
    const reviewTurn = requireTurn(card.currentTurnId);
    if (reviewTurn.status !== "review") {
      throw typedError(
        "REVIEW_TURN_REQUIRED",
        "The current decision turn is not ready for acceptance.",
      );
    }
    run(
      "UPDATE execution_turns SET status='complete',completed_at=? WHERE id=?",
      [timestamp, reviewTurn.id],
    );
    appendActivity(
      card.id,
      "turn_complete",
      context.actorId,
      `Turn ${reviewTurn.displayNumber} completed by decision acceptance.`,
      { turnId: reviewTurn.id },
    );
  }
  run("UPDATE decision_threads SET phase=?,updated_at=? WHERE id=?", [phase, timestamp, decision.id]);
  if (phase === "accepted") {
    run(
      `UPDATE cards SET column_id='done',position=?,attention='none',
       current_turn_id=NULL,updated_at=?,last_change_actor=? WHERE id=?`,
      [nextPosition("cards", "column_id", "done"), timestamp, context.actorId, card.id],
    );
  }
  appendActivity(card.id, "decision_phase", context.actorId, `Decision moved to ${phase.replace("_", " ")}.`);
  return { cardId: card.id, phase };
}

function requestDecisionRevision(input, context) {
  const card = requireCard(input.cardId);
  const decision = requireDecision(card.id);
  if (decision.phase !== "review" || !card.currentTurnId) {
    throw typedError(
      "REVIEW_TURN_REQUIRED",
      "A revision requires the active decision review turn.",
    );
  }
  const reviewTurn = requireTurn(card.currentTurnId);
  if (reviewTurn.status !== "review") {
    throw typedError(
      "REVIEW_TURN_REQUIRED",
      "The current decision turn is not in review.",
    );
  }
  const timestamp = now();
  run(
    "UPDATE execution_turns SET status='complete',completed_at=? WHERE id=?",
    [timestamp, reviewTurn.id],
  );
  run(
    "UPDATE decision_threads SET phase='deep_work',updated_at=? WHERE id=?",
    [timestamp, decision.id],
  );
  run(
    `UPDATE cards SET current_turn_id=NULL,column_id='in_progress',
     position=?,updated_at=?,last_change_actor=? WHERE id=?`,
    [
      nextPosition("cards", "column_id", "in_progress"),
      timestamp,
      context.actorId,
      card.id,
    ],
  );
  appendActivity(
    card.id,
    "decision_revision_requested",
    context.actorId,
    `Revision requested after turn ${reviewTurn.displayNumber}.`,
    { turnId: reviewTurn.id },
  );
  const successor = queueTurn(
    {
      cardId: card.id,
      instruction: requireText(input.instruction, "instruction", 50_000),
      trigger: "review_revision",
      requester: context.actorId,
      linkedTurnId: reviewTurn.id,
      idempotencyKey: input.idempotencyKey || crypto.randomUUID(),
    },
    context,
  );
  return {
    ...successor,
    completedTurnId: reviewTurn.id,
  };
}

function memoryAction(input, context) {
  const card = requireCard(input.cardId);
  const id = requireId(input.memoryId, "memoryId");
  const action = oneOf(input.action, ["pin", "dismiss", "correct", "forget"], "action");
  const memory = rows("SELECT id,summary FROM research_memory WHERE id=? AND card_id=?", [id, card.id])[0];
  if (!memory) throw typedError("MEMORY_NOT_FOUND", "Research memory was not found.");
  if (action === "pin") run("UPDATE research_memory SET pinned=1,last_seen=? WHERE id=?", [now(), id]);
  if (action === "dismiss") run("UPDATE research_memory SET state='dismissed',last_seen=? WHERE id=?", [now(), id]);
  if (action === "forget") {
    run(
      `UPDATE research_memory SET
         cycle_id=NULL,
         subject='',
         fingerprint='',
         summary='',
         source='',
         publisher='',
         evidence_date='',
         last_seen=?,
         content_hash='',
         relevance='',
         state='forgotten',
         coverage='',
         gaps='',
         lineage='[]',
         pinned=0
       WHERE id=?`,
      [now(), id],
    );
  }
  if (action === "correct") {
    run("UPDATE research_memory SET state='corrected',summary=?,last_seen=? WHERE id=?", [
      requireText(input.summary, "summary", 10_000),
      now(),
      id,
    ]);
  }
  const actionLabel = action === "forget" ? "forgotten" : `${action}ed`;
  appendActivity(card.id, "memory_changed", context.actorId, `Research memory ${actionLabel}.`, { memoryId: id });
  return { cardId: card.id, memoryId: id };
}

function recordResearchMemory(input, context) {
  const card = requireCard(input.cardId);
  if (!card.recurring) {
    throw typedError("NOT_RECURRING", "Research memory belongs to a recurring topic monitor card.");
  }
  const fingerprint = requireText(input.fingerprint, "fingerprint", 500);
  const contentHash = requireText(input.contentHash, "contentHash", 500);
  const existing = rows(
    `SELECT id,content_hash AS contentHash,state,summary,pinned FROM research_memory
      WHERE card_id=? AND fingerprint=? ORDER BY last_seen DESC LIMIT 1`,
    [card.id, fingerprint],
  )[0];
  const classification = input.classification
    ? oneOf(input.classification, OBSERVATION_STATES, "classification")
    : !existing
      ? "new"
      : existing.contentHash === contentHash
        ? "unchanged_context"
        : "materially_updated";
  const timestamp = now();
  if (existing) {
    const userCurated = ["corrected", "dismissed"].includes(existing.state);
    run(
      `UPDATE research_memory SET summary=?,source=?,publisher=?,evidence_date=?,
       last_seen=?,content_hash=?,relevance=?,state=?,observation_state=?,
       coverage=?,gaps=?,lineage=?
       WHERE id=?`,
      [
        userCurated ? existing.summary : cleanText(input.summary, 20_000),
        cleanText(input.source, 2_000),
        cleanText(input.publisher, 500),
        cleanText(input.evidenceDate, 100),
        timestamp,
        contentHash,
        cleanText(input.relevance, 100),
        userCurated ? existing.state : classification,
        classification,
        cleanText(input.coverage, 5_000),
        cleanText(input.gaps, 5_000),
        JSON.stringify(input.lineage || []),
        existing.id,
      ],
    );
    appendActivity(card.id, "memory_classified", context.actorId, `Research memory classified ${classification}.`);
    return { cardId: card.id, memoryId: existing.id, classification };
  }
  const id = crypto.randomUUID();
  run(
    `INSERT INTO research_memory(
      id,card_id,cycle_id,subject,fingerprint,summary,source,publisher,evidence_date,
      first_seen,last_seen,content_hash,relevance,state,observation_state,
      coverage,gaps,lineage,pinned
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)`,
    [
      id,
      card.id,
      input.cycleId || null,
      requireText(input.subject, "subject", 500),
      fingerprint,
      cleanText(input.summary, 20_000),
      cleanText(input.source, 2_000),
      cleanText(input.publisher, 500),
      cleanText(input.evidenceDate, 100),
      timestamp,
      timestamp,
      contentHash,
      cleanText(input.relevance, 100),
      classification,
      classification,
      cleanText(input.coverage, 5_000),
      cleanText(input.gaps, 5_000),
      JSON.stringify(input.lineage || []),
    ],
  );
  appendActivity(card.id, "memory_classified", context.actorId, `New research memory retained.`);
  return { cardId: card.id, memoryId: id, classification };
}

function setControl(input, context) {
  const state = oneOf(
    input.state,
    ["human", "granting_agent", "agent", "reclaim_requested", "recovering"],
    "state",
  );
  const generation = Number(meta("control_generation")) + (input.incrementGeneration ? 1 : 0);
  const holder = requireId(input.holderId || (state === "human" ? "human" : context.holderId), "holderId");
  setMeta("control_state", state);
  setMeta("control_holder", holder);
  setMeta("control_owner", input.ownerId || "human");
  setMeta("control_generation", String(generation));
  setMeta("control_lease_until", cleanText(input.leaseUntil, 100));
  appendActivity(null, "control_changed", context.actorId, `Control state changed to ${state}.`, {
    holder,
    generation,
  });
  return { state, holder, generation };
}

function getSnapshot() {
  requireDatabase();
  const columns = rows("SELECT id,title,position,color FROM columns ORDER BY position");
  const cards = rows(
    `SELECT
      c.id,c.column_id AS columnId,c.position,c.title,c.description,c.priority,
      c.assignee,c.kind,c.attention,c.recurring,c.cadence,c.lookback_window AS lookbackWindow,
      c.current_turn_id AS currentTurnId,c.latest_output_id AS latestOutputId,
      c.latest_successful_output_version_id AS latestSuccessfulOutputVersionId,
      c.created_at AS createdAt,c.updated_at AS updatedAt,c.provenance,
      c.last_change_actor AS lastChangeActor,
      (SELECT COUNT(*) FROM plan_items p WHERE p.card_id=c.id) AS planCount,
      (SELECT COUNT(*) FROM plan_items p WHERE p.card_id=c.id AND p.state='done') AS planDone,
      (SELECT COUNT(*) FROM outputs o WHERE o.card_id=c.id) AS outputCount,
      (SELECT COUNT(*) FROM dependencies d WHERE d.card_id=c.id) AS dependencyCount,
      (SELECT t.status FROM execution_turns t WHERE t.id=c.current_turn_id) AS turnStatus,
      (SELECT v.payload FROM output_versions v
        WHERE v.id=c.latest_successful_output_version_id) AS latestOutputPreview,
      (SELECT d.phase FROM decision_threads d WHERE d.card_id=c.id) AS decisionPhase
     FROM cards c
     WHERE c.archived=0
     ORDER BY c.column_id,c.position,c.created_at`,
  ).map((card) => ({
    ...card,
    recurring: Boolean(card.recurring),
    provenance: parseJson(card.provenance, {}),
  }));
  const metadata = Object.fromEntries(rows("SELECT key,value FROM metadata").map(
    (item) => [item.key, item.value],
  ));
  return {
    meta: metadata,
    columns,
    cards,
    counts: {
      needsYou: Number(scalar("SELECT COUNT(*) FROM cards WHERE archived=0 AND attention='needs_you'")),
      aiWorking: Number(scalar("SELECT COUNT(*) FROM cards WHERE archived=0 AND attention='ai_working'")),
      aiUpdated: Number(scalar("SELECT COUNT(*) FROM cards WHERE archived=0 AND attention='ai_updated'")),
      archived: Number(scalar("SELECT COUNT(*) FROM cards WHERE archived=1")),
    },
  };
}

function getCard(cardId) {
  const card = requireCard(cardId);
  const decision = decisionForCard(card.id);
  const outputs = rows(
    `SELECT o.id,o.turn_id AS turnId,o.type,o.title,o.owner,o.status,o.source,o.lineage,
            o.created_at AS createdAt,o.updated_at AS updatedAt,o.current_version AS currentVersion,
            v.payload AS content,s.reference,s.alt_text AS altText
       FROM outputs o
       JOIN output_versions v ON v.output_id=o.id AND v.version=o.current_version
       JOIN output_surfaces s ON s.output_version_id=v.id
      WHERE o.card_id=? ORDER BY o.position DESC,o.created_at DESC`,
    [card.id],
  ).map((output) => ({ ...output, lineage: parseJson(output.lineage, []) }));
  return {
    ...card,
    recurring: Boolean(card.recurring),
    provenance: parseJson(card.provenance, {}),
    columnTitle: columnTitle(card.columnId),
    plan: rows(
      `SELECT id,text,state,position,created_at AS createdAt,updated_at AS updatedAt
         FROM plan_items WHERE card_id=? ORDER BY position`,
      [card.id],
    ),
    dependencies: rows(
      `SELECT c.id,c.title,c.column_id AS columnId
         FROM dependencies d JOIN cards c ON c.id=d.depends_on_id
        WHERE d.card_id=? ORDER BY c.title`,
      [card.id],
    ),
    turns: rows(
      `SELECT id,display_number AS displayNumber,status,trigger,requester,actor,
              agent_run_id AS agentRunId,instruction_snapshot AS instructionSnapshot,
              linked_turn_id AS linkedTurnId,queued_at AS queuedAt,claimed_at AS claimedAt,
              started_at AS startedAt,input_requested_at AS inputRequestedAt,
              reviewed_at AS reviewedAt,completed_at AS completedAt,failed_at AS failedAt,
              cancelled_at AS cancelledAt,result,error,cancellation_reason AS cancellationReason
         FROM execution_turns WHERE card_id=? ORDER BY display_number DESC`,
      [card.id],
    ).map((turn) => ({
      ...turn,
      checkpoints: rows(
        "SELECT id,kind,summary,progress,created_at AS createdAt FROM turn_checkpoints WHERE turn_id=? ORDER BY created_at",
        [turn.id],
      ),
      questions: rows(
        `SELECT q.id,q.question,q.context,q.status,q.created_at AS createdAt,
                a.answer,a.created_at AS answeredAt
           FROM agent_questions q LEFT JOIN agent_answers a ON a.question_id=q.id
          WHERE q.turn_id=? ORDER BY q.created_at`,
        [turn.id],
      ),
    })),
    outputs,
    outputVersions: Object.fromEntries(outputs.map((output) => [
      output.id,
      rows(
        `SELECT id,version,title,payload AS content,status,source,created_at AS createdAt
           FROM output_versions WHERE output_id=? ORDER BY version DESC`,
        [output.id],
      ),
    ])),
    decision,
    memory: rows(
      `SELECT id,cycle_id AS cycleId,subject,fingerprint,summary,source,publisher,
              evidence_date AS evidenceDate,first_seen AS firstSeen,last_seen AS lastSeen,
              content_hash AS contentHash,relevance,state,
              observation_state AS observationState,coverage,gaps,lineage,pinned
         FROM research_memory WHERE card_id=? ORDER BY pinned DESC,last_seen DESC`,
      [card.id],
    ).map((memory) => ({
      ...memory,
      pinned: Boolean(memory.pinned),
      lineage: parseJson(memory.lineage, []),
    })),
    cycles: rows(
      `SELECT id,cycle_number AS cycleNumber,topic,cadence,lookback_window AS lookbackWindow,
              coverage,gaps,new_findings AS newFindings,retained_context AS retainedContext,
              started_at AS startedAt,completed_at AS completedAt
         FROM research_cycles WHERE card_id=? ORDER BY cycle_number DESC`,
      [card.id],
    ),
    activity: rows(
      `SELECT id,type,actor,summary,payload,created_at AS createdAt
         FROM activity_events WHERE card_id=? ORDER BY created_at DESC,rowid DESC LIMIT 200`,
      [card.id],
    ).map(parsePayload),
    handoffs: rows(
      `SELECT id,direction,format,status,created_at AS createdAt,approved_at AS approvedAt
         FROM handoff_packets WHERE card_id=? ORDER BY created_at DESC`,
      [card.id],
    ),
  };
}

function searchCards(filters) {
  const clauses = ["c.archived=?"];
  const parameters = [filters.archived ? 1 : 0];
  if (filters.query) {
    clauses.push("(LOWER(c.title) LIKE ? OR LOWER(c.description) LIKE ?)");
    const query = `%${String(filters.query).toLowerCase()}%`;
    parameters.push(query, query);
  }
  for (const [key, column] of [
    ["priority", "c.priority"],
    ["assignee", "c.assignee"],
    ["columnId", "c.column_id"],
    ["kind", "c.kind"],
    ["attention", "c.attention"],
  ]) {
    if (filters[key]) {
      clauses.push(`${column}=?`);
      parameters.push(filters[key]);
    }
  }
  if (filters.turnStatus) {
    clauses.push("EXISTS (SELECT 1 FROM execution_turns t WHERE t.id=c.current_turn_id AND t.status=?)");
    parameters.push(filters.turnStatus);
  }
  if (filters.origin) {
    clauses.push("c.provenance LIKE ?");
    parameters.push(`%${filters.origin}%`);
  }
  if (filters.blocked) clauses.push("c.column_id='blocked'");
  return rows(
    `SELECT c.id,c.title,c.column_id AS columnId,c.priority,c.assignee,c.kind,c.attention
       FROM cards c WHERE ${clauses.join(" AND ")} ORDER BY c.updated_at DESC LIMIT 500`,
    parameters,
  );
}

function decisionForCard(cardId) {
  const decision = rows(
    `SELECT id,phase,briefing,selected_option_id AS selectedOptionId,gate_id AS gateId,
            created_at AS createdAt,updated_at AS updatedAt
       FROM decision_threads WHERE card_id=?`,
    [cardId],
  )[0];
  if (!decision) return null;
  decision.briefing = parseJson(decision.briefing, {});
  decision.options = rows(
    `SELECT id,position,title,summary,evidence,fit,tradeoffs,uncertainty,
            practical_constraints AS practicalConstraints,status,
            created_at AS createdAt,updated_at AS updatedAt
       FROM decision_options WHERE decision_id=? ORDER BY position`,
    [decision.id],
  );
  decision.feedback = feedbackForDecision(decision.id);
  decision.gates = rows(
    `SELECT id,option_id AS optionId,constraints_snapshot AS constraintsSnapshot,
            evidence_snapshot AS evidenceSnapshot,feedback_snapshot AS feedbackSnapshot,
            unresolved_questions AS unresolvedQuestions,confirmed_by AS confirmedBy,
            confirmed_at AS confirmedAt
       FROM decision_gates WHERE decision_id=? ORDER BY confirmed_at DESC`,
    [decision.id],
  ).map((gate) => ({ ...gate, feedbackSnapshot: parseJson(gate.feedbackSnapshot, []) }));
  const selected = decision.options.find((option) => option.id === decision.selectedOptionId);
  decision.selectedOptionTitle = selected?.title || null;
  return decision;
}

function feedbackForDecision(decisionId) {
  return rows(
    `SELECT id,option_id AS optionId,actor,action,value,note,created_at AS createdAt
       FROM decision_feedback WHERE decision_id=? ORDER BY created_at`,
    [decisionId],
  );
}

function requireDecision(cardId) {
  const decision = decisionForCard(cardId);
  if (!decision) throw typedError("DECISION_NOT_FOUND", "This card has no decision thread.");
  return decision;
}

function seedDemo() {
  const cards = [
    {
      id: "demo-macro-pulse",
      column: "planning",
      position: 1024,
      title: "Macroeconomic pulse",
      description: "A monthly evidence-led scan of inflation, rates, employment, and material changes for family planning.",
      priority: "P1",
      assignee: "Research agent",
      kind: "result",
      attention: "ai_updated",
      recurring: 1,
      cadence: "Monthly · first Monday",
      lookback: "35 days",
    },
    {
      id: "demo-sao-paulo",
      column: "inbox",
      position: 1024,
      title: "Things to do with a four-year-old in São Paulo",
      description: "Find age-appropriate activities for this weekend, balancing weather, travel time, cost, and nap windows.",
      priority: "P1",
      assignee: "You + Research agent",
      kind: "question",
      attention: "needs_you",
      recurring: 1,
      cadence: "Weekly · Thursday",
      lookback: "14 days",
    },
    {
      id: "demo-family-trips",
      column: "planning",
      position: 2048,
      title: "Family trip ideas for the school break",
      description: "Explore calm, child-friendly trips from São Paulo with direct travel and a mix of nature and comfort.",
      priority: "P2",
      assignee: "Research agent",
      kind: "task",
      attention: "ai_working",
      recurring: 0,
      cadence: "",
      lookback: "",
    },
    {
      id: "demo-vacation",
      column: "planning",
      position: 3072,
      title: "Choose our July family vacation",
      description: "Compare credible destinations broadly, incorporate family feedback, then research only the selected option and produce a dated itinerary.",
      priority: "P0",
      assignee: "Family + Planning agent",
      kind: "question",
      attention: "needs_you",
      recurring: 0,
      cadence: "",
      lookback: "",
    },
    {
      id: "demo-age-activities",
      column: "review",
      position: 1024,
      title: "Age-appropriate rainy-day activities",
      description: "A durable collection of low-prep indoor activities with developmental fit and material lists.",
      priority: "P2",
      assignee: "Research agent",
      kind: "result",
      attention: "ai_updated",
      recurring: 1,
      cadence: "Every 6 weeks",
      lookback: "90 days",
    },
  ];
  const timestamp = now();
  for (const card of cards) {
    run(
      `INSERT INTO cards(
        id,column_id,position,title,description,priority,assignee,kind,attention,
        recurring,cadence,lookback_window,created_at,updated_at,provenance,last_change_actor
      ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
      [
        card.id,
        card.column,
        card.position,
        card.title,
        card.description,
        card.priority,
        card.assignee,
        card.kind,
        card.attention,
        card.recurring,
        card.cadence,
        card.lookback,
        timestamp,
        timestamp,
        '{"origin":"bundled-demo","actor":"AI Kanban"}',
        "AI Kanban",
      ],
    );
    appendActivity(card.id, "demo_seeded", "AI Kanban", "Personal Research demo card added.");
  }
  seedVacation(timestamp);
  seedResearch(timestamp);
  seedOutputs(timestamp);
  queueTurn(
    {
      cardId: "demo-family-trips",
      instruction: "Compare family-friendly school-break destinations using current evidence.",
      trigger: "demo",
      idempotencyKey: "demo-family-trips-turn",
    },
    { actorId: "human" },
  );
  setMeta("revision", "0");
}

function seedVacation(timestamp) {
  const decisionId = "decision-vacation";
  run(
    "INSERT INTO decision_threads(id,card_id,phase,briefing,created_at,updated_at) VALUES(?,?,?,?,?,?)",
    [
      decisionId,
      "demo-vacation",
      "needs_feedback",
      JSON.stringify({
        goals: "A restorative 8–10 day family trip in July.",
        suggestions: "Beach, mountains, or a compact international city.",
        constraints: "One four-year-old; no more than one connection; easy medical access.",
        preferences: "Nature, excellent food, unhurried days, one memorable train or boat ride.",
        exclusions: "Very cold weather, packed attraction schedules, overnight transfers.",
        bounds: "Mid-range to comfortable; up to 10 days.",
        criteria: "Travel friction, weather, child fit, accommodation quality, and cost.",
        unknowns: "Tolerance for a long-haul flight and whether grandparents will join.",
      }),
      timestamp,
      timestamp,
    ],
  );
  const options = [
    [
      "option-florianopolis",
      1024,
      "Florianópolis",
      "Low-friction coastal week with flexible beach and nature days.",
      "Direct flights and family-oriented stays are widely available; July weather can be variable.",
      "Strong on travel ease and spacious stays.",
      "Cooler beach weather; less novelty.",
      "Weather-dependent outdoor value.",
      "Renting a car improves flexibility.",
      "active",
    ],
    [
      "option-buenos-aires",
      2048,
      "Buenos Aires",
      "Compact city break combining parks, food, museums, and short daily journeys.",
      "Frequent direct flights; broad indoor options; winter temperatures require planning.",
      "Strong food and culture fit with manageable travel.",
      "Urban pace and cool weather.",
      "School-holiday demand may affect prices.",
      "Choose a walkable neighborhood near parks.",
      "active",
    ],
    [
      "option-patagonia",
      3072,
      "Northern Patagonia",
      "Beautiful winter scenery and cozy stays centered on Bariloche.",
      "Reliable winter infrastructure but snow logistics and colder days add friction.",
      "High nature and memorable-experience fit.",
      "More gear, transfers, and weather exposure.",
      "Snow disruption and child cold tolerance.",
      "Limit hotel changes and reserve transfers.",
      "active",
    ],
  ];
  for (const option of options) {
    run(
      `INSERT INTO decision_options(
        id,decision_id,position,title,summary,evidence,fit,tradeoffs,uncertainty,
        practical_constraints,status,created_at,updated_at
      ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)`,
      [option[0], decisionId, ...option.slice(1), timestamp, timestamp],
    );
  }
  run(
    `INSERT INTO decision_feedback(
      id,decision_id,option_id,actor,action,value,note,created_at
    ) VALUES(?,?,?,?,?,?,?,?)`,
    [
      "feedback-vacation-1",
      decisionId,
      "option-buenos-aires",
      "You",
      "shortlist",
      "",
      "Keep this option; the parks and food mix feels right.",
      timestamp,
    ],
  );
}

function seedResearch(timestamp) {
  run(
    `INSERT INTO research_cycles(
      id,card_id,cycle_number,topic,cadence,lookback_window,coverage,gaps,
      new_findings,retained_context,started_at,completed_at
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)`,
    [
      "cycle-macro-1",
      "demo-macro-pulse",
      1,
      "Brazil macroeconomic family-planning pulse",
      "monthly",
      "35 days",
      "Central bank, statistics agency, major bank research",
      "Household credit conditions need another primary source",
      "Rate expectations shifted while current inflation remained mixed.",
      "Employment is resilient; food inflation remains important to household budgets.",
      timestamp,
      timestamp,
    ],
  );
  const memories = [
    ["memory-macro-rate", "Interest-rate outlook", "rate-outlook-july", "Survey expectations moved, but no policy decision has occurred.", "https://www.bcb.gov.br/", "Banco Central do Brasil", "2026-07-24", "materially_updated", 1],
    ["memory-macro-inflation", "Household inflation", "household-inflation-july", "Food and services remain the categories most relevant to the family budget watch.", "https://www.ibge.gov.br/", "IBGE", "2026-07-15", "unchanged_context", 0],
    ["memory-activities", "Indoor movement games", "rainy-day-movement", "Short obstacle courses support gross-motor play with household materials.", "https://www.unicef.org/parenting/", "UNICEF", "2026-06-10", "new", 1],
  ];
  for (const memory of memories) {
    const cardId = memory[0] === "memory-activities" ? "demo-age-activities" : "demo-macro-pulse";
    run(
      `INSERT INTO research_memory(
        id,card_id,cycle_id,subject,fingerprint,summary,source,publisher,evidence_date,
        first_seen,last_seen,content_hash,relevance,state,coverage,gaps,lineage,pinned
      ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
      [
        memory[0],
        cardId,
        cardId === "demo-macro-pulse" ? "cycle-macro-1" : null,
        memory[1],
        memory[2],
        memory[3],
        memory[4],
        memory[5],
        memory[6],
        timestamp,
        timestamp,
        memory[2],
        "high",
        memory[7],
        "Primary and expert source",
        "",
        "[]",
        memory[8],
      ],
    );
  }
}

function seedOutputs(timestamp) {
  insertOutput({
    id: "output-macro-report",
    cardId: "demo-macro-pulse",
    type: "text",
    title: "July macro pulse",
    content: "## What changed\nRate expectations moved while the latest confirmed policy stance is unchanged.\n\n## Household relevance\nFood and service prices remain the most useful budget watchpoints.\n\n**Confidence:** Moderate. Primary releases are current to July 24.",
    status: "complete",
    owner: "Research agent",
    source: "demo-cycle",
    createdAt: timestamp,
    updatedAt: timestamp,
  });
  insertOutput({
    id: "output-activity-table",
    cardId: "demo-age-activities",
    type: "table",
    title: "Rainy-day activity shortlist",
    content: JSON.stringify([
      { activity: "Tape-line balance trail", age: "4+", setup: "5 min", mess: "Low" },
      { activity: "Cushion obstacle course", age: "3+", setup: "8 min", mess: "Low" },
      { activity: "Color sorting relay", age: "4+", setup: "10 min", mess: "Medium" },
    ]),
    status: "approved",
    owner: "Research agent",
    source: "demo-cycle",
    createdAt: timestamp,
    updatedAt: timestamp,
  });
}

function verifyControl(context, operation) {
  const expectedRevision = Number(context.expectedRevision);
  const currentRevision = Number(meta("revision"));
  if (expectedRevision !== currentRevision) {
    throw typedError("REVISION_MISMATCH", "Workspace revision changed; reload before writing.", {
      expected: expectedRevision,
      actual: currentRevision,
    });
  }
  const generation = Number(meta("control_generation"));
  if (Number(context.generation) !== generation) {
    throw typedError("STALE_GENERATION", "Control generation is stale.", {
      expected: generation,
      actual: Number(context.generation),
    });
  }
  const holder = meta("control_holder");
  if (context.holderId !== holder) {
    throw typedError("CONTROL_NOT_HELD", `Writes belong to ${holder}, not ${context.holderId}.`);
  }
  const state = meta("control_state");
  if (
    context.actorId === "human" &&
    state !== "human" &&
    !["setControl"].includes(operation)
  ) {
    throw typedError("AGENT_HAS_CONTROL", "The agent holds the writer baton. Reclaim control before editing.");
  }
}

function validateContext(context) {
  if (!context || typeof context !== "object") throw typedError("INVALID_CONTEXT", "Mutation context is required.");
  requireId(context.actorId, "actorId");
  requireId(context.holderId, "holderId");
  if (!Number.isSafeInteger(Number(context.generation)) || Number(context.generation) < 0) {
    throw typedError("INVALID_CONTEXT", "Control generation is invalid.");
  }
  if (!Number.isSafeInteger(Number(context.expectedRevision)) || Number(context.expectedRevision) < 0) {
    throw typedError("INVALID_CONTEXT", "Expected revision is invalid.");
  }
}

function incrementRevision() {
  setMeta("revision", String(Number(meta("revision")) + 1));
  setMeta("updated_at", now());
}

function registerIdempotency(key, scope, resultId, actor, requestFingerprint) {
  try {
    run(
      `INSERT INTO idempotency_keys(
         key,scope,result_id,actor,request_fingerprint,created_at
       ) VALUES(?,?,?,?,?,?)`,
      [key, scope, resultId, actor, requestFingerprint, now()],
    );
  } catch {
    const existing = rows(
      `SELECT result_id AS resultId,actor,request_fingerprint AS requestFingerprint
         FROM idempotency_keys WHERE key=? AND scope=?`,
      [key, scope],
    )[0];
    if (
      existing?.resultId !== resultId ||
      existing?.actor !== actor ||
      existing?.requestFingerprint !== requestFingerprint
    ) {
      throw typedError("IDEMPOTENCY_CONFLICT", "Idempotency key was already used.");
    }
  }
}

function appendActivity(cardId, type, actor, summary, payload = {}) {
  run(
    `INSERT INTO activity_events(id,card_id,type,actor,summary,payload,created_at)
     VALUES(?,?,?,?,?,?,?)`,
    [crypto.randomUUID(), cardId, type, actor, summary, JSON.stringify(payload), now()],
  );
}

function activeTurn(cardId) {
  return rows(
    `SELECT id,status FROM execution_turns WHERE card_id=? AND status IN (${ACTIVE_TURNS.map(() => "?").join(",")}) LIMIT 1`,
    [cardId, ...ACTIVE_TURNS],
  )[0] || null;
}

function latestSuccessfulTurn(cardId) {
  return rows(
    "SELECT id FROM execution_turns WHERE card_id=? AND status='complete' ORDER BY display_number DESC LIMIT 1",
    [cardId],
  )[0] || null;
}

function requireTurn(turnId) {
  const turn = rows(
    "SELECT id,card_id AS cardId,display_number AS displayNumber,status FROM execution_turns WHERE id=?",
    [requireId(turnId, "turnId")],
  )[0];
  if (!turn) throw typedError("TURN_NOT_FOUND", "Execution turn was not found.");
  return turn;
}

function requireCard(cardId) {
  const card = rows(
    `SELECT id,column_id AS columnId,position,title,description,priority,assignee,
            kind,attention,recurring,cadence,lookback_window AS lookbackWindow,
            current_turn_id AS currentTurnId,latest_output_id AS latestOutputId,
            latest_successful_output_version_id AS latestSuccessfulOutputVersionId,
            created_at AS createdAt,updated_at AS updatedAt,provenance,
            last_change_actor AS lastChangeActor
       FROM cards WHERE id=?`,
    [requireId(cardId, "cardId")],
  )[0];
  if (!card) throw typedError("CARD_NOT_FOUND", "The selected card no longer exists.");
  return card;
}

function requireColumn(columnId) {
  const id = requireId(columnId, "columnId");
  if (!scalar("SELECT id FROM columns WHERE id=?", [id])) {
    throw typedError("COLUMN_NOT_FOUND", "The selected column no longer exists.");
  }
  return id;
}

function hasIncompleteDependencies(cardId) {
  return Boolean(
    scalar(
      `SELECT 1 FROM dependencies d JOIN cards c ON c.id=d.depends_on_id
        WHERE d.card_id=? AND c.column_id<>'done' LIMIT 1`,
      [cardId],
    ),
  );
}

function normalizePositions(columnId) {
  const cards = rows(
    "SELECT id FROM cards WHERE column_id=? AND archived=0 ORDER BY position,created_at",
    [columnId],
  );
  const statement = db.prepare("UPDATE cards SET position=? WHERE id=?");
  cards.forEach((card, index) => statement.run([(index + 1) * 1024, card.id]));
  statement.free();
}

function nextPosition(table, field, value) {
  const allowed = {
    cards: "column_id",
    plan_items: "card_id",
    outputs: "card_id",
    decision_options: "decision_id",
  };
  if (allowed[table] !== field) throw typedError("INTERNAL_ERROR", "Invalid ordering target.");
  return Number(scalar(`SELECT COALESCE(MAX(position),0)+1024 FROM ${table} WHERE ${field}=?`, [value]));
}

function columnTitle(columnId) {
  return scalar("SELECT title FROM columns WHERE id=?", [columnId]) || columnId;
}

function meta(key) {
  return scalar("SELECT value FROM metadata WHERE key=?", [key]);
}

function setMeta(key, value) {
  run(
    "INSERT INTO metadata(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
    [key, String(value)],
  );
}

function tableExists(table) {
  return Boolean(scalar("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table]));
}

function columnExists(table, column) {
  return rows(`PRAGMA table_info(${table})`).some((item) => item.name === column);
}

function rows(sql, parameters = []) {
  const statement = db.prepare(sql);
  try {
    statement.bind(parameters);
    const result = [];
    while (statement.step()) result.push(statement.getAsObject());
    return result;
  } finally {
    statement.free();
  }
}

function scalar(sql, parameters = []) {
  const result = rows(sql, parameters);
  return result.length ? Object.values(result[0])[0] : null;
}

function run(sql, parameters = []) {
  db.run(sql, parameters);
}

function requireDatabase() {
  if (!db) throw typedError("NO_WORKSPACE", "Open or create a workspace first.");
}

function validatePacket(data) {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    throw typedError("INVALID_PACKET", "Worker message must be an object.");
  }
  if (!Number.isSafeInteger(data.id) || data.id < 1) {
    throw typedError("INVALID_PACKET", "Worker message id is invalid.");
  }
  if (typeof data.type !== "string" || !data.type) {
    throw typedError("INVALID_PACKET", "Worker message type is required.");
  }
  if (data.payload != null && (typeof data.payload !== "object" || Array.isArray(data.payload))) {
    throw typedError("INVALID_PACKET", "Worker message payload must be an object.");
  }
}

function requireId(value, label) {
  if (typeof value !== "string" || !/^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$/.test(value)) {
    throw typedError("VALIDATION_ERROR", `${label} is invalid.`);
  }
  return value;
}

function requireText(value, label, maximum) {
  const result = cleanText(value, maximum);
  if (!result) throw typedError("VALIDATION_ERROR", `${label} is required.`);
  return result;
}

function cleanText(value, maximum = 100_000) {
  if (value == null) return "";
  if (typeof value !== "string") throw typedError("VALIDATION_ERROR", "Expected text input.");
  const result = value.trim();
  if (result.length > maximum) throw typedError("VALIDATION_ERROR", "Text input is too long.");
  return result;
}

function exactText(value, maximum = 100_000) {
  if (value == null) return "";
  if (typeof value !== "string") throw typedError("VALIDATION_ERROR", "Expected text input.");
  if (value.length > maximum) throw typedError("VALIDATION_ERROR", "Text input is too long.");
  return value;
}

function stableMigrationTimestamp(legacy) {
  const candidates = [
    ...legacy.cards.flatMap((item) => [item.created_at, item.updated_at]),
    ...legacy.plan.flatMap((item) => [item.created_at, item.updated_at]),
    ...legacy.outputs.flatMap((item) => [item.created_at, item.updated_at]),
    ...legacy.activity.map((item) => item.created_at),
    ...legacy.handoffs.map((item) => item.created_at),
  ].filter((value) => typeof value === "string" && value);
  return candidates.sort()[0] || "1970-01-01T00:00:00.000Z";
}

function stableDerivedId(prefix, ...parts) {
  const source = `${prefix}\0${parts.join("\0")}`;
  let first = 0x811c9dc5;
  let second = 0x9e3779b9;
  for (let index = 0; index < source.length; index += 1) {
    const code = source.charCodeAt(index);
    first = Math.imul(first ^ code, 0x01000193) >>> 0;
    second = Math.imul(second ^ (code + index), 0x85ebca6b) >>> 0;
  }
  return `migration-${prefix}-${first.toString(16).padStart(8, "0")}${second
    .toString(16)
    .padStart(8, "0")}`;
}

function oneOf(value, allowed, label) {
  if (!allowed.includes(value)) throw typedError("VALIDATION_ERROR", `${label} is invalid.`);
  return value;
}

function boundedInteger(value, minimum, maximum, fallback) {
  const number = Number(value);
  return Number.isSafeInteger(number) && number >= minimum && number <= maximum ? number : fallback;
}

function parseJson(value, fallback) {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function parsePayload(item) {
  return { ...item, payload: parseJson(item.payload, {}) };
}

function now() {
  return new Date().toISOString();
}

function typedError(code, message, details = null) {
  const error = new Error(message);
  error.code = code;
  error.details = details;
  return error;
}

const SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS columns (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  position INTEGER NOT NULL UNIQUE,
  color TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cards (
  id TEXT PRIMARY KEY,
  column_id TEXT NOT NULL REFERENCES columns(id),
  position INTEGER NOT NULL,
  title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 160),
  description TEXT NOT NULL DEFAULT '',
  priority TEXT NOT NULL DEFAULT 'P2' CHECK(priority IN ('P0','P1','P2','P3')),
  assignee TEXT NOT NULL DEFAULT '',
  kind TEXT NOT NULL DEFAULT 'task' CHECK(kind IN ('task','question','result')),
  attention TEXT NOT NULL DEFAULT 'none' CHECK(attention IN ('none','needs_you','ai_working','ai_updated')),
  recurring INTEGER NOT NULL DEFAULT 0 CHECK(recurring IN (0,1)),
  cadence TEXT NOT NULL DEFAULT '',
  lookback_window TEXT NOT NULL DEFAULT '',
  archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1)),
  current_turn_id TEXT,
  latest_output_id TEXT,
  latest_successful_output_version_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  provenance TEXT NOT NULL DEFAULT '{}',
  last_change_actor TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dependencies (
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  depends_on_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  created_at TEXT NOT NULL,
  PRIMARY KEY(card_id,depends_on_id),
  CHECK(card_id<>depends_on_id)
);
CREATE TABLE IF NOT EXISTS plan_items (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  text TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','active','done','skipped','blocked','failed')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS execution_turns (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  display_number INTEGER NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('queued','claimed','running','needs_input','review','complete','failed','cancelled')),
  trigger TEXT NOT NULL,
  requester TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT '',
  agent_run_id TEXT NOT NULL DEFAULT '',
  idempotency_key TEXT NOT NULL UNIQUE,
  instruction_snapshot TEXT NOT NULL,
  linked_turn_id TEXT REFERENCES execution_turns(id),
  queued_at TEXT NOT NULL,
  claimed_at TEXT,
  started_at TEXT,
  input_requested_at TEXT,
  resumed_at TEXT,
  reviewed_at TEXT,
  completed_at TEXT,
  failed_at TEXT,
  cancelled_at TEXT,
  result TEXT NOT NULL DEFAULT '',
  error TEXT NOT NULL DEFAULT '',
  cancellation_reason TEXT NOT NULL DEFAULT '',
  memory_lineage TEXT NOT NULL DEFAULT '[]',
  UNIQUE(card_id,display_number)
);
CREATE TABLE IF NOT EXISTS turn_checkpoints (
  id TEXT PRIMARY KEY,
  turn_id TEXT NOT NULL REFERENCES execution_turns(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK(kind IN ('progress','output','warning','error')),
  summary TEXT NOT NULL,
  progress INTEGER CHECK(progress BETWEEN 0 AND 100),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outputs (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  turn_id TEXT REFERENCES execution_turns(id),
  position INTEGER NOT NULL,
  type TEXT NOT NULL CHECK(type IN ('text','status','link','program','table','diff','image','file')),
  title TEXT NOT NULL,
  owner TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('draft','streaming','complete','failed','stale','superseded','approved')),
  source TEXT NOT NULL,
  lineage TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  current_version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS output_versions (
  id TEXT PRIMARY KEY,
  output_id TEXT NOT NULL REFERENCES outputs(id) ON DELETE CASCADE,
  version INTEGER NOT NULL,
  title TEXT NOT NULL,
  payload TEXT NOT NULL,
  status TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(output_id,version)
);
CREATE TABLE IF NOT EXISTS output_surfaces (
  id TEXT PRIMARY KEY,
  output_version_id TEXT NOT NULL REFERENCES output_versions(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  payload TEXT NOT NULL,
  reference TEXT NOT NULL DEFAULT '',
  schema_version INTEGER NOT NULL,
  alt_text TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_threads (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL UNIQUE REFERENCES cards(id) ON DELETE CASCADE,
  phase TEXT NOT NULL CHECK(phase IN ('briefing','exploring','needs_feedback','committed','deep_work','review','accepted')),
  briefing TEXT NOT NULL,
  selected_option_id TEXT,
  gate_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_options (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL REFERENCES decision_threads(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  evidence TEXT NOT NULL,
  fit TEXT NOT NULL,
  tradeoffs TEXT NOT NULL,
  uncertainty TEXT NOT NULL,
  practical_constraints TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('active','shortlisted','rejected','selected')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_feedback (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL REFERENCES decision_threads(id) ON DELETE CASCADE,
  option_id TEXT REFERENCES decision_options(id),
  actor TEXT NOT NULL,
  action TEXT NOT NULL CHECK(action IN ('rank','shortlist','reject','restore','note')),
  value TEXT NOT NULL,
  note TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_gates (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL REFERENCES decision_threads(id) ON DELETE CASCADE,
  option_id TEXT NOT NULL REFERENCES decision_options(id),
  constraints_snapshot TEXT NOT NULL,
  evidence_snapshot TEXT NOT NULL,
  feedback_snapshot TEXT NOT NULL,
  unresolved_questions TEXT NOT NULL,
  confirmed_by TEXT NOT NULL,
  confirmed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_cycles (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  cycle_number INTEGER NOT NULL,
  topic TEXT NOT NULL,
  cadence TEXT NOT NULL,
  lookback_window TEXT NOT NULL,
  coverage TEXT NOT NULL,
  gaps TEXT NOT NULL,
  new_findings TEXT NOT NULL,
  retained_context TEXT NOT NULL,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  UNIQUE(card_id,cycle_number)
);
CREATE TABLE IF NOT EXISTS research_memory (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  cycle_id TEXT REFERENCES research_cycles(id),
  subject TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  summary TEXT NOT NULL,
  source TEXT NOT NULL,
  publisher TEXT NOT NULL,
  evidence_date TEXT NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  relevance TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('new','materially_updated','unchanged_context','duplicate_coverage','corrected','no_longer_current','dismissed','forgotten')),
  observation_state TEXT NOT NULL DEFAULT 'new' CHECK(observation_state IN ('new','materially_updated','unchanged_context','duplicate_coverage','no_longer_current')),
  coverage TEXT NOT NULL,
  gaps TEXT NOT NULL,
  lineage TEXT NOT NULL,
  pinned INTEGER NOT NULL DEFAULT 0 CHECK(pinned IN (0,1))
);
CREATE TABLE IF NOT EXISTS research_coverage (
  id TEXT PRIMARY KEY,
  cycle_id TEXT NOT NULL REFERENCES research_cycles(id) ON DELETE CASCADE,
  source_family TEXT NOT NULL,
  source TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('covered','gap','unavailable')),
  note TEXT NOT NULL,
  checked_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS activity_events (
  id TEXT PRIMARY KEY,
  card_id TEXT REFERENCES cards(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  actor TEXT NOT NULL,
  summary TEXT NOT NULL,
  payload TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attachments (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  relative_path TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  media_type TEXT NOT NULL,
  size INTEGER NOT NULL,
  fingerprint TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  turn_id TEXT REFERENCES execution_turns(id),
  relative_path TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS handoff_packets (
  id TEXT PRIMARY KEY,
  card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  direction TEXT NOT NULL CHECK(direction IN ('export','import')),
  format TEXT NOT NULL,
  payload TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('draft','previewed','approved','rejected')),
  created_at TEXT NOT NULL,
  approved_at TEXT
);
CREATE TABLE IF NOT EXISTS agent_runs (
  id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  agent_name TEXT NOT NULL,
  host TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('registered','watching','working','waiting','stopped','crashed')),
  control_generation INTEGER NOT NULL,
  observed_revision INTEGER NOT NULL,
  current_turn_id TEXT REFERENCES execution_turns(id),
  registered_at TEXT NOT NULL,
  heartbeat_at TEXT NOT NULL,
  stopped_at TEXT
);
CREATE TABLE IF NOT EXISTS agent_questions (
  id TEXT PRIMARY KEY,
  turn_id TEXT NOT NULL REFERENCES execution_turns(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  context TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('open','answered','withdrawn')),
  created_at TEXT NOT NULL,
  answered_at TEXT
);
CREATE TABLE IF NOT EXISTS agent_answers (
  id TEXT PRIMARY KEY,
  question_id TEXT NOT NULL UNIQUE REFERENCES agent_questions(id) ON DELETE CASCADE,
  actor TEXT NOT NULL,
  answer TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS idempotency_keys (
  key TEXT NOT NULL,
  scope TEXT NOT NULL,
  result_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  request_fingerprint TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(key,scope)
);
CREATE TABLE IF NOT EXISTS coordination_outbox (
  idempotency_key TEXT NOT NULL,
  scope TEXT NOT NULL,
  actor TEXT NOT NULL,
  run_id TEXT NOT NULL,
  generation INTEGER NOT NULL,
  revision INTEGER NOT NULL,
  current_turn_id TEXT,
  status TEXT NOT NULL,
  requested_state TEXT NOT NULL,
  holder_id TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  marker_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(idempotency_key,scope)
);
CREATE TABLE IF NOT EXISTS coordination_state (
  actor TEXT PRIMARY KEY,
  sequence INTEGER NOT NULL,
  marker_json TEXT NOT NULL,
  revision INTEGER NOT NULL,
  generation INTEGER NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS cards_column_order ON cards(column_id,archived,position);
CREATE INDEX IF NOT EXISTS cards_search ON cards(title,description);
CREATE INDEX IF NOT EXISTS cards_priority_attention ON cards(priority,attention,archived);
CREATE INDEX IF NOT EXISTS turns_card_status ON execution_turns(card_id,status,display_number);
CREATE UNIQUE INDEX IF NOT EXISTS turns_one_active_per_card
  ON execution_turns(card_id) WHERE status IN ('queued','claimed','running','needs_input','review');
CREATE INDEX IF NOT EXISTS turns_ready_claims ON execution_turns(status,queued_at);
CREATE INDEX IF NOT EXISTS plan_items_card_state ON plan_items(card_id,state);
CREATE INDEX IF NOT EXISTS outputs_card ON outputs(card_id);
CREATE INDEX IF NOT EXISTS output_history ON output_versions(output_id,version DESC);
CREATE INDEX IF NOT EXISTS activity_target_time ON activity_events(card_id,created_at DESC,type,actor);
CREATE INDEX IF NOT EXISTS dependencies_card ON dependencies(card_id,depends_on_id);
CREATE INDEX IF NOT EXISTS memory_fingerprint_state ON research_memory(fingerprint,state,last_seen DESC);
CREATE INDEX IF NOT EXISTS questions_turn_status ON agent_questions(turn_id,status);
`;
