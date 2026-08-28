from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ptd_tool_mermaid_editor.app.bridge import EditorBridge
from ptd_tool_mermaid_editor.domain.diagram_editor import DiagramEditor
from ptd_tool_mermaid_editor.domain.graph import MermaidDiagram, MermaidDocument
from ptd_tool_mermaid_editor.domain.mermaid_parser import MermaidParser
from ptd_tool_mermaid_editor.infra.layout_store import LayoutStore
from ptd_tool_mermaid_editor.infra.markdown_loader import MarkdownLoader


class MainWindow(QMainWindow):
    """Desktop shell that hosts the Mermaid source editor and canvas."""

    def __init__(
        self,
        tool_root: Path,
        project_root: Path,
        initial_markdown_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.tool_root = tool_root
        self.project_root = project_root
        self.initial_markdown_path = initial_markdown_path
        self.setWindowTitle("Mermaid Editor")
        self.resize(1600, 950)

        self.parser = MermaidParser()
        self.diagram_editor = DiagramEditor()
        self.loader = MarkdownLoader(parser=self.parser)
        self.layout_store = LayoutStore()
        self.bridge = EditorBridge()

        self.current_document: MermaidDocument | None = None
        self.current_path: Path | None = None
        self.current_index = 0
        self.current_selection_payload: dict[str, object] | None = None

        self._build_ui()
        self._connect_bridge()
        self._load_editor_page()
        self._load_initial_document()

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
        left_splitter = QSplitter(left_panel)
        left_layout.addWidget(left_splitter)

        navigator_panel = QWidget(left_splitter)
        navigator_layout = QVBoxLayout(navigator_panel)

        self.path_label = QLabel("No file loaded", navigator_panel)
        navigator_layout.addWidget(self.path_label)

        self.diagram_list = QListWidget(navigator_panel)
        self.diagram_list.currentRowChanged.connect(self.on_diagram_changed)
        navigator_layout.addWidget(self.diagram_list, stretch=2)

        button_row = QWidget(navigator_panel)
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.apply_button = QPushButton("Apply Source", button_row)
        self.apply_button.clicked.connect(self.apply_source_changes)
        self.save_button = QPushButton("Save File", button_row)
        self.save_button.clicked.connect(self.save_current_file)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        navigator_layout.addWidget(button_row)

        self.source_editor = QPlainTextEdit(navigator_panel)
        self.source_editor.setPlaceholderText("Selected Mermaid source appears here.")
        navigator_layout.addWidget(self.source_editor, stretch=5)

        detail_panel = QWidget(left_splitter)
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_summary = QLabel("No selection", detail_panel)
        detail_layout.addWidget(self.detail_summary)

        form_widget = QWidget(detail_panel)
        form_layout = QFormLayout(form_widget)
        self.detail_id_edit = QLineEdit(form_widget)
        self.detail_label_edit = QLineEdit(form_widget)
        self.detail_source_edit = QLineEdit(form_widget)
        self.detail_target_edit = QLineEdit(form_widget)
        self.detail_style_combo = QComboBox(form_widget)
        self.detail_style_combo.addItems(["solid", "thick", "dotted", "plain"])
        self.detail_anchor_combo = QComboBox(form_widget)
        self.detail_anchor_combo.addItems(["auto", "top", "right", "bottom", "left"])
        form_layout.addRow("Identifier", self.detail_id_edit)
        form_layout.addRow("Label / Title", self.detail_label_edit)
        form_layout.addRow("Edge Source", self.detail_source_edit)
        form_layout.addRow("Edge Target", self.detail_target_edit)
        form_layout.addRow("Edge Style", self.detail_style_combo)
        form_layout.addRow("Anchor Side", self.detail_anchor_combo)
        detail_layout.addWidget(form_widget)

        self.detail_apply_button = QPushButton("Apply Detail Changes", detail_panel)
        self.detail_apply_button.clicked.connect(self.apply_detail_changes)
        detail_layout.addWidget(self.detail_apply_button)
        detail_layout.addStretch(1)

        left_splitter.addWidget(navigator_panel)
        left_splitter.addWidget(detail_panel)
        left_splitter.setStretchFactor(0, 4)
        left_splitter.setStretchFactor(1, 3)

        self.web_view = QWebEngineView(splitter)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.web_view)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)

        self.statusBar().showMessage(f"Ready | project_root={self.project_root}")

    def _connect_bridge(self) -> None:
        channel = QWebChannel(self.web_view.page())
        channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(channel)

        self.bridge.page_ready_signal.connect(self.push_current_diagram)
        self.bridge.diagram_updated.connect(self.on_diagram_updated)
        self.bridge.status_changed.connect(self.statusBar().showMessage)
        self.bridge.selection_changed.connect(self.on_selection_changed)

    def _load_editor_page(self) -> None:
        editor_path = (
            self.tool_root
            / "src"
            / "ptd_tool_mermaid_editor"
            / "app"
            / "static"
            / "editor.html"
        )
        self.web_view.setUrl(QUrl.fromLocalFile(str(editor_path)))

    def _load_initial_document(self) -> None:
        if self.initial_markdown_path and self.initial_markdown_path.exists():
            self.load_markdown_file(self.initial_markdown_path)
            return
        self._load_default_sample()

    def _load_default_sample(self) -> None:
        sample_path = self.tool_root / "samples" / "sample_workflow.md"
        if sample_path.exists():
            self.load_markdown_file(sample_path)

    def open_markdown_file(self) -> None:
        start_dir = self.current_path.parent if self.current_path else self.project_root
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown",
            str(start_dir),
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
        self.current_index = 0
        self.path_label.setText(str(path))
        self.diagram_list.clear()

        for diagram in document.diagrams:
            self.diagram_list.addItem(f"{diagram.diagram_id} - {diagram.title}")

        if document.diagrams:
            self.diagram_list.setCurrentRow(0)
        else:
            self.source_editor.clear()
        self.on_selection_changed("")

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
        self.web_view.page().runJavaScript(f"window.loadDiagram({payload});")

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
        if self.current_path:
            self.layout_store.save(self.current_path, self.current_document.diagrams)
        self.push_current_diagram()
        self.statusBar().showMessage("Source applied")

    def on_diagram_updated(self, payload: str) -> None:
        if not self.current_document:
            return
        data = json.loads(payload)
        diagram = MermaidDiagram.from_dict(data)
        self.diagram_editor.normalize(diagram)
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

    def on_selection_changed(self, payload: str) -> None:
        self.current_selection_payload = json.loads(payload) if payload else None
        selection = self.current_selection_payload or {}
        kind = selection.get("kind", "none")
        count = int(selection.get("count", 0))

        if kind == "none" or count == 0:
            self.detail_summary.setText("No selection")
            self._set_detail_enabled(False)
            self._clear_detail_fields()
            return

        if kind == "multi":
            self.detail_summary.setText(f"Multiple selection ({count})")
            self._set_detail_enabled(False)
            self._clear_detail_fields()
            return

        self.detail_summary.setText(f"Selected {kind}: {selection.get('id', '')}")
        self._set_detail_enabled(True)
        self.detail_id_edit.setVisible(kind != "edge")
        self.detail_anchor_combo.setVisible(kind in {"node", "subgraph"})
        self.detail_source_edit.setVisible(kind == "edge")
        self.detail_target_edit.setVisible(kind == "edge")
        self.detail_style_combo.setVisible(kind == "edge")

        self.detail_id_edit.setText(str(selection.get("id", "")))
        self.detail_label_edit.setText(str(selection.get("label", "")))
        self.detail_source_edit.setText(str(selection.get("source", "")))
        self.detail_target_edit.setText(str(selection.get("target", "")))
        self.detail_style_combo.setCurrentText(str(selection.get("style", "solid")))
        self.detail_anchor_combo.setCurrentText(str(selection.get("anchor_side", "auto")))

    def apply_detail_changes(self) -> None:
        selection = self.current_selection_payload
        if not selection:
            return
        payload = {
            "kind": selection.get("kind", "none"),
            "id": selection.get("id", ""),
            "label": self.detail_label_edit.text(),
            "new_id": self.detail_id_edit.text(),
            "source": self.detail_source_edit.text(),
            "target": self.detail_target_edit.text(),
            "style": self.detail_style_combo.currentText(),
            "anchor_side": self.detail_anchor_combo.currentText(),
        }
        escaped = json.dumps(payload, ensure_ascii=False)
        self.web_view.page().runJavaScript(f"window.applyInspectorPayload({escaped});")

    def _set_detail_enabled(self, enabled: bool) -> None:
        self.detail_id_edit.setEnabled(enabled)
        self.detail_label_edit.setEnabled(enabled)
        self.detail_source_edit.setEnabled(enabled)
        self.detail_target_edit.setEnabled(enabled)
        self.detail_style_combo.setEnabled(enabled)
        self.detail_anchor_combo.setEnabled(enabled)
        self.detail_apply_button.setEnabled(enabled)

    def _clear_detail_fields(self) -> None:
        self.detail_id_edit.clear()
        self.detail_label_edit.clear()
        self.detail_source_edit.clear()
        self.detail_target_edit.clear()
        self.detail_style_combo.setCurrentText("solid")
        self.detail_anchor_combo.setCurrentText("auto")
