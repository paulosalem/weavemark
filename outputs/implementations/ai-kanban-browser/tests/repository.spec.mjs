import { expect, test } from "@playwright/test";

test("repository creates, exports, reopens, and reports health", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    const created = await repository.create({ workspaceId: "repository-test" });
    const bytes = await repository.exportBytes();
    const reopened = await repository.open(bytes);
    const health = await repository.health();
    await repository.close();
    repository.terminate();
    return {
      workspaceId: reopened.meta.workspace_id,
      columns: reopened.columns.map((column) => column.title),
      bytes: bytes.length,
      health,
      revision: created.meta.revision,
      format: reopened.meta.workspace_format,
      formatVersion: reopened.meta.format_version,
      protocolVersion: reopened.meta.protocol_version,
    };
  });

  expect(result.workspaceId).toBe("repository-test");
  expect(result.columns).toEqual(["Inbox", "Planning", "In Progress", "Review", "Blocked", "Done"]);
  expect(result.bytes).toBeGreaterThan(50_000);
  expect(result.health.ok).toBe(true);
  expect(result.health.foreignKeys).toBe(true);
  expect(result.format).toBe("ai-kanban-workspace");
  expect(result.formatVersion).toBe("1");
  expect(result.protocolVersion).toBe("1");
});

test("failed database open preserves the current live repository", async ({ page }) => {
  await page.goto("/");
  await page.addScriptTag({ url: "/vendor/sql-wasm.js" });
  const result = await page.evaluate(async () => {
    const SQL = await window.initSqlJs({
      locateFile: (file) => `/vendor/${file}`,
    });

    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "preserve-live" });
    const created = await repository.mutate("createCard", { title: "Keep me" });
    const trusted = await repository.exportBytes();
    const invalid = new SQL.Database(trusted);
    invalid.run("PRAGMA foreign_keys=OFF");
    invalid.run(
      "INSERT INTO dependencies(card_id,depends_on_id,created_at) VALUES(?,?,?)",
      [created.cardId, "missing-card", "2026-07-31T05:00:00Z"],
    );
    const invalidForeignKeys = invalid.export();
    invalid.close();
    let foreignKeyCode = null;
    try {
      await repository.open(invalidForeignKeys);
    } catch (error) {
      foreignKeyCode = error.code;
    }
    let errorCode = null;
    try {
      await repository.open(Uint8Array.from([0, 1, 2, 3, 4]));
    } catch (error) {
      errorCode = error.code;
    }
    const snapshot = await repository.snapshot();
    const card = await repository.card(created.cardId);
    await repository.close();
    repository.terminate();
    return {
      errorCode,
      foreignKeyCode,
      cards: snapshot.cards.length,
      title: card.title,
    };
  });
  expect(result.errorCode).toBe("CORRUPT_DATABASE");
  expect(result.foreignKeyCode).toBe("FOREIGN_KEY_VIOLATION");
  expect(result.cards).toBe(1);
  expect(result.title).toBe("Keep me");
});

test("crafted enum payload is rejected before HTML rendering and preserves the live database", async ({ page }) => {
  await page.goto("/");
  await page.addScriptTag({ url: "/vendor/sql-wasm.js" });
  const result = await page.evaluate(async () => {
    window.__certificationXss = false;
    const SQL = await window.initSqlJs({
      locateFile: (file) => `/vendor/${file}`,
    });
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "trusted-xss-boundary" });
    const card = await repository.mutate("createCard", { title: "Trusted card" });
    const trusted = await repository.exportBytes();
    const crafted = new SQL.Database(trusted);
    crafted.run("PRAGMA ignore_check_constraints=ON");
    crafted.run("UPDATE cards SET priority=? WHERE id=?", [
      `"><img data-certification-xss src=x onerror="window.__certificationXss=true">`,
      card.cardId,
    ]);
    const malicious = crafted.export();
    crafted.close();
    let code;
    try {
      await repository.open(malicious);
    } catch (error) {
      code = error.code;
    }
    const preserved = await repository.card(card.cardId);
    await repository.close();
    repository.terminate();
    return {
      code,
      title: preserved.title,
      executed: window.__certificationXss,
      injectedImages: document.querySelectorAll("[data-certification-xss]").length,
    };
  });
  expect(result).toEqual({
    code: "INVALID_DATABASE_CONTENT",
    title: "Trusted card",
    executed: false,
    injectedImages: 0,
  });
});

