from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from app.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Mermaid Editor")

    window = MainWindow(project_root=Path(__file__).resolve().parent.parent)
    window.show()
    return app.exec()
