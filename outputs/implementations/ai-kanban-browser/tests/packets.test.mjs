import test from "node:test";
import assert from "node:assert/strict";
import {
  HANDOFF_SCHEMA,
  RESPONSE_SCHEMA,
  createHandoffPacket,
  validateResponsePacket,
} from "../src/packets.js";

test("creates a compact versioned handoff", () => {
  const packet = createHandoffPacket({
    id: "card-1",
    title: "Ship demo",
    description: "Build it",
    priority: "P1",
    assignee: "Researcher",
    columnTitle: "Planning",
    dependencies: [],
    plan: [{ id: "step-1", text: "Inspect", status: "done" }],
    outputs: [],
    activity: [],
  });

  assert.equal(packet.schema, HANDOFF_SCHEMA);
  assert.equal(packet.card.id, "card-1");
  assert.equal(packet.requestedResponse.schema, RESPONSE_SCHEMA);
});

test("validates and normalizes an AI response", () => {
  const result = validateResponsePacket(
    {
      schema: RESPONSE_SCHEMA,
      cardId: "card-1",
      summary: " Proposed update ",
      plan: [{ text: " Write tests ", status: "pending" }],
      outputs: [
        { type: "status", title: " Quality ", content: "Green", status: "complete" },
      ],
      activity: [{ summary: "Prepared a plan" }],
    },
    "card-1",
  );

  assert.equal(result.ok, true);
  assert.equal(result.packet.plan[0].text, "Write tests");
  assert.equal(result.packet.outputs[0].title, "Quality");
});

test("rejects wrong cards and unsafe shapes", () => {
  const result = validateResponsePacket(
    {
      schema: RESPONSE_SCHEMA,
      cardId: "other",
      plan: [{ text: "", status: "unknown" }],
      outputs: [{ type: "html", title: "", content: 42 }],
    },
    "card-1",
  );

  assert.equal(result.ok, false);
  assert.match(result.errors.join(" "), /cardId/);
  assert.match(result.errors.join(" "), /unsupported/);
});
