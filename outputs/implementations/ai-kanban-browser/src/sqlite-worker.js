/* global initSqlJs */
importScripts("../vendor/sql-wasm.js");

const SCHEMA_VERSION = "1";
const DEFAULT_COLUMNS = [
  ["inbox", "Inbox", 100, "#52656b"],
  ["planning", "Planning", 200, "#547a83"],
  ["progress", "In Progress", 300, "#276c63"],
  ["review", "Review", 400, "#8a653a"],
  ["blocked", "Blocked", 500, "#a64f46"],
  ["done", "Done", 600, "#51705c"],
];

let SQL;
let db;

const ready = (async () => {
  SQL = await initSqlJs({
    locateFile: () => new URL("../vendor/sql-wasm.wasm", self.location.href).href,
  });
})();

self.addEventListener("message", async ({ data }) => {
  const { id, type, payload = {} } = data;
  try {
    await ready;
    const result = await dispatch(type, payload);
    const transfer = result?.buffer instanceof ArrayBuffer ? [result.buffer] : [];
    self.postMessage({ id, ok: true, result }, transfer);
  } catch (error) {
    self.postMessage({
      id,
      ok: false,
      error: {
        code: error.code || "SQLITE_ERROR",
        message: error.message || String(error),
      },
    });
  }
});

async function dispatch(type, payload) {
  switch (type) {
    case "open":
      return openDatabase(payload);
    case "snapshot":
      requireDatabase();
      return getSnapshot();
    case "card":
      requireDatabase();
      return getCard(payload.cardId);
    case "createCard":
      return mutate(() => createCard(payload));
    case "updateCard":
      return mutate(() => updateCard(payload));
    case "moveCard":
      return mutate(() => moveCard(payload));
    case "archiveCard":
      return mutate(() => archiveCard(payload.cardId));
    case "addPlanItem":
      return mutate(() => addPlanItem(payload));
    case "updatePlanItem":
      return mutate(() => updatePlanItem(payload));
    case "addOutput":
      return mutate(() => addOutput(payload));
    case "applyResponse":
      return mutate(() => applyResponse(payload));
    case "export": {
      requireDatabase();
      const bytes = db.export();
      const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
      return { buffer };
    }
    case "close":
      db?.close();
      db = null;
      return { closed: true };
    default:
      throw typedError("UNKNOWN_OPERATION", `Unsupported worker operation: ${type}`);
  }
}

function openDatabase({ buffer, seed }) {
  db?.close();
  db = buffer ? new SQL.Database(new Uint8Array(buffer)) : new SQL.Database();
  db.run("PRAGMA foreign_keys = ON");
  if (buffer) validateSchema();
  else initializeSchema(Boolean(seed));
  return getSnapshot();
}

function initializeSchema(seed) {
  db.run(`
    BEGIN;
    CREATE TABLE meta (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
    CREATE TABLE columns (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      position INTEGER NOT NULL UNIQUE,
      color TEXT NOT NULL
    );
    CREATE TABLE cards (
      id TEXT PRIMARY KEY,
      column_id TEXT NOT NULL REFERENCES columns(id),
      position INTEGER NOT NULL,
      title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 160),
      description TEXT NOT NULL DEFAULT '',
      priority TEXT NOT NULL DEFAULT 'P2' CHECK(priority IN ('P0','P1','P2','P3')),
      assignee TEXT NOT NULL DEFAULT '',
      archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1)),
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );
    CREATE INDEX cards_column_position ON cards(column_id, position);
    CREATE INDEX cards_search ON cards(title, assignee);
    CREATE TABLE plan_items (
      id TEXT PRIMARY KEY,
      card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
      position INTEGER NOT NULL,
      text TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','running','done','failed')),
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );
    CREATE INDEX plan_card_position ON plan_items(card_id, position);
    CREATE TABLE outputs (
      id TEXT PRIMARY KEY,
      card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
      position INTEGER NOT NULL,
      type TEXT NOT NULL CHECK(type IN ('text','status','link','program','table')),
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'complete'
        CHECK(status IN ('draft','streaming','complete','failed','stale')),
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );
    CREATE INDEX outputs_card_position ON outputs(card_id, position);
    CREATE TABLE activity (
      id TEXT PRIMARY KEY,
      card_id TEXT REFERENCES cards(id) ON DELETE CASCADE,
      type TEXT NOT NULL,
      actor TEXT NOT NULL,
      summary TEXT NOT NULL,
      payload TEXT NOT NULL DEFAULT '{}',
      created_at TEXT NOT NULL
    );
    CREATE INDEX activity_card_time ON activity(card_id, created_at DESC);
    CREATE TABLE dependencies (
      card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
      depends_on_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
      PRIMARY KEY(card_id, depends_on_id),
      CHECK(card_id <> depends_on_id)
    );
    CREATE TABLE handoffs (
      id TEXT PRIMARY KEY,
      card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
      direction TEXT NOT NULL CHECK(direction IN ('export','import')),
      payload TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    INSERT INTO meta(key, value) VALUES
      ('schema_version', '${SCHEMA_VERSION}'),
      ('workspace_id', '${crypto.randomUUID()}'),
      ('created_at', '${now()}');
    COMMIT;
  `);
  const statement = db.prepare(
    "INSERT INTO columns(id,title,position,color) VALUES(?,?,?,?)",
  );
  for (const column of DEFAULT_COLUMNS) statement.run(column);
  statement.free();
  if (seed) seedDemo();
}

