from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
)

from ptd_tool_mermaid_editor.domain.geometry import box_center, resolve_anchor_point
from ptd_tool_mermaid_editor.domain.geometry import build_edge_curve
from ptd_tool_mermaid_editor.domain.graph import EdgeModel, MermaidDiagram, NodeModel, SubgraphModel
from ptd_tool_mermaid_editor.infra.export.svg_exporter import SvgExporter


_QT_APP: QGuiApplication | None = None


@dataclass(slots=True)
class PngExportResult:
    """Result of exporting one Mermaid diagram to PNG."""

    diagram_id: str
    output_path: Path


class PngExporter:
    """Export Mermaid diagrams into rasterized PNG files."""

    def __init__(self, svg_exporter: SvgExporter | None = None) -> None:
        self._svg_exporter = svg_exporter or SvgExporter()

    def export_document(
        self,
        markdown_file: Path,
        output_dir: Path,
        diagram_id: str | None = None,
    ) -> list[PngExportResult]:
        diagrams = self._svg_exporter.load_diagrams(
            markdown_file=markdown_file,
            diagram_id=diagram_id,
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        results: list[PngExportResult] = []
        for diagram in diagrams:
            output_path = output_dir / f"{diagram.diagram_id}.png"
            self._render_png(diagram=diagram, output_path=output_path)
            results.append(PngExportResult(diagram_id=diagram.diagram_id, output_path=output_path))
        return results

    def _render_png(self, diagram: MermaidDiagram, output_path: Path) -> None:
        self._ensure_qt_app()
        canvas = self._svg_exporter.compute_canvas(diagram)
        image = QImage(canvas["width"], canvas["height"], QImage.Format.Format_ARGB32)
        image.fill(QColor("#0f172a"))

        painter = QPainter(image)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            self._draw_title(painter, diagram)
            for subgraph in diagram.subgraphs:
                self._draw_subgraph(painter, subgraph)
            for edge in diagram.edges:
                self._draw_edge(painter, diagram, edge)
            for node in diagram.nodes:
                self._draw_node(painter, node)
        finally:
            painter.end()

        if not image.save(str(output_path), "PNG"):
            raise ValueError(f"Failed to save PNG file: {output_path}")

    @staticmethod
    def _ensure_qt_app() -> None:
        global _QT_APP
        if QGuiApplication.instance() is None:
            _QT_APP = QGuiApplication([])

    def _draw_title(self, painter: QPainter, diagram: MermaidDiagram) -> None:
        painter.setPen(QPen(QColor("#e2e8f0")))
        title_font = QFont("Segoe UI", 20)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(QPointF(24, 36), diagram.title)

    def _draw_subgraph(self, painter: QPainter, subgraph: SubgraphModel) -> None:
        x = subgraph.x or 40.0
        y = subgraph.y or 40.0
        rect = QRectF(x, y, subgraph.width, subgraph.height)

        painter.setPen(QPen(QColor("#38bdf8"), 1.5))
        painter.setBrush(QBrush(QColor(56, 189, 248, 31)))
        painter.drawRoundedRect(rect, 12, 12)

        title_font = QFont("Segoe UI", 14)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QPen(QColor("#7dd3fc")))
        painter.drawText(QPointF(x + 16, y + 24), subgraph.title)

    def _draw_node(self, painter: QPainter, node: NodeModel) -> None:
        x = node.x or 80.0
        y = node.y or 80.0
        rect = QRectF(x, y, node.width, node.height)

        painter.setPen(QPen(QColor("#60a5fa"), 1.5))
        painter.setBrush(QBrush(QColor("#111827")))
        painter.drawRoundedRect(rect, 10, 10)

        label_font = QFont("Segoe UI", 13)
        painter.setFont(label_font)
        painter.setPen(QPen(QColor("#e5e7eb")))
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            node.label or node.node_id,
        )

    def _draw_edge(self, painter: QPainter, diagram: MermaidDiagram, edge: EdgeModel) -> None:
        source_box = self._resolve_box(diagram, edge.source)
        target_box = self._resolve_box(diagram, edge.target)
        if source_box is None or target_box is None:
            return

        target_center = box_center(target_box)
        source_center = box_center(source_box)
        source_anchor = resolve_anchor_point(
            source_box,
            target_center,
            side_override=getattr(edge, "source_anchor_side", "auto"),
        )
        target_anchor = resolve_anchor_point(
            target_box,
            source_center,
            side_override=getattr(edge, "target_anchor_side", "auto"),
        )
        x1, y1 = source_anchor
        x2, y2 = target_anchor
        (cx1, cy1), (cx2, cy2) = build_edge_curve(source_anchor, target_anchor)

        pen = QPen(QColor("#a5b4fc"), 3 if edge.style == "thick" else 2)
        if edge.style == "dotted":
            pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        painter.setBrush(QBrush())

        path = QPainterPath(QPointF(x1, y1))
        path.cubicTo(QPointF(cx1, cy1), QPointF(cx2, cy2), QPointF(x2, y2))
        painter.drawPath(path)

        if edge.style != "plain":
            self._draw_arrowhead(painter, x2, y2, cx2, cy2)

        if edge.label:
            label_font = QFont("Segoe UI", 12)
            painter.setFont(label_font)
            painter.setPen(QPen(QColor("#cbd5e1")))
            painter.drawText(QPointF((x1 + x2) / 2 - 10, (y1 + y2) / 2 - 10), edge.label)

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

    def _draw_arrowhead(
        self,
        painter: QPainter,
        x: float,
        y: float,
        control_x: float,
        control_y: float,
    ) -> None:
        dx = x - control_x
        dy = y - control_y
        length = math.hypot(dx, dy) or 1.0
        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux
        tip_back_x = x - ux * 10.0
        tip_back_y = y - uy * 10.0

        arrow = QPainterPath(QPointF(x, y))
        arrow.lineTo(tip_back_x + px * 5.0, tip_back_y + py * 5.0)
        arrow.lineTo(tip_back_x - px * 5.0, tip_back_y - py * 5.0)
        arrow.closeSubpath()
        painter.fillPath(arrow, QBrush(QColor("#a5b4fc")))

__all__ = ["PngExporter", "PngExportResult"]
