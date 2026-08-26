from __future__ import annotations

import itertools
import re
from collections import defaultdict

from app.models.graph import EdgeModel, MermaidDiagram, NodeModel, SubgraphModel


EDGE_CONNECTOR_RE = re.compile(r"(==.*?==>|--.*?-->|==>|-->|-\.->|---)")
SUBGRAPH_RE = re.compile(
    r'^subgraph\s+(?P<identifier>[A-Za-z0-9_]+)(?:\[(?P<label>".*"|.+)\])?$'
)
NODE_RE = re.compile(
    r"^(?P<identifier>[A-Za-z0-9_]+)(?:\[(?P<label>[\s\S]+)\])?$"
)


class MermaidParser:
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
        title = f"Diagram {index + 1}"
        diagram = MermaidDiagram(
            diagram_id=f"diagram_{index + 1}",
            title=title,
            chart_type=chart_type,
            direction=direction,
            source=source.strip(),
        )

        node_map: dict[str, NodeModel] = {}
        subgraph_map: dict[str, SubgraphModel] = {}
        subgraph_stack: list[str] = []

        for statement in self._tokenize_statements(lines[1:]):
            if statement == "end":
                if subgraph_stack:
                    subgraph_stack.pop()
                continue

            if statement.startswith("direction "):
                current_direction = statement.split(maxsplit=1)[1]
                if subgraph_stack:
                    subgraph_map[subgraph_stack[-1]].direction = current_direction
                else:
                    diagram.direction = current_direction
                continue

            if statement.startswith("subgraph "):
                match = SUBGRAPH_RE.match(statement)
                if not match:
                    continue
                subgraph_id = match.group("identifier")
                title_text = self._normalize_label(
                    match.group("label") or subgraph_id
                )
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
                self._parse_edge_chain(
                    diagram=diagram,
                    statement=statement,
                    node_map=node_map,
                    current_parent=subgraph_stack[-1] if subgraph_stack else None,
                )
                continue

            node = self._parse_node(
                statement=statement,
                parent_subgraph=subgraph_stack[-1] if subgraph_stack else None,
            )
            if node and node.node_id not in node_map:
                diagram.nodes.append(node)
                node_map[node.node_id] = node

        self.assign_default_layout(diagram)
        diagram.source = self.serialize(diagram)
        return diagram

    def serialize(self, diagram: MermaidDiagram) -> str:
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
                connector = self._edge_connector(edge)
                lines.append(
                    f"    {edge.source} {connector} {edge.target}".rstrip()
                )

        return "\n".join(lines)

    def assign_default_layout(self, diagram: MermaidDiagram) -> None:
        nodes_by_parent = defaultdict(list)
        subgraphs_by_parent = defaultdict(list)

        for node in diagram.nodes:
            nodes_by_parent[node.parent_subgraph].append(node)
        for subgraph in diagram.subgraphs:
            subgraphs_by_parent[subgraph.parent_subgraph].append(subgraph)

        def walk(parent_id: str | None, origin_x: float, origin_y: float) -> None:
            current_y = origin_y
            for node_index, node in enumerate(nodes_by_parent.get(parent_id, [])):
                if node.x is None:
                    node.x = origin_x + (node_index % 2) * 220
                if node.y is None:
                    node.y = current_y + (node_index // 2) * 100
            used_rows = (len(nodes_by_parent.get(parent_id, [])) + 1) // 2
            current_y += max(used_rows * 100, 80)

            for subgraph in subgraphs_by_parent.get(parent_id, []):
                if subgraph.x is None:
                    subgraph.x = origin_x - 30
                if subgraph.y is None:
                    subgraph.y = current_y
                walk(subgraph.subgraph_id, origin_x + 30, current_y + 70)
                current_y += subgraph.height + 40

        walk(None, 90, 80)

    def _parse_edge_chain(
        self,
        diagram: MermaidDiagram,
        statement: str,
        node_map: dict[str, NodeModel],
        current_parent: str | None,
    ) -> None:
        tokens = [token.strip() for token in EDGE_CONNECTOR_RE.split(statement) if token.strip()]
        if len(tokens) < 3:
            return

        for left, connector, right in itertools.zip_longest(
            tokens[0::2],
            tokens[1::2],
            tokens[2::2],
        ):
            if not left or not connector or not right:
                continue
            left_node = self._parse_or_get_node(
                left,
                diagram,
                node_map,
                current_parent,
            )
            right_node = self._parse_or_get_node(
                right,
                diagram,
                node_map,
                current_parent,
            )
            label, style = self._parse_connector(connector)
            diagram.edges.append(
                EdgeModel(
                    source=left_node.node_id,
                    target=right_node.node_id,
                    label=label,
                    style=style,
                )
            )

    def _parse_or_get_node(
        self,
        raw: str,
        diagram: MermaidDiagram,
        node_map: dict[str, NodeModel],
        parent_subgraph: str | None,
    ) -> NodeModel:
        node = self._parse_node(raw, parent_subgraph=parent_subgraph)
        if node is None:
            raise ValueError(f"Unable to parse node token: {raw}")
        existing = node_map.get(node.node_id)
        if existing is not None:
            return existing
        node_map[node.node_id] = node
        diagram.nodes.append(node)
        return node

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
