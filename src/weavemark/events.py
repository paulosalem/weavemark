"""Structured JSONL lifecycle events for subprocess and GUI consumers."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any, TextIO


class EventJsonlWriter:
    """Write ordered, flushed event records to a JSON Lines stream."""

    def __init__(self, target: Path | str) -> None:
        self._sequence = 0
        self._lock = Lock()
        self._disabled = False
        self._owns_stream = str(target) != "-"
        if self._owns_stream:
            path = Path(target).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            self._stream: TextIO = path.open("w", encoding="utf-8")
            if os.name != "nt":
                path.chmod(0o600)
        else:
            self._stream = sys.stdout

    def emit(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        *,
        phase: str | None = None,
    ) -> None:
        """Append one event and flush it immediately."""

        with self._lock:
            if self._disabled:
                return
            self._sequence += 1
            record: dict[str, Any] = {
                "timestamp": datetime.now(UTC).isoformat(),
                "sequence": self._sequence,
                "type": event_type,
                "data": data or {},
            }
            if phase is not None:
                record["phase"] = phase
            try:
                self._stream.write(
                    json.dumps(record, ensure_ascii=False, default=str) + "\n"
                )
                self._stream.flush()
            except OSError:
                self._disabled = True

    def close(self) -> None:
        """Close an owned file stream."""

        if self._owns_stream:
            try:
                self._stream.close()
            except OSError:
                self._disabled = True

    def __enter__(self) -> EventJsonlWriter:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


__all__ = ["EventJsonlWriter"]
