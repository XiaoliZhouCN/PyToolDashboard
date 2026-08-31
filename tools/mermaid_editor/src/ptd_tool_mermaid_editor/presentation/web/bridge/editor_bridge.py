from __future__ import annotations

import json
from collections.abc import Callable

from ptd_tool_mermaid_editor.protocols import (
    MESSAGE_DIAGRAM_SAVE,
    MESSAGE_PAGE_READY,
    MESSAGE_SELECTION_SYNC,
    MESSAGE_STATUS_UPDATE,
    QT_BRIDGE_TARGET,
    WEB_RUNTIME_SOURCE,
    WEB_TO_QT_MESSAGE_TYPES,
    RuntimeMessage,
    RuntimeMessageError,
    build_web_to_qt_message,
)
from PySide6.QtCore import QObject, Signal, Slot


class EditorBridge(QObject):
    """Bridge Qt signals to the embedded web editor."""

    page_ready_signal = Signal()
    diagram_updated = Signal(str)
    status_changed = Signal(str)
    selection_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._message_handlers: dict[str, Callable[[RuntimeMessage], None]] = {
            MESSAGE_PAGE_READY: self._handle_page_ready,
            MESSAGE_DIAGRAM_SAVE: self._handle_diagram_save,
            MESSAGE_SELECTION_SYNC: self._handle_selection_sync,
            MESSAGE_STATUS_UPDATE: self._handle_status_update,
        }

    @Slot(str)
    def postMessage(self, payload: str) -> None:
        try:
            message = RuntimeMessage.from_json(payload)
        except RuntimeMessageError as exc:
            self.status_changed.emit(f"Protocol error: {exc}")
            return
        self._dispatch_runtime_message(message)

    @Slot()
    def pageReady(self) -> None:
        self._dispatch_runtime_message(build_web_to_qt_message(MESSAGE_PAGE_READY))

    @Slot(str)
    def saveDiagram(self, payload: str) -> None:
        self._dispatch_legacy_json_message(MESSAGE_DIAGRAM_SAVE, payload)

    @Slot(str)
    def setStatus(self, message: str) -> None:
        self._dispatch_runtime_message(
            build_web_to_qt_message(
                MESSAGE_STATUS_UPDATE,
                payload={"message": message},
            )
        )

    @Slot(str)
    def selectionChanged(self, payload: str) -> None:
        self._dispatch_legacy_json_message(MESSAGE_SELECTION_SYNC, payload)

    def _dispatch_legacy_json_message(self, message_type: str, payload: str) -> None:
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            self.status_changed.emit(f"Protocol error: Invalid legacy JSON for {message_type}.")
            return
        self._dispatch_runtime_message(build_web_to_qt_message(message_type, payload=parsed))

    def _dispatch_runtime_message(self, message: RuntimeMessage) -> None:
        if message.target != QT_BRIDGE_TARGET:
            self.status_changed.emit(f"Protocol error: Unexpected target {message.target}.")
            return
        if message.source != WEB_RUNTIME_SOURCE:
            self.status_changed.emit(f"Protocol error: Unexpected source {message.source}.")
            return
        if message.message_type not in WEB_TO_QT_MESSAGE_TYPES:
            self.status_changed.emit(f"Protocol error: Unsupported message {message.message_type}.")
            return
        handler = self._message_handlers.get(message.message_type)
        if handler is None:
            self.status_changed.emit(f"Protocol error: No handler for {message.message_type}.")
            return
        handler(message)

    def _handle_page_ready(self, _message: RuntimeMessage) -> None:
        self.page_ready_signal.emit()

    def _handle_diagram_save(self, message: RuntimeMessage) -> None:
        self.diagram_updated.emit(json.dumps(message.payload, ensure_ascii=False))

    def _handle_status_update(self, message: RuntimeMessage) -> None:
        self.status_changed.emit(str(message.payload.get("message", "")))

    def _handle_selection_sync(self, message: RuntimeMessage) -> None:
        self.selection_changed.emit(json.dumps(message.payload, ensure_ascii=False))
