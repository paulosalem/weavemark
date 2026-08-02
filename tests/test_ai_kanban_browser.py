"""Contracts for the static, file-backed AI Kanban implementation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "outputs" / "implementations" / "ai-kanban-browser"


def test_ai_kanban_static_asset_contract() -> None:
    required = (
        "index.html",
        "styles.css",
        "favicon.svg",
        "src/app.js",
        "src/bootstrap.js",
        "src/constants.js",
        "src/coordination.js",
        "src/file-workspace.js",
        "src/markdown.js",
        "src/output-selection.js",
        "src/packets.js",
        "src/provider-adapter.js",
        "src/repository.js",
        "src/save-queue.js",
        "src/sqlite-client.js",
        "src/sqlite-worker.js",
        "src/surfaces.js",
        "vendor/sql-wasm.js",
        "vendor/sql-wasm.wasm",
        "scripts/serve-static.mjs",
        "scripts/verify-vendor-assets.mjs",
        "sample-board-workspace/manifest.json",
        "sample-board-workspace/board.sqlite",
        "sample-board-workspace/.agents/skills/ai-kanban/SKILL.md",
        "sample-board-workspace/.agents/skills/ai-kanban/ai_kanban.py",
    )
    assert all((APP / relative).is_file() for relative in required)

    package = json.loads((APP / "package.json").read_text(encoding="utf-8"))
    assert package["dependencies"] == {"sql.js": "1.14.1"}
    assert (APP / "vendor/sql-wasm.wasm").stat().st_size > 500_000


def test_ai_kanban_has_no_backend_runtime() -> None:
    source = "\n".join(
        (APP / relative).read_text(encoding="utf-8")
        for relative in (
            "index.html",
            "src/app.js",
            "src/file-workspace.js",
            "src/sqlite-client.js",
            "src/sqlite-worker.js",
        )
    )
    for forbidden in (
        "new WebSocket(",
        "/api/",
        "localhost:",
        "Prisma",
        "Server Action",
    ):
        assert forbidden not in source

    assert "showDirectoryPicker" in source
    assert "showOpenFilePicker" not in source
    assert "showSaveFilePicker" not in source
    assert "FileSystemFileHandle" not in source  # structural typing, no fake class
    assert "new Worker(" in source
    assert "BroadcastChannel" in source
    assert "navigator.locks" in source
    assert "prepareWorkspaceSwitch" in source
    assert "Discard the in-memory draft and switch workspaces?" in source
    assert "This file is unreadable or is not a valid SQLite database." in source


def test_ai_kanban_sqlite_schema_and_repository_are_complete() -> None:
    worker = (APP / "src/sqlite-worker.js").read_text(encoding="utf-8")
    for table in (
        "metadata",
        "columns",
        "cards",
        "plan_items",
        "outputs",
        "output_versions",
        "output_surfaces",
        "activity_events",
        "dependencies",
        "execution_turns",
        "decision_threads",
        "research_memory",
        "handoff_packets",
        "agent_runs",
        "agent_questions",
        "idempotency_keys",
        "coordination_outbox",
        "coordination_state",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in worker
    for operation in (
        "createCard",
        "updateCard",
        "moveCard",
        "archiveCard",
        "addPlanItem",
        "updatePlanItem",
        "queueTurn",
        "claimReadyTurn",
        "transitionTurn",
        "addOutput",
        "versionOutput",
        "recordResearchMemory",
        "applyResponse",
        "export",
    ):
        assert f'"{operation}"' in worker
    assert 'db.run("BEGIN IMMEDIATE")' in worker
    assert 'db.run("ROLLBACK")' in worker
    assert "PRAGMA foreign_keys = ON" in worker


def test_ai_kanban_compiled_spec_matches_browser_delivery() -> None:
    compiled = (APP / "compiled-spec.md").read_text(encoding="utf-8")
    assert compiled.startswith(
        "# AI Kanban — Browser Workspace for Human-AI Work\n\n"
        "## 1. Architecture and Board Workspace lifecycle"
    )
    for obligation in (
        "showDirectoryPicker",
        "FileSystemDirectoryHandle",
        "Web Worker",
        "import/download",
        "AIProviderAdapter",
        "real demo workspace",
        "disables local-agent integration",
        "outputs/implementations/ai-kanban-browser/",
    ):
        assert obligation in compiled
    assert "Next.js" not in compiled
    assert "Prisma" not in compiled
    assert "Write an implementation-ready specification" not in compiled
    assert "Return an implementation specification" not in compiled
    assert "final answer" not in compiled.casefold()


def test_ai_kanban_demo_workspace_fix_is_preserved_in_source_and_output() -> None:
    source = (
        ROOT / "promplets/catalog/standalone/ai-kanban-board.weavemark.md"
    ).read_text(encoding="utf-8")
    implementation = "\n".join(
        (APP / relative).read_text(encoding="utf-8")
        for relative in ("index.html", "src/app.js")
    )

    for required in (
        "Create a real demo workspace",
        "Try in memory",
        "Personal Research",
    ):
        assert required.casefold() in source.casefold()
        assert required.casefold() in implementation.casefold()
    assert "disables local-agent integration" in source
    assert "Local agents cannot read or update" in implementation
    assert "demo: true, connectedOnly: true" in implementation


def test_ai_kanban_coordination_hardening_is_preserved_in_source_and_output() -> None:
    source = (
        ROOT / "promplets/catalog/standalone/ai-kanban-board.weavemark.md"
    ).read_text(encoding="utf-8")
    implementation = "\n".join(
        (APP / relative).read_text(encoding="utf-8")
        for relative in (
            "src/app.js",
            "src/coordination.js",
            "templates/skill/ai_kanban.py",
            "tests/real-coordination.spec.mjs",
        )
    )

    for required in (
        "single-flight",
        "durable SQLite control holder",
        "Freeze the user-confirmed grant target",
        "typed busy result",
        "same idempotency key",
        "guarded recovery command",
        "real-filesystem browser bridge",
    ):
        assert required.casefold() in source.casefold()
    for required in (
        "workspaceTransition",
        "selectRelevantAgent",
        "grantTarget",
        "MUTATION_BUSY",
        "COORDINATION_PUBLICATION_FAILED",
        "Copy guarded recovery command",
        "resume-real-turn",
    ):
        assert required in implementation


def test_ai_kanban_live_app_links_its_generation_path() -> None:
    html = (APP / "index.html").read_text(encoding="utf-8")

    assert "Built from a WeaveMark promplet." in html
    assert "Source promplet" in html
    assert "Compiled specification" in html
    assert "Tutorial" in html
