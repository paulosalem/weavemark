"""Contracts for final artifacts retained in replay bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from weavemark.app import _recorded_run_destinations
from weavemark.replay_snapshot import (
    RecordedRunSnapshot,
    RecordedRunSnapshotError,
    load_recorded_run_snapshot,
)

ROOT = Path(__file__).parents[1]
MARKET_REPLAY = (
    ROOT
    / "promplets"
    / "replays"
    / "catalog"
    / "executable"
    / "market-snapshot"
)


def test_market_replay_retains_the_complete_recorded_run() -> None:
    snapshot = load_recorded_run_snapshot(MARKET_REPLAY)

    assert snapshot is not None
    assert snapshot.mode == "compile-and-execute"
    assert str(snapshot.primary_output) == "execution-output.md"
    assert str(snapshot.open_artifact) == "market-dashboard.html"
    assert {
        (str(artifact.relative_path), artifact.kind)
        for artifact in snapshot.artifacts
    } == {
        ("execution-output.md", "execution-output"),
        ("execution-trace.md", "execution-trace"),
        ("market-dashboard.html", "package"),
    }
    assert "VALE3 Market Learning Dashboard" in snapshot.artifact(
        snapshot.open_artifact
    ).bundle_file.read_text(encoding="utf-8")


def test_recorded_run_snapshot_rejects_paths_that_escape_the_bundle(
    tmp_path: Path,
) -> None:
    manifest = _manifest(
        bundle_path="../outside.html",
        content=b"not used",
    )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RecordedRunSnapshotError, match="safe relative path"):
        load_recorded_run_snapshot(tmp_path)


def test_recorded_run_snapshot_rejects_modified_artifacts(tmp_path: Path) -> None:
    artifact_path = tmp_path / "run-artifacts" / "report.html"
    artifact_path.parent.mkdir()
    artifact_path.write_bytes(b"modified")
    manifest = _manifest(
        bundle_path="run-artifacts/report.html",
        content=b"original",
    )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RecordedRunSnapshotError, match="hash mismatch"):
        load_recorded_run_snapshot(tmp_path)


def test_snapshot_retains_the_bytes_that_passed_validation(tmp_path: Path) -> None:
    content = b"<html>validated</html>"
    artifact_path = tmp_path / "run-artifacts" / "report.html"
    artifact_path.parent.mkdir()
    artifact_path.write_bytes(content)
    manifest = _manifest(
        bundle_path="run-artifacts/report.html",
        content=content,
    )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    snapshot = load_recorded_run_snapshot(tmp_path)
    artifact_path.write_bytes(b"<html>changed later</html>")

    assert snapshot is not None
    assert snapshot.artifacts[0].content == content


def test_restore_rejects_case_equivalent_output_paths(tmp_path: Path) -> None:
    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    snapshot = _write_multi_artifact_snapshot(
        replay_dir,
        ("Report.html", "report.html"),
    )
    output_dir = tmp_path / "out"

    with pytest.raises(ValueError, match="case-equivalent output paths"):
        _recorded_run_destinations(
            snapshot,
            SimpleNamespace(output=None),
            output_dir,
        )


def test_restore_rejects_existing_hardlink_aliases(tmp_path: Path) -> None:
    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    snapshot = _write_multi_artifact_snapshot(
        replay_dir,
        ("one.html", "two.html"),
    )
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    first = output_dir / "one.html"
    first.write_text("existing", encoding="utf-8")
    (output_dir / "two.html").hardlink_to(first)

    with pytest.raises(ValueError, match="aliases of the same filesystem object"):
        _recorded_run_destinations(
            snapshot,
            SimpleNamespace(output=None),
            output_dir,
        )


def test_restore_rejects_ancestor_and_descendant_output_paths(
    tmp_path: Path,
) -> None:
    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    snapshot = _write_multi_artifact_snapshot(
        replay_dir,
        ("report", "report/index.html"),
    )

    with pytest.raises(ValueError, match="cannot contain one another"):
        _recorded_run_destinations(
            snapshot,
            SimpleNamespace(output=None),
            tmp_path / "out",
        )


def test_restore_rejects_destinations_inside_the_replay_bundle(
    tmp_path: Path,
) -> None:
    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    snapshot = _write_multi_artifact_snapshot(
        replay_dir,
        ("one.html", "two.html"),
    )

    with pytest.raises(ValueError, match="inside their replay bundle"):
        _recorded_run_destinations(
            snapshot,
            SimpleNamespace(output=None),
            replay_dir,
        )


def test_restore_rejects_case_variants_of_the_replay_bundle(
    tmp_path: Path,
) -> None:
    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    snapshot = _write_multi_artifact_snapshot(
        replay_dir,
        ("one.html", "two.html"),
    )
    case_variant = replay_dir.with_name(replay_dir.name.upper())

    with pytest.raises(ValueError, match="inside their replay bundle"):
        _recorded_run_destinations(
            snapshot,
            SimpleNamespace(output=None),
            case_variant,
        )


def _manifest(*, bundle_path: str, content: bytes) -> dict[str, object]:
    return {
        "original_run": {
            "mode": "compile-and-execute",
            "primary_output": "report.html",
            "open_artifact": "report.html",
            "artifacts": [
                {
                    "path": "report.html",
                    "bundle_path": bundle_path,
                    "kind": "package",
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            ],
        }
    }


def _write_multi_artifact_snapshot(
    replay_dir: Path,
    paths: tuple[str, str],
) -> RecordedRunSnapshot:
    artifacts: list[dict[str, object]] = []
    for index, path in enumerate(paths):
        content = f"artifact {index}".encode()
        bundle_path = replay_dir / "run-artifacts" / f"{index}.html"
        bundle_path.parent.mkdir(exist_ok=True)
        bundle_path.write_bytes(content)
        artifacts.append(
            {
                "path": path,
                "bundle_path": f"run-artifacts/{index}.html",
                "kind": "package",
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    manifest = {
        "original_run": {
            "mode": "compile-and-execute",
            "primary_output": paths[0],
            "open_artifact": paths[1],
            "artifacts": artifacts,
        }
    }
    (replay_dir / "manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    snapshot = load_recorded_run_snapshot(replay_dir)
    assert snapshot is not None
    return snapshot
