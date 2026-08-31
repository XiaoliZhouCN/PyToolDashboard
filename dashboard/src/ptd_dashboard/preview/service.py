from __future__ import annotations

from typing import Any

from ptd_dashboard.preview.models import DashboardPreview
from ptd_dashboard.registry.models import ToolManifest


def adapt_preview_response(
    manifest: ToolManifest,
    response: dict[str, Any],
) -> DashboardPreview:
    """Adapt a tool preview response into a dashboard-friendly preview model."""

    payload = _as_dict(response.get("payload"))
    artifacts = _as_sequence_of_dicts(response.get("artifacts"))
    errors = _as_sequence_of_dicts(response.get("errors"))
    record_type = str(payload.get("record_type", "preview.unknown"))
    summary = _build_summary(record_type=record_type, payload=payload, message=str(response.get("message", "")))

    return DashboardPreview(
        tool_id=manifest.tool_id,
        tool_name=manifest.name,
        status=str(response.get("status", "unknown")),
        message=str(response.get("message", "")),
        record_type=record_type,
        summary=summary,
        payload=payload,
        artifacts=artifacts,
        errors=errors,
    )


def _build_summary(
    *,
    record_type: str,
    payload: dict[str, Any],
    message: str,
) -> str:
    if record_type == "preview.mermaid_document":
        diagram_count = payload.get("diagram_count", 0)
        document_path = payload.get("document_path", "")
        return f"{diagram_count} Mermaid diagram(s) from {document_path}"
    if message:
        return message
    return record_type


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _as_sequence_of_dicts(value: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, dict))
