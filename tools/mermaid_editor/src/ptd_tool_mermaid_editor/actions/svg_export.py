from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from ptd_tool_mermaid_editor.domain.graph import MermaidDiagram, NodeModel, SubgraphModel
from ptd_tool_mermaid_editor.infra.markdown_loader import MarkdownLoader


@dataclass(slots=True)
class SvgExportResult:
    """Result of exporting one Mermaid diagram to SVG."""

    diagram_id: str
    output_path: Path


class SvgExporter:
    """Export Mermaid diagrams into simple standalone SVG documents."""

    def export_document(
        self,
        markdown_file: Path,
        output_dir: Path,
        diagram_id: str | None = None,
    ) -> list[SvgExportResult]:
        diagrams = self.load_diagrams(markdown_file=markdown_file, diagram_id=diagram_id)

        output_dir.mkdir(parents=True, exist_ok=True)

        results: list[SvgExportResult] = []
        for diagram in diagrams:
            file_name = f"{diagram.diagram_id}.svg"
            output_path = output_dir / file_name
            output_path.write_text(self.render_svg(diagram), encoding="utf-8")
            results.append(SvgExportResult(diagram_id=diagram.diagram_id, output_path=output_path))
        return results

    def load_diagrams(
        self,
        markdown_file: Path,
        diagram_id: str | None = None,
    ) -> list[MermaidDiagram]:
        """Load diagrams from a Markdown file with optional diagram filtering."""

        document = MarkdownLoader().load(markdown_file)
        diagrams = document.diagrams

        if diagram_id is not None:
            diagrams = [diagram for diagram in diagrams if diagram.diagram_id == diagram_id]
            if not diagrams:
                raise ValueError(f"Diagram not found: {diagram_id}")

        return diagrams

    def render_svg(self, diagram: MermaidDiagram) -> str:
        """Render a diagram into standalone SVG markup."""

        canvas = self.compute_canvas(diagram)
        subgraph_markup = "\n".join(
            self._render_subgraph(subgraph) for subgraph in diagram.subgraphs
        )
        edge_markup = "\n".join(self._render_edge(diagram, edge) for edge in diagram.edges)
        node_markup = "\n".join(self._render_node(node) for node in diagram.nodes)
        title = escape(diagram.title)

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{canvas['width']}" height="{canvas['height']}" viewBox="0 0 {canvas['width']} {canvas['height']}">
  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 z" fill="#64748b" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#0f172a" />
  <text x="24" y="36" fill="#e2e8f0" font-family="Segoe UI, sans-serif" font-size="20" font-weight="600">{title}</text>
  <g id="subgraphs">
{self._indent_markup(subgraph_markup, 4)}
  </g>
  <g id="edges">
{self._indent_markup(edge_markup, 4)}
  </g>
  <g id="nodes">
{self._indent_markup(node_markup, 4)}
  </g>
