from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

import pytest

APP = Path(__file__).parents[2]
SAMPLE = APP / "sample-board-workspace"


def run_cli(workspace: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(workspace / ".agents" / "skills" / "ai-kanban" / "ai_kanban.py"),
            "--workspace",
            str(workspace),
            *arguments,
        ],
        check=check,
        capture_output=True,
        text=True,
    )


def protocol_args(*, revision: int, generation: int = 0, key: str) -> tuple[str, ...]:
    return (
        "--actor", "test-agent",
        "--run-id", "run-1",
        "--revision", str(revision),
        "--generation", str(generation),
        "--idempotency-key", key,
    )


def assert_revision_pair(workspace: Path, expected: int) -> None:
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    connection = sqlite3.connect(workspace / "board.sqlite")
    database_revision = int(
        connection.execute(
            "SELECT value FROM metadata WHERE key='revision'"
        ).fetchone()[0]
    )
    connection.close()
    assert manifest["revision"] == expected
    assert database_revision == expected
    fingerprint = hashlib.sha256((workspace / "board.sqlite").read_bytes()).hexdigest()
    assert manifest["content_fingerprints"]["board.sqlite"] == fingerprint


def synchronize_manifest(workspace: Path) -> int:
    connection = sqlite3.connect(workspace / "board.sqlite")
    revision = int(
        connection.execute(
            "SELECT value FROM metadata WHERE key='revision'"
        ).fetchone()[0]
    )
    connection.close()
    manifest_path = workspace / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["revision"] = revision
    manifest["content_fingerprints"]["board.sqlite"] = hashlib.sha256(
        (workspace / "board.sqlite").read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return revision


def test_sample_workspace_preflight_and_announcement() -> None:
    result = json.loads(run_cli(SAMPLE, "preflight").stdout)
    assert result["ok"] is True
    assert result["control_holder"] == "human"
    announced = json.loads(
        run_cli(SAMPLE, "announce", "--actor", "test-agent", "--run-id", "run-1").stdout
    )
    assert announced["announced"] is True
    # The checked-in sample must remain deterministic.
    (SAMPLE / ".ai-kanban" / "coordination" / "agent-test-agent.json").unlink()


def test_agent_turn_lifecycle_and_control_yield(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    database = workspace / "board.sqlite"
    connection = sqlite3.connect(database)
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.execute(
        """INSERT INTO execution_turns(
             id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
             idempotency_key,instruction_snapshot,queued_at,memory_lineage
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            "turn-1", "sample-card", 1, "queued", "test", "human", "", "",
            "queued-before-agent", "Complete the sample turn.", "2026-07-30T12:01:00Z", "[]",
        ),
    )
    connection.execute(
        "UPDATE cards SET current_turn_id='turn-1',attention='ai_working' WHERE id='sample-card'"
    )
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)

    registered = json.loads(
        run_cli(
            workspace,
            "register",
            *protocol_args(revision=0, key="register-1"),
            "--name", "Test agent",
            "--host", "pytest",
        ).stdout
    )
    assert registered["revision"] == 1
    assert_revision_pair(workspace, 1)
    retried = json.loads(
        run_cli(
            workspace,
            "register",
            *protocol_args(revision=0, key="register-1"),
            "--name", "Test agent",
            "--host", "pytest",
        ).stdout
    )
    assert retried == {
        "idempotent": True,
        "revision": 1,
        "run_id": "run-1",
    }
    marker_path = workspace / ".ai-kanban" / "coordination" / "agent-test-agent.json"
    marker_path.unlink()
    republished = json.loads(
        run_cli(
            workspace,
            "register",
            *protocol_args(revision=0, key="register-1"),
            "--name", "Test agent",
            "--host", "pytest",
        ).stdout
    )
    assert republished["idempotent"] is True
    assert marker_path.is_file()
    current_marker = json.loads(marker_path.read_text(encoding="utf-8"))
    newer_marker = {
        **current_marker,
        "sequence": current_marker["sequence"] + 1,
        "control_generation": current_marker["control_generation"] + 1,
        "observed_revision": current_marker["observed_revision"] + 10,
        "timestamp": "2026-07-31T04:00:00Z",
    }
    marker_path.write_text(
        json.dumps(newer_marker, indent=2) + "\n",
        encoding="utf-8",
    )
    run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-1"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    assert json.loads(marker_path.read_text(encoding="utf-8")) == newer_marker
    marker_path.write_text(
        json.dumps(current_marker, indent=2) + "\n",
        encoding="utf-8",
    )
    conflict = run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-1"),
        "--name", "Test agent",
        "--host", "different-host",
        check=False,
    )
    assert json.loads(conflict.stderr)["code"] == "IDEMPOTENCY_CONFLICT"

    claimed = json.loads(
        run_cli(workspace, "claim", *protocol_args(revision=1, key="claim-1")).stdout
    )
    assert claimed["turn_id"] == "turn-1"
    assert claimed["instruction"] == "Complete the sample turn."
    assert claimed["revision"] == 2
    assert_revision_pair(workspace, 2)
    claimed_retry = json.loads(
        run_cli(workspace, "claim", *protocol_args(revision=1, key="claim-1")).stdout
    )
    assert claimed_retry == {
        "card_id": "sample-card",
        "idempotent": True,
        "instruction": "Complete the sample turn.",
        "revision": 2,
        "title": "Plan a family research question",
        "turn_id": "turn-1",
    }

    started = json.loads(
        run_cli(
            workspace,
            "start",
            *protocol_args(revision=2, key="start-1"),
            "--turn-id", "turn-1",
        ).stdout
    )
    assert started["revision"] == 3
    assert_revision_pair(workspace, 3)

    checkpoint = json.loads(
        run_cli(
            workspace,
            "checkpoint",
            *protocol_args(revision=3, key="checkpoint-1"),
            "--turn-id", "turn-1",
            "--summary", "Evidence checked.",
            "--progress", "60",
        ).stdout
    )
    assert checkpoint["revision"] == 4
    assert_revision_pair(workspace, 4)

    output = json.loads(
        run_cli(
            workspace,
            "output",
            *protocol_args(revision=4, key="output-1"),
            "--turn-id", "turn-1",
            "--type", "text",
            "--title", "Sample result",
            "--content", "Evidence-backed result.",
        ).stdout
    )
    assert output["revision"] == 5
    assert_revision_pair(workspace, 5)

    completed = json.loads(
        run_cli(
            workspace,
            "complete",
            *protocol_args(revision=5, key="complete-1"),
            "--turn-id", "turn-1",
            "--result", "The bounded turn completed.",
        ).stdout
    )
    assert completed["revision"] == 6
    assert_revision_pair(workspace, 6)

    rejected_ask = run_cli(
        workspace,
        "ask",
        *protocol_args(revision=6, key="ask-after-complete"),
        "--turn-id", "turn-1",
        "--question", "Can immutable history change?",
        check=False,
    )
    assert rejected_ask.returncode == 2
    assert json.loads(rejected_ask.stderr)["code"] == "TURN_NOT_RUNNING"
    rejected_checkpoint = run_cli(
        workspace,
        "checkpoint",
        *protocol_args(revision=6, key="checkpoint-after-complete"),
        "--turn-id", "turn-1",
        "--summary", "Too late",
        check=False,
    )
    assert json.loads(rejected_checkpoint.stderr)["code"] == "TURN_IMMUTABLE"
    rejected_output = run_cli(
        workspace,
        "output",
        *protocol_args(revision=6, key="output-after-complete"),
        "--turn-id", "turn-1",
        "--title", "Too late",
        "--content", "Immutable",
        check=False,
    )
    assert json.loads(rejected_output.stderr)["code"] == "TURN_IMMUTABLE"
    assert_revision_pair(workspace, 6)

    yielded = json.loads(
        run_cli(workspace, "yield", *protocol_args(revision=6, key="yield-1")).stdout
    )
    assert yielded == {"generation": 1, "revision": 7, "run_id": "run-1"}
    assert_revision_pair(workspace, 7)

    connection = sqlite3.connect(database)
    metadata = dict(connection.execute("SELECT key,value FROM metadata"))
    turn = connection.execute(
        "SELECT status,result FROM execution_turns WHERE id='turn-1'"
    ).fetchone()
    latest_successful_version = connection.execute(
        "SELECT latest_successful_output_version_id FROM cards WHERE id='sample-card'"
    ).fetchone()[0]
    connection.close()
    assert metadata["control_state"] == "human"
    assert metadata["control_holder"] == "human"
    assert metadata["control_generation"] == "1"
    assert turn == ("complete", "The bounded turn completed.")
    assert latest_successful_version
    marker = json.loads(
        (
            workspace
            / ".ai-kanban"
            / "coordination"
            / "agent-test-agent.json"
        ).read_text(encoding="utf-8")
    )
    assert marker["holder_id"] == "human"
    assert marker["requested_state"] == "human"
    assert marker["status"] == "stopped"


def test_stale_revision_is_rejected_without_mutation(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.execute("UPDATE metadata SET value='4' WHERE key='revision'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    result = run_cli(
        workspace,
        "register",
        *protocol_args(revision=3, key="stale-register"),
        "--name", "Test agent",
        "--host", "pytest",
        check=False,
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "REVISION_MISMATCH"


def test_manifest_publication_failure_records_partial_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)

    module_path = workspace / ".agents" / "skills" / "ai-kanban" / "ai_kanban.py"
    spec = importlib.util.spec_from_file_location("ai_kanban_partial_test", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = module.load_manifest(workspace)
    args = argparse.Namespace(
        actor="test-agent",
        run_id="run-1",
        revision=0,
        generation=0,
        idempotency_key="register-partial",
        name="Test agent",
        host="pytest",
    )
    monkeypatch.setattr(
        module,
        "publish_manifest_revision",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("disk full")),
    )

    with pytest.raises(module.ProtocolError) as captured:
        module.command_register(workspace, manifest, args)

    assert captured.value.code == "MANIFEST_PUBLICATION_FAILED"
    connection = sqlite3.connect(workspace / "board.sqlite")
    database_revision = connection.execute(
        "SELECT value FROM metadata WHERE key='revision'"
    ).fetchone()[0]
    connection.close()
    durable_manifest = json.loads(
        (workspace / "manifest.json").read_text(encoding="utf-8")
    )
    marker = json.loads(
        (
            workspace
            / ".ai-kanban"
            / "coordination"
            / "agent-test-agent.json"
        ).read_text(encoding="utf-8")
    )
    assert database_revision == "1"
    assert durable_manifest["revision"] == 0
    assert marker["observed_revision"] == 1
    assert marker["requested_state"] == "recovering"
    assert marker["status"] == "manifest_publication_failed"
    (
        workspace
        / ".ai-kanban"
        / "coordination"
        / "agent-test-agent.json"
    ).unlink()

    reconciled = json.loads(
        run_cli(
            workspace,
            "reconcile-manifest",
            "--actor",
            "test-agent",
            "--run-id",
            "run-1",
        ).stdout
    )
    assert reconciled == {"reconciled": True, "revision": 1}
    assert_revision_pair(workspace, 1)
    recovered_marker = json.loads(
        (
            workspace
            / ".ai-kanban"
            / "coordination"
            / "agent-test-agent.json"
        ).read_text(encoding="utf-8")
    )
    assert recovered_marker["status"] == "watching"
    assert recovered_marker["observed_revision"] == 1


def test_watch_generation_handles_human_reclamation(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.execute("UPDATE metadata SET value='2' WHERE key='control_generation'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    human_path = workspace / ".ai-kanban" / "coordination" / "human.json"
    human = json.loads(human_path.read_text(encoding="utf-8"))
    human.update(
        requested_state="reclaim_requested",
        control_generation=2,
        sequence=1,
    )
    human_path.write_text(json.dumps(human, indent=2) + "\n", encoding="utf-8")

    result = json.loads(
        run_cli(
            workspace,
            "watch",
            "--actor",
            "test-agent",
            "--run-id",
            "run-1",
            "--generation",
            "2",
            "--once",
        ).stdout
    )
    assert result == {"reason": "human_reclaim_requested", "stopped": True}


def test_coordination_symlink_escape_is_rejected(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    shutil.copytree(SAMPLE, workspace)
    outside.mkdir()
    coordination = workspace / ".ai-kanban" / "coordination"
    shutil.rmtree(coordination)
    coordination.symlink_to(outside, target_is_directory=True)

    result = run_cli(
        workspace,
        "announce",
        "--actor",
        "test-agent",
        "--run-id",
        "run-1",
        check=False,
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "PATH_ESCAPE"
    assert list(outside.iterdir()) == []


def test_coordination_outbox_republishes_missing_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)

    module_path = workspace / ".agents" / "skills" / "ai-kanban" / "ai_kanban.py"
    spec = importlib.util.spec_from_file_location("ai_kanban_outbox_test", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    args = argparse.Namespace(
        actor="test-agent",
        run_id="run-outbox",
        revision=0,
        generation=0,
        idempotency_key="register-outbox",
        name="Test agent",
        host="pytest",
    )
    original_publish = module.publish_exact_record
    monkeypatch.setattr(
        module,
        "publish_exact_record",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("mailbox unavailable")),
    )
    with pytest.raises(module.ProtocolError) as captured:
        module.command_register(workspace, module.load_manifest(workspace), args)
    assert captured.value.code == "COORDINATION_PUBLICATION_FAILED"
    assert_revision_pair(workspace, 1)

    marker_path = (
        workspace
        / ".ai-kanban"
        / "coordination"
        / "agent-test-agent.json"
    )
    marker_path.write_text("[]\n", encoding="utf-8")
    monkeypatch.setattr(module, "publish_exact_record", original_publish)
    result = module.command_register(workspace, module.load_manifest(workspace), args)
    assert result == {
        "idempotent": True,
        "revision": 1,
        "run_id": "run-outbox",
    }
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    assert marker["observed_revision"] == 1
    assert marker["run_id"] == "run-outbox"
    connection = sqlite3.connect(workspace / "board.sqlite")
    durable = connection.execute(
        "SELECT sequence,marker_json FROM coordination_state WHERE actor='test-agent'"
    ).fetchone()
    connection.close()
    assert durable[0] == marker["sequence"]
    assert json.loads(durable[1]) == marker


def test_needs_input_resume_requires_durable_answer(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-resume"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute(
        """INSERT INTO execution_turns(
             id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
             idempotency_key,instruction_snapshot,queued_at,memory_lineage
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            "turn-input", "sample-card", 1, "needs_input", "test", "human",
            "test-agent", "run-1", "queued-input", "Resume safely.",
            "2026-07-30T12:01:00Z", "[]",
        ),
    )
    connection.execute(
        """INSERT INTO agent_questions(id,turn_id,question,context,status,created_at)
           VALUES('question-1','turn-input','Need answer?','','open','2026-07-30T12:02:00Z')"""
    )
    connection.execute(
        "UPDATE cards SET current_turn_id='turn-input' WHERE id='sample-card'"
    )
    connection.execute("UPDATE metadata SET value='2' WHERE key='revision'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)

    rejected = run_cli(
        workspace,
        "resume",
        *protocol_args(revision=2, key="resume-1"),
        "--turn-id", "turn-input",
        check=False,
    )
    assert json.loads(rejected.stderr)["code"] == "ANSWER_REQUIRED"

    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute(
        """INSERT INTO agent_answers(id,question_id,actor,answer,created_at)
           VALUES('answer-1','question-1','human','Yes','2026-07-30T12:03:00Z')"""
    )
    connection.execute(
        "UPDATE agent_questions SET status='answered',answered_at='2026-07-30T12:03:00Z' WHERE id='question-1'"
    )
    connection.execute("UPDATE metadata SET value='3' WHERE key='revision'")
    connection.execute("UPDATE metadata SET value='1' WHERE key='control_generation'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    run_cli(
        workspace,
        "register",
        *protocol_args(
            revision=3,
            generation=1,
            key="register-resume-generation-1",
        ),
        "--name", "Test agent",
        "--host", "pytest",
    )
    resumed = json.loads(
        run_cli(
            workspace,
            "resume",
            *protocol_args(
                revision=4,
                generation=1,
                key="resume-generation-1",
            ),
            "--turn-id", "turn-input",
        ).stdout
    )
    assert resumed["revision"] == 5
    assert resumed["instruction"] == "Resume safely."
    assert resumed["answers"] == [{
        "question_id": "question-1",
        "question": "Need answer?",
        "answer": "Yes",
        "answered_at": "2026-07-30T12:03:00Z",
    }]
    resumed_retry = json.loads(
        run_cli(
            workspace,
            "resume",
            *protocol_args(
                revision=4,
                generation=1,
                key="resume-generation-1",
            ),
            "--turn-id", "turn-input",
        ).stdout
    )
    assert resumed_retry == {
        "answers": resumed["answers"],
        "card_id": "sample-card",
        "idempotent": True,
        "instruction": "Resume safely.",
        "revision": 5,
        "turn_id": "turn-input",
    }
    connection = sqlite3.connect(workspace / "board.sqlite")
    ownership = connection.execute(
        """SELECT t.status,t.actor,t.agent_run_id,r.status,r.current_turn_id,
                  r.control_generation
             FROM execution_turns t JOIN agent_runs r ON r.id='run-1'
            WHERE t.id='turn-input'"""
    ).fetchone()
    connection.close()
    assert ownership == (
        "running",
        "test-agent",
        "run-1",
        "working",
        "turn-input",
        1,
    )


def test_yield_requires_active_owned_run(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.execute(
        """INSERT INTO execution_turns(
             id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
             idempotency_key,instruction_snapshot,queued_at,memory_lineage
           ) VALUES(
             'unregistered-turn','sample-card',1,'queued','test','human','','',
             'unregistered-queue','Do work','2026-07-30T12:01:00Z','[]'
           )"""
    )
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    result = run_cli(
        workspace,
        "yield",
        *protocol_args(revision=0, key="yield-without-run"),
        check=False,
    )
    assert json.loads(result.stderr)["code"] == "RUN_NOT_ACTIVE"
    claim = run_cli(
        workspace,
        "claim",
        *protocol_args(revision=0, key="claim-without-run"),
        check=False,
    )
    assert json.loads(claim.stderr)["code"] == "RUN_NOT_ACTIVE"
    assert_revision_pair(workspace, 0)


def test_idle_watch_heartbeat_is_revision_neutral_and_only_publishes_coordination(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.execute(
        """INSERT INTO execution_turns(
             id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
             idempotency_key,instruction_snapshot,queued_at,memory_lineage
           ) VALUES(
             'run-turn','sample-card',1,'queued','test','human','','',
             'run-queue','Do work','2026-07-30T12:01:00Z','[]'
           )"""
    )
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-run-state"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    claim = json.loads(
        run_cli(
            workspace,
            "claim",
            *protocol_args(revision=1, key="claim-run-state"),
        ).stdout
    )
    assert claim["turn_id"] == "run-turn"
    connection = sqlite3.connect(workspace / "board.sqlite")
    run_state = connection.execute(
        "SELECT status,current_turn_id FROM agent_runs WHERE id='run-1'"
    ).fetchone()
    durable_counts_before = (
        connection.execute("SELECT COUNT(*) FROM idempotency_keys").fetchone()[0],
        connection.execute("SELECT COUNT(*) FROM coordination_outbox").fetchone()[0],
    )
    connection.close()
    assert run_state == ("working", "run-turn")

    watched = json.loads(
        run_cli(
            workspace,
            "watch",
            "--actor",
            "test-agent",
            "--run-id",
            "run-1",
            "--generation",
            "0",
            "--once",
        ).stdout
    )
    assert watched["revision"] == 2
    connection = sqlite3.connect(workspace / "board.sqlite")
    heartbeat_state = connection.execute(
        "SELECT status,current_turn_id,observed_revision FROM agent_runs WHERE id='run-1'"
    ).fetchone()
    durable_counts_after = (
        connection.execute("SELECT COUNT(*) FROM idempotency_keys").fetchone()[0],
        connection.execute("SELECT COUNT(*) FROM coordination_outbox").fetchone()[0],
    )
    connection.close()
    assert heartbeat_state == ("working", "run-turn", 2)
    assert durable_counts_after == durable_counts_before
    marker = json.loads(
        (
            workspace
            / ".ai-kanban"
            / "coordination"
            / "agent-test-agent.json"
        ).read_text(encoding="utf-8")
    )
    assert marker["status"] == "working"
    assert marker["current_turn_id"] == "run-turn"
    assert marker["observed_revision"] == 2

    yielded = json.loads(
        run_cli(
            workspace,
            "yield",
            *protocol_args(revision=2, key="yield-run-state"),
        ).stdout
    )
    assert yielded["revision"] == 3


def test_protocol_json_actor_timestamp_and_database_binding_validation(
    tmp_path: Path,
) -> None:
    array_workspace = tmp_path / "array-workspace"
    shutil.copytree(SAMPLE, array_workspace)
    (array_workspace / "manifest.json").write_text("[]\n", encoding="utf-8")
    array_result = run_cli(array_workspace, "preflight", check=False)
    assert json.loads(array_result.stderr)["code"] == "INVALID_MANIFEST"

    nested_workspace = tmp_path / "nested-workspace"
    shutil.copytree(SAMPLE, nested_workspace)
    nested_manifest_path = nested_workspace / "manifest.json"
    nested_manifest = json.loads(nested_manifest_path.read_text(encoding="utf-8"))
    nested_manifest["application_files"] = [None]
    nested_manifest_path.write_text(
        json.dumps(nested_manifest) + "\n",
        encoding="utf-8",
    )
    nested_result = run_cli(nested_workspace, "preflight", check=False)
    assert json.loads(nested_result.stderr)["code"] == "INVALID_MANIFEST"

    actor_result = run_cli(
        SAMPLE,
        "announce",
        "--actor",
        "agent:alternate-stream",
        "--run-id",
        "run-1",
        check=False,
    )
    assert json.loads(actor_result.stderr)["code"] == "INVALID_ACTOR"
    run_id_result = run_cli(
        SAMPLE,
        "announce",
        "--actor",
        "safe-agent",
        "--run-id",
        "run;touch-owned",
        check=False,
    )
    assert json.loads(run_id_result.stderr)["code"] == "INVALID_RUN_ID"

    human_workspace = tmp_path / "human-workspace"
    shutil.copytree(SAMPLE, human_workspace)
    connection = sqlite3.connect(human_workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.commit()
    connection.close()
    synchronize_manifest(human_workspace)
    human_path = human_workspace / ".ai-kanban" / "coordination" / "human.json"
    human_path.write_text("[]\n", encoding="utf-8")
    run_cli(
        human_workspace,
        "register",
        *protocol_args(revision=0, key="register-malformed-human"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    human_result = run_cli(
        human_workspace,
        "watch",
        "--actor",
        "test-agent",
        "--run-id",
        "run-1",
        "--generation",
        "0",
        "--once",
        check=True,
    )
    assert json.loads(human_result.stdout)["revision"] == 1

    human = {
        "workspace_id": "sample-personal-research-workspace",
        "protocol_version": 1,
        "actor_id": "human",
        "holder_id": "test-agent",
        "sequence": 1,
        "control_generation": 0,
        "observed_revision": 0,
        "requested_state": "reclaim_requested",
        "timestamp": "2026-07-31T03:00:00",
    }
    human_path.write_text(json.dumps(human) + "\n", encoding="utf-8")
    timestamp_result = run_cli(
        human_workspace,
        "watch",
        "--actor",
        "test-agent",
        "--run-id",
        "run-1",
        "--generation",
        "0",
        "--once",
        check=True,
    )
    assert json.loads(timestamp_result.stdout)["revision"] == 1

    fingerprint_workspace = tmp_path / "fingerprint-workspace"
    shutil.copytree(SAMPLE, fingerprint_workspace)
    connection = sqlite3.connect(fingerprint_workspace / "board.sqlite")
    connection.execute(
        "UPDATE metadata SET value='changed-without-manifest' WHERE key='updated_at'"
    )
    connection.commit()
    connection.close()
    fingerprint_result = run_cli(fingerprint_workspace, "preflight", check=False)
    assert json.loads(fingerprint_result.stderr)["code"] == "DATABASE_FINGERPRINT_MISMATCH"

    foreign_key_workspace = tmp_path / "foreign-key-workspace"
    shutil.copytree(SAMPLE, foreign_key_workspace)
    connection = sqlite3.connect(foreign_key_workspace / "board.sqlite")
    connection.execute("PRAGMA foreign_keys=OFF")
    connection.execute(
        """INSERT INTO dependencies(card_id,depends_on_id,created_at)
           VALUES('sample-card','missing-card','2026-07-31T03:00:00Z')"""
    )
    connection.commit()
    connection.close()
    synchronize_manifest(foreign_key_workspace)
    foreign_key_result = run_cli(
        foreign_key_workspace,
        "preflight",
        check=False,
    )
    assert json.loads(foreign_key_result.stderr)["code"] == "FOREIGN_KEY_VIOLATION"

    identity_workspace = tmp_path / "identity-workspace"
    shutil.copytree(SAMPLE, identity_workspace)
    connection = sqlite3.connect(identity_workspace / "board.sqlite")
    connection.execute(
        "UPDATE metadata SET value='swapped-workspace' WHERE key='workspace_id'"
    )
    connection.commit()
    connection.close()
    synchronize_manifest(identity_workspace)
    identity_result = run_cli(identity_workspace, "preflight", check=False)
    assert json.loads(identity_result.stderr)["code"] == "WORKSPACE_ID_MISMATCH"


@pytest.mark.parametrize(
    ("metadata_key", "metadata_value", "expected_code"),
    [
        ("workspace_id", "other-workspace", "WORKSPACE_ID_MISMATCH"),
        ("schema_version", "3", "SCHEMA_MISMATCH"),
        ("protocol_version", "2", "PROTOCOL_MISMATCH"),
        ("workspace_format", "other-format", "PROTOCOL_MISMATCH"),
        ("format_version", "2", "PROTOCOL_MISMATCH"),
    ],
)
def test_reconcile_manifest_verifies_sqlite_identity_before_publication(
    tmp_path: Path,
    metadata_key: str,
    metadata_value: str,
    expected_code: str,
) -> None:
    workspace = tmp_path / metadata_key
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute(
        "UPDATE metadata SET value=? WHERE key=?",
        (metadata_value, metadata_key),
    )
    connection.execute("UPDATE metadata SET value='1' WHERE key='revision'")
    connection.commit()
    connection.close()
    result = run_cli(
        workspace,
        "reconcile-manifest",
        "--actor",
        "test-agent",
        "--run-id",
        "run-1",
        check=False,
    )
    assert json.loads(result.stderr)["code"] == expected_code
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["revision"] == 0


def test_claim_requires_watching_run_without_current_turn(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    for turn_id, number, status in (("queued-turn", 1, "queued"),):
        connection.execute(
            """INSERT INTO execution_turns(
                 id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
                 idempotency_key,instruction_snapshot,queued_at,memory_lineage
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                turn_id,
                "sample-card",
                number,
                status,
                "test",
                "human",
                "",
                "",
                f"queue-{turn_id}",
                f"Instruction {number}",
                f"2026-07-30T12:0{number}:00Z",
                "[]",
            ),
        )
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-claim-invariant"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute(
        """UPDATE agent_runs SET status='working',current_turn_id='queued-turn'
            WHERE id='run-1'"""
    )
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)

    result = run_cli(
        workspace,
        "claim",
        *protocol_args(revision=1, key="second-claim"),
        check=False,
    )
    assert json.loads(result.stderr)["code"] == "RUN_NOT_ACTIVE"
    connection = sqlite3.connect(workspace / "board.sqlite")
    assert connection.execute(
        "SELECT status FROM execution_turns WHERE id='queued-turn'"
    ).fetchone()[0] == "queued"
    connection.close()


def test_cancellation_preserves_reviewed_result_and_withdraws_open_questions(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-cancel-preserve"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute(
        """INSERT INTO execution_turns(
             id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
             idempotency_key,instruction_snapshot,queued_at,reviewed_at,result,error,
             memory_lineage
           ) VALUES(
             'review-turn','sample-card',1,'review','test','human','test-agent','run-1',
             'review-queue','Review proposal','2026-07-30T12:01:00Z',
             '2026-07-30T12:02:00Z','Reviewed proposal','Existing warning','[]'
           )"""
    )
    connection.execute(
        """INSERT INTO agent_questions(id,turn_id,question,context,status,created_at)
           VALUES('review-question','review-turn','Still relevant?','','open',
                  '2026-07-30T12:03:00Z')"""
    )
    connection.execute(
        """UPDATE agent_runs SET status='working',current_turn_id='review-turn'
            WHERE id='run-1'"""
    )
    connection.execute(
        "UPDATE cards SET current_turn_id='review-turn' WHERE id='sample-card'"
    )
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)

    cancelled = json.loads(
        run_cli(
            workspace,
            "cancel",
            *protocol_args(revision=1, key="cancel-preserve"),
            "--turn-id", "review-turn",
            "--reason", "Human cancelled",
        ).stdout
    )
    assert cancelled["revision"] == 2
    connection = sqlite3.connect(workspace / "board.sqlite")
    turn = connection.execute(
        """SELECT status,result,error,cancellation_reason
             FROM execution_turns WHERE id='review-turn'"""
    ).fetchone()
    question = connection.execute(
        "SELECT status FROM agent_questions WHERE id='review-question'"
    ).fetchone()[0]
    connection.close()
    assert turn == (
        "cancelled",
        "Reviewed proposal",
        "Existing warning",
        "Human cancelled",
    )
    assert question == "withdrawn"


def test_future_human_record_is_transient_untrusted_watch_input(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-future-human"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    human_path = workspace / ".ai-kanban" / "coordination" / "human.json"
    human = json.loads(human_path.read_text(encoding="utf-8"))
    human.update(
        requested_state="reclaim_requested",
        sequence=99,
        timestamp="2999-01-01T00:00:00Z",
    )
    human_path.write_text(json.dumps(human) + "\n", encoding="utf-8")

    watched = json.loads(
        run_cli(
            workspace,
            "watch",
            "--actor", "test-agent",
            "--run-id", "run-1",
            "--generation", "0",
            "--once",
        ).stdout
    )
    assert watched["revision"] == 1
    assert watched.get("reason") is None


def test_cli_rejects_unsupported_manifest_format_version_with_typed_error(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    manifest_path = workspace / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["format_version"] = 99
    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    result = run_cli(workspace, "preflight", check=False)
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "FORMAT_VERSION_MISMATCH"


def test_cli_program_output_preserves_exact_whitespace_and_terminal_newlines(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    shutil.copytree(SAMPLE, workspace)
    connection = sqlite3.connect(workspace / "board.sqlite")
    connection.execute("UPDATE metadata SET value='agent' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='test-agent' WHERE key='control_holder'")
    connection.execute(
        """INSERT INTO execution_turns(
             id,card_id,display_number,status,trigger,requester,actor,agent_run_id,
             idempotency_key,instruction_snapshot,queued_at,memory_lineage
           ) VALUES(
             'exact-turn','sample-card',1,'queued','test','human','','',
             'exact-queue','Produce exact program','2026-07-30T12:01:00Z','[]'
           )"""
    )
    connection.commit()
    connection.close()
    synchronize_manifest(workspace)
    run_cli(
        workspace,
        "register",
        *protocol_args(revision=0, key="register-exact-output"),
        "--name", "Test agent",
        "--host", "pytest",
    )
    run_cli(
        workspace,
        "claim",
        *protocol_args(revision=1, key="claim-exact-output"),
    )
    run_cli(
        workspace,
        "start",
        *protocol_args(revision=2, key="start-exact-output"),
        "--turn-id", "exact-turn",
    )
    payload = "\n  print('exact')  \n\n"
    created = json.loads(
        run_cli(
            workspace,
            "output",
            *protocol_args(revision=3, key="program-exact-output"),
            "--turn-id", "exact-turn",
            "--type", "program",
            "--title", "Exact program",
            "--content", payload,
        ).stdout
    )
    connection = sqlite3.connect(workspace / "board.sqlite")
    stored = connection.execute(
        """SELECT v.payload,s.payload
             FROM output_versions v JOIN output_surfaces s
               ON s.output_version_id=v.id
            WHERE v.output_id=?""",
        (created["output_id"],),
    ).fetchone()
    connection.close()
    assert stored == (payload, payload)
