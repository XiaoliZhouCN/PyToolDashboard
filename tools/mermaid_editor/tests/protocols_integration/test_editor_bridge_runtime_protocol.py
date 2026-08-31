from __future__ import annotations

import json
import unittest

try:
    from ptd_tool_mermaid_editor.presentation.web.bridge.editor_bridge import EditorBridge
    from ptd_tool_mermaid_editor.protocols import (
        MESSAGE_DIAGRAM_SAVE,
        MESSAGE_PAGE_READY,
        MESSAGE_SELECTION_SYNC,
        MESSAGE_STATUS_UPDATE,
        build_web_to_qt_message,
    )
except ImportError:  # pragma: no cover - optional in headless environments
    EditorBridge = None


@unittest.skipIf(EditorBridge is None, "PySide6 is not available")
class EditorBridgeRuntimeProtocolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = EditorBridge()

    def test_post_message_routes_page_ready(self) -> None:
        events: list[str] = []
        self.bridge.page_ready_signal.connect(lambda: events.append("ready"))

        self.bridge.postMessage(build_web_to_qt_message(MESSAGE_PAGE_READY).to_json())

        self.assertEqual(events, ["ready"])

    def test_post_message_routes_diagram_save_payload(self) -> None:
        payloads: list[str] = []
        self.bridge.diagram_updated.connect(payloads.append)

        self.bridge.postMessage(
            build_web_to_qt_message(
                MESSAGE_DIAGRAM_SAVE,
                payload={
                    "diagram_id": "demo",
                    "nodes": [{"node_id": "n1", "label": "Node 1"}],
                    "edges": [],
                    "subgraphs": [],
                },
            ).to_json()
        )

        self.assertEqual(len(payloads), 1)
        self.assertEqual(json.loads(payloads[0])["diagram_id"], "demo")

    def test_post_message_routes_selection_sync_payload(self) -> None:
        payloads: list[str] = []
        self.bridge.selection_changed.connect(payloads.append)

        self.bridge.postMessage(
            build_web_to_qt_message(
                MESSAGE_SELECTION_SYNC,
                payload={"kind": "node", "count": 1, "id": "n1", "label": "Node 1"},
            ).to_json()
        )

        self.assertEqual(
            json.loads(payloads[0]),
            {"kind": "node", "count": 1, "id": "n1", "label": "Node 1"},
        )

    def test_legacy_methods_are_normalized_into_runtime_routing(self) -> None:
        diagram_payloads: list[str] = []
        status_payloads: list[str] = []
        self.bridge.diagram_updated.connect(diagram_payloads.append)
        self.bridge.status_changed.connect(status_payloads.append)

        self.bridge.saveDiagram('{"diagram_id":"legacy","nodes":[],"edges":[],"subgraphs":[]}')
        self.bridge.setStatus("saved")

        self.assertEqual(json.loads(diagram_payloads[0])["diagram_id"], "legacy")
        self.assertEqual(status_payloads, ["saved"])

    def test_invalid_message_emits_protocol_error_status(self) -> None:
        payloads: list[str] = []
        self.bridge.status_changed.connect(payloads.append)

        self.bridge.postMessage('{"message_type":"","source":"web.canvas","target":"qt.bridge","payload":{}}')
        self.bridge.postMessage(
            build_web_to_qt_message(MESSAGE_STATUS_UPDATE, payload="invalid").to_json()
        )

        self.assertEqual(len(payloads), 2)
        self.assertIn("Protocol error:", payloads[0])
        self.assertIn("Protocol error:", payloads[1])


if __name__ == "__main__":
    unittest.main()
