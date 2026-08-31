from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ptd_tool_mermaid_editor.application.store.domain_store import DomainStore
from ptd_tool_mermaid_editor.domain.editor.diagram_editor import DiagramEditor
from ptd_tool_mermaid_editor.parsing.markdown.loader import MarkdownLoader
from ptd_tool_mermaid_editor.parsing.mermaid.parser import MermaidParser
from ptd_tool_mermaid_editor.infra.repository.layout_repository import LayoutRepository
from ptd_tool_mermaid_editor.infra.repository.markdown_repository import MarkdownFileRepository


@dataclass(slots=True)
class EditorCoordinator:
    """Coordinate document loading and saving across parsing and persistence layers."""

    parser: MermaidParser
    diagram_editor: DiagramEditor
    markdown_repository: MarkdownFileRepository
    layout_repository: LayoutRepository
    store: DomainStore

    @classmethod
    def create_default(cls) -> "EditorCoordinator":
        """Build the default coordinator wiring used by the current desktop shell."""

        parser = MermaidParser()
        return cls(
            parser=parser,
            diagram_editor=DiagramEditor(),
            markdown_repository=MarkdownFileRepository(loader=MarkdownLoader(parser=parser)),
            layout_repository=LayoutRepository(),
            store=DomainStore(),
        )

    def load_document(self, path: Path) -> None:
        """Load a Markdown document and apply persisted layout state."""

        document = self.markdown_repository.load(path)
        self.layout_repository.apply(document.diagrams, self.layout_repository.load(path))
        self.store.current_document = document
        self.store.current_diagram_index = 0

    def save_document(self, path: Path) -> None:
        """Persist the current Markdown document and its layout sidecar."""

        if self.store.current_document is None:
            return
        self.markdown_repository.save(path, self.store.current_document)
        self.layout_repository.save(path, self.store.current_document.diagrams)