test("verified candidate rejection restores the prior live repository", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "trusted-candidate" });
    const trustedCard = await repository.mutate("createCard", {
      title: "Keep trusted state",
    });
    const candidateRepository = new BoardRepository();
    await candidateRepository.create({ workspaceId: "rejected-candidate" });
    await candidateRepository.mutate("createCard", { title: "Reject candidate" });
    const candidateBytes = await candidateRepository.exportBytes();
    await candidateRepository.close();
    candidateRepository.terminate();
    let code;
    let message;
    try {
      await repository.openVerified(candidateBytes, (candidate) => {
        if (candidate.meta.workspace_id !== "trusted-candidate") {
          const error = new Error("Candidate identity mismatch");
          error.code = "WORKSPACE_ID_MISMATCH";
          throw error;
        }
      });
    } catch (error) {
      code = error.code;
      message = error.message;
    }
    const snapshot = await repository.snapshot();
    const card = await repository.card(trustedCard.cardId);
    await repository.close();
    repository.terminate();
    return {
      code,
      message,
      workspaceId: snapshot.meta.workspace_id,
      title: card.title,
      cardCount: snapshot.cards.length,
    };
  });
  expect(result).toEqual({
    code: "WORKSPACE_ID_MISMATCH",
    message: "Candidate identity mismatch",
    workspaceId: "trusted-candidate",
    title: "Keep trusted state",
    cardCount: 1,
  });
});

test("real v2, v3, and v4 databases migrate transactionally to v6", async ({ page }) => {
  await page.goto("/");
  await page.addScriptTag({ url: "/vendor/sql-wasm.js" });
  const result = await page.evaluate(async () => {
    const SQL = await window.initSqlJs({
      locateFile: (file) => `/vendor/${file}`,
    });
    const { BoardRepository } = await import("./src/repository.js");
    const outcomes = [];
    for (const version of [2, 3, 4]) {
      const source = new BoardRepository();
      await source.create({ workspaceId: `migration-v${version}` });
      const current = await source.exportBytes();
      await source.close();
      source.terminate();
      const database = new SQL.Database(current);
      database.run("DROP TABLE coordination_state");
      database.run("ALTER TABLE coordination_outbox DROP COLUMN marker_json");
      database.run("ALTER TABLE coordination_outbox DROP COLUMN sequence");
      if (version < 4) {
        database.run("DROP TABLE coordination_outbox");
        database.run(
          "ALTER TABLE idempotency_keys DROP COLUMN request_fingerprint",
        );
        database.run(
          "ALTER TABLE cards DROP COLUMN latest_successful_output_version_id",
        );
        if (version === 2) {
          database.run("ALTER TABLE cards DROP COLUMN last_change_actor");
        }
      }
      database.run(
        "UPDATE metadata SET value=? WHERE key='schema_version'",
        [String(version)],
      );
      const downgraded = database.export();
      database.close();

      const migrated = new BoardRepository();
      const snapshot = await migrated.open(downgraded);
      const health = await migrated.health();
      const card = await migrated.mutate("createCard", {
        title: `Migrated from v${version}`,
      });
      outcomes.push({
        version,
        schema: health.schemaVersion,
        workspaceId: snapshot.meta.workspace_id,
        cardCreated: Boolean(card.cardId),
      });
      await migrated.close();
      migrated.terminate();
    }
    return outcomes;
  });
  expect(result).toEqual([
    {
      version: 2,
      schema: 6,
      workspaceId: "migration-v2",
      cardCreated: true,
    },
    {
      version: 3,
      schema: 6,
      workspaceId: "migration-v3",
      cardCreated: true,
    },
    {
      version: 4,
      schema: 6,
      workspaceId: "migration-v4",
      cardCreated: true,
    },
  ]);
});

