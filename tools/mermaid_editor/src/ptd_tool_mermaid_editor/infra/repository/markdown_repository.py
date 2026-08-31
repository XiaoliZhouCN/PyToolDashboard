from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ptd_tool_mermaid_editor.domain.graph import MermaidDocument
from ptd_tool_mermaid_editor.parsing.markdown.loader import MarkdownLoader


@dataclass(slots=True)
class MarkdownFileRepository:
    """Read and write Markdown documents while keeping parsing separate."""

    loader: MarkdownLoader | None = None

    def load(self, path: Path) -> MermaidDocument:
        """Load a Markdown document and extract Mermaid diagrams."""

        loader = self.loader or MarkdownLoader()
        return loader.load(path)

    def save(self, path: Path, document: MermaidDocument) -> None:
        """Persist the document text produced by the parsing layer."""

        path.write_text(document.to_markdown(), encoding="utf-8")
