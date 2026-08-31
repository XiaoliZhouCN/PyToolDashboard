from __future__ import annotations

import unittest

try:
    from ptd_tool_mermaid_editor.presentation.qt.main_window import MainWindow
except ImportError:  # pragma: no cover - optional in headless environments
    MainWindow = None


@unittest.skipIf(MainWindow is None, "PySide6 is not available")
class MainWindowLogicTest(unittest.TestCase):
    def test_subgraph_summary_uses_title_without_prefix(self) -> None:
        summary = MainWindow._build_detail_summary(
            {
                "kind": "subgraph",
                "id": "cluster_a",
                "label": "Very Long Subgraph Title",
            }
        )
        self.assertEqual(summary, "Very Long Subgraph Title")

    def test_subgraph_summary_falls_back_to_identifier(self) -> None:
        summary = MainWindow._build_detail_summary(
            {
                "kind": "subgraph",
                "id": "cluster_a",
                "label": "",
            }
        )
        self.assertEqual(summary, "cluster_a")

    def test_left_panel_width_is_clamped_to_quarter_and_half(self) -> None:
        self.assertEqual(MainWindow._bounded_left_width(total_width=1200, left_width=200), 300)
        self.assertEqual(MainWindow._bounded_left_width(total_width=1200, left_width=700), 600)
        self.assertEqual(MainWindow._bounded_left_width(total_width=1200, left_width=400), 400)


if __name__ == "__main__":
    unittest.main()
