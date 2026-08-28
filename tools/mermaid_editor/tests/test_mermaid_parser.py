from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = TOOL_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ptd_tool_mermaid_editor.domain.mermaid_parser import MermaidParser
from ptd_tool_mermaid_editor.domain.graph import EdgeModel, MermaidDiagram, NodeModel
from ptd_tool_mermaid_editor.domain.diagram_editor import DiagramEditor
from ptd_tool_mermaid_editor.domain.graph import SubgraphModel
from ptd_tool_mermaid_editor.infra.markdown_loader import MarkdownLoader
from ptd_tool_mermaid_editor.preview.service import build_preview_response

try:
    from ptd_tool_mermaid_editor.actions.service import run_action
except ModuleNotFoundError:
    run_action = None


WORKFLOW_SAMPLE = """```mermaid
flowchart TD
    start

    subgraph Main["main"]
        direction TB
        main["`main()`"]
    end

    start ==> main
```

```mermaid
flowchart TD
    info["line1
line2"]
    info --> done["done"]
```"""


class MermaidParserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = MermaidParser()
        self.diagram_editor = DiagramEditor()

    def test_parse_flowchart_with_subgraph_and_edges(self) -> None:
        source = """flowchart TD
    start
    subgraph Main["main"]
        direction TB
        main["`main()`"]
    end
    start ==> main"""

        diagram = self.parser.parse(source, index=0)

        self.assertEqual(diagram.chart_type, "flowchart")
        self.assertEqual(diagram.direction, "TD")
        self.assertEqual(len(diagram.nodes), 2)
        self.assertEqual(len(diagram.subgraphs), 1)
        self.assertEqual(diagram.subgraphs[0].title, "main")
        self.assertEqual(diagram.edges[0].style, "thick")

    def test_parse_multiline_node_label(self) -> None:
        source = """flowchart TD
    info["line1
line2"]
    info --> done["done"]"""

        diagram = self.parser.parse(source, index=0)
        labels = {node.node_id: node.label for node in diagram.nodes}

        self.assertEqual(labels["info"], "line1\nline2")
        self.assertEqual(labels["done"], "done")

    def test_parse_edge_endpoint_to_existing_subgraph_without_creating_top_level_node(self) -> None:
        source = """flowchart TD
    start
    subgraph RenderApp["RenderApp"]
        direction TB
        subgraph app_func_exec["exec()"]
        end
    end
    start ==> app_func_exec"""

        diagram = self.parser.parse(source, index=0)

        node_ids = {node.node_id for node in diagram.nodes}
        subgraph_ids = {subgraph.subgraph_id for subgraph in diagram.subgraphs}

        self.assertIn("app_func_exec", subgraph_ids)
        self.assertNotIn("app_func_exec", node_ids)
        self.assertEqual(diagram.edges[0].target, "app_func_exec")

    def test_default_layout_avoids_overlap_for_top_level_items(self) -> None:
        source = """flowchart TD
    start
    QtEvenLoop
    subgraph Main["main"]
        direction TB
        main["main()"]
    end
    subgraph RenderApp["RenderApp"]
        direction TB
        worker["worker()"]
    end"""

        diagram = self.parser.parse(source, index=0)
        boxes = []
        for node in diagram.nodes:
            if node.parent_subgraph is None:
                boxes.append((node.x, node.y, node.width, node.height))
        for subgraph in diagram.subgraphs:
            if subgraph.parent_subgraph is None:
                boxes.append((subgraph.x, subgraph.y, subgraph.width, subgraph.height))

        for index, left in enumerate(boxes):
            for right in boxes[index + 1 :]:
                self.assertFalse(self._boxes_overlap(left, right))

    def test_serialize_and_parse_edge_styles_round_trip(self) -> None:
        diagram = MermaidDiagram(
            diagram_id="diagram_1",
            title="Diagram 1",
            chart_type="flowchart",
            direction="TD",
            source="",
            nodes=[
                NodeModel(node_id="start", label="start"),
                NodeModel(node_id="middle", label="middle"),
                NodeModel(node_id="done", label="done"),
            ],
            edges=[
                EdgeModel(source="start", target="middle", label="next", style="solid"),
                EdgeModel(source="middle", target="done", label="", style="dotted"),
            ],
        )

        serialized = self.parser.serialize(diagram)
        reparsed = self.parser.parse(serialized, index=0)

        self.assertEqual(len(reparsed.edges), 2)
        self.assertEqual(reparsed.edges[0].label, "next")
        self.assertEqual(reparsed.edges[0].style, "solid")
        self.assertEqual(reparsed.edges[1].style, "dotted")

    def test_diagram_editor_node_operations_keep_edges_consistent(self) -> None:
        diagram = MermaidDiagram(
            diagram_id="diagram_1",
            title="Diagram 1",
            chart_type="flowchart",
            direction="TD",
            source="",
            nodes=[
                NodeModel(node_id="start", label="start"),
                NodeModel(node_id="done", label="done"),
            ],
            edges=[EdgeModel(source="start", target="done", label="", style="solid")],
        )

        self.diagram_editor.add_node(diagram, node_id="middle", label="middle")
        self.diagram_editor.rename_node(
            diagram,
            node_id="middle",
            new_id="step",
            new_label="step label",
        )

        self.assertEqual(len(diagram.nodes), 3)
        self.assertEqual(self.diagram_editor.find_node(diagram, "step").label, "step label")

        diagram.edges.append(
            EdgeModel(source="step", target="done", label="go", style="solid")
        )
        self.diagram_editor.delete_node(diagram, "step")

        self.assertIsNone(self.diagram_editor.find_node(diagram, "step"))
        self.assertEqual(len(diagram.edges), 1)
        self.assertEqual(diagram.edges[0].source, "start")

    def test_diagram_editor_subgraph_operations_update_children(self) -> None:
        diagram = MermaidDiagram(
            diagram_id="diagram_1",
            title="Diagram 1",
            chart_type="flowchart",
            direction="TD",
            source="",
            nodes=[],
            edges=[],
            subgraphs=[],
        )

        self.diagram_editor.add_subgraph(diagram, subgraph_id="main", title="Main")
        self.diagram_editor.add_node(
            diagram,
            node_id="task",
            label="Task",
            parent_subgraph="main",
        )
        self.diagram_editor.add_subgraph(
            diagram,
            subgraph_id="nested",
            title="Nested",
            parent_subgraph="main",
        )

        self.diagram_editor.rename_subgraph(
            diagram,
            subgraph_id="main",
            new_id="root",
            new_title="Root",
        )

        self.assertEqual(self.diagram_editor.find_node(diagram, "task").parent_subgraph, "root")
        self.assertEqual(
            self.diagram_editor.find_subgraph(diagram, "nested").parent_subgraph,
            "root",
        )

        self.diagram_editor.delete_subgraph(diagram, "root")
        self.assertEqual(diagram.subgraphs, [])
        self.assertEqual(diagram.nodes, [])

    def test_diagram_editor_normalize_clears_dangling_references(self) -> None:
        diagram = MermaidDiagram(
            diagram_id="diagram_1",
            title="Diagram 1",
            chart_type="flowchart",
            direction="TD",
            source="",
            nodes=[
                NodeModel(node_id="start", label="start", parent_subgraph="missing"),
                NodeModel(node_id="done", label="done"),
            ],
            edges=[
                EdgeModel(source="start", target="done", label="", style="solid"),
                EdgeModel(source="missing", target="done", label="", style="solid"),
            ],
            subgraphs=[SubgraphModel(subgraph_id="group", title="Group", parent_subgraph="missing")],
        )

        normalized = self.diagram_editor.normalize(diagram)

        self.assertIsNone(normalized.nodes[0].parent_subgraph)
        self.assertIsNone(normalized.subgraphs[0].parent_subgraph)
        self.assertEqual(len(normalized.edges), 1)

    def test_diagram_editor_promote_node_to_subgraph_keeps_external_edges(self) -> None:
        diagram = MermaidDiagram(
            diagram_id="diagram_1",
            title="Diagram 1",
            chart_type="flowchart",
            direction="TD",
            source="",
            nodes=[
                NodeModel(node_id="entry", label="Entry"),
                NodeModel(node_id="step", label="Step"),
            ],
            edges=[EdgeModel(source="entry", target="step", label="", style="solid")],
        )

        subgraph, child = self.diagram_editor.promote_node_to_subgraph(diagram, "step")

        self.assertEqual(subgraph.subgraph_id, "step")
        self.assertEqual(child.parent_subgraph, "step")
        self.assertEqual(diagram.edges[0].target, "step")

    def test_markdown_loader_extracts_multiple_mermaid_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.md"
            path.write_text(WORKFLOW_SAMPLE, encoding="utf-8")

            document = MarkdownLoader().load(path)

        self.assertEqual(len(document.diagrams), 2)
        self.assertEqual(document.diagrams[0].diagram_id, "diagram_1")
        self.assertEqual(document.diagrams[1].diagram_id, "diagram_2")

    def test_preview_service_builds_standardized_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.md"
            path.write_text(WORKFLOW_SAMPLE, encoding="utf-8")

            payload = build_preview_response(path, request_id="req-1")

        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["request_id"], "req-1")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["payload"]["diagram_count"], 2)
        self.assertEqual(len(payload["payload"]["diagrams"]), 2)
        json.dumps(payload)

    def test_export_svg_action_writes_svg_artifacts(self) -> None:
        if run_action is None:
            self.skipTest("PySide6 is not available in the current Python environment.")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            markdown_path = temp_root / "sample.md"
            markdown_path.write_text(WORKFLOW_SAMPLE, encoding="utf-8")

            response = run_action(
                action_name="export_svg",
                project_root=temp_root,
                request_id="req-export",
                markdown_file="sample.md",
            )

            self.assertEqual(response["schema_version"], "1.0")
            self.assertEqual(response["request_id"], "req-export")
            self.assertEqual(response["status"], "ok")
            self.assertEqual(len(response["artifacts"]), 2)

            first_svg = Path(response["artifacts"][0]["path"])
            self.assertTrue(first_svg.exists())
            self.assertIn("<svg", first_svg.read_text(encoding="utf-8"))

    def test_export_png_action_writes_png_artifacts(self) -> None:
        if run_action is None:
            self.skipTest("PySide6 is not available in the current Python environment.")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            markdown_path = temp_root / "sample.md"
            markdown_path.write_text(WORKFLOW_SAMPLE, encoding="utf-8")

            response = run_action(
                action_name="export_png",
                project_root=temp_root,
                request_id="req-png",
                markdown_file="sample.md",
                diagram_id="diagram_1",
            )

            self.assertEqual(response["schema_version"], "1.0")
            self.assertEqual(response["request_id"], "req-png")
            self.assertEqual(response["status"], "ok")
            self.assertEqual(response["payload"]["record_type"], "action.export_png")
            self.assertEqual(len(response["artifacts"]), 1)

            first_png = Path(response["artifacts"][0]["path"])
            self.assertTrue(first_png.exists())
            self.assertEqual(first_png.suffix, ".png")
            self.assertEqual(first_png.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    @staticmethod
    def _boxes_overlap(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> bool:
        lx, ly, lw, lh = left
        rx, ry, rw, rh = right
        return not (
            lx + lw <= rx
            or rx + rw <= lx
            or ly + lh <= ry
            or ry + rh <= ly
        )


if __name__ == "__main__":
    unittest.main()
