#!/usr/bin/env python3
"""Dependency-free cooperative agent CLI for an AI Kanban Board Workspace."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import uuid

PROTOCOL_VERSION = 1
SCHEMA_VERSION = 6
WORKSPACE_FORMAT_VERSION = 1
MAX_COORDINATION_FUTURE_SKEW = timedelta(seconds=30)
ACTIVE_STATUSES = ("queued", "claimed", "running", "needs_input", "review")
TERMINAL_STATUSES = ("complete", "failed", "cancelled")
ACTOR_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ISO_TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$"
)


class ProtocolError(RuntimeError):
    """A typed protocol failure safe to show to an agent host."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def is_sqlite_busy(error: BaseException) -> bool:
    message = str(error).lower()
    return "locked" in message or "busy" in message


def workspace_root(value: str) -> Path:
    root = Path(value).resolve()
    manifest = root / "manifest.json"
    if not manifest.is_file():
        raise ProtocolError("MISSING_MANIFEST", f"No manifest.json in {root}")
    return root


def require_beneath(root: Path, target: Path, label: str) -> Path:
    canonical_root = root.resolve(strict=True)
    try:
        resolved = target.resolve(strict=target.exists())
        resolved.relative_to(canonical_root)
    except (OSError, ValueError) as error:
        raise ProtocolError("PATH_ESCAPE", f"{label} escapes the workspace") from error
    return resolved


def coordination_directory(root: Path, *, create: bool) -> Path:
    current = root.resolve(strict=True)
    for part in (".ai-kanban", "coordination"):
        candidate = current / part
        if candidate.is_symlink():
            raise ProtocolError("PATH_ESCAPE", "Coordination directory cannot be a symlink")
        if candidate.exists():
            if not candidate.is_dir():
                raise ProtocolError("PATH_ESCAPE", "Coordination path is not a directory")
        elif create:
            candidate.mkdir()
        else:
            raise ProtocolError("PATH_ESCAPE", "Coordination directory is missing")
        current = require_beneath(root, candidate, "Coordination directory")
    return current


def coordination_record_path(root: Path, name: str, *, create_directory: bool) -> Path:
    if Path(name).name != name:
        raise ProtocolError("PATH_ESCAPE", "Coordination record name is invalid")
    directory = coordination_directory(root, create=create_directory)
    path = directory / name
    if path.is_symlink():
        raise ProtocolError("PATH_ESCAPE", "Coordination record cannot be a symlink")
    require_beneath(root, directory, "Coordination directory")
    if path.exists():
        require_beneath(root, path, "Coordination record")
    return path


def load_manifest(root: Path) -> dict:
    try:
        value = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProtocolError("INVALID_MANIFEST", str(error)) from error
    if not isinstance(value, dict):
        raise ProtocolError("INVALID_MANIFEST", "Manifest must be a JSON object")
    if value.get("format") != "ai-kanban-workspace":
        raise ProtocolError("INVALID_MANIFEST", "Unsupported workspace format")
    if value.get("format_version") != WORKSPACE_FORMAT_VERSION:
        raise ProtocolError(
            "FORMAT_VERSION_MISMATCH",
            f"Unsupported workspace format_version {value.get('format_version')!r}",
        )
    if value.get("protocol_version") != PROTOCOL_VERSION:
        raise ProtocolError("PROTOCOL_MISMATCH", "Unsupported protocol version")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ProtocolError("SCHEMA_MISMATCH", "Open the workspace in AI Kanban to migrate it first")
    try:
        revision = int(value["revision"])
    except (KeyError, TypeError, ValueError) as error:
        raise ProtocolError("INVALID_MANIFEST", "Manifest revision is invalid") from error
    if revision < 0:
        raise ProtocolError("INVALID_MANIFEST", "Manifest revision is invalid")
    if not isinstance(value.get("content_fingerprints"), dict):
        raise ProtocolError("INVALID_MANIFEST", "Manifest fingerprints must be an object")
    for field in ("reserved_directories", "agent_bootstrap_paths"):
        paths = value.get(field)
        if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
            raise ProtocolError("INVALID_MANIFEST", f"{field} must be an array of paths")
        if len(paths) != len(set(paths)):
            raise ProtocolError("INVALID_MANIFEST", f"{field} contains duplicate paths")
        for path in paths:
            validate_relative_path(path)
    application_files = value.get("application_files")
    if not isinstance(application_files, list):
        raise ProtocolError("INVALID_MANIFEST", "application_files must be an array")
    application_paths: set[str] = set()
    for index, item in enumerate(application_files):
        if not isinstance(item, dict):
            raise ProtocolError(
                "INVALID_MANIFEST",
                f"application_files[{index}] must be an object",
            )
        path = item.get("path")
        if not isinstance(path, str):
            raise ProtocolError(
                "INVALID_MANIFEST",
                f"application_files[{index}].path is invalid",
            )
        validate_relative_path(path)
        if path in application_paths:
            raise ProtocolError("INVALID_MANIFEST", f"Duplicate application file: {path}")
        application_paths.add(path)
        if not isinstance(item.get("owner"), str) or not item["owner"]:
            raise ProtocolError(
                "INVALID_MANIFEST",
                f"application_files[{index}].owner is invalid",
            )
        fingerprint = item.get("fingerprint")
        if fingerprint is not None and (
            not isinstance(fingerprint, str)
            or not re.fullmatch(r"[a-f0-9]{64}", fingerprint)
        ):
            raise ProtocolError(
                "INVALID_MANIFEST",
                f"application_files[{index}].fingerprint is invalid",
            )
    for field in ("created_at", "updated_at"):
        if field in value:
            require_iso_timestamp(value[field], f"manifest {field}")
    primary_state = value.get("primary_state", "")
    state_path = validate_relative_path(primary_state)
    if primary_state not in application_paths:
        raise ProtocolError("INVALID_MANIFEST", "application_files omits primary_state")
    for path, fingerprint in value["content_fingerprints"].items():
        validate_relative_path(path)
        if not isinstance(fingerprint, str) or not re.fullmatch(
            r"[a-f0-9]{64}", fingerprint
        ):
            raise ProtocolError("INVALID_MANIFEST", f"Invalid fingerprint: {path}")
    if primary_state not in value["content_fingerprints"]:
        raise ProtocolError("INVALID_MANIFEST", "Primary state fingerprint is missing")
    database = (root / state_path).resolve()
    if root not in database.parents or not database.is_file():
        raise ProtocolError("PATH_ESCAPE", "Primary state escapes the workspace or is missing")
    return value


