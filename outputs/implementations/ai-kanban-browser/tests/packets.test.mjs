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

test("exports repository plan state as packet status", () => {
  const packet = createHandoffPacket({
    id: "card-state",
    title: "Preserve plan state",
    description: "",
    priority: "P2",
    assignee: "",
    columnTitle: "Planning",
    plan: [{ id: "step-done", text: "Verified", state: "done" }],
  });

  assert.deepEqual(packet.card.plan, [
    { id: "step-done", text: "Verified", status: "done" },
  ]);
});

test("rejects present packet collections that are not arrays", () => {
  for (const field of ["plan", "outputs", "activity"]) {
    const result = validateResponsePacket({
      schema: RESPONSE_SCHEMA,
      cardId: "card-1",
      [field]: {},
    }, "card-1");
    assert.equal(result.ok, false);
    assert.match(result.errors.join(" "), new RegExp(`${field} must be an array`));
  }
});

test("rejects response values outside repository length and type bounds", () => {
  const result = validateResponsePacket({
    schema: RESPONSE_SCHEMA,
    cardId: "card-1",
    summary: "s".repeat(2_001),
    plan: [{ text: "p".repeat(501), status: "pending" }],
    outputs: [{
      type: "text",
      title: "t".repeat(201),
      content: "c".repeat(1_000_001),
      status: "complete",
    }],
    activity: [{
      type: "x".repeat(101),
      summary: "a".repeat(5_001),
    }],
  }, "card-1");
  assert.equal(result.ok, false);
  const errors = result.errors.join(" ");
  assert.match(errors, /summary must be at most 2000/);
  assert.match(errors, /plan\[0\]\.text must be at most 500/);
  assert.match(errors, /outputs\[0\]\.title must be at most 200/);
  assert.match(errors, /outputs\[0\]\.content must be at most 1000000/);
  assert.match(errors, /activity\[0\]\.summary must be at most 5000/);
  assert.match(errors, /activity\[0\]\.type/);
});

test("response imports enforce an aggregate encoded-byte budget before validation", () => {
  const packet = {
    schema: RESPONSE_SCHEMA,
    cardId: "card-budget",
    summary: "aggregate payload",
    outputs: [
      { type: "text", title: "First", content: "1234567890", status: "complete" },
      { type: "text", title: "Second", content: "abcdefghij", status: "complete" },
    ],
  };
  const result = validateResponsePacket(packet, "card-budget", 32);
  assert.equal(result.ok, false);
  assert.match(result.errors[0], /aggregate import limit/);
});
