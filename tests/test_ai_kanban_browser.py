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
        "src/file-workspace.js",
        "src/packets.js",
        "src/sqlite-client.js",
        "src/sqlite-worker.js",
        "vendor/sql-wasm.js",
        "vendor/sql-wasm.wasm",
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

    assert "showOpenFilePicker" in source
    assert "showSaveFilePicker" in source
    assert "FileSystemFileHandle" not in source  # structural typing, no fake class
    assert "new Worker(" in source
    assert "BroadcastChannel" in source
    assert "navigator.locks" in source
    assert source.count("function confirmWorkspaceSwitch()") == 1
    assert "Discard unsaved changes and switch workspaces?" in source
    assert "This file is unreadable or is not a valid SQLite database." in source


def test_ai_kanban_sqlite_schema_and_repository_are_complete() -> None:
    worker = (APP / "src/sqlite-worker.js").read_text(encoding="utf-8")
    for table in (
        "meta",
        "columns",
        "cards",
        "plan_items",
        "outputs",
        "activity",
        "dependencies",
        "handoffs",
    ):
        assert f"CREATE TABLE {table}" in worker
    for operation in (
        "createCard",
        "updateCard",
        "moveCard",
        "archiveCard",
        "addPlanItem",
        "updatePlanItem",
        "addOutput",
        "applyResponse",
        "export",
    ):
        assert f'"{operation}"' in worker
    assert 'db.run("BEGIN")' in worker
    assert 'db.run("ROLLBACK")' in worker
    assert "PRAGMA foreign_keys = ON" in worker


def test_ai_kanban_compiled_spec_matches_browser_delivery() -> None:
    compiled = (APP / "compiled-spec.md").read_text(encoding="utf-8")
    for obligation in (
        "showOpenFilePicker",
        "showSaveFilePicker",
        "FileSystemFileHandle",
        "Web Worker",
        "import/download",
        "AIProviderAdapter",
        "outputs/implementations/ai-kanban-browser/",
    ):
        assert obligation in compiled
    assert "Next.js" not in compiled
    assert "Prisma" not in compiled
