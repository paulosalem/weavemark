import test from "node:test";
import assert from "node:assert/strict";
import { latestSuccessfulOutput } from "../src/output-selection.js";

test("selects projected or newest successful output and ignores draft/failed entries", () => {
  const projected = {
    id: "complete-1",
    status: "complete",
    content: "Trusted result",
    updatedAt: "2026-07-01T00:00:00Z",
  };
  const card = {
    latestOutputId: projected.id,
    outputs: [
      { id: "draft-new", status: "draft", content: "Unready", updatedAt: "2026-07-03T00:00:00Z" },
      { id: "failed-new", status: "failed", content: "Broken", updatedAt: "2026-07-02T00:00:00Z" },
      projected,
    ],
  };
  assert.equal(latestSuccessfulOutput(card), projected);
  assert.equal(latestSuccessfulOutput({
    outputs: card.outputs.filter((output) => output !== projected),
  }), null);
  assert.equal(latestSuccessfulOutput({
    outputs: [
      { id: "approved-old", status: "approved", updatedAt: "2026-07-01T00:00:00Z" },
      { id: "complete-new", status: "complete", updatedAt: "2026-07-04T00:00:00Z" },
    ],
  }).id, "complete-new");
  const versioned = latestSuccessfulOutput({
    latestOutputId: "output-1",
    latestSuccessfulOutputVersionId: "version-1",
    outputs: [{
      id: "output-1",
      status: "failed",
      title: "Failed v2",
      content: "failed",
    }],
    outputVersions: {
      "output-1": [
        {
          id: "version-2",
          version: 2,
          status: "failed",
          title: "Failed v2",
          content: "failed",
          createdAt: "2026-07-04T00:00:00Z",
        },
        {
          id: "version-1",
          version: 1,
          status: "complete",
          title: "Trusted v1",
          content: "trusted",
          createdAt: "2026-07-03T00:00:00Z",
        },
      ],
    },
  });
  assert.equal(versioned.title, "Trusted v1");
  assert.equal(versioned.content, "trusted");
});
