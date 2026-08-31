"""Static contract checks for undo/redo behavior in the web editor entry."""

from __future__ import annotations

from pathlib import Path
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[2]
MAIN_ENTRY = (
    TOOL_ROOT / "src" / "ptd_tool_mermaid_editor" / "presentation" / "web" / "index.html"
)


class HistoryRedoContractTest(unittest.TestCase):
    """Lock the redo pipeline and history reset behavior in the web entry."""

    def test_main_entry_defines_bounded_undo_and_redo_helpers(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertIn("function pushSnapshot(stack, snapshot)", html)
        self.assertIn("function pushUndoSnapshot(snapshot, options = {})", html)
        self.assertIn("function pushRedoSnapshot(snapshot)", html)
        self.assertIn("function redoDiagramChange()", html)
        self.assertIn('notifyStatus("已重做一步");', html)
        self.assertIn("pushUndoSnapshot(current, { clearRedo: false });", html)

    def test_mutation_and_drag_paths_share_undo_snapshot_contract(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertIn("pushUndoSnapshot(before);", html)
        self.assertIn("pushUndoSnapshot(dragState.beforeSnapshot);", html)
        self.assertIn("state.history.redoStack = [];", html)

    def test_keyboard_shortcuts_cover_redo_variants(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertIn('Ctrl+Y / Ctrl+Shift+Z 重做', html)
        self.assertIn('(!evt.shiftKey && evt.key.toLowerCase() === "y")', html)
        self.assertIn('(evt.shiftKey && evt.key.toLowerCase() === "z")', html)
        self.assertIn("redoDiagramChange();", html)

    def test_load_diagram_resets_both_history_stacks(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertIn("state.history.undoStack = [];", html)
        self.assertIn("state.history.redoStack = [];", html)


if __name__ == "__main__":
    unittest.main()
