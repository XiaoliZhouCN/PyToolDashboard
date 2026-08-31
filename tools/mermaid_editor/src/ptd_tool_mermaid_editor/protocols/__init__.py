"""Typed runtime messages shared across editor layers."""

from ptd_tool_mermaid_editor.protocols.messages import RuntimeMessage, RuntimeMessageError
from ptd_tool_mermaid_editor.protocols.qt_web import (
    MESSAGE_DIAGRAM_SAVE,
    MESSAGE_PAGE_READY,
    MESSAGE_SELECTION_SYNC,
    MESSAGE_STATUS_UPDATE,
    QT_BRIDGE_TARGET,
    QT_WEB_SCHEMA_VERSION,
    WEB_RUNTIME_SOURCE,
    WEB_TO_QT_MESSAGE_TYPES,
    build_web_to_qt_message,
)

__all__ = [
    "MESSAGE_DIAGRAM_SAVE",
    "MESSAGE_PAGE_READY",
    "MESSAGE_SELECTION_SYNC",
    "MESSAGE_STATUS_UPDATE",
    "QT_BRIDGE_TARGET",
    "QT_WEB_SCHEMA_VERSION",
    "RuntimeMessage",
    "RuntimeMessageError",
    "WEB_RUNTIME_SOURCE",
    "WEB_TO_QT_MESSAGE_TYPES",
    "build_web_to_qt_message",
]
