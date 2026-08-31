from __future__ import annotations

from dataclasses import dataclass

from ptd_tool_mermaid_editor.domain.graph import MermaidDocument


@dataclass(slots=True)
class DomainStore:
    """Mutable, persistable editor state that represents the current document."""

    current_document: MermaidDocument | None = None
    current_diagram_index: int = 0