def publish_manifest_revision(
    root: Path,
    manifest: dict,
    *,
    expected_revision: int,
    committed_revision: int,
) -> None:
    current = load_manifest(root)
    if current["workspace_id"] != manifest["workspace_id"]:
        raise ProtocolError("WORKSPACE_ID_MISMATCH", "Manifest workspace changed during commit")
    if int(current["revision"]) != expected_revision:
        raise ProtocolError(
            "COMMIT_MARKER_MISMATCH",
            f"Manifest revision changed from expected {expected_revision}",
        )
    database_path = root / validate_relative_path(current["primary_state"])
    fingerprint = hashlib.sha256(database_path.read_bytes()).hexdigest()
    current["revision"] = committed_revision
    current["updated_at"] = utc_now()
    current.setdefault("content_fingerprints", {})[current["primary_state"]] = fingerprint
    for item in current.get("application_files", []):
        if item.get("path") == current["primary_state"]:
            item["fingerprint"] = fingerprint

    temporary = root / f".manifest.{os.getpid()}.{uuid.uuid4().hex}.new"
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(current, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, root / "manifest.json")
        try:
            directory = os.open(root, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError:
            pass
    finally:
        temporary.unlink(missing_ok=True)
    manifest.clear()
    manifest.update(current)


def validate_relative_path(value: str) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise ProtocolError("PATH_ESCAPE", f"Unsafe relative path: {value!r}")
    return path


def connect(
    root: Path, manifest: dict, *, busy_timeout_ms: int = 5_000
) -> sqlite3.Connection:
    database = require_beneath(
        root,
        root / validate_relative_path(manifest["primary_state"]),
        "Primary state",
    )
    connection = sqlite3.connect(
        database,
        timeout=busy_timeout_ms / 1_000,
        isolation_level=None,
    )
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute(f"PRAGMA busy_timeout={busy_timeout_ms}")
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ProtocolError("INTEGRITY_FAILURE", "SQLite integrity check failed")
        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise ProtocolError(
                "FOREIGN_KEY_VIOLATION",
                f"SQLite foreign-key check found {len(violations)} violation(s)",
            )
    except Exception:
        connection.close()
        raise
    return connection


def metadata(connection: sqlite3.Connection) -> dict[str, str]:
    return dict(connection.execute("SELECT key,value FROM metadata"))


def require_iso_timestamp(value: object, label: str) -> str:
    if not isinstance(value, str) or not ISO_TIMESTAMP_PATTERN.fullmatch(value):
        raise ProtocolError("INVALID_TIMESTAMP", f"{label} must include Z or an explicit offset")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ProtocolError("INVALID_TIMESTAMP", f"{label} is not a real ISO 8601 timestamp") from error
    offset = value[-6:] if not value.endswith("Z") else None
    if offset:
        hours, minutes = map(int, offset[1:].split(":"))
        if hours > 14 or minutes > 59 or (hours == 14 and minutes):
            raise ProtocolError("INVALID_TIMESTAMP", f"{label} has an invalid UTC offset")
    return value


def validate_protocol_record(
    value: object,
    *,
    workspace_id: str,
    label: str,
) -> dict:
    if not isinstance(value, dict):
        raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} must be a JSON object")
    if value.get("workspace_id") != workspace_id:
        raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} workspace does not match")
    if value.get("protocol_version") != PROTOCOL_VERSION:
        raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} protocol is unsupported")
    actor = value.get("actor_id")
    if not isinstance(actor, str) or not ACTOR_PATTERN.fullmatch(actor):
        raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} actor id is invalid")
    holder = value.get("holder_id")
    if not isinstance(holder, str) or not ACTOR_PATTERN.fullmatch(holder):
        raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} holder id is invalid")
    run_id = value.get("run_id")
    if run_id is not None and (
        not isinstance(run_id, str) or not RUN_ID_PATTERN.fullmatch(run_id)
    ):
        raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} run id is invalid")
    if value.get("requested_state") not in {
        "human",
        "granting_agent",
        "agent",
        "reclaim_requested",
        "recovering",
    }:
        raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} state is invalid")
    for field in ("sequence", "control_generation", "observed_revision"):
        item = value.get(field)
        if not isinstance(item, int) or isinstance(item, bool) or item < 0:
            raise ProtocolError("INVALID_COORDINATION_RECORD", f"{label} {field} is invalid")
    timestamp = require_iso_timestamp(value.get("timestamp"), f"{label} timestamp")
    normalized = timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
    if datetime.fromisoformat(normalized) > datetime.now(timezone.utc) + MAX_COORDINATION_FUTURE_SKEW:
        raise ProtocolError(
            "INVALID_COORDINATION_RECORD",
            f"{label} timestamp is untrustworthily far in the future",
        )
    return value


def verify_database_binding(
    root: Path,
    manifest: dict,
    connection: sqlite3.Connection,
) -> dict[str, str]:
    values = metadata(connection)
    if values.get("workspace_id") != manifest["workspace_id"]:
        raise ProtocolError("WORKSPACE_ID_MISMATCH", "SQLite workspace_id does not match manifest")
    if int(values.get("revision", -1)) != int(manifest["revision"]):
        raise ProtocolError("COMMIT_MARKER_MISMATCH", "SQLite revision does not match manifest")
    if int(values.get("schema_version", -1)) != int(manifest["schema_version"]):
        raise ProtocolError("SCHEMA_MISMATCH", "SQLite schema does not match manifest")
    if (
        values.get("workspace_format") != manifest["format"]
        or int(values.get("format_version", -1)) != int(manifest["format_version"])
        or int(values.get("protocol_version", -1))
        != int(manifest["protocol_version"])
    ):
        raise ProtocolError(
            "PROTOCOL_MISMATCH",
            "SQLite format or protocol does not match manifest",
        )
    state_path = validate_relative_path(manifest["primary_state"])
    database = require_beneath(root, root / state_path, "Primary state")
    actual = hashlib.sha256(database.read_bytes()).hexdigest()
    expected = manifest.get("content_fingerprints", {}).get(manifest["primary_state"])
    if not isinstance(expected, str) or actual != expected:
        raise ProtocolError(
            "DATABASE_FINGERPRINT_MISMATCH",
            "SQLite bytes do not match the manifest fingerprint",
        )
    return values


def verify_mutation(connection: sqlite3.Connection, args: argparse.Namespace) -> dict[str, str]:
    values = metadata(connection)
    if int(values["revision"]) != args.revision:
        raise ProtocolError(
            "REVISION_MISMATCH",
            f"Expected revision {args.revision}, found {values['revision']}",
        )
    if int(values["control_generation"]) != args.generation:
        raise ProtocolError("STALE_GENERATION", "Control generation no longer matches")
    if values["control_holder"] != args.actor:
        raise ProtocolError("CONTROL_NOT_HELD", f"Writer baton belongs to {values['control_holder']}")
    if values["control_state"] != "agent":
        raise ProtocolError("CONTROL_REVOKED", f"Control state is {values['control_state']}")
    return values


