from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = DASHBOARD_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

cli_module = importlib.import_module("ptd_dashboard.app.cli")
launcher_module = importlib.import_module("ptd_dashboard.launcher")
registry_module = importlib.import_module("ptd_dashboard.registry")
runtime_module = importlib.import_module("ptd_dashboard.services.runtime")

main = cli_module.main
ToolLauncherService = launcher_module.ToolLauncherService
ManifestValidationError = registry_module.ManifestValidationError
ToolRegistryService = registry_module.ToolRegistryService
build_runtime_context = runtime_module.build_runtime_context


class DashboardRegistryTestCase(unittest.TestCase):
    def test_registry_discovers_manifests_from_tools_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_root = temp_root / "subject_project"
            manifest_path = repo_root / "tools" / "demo_tool" / "tool.json"
            manifest_path.parent.mkdir(parents=True)
            project_root.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "tool_id": "demo_tool",
                        "name": "Demo Tool",
                        "version": "0.1.0",
                        "entrypoints": {"launch": "python run.py launch"},
                        "capabilities": ["launch_panel"],
                        "launcher_policy": "standalone_allowed",
                    }
                ),
                encoding="utf-8",
            )

            runtime_context = build_runtime_context(
                project_root=project_root,
                repo_root=repo_root,
            )
            manifests = ToolRegistryService(runtime_context.tools_root).discover_manifests()

        self.assertEqual(len(manifests), 1)
        self.assertEqual(manifests[0].tool_id, "demo_tool")
        self.assertEqual(manifests[0].tool_root, manifest_path.parent.resolve())

    def test_registry_rejects_manifest_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            tools_root = temp_root / "tools"
            manifest_path = tools_root / "broken_tool" / "tool.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "tool_id": "broken_tool",
                    }
                ),
                encoding="utf-8",
            )

            service = ToolRegistryService(tools_root)

            with self.assertRaises(ManifestValidationError) as error_context:
                service.load_manifest(manifest_path)

        self.assertIn("missing required fields", str(error_context.exception))

    def test_cli_host_prints_json_summary_for_discovered_tools(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_root = temp_root / "subject_project"
            manifest_path = repo_root / "tools" / "alpha_tool" / "tool.json"
            manifest_path.parent.mkdir(parents=True)
            project_root.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "tool_id": "alpha_tool",
                        "name": "Alpha Tool",
                        "version": "0.2.0",
                        "entrypoints": {"launch": "python run.py launch"},
                        "capabilities": ["launch_panel", "preview"],
                        "launcher_policy": "dashboard_only",
                    }
                ),
                encoding="utf-8",
            )

            stdout_buffer = StringIO()
            with redirect_stdout(stdout_buffer):
                exit_code = main(
                    [
                        "host",
                        "--project-root",
                        str(project_root),
                        "--repo-root",
                        str(repo_root),
                    ]
                )

        payload = json.loads(stdout_buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["record_type"], "dashboard.host_summary")
        self.assertEqual(payload["tool_count"], 1)
        self.assertEqual(payload["tools"][0]["tool_id"], "alpha_tool")

    def test_cli_show_tool_returns_input_error_for_missing_project_root(self) -> None:
        missing_project_root = Path.cwd() / "dashboard_project_root_should_not_exist"
        if missing_project_root.exists():
            self.fail(f"Expected test path to be absent, but found: {missing_project_root}")

        stderr_buffer = StringIO()
        with redirect_stderr(stderr_buffer):
            exit_code = main(
                [
                    "show-tool",
                    "mermaid_editor",
                    "--project-root",
                    str(missing_project_root),
                ]
            )

        self.assertEqual(exit_code, 3)
        self.assertIn("Project root does not exist", stderr_buffer.getvalue())

    def test_tool_launcher_runs_preview_entrypoint_from_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root, project_root, markdown_file = _prepare_fake_tool_repo(temp_root)
            runtime_context = build_runtime_context(
                project_root=project_root,
                repo_root=repo_root,
            )
            manifest = ToolRegistryService(runtime_context.tools_root).get_manifest("fake_tool")
            launcher_service = ToolLauncherService(
                repo_root=runtime_context.repo_root,
                project_root=runtime_context.project_root,
            )

            invocation = launcher_service.run_preview(
                manifest,
                markdown_file=markdown_file.name,
                request_id="preview-1",
            )

        self.assertEqual(invocation.return_code, 0)
        self.assertEqual(invocation.response["request_id"], "preview-1")
        self.assertEqual(
            invocation.response["payload"]["cwd"],
            str(project_root.resolve()),
        )
        self.assertEqual(
            invocation.response["payload"]["document_path"],
            str(markdown_file.resolve()),
        )

    def test_cli_preview_tool_prints_adapted_preview_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root, project_root, markdown_file = _prepare_fake_tool_repo(temp_root)

            stdout_buffer = StringIO()
            with redirect_stdout(stdout_buffer):
                exit_code = main(
                    [
                        "preview-tool",
                        "fake_tool",
                        "--markdown-file",
                        markdown_file.name,
                        "--project-root",
                        str(project_root),
                        "--repo-root",
                        str(repo_root),
                    ]
                )

        payload = json.loads(stdout_buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["tool_id"], "fake_tool")
        self.assertEqual(payload["record_type"], "preview.fake_document")
        self.assertEqual(payload["summary"], "Previewed sample.md from fake tool")

    def test_cli_run_tool_action_prints_action_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root, project_root, markdown_file = _prepare_fake_tool_repo(temp_root)

            stdout_buffer = StringIO()
            with redirect_stdout(stdout_buffer):
                exit_code = main(
                    [
                        "run-tool-action",
                        "fake_tool",
                        "--action-name",
                        "write_marker",
                        "--markdown-file",
                        markdown_file.name,
                        "--project-root",
                        str(project_root),
                        "--repo-root",
                        str(repo_root),
                    ]
                )

            payload = json.loads(stdout_buffer.getvalue())
            artifact_path = Path(payload["artifacts"][0]["path"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(artifact_path.exists())
            self.assertEqual(artifact_path.read_text(encoding="utf-8"), "marker")


def _prepare_fake_tool_repo(temp_root: Path) -> tuple[Path, Path, Path]:
    repo_root = temp_root / "repo"
    project_root = temp_root / "subject_project"
    project_root.mkdir(parents=True)
    markdown_file = project_root / "sample.md"
    markdown_file.write_text("# sample", encoding="utf-8")

    tool_root = repo_root / "tools" / "fake_tool"
    tool_root.mkdir(parents=True)
    (tool_root / "tool.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "tool_id": "fake_tool",
                "name": "Fake Tool",
                "version": "0.1.0",
                "entrypoints": {
                    "launch": "python run.py launch",
                    "preview": "python run.py preview",
                    "action": "python run.py action",
                },
                "capabilities": [
                    "launch_panel",
                    "preview",
                    "run_action",
                ],
                "launcher_policy": "standalone_allowed",
            }
        ),
        encoding="utf-8",
    )
    (tool_root / "run.py").write_text(
        _fake_tool_script(),
        encoding="utf-8",
    )

    return repo_root, project_root, markdown_file


