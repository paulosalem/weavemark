"""Persist a pipeline's produced artifacts to files.

A production point can name its artifact with ``@output ... file: <path>``. The
engines resolve that path at runtime (so ``file: pages/page-@{index}.png`` yields
one file per iteration) and record it on each artifact in
``ExecutionResult.metadata``. This module walks those records and writes the
bytes/text under a root output directory — the deterministic half of packaging,
independent of any particular deliverable format.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..engines.base import ExecutionResult, decode_generated_image
from ..protection import ProtectionContext


def _artifact_records(execution: ExecutionResult) -> list[dict[str, Any]]:
    """Return the produced-artifact records carried in execution metadata.

    Chain executions expose a ``metadata["artifacts"]`` list; a single-call
    image execution exposes one image inline. Only records that declare a
    ``file`` target are persistable.
    """

    metadata = execution.metadata or {}
    records = list(metadata.get("artifacts", []))
    if not records and metadata.get("output_type") == "image" and metadata.get("file"):
        records = [
            {
                "stage": "default",
                "index": 1,
                "file": metadata["file"],
                "images": metadata.get("images", []),
            }
        ]
    return [record for record in records if record.get("file")]


def has_persistable_artifacts(execution: ExecutionResult) -> bool:
    """Whether *execution* produced any ``@output file:`` artifacts to persist."""

    return bool(_artifact_records(execution))


def _safe_target(root: Path, file_name: str) -> Path | None:
    """Resolve ``file_name`` under ``root``, rejecting escapes."""

    candidate = Path(file_name)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    target = (root / candidate).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


def _record_payload(
    record: dict[str, Any],
    protection: ProtectionContext | None,
) -> bytes | None:
    """Decode a record's bytes: an image payload, or UTF-8 text."""

    if record.get("images"):
        return decode_generated_image(record["images"], protection)
    if "text" in record:
        return str(record["text"]).encode("utf-8")
    return None


def persist_artifact_record(
    record: dict[str, Any],
    root: Path,
    protection: ProtectionContext | None = None,
) -> str | None:
    """Write a single ``@output file:`` artifact under *root*.

    Returns the relative file path written (as declared in ``file:``), or ``None``
    when the record has no file target, escapes the root, or carries no payload.
    This is the atom used both by the batch writer below and by the streaming sink
    that persists each artifact the moment an engine produces it.
    """

    file_name = record.get("file")
    if not file_name:
        return None
    file_name = str(file_name)
    target = _safe_target(Path(root), file_name)
    if target is None:
        return None
    if protection is not None:
        target = protection.authorize_write(
            target,
            reason="Persisting an @output file artifact",
        )
    payload = _record_payload(record, protection)
    if payload is None:
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return file_name


def persist_execution_artifacts(
    execution: ExecutionResult,
    root: Path,
    protection: ProtectionContext | None = None,
) -> dict[str, list[str]]:
    """Write ``@output file:`` artifacts under *root*.

    Returns a mapping of stage name to the ordered list of relative file paths
    written for that stage (as declared in ``file:``), so a packaging step can
    reference them (e.g. ``@{page_files}``).
    """

    root = Path(root)
    stage_files: dict[str, list[str]] = {}
    for record in _artifact_records(execution):
        written = persist_artifact_record(record, root, protection)
        if written is None:
            continue
        stage = str(record.get("stage", "default"))
        stage_files.setdefault(stage, []).append(written)
    return stage_files


__all__ = [
    "persist_execution_artifacts",
    "persist_artifact_record",
    "has_persistable_artifacts",
]