def canonical_request_fingerprint(args: argparse.Namespace, scope: str) -> str:
    excluded = {"workspace", "command", "revision", "idempotency_key"}
    semantic = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in vars(args).items()
        if key not in excluded
    }
    targets = {
        key: value
        for key, value in semantic.items()
        if key.endswith("_id") and key != "run_id"
    }
    request = {
        "operation": scope,
        "actor": args.actor,
        "run_id": args.run_id,
        "generation": args.generation,
        "target": targets,
        "payload": semantic,
    }
    canonical = json.dumps(
        request,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def begin_mutation(
    root: Path, manifest: dict, args: argparse.Namespace, scope: str
) -> tuple[sqlite3.Connection, dict[str, str], dict | None]:
    try:
        connection = connect(root, manifest, busy_timeout_ms=0)
        connection.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError as error:
        if "connection" in locals():
            connection.close()
        if is_sqlite_busy(error):
            raise ProtocolError(
                "MUTATION_BUSY",
                "Another mutation owns the SQLite writer lock; rerun preflight before retrying",
            ) from error
        raise ProtocolError(
            "DATABASE_WRITE_FAILED",
            f"Could not begin the SQLite mutation: {error}",
        ) from error
    try:
        values = verify_database_binding(root, manifest, connection)
        request_fingerprint = canonical_request_fingerprint(args, scope)
        prior = connection.execute(
            """SELECT i.result_id,i.actor,i.request_fingerprint,
                      o.run_id,o.generation,o.revision,o.current_turn_id,
                      o.status,o.requested_state,o.holder_id,o.sequence,o.marker_json,
                      s.marker_json AS latest_marker_json
                 FROM idempotency_keys i
                 LEFT JOIN coordination_outbox o
                   ON o.idempotency_key=i.key AND o.scope=i.scope
                 LEFT JOIN coordination_state s ON s.actor=i.actor
                WHERE i.key=? AND i.scope=?""",
            (args.idempotency_key, scope),
        ).fetchone()
        if prior:
            if prior["actor"] != args.actor:
                raise ProtocolError(
                    "IDEMPOTENCY_CONFLICT",
                    "Idempotency key belongs to another actor",
                )
            if not prior["request_fingerprint"]:
                raise ProtocolError(
                    "IDEMPOTENCY_UNBOUND",
                    "Legacy idempotency record has no canonical request fingerprint",
                )
            if prior["request_fingerprint"] != request_fingerprint:
                raise ProtocolError(
                    "IDEMPOTENCY_CONFLICT",
                    "Idempotency key was reused with a different canonical request",
                )
            return connection, values, {
                "result_id": prior["result_id"],
                "actor": prior["actor"],
                "revision": prior["revision"],
                "run_id": prior["run_id"],
                "generation": prior["generation"],
                "current_turn_id": prior["current_turn_id"],
                "status": prior["status"],
                "requested_state": prior["requested_state"],
                "holder_id": prior["holder_id"],
                "sequence": prior["sequence"],
                "marker_json": prior["marker_json"],
                "latest_marker_json": prior["latest_marker_json"],
            }
        if scope != "register":
            active_run = connection.execute(
                """SELECT id FROM agent_runs
                    WHERE id=? AND actor_id=? AND control_generation=?
                      AND status IN ('registered','watching','working','waiting')""",
                (args.run_id, args.actor, args.generation),
            ).fetchone()
            if not active_run:
                raise ProtocolError(
                    "RUN_NOT_ACTIVE",
                    "Mutation requires an active current-generation run owned by this actor",
                )
        values = verify_mutation(connection, args)
        return connection, values, None
    except Exception:
        connection.execute("ROLLBACK")
        connection.close()
        raise


def current_mailbox_sequence(root: Path, manifest: dict, actor: str) -> int:
    path = coordination_record_path(
        root,
        f"agent-{actor}.json",
        create_directory=True,
    )
    if not path.exists():
        return 0
    try:
        marker = validate_protocol_record(
            json.loads(path.read_text(encoding="utf-8")),
            workspace_id=manifest["workspace_id"],
            label="agent coordination record",
        )
    except (OSError, json.JSONDecodeError, ProtocolError):
        return 0
    return marker["sequence"]


def finish_mutation(
    root: Path,
    manifest: dict,
    connection: sqlite3.Connection,
    args: argparse.Namespace,
    scope: str,
    result_id: str,
    current_turn_id: str | None = None,
    publish_generation: int | None = None,
    requested_state: str = "agent",
    publish_status: str | None = None,
    publish_holder_id: str | None = None,
) -> int:
    request_fingerprint = canonical_request_fingerprint(args, scope)
    connection.execute(
        """INSERT INTO idempotency_keys(
             key,scope,result_id,actor,request_fingerprint,created_at
           ) VALUES(?,?,?,?,?,?)""",
        (
            args.idempotency_key,
            scope,
            result_id,
            args.actor,
            request_fingerprint,
            utc_now(),
        ),
    )
    revision = args.revision + 1
    marker_generation = (
        publish_generation if publish_generation is not None else args.generation
    )
    marker_status = publish_status or ("working" if current_turn_id else "watching")
    marker_holder = publish_holder_id or args.actor
    durable_sequence = int(
        connection.execute(
            "SELECT COALESCE(sequence,0)+1 FROM coordination_state WHERE actor=?",
            (args.actor,),
        ).fetchone()[0]
        if connection.execute(
            "SELECT 1 FROM coordination_state WHERE actor=?",
            (args.actor,),
        ).fetchone()
        else 1
    )
    mailbox_sequence = current_mailbox_sequence(root, manifest, args.actor)
    sequence = max(durable_sequence - 1, mailbox_sequence) + 1
    marker = {
        "workspace_id": manifest["workspace_id"],
        "protocol_version": PROTOCOL_VERSION,
        "actor_id": args.actor,
        "holder_id": marker_holder,
        "run_id": args.run_id,
        "sequence": sequence,
        "control_generation": marker_generation,
        "observed_revision": revision,
        "requested_state": requested_state,
        "status": marker_status,
        "current_turn_id": current_turn_id,
        "timestamp": utc_now(),
    }
    marker_json = json.dumps(marker, sort_keys=True, separators=(",", ":"))
    connection.execute(
        """INSERT INTO coordination_outbox(
             idempotency_key,scope,actor,run_id,generation,revision,
             current_turn_id,status,requested_state,holder_id,sequence,
             marker_json,created_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            args.idempotency_key,
            scope,
            args.actor,
            args.run_id,
            marker_generation,
            revision,
            current_turn_id,
            marker_status,
            requested_state,
            marker_holder,
            sequence,
            marker_json,
            utc_now(),
        ),
    )
    connection.execute(
        """INSERT INTO coordination_state(
             actor,sequence,marker_json,revision,generation,updated_at
           ) VALUES(?,?,?,?,?,?)
           ON CONFLICT(actor) DO UPDATE SET
             sequence=excluded.sequence,
             marker_json=excluded.marker_json,
             revision=excluded.revision,
             generation=excluded.generation,
             updated_at=excluded.updated_at""",
        (
            args.actor,
            sequence,
            marker_json,
            revision,
            marker_generation,
            utc_now(),
        ),
    )
    connection.execute("UPDATE metadata SET value=? WHERE key='revision'", (str(revision),))
    connection.execute("UPDATE metadata SET value=? WHERE key='updated_at'", (utc_now(),))
    connection.execute("COMMIT")
    connection.close()
    try:
        publish_manifest_revision(
            root,
            manifest,
            expected_revision=args.revision,
            committed_revision=revision,
        )
    except Exception as error:
        try:
            publish_record(
                root,
                manifest,
                actor=args.actor,
                run_id=args.run_id,
                generation=marker_generation,
                revision=revision,
                current_turn_id=current_turn_id,
                status="manifest_publication_failed",
                requested_state="recovering",
                holder_id=marker_holder,
            )
        except Exception:
            pass
        raise ProtocolError(
            "MANIFEST_PUBLICATION_FAILED",
            f"SQLite committed revision {revision}, but manifest publication failed: {error}",
        ) from error
    try:
        publish_exact_record(root, manifest, marker)
    except OSError as error:
        raise ProtocolError(
            "COORDINATION_PUBLICATION_FAILED",
            f"Revision {revision} is durable, but its coordination marker failed: {error}",
        ) from error
    return revision


def complete_idempotent_retry(
    root: Path,
    manifest: dict,
    connection: sqlite3.Connection,
    prior: dict,
    result_field: str,
    response: dict | None = None,
) -> dict:
    connection.execute("ROLLBACK")
    connection.close()
    if not all(
        prior.get(key) is not None
        for key in (
            "run_id",
            "generation",
            "revision",
            "status",
            "requested_state",
            "holder_id",
        )
    ):
        raise ProtocolError(
            "OUTBOX_MISSING",
            "Completed operation has no durable coordination outbox",
        )
    marker_json = prior.get("latest_marker_json") or prior.get("marker_json")
    if not marker_json:
        raise ProtocolError("OUTBOX_MISSING", "Completed operation has no exact marker payload")
    marker = validate_protocol_record(
        json.loads(marker_json),
        workspace_id=manifest["workspace_id"],
        label="coordination outbox marker",
    )
    publish_exact_record(root, manifest, marker)
    return {
        **(response or {}),
        result_field: prior["result_id"],
        "idempotent": True,
        "revision": prior["revision"],
    }


def command_reconcile_manifest(
    root: Path, manifest: dict, args: argparse.Namespace
) -> dict:
    connection = connect(root, manifest)
    values = metadata(connection)
    if values.get("workspace_id") != manifest["workspace_id"]:
        connection.close()
        raise ProtocolError(
            "WORKSPACE_ID_MISMATCH",
            "Reconciliation SQLite workspace_id does not match manifest",
        )
    if int(values.get("schema_version", -1)) != int(manifest["schema_version"]):
        connection.close()
        raise ProtocolError(
            "SCHEMA_MISMATCH",
            "Reconciliation SQLite schema does not match manifest",
        )
    if int(values.get("protocol_version", -1)) != int(manifest["protocol_version"]):
        connection.close()
        raise ProtocolError(
            "PROTOCOL_MISMATCH",
            "Reconciliation SQLite protocol does not match manifest",
        )
    if (
        values.get("workspace_format") != manifest["format"]
        or int(values.get("format_version", -1)) != int(manifest["format_version"])
    ):
        connection.close()
        raise ProtocolError(
            "PROTOCOL_MISMATCH",
            "Reconciliation SQLite format does not match manifest",
        )
    database_revision = int(values["revision"])
    manifest_revision = int(manifest["revision"])
    outbox = connection.execute(
        """SELECT actor,run_id,generation,revision,current_turn_id,status,
                  requested_state,holder_id,marker_json
             FROM coordination_outbox
            WHERE actor=? AND run_id=? AND revision=?
            ORDER BY created_at DESC LIMIT 1""",
        (args.actor, args.run_id, database_revision),
    ).fetchone()
    connection.close()
    if database_revision == manifest_revision:
        return {"reconciled": False, "revision": database_revision}
    if database_revision != manifest_revision + 1:
        raise ProtocolError(
            "RECONCILIATION_UNSAFE",
            "Manifest recovery requires exactly one unpublished SQLite revision",
        )
    if not outbox or not (
        outbox["actor"] == args.actor
        and outbox["run_id"] == args.run_id
        and int(outbox["revision"]) == database_revision
        and int(outbox["generation"]) == int(values["control_generation"])
        and outbox["holder_id"] == values["control_holder"]
    ):
        raise ProtocolError(
            "RECONCILIATION_UNSAFE",
            "Coordination outbox does not match durable SQLite state",
        )
    publish_manifest_revision(
        root,
        manifest,
        expected_revision=manifest_revision,
        committed_revision=database_revision,
    )
    marker = validate_protocol_record(
        json.loads(outbox["marker_json"]),
        workspace_id=manifest["workspace_id"],
        label="reconciliation outbox marker",
    )
    publish_exact_record(
        root,
        manifest,
        marker,
        replace_recovery_notice=True,
    )
    return {"reconciled": True, "revision": database_revision}


def command_preflight(root: Path, manifest: dict, _args: argparse.Namespace) -> dict:
    connection = connect(root, manifest)
    health = connection.execute("PRAGMA quick_check").fetchone()[0]
    values = verify_database_binding(root, manifest, connection)
    tables = {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    required = {"metadata", "cards", "execution_turns", "activity_events", "agent_runs"}
    connection.close()
    if health != "ok" or not required <= tables:
        raise ProtocolError("PREFLIGHT_FAILED", "Workspace schema or integrity check failed")
    if int(values["revision"]) != int(manifest["revision"]):
        raise ProtocolError(
            "COMMIT_MARKER_MISMATCH",
            "manifest.json and board.sqlite revisions disagree",
        )
    return {
        "ok": True,
        "workspace_id": manifest["workspace_id"],
        "revision": int(values["revision"]),
        "generation": int(values["control_generation"]),
        "control_state": values["control_state"],
        "control_holder": values["control_holder"],
    }


def command_status(root: Path, manifest: dict, _args: argparse.Namespace) -> dict:
    connection = connect(root, manifest)
    values = verify_database_binding(root, manifest, connection)
    turns = [
        dict(row)
        for row in connection.execute(
            """SELECT t.id,t.card_id AS card_id,t.display_number,t.status,c.title
                 FROM execution_turns t JOIN cards c ON c.id=t.card_id
                WHERE t.status IN ('queued','claimed','running','needs_input','review')
                ORDER BY t.queued_at,t.id"""
        )
    ]
    connection.close()
    if int(values["revision"]) != int(manifest["revision"]):
        raise ProtocolError(
            "COMMIT_MARKER_MISMATCH",
            "manifest.json and board.sqlite revisions disagree",
        )
    return {
        "workspace_id": values["workspace_id"],
        "revision": int(values["revision"]),
        "generation": int(values["control_generation"]),
        "control_state": values["control_state"],
        "control_holder": values["control_holder"],
        "turns": turns,
    }


def command_inspect(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection = connect(root, manifest)
    card = connection.execute(
        """SELECT id,title,description,priority,assignee,kind,attention,column_id,
                  recurring,cadence,lookback_window,current_turn_id,latest_output_id,
                  provenance,created_at,updated_at
             FROM cards WHERE id=? AND archived=0""",
        (args.card_id,),
    ).fetchone()
    if not card:
        connection.close()
        raise ProtocolError("CARD_NOT_FOUND", "Card was not found")
    result = {
        "card": dict(card),
        "plan": [
            dict(row)
            for row in connection.execute(
                "SELECT id,text,state,position FROM plan_items WHERE card_id=? ORDER BY position",
                (args.card_id,),
            )
        ],
        "turns": [
            dict(row)
            for row in connection.execute(
                """SELECT id,display_number,status,trigger,actor,instruction_snapshot,
                          linked_turn_id,result,error,queued_at,completed_at
                     FROM execution_turns WHERE card_id=? ORDER BY display_number""",
                (args.card_id,),
            )
        ],
        "outputs": [
            dict(row)
            for row in connection.execute(
                """SELECT o.id,o.type,o.title,o.status,o.source,o.current_version,
                          v.payload,v.created_at
                     FROM outputs o JOIN output_versions v
                       ON v.output_id=o.id AND v.version=o.current_version
                    WHERE o.card_id=? ORDER BY o.position""",
                (args.card_id,),
            )
        ],
        "decision": [
            dict(row)
            for row in connection.execute(
                """SELECT d.id,d.phase,d.briefing,d.selected_option_id,
                          o.title AS selected_option
                     FROM decision_threads d LEFT JOIN decision_options o
                       ON o.id=d.selected_option_id WHERE d.card_id=?""",
                (args.card_id,),
            )
        ],
        "memory": [
            dict(row)
            for row in connection.execute(
                """SELECT id,subject,summary,source,publisher,evidence_date,state,
                          relevance,coverage,gaps,last_seen,pinned
                     FROM research_memory WHERE card_id=?
                    ORDER BY pinned DESC,last_seen DESC""",
                (args.card_id,),
            )
        ],
        "activity": [
            dict(row)
            for row in connection.execute(
                """SELECT type,actor,summary,created_at FROM activity_events
                    WHERE card_id=? ORDER BY created_at DESC LIMIT 100""",
                (args.card_id,),
            )
        ],
    }
    connection.close()
    return result


def command_announce(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection = connect(root, manifest)
    values = metadata(connection)
    connection.close()
    publish_live_record(
        root,
        manifest,
        actor=args.actor,
        run_id=args.run_id,
        generation=int(values["control_generation"]),
        revision=int(values["revision"]),
        current_turn_id=None,
        status="requesting_control",
        requested_state="granting_agent",
    )
    return {
        "actor": args.actor,
        "run_id": args.run_id,
        "revision": int(values["revision"]),
        "generation": int(values["control_generation"]),
        "announced": True,
    }


def command_register(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, "register")
    if prior:
        return complete_idempotent_retry(
            root, manifest, connection, prior, "run_id"
        )
    timestamp = utc_now()
    connection.execute(
        """INSERT INTO agent_runs(
             id,actor_id,agent_name,host,status,control_generation,observed_revision,
             registered_at,heartbeat_at
           ) VALUES(?,?,?,?,?,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET
             actor_id=excluded.actor_id,
             agent_name=excluded.agent_name,
             host=excluded.host,
             status='watching',
             control_generation=excluded.control_generation,
             observed_revision=excluded.observed_revision,
             current_turn_id=NULL,
             heartbeat_at=excluded.heartbeat_at,
             stopped_at=NULL""",
        (
            args.run_id,
            args.actor,
            args.name,
            args.host,
            "watching",
            args.generation,
            args.revision,
            timestamp,
            timestamp,
        ),
    )
    revision = finish_mutation(
        root, manifest, connection, args, "register", args.run_id
    )
    return {"run_id": args.run_id, "revision": revision}


def command_heartbeat(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, "heartbeat")
    if prior:
        return complete_idempotent_retry(
            root, manifest, connection, prior, "run_id"
        )
    changed = connection.execute(
        """UPDATE agent_runs
              SET heartbeat_at=?,observed_revision=?,
                  status=CASE WHEN current_turn_id IS NULL THEN 'watching' ELSE 'working' END
            WHERE id=? AND actor_id=? AND control_generation=?""",
        (
            utc_now(),
            args.revision + 1,
            args.run_id,
            args.actor,
            args.generation,
        ),
    ).rowcount
    if not changed:
        raise ProtocolError("RUN_NOT_REGISTERED", "Register this agent run first")
    run_state = connection.execute(
        "SELECT status,current_turn_id FROM agent_runs WHERE id=? AND actor_id=?",
        (args.run_id, args.actor),
    ).fetchone()
    revision = finish_mutation(
        root,
        manifest,
        connection,
        args,
        "heartbeat",
        args.run_id,
        run_state["current_turn_id"],
        publish_status=run_state["status"],
    )
    return {"run_id": args.run_id, "revision": revision}


def command_claim(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, "claim")
    if prior:
        original = connection.execute(
            """SELECT t.card_id,t.instruction_snapshot,c.title
                 FROM execution_turns t JOIN cards c ON c.id=t.card_id
                WHERE t.id=?""",
            (prior["result_id"],),
        ).fetchone()
        if not original:
            connection.execute("ROLLBACK")
            connection.close()
            raise ProtocolError(
                "IDEMPOTENCY_RESULT_MISSING",
                "Claim result no longer exists",
            )
        return complete_idempotent_retry(
            root,
            manifest,
            connection,
            prior,
            "turn_id",
            {
                "card_id": original["card_id"],
                "title": original["title"],
                "instruction": original["instruction_snapshot"],
            },
        )
    active_run = connection.execute(
        """SELECT id FROM agent_runs
            WHERE id=? AND actor_id=? AND control_generation=?
              AND status='watching' AND current_turn_id IS NULL""",
        (args.run_id, args.actor, args.generation),
    ).fetchone()
    if not active_run:
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "RUN_NOT_ACTIVE",
            "Claim requires a watching current-generation run with no current turn",
        )
    row = connection.execute(
        """SELECT t.id,t.card_id,t.display_number,t.instruction_snapshot,c.title
             FROM execution_turns t JOIN cards c ON c.id=t.card_id
            WHERE t.status='queued' AND c.archived=0
              AND NOT EXISTS (
                SELECT 1 FROM dependencies d JOIN cards dependency
                  ON dependency.id=d.depends_on_id
                 WHERE d.card_id=c.id AND dependency.column_id<>'done'
              )
            ORDER BY t.queued_at,t.id LIMIT 1"""
    ).fetchone()
    if not row:
        connection.execute("ROLLBACK")
        connection.close()
        return {"turn_id": None, "revision": args.revision}
    changed = connection.execute(
        """UPDATE execution_turns
              SET status='claimed',actor=?,agent_run_id=?,claimed_at=?
            WHERE id=? AND status='queued'""",
        (args.actor, args.run_id, utc_now(), row["id"]),
    ).rowcount
    if changed != 1:
        raise ProtocolError("COMPETING_CLAIM", "Another agent claimed this turn")
    connection.execute(
        """UPDATE agent_runs
              SET status='working',current_turn_id=?,heartbeat_at=?,observed_revision=?
            WHERE id=? AND actor_id=?""",
        (row["id"], utc_now(), args.revision + 1, args.run_id, args.actor),
    )
    append_activity(
        connection, row["card_id"], "turn_claimed", args.actor,
        f"Turn {row['display_number']} claimed."
    )
    revision = finish_mutation(
        root, manifest, connection, args, "claim", row["id"], row["id"]
    )
    return {
        "turn_id": row["id"],
        "card_id": row["card_id"],
        "title": row["title"],
        "instruction": row["instruction_snapshot"],
        "revision": revision,
    }


def command_start(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    return transition(root, manifest, args, "running")


def command_resume(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, "resume")
    if prior:
        original = connection.execute(
            "SELECT card_id,instruction_snapshot FROM execution_turns WHERE id=?",
            (prior["result_id"],),
        ).fetchone()
        answers = [
            dict(row)
            for row in connection.execute(
                """SELECT q.id AS question_id,q.question,a.answer,
                          a.created_at AS answered_at
                     FROM agent_questions q
                     JOIN agent_answers a ON a.question_id=q.id
                    WHERE q.turn_id=? AND q.status='answered'
                    ORDER BY a.created_at,q.id""",
                (prior["result_id"],),
            )
        ]
        if not original:
            connection.execute("ROLLBACK")
            connection.close()
            raise ProtocolError(
                "IDEMPOTENCY_RESULT_MISSING",
                "Resume result no longer exists",
            )
        return complete_idempotent_retry(
            root,
            manifest,
            connection,
            prior,
            "turn_id",
            {
                "card_id": original["card_id"],
                "instruction": original["instruction_snapshot"],
                "answers": answers,
            },
        )
    turn = connection.execute(
        """SELECT id,card_id,display_number,status,instruction_snapshot FROM execution_turns
            WHERE id=?""",
        (args.turn_id,),
    ).fetchone()
    if not turn or turn["status"] != "needs_input":
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "TURN_NOT_WAITING",
            "Resume requires a needs_input turn",
        )
    open_question = connection.execute(
        "SELECT 1 FROM agent_questions WHERE turn_id=? AND status='open' LIMIT 1",
        (turn["id"],),
    ).fetchone()
    answers = [
        dict(row)
        for row in connection.execute(
            """SELECT q.id AS question_id,q.question,a.answer,
                      a.created_at AS answered_at
                 FROM agent_questions q
                 JOIN agent_answers a ON a.question_id=q.id
                WHERE q.turn_id=? AND q.status='answered'
                ORDER BY a.created_at,q.id""",
            (turn["id"],),
        )
    ]
    if open_question or not answers:
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "ANSWER_REQUIRED",
            "Resume requires durable answers for every open question",
        )
    timestamp = utc_now()
    connection.execute(
        """UPDATE execution_turns
              SET status='running',actor=?,agent_run_id=?,resumed_at=?
            WHERE id=? AND status='needs_input'""",
        (args.actor, args.run_id, timestamp, turn["id"]),
    )
    connection.execute(
        """UPDATE cards SET current_turn_id=?,attention='ai_working',
                  updated_at=?,last_change_actor=? WHERE id=?""",
        (turn["id"], timestamp, args.actor, turn["card_id"]),
    )
    connection.execute(
        """UPDATE agent_runs
              SET status='working',control_generation=?,current_turn_id=?,
                  heartbeat_at=?,observed_revision=?
            WHERE id=? AND actor_id=?""",
        (
            args.generation,
            turn["id"],
            timestamp,
            args.revision + 1,
            args.run_id,
            args.actor,
        ),
    )
    append_activity(
        connection,
        turn["card_id"],
        "turn_resumed",
        args.actor,
        f"Turn {turn['display_number']} resumed with durable human answer.",
    )
    revision = finish_mutation(
        root,
        manifest,
        connection,
        args,
        "resume",
        turn["id"],
        turn["id"],
        publish_status="working",
    )
    return {
        "turn_id": turn["id"],
        "card_id": turn["card_id"],
        "instruction": turn["instruction_snapshot"],
        "answers": answers,
        "revision": revision,
    }


def command_checkpoint(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, "checkpoint")
    if prior:
        return complete_idempotent_retry(
            root, manifest, connection, prior, "checkpoint_id"
        )
    turn = owned_turn(connection, args)
    if turn["status"] in TERMINAL_STATUSES:
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "TURN_IMMUTABLE",
            f"Cannot checkpoint an immutable {turn['status']} turn",
        )
    checkpoint_id = str(uuid.uuid4())
    connection.execute(
        """INSERT INTO turn_checkpoints(id,turn_id,kind,summary,progress,created_at)
           VALUES(?,?,?,?,?,?)""",
        (
            checkpoint_id,
            turn["id"],
            args.kind,
            args.summary,
            args.progress,
            utc_now(),
        ),
    )
    append_activity(
        connection, turn["card_id"], "turn_checkpoint", args.actor, args.summary
    )
    revision = finish_mutation(
        root, manifest, connection, args, "checkpoint", checkpoint_id, turn["id"]
    )
    return {"checkpoint_id": checkpoint_id, "revision": revision}


def command_output(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    if not args.title.strip() or len(args.title.strip()) > 200:
        raise ProtocolError("VALIDATION_ERROR", "Output title must be 1-200 characters")
    if len(args.content) > 1_000_000:
        raise ProtocolError("VALIDATION_ERROR", "Output content exceeds 1000000 characters")
    connection, _, prior = begin_mutation(root, manifest, args, "output")
    if prior:
        return complete_idempotent_retry(
            root, manifest, connection, prior, "output_id"
        )
    turn = owned_turn(connection, args)
    if turn["status"] in TERMINAL_STATUSES:
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "TURN_IMMUTABLE",
            f"Cannot add output to an immutable {turn['status']} turn",
        )
    output_id = str(uuid.uuid4())
    version_id = str(uuid.uuid4())
    timestamp = utc_now()
    position = connection.execute(
        "SELECT COALESCE(MAX(position),0)+1024 FROM outputs WHERE card_id=?",
        (turn["card_id"],),
    ).fetchone()[0]
    connection.execute(
        """INSERT INTO outputs(
             id,card_id,turn_id,position,type,title,owner,status,source,lineage,
             created_at,updated_at,current_version
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1)""",
        (
            output_id,
            turn["card_id"],
            turn["id"],
            position,
            args.type,
            args.title,
            args.actor,
            args.status,
            "agent",
            "[]",
            timestamp,
            timestamp,
        ),
    )
    connection.execute(
        """INSERT INTO output_versions(
             id,output_id,version,title,payload,status,source,created_at
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (
            version_id,
            output_id,
            1,
            args.title,
            args.content,
            args.status,
            "agent",
            timestamp,
        ),
    )
    connection.execute(
        """INSERT INTO output_surfaces(
             id,output_version_id,type,title,payload,reference,schema_version,
             alt_text,created_at
           ) VALUES(?,?,?,?,?,?,1,?,?)""",
        (
            str(uuid.uuid4()),
            version_id,
            args.type,
            args.title,
            args.content,
            args.reference,
            args.alt_text,
            timestamp,
        ),
    )
    if args.status in ("complete", "approved"):
        connection.execute(
            """UPDATE cards SET latest_output_id=?,
                   latest_successful_output_version_id=?,attention='ai_updated',
                   updated_at=?,last_change_actor=? WHERE id=?""",
            (output_id, version_id, timestamp, args.actor, turn["card_id"]),
        )
    append_activity(
        connection,
        turn["card_id"],
        "output_created",
        args.actor,
        f"Output added: {args.title}",
    )
    revision = finish_mutation(
        root, manifest, connection, args, "output", output_id, turn["id"]
    )
    return {"output_id": output_id, "revision": revision}


def command_ask(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, "ask")
    if prior:
        return complete_idempotent_retry(
            root, manifest, connection, prior, "question_id"
        )
    turn = owned_turn(connection, args)
    if turn["status"] != "running":
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "TURN_NOT_RUNNING",
            f"Cannot ask for input from an immutable {turn['status']} turn",
        )
    question_id = str(uuid.uuid4())
    timestamp = utc_now()
    connection.execute(
        """INSERT INTO agent_questions(id,turn_id,question,context,status,created_at)
           VALUES(?,?,?,?,?,?)""",
        (question_id, turn["id"], args.question, args.context, "open", timestamp),
    )
    connection.execute(
        "UPDATE execution_turns SET status='needs_input',input_requested_at=? WHERE id=?",
        (timestamp, turn["id"]),
    )
    connection.execute(
        "UPDATE cards SET attention='needs_you',updated_at=? WHERE id=?",
        (timestamp, turn["card_id"]),
    )
    connection.execute(
        """UPDATE agent_runs
              SET status='waiting',current_turn_id=?,heartbeat_at=?,observed_revision=?
            WHERE id=? AND actor_id=?""",
        (
            turn["id"],
            timestamp,
            args.revision + 1,
            args.run_id,
            args.actor,
        ),
    )
    append_activity(
        connection, turn["card_id"], "turn_needs_input", args.actor,
        "Agent asked a focused question."
    )
    revision = finish_mutation(
        root, manifest, connection, args, "ask", question_id, turn["id"]
    )
    return {"question_id": question_id, "revision": revision}


def command_complete(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    return transition(root, manifest, args, "complete")


def command_review(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    return transition(root, manifest, args, "review")


def command_fail(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    return transition(root, manifest, args, "failed")


def command_cancel(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    return transition(root, manifest, args, "cancelled")


def command_yield(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, "yield")
    if prior:
        return complete_idempotent_retry(
            root, manifest, connection, prior, "run_id"
        )
    active_run = connection.execute(
        """SELECT id FROM agent_runs
            WHERE id=? AND actor_id=?
              AND status IN ('registered','watching','working','waiting')""",
        (args.run_id, args.actor),
    ).fetchone()
    if not active_run:
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "RUN_NOT_ACTIVE",
            "Yield requires an active run owned by this actor",
        )
    connection.execute(
        """UPDATE agent_runs
              SET status='stopped',current_turn_id=NULL,stopped_at=?,heartbeat_at=?
            WHERE id=?""",
        (utc_now(), utc_now(), args.run_id),
    )
    next_generation = args.generation + 1
    connection.execute("UPDATE metadata SET value='human' WHERE key='control_state'")
    connection.execute("UPDATE metadata SET value='human' WHERE key='control_holder'")
    connection.execute(
        "UPDATE metadata SET value=? WHERE key='control_generation'",
        (str(next_generation),),
    )
    connection.execute("UPDATE metadata SET value='' WHERE key='control_lease_until'")
    revision = finish_mutation(
        root,
        manifest,
        connection,
        args,
        "yield",
        args.run_id,
        publish_generation=next_generation,
        requested_state="human",
        publish_status="stopped",
        publish_holder_id="human",
    )
    return {"run_id": args.run_id, "revision": revision, "generation": next_generation}


def transition(
    root: Path, manifest: dict, args: argparse.Namespace, target: str
) -> dict:
    connection, _, prior = begin_mutation(root, manifest, args, f"turn_{target}")
    if prior:
        return complete_idempotent_retry(
            root, manifest, connection, prior, "turn_id"
        )
    turn = owned_turn(connection, args)
    allowed = {
        "running": ("claimed",),
        "review": ("running",),
        "complete": ("running", "review"),
        "failed": ("claimed", "running"),
        "cancelled": ("claimed", "running", "needs_input", "review"),
    }
    if turn["status"] not in allowed[target]:
        raise ProtocolError(
            "INVALID_TURN_TRANSITION",
            f"Cannot change {turn['status']} to {target}",
        )
    decision = connection.execute(
        "SELECT id FROM decision_threads WHERE card_id=?",
        (turn["card_id"],),
    ).fetchone()
    if target == "complete" and decision:
        connection.execute("ROLLBACK")
        connection.close()
        raise ProtocolError(
            "DECISION_ACCEPTANCE_REQUIRED",
            "Decision turns must enter review and complete through acceptance",
        )
    timestamp_column = {
        "running": "started_at",
        "review": "reviewed_at",
        "complete": "completed_at",
        "failed": "failed_at",
        "cancelled": "cancelled_at",
    }[target]
    fields = ["status=?", f"{timestamp_column}=?"]
    values: list[object] = [target, utc_now()]
    for attribute, column in (
        ("result", "result"),
        ("error", "error"),
        ("reason", "cancellation_reason"),
    ):
        if hasattr(args, attribute):
            fields.append(f"{column}=?")
            values.append(getattr(args, attribute))
    values.append(turn["id"])
    connection.execute(
        f"UPDATE execution_turns SET {','.join(fields)} WHERE id=?",
        values,
    )
    terminal = target in TERMINAL_STATUSES
    if terminal:
        connection.execute(
            """UPDATE agent_questions SET status='withdrawn'
                WHERE turn_id=? AND status='open'""",
            (turn["id"],),
        )
    attention = "ai_updated" if target in ("review", "complete") else "needs_you" if terminal else "ai_working"
    connection.execute(
        """UPDATE cards SET current_turn_id=?,attention=?,updated_at=?,last_change_actor=?
            WHERE id=?""",
        (None if terminal else turn["id"], attention, utc_now(), args.actor, turn["card_id"]),
    )
    connection.execute(
        """UPDATE agent_runs
              SET status=?,current_turn_id=?,heartbeat_at=?,observed_revision=?
            WHERE id=? AND actor_id=?""",
        (
            "watching" if terminal else "working",
            None if terminal else turn["id"],
            utc_now(),
            args.revision + 1,
            args.run_id,
            args.actor,
        ),
    )
    if target == "review":
        position = connection.execute(
            "SELECT COALESCE(MAX(position),0)+1024 FROM cards WHERE column_id='review'"
        ).fetchone()[0]
        connection.execute(
            "UPDATE cards SET column_id='review',position=? WHERE id=?",
            (position, turn["card_id"]),
        )
        connection.execute(
            "UPDATE decision_threads SET phase='review',updated_at=? WHERE card_id=?",
            (utc_now(), turn["card_id"]),
        )
    if target == "complete":
        position = connection.execute(
            "SELECT COALESCE(MAX(position),0)+1024 FROM cards WHERE column_id='review'"
        ).fetchone()[0]
        connection.execute(
            "UPDATE cards SET column_id='review',position=? WHERE id=?",
            (position, turn["card_id"]),
        )
        connection.execute(
            "UPDATE decision_threads SET phase='review',updated_at=? WHERE card_id=?",
            (utc_now(), turn["card_id"]),
        )
    if target == "failed":
        position = connection.execute(
            "SELECT COALESCE(MAX(position),0)+1024 FROM cards WHERE column_id='blocked'"
        ).fetchone()[0]
        connection.execute(
            "UPDATE cards SET column_id='blocked',position=? WHERE id=?",
            (position, turn["card_id"]),
        )
    append_activity(
        connection, turn["card_id"], f"turn_{target}", args.actor,
        f"Turn {turn['display_number']} {target}."
    )
    revision = finish_mutation(
        root,
        manifest,
        connection,
        args,
        f"turn_{target}",
        turn["id"],
        None if terminal else turn["id"],
    )
    return {"turn_id": turn["id"], "revision": revision}


def command_watch(root: Path, manifest: dict, args: argparse.Namespace) -> dict:
    delay = 1.0
    while True:
        status = command_status(root, manifest, args)
        if status["generation"] != args.generation:
            return {"stopped": True, "reason": "stale_generation", **status}
        human_path = coordination_record_path(
            root,
            "human.json",
            create_directory=False,
        )
        if human_path.is_file():
            try:
                human = validate_protocol_record(
                    json.loads(human_path.read_text(encoding="utf-8")),
                    workspace_id=manifest["workspace_id"],
                    label="human coordination record",
                )
            except (OSError, json.JSONDecodeError, ProtocolError):
                human = None
            if (
                human
                and
                human.get("workspace_id") == manifest["workspace_id"]
                and human.get("requested_state") == "reclaim_requested"
                and int(human.get("control_generation", -1)) == args.generation
            ):
                return {"stopped": True, "reason": "human_reclaim_requested"}
        if status["control_state"] != "agent" or status["control_holder"] != args.actor:
            return {"stopped": True, "reason": "control_revoked", **status}
        connection = connect(root, manifest)
        run_state = connection.execute(
            """SELECT status,current_turn_id FROM agent_runs
                WHERE id=? AND actor_id=? AND control_generation=?
                  AND status IN ('registered','watching','working','waiting')""",
            (args.run_id, args.actor, args.generation),
        ).fetchone()
        connection.close()
        if not run_state:
            return {"stopped": True, "reason": "run_not_active", **status}
        publish_live_record(
            root,
            manifest,
            actor=args.actor,
            run_id=args.run_id,
            generation=args.generation,
            revision=status["revision"],
            current_turn_id=run_state["current_turn_id"],
            status=run_state["status"],
        )
        queued = [turn for turn in status["turns"] if turn["status"] == "queued"]
        if queued or args.once:
            return {"ready": bool(queued), **status}
        time.sleep(delay)
        delay = min(delay * 1.6, 15.0)


def owned_turn(connection: sqlite3.Connection, args: argparse.Namespace) -> sqlite3.Row:
    row = connection.execute(
        """SELECT id,card_id,display_number,status FROM execution_turns
            WHERE id=? AND actor=? AND agent_run_id=?""",
        (args.turn_id, args.actor, args.run_id),
    ).fetchone()
    if not row:
        raise ProtocolError("TURN_NOT_OWNED", "Turn is not owned by this agent run")
    return row


def append_activity(
    connection: sqlite3.Connection,
    card_id: str | None,
    event_type: str,
    actor: str,
    summary: str,
) -> None:
    connection.execute(
        """INSERT INTO activity_events(id,card_id,type,actor,summary,payload,created_at)
           VALUES(?,?,?,?,?,'{}',?)""",
        (str(uuid.uuid4()), card_id, event_type, actor, summary, utc_now()),
    )


def publish_exact_record(
    root: Path,
    manifest: dict,
    marker: dict,
    *,
    replace_recovery_notice: bool = False,
) -> None:
    marker = validate_protocol_record(
        marker,
        workspace_id=manifest["workspace_id"],
        label="durable coordination marker",
    )
    actor = marker["actor_id"]
    path = coordination_record_path(
        root,
        f"agent-{actor}.json",
        create_directory=True,
    )
    if path.exists():
        try:
            current = validate_protocol_record(
                json.loads(path.read_text(encoding="utf-8")),
                workspace_id=manifest["workspace_id"],
                label="agent coordination record",
            )
        except (OSError, json.JSONDecodeError, ProtocolError):
            current = None
        if current and not (
            replace_recovery_notice
            and current.get("status") == "manifest_publication_failed"
            and current["sequence"] == marker["sequence"]
        ) and (
            current["sequence"] > marker["sequence"]
            or (
                current["sequence"] == marker["sequence"]
                and (
                    current["control_generation"] > marker["control_generation"]
                    or current["observed_revision"] >= marker["observed_revision"]
                )
            )
        ):
            return
    coordination = coordination_directory(root, create=True)
    temporary = coordination / f".agent-{actor}.{os.getpid()}.{uuid.uuid4().hex}.new"
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(marker, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        require_beneath(root, temporary, "Temporary coordination record")
        if path.is_symlink():
            raise ProtocolError("PATH_ESCAPE", "Coordination record became a symlink")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def publish_record(
    root: Path,
    manifest: dict,
    *,
    actor: str,
    run_id: str,
    generation: int,
    revision: int,
    current_turn_id: str | None,
    status: str,
    requested_state: str = "agent",
    holder_id: str | None = None,
) -> None:
    if not ACTOR_PATTERN.fullmatch(actor):
        raise ProtocolError("INVALID_ACTOR", "Actor id is invalid")
    coordination = coordination_directory(root, create=True)
    path = coordination_record_path(
        root,
        f"agent-{actor}.json",
        create_directory=True,
    )
    previous_sequence = 0
    if path.exists():
        try:
            existing = validate_protocol_record(
                json.loads(path.read_text(encoding="utf-8")),
                workspace_id=manifest["workspace_id"],
                label="agent coordination record",
            )
            previous_sequence = existing["sequence"]
        except (OSError, json.JSONDecodeError, ProtocolError):
            previous_sequence = 0
    record = {
        "workspace_id": manifest["workspace_id"],
        "protocol_version": PROTOCOL_VERSION,
        "actor_id": actor,
        "holder_id": holder_id or actor,
        "run_id": run_id,
        "sequence": previous_sequence + 1,
        "control_generation": generation,
        "observed_revision": revision,
        "requested_state": requested_state,
        "status": status,
        "current_turn_id": current_turn_id,
        "timestamp": utc_now(),
    }
    temporary = coordination / f".agent-{actor}.{os.getpid()}.new"
    require_beneath(root, coordination, "Coordination directory")
    if temporary.is_symlink():
        raise ProtocolError("PATH_ESCAPE", "Temporary coordination path is a symlink")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        require_beneath(root, temporary, "Temporary coordination record")
        if path.is_symlink():
            raise ProtocolError("PATH_ESCAPE", "Coordination record became a symlink")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def publish_live_record(*args, **kwargs) -> None:
    try:
        publish_record(*args, **kwargs)
    except OSError as error:
        raise ProtocolError(
            "COORDINATION_PUBLICATION_FAILED",
            f"Coordination heartbeat publication failed: {error}",
        ) from error


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def non_negative_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected a non-negative integer") from error
    if number < 0:
        raise argparse.ArgumentTypeError("expected a non-negative integer")
    return number


def add_protocol_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--actor", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--revision", required=True, type=non_negative_integer)
    parser.add_argument("--generation", required=True, type=non_negative_integer)
    parser.add_argument("--idempotency-key", required=True)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cooperative AI Kanban workspace agent CLI.",
        epilog=(
            "Every mutation verifies revision, control generation, holder, run id, "
            "and idempotency before writing. JSON is printed to stdout."
        ),
    )
    parser.add_argument("--workspace", default=".", help="Board Workspace folder (default: .)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("preflight", help="Validate manifest, database, and protocol.")
    commands.add_parser("status", help="Show control state and active turns.")

    inspect = commands.add_parser("inspect", help="Inspect one card and its durable history.")
    inspect.add_argument("--card-id", required=True)

    announce = commands.add_parser("announce", help="Publish identity before requesting control.")
    announce.add_argument("--actor", required=True)
    announce.add_argument("--run-id", required=True)

    reconcile = commands.add_parser(
        "reconcile-manifest",
        help="Republish one verified SQLite commit after manifest publication failed.",
    )
    reconcile.add_argument("--actor", required=True)
    reconcile.add_argument("--run-id", required=True)

    register = commands.add_parser("register", help="Register an approved agent run.")
    add_protocol_arguments(register)
    register.add_argument("--name", required=True)
    register.add_argument("--host", required=True)

    heartbeat = commands.add_parser("heartbeat", help="Publish a durable heartbeat.")
    add_protocol_arguments(heartbeat)

    claim = commands.add_parser("claim", help="Atomically claim one dependency-ready turn.")
    add_protocol_arguments(claim)

    start = commands.add_parser("start", help="Mark a claimed turn running.")
    add_protocol_arguments(start)
    start.add_argument("--turn-id", required=True)

    resume = commands.add_parser(
        "resume",
        help="Atomically adopt an answered needs-input turn into this run.",
    )
    add_protocol_arguments(resume)
    resume.add_argument("--turn-id", required=True)

    checkpoint = commands.add_parser("checkpoint", help="Publish a short progress checkpoint.")
    add_protocol_arguments(checkpoint)
    checkpoint.add_argument("--turn-id", required=True)
    checkpoint.add_argument("--kind", choices=("progress", "output", "warning", "error"), default="progress")
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--progress", type=int, choices=range(0, 101), default=None)

    output = commands.add_parser("output", help="Publish a typed output for an owned turn.")
    add_protocol_arguments(output)
    output.add_argument("--turn-id", required=True)
    output.add_argument(
        "--type",
        choices=("text", "status", "link", "program", "table", "diff", "image", "file"),
        default="text",
    )
    output.add_argument("--title", required=True)
    output.add_argument("--content", required=True)
    output.add_argument(
        "--status",
        choices=("draft", "streaming", "complete", "failed", "stale", "superseded", "approved"),
        default="complete",
    )
    output.add_argument("--reference", default="")
    output.add_argument("--alt-text", default="")

    ask = commands.add_parser("ask", help="Pause and ask one focused question.")
    add_protocol_arguments(ask)
    ask.add_argument("--turn-id", required=True)
    ask.add_argument("--question", required=True)
    ask.add_argument("--context", default="")

    complete = commands.add_parser("complete", help="Complete a turn with a result.")
    add_protocol_arguments(complete)
    complete.add_argument("--turn-id", required=True)
    complete.add_argument("--result", required=True)

    review = commands.add_parser("review", help="Submit a running decision turn for human review.")
    add_protocol_arguments(review)
    review.add_argument("--turn-id", required=True)
    review.add_argument("--result", required=True)

    fail = commands.add_parser("fail", help="Fail a turn while retaining partial outputs.")
    add_protocol_arguments(fail)
    fail.add_argument("--turn-id", required=True)
    fail.add_argument("--error", required=True)

    cancel = commands.add_parser("cancel", help="Cancel a turn while retaining partial outputs.")
    add_protocol_arguments(cancel)
    cancel.add_argument("--turn-id", required=True)
    cancel.add_argument("--reason", required=True)

    yield_parser = commands.add_parser("yield", help="Stop this run and return to the host.")
    add_protocol_arguments(yield_parser)

    watch = commands.add_parser("watch", help="Poll quietly with bounded backoff until work or revocation.")
    watch.add_argument("--actor", required=True)
    watch.add_argument("--run-id", required=True)
    watch.add_argument("--generation", required=True, type=non_negative_integer)
    watch.add_argument("--once", action="store_true")
    return parser


COMMANDS = {
    "preflight": command_preflight,
    "status": command_status,
    "inspect": command_inspect,
    "announce": command_announce,
    "reconcile-manifest": command_reconcile_manifest,
    "register": command_register,
    "heartbeat": command_heartbeat,
    "claim": command_claim,
    "start": command_start,
    "resume": command_resume,
    "checkpoint": command_checkpoint,
    "output": command_output,
    "ask": command_ask,
    "complete": command_complete,
    "review": command_review,
    "fail": command_fail,
    "cancel": command_cancel,
    "yield": command_yield,
    "watch": command_watch,
}


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        if hasattr(args, "actor") and not ACTOR_PATTERN.fullmatch(args.actor):
            raise ProtocolError("INVALID_ACTOR", "Actor id is invalid")
        if hasattr(args, "run_id") and not RUN_ID_PATTERN.fullmatch(args.run_id):
            raise ProtocolError("INVALID_RUN_ID", "Run id is invalid or not portable")
        root = workspace_root(args.workspace)
        manifest = load_manifest(root)
        result = COMMANDS[args.command](root, manifest, args)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except ProtocolError as error:
        print(json.dumps({"ok": False, "code": error.code, "error": str(error)}), file=sys.stderr)
        return 2
    except sqlite3.OperationalError as error:
        code = "MUTATION_BUSY" if is_sqlite_busy(error) else "SQLITE_ERROR"
        print(json.dumps({"ok": False, "code": code, "error": str(error)}), file=sys.stderr)
        return 2 if code == "MUTATION_BUSY" else 3
    except sqlite3.Error as error:
        print(json.dumps({"ok": False, "code": "SQLITE_ERROR", "error": str(error)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
