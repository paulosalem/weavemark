#!/usr/bin/env python3
"""Rebuild the checked-in sample Board Workspace from shipped assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3

ROOT = Path(__file__).parents[1]
SAMPLE = ROOT / "sample-board-workspace"
WORKSPACE_ID = "sample-personal-research-workspace"
TIMESTAMP = "2026-07-30T12:00:00Z"


def main() -> None:
    schema_source = (ROOT / "src" / "sqlite-worker.js").read_text(encoding="utf-8")
    match = re.search(r"const SCHEMA_SQL = `([\s\S]+)`;\s*$", schema_source)
    if not match:
        raise RuntimeError("Could not extract the browser schema")
    SAMPLE.mkdir(parents=True, exist_ok=True)
    database_path = SAMPLE / "board.sqlite"
    database_path.unlink(missing_ok=True)
    connection = sqlite3.connect(database_path)
    connection.executescript(match.group(1))
    metadata = {
        "schema_version": "6",
        "protocol_version": "1",
        "workspace_format": "ai-kanban-workspace",
        "format_version": "1",
        "workspace_id": WORKSPACE_ID,
        "revision": "0",
        "control_state": "human",
        "control_owner": "human",
        "control_holder": "human",
        "control_generation": "0",
        "control_lease_until": "",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
    }
    connection.executemany(
        "INSERT INTO metadata(key,value) VALUES(?,?)", metadata.items()
    )
    columns = (
        ("inbox", "Inbox", 100, "#64757a"),
        ("planning", "Planning", 200, "#547c86"),
        ("in_progress", "In Progress", 300, "#22746b"),
        ("review", "Review", 400, "#9a6b35"),
        ("blocked", "Blocked", 500, "#b55249"),
        ("done", "Done", 600, "#52735e"),
    )
    connection.executemany(
        "INSERT INTO columns(id,title,position,color) VALUES(?,?,?,?)", columns
    )
    connection.execute(
        """INSERT INTO cards(
             id,column_id,position,title,description,priority,assignee,kind,
             attention,recurring,cadence,lookback_window,created_at,updated_at,
             provenance,last_change_actor
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            "sample-card",
            "inbox",
            1024,
            "Plan a family research question",
            "Turn an open family question into an evidence-led plan, then mark it Ready for agent.",
            "P1",
            "You",
            "question",
            "none",
            0,
            "",
            "",
            TIMESTAMP,
            TIMESTAMP,
            '{"origin":"sample-workspace"}',
            "AI Kanban",
        ),
    )
    connection.execute(
        """INSERT INTO activity_events(id,card_id,type,actor,summary,payload,created_at)
           VALUES(?,?,?,?,?,'{}',?)""",
        (
            "sample-activity",
            "sample-card",
            "sample_created",
            "AI Kanban",
            "Sample workspace created.",
            TIMESTAMP,
        ),
    )
    connection.commit()
    connection.execute("PRAGMA wal_checkpoint")
    connection.close()

    copies = {
        "templates/root/AGENTS.md": "AGENTS.md",
        "templates/root/CLAUDE.md": "CLAUDE.md",
        "templates/skill/SKILL.md": ".agents/skills/ai-kanban/SKILL.md",
        "templates/skill/ai_kanban.py": ".agents/skills/ai-kanban/ai_kanban.py",
        "templates/skill/ai-kanban.sh": ".agents/skills/ai-kanban/ai-kanban.sh",
        "templates/skill/ai-kanban.ps1": ".agents/skills/ai-kanban/ai-kanban.ps1",
    }
    for source, target in copies.items():
        destination = SAMPLE / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = (ROOT / source).read_text(encoding="utf-8")
        content = content.replace("{{APP_VERSION}}", "2.0.0").replace(
            "{{WORKSPACE_FOLDER}}", "the selected Board Workspace folder"
        )
        destination.write_text(content, encoding="utf-8")
    for directory in ("attachments", "artifacts", "exports"):
        (SAMPLE / directory).mkdir(exist_ok=True)
    coordination = SAMPLE / ".ai-kanban" / "coordination"
    coordination.mkdir(parents=True, exist_ok=True)
    human = {
        "workspace_id": WORKSPACE_ID,
        "protocol_version": 1,
        "actor_id": "human",
        "holder_id": "human",
        "sequence": 0,
        "control_generation": 0,
        "observed_revision": 0,
        "requested_state": "human",
        "timestamp": TIMESTAMP,
    }
    (coordination / "human.json").write_text(
        json.dumps(human, indent=2) + "\n", encoding="utf-8"
    )

    paths = ["board.sqlite", *copies.values(), ".ai-kanban/coordination/human.json"]
    fingerprints = {
        path: hashlib.sha256((SAMPLE / path).read_bytes()).hexdigest()
        for path in paths
    }
    manifest = {
        "format": "ai-kanban-workspace",
        "format_version": 1,
        "protocol_version": 1,
        "schema_version": 6,
        "app_version": "2.0.0",
        "workspace_id": WORKSPACE_ID,
        "revision": 0,
        "primary_state": "board.sqlite",
        "reserved_directories": [
            "attachments",
            "artifacts",
            "exports",
            ".ai-kanban/coordination",
            ".agents/skills/ai-kanban",
        ],
        "application_files": [
            {"path": "manifest.json", "owner": "ai-kanban"},
            *[
                {
                    "path": path,
                    "owner": "ai-kanban",
                    "fingerprint": fingerprints[path],
                }
                for path in paths
            ],
        ],
        "agent_bootstrap_paths": list(copies.values()),
        "content_fingerprints": fingerprints,
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
    }
    (SAMPLE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copymode(ROOT / "templates" / "skill" / "ai-kanban.sh",
                    SAMPLE / ".agents" / "skills" / "ai-kanban" / "ai-kanban.sh")
    print(f"Built {SAMPLE}")


if __name__ == "__main__":
    main()