def _fake_tool_script() -> str:
    return """from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview_parser = subparsers.add_parser("preview")
    preview_parser.add_argument("--project-root", required=True)
    preview_parser.add_argument("--markdown-file", required=True)
    preview_parser.add_argument("--request-id", default="")

    action_parser = subparsers.add_parser("action")
    action_parser.add_argument("--project-root", required=True)
    action_parser.add_argument("--action-name", required=True)
    action_parser.add_argument("--markdown-file")
    action_parser.add_argument("--output-dir")
    action_parser.add_argument("--request-id", default="")

    launch_parser = subparsers.add_parser("launch")
    launch_parser.add_argument("--project-root", required=True)

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if args.command == "preview":
        document_path = Path(args.markdown_file)
        if not document_path.is_absolute():
            document_path = (project_root / document_path).resolve()
        print(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "request_id": args.request_id,
                    "status": "ok",
                    "message": "Previewed sample.md from fake tool",
                    "payload": {
                        "record_type": "preview.fake_document",
                        "cwd": os.getcwd(),
                        "document_path": str(document_path),
                    },
                    "artifacts": [],
                    "errors": [],
                }
            )
        )
        return

    if args.command == "action":
        output_dir = (
            Path(args.output_dir)
            if args.output_dir
            else project_root / "artifacts" / "fake_tool"
        )
        if not output_dir.is_absolute():
            output_dir = (project_root / output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = output_dir / "marker.txt"
        artifact_path.write_text("marker", encoding="utf-8")
        print(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "request_id": args.request_id,
                    "status": "ok",
                    "message": "Action completed",
                    "payload": {
                        "record_type": "action.write_marker",
                        "cwd": os.getcwd(),
                    },
                    "artifacts": [
                        {
                            "artifact_type": "text",
                            "path": str(artifact_path),
                        }
                    ],
                    "errors": [],
                }
            )
        )
        return

    print(
        json.dumps(
            {
                "schema_version": "1.0",
                "request_id": "",
                "status": "ok",
                "message": "Launch placeholder",
                "payload": {
                    "record_type": "launch.fake_tool",
                    "cwd": os.getcwd(),
                },
                "artifacts": [],
                "errors": [],
            }
        )
    )


if __name__ == "__main__":
    main()
"""


if __name__ == "__main__":
    unittest.main()
