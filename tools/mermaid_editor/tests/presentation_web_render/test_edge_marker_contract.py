"""Static contract checks for SVG edge marker rendering."""

from __future__ import annotations

from pathlib import Path
import re
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[2]
MAIN_ENTRY = (
    TOOL_ROOT / "src" / "ptd_tool_mermaid_editor" / "presentation" / "web" / "index.html"
)
COMPAT_ENTRY = (
    TOOL_ROOT / "src" / "ptd_tool_mermaid_editor" / "app" / "static" / "editor.html"
)


class EdgeMarkerContractTest(unittest.TestCase):
    """Lock edge width and marker rendering rules in the web editor HTML."""

    def test_main_entry_keeps_markers_in_user_space(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertEqual(html.count('markerUnits="userSpaceOnUse"'), 2)
        self.assertIn('fill="#a5b4fc" stroke="none"', html)
        self.assertIn('fill="#f59e0b" stroke="none"', html)

    def test_main_entry_drives_edge_width_in_javascript(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertIn("function getEdgeStrokeWidth(style, selected)", html)
        self.assertIn(
            'line.style.strokeWidth = String(getEdgeStrokeWidth(edgeStyle, selected));',
            html,
        )
        self.assertIn(
            'line.style.markerEnd = edgeStyle === "plain" ? "none" : "url(#arrowhead)";',
            html,
        )
        self.assertIsNone(re.search(r"\.edge\.thick\s*\{[^}]*stroke-width", html))
        self.assertIsNone(re.search(r"\.edge\.selected\s*\{[^}]*stroke-width", html))

    def test_main_entry_exposes_anchor_handle_editing_contract(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertIn('<g id="handles-layer"></g>', html)
        self.assertIn("function renderAnchorHandles()", html)
        self.assertIn("function applyEdgeAnchorSide(edgeIndex, endpoint, side)", html)
        self.assertIn("source_anchor_side", html)
        self.assertIn("target_anchor_side", html)

    def test_plain_and_draft_edge_contracts_remain_intact(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")
        self.assertIn(".edge.plain { marker-end: none; }", html)
        self.assertIn("marker-end: url(#draft-arrowhead);", html)

    def test_compatibility_copy_uses_same_edge_marker_contract(self) -> None:
        compat_html = COMPAT_ENTRY.read_text(encoding="utf-8")
        shared_fragments = (
            'markerUnits="userSpaceOnUse"',
            'fill="#a5b4fc" stroke="none"',
            'fill="#f59e0b" stroke="none"',
            "function getEdgeStrokeWidth(style, selected)",
            'line.style.markerEnd = edgeStyle === "plain" ? "none" : "url(#arrowhead)";',
        )
        for fragment in shared_fragments:
            self.assertIn(fragment, compat_html)


if __name__ == "__main__":
    unittest.main()
