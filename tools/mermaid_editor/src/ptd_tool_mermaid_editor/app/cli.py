from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ptd_tool_mermaid_editor.app.bootstrap import create_main_window
from ptd_tool_mermaid_editor.app.runtime import (
    RuntimeContext,
    resolve_existing_path,
    resolve_optional_path,
    tool_root_from_path,
)


EXIT_OK = 0
EXIT_INVALID_ARGUMENTS = 2
EXIT_INPUT_ERROR = 3
EXIT_INTERNAL_ERROR = 20


def main(argv: list[str] | None = None) -> int:
    """Run the Mermaid Editor CLI."""

    args = list(sys.argv[1:] if argv is None else argv)
    normalized_args = _normalize_args(args)
    parser = _build_parser()
    namespace = parser.parse_args(normalized_args)
    command = namespace.command or "launch"

    try:
        if command == "launch":
            return _launch_command(namespace)
        if command == "preview":
            return _preview_command(namespace)
        if command == "action":
            return _action_command(namespace)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_INPUT_ERROR
    except Exception as exc:  # pragma: no cover - CLI safety net
        print(str(exc), file=sys.stderr)
        return EXIT_INTERNAL_ERROR

    parser.print_help()
    return EXIT_INVALID_ARGUMENTS


def _normalize_args(args: list[str]) -> list[str]:
    known_commands = {"launch", "preview", "action"}
    if not args or args[0] not in known_commands:
        return ["launch", *args]
    return args


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ptd_tool_mermaid_editor",
        description="Local-first Mermaid editor for Markdown knowledge bases.",
    )
    subparsers = parser.add_subparsers(dest="command")

    launch_parser = subparsers.add_parser("launch", help="Launch the desktop editor.")
    launch_parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Workspace project root used for file dialogs and runtime context.",
    )
    launch_parser.add_argument(
        "--markdown-file",
        type=Path,
        help="Optional Markdown file to open on startup.",
    )

    preview_parser = subparsers.add_parser(
        "preview",
        help="Print a JSON preview summary for a Markdown document.",
    )
    preview_parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Workspace project root used to resolve relative paths.",
    )
    preview_parser.add_argument(
        "--markdown-file",
        type=Path,
        required=True,
        help="Markdown file to inspect.",
    )
    preview_parser.add_argument(
        "--request-id",
        default="",
        help="Optional request identifier for dashboard orchestration.",
    )

    action_parser = subparsers.add_parser(
        "action",
        help="Run a standard tool action and print a JSON response.",
    )
    action_parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Workspace project root used to resolve relative paths.",
    )
    action_parser.add_argument(
        "--action-name",
        required=True,
        help="Action identifier, for example export_svg.",
    )
    action_parser.add_argument(
        "--markdown-file",
        type=Path,
        help="Markdown file consumed by the action.",
    )
    action_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for generated artifacts.",
    )
    action_parser.add_argument(
        "--diagram-id",
        help="Optional diagram identifier to limit the action target.",
    )
    action_parser.add_argument(
        "--request-id",
        default="",
        help="Optional request identifier for dashboard orchestration.",
    )

    return parser


def _launch_command(namespace: argparse.Namespace) -> int:
    project_root = namespace.project_root.resolve()
    markdown_file = resolve_optional_path(namespace.markdown_file, project_root)

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("Mermaid Editor")

    context = RuntimeContext(
        tool_root=tool_root_from_path(Path(__file__)),
        project_root=project_root,
        initial_markdown_path=markdown_file,
    )
    window = create_main_window(context)
    window.show()
    return app.exec()


def _preview_command(namespace: argparse.Namespace) -> int:
    project_root = namespace.project_root.resolve()
    markdown_file = resolve_existing_path(namespace.markdown_file, project_root)

    from ptd_tool_mermaid_editor.preview.service import build_preview_response

    response = build_preview_response(
        markdown_file=markdown_file,
        request_id=namespace.request_id,
    )
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return EXIT_OK


def _action_command(namespace: argparse.Namespace) -> int:
    project_root = namespace.project_root.resolve()

    from ptd_tool_mermaid_editor.actions.service import run_action

    response = run_action(
        action_name=namespace.action_name,
        project_root=project_root,
        request_id=namespace.request_id,
        markdown_file=str(namespace.markdown_file) if namespace.markdown_file else None,
        output_dir=str(namespace.output_dir) if namespace.output_dir else None,
        diagram_id=namespace.diagram_id,
    )
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return EXIT_OK