test("movement, activity, turn claims, questions, cancellation, and requeue are transactional", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "turn-test" });
    const created = await repository.mutate("createCard", {
      title: "Turn lifecycle",
      description: "Run one bounded attempt.",
      columnId: "inbox",
      priority: "P1",
    });

    const cardId = created.cardId;
    await repository.mutate("moveCard", { cardId, columnId: "planning" });
    const queued = await repository.mutate("queueTurn", {
      cardId,
      instruction: "Do the bounded work.",
      idempotencyKey: "queue-1",
    });
    const queuedRevision = Number(repository.snapshotValue.meta.revision);
    const retriedQueue = await repository.mutate("queueTurn", {
      cardId,
      instruction: "Do the bounded work.",
      idempotencyKey: "queue-1",
    });
    const retryRevision = Number(repository.snapshotValue.meta.revision);
    let queueConflict = null;
    try {
      await repository.mutate("queueTurn", {
        cardId,
        instruction: "Different work.",
        idempotencyKey: "queue-1",
      });
    } catch (error) {
      queueConflict = error.code;
    }
    const claim = await repository.mutate("claimReadyTurn", {
      idempotencyKey: "claim-1",
      runId: "run-1",
    });
    await repository.mutate("transitionTurn", { turnId: claim.turnId, status: "running" });
    const asked = await repository.mutate("askQuestion", {
      turnId: claim.turnId,
      question: "Which constraint matters most?",
    });
    await repository.mutate("answerQuestion", {
      questionId: asked.questionId,
      answer: "Travel time.",
    });
    await repository.mutate("transitionTurn", {
      turnId: claim.turnId,
      status: "cancelled",
      reason: "Scope changed.",
    });
    const requeue = await repository.mutate("queueTurn", {
      cardId,
      instruction: "Try again with the answer.",
      trigger: "run_again",
      linkedTurnId: claim.turnId,
      idempotencyKey: "queue-2",
    });
    const card = await repository.card(cardId);
    await repository.close();
    repository.terminate();
    return {
      queued: queued.turnId,
      retriedQueue: retriedQueue.turnId,
      queuedRevision,
      retryRevision,
      queueConflict,
      claimed: claim.turnId,
      requeued: requeue.turnId,
      statuses: card.turns.map((turn) => turn.status),
      linked: card.turns.find((turn) => turn.id === requeue.turnId).linkedTurnId,
      activity: card.activity.map((event) => event.type),
    };
  });
  expect(result.queued).toBe(result.claimed);
  expect(result.retriedQueue).toBe(result.queued);
  expect(result.retryRevision).toBe(result.queuedRevision);
  expect(result.queueConflict).toBe("IDEMPOTENCY_CONFLICT");
  expect(result.requeued).not.toBe(result.claimed);
  expect(result.statuses).toContain("cancelled");
  expect(result.statuses).toContain("queued");
  expect(result.linked).toBe(result.claimed);
  expect(result.activity).toContain("card_moved");
  expect(result.activity).toContain("question_answered");
});

test("empty ready-turn claim is revision-neutral", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "empty-claim-test" });
    const before = Number(repository.snapshotValue.meta.revision);
    const claim = await repository.mutate("claimReadyTurn", {
      idempotencyKey: "empty-claim",
      runId: "run-empty",
    });

    const after = Number(repository.snapshotValue.meta.revision);
    await repository.close();
    repository.terminate();
    return { before, after, turnId: claim.turnId, noMutation: claim.noMutation };
  });
  expect(result).toEqual({
    before: 0,
    after: 0,
    turnId: null,
    noMutation: true,
  });
});

test("moving queued work to Done cancels it and leaves nothing claimable", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "done-queue-test" });
    const card = await repository.mutate("createCard", { title: "Finish without run" });
    const queued = await repository.mutate("queueTurn", {
      cardId: card.cardId,
      instruction: "Should be cancelled.",
      idempotencyKey: "done-queue",
    });
    await repository.mutate("moveCard", {
      cardId: card.cardId,
      columnId: "done",
    });
    const detail = await repository.card(card.cardId);
    const board = repository.snapshotValue.cards.find(
      (item) => item.id === card.cardId,
    );
    const beforeClaim = Number(repository.snapshotValue.meta.revision);
    const claim = await repository.mutate("claimReadyTurn", {
      idempotencyKey: "done-empty-claim",
      runId: "run-done",
    });
    const afterClaim = Number(repository.snapshotValue.meta.revision);
    await repository.close();
    repository.terminate();
    return {
      turnId: queued.turnId,
      status: detail.turns[0].status,
      reason: detail.turns[0].cancellationReason,
      current: board.currentTurnId,
      column: board.columnId,
      claim: claim.turnId,
      beforeClaim,
      afterClaim,
    };
  });
  expect(result.status).toBe("cancelled");
  expect(result.reason).toContain("moved to Done");
  expect(result.current).toBeNull();
  expect(result.column).toBe("done");
  expect(result.claim).toBeNull();
  expect(result.afterClaim).toBe(result.beforeClaim);
});

