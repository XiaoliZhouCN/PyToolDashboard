from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.bridge import EditorBridge
from app.models.graph import MermaidDiagram, MermaidDocument
from app.services.layout_store import LayoutStore
from app.services.markdown_loader import MarkdownLoader
from app.services.mermaid_parser import MermaidParser


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle("Mermaid Editor")
        self.resize(1600, 950)

        self.parser = MermaidParser()
        self.loader = MarkdownLoader(parser=self.parser)
        self.layout_store = LayoutStore()
        self.bridge = EditorBridge()

        self.current_document: MermaidDocument | None = None
        self.current_path: Path | None = None
        self.current_index = 0

        self._build_ui()
        self._connect_bridge()
        self._load_editor_page()
        self._load_default_sample()

    def _build_ui(self) -> None:
        open_action = QAction("Open Markdown", self)
        open_action.triggered.connect(self.open_markdown_file)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_current_file)
        apply_action = QAction("Apply Source", self)
        apply_action.triggered.connect(self.apply_source_changes)
        reload_action = QAction("Reload Sample", self)
        reload_action.triggered.connect(self._load_default_sample)

        toolbar = self.addToolBar("Main")
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addAction(apply_action)
        toolbar.addAction(reload_action)

        root = QWidget(self)
        layout = QHBoxLayout(root)
        splitter = QSplitter(root)
        layout.addWidget(splitter)
        self.setCentralWidget(root)

        left_panel = QWidget(splitter)
        left_layout = QVBoxLayout(left_panel)

        self.path_label = QLabel("No file loaded", left_panel)
        left_layout.addWidget(self.path_label)

        self.diagram_list = QListWidget(left_panel)
        self.diagram_list.currentRowChanged.connect(self.on_diagram_changed)
        left_layout.addWidget(self.diagram_list, stretch=2)

        button_row = QWidget(left_panel)
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.apply_button = QPushButton("Apply Source", button_row)
        self.apply_button.clicked.connect(self.apply_source_changes)
        self.save_button = QPushButton("Save File", button_row)
        self.save_button.clicked.connect(self.save_current_file)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        left_layout.addWidget(button_row)

        self.source_editor = QPlainTextEdit(left_panel)
        self.source_editor.setPlaceholderText("Selected Mermaid source appears here.")
        left_layout.addWidget(self.source_editor, stretch=5)

        self.web_view = QWebEngineView(splitter)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.web_view)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)

        self.statusBar().showMessage("Ready")

    def _connect_bridge(self) -> None:
        channel = QWebChannel(self.web_view.page())
        channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(channel)

        self.bridge.page_ready_signal.connect(self.push_current_diagram)
        self.bridge.diagram_updated.connect(self.on_diagram_updated)
        self.bridge.status_changed.connect(self.statusBar().showMessage)

    def _load_editor_page(self) -> None:
        editor_path = self.project_root / "app" / "static" / "editor.html"
        self.web_view.setUrl(QUrl.fromLocalFile(str(editor_path)))

    def _load_default_sample(self) -> None:
        sample_path = Path("D:/Repositories/NexusRenderer/workflow.md")
        if sample_path.exists():
            self.load_markdown_file(sample_path)

    def open_markdown_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown",
            str(self.current_path.parent if self.current_path else self.project_root),
            "Markdown Files (*.md *.markdown);;All Files (*.*)",
        )
        if not file_path:
            return
        self.load_markdown_file(Path(file_path))

    def load_markdown_file(self, path: Path) -> None:
        try:
            document = self.loader.load(path)
            self.layout_store.apply(document.diagrams, self.layout_store.load(path))
        except Exception as exc:  # pragma: no cover - UI error surface
            QMessageBox.critical(self, "Load Failed", str(exc))
            return

        self.current_document = document
        self.current_path = path
        self.path_label.setText(str(path))
        self.diagram_list.clear()

        for diagram in document.diagrams:
            self.diagram_list.addItem(f"{diagram.diagram_id} - {diagram.title}")

        if document.diagrams:
            self.diagram_list.setCurrentRow(0)
        else:
            self.source_editor.clear()
        self.statusBar().showMessage(f"Loaded {path}")

    def on_diagram_changed(self, index: int) -> None:
        if not self.current_document or index < 0 or index >= len(self.current_document.diagrams):
            return
        self.current_index = index
        diagram = self.current_document.diagrams[index]
        self.source_editor.setPlainText(diagram.source)
        self.push_current_diagram()

    def push_current_diagram(self) -> None:
        if not self.current_document or not self.current_document.diagrams:
            return
        diagram = self.current_document.diagrams[self.current_index]
        payload = json.dumps(diagram.to_dict(), ensure_ascii=False)
        script = f"window.loadDiagram({payload});"
        self.web_view.page().runJavaScript(script)

    def apply_source_changes(self) -> None:
        if not self.current_document:
            return

        source = self.source_editor.toPlainText().strip()
        if not source:
            QMessageBox.warning(self, "Empty Source", "Mermaid source cannot be empty.")
            return

        try:
            parsed = self.parser.parse(source=source, index=self.current_index)
        except Exception as exc:  # pragma: no cover - UI error surface
            QMessageBox.critical(self, "Parse Failed", str(exc))
            return

        current = self.current_document.diagrams[self.current_index]
        parsed.diagram_id = current.diagram_id
        parsed.title = current.title
        self.current_document.diagrams[self.current_index] = parsed
        self.source_editor.setPlainText(parsed.source)
        self.layout_store.save(self.current_path, self.current_document.diagrams)
        self.push_current_diagram()
        self.statusBar().showMessage("Source applied")

    def on_diagram_updated(self, payload: str) -> None:
        if not self.current_document:
            return
        data = json.loads(payload)
        diagram = MermaidDiagram.from_dict(data)
        diagram.source = self.parser.serialize(diagram)
        self.current_document.diagrams[self.current_index] = diagram
        self.source_editor.setPlainText(diagram.source)
        if self.current_path:
            self.layout_store.save(self.current_path, self.current_document.diagrams)
        self.statusBar().showMessage("Diagram updated")

    def save_current_file(self) -> None:
        if not self.current_document or not self.current_path:
            return
        markdown = self.current_document.to_markdown()
        self.current_path.write_text(markdown, encoding="utf-8")
        self.layout_store.save(self.current_path, self.current_document.diagrams)
        self.statusBar().showMessage(f"Saved {self.current_path}")
