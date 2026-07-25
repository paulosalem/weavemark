"""Versioned bidirectional JSONL interactions over subprocess stdin."""

from __future__ import annotations

import json
import queue
import sys
import threading
import uuid
from collections.abc import Callable
from typing import Any, TextIO, cast

from .protection import ApprovalDecision, ProtectionRequest

INTERACTION_PROTOCOL_VERSION = 1
_DECISIONS = {
    "allow_once",
    "allow_remember",
    "deny_once",
    "deny_remember",
}

EventEmitter = Callable[[str, dict[str, Any], str | None], None]


class JsonlStdinInteraction:
    """Request scoped decisions through JSONL responses read from stdin."""

    def __init__(
        self,
        emit: EventEmitter,
        *,
        stream: TextIO | None = None,
        timeout_seconds: float = 300.0,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._emit = emit
        self._stream = stream or sys.stdin
        self._timeout_seconds = timeout_seconds
        self._id_factory = id_factory or (lambda: str(uuid.uuid4()))
        self._messages: queue.Queue[dict[str, Any] | BaseException | None] = (
            queue.Queue()
        )
        threading.Thread(target=self._read_messages, daemon=True).start()

    def request_protection(self, request: ProtectionRequest) -> ApprovalDecision:
        """Emit one protection request and wait for its exact response."""

        request_id = self._id_factory()
        self._emit(
            "protection_request",
            {
                "version": INTERACTION_PROTOCOL_VERSION,
                "request_id": request_id,
                "capability": request.capability,
                "subject": request.subject,
                "fingerprint": request.fingerprint,
                "reason": request.reason,
                "danger": request.danger,
                "config_key": request.config_key,
                "decisions": sorted(_DECISIONS),
            },
            "interaction",
        )
        try:
            message = self._messages.get(timeout=self._timeout_seconds)
            decision = self._validate_response(message, request_id)
        except (ValueError, queue.Empty) as exc:
            reason = (
                "Timed out waiting for an interaction response."
                if isinstance(exc, queue.Empty)
                else str(exc)
            )
            self._emit(
                "interaction_failed",
                {
                    "version": INTERACTION_PROTOCOL_VERSION,
                    "request_id": request_id,
                    "error": reason,
                },
                "interaction",
            )
            return "deny_once"
        self._emit(
            "interaction_resolved",
            {
                "version": INTERACTION_PROTOCOL_VERSION,
                "request_id": request_id,
                "decision": decision,
            },
            "interaction",
        )
        return decision

    def _read_messages(self) -> None:
        try:
            for line in self._stream:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except (json.JSONDecodeError, UnicodeError) as exc:
                    self._messages.put(exc)
                    continue
                if not isinstance(payload, dict):
                    self._messages.put(ValueError("Interaction response must be an object."))
                    continue
                self._messages.put(payload)
        except (OSError, UnicodeError) as exc:
            self._messages.put(exc)
        finally:
            self._messages.put(None)

    @staticmethod
    def _validate_response(
        message: dict[str, Any] | BaseException | None,
        request_id: str,
    ) -> ApprovalDecision:
        if message is None:
            raise ValueError("Interaction stdin closed before a response arrived.")
        if isinstance(message, BaseException):
            raise ValueError(f"Invalid interaction response: {message}") from message
        if message.get("version") != INTERACTION_PROTOCOL_VERSION:
            raise ValueError("Unsupported interaction protocol version.")
        if message.get("type") != "protection_response":
            raise ValueError("Expected a protection_response interaction.")
        if message.get("request_id") != request_id:
            raise ValueError("Interaction response request ID does not match.")
        decision = message.get("decision")
        if decision not in _DECISIONS:
            raise ValueError(f"Unknown protection decision: {decision}")
        return cast(ApprovalDecision, decision)


__all__ = ["INTERACTION_PROTOCOL_VERSION", "JsonlStdinInteraction"]
