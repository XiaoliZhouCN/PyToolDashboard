from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ptd_tool_mermaid_editor.parsing.markdown.loader import MarkdownLoader


def build_preview_response(
    markdown_file: Path,
    request_id: str = "",
) -> dict[str, Any]:
    """Build a lightweight preview payload for dashboard integration."""

    loader = MarkdownLoader()
    document = loader.load(markdown_file)
    created_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    return {
        "schema_version": "1.0",
        "request_id": request_id,
        "status": "ok",
        "message": f"Loaded {len(document.diagrams)} Mermaid diagrams",
        "payload": {
            "record_type": "preview.mermaid_document",
            "created_at": created_at,
            "document_path": str(markdown_file),
            "diagram_count": len(document.diagrams),
            "diagrams": [
                {
                    "diagram_id": diagram.diagram_id,
                    "title": diagram.title,
                    "chart_type": diagram.chart_type,
                    "direction": diagram.direction,
                    "node_count": len(diagram.nodes),
                    "edge_count": len(diagram.edges),
                    "subgraph_count": len(diagram.subgraphs),
                }
                for diagram in document.diagrams
            ],
        },
        "artifacts": [],
        "errors": [],
    }