</svg>
"""

    def compute_canvas(self, diagram: MermaidDiagram) -> dict[str, int]:
        """Compute the output canvas size for a diagram."""

        max_x = 640.0
        max_y = 420.0

        for node in diagram.nodes:
            max_x = max(max_x, (node.x or 80.0) + node.width + 60.0)
            max_y = max(max_y, (node.y or 80.0) + node.height + 80.0)

        for subgraph in diagram.subgraphs:
            max_x = max(max_x, (subgraph.x or 40.0) + subgraph.width + 60.0)
            max_y = max(max_y, (subgraph.y or 40.0) + subgraph.height + 80.0)

        return {
            "width": int(max_x),
            "height": int(max_y),
        }

    def _render_node(self, node: NodeModel) -> str:
        x = node.x or 80.0
        y = node.y or 80.0
        label = escape(node.label or node.node_id)
        return (
            f'<g class="node" data-node-id="{escape(node.node_id)}">'
            f'<rect x="{x}" y="{y}" width="{node.width}" height="{node.height}" '
            f'rx="10" ry="10" fill="#111827" stroke="#60a5fa" stroke-width="1.5" />'
            f'<text x="{x + node.width / 2}" y="{y + node.height / 2 + 4}" '
            f'fill="#e5e7eb" font-family="Segoe UI, sans-serif" font-size="13" '
            f'text-anchor="middle">{label}</text>'
            f"</g>"
        )

    def _render_subgraph(self, subgraph: SubgraphModel) -> str:
        x = subgraph.x or 40.0
        y = subgraph.y or 40.0
        title = escape(subgraph.title)
        return (
            f'<g class="subgraph" data-subgraph-id="{escape(subgraph.subgraph_id)}">'
            f'<rect x="{x}" y="{y}" width="{subgraph.width}" height="{subgraph.height}" '
            f'rx="12" ry="12" fill="rgba(56, 189, 248, 0.12)" stroke="#38bdf8" stroke-width="1.5" />'
            f'<text x="{x + 16}" y="{y + 24}" fill="#7dd3fc" '
            f'font-family="Segoe UI, sans-serif" font-size="14" font-weight="600">{title}</text>'
            f"</g>"
        )

    def _render_edge(self, diagram: MermaidDiagram, edge) -> str:
        source_box = self._resolve_box(diagram, edge.source)
        target_box = self._resolve_box(diagram, edge.target)
        if source_box is None or target_box is None:
            return ""

        target_center = self._box_center(target_box)
        source_center = self._box_center(source_box)
        source_anchor = self._resolve_anchor(source_box, target_center)
        target_anchor = self._resolve_anchor(target_box, source_center)
        x1, y1 = source_anchor
        x2, y2 = target_anchor
        stroke_width = "3" if edge.style == "thick" else "2"
        dash_array = ' stroke-dasharray="7 5"' if edge.style == "dotted" else ""
        marker_end = "" if edge.style == "plain" else ' marker-end="url(#arrowhead)"'
        label_markup = ""
        if edge.label:
            label_markup = (
                f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 10}" fill="#cbd5e1" '
                f'font-family="Segoe UI, sans-serif" font-size="12" text-anchor="middle">'
                f"{escape(edge.label)}</text>"
            )

        path_markup = (
            f'<path d="M {x1} {y1} C {x1 + 60} {y1}, {x2 - 60} {y2}, {x2} {y2}" '
            f'stroke="#a5b4fc" stroke-width="{stroke_width}" fill="none"{dash_array}{marker_end} />'
        )
        return f"<g>{path_markup}{label_markup}</g>"

    def _resolve_box(self, diagram: MermaidDiagram, reference_id: str) -> dict[str, float] | None:
        node = next((item for item in diagram.nodes if item.node_id == reference_id), None)
        if node is not None:
            return {
                "x": node.x or 80.0,
                "y": node.y or 80.0,
                "width": node.width,
                "height": node.height,
                "anchor_side": getattr(node, "anchor_side", "auto"),
            }

        subgraph = next(
            (item for item in diagram.subgraphs if item.subgraph_id == reference_id),
            None,
        )
        if subgraph is not None:
            return {
                "x": subgraph.x or 40.0,
                "y": subgraph.y or 40.0,
                "width": subgraph.width,
                "height": subgraph.height,
                "anchor_side": getattr(subgraph, "anchor_side", "auto"),
            }
        return None

    def _resolve_anchor(self, box: dict[str, float], toward: tuple[float, float]) -> tuple[float, float]:
        explicit = self._anchor_by_side(box, str(box.get("anchor_side", "auto")))
        if explicit is not None:
            return explicit

        center_x, center_y = self._box_center(box)
        dx = toward[0] - center_x
        dy = toward[1] - center_y
        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return center_x, center_y

        half_width = box["width"] / 2
        half_height = box["height"] / 2
        scale = 1.0 / max(abs(dx) / half_width, abs(dy) / half_height)
        return center_x + dx * scale, center_y + dy * scale

    @staticmethod
    def _box_center(box: dict[str, float]) -> tuple[float, float]:
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    @staticmethod
    def _anchor_by_side(box: dict[str, float], side: str) -> tuple[float, float] | None:
        center_x, center_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        if side == "top":
            return center_x, box["y"]
        if side == "right":
            return box["x"] + box["width"], center_y
        if side == "bottom":
            return center_x, box["y"] + box["height"]
        if side == "left":
            return box["x"], center_y
        return None

    @staticmethod
    def _indent_markup(markup: str, spaces: int) -> str:
        if not markup.strip():
            return ""
        prefix = " " * spaces
        return "\n".join(f"{prefix}{line}" for line in markup.splitlines() if line.strip())
