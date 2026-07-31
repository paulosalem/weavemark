import {
  MAX_WORKSPACE_BYTES,
  OUTPUT_STATUSES,
  OUTPUT_TYPES,
} from "./constants.js";
import { cleanText, isRecord } from "./validation.js";

export const HANDOFF_SCHEMA = "ai-kanban-handoff/v1";
export const RESPONSE_SCHEMA = "ai-kanban-response/v1";

const OUTPUT_TYPE_SET = new Set(OUTPUT_TYPES);
const OUTPUT_STATUS_SET = new Set(OUTPUT_STATUSES);
const PLAN_STATUSES = new Set(["pending", "active", "done", "skipped", "blocked", "failed"]);

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
      plan: (card.plan || []).map(({ id, text, state, status }) => ({
        id,
        text,
        status: state ?? status ?? "pending",
      })),
      decision: card.decision
        ? {
            phase: card.decision.phase,
            briefing: card.decision.briefing,
            options: card.decision.options?.map(
              ({ id, title, summary, evidence, tradeoffs, uncertainty, status }) => ({
                id,
                title,
                summary,
                evidence,
                tradeoffs,
                uncertainty,
                status,
              }),
            ),
            selectedOptionId: card.decision.selectedOptionId,
          }
        : null,
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
      requestedResponseShape: card.requestedResponseShape || "A concise update with evidence and explicit uncertainty.",
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

export function validateResponsePacket(
  value,
  expectedCardId,
  maximumEncodedBytes = MAX_WORKSPACE_BYTES,
) {
  const errors = [];
  if (!isRecord(value)) {
    return { ok: false, errors: ["Response packet must be a JSON object."] };
  }
  let encodedBytes;
  try {
    encodedBytes = new TextEncoder().encode(JSON.stringify(value)).byteLength;
  } catch {
    return { ok: false, errors: ["Response packet cannot be encoded as JSON."] };
  }
  if (encodedBytes > maximumEncodedBytes) {
    return {
      ok: false,
      errors: [`Response packet exceeds the ${maximumEncodedBytes}-byte aggregate import limit.`],
    };
  }
  if (value.schema !== RESPONSE_SCHEMA) {
    errors.push(`schema must be ${RESPONSE_SCHEMA}.`);
  }
  if (value.cardId !== expectedCardId) {
    errors.push("cardId does not match the open card.");
  }
  if (value.summary != null && typeof value.summary !== "string") {
    errors.push("summary must be a string.");
  } else if (value.summary?.length > 2_000) {
    errors.push("summary must be at most 2000 characters.");
  }

  for (const field of ["plan", "outputs", "activity"]) {
    if (field in value && !Array.isArray(value[field])) {
      errors.push(`${field} must be an array when present.`);
    }
  }
  const plan = Array.isArray(value.plan) ? value.plan : [];
  if (plan.length > 1_000) errors.push("plan must contain at most 1000 items.");
  for (const [index, item] of plan.entries()) {
    if (!item || typeof item.text !== "string" || !item.text.trim()) {
      errors.push(`plan[${index}].text must be a non-empty string.`);
    }
    if (!PLAN_STATUSES.has(item?.status || "pending")) {
      errors.push(`plan[${index}].status is unsupported.`);
    }
    if (typeof item?.text === "string" && item.text.trim().length > 500) {
      errors.push(`plan[${index}].text must be at most 500 characters.`);
    }
  }

  const outputs = Array.isArray(value.outputs) ? value.outputs : [];
  if (outputs.length > 1_000) errors.push("outputs must contain at most 1000 items.");
  for (const [index, item] of outputs.entries()) {
    if (!item || !OUTPUT_TYPE_SET.has(item.type)) {
      errors.push(`outputs[${index}].type is unsupported.`);
    }
    if (typeof item?.title !== "string" || !item.title.trim()) {
      errors.push(`outputs[${index}].title must be a non-empty string.`);
    }
    if (typeof item?.content !== "string") {
      errors.push(`outputs[${index}].content must be a string.`);
    }
    if (typeof item?.title === "string" && item.title.trim().length > 200) {
      errors.push(`outputs[${index}].title must be at most 200 characters.`);
    }
    if (typeof item?.content === "string" && item.content.length > 1_000_000) {
      errors.push(`outputs[${index}].content must be at most 1000000 characters.`);
    }
    if (!OUTPUT_STATUS_SET.has(item?.status || "complete")) {
      errors.push(`outputs[${index}].status is unsupported.`);
    }
  }

  const activity = Array.isArray(value.activity) ? value.activity : [];
  if (activity.length > 1_000) errors.push("activity must contain at most 1000 items.");
  for (const [index, item] of activity.entries()) {
    if (typeof item?.summary !== "string" || !item.summary.trim()) {
      errors.push(`activity[${index}].summary must be a non-empty string.`);
    }
    if (typeof item?.summary === "string" && item.summary.trim().length > 5_000) {
      errors.push(`activity[${index}].summary must be at most 5000 characters.`);
    }
    if (item?.type != null && (
      typeof item.type !== "string" ||
      !item.type.trim() ||
      item.type.trim().length > 100
    )) {
      errors.push(`activity[${index}].type must be non-empty text up to 100 characters.`);
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
          summary: cleanText(value.summary || "", "summary", 2_000),
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
