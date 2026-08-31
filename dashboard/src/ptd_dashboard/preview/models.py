from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DashboardPreview:
    """Represent a dashboard-friendly preview model derived from tool output."""

    tool_id: str
    tool_name: str
    status: str
    message: str
    record_type: str
    summary: str
    payload: dict[str, Any]
    artifacts: tuple[dict[str, Any], ...]
    errors: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert the preview model into a JSON-friendly object."""

        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "status": self.status,
            "message": self.message,
            "record_type": self.record_type,
            "summary": self.summary,
            "payload": self.payload,
            "artifacts": list(self.artifacts),
            "errors": list(self.errors),
        }