test("successful output projection survives failed versions and advances on approval", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "output-projection-test" });
    const card = await repository.mutate("createCard", { title: "Output projection" });
    const output = await repository.mutate("addOutput", {
      cardId: card.cardId,
      type: "text",
      title: "Trusted v1",
      content: "successful payload",
      status: "complete",
    });
    const before = await repository.card(card.cardId);
    await repository.mutate("versionOutput", {
      outputId: output.outputId,
      title: "Failed v2",
      content: "failed payload",
      status: "failed",
    });
    const failed = await repository.card(card.cardId);
    const boardAfterFailure = repository.snapshotValue.cards.find(
      (item) => item.id === card.cardId,
    );
    await repository.mutate("approveOutput", { outputId: output.outputId });
    const approved = await repository.card(card.cardId);
    await repository.close();
    repository.terminate();
    return {
      firstVersionId: before.outputVersions[output.outputId][0].id,
      projectedAfterFailure: failed.latestSuccessfulOutputVersionId,
      previewAfterFailure: boardAfterFailure.latestOutputPreview,
      currentStatusAfterFailure: failed.outputs[0].status,
      projectedAfterApproval: approved.latestSuccessfulOutputVersionId,
      newestVersionId: approved.outputVersions[output.outputId][0].id,
    };
  });
  expect(result.projectedAfterFailure).toBe(result.firstVersionId);
  expect(result.previewAfterFailure).toBe("successful payload");
  expect(result.currentStatusAfterFailure).toBe("failed");
  expect(result.projectedAfterApproval).toBe(result.newestVersionId);
});

test("decisions, output versions, and recurring memory preserve history", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "history-test" });
    const created = await repository.mutate("createCard", {
      title: "Monitor and decide",
      description: "Keep evidence.",
      recurring: true,
      decision: true,
    });
    const cardId = created.cardId;
    await repository.mutate("saveDecisionBriefing", {
      cardId,
      briefing: { goals: "Choose well", constraints: "Budget" },
    });
    const option = await repository.mutate("addDecisionOption", {
      cardId,
      title: "Option A",
      evidence: "Current source",
    });
    await repository.mutate("feedbackDecisionOption", {
      cardId,
      optionId: option.optionId,
      action: "shortlist",
      note: "Good fit",
    });
    await repository.mutate("setDecisionGate", {
      cardId,
      optionId: option.optionId,
      constraints: "Budget",
    });
    const output = await repository.mutate("addOutput", {
      cardId,
      type: "diff",
      title: "Proposal",
      content: "- old\\n+ new",
    });
    await repository.mutate("versionOutput", {
      outputId: output.outputId,
      title: "Proposal revised",
      content: "- old\\n+ better",
      status: "complete",
    });
    const first = await repository.mutate("recordResearchMemory", {
      cardId,
      subject: "Evidence",
      fingerprint: "evidence-1",
      contentHash: "hash-1",
      summary: "Original evidence",
    });
    const second = await repository.mutate("recordResearchMemory", {
      cardId,
      subject: "Evidence",
      fingerprint: "evidence-1",
      contentHash: "hash-2",
      summary: "Updated evidence",
      source: "https://sensitive.example/evidence",
      publisher: "Sensitive publisher",
      evidenceDate: "2026-07-30",
      relevance: "high",
      coverage: "Private coverage notes",
      gaps: "Private gap notes",
      lineage: ["private-parent"],
    });
    await repository.mutate("memoryAction", {
      cardId,
      memoryId: second.memoryId,
      action: "forget",
    });
    const card = await repository.card(cardId);
    await repository.close();
    repository.terminate();
    return {
      decision: card.decision,
      versions: card.outputVersions[output.outputId].length,
      classifications: [first.classification, second.classification],
      memoryCount: card.memory.length,
      forgotten: card.memory[0],
    };
  });
  expect(result.decision.phase).toBe("committed");
  expect(result.decision.feedback).toHaveLength(1);
  expect(result.versions).toBe(2);
  expect(result.classifications).toEqual(["new", "materially_updated"]);
  expect(result.memoryCount).toBe(1);
  expect(result.forgotten).toMatchObject({
    cycleId: null,
    subject: "",
    fingerprint: "",
    summary: "",
    source: "",
    publisher: "",
    evidenceDate: "",
    contentHash: "",
    relevance: "",
    state: "forgotten",
    coverage: "",
    gaps: "",
    lineage: [],
    pinned: false,
  });
});