function validateSchema() {
  const tables = rows(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='meta'",
  );
  if (!tables.length) throw typedError("INVALID_SCHEMA", "This is not an AI Kanban workspace.");
  const version = scalar("SELECT value FROM meta WHERE key='schema_version'");
  if (version !== SCHEMA_VERSION) {
    throw typedError(
      version && Number(version) > Number(SCHEMA_VERSION)
        ? "FUTURE_SCHEMA"
        : "UNSUPPORTED_SCHEMA",
      `Workspace schema ${version || "unknown"} is not supported.`,
    );
  }
  for (const table of ["columns", "cards", "plan_items", "outputs", "activity"]) {
    if (!scalar("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table])) {
      throw typedError("INVALID_SCHEMA", `Workspace table is missing: ${table}.`);
    }
  }
}

function seedDemo() {
  const cards = [
    ["demo-1", "planning", 1024, "Prepare launch brief", "Turn the release notes into a concise launch narrative.", "P1", "Planner"],
    ["demo-2", "progress", 1024, "Validate browser persistence", "Exercise create, save, reopen, and conflict recovery.", "P0", "Builder"],
    ["demo-3", "review", 1024, "Review accessibility", "Check keyboard movement, focus order, and narrow layouts.", "P1", "Reviewer"],
    ["demo-4", "inbox", 1024, "Research onboarding examples", "Collect three useful first-run board templates.", "P2", "Researcher"],
  ];
  const statement = db.prepare(`
    INSERT INTO cards(id,column_id,position,title,description,priority,assignee,created_at,updated_at)
    VALUES(?,?,?,?,?,?,?,?,?)
  `);
  for (const card of cards) statement.run([...card, now(), now()]);
  statement.free();
  addPlanItem({ cardId: "demo-2", text: "Create a workspace file", status: "done" });
  addPlanItem({ cardId: "demo-2", text: "Reopen exported bytes", status: "running" });
  addOutput({
    cardId: "demo-1",
    type: "status",
    title: "Launch readiness",
    content: "Draft ready · evidence review pending",
    status: "complete",
  });
  appendActivity("demo-1", "ai", "Planner created a first-pass launch structure.", "Planner");
  appendActivity("demo-2", "system", "Demo workspace initialized.", "System");
}

function createCard({ columnId = "inbox", title, description = "", priority = "P2", assignee = "" }) {
  requireText(title, "Card title");
  requireColumn(columnId);
  const id = crypto.randomUUID();
  const timestamp = now();
  db.run(
    `INSERT INTO cards(id,column_id,position,title,description,priority,assignee,created_at,updated_at)
     VALUES(?,?,?,?,?,?,?,?,?)`,
    [id, columnId, nextPosition("cards", "column_id", columnId), title.trim(), description, priority, assignee, timestamp, timestamp],
  );
  appendActivity(id, "human", "Card created.", "You");
  return { cardId: id };
}

function updateCard({ cardId, title, description = "", priority = "P2", assignee = "" }) {
  requireCard(cardId);
  requireText(title, "Card title");
  db.run(
    `UPDATE cards SET title=?, description=?, priority=?, assignee=?, updated_at=? WHERE id=?`,
    [title.trim(), description, priority, assignee, now(), cardId],
  );
  appendActivity(cardId, "human", "Card details updated.", "You");
  return { cardId };
}

function moveCard({ cardId, columnId, beforeCardId = null }) {
  const card = requireCard(cardId);
  requireColumn(columnId);
  let position = nextPosition("cards", "column_id", columnId);
  if (beforeCardId) {
    const before = requireCard(beforeCardId);
    if (before.columnId !== columnId) throw typedError("INVALID_MOVE", "Drop target is in another column.");
    position = before.position - 1;
  }
  db.run(
    "UPDATE cards SET column_id=?, position=?, updated_at=? WHERE id=?",
    [columnId, position, now(), cardId],
  );
  normalizeCardPositions(columnId);
  if (card.columnId !== columnId) normalizeCardPositions(card.columnId);
  appendActivity(cardId, "movement", `Moved to ${columnTitle(columnId)}.`, "You", {
    from: card.columnId,
    to: columnId,
  });
  return { cardId };
}

function archiveCard(cardId) {
  requireCard(cardId);
  db.run("UPDATE cards SET archived=1, updated_at=? WHERE id=?", [now(), cardId]);
  appendActivity(cardId, "human", "Card archived.", "You");
  return { cardId };
}

function addPlanItem({ cardId, text, status = "pending" }) {
  requireCard(cardId);
  requireText(text, "Plan step");
  const id = crypto.randomUUID();
  const timestamp = now();
  db.run(
    `INSERT INTO plan_items(id,card_id,position,text,status,created_at,updated_at)
     VALUES(?,?,?,?,?,?,?)`,
    [id, cardId, nextPosition("plan_items", "card_id", cardId), text.trim(), status, timestamp, timestamp],
  );
  appendActivity(cardId, "plan", `Plan step added: ${text.trim()}`, "You");
  return { cardId, planItemId: id };
}

function updatePlanItem({ cardId, planItemId, text, status }) {
  requireCard(cardId);
  db.run(
    "UPDATE plan_items SET text=?, status=?, updated_at=? WHERE id=? AND card_id=?",
    [text, status, now(), planItemId, cardId],
  );
  appendActivity(cardId, "plan", `Plan step marked ${status}.`, "You");
  return { cardId, planItemId };
}

function addOutput({ cardId, type = "text", title, content = "", status = "complete" }) {
  requireCard(cardId);
  requireText(title, "Output title");
  const id = crypto.randomUUID();
  const timestamp = now();
  db.run(
    `INSERT INTO outputs(id,card_id,position,type,title,content,status,created_at,updated_at)
     VALUES(?,?,?,?,?,?,?,?,?)`,
    [id, cardId, nextPosition("outputs", "card_id", cardId), type, title.trim(), content, status, timestamp, timestamp],
  );
  appendActivity(cardId, "output", `Output added: ${title.trim()}`, "You");
  return { cardId, outputId: id };
}

function applyResponse({ cardId, packet }) {
  requireCard(cardId);
  for (const item of packet.plan || []) addPlanItem({ cardId, ...item });
  for (const output of packet.outputs || []) addOutput({ cardId, ...output });
  for (const event of packet.activity || []) {
    appendActivity(cardId, event.type || "ai", event.summary, "AI");
  }
  db.run(
    "INSERT INTO handoffs(id,card_id,direction,payload,created_at) VALUES(?,?,?,?,?)",
    [crypto.randomUUID(), cardId, "import", JSON.stringify(packet), now()],
  );
  appendActivity(cardId, "import", packet.summary || "AI response packet applied.", "You");
  return { cardId };
}

function mutate(operation) {
  requireDatabase();
  db.run("BEGIN");
  try {
    const result = operation();
    db.run("COMMIT");
    return { ...result, snapshot: getSnapshot() };
  } catch (error) {
    db.run("ROLLBACK");
    throw error;
  }
}

function getSnapshot() {
  const columns = rows("SELECT id,title,position,color FROM columns ORDER BY position");
  const cards = rows(`
    SELECT c.id, c.column_id AS columnId, c.position, c.title, c.description,
           c.priority, c.assignee, c.created_at AS createdAt, c.updated_at AS updatedAt,
           (SELECT COUNT(*) FROM plan_items p WHERE p.card_id=c.id) AS planCount,
           (SELECT COUNT(*) FROM plan_items p WHERE p.card_id=c.id AND p.status='done') AS planDone,
           (SELECT COUNT(*) FROM outputs o WHERE o.card_id=c.id) AS outputCount
      FROM cards c
     WHERE c.archived=0
     ORDER BY c.column_id, c.position, c.created_at
  `);
  const meta = Object.fromEntries(rows("SELECT key,value FROM meta").map((item) => [item.key, item.value]));
  return { meta, columns, cards };
}

function getCard(cardId) {
  const card = requireCard(cardId);
  return {
    ...card,
    columnTitle: columnTitle(card.columnId),
    plan: rows(
      `SELECT id,text,status,position,created_at AS createdAt,updated_at AS updatedAt
         FROM plan_items WHERE card_id=? ORDER BY position`,
      [cardId],
    ),
    outputs: rows(
      `SELECT id,type,title,content,status,position,created_at AS createdAt,updated_at AS updatedAt
         FROM outputs WHERE card_id=? ORDER BY position`,
      [cardId],
    ),
    activity: rows(
      `SELECT id,type,actor,summary,payload,created_at AS createdAt
         FROM activity WHERE card_id=? ORDER BY created_at DESC, rowid DESC LIMIT 100`,
      [cardId],
    ).map((item) => ({ ...item, payload: JSON.parse(item.payload || "{}") })),
    dependencies: rows(
      `SELECT c.id,c.title FROM dependencies d JOIN cards c ON c.id=d.depends_on_id
        WHERE d.card_id=? ORDER BY c.title`,
      [cardId],
    ),
  };
}

function appendActivity(cardId, type, summary, actor, payload = {}) {
  db.run(
    "INSERT INTO activity(id,card_id,type,actor,summary,payload,created_at) VALUES(?,?,?,?,?,?,?)",
    [crypto.randomUUID(), cardId, type, actor, summary, JSON.stringify(payload), now()],
  );
}

function requireDatabase() {
  if (!db) throw typedError("NO_WORKSPACE", "Open or create a workspace first.");
}

function requireCard(cardId) {
  const card = rows(
    `SELECT id,column_id AS columnId,position,title,description,priority,assignee,
            created_at AS createdAt,updated_at AS updatedAt
       FROM cards WHERE id=? AND archived=0`,
    [cardId],
  )[0];
  if (!card) throw typedError("CARD_NOT_FOUND", "The selected card no longer exists.");
  return card;
}

function requireColumn(columnId) {
  if (!scalar("SELECT id FROM columns WHERE id=?", [columnId])) {
    throw typedError("COLUMN_NOT_FOUND", "The selected column no longer exists.");
  }
}

function requireText(value, label) {
  if (typeof value !== "string" || !value.trim()) {
    throw typedError("VALIDATION_ERROR", `${label} is required.`);
  }
}

function columnTitle(columnId) {
  return scalar("SELECT title FROM columns WHERE id=?", [columnId]) || columnId;
}

function nextPosition(table, field, value) {
  return Number(
    scalar(`SELECT COALESCE(MAX(position),0)+1024 FROM ${table} WHERE ${field}=?`, [value]),
  );
}

function normalizeCardPositions(columnId) {
  const cards = rows("SELECT id FROM cards WHERE column_id=? AND archived=0 ORDER BY position,created_at", [columnId]);
  const statement = db.prepare("UPDATE cards SET position=? WHERE id=?");
  cards.forEach((card, index) => statement.run([(index + 1) * 1024, card.id]));
  statement.free();
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

function now() {
  return new Date().toISOString();
}

function typedError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}
