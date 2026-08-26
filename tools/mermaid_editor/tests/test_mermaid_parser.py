from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.services.markdown_loader import MarkdownLoader
from app.services.mermaid_parser import MermaidParser


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

    def test_markdown_loader_extracts_multiple_mermaid_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.md"
            path.write_text(WORKFLOW_SAMPLE, encoding="utf-8")

            document = MarkdownLoader().load(path)

        self.assertEqual(len(document.diagrams), 2)
        self.assertEqual(document.diagrams[0].diagram_id, "diagram_1")
        self.assertEqual(document.diagrams[1].diagram_id, "diagram_2")


if __name__ == "__main__":
    unittest.main()
