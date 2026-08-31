from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any


class RuntimeMessageError(ValueError):
    """Raised when runtime message payloads do not satisfy the protocol contract."""


@dataclass(slots=True)
class RuntimeMessage:
    """Standard runtime message envelope for Qt and Web coordination."""

    message_type: str
    source: str
    target: str
    payload: dict[str, Any] = field(default_factory=dict)
    request_id: str = ""
    schema_version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the message into a JSON-friendly dictionary."""

        return asdict(self)

    def to_json(self) -> str:
        """Serialize the message into a JSON string."""

        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> RuntimeMessage:
        """Build a runtime message from a mapping and validate required fields."""

        if not isinstance(payload, Mapping):
            raise RuntimeMessageError("Runtime message must be a JSON object.")

        message_type = str(payload.get("message_type", "")).strip()
        source = str(payload.get("source", "")).strip()
        target = str(payload.get("target", "")).strip()
        request_id = str(payload.get("request_id", "")).strip()
        schema_version = str(payload.get("schema_version", "1.0")).strip() or "1.0"
        message_payload = payload.get("payload", {})

        if not message_type:
            raise RuntimeMessageError("Runtime message_type is required.")
        if not source:
            raise RuntimeMessageError("Runtime message source is required.")
        if not target:
            raise RuntimeMessageError("Runtime message target is required.")
        if not isinstance(message_payload, dict):
            raise RuntimeMessageError("Runtime message payload must be an object.")

        return cls(
            message_type=message_type,
            source=source,
            target=target,
            payload=dict(message_payload),
            request_id=request_id,
            schema_version=schema_version,
        )

    @classmethod
    def from_json(cls, payload: str) -> RuntimeMessage:
        """Build a runtime message from a JSON string."""

        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeMessageError("Runtime message JSON is invalid.") from exc
        return cls.from_dict(parsed)
