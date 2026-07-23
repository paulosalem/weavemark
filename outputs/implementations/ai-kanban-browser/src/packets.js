export const HANDOFF_SCHEMA = "ai-kanban-handoff/v1";
export const RESPONSE_SCHEMA = "ai-kanban-response/v1";

const OUTPUT_TYPES = new Set(["text", "status", "link", "program", "table"]);
const PLAN_STATUSES = new Set(["pending", "running", "done", "failed"]);

export function createHandoffPacket(card) {
  if (!card?.id) throw new TypeError("A card with a stable id is required.");
  return {
    schema: HANDOFF_SCHEMA,
    exportedAt: new Date().toISOString(),
    card: {
      id: card.id,
      title: card.title,
      description: card.description,
      priority: card.priority,
      assignee: card.assignee,
      column: card.columnTitle,
      dependencies: card.dependencies || [],
      plan: (card.plan || []).map(({ id, text, status }) => ({ id, text, status })),
      outputs: (card.outputs || []).map(({ id, type, title, content, status }) => ({
        id,
        type,
        title,
        content,
        status,
      })),
      recentActivity: (card.activity || []).slice(0, 12).map(
        ({ type, actor, summary, createdAt }) => ({ type, actor, summary, createdAt }),
      ),
    },
    requestedResponse: {
      schema: RESPONSE_SCHEMA,
      cardId: card.id,
      summary: "Brief explanation of the proposed update.",
      plan: [{ text: "Concrete step", status: "pending" }],
      outputs: [{ type: "text", title: "Result", content: "", status: "complete" }],
      activity: [{ type: "ai", summary: "What the assistant did." }],
    },
  };
}

export function validateResponsePacket(value, expectedCardId) {
  const errors = [];
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return { ok: false, errors: ["Response packet must be a JSON object."] };
  }
  if (value.schema !== RESPONSE_SCHEMA) {
    errors.push(`schema must be ${RESPONSE_SCHEMA}.`);
  }
  if (value.cardId !== expectedCardId) {
    errors.push("cardId does not match the open card.");
  }
  if (value.summary != null && typeof value.summary !== "string") {
    errors.push("summary must be a string.");
  }

  const plan = Array.isArray(value.plan) ? value.plan : [];
  for (const [index, item] of plan.entries()) {
    if (!item || typeof item.text !== "string" || !item.text.trim()) {
      errors.push(`plan[${index}].text must be a non-empty string.`);
    }
    if (!PLAN_STATUSES.has(item?.status || "pending")) {
      errors.push(`plan[${index}].status is unsupported.`);
    }
  }

  const outputs = Array.isArray(value.outputs) ? value.outputs : [];
  for (const [index, item] of outputs.entries()) {
    if (!item || !OUTPUT_TYPES.has(item.type)) {
      errors.push(`outputs[${index}].type is unsupported.`);
    }
    if (typeof item?.title !== "string" || !item.title.trim()) {
      errors.push(`outputs[${index}].title must be a non-empty string.`);
    }
    if (typeof item?.content !== "string") {
      errors.push(`outputs[${index}].content must be a string.`);
    }
  }

  const activity = Array.isArray(value.activity) ? value.activity : [];
  for (const [index, item] of activity.entries()) {
    if (typeof item?.summary !== "string" || !item.summary.trim()) {
      errors.push(`activity[${index}].summary must be a non-empty string.`);
    }
  }

  return {
    ok: errors.length === 0,
    errors,
    packet: errors.length
      ? null
      : {
          schema: RESPONSE_SCHEMA,
          cardId: value.cardId,
          summary: (value.summary || "").trim(),
          plan: plan.map((item) => ({
            text: item.text.trim(),
            status: item.status || "pending",
          })),
          outputs: outputs.map((item) => ({
            type: item.type,
            title: item.title.trim(),
            content: item.content,
            status: item.status || "complete",
          })),
          activity: activity.map((item) => ({
            type: item.type || "ai",
            summary: item.summary.trim(),
          })),
        },
  };
}