test("dependencies reject transitive cycles and support removal", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "dependency-test" });
    const a = await repository.mutate("createCard", { title: "A" });
    const b = await repository.mutate("createCard", { title: "B" });
    const c = await repository.mutate("createCard", { title: "C" });
    await repository.mutate("addDependency", {
      cardId: a.cardId,
      dependsOnId: b.cardId,
    });

    await repository.mutate("addDependency", {
      cardId: b.cardId,
      dependsOnId: c.cardId,
    });
    let cycleCode = null;
    try {
      await repository.mutate("addDependency", {
        cardId: c.cardId,
        dependsOnId: a.cardId,
      });
    } catch (error) {
      cycleCode = error.code;
    }
    await repository.mutate("removeDependency", {
      cardId: b.cardId,
      dependsOnId: c.cardId,
    });
    await repository.mutate("addDependency", {
      cardId: c.cardId,
      dependsOnId: a.cardId,
    });
    const cardB = await repository.card(b.cardId);
    const cardC = await repository.card(c.cardId);
    await repository.close();
    repository.terminate();
    return {
      cycleCode,
      bDependencies: cardB.dependencies,
      cDependencies: cardC.dependencies.map((item) => item.title),
    };
  });
  expect(result.cycleCode).toBe("DEPENDENCY_CYCLE");
  expect(result.bDependencies).toEqual([]);
  expect(result.cDependencies).toEqual(["A"]);
});

test("decision acceptance completes review turn atomically and supports Run again", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "decision-accept-test" });
    const card = await repository.mutate("createCard", {
      title: "Decision",
      description: "Choose.",
      decision: true,
      columnId: "planning",
    });

    const option = await repository.mutate("addDecisionOption", {
      cardId: card.cardId,
      title: "Option",
    });
    await repository.mutate("setDecisionGate", {
      cardId: card.cardId,
      optionId: option.optionId,
      constraints: "Safe",
    });
    const queued = await repository.mutate("queueTurn", {
      cardId: card.cardId,
      instruction: "Prepare proposal.",
      idempotencyKey: "decision-turn",
    });
    const claimed = await repository.mutate("claimReadyTurn", {
      idempotencyKey: "decision-claim",
      runId: "run-decision",
    });
    await repository.mutate("transitionTurn", {
      turnId: claimed.turnId,
      status: "running",
    });
    await repository.mutate("transitionTurn", {
      turnId: claimed.turnId,
      status: "review",
    });
    await repository.mutate("setDecisionPhase", {
      cardId: card.cardId,
      phase: "accepted",
    });
    const accepted = await repository.card(card.cardId);
    const boardAccepted = repository.snapshotValue.cards.find(
      (item) => item.id === card.cardId,
    );
    await repository.mutate("moveCard", {
      cardId: card.cardId,
      columnId: "inbox",
      confirmRunAgain: true,
    });
    const rerun = await repository.card(card.cardId);
    await repository.close();
    repository.terminate();
    return {
      originalTurn: queued.turnId,
      acceptedStatus: accepted.turns[0].status,
      currentAfterAccept: boardAccepted.currentTurnId,
      columnAfterAccept: boardAccepted.columnId,
      rerunStatus: rerun.turns[0].status,
      rerunLinked: rerun.turns[0].linkedTurnId,
    };
  });
  expect(result.acceptedStatus).toBe("complete");
  expect(result.currentAfterAccept).toBeNull();
  expect(result.columnAfterAccept).toBe("done");
  expect(result.rerunStatus).toBe("queued");
  expect(result.rerunLinked).toBe(result.originalTurn);
});

test("decision revision atomically closes review and queues a linked successor", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "decision-revision-test" });
    const card = await repository.mutate("createCard", {
      title: "Revise decision",
      description: "Choose.",
      decision: true,
      columnId: "planning",
    });
    const option = await repository.mutate("addDecisionOption", {
      cardId: card.cardId,
      title: "Option",
    });
    await repository.mutate("setDecisionGate", {
      cardId: card.cardId,
      optionId: option.optionId,
      constraints: "Safe",
    });
    const queued = await repository.mutate("queueTurn", {
      cardId: card.cardId,
      instruction: "Prepare proposal.",
      idempotencyKey: "revision-original",
    });
    const claim = await repository.mutate("claimReadyTurn", {
      idempotencyKey: "revision-claim",
      runId: "run-revision",
    });
    await repository.mutate("transitionTurn", {
      turnId: claim.turnId,
      status: "running",
    });
    await repository.mutate("transitionTurn", {
      turnId: claim.turnId,
      status: "review",
    });
    const revision = await repository.mutate("requestDecisionRevision", {
      cardId: card.cardId,
      instruction: "Address the review concern.",
      idempotencyKey: "revision-successor",
    });
    const detail = await repository.card(card.cardId);
    const board = repository.snapshotValue.cards.find(
      (item) => item.id === card.cardId,
    );
    await repository.close();
    repository.terminate();
    return {
      original: queued.turnId,
      successor: revision.turnId,
      statuses: detail.turns.map((turn) => turn.status),
      linked: detail.turns[0].linkedTurnId,
      phase: detail.decision.phase,
      current: board.currentTurnId,
      column: board.columnId,
    };
  });
  expect(result.successor).not.toBe(result.original);
  expect(result.statuses).toEqual(["queued", "complete"]);
  expect(result.linked).toBe(result.original);
  expect(result.phase).toBe("deep_work");
  expect(result.current).toBe(result.successor);
  expect(result.column).toBe("in_progress");
});

