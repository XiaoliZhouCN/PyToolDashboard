from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot


class EditorBridge(QObject):
    """Bridge Qt signals to the embedded web editor."""

    page_ready_signal = Signal()
    diagram_updated = Signal(str)
    status_changed = Signal(str)
    selection_changed = Signal(str)

    @Slot()
    def pageReady(self) -> None:
        self.page_ready_signal.emit()

    @Slot(str)
    def saveDiagram(self, payload: str) -> None:
        self.diagram_updated.emit(payload)

    @Slot(str)
    def setStatus(self, message: str) -> None:
        self.status_changed.emit(message)

    @Slot(str)
    def selectionChanged(self, payload: str) -> None:
        self.selection_changed.emit(payload)
