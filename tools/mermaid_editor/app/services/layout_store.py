from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.graph import MermaidDiagram


class LayoutStore:
    def load(self, markdown_path: Path) -> dict[str, Any]:
        layout_path = self._layout_path(markdown_path)
        if not layout_path.exists():
            return {}
        return json.loads(layout_path.read_text(encoding="utf-8"))

    def save(self, markdown_path: Path, diagrams: list[MermaidDiagram]) -> None:
        layout_path = self._layout_path(markdown_path)
        payload = {
            "version": 1,
            "diagrams": {
                diagram.diagram_id: {
                    "nodes": {
                        node.node_id: {"x": node.x, "y": node.y}
                        for node in diagram.nodes
                    },
                    "subgraphs": {
                        subgraph.subgraph_id: {
                            "x": subgraph.x,
                            "y": subgraph.y,
                            "width": subgraph.width,
                            "height": subgraph.height,
                        }
                        for subgraph in diagram.subgraphs
                    },
                }
                for diagram in diagrams
            },
        }
        layout_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def apply(self, diagrams: list[MermaidDiagram], layout_data: dict[str, Any]) -> None:
        diagrams_layout = layout_data.get("diagrams", {})
        for diagram in diagrams:
            diagram_layout = diagrams_layout.get(diagram.diagram_id, {})
            node_layout = diagram_layout.get("nodes", {})
            subgraph_layout = diagram_layout.get("subgraphs", {})

            for node in diagram.nodes:
                coords = node_layout.get(node.node_id, {})
                node.x = coords.get("x", node.x)
                node.y = coords.get("y", node.y)

            for subgraph in diagram.subgraphs:
                rect = subgraph_layout.get(subgraph.subgraph_id, {})
                subgraph.x = rect.get("x", subgraph.x)
                subgraph.y = rect.get("y", subgraph.y)
                subgraph.width = rect.get("width", subgraph.width)
                subgraph.height = rect.get("height", subgraph.height)

    @staticmethod
    def _layout_path(markdown_path: Path) -> Path:
        return markdown_path.with_suffix(markdown_path.suffix + ".layout.json")
