from __future__ import annotations

from typing import TYPE_CHECKING

from ptd_tool_mermaid_editor.app.runtime import RuntimeContext

if TYPE_CHECKING:
    from ptd_tool_mermaid_editor.presentation.qt.main_window import MainWindow


def create_main_window(context: RuntimeContext) -> MainWindow:
    """Create the desktop shell for the current runtime context."""

    from ptd_tool_mermaid_editor.presentation.qt.main_window import MainWindow

    return MainWindow(
        tool_root=context.tool_root,
        project_root=context.project_root,
        initial_markdown_path=context.initial_markdown_path,
    )
