"""Validation and access for final artifacts retained in a replay bundle."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


class RecordedRunSnapshotError(ValueError):
    """Raised when a replay bundle's recorded-run snapshot is invalid."""


@dataclass(frozen=True)
class RecordedRunArtifact:
    """One immutable final artifact stored inside a replay bundle."""

    relative_path: PurePosixPath
    bundle_file: Path
    content: bytes
    kind: str
    byte_count: int
    sha256: str


@dataclass(frozen=True)
class RecordedRunSnapshot:
    """Final outputs retained from the execution that produced a replay bundle."""

    bundle_dir: Path
    mode: str
    artifacts: tuple[RecordedRunArtifact, ...]
    primary_output: PurePosixPath
    open_artifact: PurePosixPath

    def artifact(self, relative_path: PurePosixPath) -> RecordedRunArtifact:
        """Return the artifact with ``relative_path``."""

        return next(
            artifact
            for artifact in self.artifacts
            if artifact.relative_path == relative_path
        )


def load_recorded_run_snapshot(replay_dir: Path) -> RecordedRunSnapshot | None:
    """Load and validate a final-run snapshot, if the bundle declares one."""

    manifest_path = replay_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecordedRunSnapshotError(
            f"Replay manifest is unreadable: {manifest_path}"
        ) from exc

    original_run = manifest.get("original_run")
    if not isinstance(original_run, dict):
        return None
    artifact_data = original_run.get("artifacts")
    if artifact_data is None:
        return None
    if not isinstance(artifact_data, list) or not artifact_data:
        raise RecordedRunSnapshotError(
            "original_run.artifacts must be a non-empty array."
        )

    artifacts = tuple(
        _load_artifact(replay_dir, item, index)
        for index, item in enumerate(artifact_data)
    )
    artifact_paths = {artifact.relative_path for artifact in artifacts}
    if len(artifact_paths) != len(artifacts):
        raise RecordedRunSnapshotError(
            "original_run.artifacts contains duplicate output paths."
        )

    primary_output = _relative_path(
        original_run.get("primary_output"),
        field="original_run.primary_output",
    )
    open_artifact = _relative_path(
        original_run.get("open_artifact"),
        field="original_run.open_artifact",
    )
    for field, path in (
        ("original_run.primary_output", primary_output),
        ("original_run.open_artifact", open_artifact),
    ):
        if path not in artifact_paths:
            raise RecordedRunSnapshotError(
                f"{field} does not name an artifact in original_run.artifacts: {path}"
            )

    mode = original_run.get("mode")
    if not isinstance(mode, str) or not mode:
        raise RecordedRunSnapshotError(
            "original_run.mode must be a non-empty string."
        )
    return RecordedRunSnapshot(
        bundle_dir=replay_dir.resolve(),
        mode=mode,
        artifacts=artifacts,
        primary_output=primary_output,
        open_artifact=open_artifact,
    )


def _load_artifact(
    replay_dir: Path,
    value: Any,
    index: int,
) -> RecordedRunArtifact:
    field = f"original_run.artifacts[{index}]"
    if not isinstance(value, dict):
        raise RecordedRunSnapshotError(f"{field} must be an object.")

    relative_path = _relative_path(value.get("path"), field=f"{field}.path")
    bundle_path = _relative_path(
        value.get("bundle_path"),
        field=f"{field}.bundle_path",
    )
    kind = value.get("kind")
    if not isinstance(kind, str) or not kind:
        raise RecordedRunSnapshotError(f"{field}.kind must be a non-empty string.")
    byte_count = value.get("bytes")
    if not isinstance(byte_count, int) or byte_count < 0:
        raise RecordedRunSnapshotError(
            f"{field}.bytes must be a non-negative integer."
        )
    expected_sha256 = value.get("sha256")
    if (
        not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or any(character not in "0123456789abcdef" for character in expected_sha256)
    ):
        raise RecordedRunSnapshotError(
            f"{field}.sha256 must be a lowercase SHA-256 digest."
        )

    bundle_file = (replay_dir / Path(*bundle_path.parts)).resolve()
    try:
        bundle_file.relative_to(replay_dir.resolve())
    except ValueError as exc:
        raise RecordedRunSnapshotError(
            f"{field}.bundle_path escapes the replay bundle."
        ) from exc
    try:
        content = bundle_file.read_bytes()
    except OSError as exc:
        raise RecordedRunSnapshotError(
            f"{field}.bundle_path is unreadable: {bundle_file}"
        ) from exc
    if len(content) != byte_count:
        raise RecordedRunSnapshotError(
            f"{field} byte count mismatch: expected {byte_count}, got {len(content)}."
        )
    actual_sha256 = hashlib.sha256(content).hexdigest()
    if actual_sha256 != expected_sha256:
        raise RecordedRunSnapshotError(
            f"{field} hash mismatch: expected {expected_sha256}, got {actual_sha256}."
        )
    return RecordedRunArtifact(
        relative_path=relative_path,
        bundle_file=bundle_file,
        content=content,
        kind=kind,
        byte_count=byte_count,
        sha256=expected_sha256,
    )


def _relative_path(value: Any, *, field: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise RecordedRunSnapshotError(f"{field} must be a non-empty string.")
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
        raise RecordedRunSnapshotError(
            f"{field} must be a safe relative path without '..': {value!r}"
        )
    return path


__all__ = [
    "RecordedRunArtifact",
    "RecordedRunSnapshot",
    "RecordedRunSnapshotError",
    "load_recorded_run_snapshot",
]