test("approved response packet activity is appended with handoff provenance", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { BoardRepository } = await import("./src/repository.js");
    const repository = new BoardRepository();
    await repository.create({ workspaceId: "packet-activity-test" });
    const card = await repository.mutate("createCard", { title: "Import activity" });
    const applied = await repository.mutate("applyResponse", {
      cardId: card.cardId,
      packet: {
        schema: "ai-kanban-response/v1",
        cardId: card.cardId,
        summary: "Imported update",
        plan: [],
        outputs: [],
        activity: [
          { type: "research", summary: "Checked primary evidence." },
          { type: "ai", summary: "Prepared the recommendation." },
        ],
      },
    });
    const detail = await repository.card(card.cardId);
    await repository.close();
    repository.terminate();
    return {
      handoffId: applied.handoffId,
      events: detail.activity.slice(0, 3),
    };
  });
  expect(result.events.map((event) => event.type)).toEqual([
    "handoff_imported",
    "ai",
    "research",
  ]);
  for (const event of result.events.slice(1)) {
    expect(event.actor).toBe("AI handoff");
    expect(event.payload).toMatchObject({
      handoffId: result.handoffId,
      packetSchema: "ai-kanban-response/v1",
      provenance: "approved-response-packet",
    });
  }
});

    test("schema v6 indexes keep large mutation snapshots bounded", async ({ page }) => {
      await page.goto("/");
      await page.addScriptTag({ url: "/vendor/sql-wasm.js" });
      const result = await page.evaluate(async () => {
        const SQL = await window.initSqlJs({
          locateFile: (file) => `/vendor/${file}`,
        });
        const { BoardRepository } = await import("./src/repository.js");
        const source = new BoardRepository();
        await source.create({ workspaceId: "large-snapshot-indexes" });
        const created = await source.mutate("createCard", { title: "Large fixture" });
        const initial = await source.exportBytes();
        await source.close();
        source.terminate();

        const database = new SQL.Database(initial);
        database.run("BEGIN");
        const plan = database.prepare(
          `INSERT INTO plan_items(id,card_id,position,text,state,created_at,updated_at)
           VALUES(?,?,?,?,?,'2026-07-31T08:00:00Z','2026-07-31T08:00:00Z')`,
        );
        const output = database.prepare(
          `INSERT INTO outputs(
             id,card_id,turn_id,position,type,title,owner,status,source,lineage,
             created_at,updated_at,current_version
           ) VALUES(?,?,NULL,?,'text',?,'fixture','failed','fixture','[]',
                    '2026-07-31T08:00:00Z','2026-07-31T08:00:00Z',1)`,
        );
        for (let index = 0; index < 8_000; index += 1) {
          plan.run([
            `plan-${index}`,
            created.cardId,
            index,
            `Step ${index}`,
            index % 2 ? "done" : "pending",
          ]);
          output.run([
            `output-${index}`,
            created.cardId,
            index,
            `Output ${index}`,
          ]);
        }
        plan.free();
        output.free();
        database.run("COMMIT");
        const fixture = database.export();
        database.close();

        const repository = new BoardRepository();
        await repository.open(fixture);
        const started = performance.now();
        const mutation = await repository.mutate("updateCard", {
          cardId: created.cardId,
          title: "Large fixture updated",
        });
        const elapsed = performance.now() - started;
        const exported = await repository.exportBytes();
        await repository.close();
        repository.terminate();
        const inspected = new SQL.Database(exported);
        const indexes = inspected.exec(
          `SELECT name FROM sqlite_master
            WHERE type='index' AND name IN ('plan_items_card_state','outputs_card')
            ORDER BY name`,
        )[0].values.flat();
        inspected.close();
        return {
          elapsed,
          indexes,
          planCount: mutation.snapshot.cards[0].planCount,
          planDone: mutation.snapshot.cards[0].planDone,
          outputCount: mutation.snapshot.cards[0].outputCount,
        };
      });
      expect(result.indexes).toEqual(["outputs_card", "plan_items_card_state"]);
      expect(result.planCount).toBe(8_000);
      expect(result.planDone).toBe(4_000);
      expect(result.outputCount).toBe(8_000);
      expect(result.elapsed).toBeLessThan(2_000);
    });

    test("research refresh preserves human memory state and records observation separately", async ({ page }) => {
      await page.goto("/");
      const result = await page.evaluate(async () => {
        const { BoardRepository } = await import("./src/repository.js");
        const repository = new BoardRepository();
        await repository.create({ workspaceId: "research-refresh" });
        const card = await repository.mutate("createCard", {
          title: "Monitor evidence",
          recurring: true,
        });
        const first = await repository.mutate("recordResearchMemory", {
          cardId: card.cardId,
          subject: "Stable fact",
          fingerprint: "source:stable",
          contentHash: "hash-1",
          summary: "Machine summary",
        });
        await repository.mutate("memoryAction", {
          cardId: card.cardId,
          memoryId: first.memoryId,
          action: "correct",
          summary: "Human-corrected summary",
        });
        await repository.mutate("memoryAction", {
          cardId: card.cardId,
          memoryId: first.memoryId,
          action: "pin",
        });
        await repository.mutate("recordResearchMemory", {
          cardId: card.cardId,
          subject: "Stable fact",
          fingerprint: "source:stable",
          contentHash: "hash-2",
          summary: "Refresh must not overwrite",
          classification: "materially_updated",
        });
        const corrected = (await repository.card(card.cardId)).memory[0];
        await repository.mutate("memoryAction", {
          cardId: card.cardId,
          memoryId: first.memoryId,
          action: "dismiss",
        });
        await repository.mutate("recordResearchMemory", {
          cardId: card.cardId,
          subject: "Stable fact",
          fingerprint: "source:stable",
          contentHash: "hash-3",
          summary: "Second overwrite attempt",
          classification: "unchanged_context",
        });
        const dismissed = (await repository.card(card.cardId)).memory[0];
        await repository.close();
        repository.terminate();
        return { corrected, dismissed };
      });
      expect(result.corrected).toMatchObject({
        state: "corrected",
        observationState: "materially_updated",
        summary: "Human-corrected summary",
        pinned: true,
      });
      expect(result.dismissed).toMatchObject({
        state: "dismissed",
        observationState: "unchanged_context",
        summary: "Human-corrected summary",
        pinned: true,
      });
    });

    test("generic transitions cannot bypass claim or resume and terminal states withdraw questions", async ({ page }) => {
      await page.goto("/");
      const result = await page.evaluate(async () => {
        const { BoardRepository } = await import("./src/repository.js");
        const repository = new BoardRepository();
        await repository.create({ workspaceId: "turn-invariants" });
        const card = await repository.mutate("createCard", { title: "Invariant turn" });
        const queued = await repository.mutate("queueTurn", {
          cardId: card.cardId,
          instruction: "Preserve invariants",
          idempotencyKey: "invariant-queue",
        });
        let directClaim;
        try {
          await repository.mutate("transitionTurn", {
            turnId: queued.turnId,
            status: "claimed",
          });
        } catch (error) {
          directClaim = error.code;
        }
        const claimed = await repository.mutate("claimReadyTurn", {
          idempotencyKey: "invariant-claim",
          runId: "run-invariant",
        });
        await repository.mutate("transitionTurn", {
          turnId: claimed.turnId,
          status: "running",
        });
        await repository.mutate("askQuestion", {
          turnId: claimed.turnId,
          question: "Need a durable answer?",
        });
        let directResume;
        try {
          await repository.mutate("transitionTurn", {
            turnId: claimed.turnId,
            status: "running",
          });
        } catch (error) {
          directResume = error.code;
        }
        await repository.mutate("transitionTurn", {
          turnId: claimed.turnId,
          status: "cancelled",
          reason: "Stopped explicitly",
        });
        const detail = await repository.card(card.cardId);
        await repository.close();
        repository.terminate();
        return {
          directClaim,
          directResume,
          questionStatus: detail.turns[0].questions[0].status,
        };
      });
      expect(result).toEqual({
        directClaim: "INVALID_TURN_TRANSITION",
        directResume: "INVALID_TURN_TRANSITION",
        questionStatus: "withdrawn",
      });
    });

    test("program and diff outputs preserve exact whitespace and terminal newlines", async ({ page }) => {
      await page.goto("/");
      const result = await page.evaluate(async () => {
        const { BoardRepository } = await import("./src/repository.js");
        const repository = new BoardRepository();
        await repository.create({ workspaceId: "exact-output-payloads" });
        const card = await repository.mutate("createCard", { title: "Exact outputs" });
        const programPayload = "\n  echo 'hello'  \n\n";
        const diffPayload = " diff --git a/a b/a\n+line  \n\n";
        const program = await repository.mutate("addOutput", {
          cardId: card.cardId,
          type: "program",
          title: "Script",
          content: programPayload,
        });
        const diff = await repository.mutate("addOutput", {
          cardId: card.cardId,
          type: "diff",
          title: "Patch",
          content: diffPayload,
        });
        const versionPayload = "\n@@ -1 +1 @@\n-old\n+new  \n";
        await repository.mutate("versionOutput", {
          outputId: diff.outputId,
          title: "Patch v2",
          content: versionPayload,
        });
        const detail = await repository.card(card.cardId);
        await repository.close();
        repository.terminate();
        return {
          program: detail.outputVersions[program.outputId][0].content,
          diffV1: detail.outputVersions[diff.outputId][1].content,
          diffV2: detail.outputVersions[diff.outputId][0].content,
          expected: { programPayload, diffPayload, versionPayload },
        };
      });
      expect(result.program).toBe(result.expected.programPayload);
      expect(result.diffV1).toBe(result.expected.diffPayload);
      expect(result.diffV2).toBe(result.expected.versionPayload);
    });

    test("legacy migration is byte deterministic and rebuilds latest-success projections", async ({ page }) => {
      await page.goto("/");
      await page.addScriptTag({ url: "/vendor/sql-wasm.js" });
      const result = await page.evaluate(async () => {
        const SQL = await window.initSqlJs({
          locateFile: (file) => `/vendor/${file}`,
        });
        const legacy = new SQL.Database();
        legacy.run(`
          CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
          CREATE TABLE columns(id TEXT PRIMARY KEY,title TEXT,position INTEGER,color TEXT);
          CREATE TABLE cards(
            id TEXT PRIMARY KEY,column_id TEXT,position INTEGER,title TEXT,description TEXT,
            priority TEXT,assignee TEXT,created_at TEXT,updated_at TEXT,archived INTEGER
          );
          CREATE TABLE plan_items(
            id TEXT PRIMARY KEY,card_id TEXT,position INTEGER,text TEXT,status TEXT,
            created_at TEXT,updated_at TEXT
          );
          CREATE TABLE outputs(
            id TEXT PRIMARY KEY,card_id TEXT,position INTEGER,type TEXT,title TEXT,
            content TEXT,status TEXT,created_at TEXT,updated_at TEXT
          );
          CREATE TABLE activity(
            id TEXT PRIMARY KEY,card_id TEXT,type TEXT,actor TEXT,summary TEXT,payload TEXT,
            created_at TEXT
          );
          INSERT INTO columns VALUES('inbox','Inbox',100,'#000');
          INSERT INTO columns VALUES('planning','Planning',200,'#111');
          INSERT INTO columns VALUES('progress','In Progress',300,'#222');
          INSERT INTO columns VALUES('review','Review',400,'#333');
          INSERT INTO columns VALUES('blocked','Blocked',500,'#444');
          INSERT INTO columns VALUES('done','Done',600,'#555');
          INSERT INTO cards VALUES(
            'legacy-card','review',1024,'Legacy card','Description','P1','',
            '2025-01-01T00:00:00Z','2025-01-02T00:00:00Z',0
          );
          INSERT INTO outputs VALUES(
            'legacy-output','legacy-card',1024,'text','Successful output',
            'retained payload','complete','2025-01-02T00:00:00Z','2025-01-02T00:00:00Z'
          );
          INSERT INTO activity VALUES(
            'legacy-event','legacy-card','legacy','migration','Legacy event','{}',
            '2025-01-01T00:00:00Z'
          );
        `);
        const source = legacy.export();
        legacy.close();
        const { BoardRepository } = await import("./src/repository.js");
        const migrate = async () => {
          const repository = new BoardRepository();
          const snapshot = await repository.open(source.slice());
          const detail = await repository.card("legacy-card");
          const bytes = await repository.exportBytes();
          await repository.close();
          repository.terminate();
          const digest = await crypto.subtle.digest("SHA-256", bytes);
          return {
            digest: [...new Uint8Array(digest)]
              .map((byte) => byte.toString(16).padStart(2, "0"))
              .join(""),
            workspaceId: snapshot.meta.workspace_id,
            projection: detail.latestSuccessfulOutputVersionId,
            payload: detail.outputs[0].content,
          };
        };
        return [await migrate(), await migrate()];
      });
      expect(result[0]).toEqual(result[1]);
      expect(result[0].workspaceId).toMatch(/^migration-workspace-/);
      expect(result[0].projection).toMatch(/^migration-output-version-/);
      expect(result[0].payload).toBe("retained payload");
    });
