from __future__ import annotations

from ptd_tool_mermaid_editor.domain.graph import EdgeModel, MermaidDiagram, NodeModel, SubgraphModel


class DiagramEditor:
    """Apply structure edits to a Mermaid diagram and keep references consistent."""

    def add_node(
        self,
        diagram: MermaidDiagram,
        node_id: str,
        label: str,
        parent_subgraph: str | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> NodeModel:
        """Add a node and validate identifier and parent references."""

        if self.find_node(diagram, node_id) is not None:
            raise ValueError(f"Node already exists: {node_id}")
        if parent_subgraph is not None and self.find_subgraph(diagram, parent_subgraph) is None:
            raise ValueError(f"Parent subgraph does not exist: {parent_subgraph}")

        node = NodeModel(
            node_id=node_id,
            label=label,
            parent_subgraph=parent_subgraph,
            x=x,
            y=y,
        )
        diagram.nodes.append(node)
        return node

    def rename_node(
        self,
        diagram: MermaidDiagram,
        node_id: str,
        new_id: str,
        new_label: str | None = None,
    ) -> NodeModel:
        """Rename a node and update all edge references that point to it."""

        node = self._require_node(diagram, node_id)
        if new_id != node_id and self.find_node(diagram, new_id) is not None:
            raise ValueError(f"Node already exists: {new_id}")

        for edge in diagram.edges:
            if edge.source == node_id:
                edge.source = new_id
            if edge.target == node_id:
                edge.target = new_id

        node.node_id = new_id
        node.label = new_label or new_id
        return node

    def delete_node(self, diagram: MermaidDiagram, node_id: str) -> None:
        """Delete a node and all edges connected to it."""

        self._require_node(diagram, node_id)
        diagram.nodes = [node for node in diagram.nodes if node.node_id != node_id]
        diagram.edges = [
            edge
            for edge in diagram.edges
            if edge.source != node_id and edge.target != node_id
        ]

    def add_subgraph(
        self,
        diagram: MermaidDiagram,
        subgraph_id: str,
        title: str,
        parent_subgraph: str | None = None,
        direction: str | None = "TB",
        x: float | None = None,
        y: float | None = None,
        width: float = 320.0,
        height: float = 220.0,
    ) -> SubgraphModel:
        """Add a subgraph and validate nesting references."""

        if self.find_subgraph(diagram, subgraph_id) is not None:
            raise ValueError(f"Subgraph already exists: {subgraph_id}")
        if parent_subgraph is not None and self.find_subgraph(diagram, parent_subgraph) is None:
            raise ValueError(f"Parent subgraph does not exist: {parent_subgraph}")

        subgraph = SubgraphModel(
            subgraph_id=subgraph_id,
            title=title,
            parent_subgraph=parent_subgraph,
            direction=direction,
            x=x,
            y=y,
            width=width,
            height=height,
        )
        diagram.subgraphs.append(subgraph)
        return subgraph

    def rename_subgraph(
        self,
        diagram: MermaidDiagram,
        subgraph_id: str,
        new_id: str,
        new_title: str | None = None,
    ) -> SubgraphModel:
        """Rename a subgraph and update its children to point to the new parent id."""

        subgraph = self._require_subgraph(diagram, subgraph_id)
        if new_id != subgraph_id and self.find_subgraph(diagram, new_id) is not None:
            raise ValueError(f"Subgraph already exists: {new_id}")

        for node in diagram.nodes:
            if node.parent_subgraph == subgraph_id:
                node.parent_subgraph = new_id

        for child_subgraph in diagram.subgraphs:
            if child_subgraph.parent_subgraph == subgraph_id:
                child_subgraph.parent_subgraph = new_id

        for edge in diagram.edges:
            if edge.source == subgraph_id:
                edge.source = new_id
            if edge.target == subgraph_id:
                edge.target = new_id

        subgraph.subgraph_id = new_id
        subgraph.title = new_title or new_id
        return subgraph

    def delete_subgraph(self, diagram: MermaidDiagram, subgraph_id: str) -> None:
        """Delete a subgraph, all descendant subgraphs, nodes, and dependent edges."""

        self._require_subgraph(diagram, subgraph_id)
        to_delete = {subgraph_id}
        changed = True

        while changed:
            changed = False
            for subgraph in diagram.subgraphs:
                if (
                    subgraph.parent_subgraph in to_delete
                    and subgraph.subgraph_id not in to_delete
                ):
                    to_delete.add(subgraph.subgraph_id)
                    changed = True

        removed_node_ids = {
            node.node_id for node in diagram.nodes if node.parent_subgraph in to_delete
        }
        diagram.subgraphs = [
            subgraph for subgraph in diagram.subgraphs if subgraph.subgraph_id not in to_delete
        ]
        diagram.nodes = [
            node for node in diagram.nodes if node.parent_subgraph not in to_delete
        ]
        diagram.edges = [
            edge
            for edge in diagram.edges
            if edge.source not in removed_node_ids
            and edge.target not in removed_node_ids
            and edge.source not in to_delete
            and edge.target not in to_delete
        ]

    def promote_node_to_subgraph(
        self,
        diagram: MermaidDiagram,
        node_id: str,
    ) -> tuple[SubgraphModel, NodeModel]:
        """Convert a node into a subgraph and keep external edge references valid."""

        node = self._require_node(diagram, node_id)
        if self.find_subgraph(diagram, node.node_id) is not None:
            raise ValueError(f"Subgraph already exists: {node.node_id}")

        title = node.label or node.node_id
        subgraph = SubgraphModel(
            subgraph_id=node.node_id,
            title=title,
            parent_subgraph=node.parent_subgraph,
            x=(node.x or 80.0) - 24.0,
            y=(node.y or 80.0) - 36.0,
            width=max(node.width + 64.0, 260.0),
            height=max(node.height + 88.0, 180.0),
        )
        child_id = self._make_unique_node_id(diagram, f"{node.node_id}_content")
        child = NodeModel(
            node_id=child_id,
            label=title,
            parent_subgraph=subgraph.subgraph_id,
            x=node.x,
            y=node.y,
            width=node.width,
            height=node.height,
        )

        diagram.nodes = [item for item in diagram.nodes if item.node_id != node_id]
        diagram.subgraphs.append(subgraph)
        diagram.nodes.append(child)
        return subgraph, child

    def normalize(self, diagram: MermaidDiagram) -> MermaidDiagram:
        """Remove dangling references created by external edits before serialization."""

        valid_subgraph_ids = {subgraph.subgraph_id for subgraph in diagram.subgraphs}
        valid_node_ids = {node.node_id for node in diagram.nodes}

        for node in diagram.nodes:
            if node.parent_subgraph not in valid_subgraph_ids:
                node.parent_subgraph = None

        for subgraph in diagram.subgraphs:
            if subgraph.parent_subgraph == subgraph.subgraph_id:
                subgraph.parent_subgraph = None
            elif subgraph.parent_subgraph not in valid_subgraph_ids:
                subgraph.parent_subgraph = None

        valid_endpoint_ids = valid_node_ids | valid_subgraph_ids
        diagram.edges = [
            edge
            for edge in diagram.edges
            if edge.source in valid_endpoint_ids and edge.target in valid_endpoint_ids
        ]
        return diagram

    @staticmethod
    def find_node(diagram: MermaidDiagram, node_id: str) -> NodeModel | None:
        """Find a node by identifier."""

        return next((node for node in diagram.nodes if node.node_id == node_id), None)

    @staticmethod
    def find_subgraph(diagram: MermaidDiagram, subgraph_id: str) -> SubgraphModel | None:
        """Find a subgraph by identifier."""

        return next(
            (subgraph for subgraph in diagram.subgraphs if subgraph.subgraph_id == subgraph_id),
            None,
        )

    def _require_node(self, diagram: MermaidDiagram, node_id: str) -> NodeModel:
        node = self.find_node(diagram, node_id)
        if node is None:
            raise ValueError(f"Node does not exist: {node_id}")
        return node

    def _require_subgraph(self, diagram: MermaidDiagram, subgraph_id: str) -> SubgraphModel:
        subgraph = self.find_subgraph(diagram, subgraph_id)
        if subgraph is None:
            raise ValueError(f"Subgraph does not exist: {subgraph_id}")
        return subgraph

    def _make_unique_node_id(self, diagram: MermaidDiagram, base_id: str) -> str:
        candidate = base_id
        suffix = 1
        while self.find_node(diagram, candidate) is not None:
            suffix += 1
            candidate = f"{base_id}_{suffix}"
        return candidate
