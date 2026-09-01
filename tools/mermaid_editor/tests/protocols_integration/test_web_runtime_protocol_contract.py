from __future__ import annotations

from pathlib import Path
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[2]
MAIN_ENTRY = (
    TOOL_ROOT / "src" / "ptd_tool_mermaid_editor" / "presentation" / "web" / "index.html"
)


class WebRuntimeProtocolContractTest(unittest.TestCase):
    def test_web_entry_uses_runtime_message_dispatcher(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")

        self.assertIn('pageReady: "lifecycle.page_ready"', html)
        self.assertIn('diagramSave: "diagram.save"', html)
        self.assertIn('selectionSync: "selection.sync"', html)
        self.assertIn('statusUpdate: "status.update"', html)
        self.assertIn('bridge.postMessage(JSON.stringify(message));', html)

    def test_web_entry_keeps_legacy_bridge_fallbacks(self) -> None:
        html = MAIN_ENTRY.read_text(encoding="utf-8")

        self.assertIn('typeof bridge.pageReady === "function"', html)
        self.assertIn('typeof bridge.setStatus === "function"', html)
        self.assertIn('typeof bridge.saveDiagram === "function"', html)
        self.assertIn('typeof bridge.selectionChanged === "function"', html)


if __name__ == "__main__":
    unittest.main()
