import assert from "node:assert/strict";
import fs from "node:fs/promises";
import test from "node:test";
import { validateAllPacks } from "../tools/validate-packs.mjs";

test("all checked-in packs validate and total 200 cards", async () => {
  const result = await validateAllPacks({ writeIndex: false });
  assert.equal(result.ok, true, result.errors.join("\n"));
  assert.equal(result.index.packs.length, 4);
  assert.equal(result.index.packs.reduce((sum, pack) => sum + pack.card_count, 0), 200);
});

test("generated pack index is deterministic and checked in", async () => {
  const result = await validateAllPacks({ writeIndex: false });
  const checkedIn = JSON.parse(await fs.readFile("content/packs/index.json", "utf8"));
  assert.deepEqual(checkedIn, result.index);
});

test("knowledge cards contain authored content without generator filler", async () => {
  const index = JSON.parse(await fs.readFile("content/packs/index.json", "utf8"));
  const filler = [
    "The learner should use this idea to organize later details",
    "The beginner-level limitation is that real cases include",
    "Use the example to point out where"
  ];
  for (const pack of index.packs) {
    const manifest = JSON.parse(
      await fs.readFile(`content/packs/${pack.id}/manifest.json`, "utf8")
    );
    for (const file of manifest.ordered_content_files) {
      const text = await fs.readFile(`content/packs/${pack.id}/${file}`, "utf8");
      for (const phrase of filler) assert.equal(text.includes(phrase), false, phrase);
    }
  }
});

test("generated content avoids known stale URLs and retired phrasing", async () => {
  const index = JSON.parse(await fs.readFile("content/packs/index.json", "utf8"));
  const badStrings = [
    "https://www.cdc.gov/ncbddd/actearly/milestones/index.html",
    "https://www.cdc.gov/safechild/",
    "relitigates preferences",
    "A lighthouse signal can guide many ships"
  ];
  for (const pack of index.packs) {
    const manifest = JSON.parse(await fs.readFile(`content/packs/${pack.id}/manifest.json`, "utf8"));
    const cardsText = await fs.readFile(`content/packs/${pack.id}/${manifest.ordered_content_files[0]}`, "utf8");
    const curriculumMapText = await fs.readFile(`content/packs/${pack.id}/curriculum-map.json`, "utf8");
    for (const bad of badStrings) {
      assert.equal(cardsText.includes(bad), false, `${pack.id} cards.json should not contain "${bad}"`);
      assert.equal(curriculumMapText.includes(bad), false, `${pack.id} curriculum-map.json should not contain "${bad}"`);
    }
  }
});

test("each card cites a real, honest subset of its pack's declared sources, not every source", async () => {
  const index = JSON.parse(await fs.readFile("content/packs/index.json", "utf8"));
  for (const pack of index.packs) {
    const manifest = JSON.parse(await fs.readFile(`content/packs/${pack.id}/manifest.json`, "utf8"));
    const cardsDoc = JSON.parse(await fs.readFile(`content/packs/${pack.id}/${manifest.ordered_content_files[0]}`, "utf8"));
    const declaredIds = new Set(cardsDoc.source_refs.map((sourceRef) => sourceRef.id));

    for (const card of cardsDoc.cards) {
      assert.ok(card.source_refs.length > 0, `${pack.id}/${card.id} has no source_refs`);
      for (const id of card.source_refs) {
        assert.ok(declaredIds.has(id), `${pack.id}/${card.id} references undeclared source "${id}"`);
      }
    }

    // The bug this guards against: every card citing the pack's entire source list verbatim.
    const subsets = new Set(cardsDoc.cards.map((card) => [...card.source_refs].sort().join("|")));
    assert.ok(
      subsets.size > 1,
      `${pack.id} cards all cite an identical source subset; expected per-card variety`
    );
    const blanketSubset = [...declaredIds].sort().join("|");
    assert.ok(
      !cardsDoc.cards.every((card) => [...card.source_refs].sort().join("|") === blanketSubset),
      `${pack.id} cards all cite every declared source, which is not an honest per-card selection`
    );
  }
});

test("card connections align with the real prerequisite graph and have no duplicate targets", async () => {
  const index = JSON.parse(await fs.readFile("content/packs/index.json", "utf8"));
  for (const pack of index.packs) {
    const manifest = JSON.parse(await fs.readFile(`content/packs/${pack.id}/manifest.json`, "utf8"));
    const cardsDoc = JSON.parse(await fs.readFile(`content/packs/${pack.id}/${manifest.ordered_content_files[0]}`, "utf8"));
    const byId = new Map(cardsDoc.cards.map((card) => [card.id, card]));

    for (const card of cardsDoc.cards) {
      const targets = card.connections.map((connection) => connection.card_id);
      assert.equal(
        new Set(targets).size,
        targets.length,
        `${pack.id}/${card.id} has duplicate connection target ids: ${targets.join(", ")}`
      );

      for (const connection of card.connections) {
        if (connection.type === "prerequisite") {
          assert.ok(
            card.prerequisites.includes(connection.card_id),
            `${pack.id}/${card.id} has a "prerequisite" connection to ${connection.card_id} that is not in its own prerequisites`
          );
        } else if (connection.type === "prepares-for") {
          const target = byId.get(connection.card_id);
          assert.ok(target, `${pack.id}/${card.id} prepares-for an unknown card ${connection.card_id}`);
          assert.ok(
            target.prerequisites.includes(card.id),
            `${pack.id}/${card.id} prepares-for ${connection.card_id}, but that card does not list ${card.id} as a prerequisite`
          );
        } else {
          assert.fail(`${pack.id}/${card.id} has an unexpected connection type "${connection.type}"`);
        }
      }
    }
  }
});

test("validation-report.json states honestly which checks are automated versus editorial", async () => {
  const index = JSON.parse(await fs.readFile("content/packs/index.json", "utf8"));
  for (const pack of index.packs) {
    const manifest = JSON.parse(await fs.readFile(`content/packs/${pack.id}/manifest.json`, "utf8"));
    const report = JSON.parse(
      await fs.readFile(`content/packs/${pack.id}/${manifest.validation_report_path}`, "utf8")
    );

    assert.ok(report.automated_checks, `${pack.id} validation report missing automated_checks`);
    assert.ok(report.editorial_review, `${pack.id} validation report missing editorial_review`);
    assert.ok(report.editorial_review.reviewed_at, `${pack.id} validation report missing a dated review note`);
    assert.match(
      report.editorial_review.limitation,
      /cannot prove|cannot verify|does not (prove|verify)/i,
      `${pack.id} validation report should state automation cannot prove claim correctness`
    );

    // The bug this guards against: hardcoding semantic claims like unsupported_claims: []
    // as if the structural validator had proven them.
    assert.equal(
      report.unsupported_claims,
      undefined,
      `${pack.id} validation report should not hardcode an "unsupported_claims" result`
    );
    assert.equal(
      report.duplicate_concepts,
      undefined,
      `${pack.id} validation report should not hardcode a "duplicate_concepts" result`
    );
    assert.ok(
      typeof report.unsupported_claims_check === "string" && /not automated/i.test(report.unsupported_claims_check),
      `${pack.id} validation report should say claim support is not automated`
    );
    assert.ok(
      typeof report.duplicate_concepts_check === "string" && /not automated/i.test(report.duplicate_concepts_check),
      `${pack.id} validation report should say duplicate-concept detection is not automated`
    );
  }
});
