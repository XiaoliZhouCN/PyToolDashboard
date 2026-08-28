from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class NodeModel:
    """A renderable Mermaid node."""

    node_id: str
    label: str | None = None
    parent_subgraph: str | None = None
    x: float | None = None
    y: float | None = None
    width: float = 160.0
    height: float = 56.0
    anchor_side: str = "auto"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EdgeModel:
    """A Mermaid edge between two nodes."""

    source: str
    target: str
    label: str = ""
    style: str = "solid"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SubgraphModel:
    """A Mermaid subgraph container."""

    subgraph_id: str
    title: str
    parent_subgraph: str | None = None
    direction: str | None = None
    x: float | None = None
    y: float | None = None
    width: float = 260.0
    height: float = 180.0
    anchor_side: str = "auto"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MermaidDiagram:
    """A single Mermaid diagram extracted from a Markdown document."""

    diagram_id: str
    title: str
    chart_type: str
    direction: str
    source: str
    nodes: list[NodeModel] = field(default_factory=list)
    edges: list[EdgeModel] = field(default_factory=list)
    subgraphs: list[SubgraphModel] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagram_id": self.diagram_id,
            "title": self.title,
            "chart_type": self.chart_type,
            "direction": self.direction,
            "source": self.source,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "subgraphs": [subgraph.to_dict() for subgraph in self.subgraphs],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MermaidDiagram":
        return cls(
            diagram_id=payload["diagram_id"],
            title=payload.get("title", payload["diagram_id"]),
            chart_type=payload.get("chart_type", "flowchart"),
            direction=payload.get("direction", "TD"),
            source=payload.get("source", ""),
            nodes=[NodeModel(**item) for item in payload.get("nodes", [])],
            edges=[EdgeModel(**item) for item in payload.get("edges", [])],
            subgraphs=[
                SubgraphModel(**item) for item in payload.get("subgraphs", [])
            ],
        )


@dataclass(slots=True)
class MermaidDocument:
    """A Markdown document plus its extracted Mermaid diagrams."""

    source_path: str
    text_parts: list[str]
    diagrams: list[MermaidDiagram]

    def to_markdown(self) -> str:
        chunks: list[str] = []
        for index, diagram in enumerate(self.diagrams):
            chunks.append(self.text_parts[index])
            chunks.append(f"```mermaid\n{diagram.source.rstrip()}\n```")
        chunks.append(self.text_parts[-1] if self.text_parts else "")
        return "".join(chunks)
