from __future__ import annotations

import itertools
import re
from collections import defaultdict

from ptd_tool_mermaid_editor.domain.graph import (
    EdgeModel,
    MermaidDiagram,
    NodeModel,
    SubgraphModel,
)


EDGE_CONNECTOR_RE = re.compile(r"(==.*?==>|--.*?-->|==>|-->|-\.->|---)")
EDGE_ANCHOR_COMMENT_RE = re.compile(
    r"^%%\s*ptd-edge-anchors:\s*source=(?P<source>auto|top|right|bottom|left)\s*,\s*target=(?P<target>auto|top|right|bottom|left)\s*$",
    re.IGNORECASE,
)
SUBGRAPH_RE = re.compile(
    r'^subgraph\s+(?P<identifier>[A-Za-z0-9_]+)(?:\[(?P<label>".*"|.+)\])?$'
)
NODE_RE = re.compile(r"^(?P<identifier>[A-Za-z0-9_]+)(?:\[(?P<label>[\s\S]+)\])?$")


class MermaidParser:
    """Parse and serialize the supported Mermaid flowchart subset."""

    def parse(self, source: str, index: int = 0) -> MermaidDiagram:
        lines = source.strip().splitlines()
        if not lines:
            raise ValueError("Mermaid source is empty.")

        header = lines[0].strip()
        header_parts = header.split()
        if len(header_parts) < 2:
            raise ValueError(f"Unsupported Mermaid header: {header}")

        chart_type = header_parts[0]
        direction = header_parts[1]
        diagram = MermaidDiagram(
            diagram_id=f"diagram_{index + 1}",
            title=f"Diagram {index + 1}",
            chart_type=chart_type,
            direction=direction,
            source=source.strip(),
        )

        node_map: dict[str, NodeModel] = {}
        subgraph_map: dict[str, SubgraphModel] = {}
        subgraph_stack: list[str] = []

        edge_statements: list[tuple[str, str | None, dict[str, str] | None]] = []
        pending_edge_anchor_sides: dict[str, str] | None = None

        for statement in self._tokenize_statements(lines[1:]):
            anchor_comment = self._parse_edge_anchor_comment(statement)
            if anchor_comment is not None:
                pending_edge_anchor_sides = anchor_comment
                continue

            if statement == "end":
                pending_edge_anchor_sides = None
                if subgraph_stack:
                    subgraph_stack.pop()
                continue

            if statement.startswith("direction "):
                pending_edge_anchor_sides = None
                current_direction = statement.split(maxsplit=1)[1]
                if subgraph_stack:
                    subgraph_map[subgraph_stack[-1]].direction = current_direction
                else:
                    diagram.direction = current_direction
                continue

            if statement.startswith("subgraph "):
                pending_edge_anchor_sides = None
                match = SUBGRAPH_RE.match(statement)
                if not match:
                    continue
                subgraph_id = match.group("identifier")
                title_text = self._normalize_label(match.group("label") or subgraph_id)
                subgraph = SubgraphModel(
                    subgraph_id=subgraph_id,
                    title=title_text,
                    parent_subgraph=subgraph_stack[-1] if subgraph_stack else None,
                )
                diagram.subgraphs.append(subgraph)
                subgraph_map[subgraph_id] = subgraph
                subgraph_stack.append(subgraph_id)
                continue

            if self._looks_like_edge(statement):
                edge_statements.append(
                    (
                        statement,
                        subgraph_stack[-1] if subgraph_stack else None,
                        pending_edge_anchor_sides,
                    )
                )
                pending_edge_anchor_sides = None
                continue

            pending_edge_anchor_sides = None
            node = self._parse_node(
                statement=statement,
                parent_subgraph=subgraph_stack[-1] if subgraph_stack else None,
            )
            if node and node.node_id not in node_map:
                diagram.nodes.append(node)
                node_map[node.node_id] = node

        for statement, parent_id, edge_anchor_sides in edge_statements:
            self._parse_edge_chain(
                diagram=diagram,
                statement=statement,
                node_map=node_map,
                subgraph_map=subgraph_map,
                current_parent=parent_id,
                edge_anchor_sides=edge_anchor_sides,
            )

        self.assign_default_layout(diagram)
        diagram.source = self.serialize(diagram)
        return diagram

    def serialize(self, diagram: MermaidDiagram) -> str:
        """Serialize an in-memory diagram back to Mermaid source."""

        lines = [f"{diagram.chart_type} {diagram.direction}"]
        children_by_parent_subgraph = defaultdict(list)
        node_map = {node.node_id: node for node in diagram.nodes}
        subgraph_map = {subgraph.subgraph_id: subgraph for subgraph in diagram.subgraphs}

        for node in diagram.nodes:
            children_by_parent_subgraph[node.parent_subgraph].append(("node", node.node_id))
        for subgraph in diagram.subgraphs:
            children_by_parent_subgraph[subgraph.parent_subgraph].append(
                ("subgraph", subgraph.subgraph_id)
            )

        def emit_subgraph(subgraph_id: str, indent: int) -> None:
            subgraph = subgraph_map[subgraph_id]
            prefix = " " * indent
            lines.append(
                f'{prefix}subgraph {subgraph.subgraph_id}["{self._escape_label(subgraph.title)}"]'
            )
            if subgraph.direction:
                lines.append(f"{prefix}    direction {subgraph.direction}")
            for kind, child_id in children_by_parent_subgraph.get(subgraph.subgraph_id, []):
                if kind == "node":
                    lines.append(self._serialize_node(node_map[child_id], indent + 4))
                else:
                    emit_subgraph(child_id, indent + 4)
            lines.append(f"{prefix}end")

        for kind, child_id in children_by_parent_subgraph.get(None, []):
            if kind == "node":
                lines.append(self._serialize_node(node_map[child_id], 4))
            else:
                emit_subgraph(child_id, 4)

        if diagram.edges:
            lines.append("")
            for edge in diagram.edges:
                if edge.source_anchor_side != "auto" or edge.target_anchor_side != "auto":
                    lines.append(
                        "    %% ptd-edge-anchors: "
                        f"source={edge.source_anchor_side}, target={edge.target_anchor_side}"
                    )
                connector = self._edge_connector(edge)
                lines.append(f"    {edge.source} {connector} {edge.target}".rstrip())

        return "\n".join(lines)

    def assign_default_layout(self, diagram: MermaidDiagram) -> None:
        """Assign a stable default layout when no sidecar data exists."""

        nodes_by_parent = defaultdict(list)
        subgraphs_by_parent = defaultdict(list)

        for node in diagram.nodes:
            nodes_by_parent[node.parent_subgraph].append(node)
        for subgraph in diagram.subgraphs:
            subgraphs_by_parent[subgraph.parent_subgraph].append(subgraph)

        def is_horizontal(direction: str | None) -> bool:
            return (direction or "").upper() in {"LR", "RL"}

        def group_direction(parent_id: str | None) -> str:
            if parent_id is None:
                return diagram.direction
            parent_subgraph = next(
                (subgraph for subgraph in diagram.subgraphs if subgraph.subgraph_id == parent_id),
                None,
            )
            return parent_subgraph.direction or diagram.direction

        def layout_group(parent_id: str | None, origin_x: float, origin_y: float) -> tuple[float, float]:
            current_y = origin_y
            current_x = origin_x
            horizontal = is_horizontal(group_direction(parent_id))
            nodes = nodes_by_parent.get(parent_id, [])
            for node_index, node in enumerate(nodes):
                if horizontal:
                    column = node_index
                    if node.x is None:
                        node.x = origin_x + column * 220
                    if node.y is None:
                        node.y = origin_y
                else:
                    column = node_index % 2
                    row = node_index // 2
                    if node.x is None:
                        node.x = origin_x + column * 230
                    if node.y is None:
                        node.y = current_y + row * 108

            if nodes:
                if horizontal:
                    current_x += len(nodes) * 220 + 36
                else:
                    current_y += (((len(nodes) - 1) // 2) + 1) * 108 + 24

            for subgraph in subgraphs_by_parent.get(parent_id, []):
                if horizontal:
                    subgraph_x = current_x
                    subgraph_y = origin_y - 24
                else:
                    subgraph_x = origin_x - 24
                    subgraph_y = current_y
                inner_origin_x = subgraph_x + 40
                inner_origin_y = subgraph_y + 72
                content_right, content_bottom = layout_group(
                    subgraph.subgraph_id,
                    inner_origin_x,
                    inner_origin_y,
                )

                for child_node in nodes_by_parent.get(subgraph.subgraph_id, []):
                    content_right = max(content_right, (child_node.x or inner_origin_x) + child_node.width)

                for child_subgraph in subgraphs_by_parent.get(subgraph.subgraph_id, []):
                    content_right = max(
                        content_right,
                        (child_subgraph.x or inner_origin_x) + child_subgraph.width,
                    )

                subgraph.x = subgraph_x if subgraph.x is None else subgraph.x
                subgraph.y = subgraph_y if subgraph.y is None else subgraph.y
                subgraph.width = max(280.0, content_right - subgraph.x + 36.0)
                subgraph.height = max(180.0, content_bottom - subgraph.y + 24.0)
                if horizontal:
                    current_x = subgraph.x + subgraph.width + 36.0
                else:
                    current_y = subgraph.y + subgraph.height + 36.0

            max_x = origin_x + 220.0
            max_y = origin_y + 80.0
            for node in nodes:
                max_x = max(max_x, (node.x or origin_x) + node.width)
                max_y = max(max_y, (node.y or origin_y) + node.height)
            for subgraph in subgraphs_by_parent.get(parent_id, []):
                max_x = max(max_x, (subgraph.x or origin_x) + subgraph.width)
                max_y = max(max_y, (subgraph.y or origin_y) + subgraph.height)
            return max_x, max_y

        layout_group(None, 96.0, 96.0)

    def _parse_edge_chain(
        self,
        diagram: MermaidDiagram,
        statement: str,
        node_map: dict[str, NodeModel],
        subgraph_map: dict[str, SubgraphModel],
        current_parent: str | None,
        edge_anchor_sides: dict[str, str] | None = None,
    ) -> None:
        tokens = [token.strip() for token in EDGE_CONNECTOR_RE.split(statement) if token.strip()]
        if len(tokens) < 3:
            return

        for pair_index, (left, connector, right) in enumerate(
            itertools.zip_longest(
                tokens[0::2],
                tokens[1::2],
                tokens[2::2],
            )
        ):
            if not left or not connector or not right:
                continue
            left_id = self._parse_or_get_endpoint_id(
                left,
                diagram,
                node_map,
                subgraph_map,
                current_parent,
            )
            right_id = self._parse_or_get_endpoint_id(
                right,
                diagram,
                node_map,
                subgraph_map,
                current_parent,
            )
            label, style = self._parse_connector(connector)
            source_anchor_side = "auto"
            target_anchor_side = "auto"
            if edge_anchor_sides and pair_index == 0:
                source_anchor_side = edge_anchor_sides.get("source", "auto")
                target_anchor_side = edge_anchor_sides.get("target", "auto")
            diagram.edges.append(
                EdgeModel(
                    source=left_id,
                    target=right_id,
                    label=label,
                    style=style,
                    source_anchor_side=source_anchor_side,
                    target_anchor_side=target_anchor_side,
                )
            )

    def _parse_or_get_endpoint_id(
        self,
        raw: str,
        diagram: MermaidDiagram,
        node_map: dict[str, NodeModel],
        subgraph_map: dict[str, SubgraphModel],
        parent_subgraph: str | None,
    ) -> str:
        subgraph_id = self._parse_reference_identifier(raw)
        if subgraph_id in subgraph_map:
            return subgraph_id

        node = self._parse_node(raw, parent_subgraph=parent_subgraph)
        if node is None:
            raise ValueError(f"Unable to parse node token: {raw}")
        existing = node_map.get(node.node_id)
        if existing is not None:
            return existing.node_id
        node_map[node.node_id] = node
        diagram.nodes.append(node)
        return node.node_id

    def _parse_node(self, statement: str, parent_subgraph: str | None) -> NodeModel | None:
        match = NODE_RE.match(statement.strip())
        if not match:
            return None
        identifier = match.group("identifier")
        label = self._normalize_label(match.group("label") or identifier)
        return NodeModel(
            node_id=identifier,
            label=label,
            parent_subgraph=parent_subgraph,
        )

    def _parse_reference_identifier(self, statement: str) -> str:
        match = NODE_RE.match(statement.strip())
        if not match:
            return statement.strip()
        return match.group("identifier")

    def _tokenize_statements(self, lines: list[str]) -> list[str]:
        statements: list[str] = []
        buffer: list[str] = []
        balance = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            balance += stripped.count("[") - stripped.count("]")
            buffer.append(stripped)
            if balance <= 0:
                statements.append("\n".join(buffer))
                buffer = []
                balance = 0

        if buffer:
            statements.append("\n".join(buffer))
        return statements

    @staticmethod
    def _looks_like_edge(statement: str) -> bool:
        return bool(EDGE_CONNECTOR_RE.search(statement))

    @staticmethod
    def _normalize_label(label: str) -> str:
        cleaned = label.strip()
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        if cleaned.startswith("`") and cleaned.endswith("`"):
            cleaned = cleaned[1:-1]
        return cleaned

    @staticmethod
    def _escape_label(label: str) -> str:
        return label.replace('"', '\\"')

    @staticmethod
    def _parse_connector(connector: str) -> tuple[str, str]:
        cleaned = connector.strip()
        if cleaned == "==>":
            return "", "thick"
        if cleaned == "-->":
            return "", "solid"
        if cleaned == "-.->":
            return "", "dotted"
        if cleaned == "---":
            return "", "plain"
        if cleaned.startswith("==") and cleaned.endswith("==>"):
            return cleaned[2:-3].strip(), "thick"
        if cleaned.startswith("--") and cleaned.endswith("-->"):
            return cleaned[2:-3].strip(), "solid"
        return "", "solid"

    @staticmethod
    def _parse_edge_anchor_comment(statement: str) -> dict[str, str] | None:
        match = EDGE_ANCHOR_COMMENT_RE.match(statement.strip())
        if not match:
            return None
        return {
            "source": match.group("source").lower(),
            "target": match.group("target").lower(),
        }

    @staticmethod
    def _edge_connector(edge: EdgeModel) -> str:
        if edge.style == "thick":
            return f"=={edge.label}==>" if edge.label else "==>"
        if edge.style == "dotted":
            return "-.->"
        if edge.style == "plain":
            return "---"
        return f"--{edge.label}-->" if edge.label else "-->"

    def _serialize_node(self, node: NodeModel, indent: int) -> str:
        prefix = " " * indent
        if node.label == node.node_id:
            return f"{prefix}{node.node_id}"
        return f'{prefix}{node.node_id}["{self._escape_label(node.label or node.node_id)}"]'


__all__ = ["MermaidParser"]
