from __future__ import annotations

from typing import Any

from ptd_tool_mermaid_editor.protocols.messages import RuntimeMessage

QT_WEB_SCHEMA_VERSION = "1.0"
WEB_RUNTIME_SOURCE = "web.canvas"
QT_BRIDGE_TARGET = "qt.bridge"

MESSAGE_PAGE_READY = "lifecycle.page_ready"
MESSAGE_DIAGRAM_SAVE = "diagram.save"
MESSAGE_SELECTION_SYNC = "selection.sync"
MESSAGE_STATUS_UPDATE = "status.update"

WEB_TO_QT_MESSAGE_TYPES = frozenset(
    {
        MESSAGE_PAGE_READY,
        MESSAGE_DIAGRAM_SAVE,
        MESSAGE_SELECTION_SYNC,
        MESSAGE_STATUS_UPDATE,
    }
)


def build_web_to_qt_message(
    message_type: str,
    payload: dict[str, Any] | None = None,
    *,
    request_id: str = "",
) -> RuntimeMessage:
    """Create a standard Web -> Qt runtime envelope."""

    return RuntimeMessage(
        schema_version=QT_WEB_SCHEMA_VERSION,
        message_type=message_type,
        source=WEB_RUNTIME_SOURCE,
        target=QT_BRIDGE_TARGET,
        request_id=request_id,
        payload=payload or {},
    )
