from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ptd_dashboard.launcher import ToolInvocationError, ToolLauncherService
from ptd_dashboard.preview import adapt_preview_response
from ptd_dashboard.registry import ManifestValidationError, ToolRegistryService
from ptd_dashboard.services.runtime import DashboardRuntimeContext, build_runtime_context

EXIT_OK = 0
EXIT_INVALID_ARGUMENTS = 2
EXIT_INPUT_ERROR = 3
EXIT_EXECUTION_ERROR = 10
EXIT_INTERNAL_ERROR = 20


def main(argv: list[str] | None = None) -> int:
    """Run the dashboard host CLI."""

    args = list(sys.argv[1:] if argv is None else argv)
    normalized_args = _normalize_args(args)
    parser = _build_parser()
    namespace = parser.parse_args(normalized_args)

    try:
        runtime_context = build_runtime_context(
            project_root=namespace.project_root,
            repo_root=namespace.repo_root,
        )
        registry_service = ToolRegistryService(runtime_context.tools_root)

        launcher_service = ToolLauncherService(
            repo_root=runtime_context.repo_root,
            project_root=runtime_context.project_root,
        )

        if namespace.command == "host":
            return _host_command(runtime_context, registry_service)
        if namespace.command == "list-tools":
            return _list_tools_command(registry_service, as_json=namespace.json)
        if namespace.command == "show-tool":
            return _show_tool_command(
                registry_service,
                tool_id=namespace.tool_id,
                as_json=namespace.json,
            )
        if namespace.command == "preview-tool":
            return _preview_tool_command(
                registry_service=registry_service,
                launcher_service=launcher_service,
                tool_id=namespace.tool_id,
                markdown_file=namespace.markdown_file,
                request_id=namespace.request_id,
                raw=namespace.raw,
            )
        if namespace.command == "run-tool-action":
            return _run_tool_action_command(
                registry_service=registry_service,
                launcher_service=launcher_service,
                tool_id=namespace.tool_id,
                action_name=namespace.action_name,
                markdown_file=namespace.markdown_file,
                output_dir=namespace.output_dir,
                diagram_id=namespace.diagram_id,
                request_id=namespace.request_id,
            )
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_INPUT_ERROR
    except ManifestValidationError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_EXECUTION_ERROR
    except ToolInvocationError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_EXECUTION_ERROR
    except Exception as exc:  # pragma: no cover - CLI safety net
        print(str(exc), file=sys.stderr)
        return EXIT_INTERNAL_ERROR

    parser.print_help()
    return EXIT_INVALID_ARGUMENTS


def _normalize_args(args: list[str]) -> list[str]:
    known_commands = {
        "host",
        "list-tools",
        "show-tool",
        "preview-tool",
        "run-tool-action",
    }
    if not args or args[0].startswith("-"):
        return ["host", *args]
    if args[0] in known_commands:
        return args
    return args


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ptd_dashboard",
        description="Local-first dashboard host for PyToolDashboard tools.",
    )
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Subject project root used as runtime working context.",
    )
    common_parser.add_argument(
        "--repo-root",
        type=Path,
        help="Optional PyToolDashboard repository root override.",
    )

    subparsers = parser.add_subparsers(dest="command")

    host_parser = subparsers.add_parser(
        "host",
        parents=[common_parser],
        help="Run the current dashboard host placeholder.",
    )
    host_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the host summary as JSON.",
    )

    list_tools_parser = subparsers.add_parser(
        "list-tools",
        parents=[common_parser],
        help="List discovered tool manifests.",
    )
    list_tools_parser.add_argument(
        "--json",
        action="store_true",
        help="Print discovered manifests as JSON.",
    )

    show_tool_parser = subparsers.add_parser(
        "show-tool",
        parents=[common_parser],
        help="Show one discovered tool manifest.",
    )
    show_tool_parser.add_argument("tool_id", help="Tool identifier from tool.json.")
    show_tool_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the selected manifest as JSON.",
    )

    preview_tool_parser = subparsers.add_parser(
        "preview-tool",
        parents=[common_parser],
        help="Run one tool preview entrypoint.",
    )
    preview_tool_parser.add_argument("tool_id", help="Tool identifier from tool.json.")
    preview_tool_parser.add_argument(
        "--markdown-file",
        required=True,
        help="Markdown file path resolved from project_root.",
    )
    preview_tool_parser.add_argument(
        "--request-id",
        default="",
        help="Optional request identifier used for dashboard orchestration.",
    )
    preview_tool_parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw tool preview response instead of the adapted dashboard model.",
    )

    run_tool_action_parser = subparsers.add_parser(
        "run-tool-action",
        parents=[common_parser],
        help="Run one tool action entrypoint.",
    )
    run_tool_action_parser.add_argument("tool_id", help="Tool identifier from tool.json.")
    run_tool_action_parser.add_argument(
        "--action-name",
        required=True,
        help="Tool action identifier, for example export_svg.",
    )
    run_tool_action_parser.add_argument(
        "--markdown-file",
        help="Markdown file path resolved from project_root.",
    )
    run_tool_action_parser.add_argument(
        "--output-dir",
        help="Optional output directory for generated artifacts.",
    )
    run_tool_action_parser.add_argument(
        "--diagram-id",
        help="Optional diagram identifier that narrows the action scope.",
    )
    run_tool_action_parser.add_argument(
        "--request-id",
        default="",
        help="Optional request identifier used for dashboard orchestration.",
    )

    return parser


def _host_command(
    runtime_context: DashboardRuntimeContext,
    registry_service: ToolRegistryService,
) -> int:
    manifests = registry_service.discover_manifests()
    summary = {
        "schema_version": "1.0",
        "record_type": "dashboard.host_summary",
        "project_root": str(runtime_context.project_root),
        "repo_root": str(runtime_context.repo_root),
        "tool_count": len(manifests),
        "tools": [manifest.to_summary_dict() for manifest in manifests],
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return EXIT_OK


def _list_tools_command(
    registry_service: ToolRegistryService,
    *,
    as_json: bool,
) -> int:
    manifests = registry_service.discover_manifests()
    if as_json:
        print(
            json.dumps(
                [manifest.to_summary_dict() for manifest in manifests],
                indent=2,
                ensure_ascii=False,
            )
        )
        return EXIT_OK

    if not manifests:
        print("No tool manifests discovered.")
        return EXIT_OK

    for manifest in manifests:
        print(f"{manifest.tool_id}\t{manifest.version}\t{','.join(manifest.capabilities)}")
    return EXIT_OK


def _show_tool_command(
    registry_service: ToolRegistryService,
    *,
    tool_id: str,
    as_json: bool,
) -> int:
    manifest = registry_service.get_manifest(tool_id)
    if as_json:
        print(json.dumps(manifest.to_summary_dict(), indent=2, ensure_ascii=False))
        return EXIT_OK

    print(f"tool_id: {manifest.tool_id}")
    print(f"name: {manifest.name}")
    print(f"version: {manifest.version}")
    print(f"launcher_policy: {manifest.launcher_policy}")
    print(f"capabilities: {', '.join(manifest.capabilities)}")
    print(f"manifest_path: {manifest.manifest_path}")
    return EXIT_OK


def _preview_tool_command(
    *,
    registry_service: ToolRegistryService,
    launcher_service: ToolLauncherService,
    tool_id: str,
    markdown_file: str,
    request_id: str,
    raw: bool,
) -> int:
    manifest = registry_service.get_manifest(tool_id)
    invocation = launcher_service.run_preview(
        manifest,
        markdown_file=markdown_file,
        request_id=request_id,
    )
    response = invocation.response or {}
    if raw:
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return EXIT_OK

    adapted_preview = adapt_preview_response(manifest, response)
    print(json.dumps(adapted_preview.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def _run_tool_action_command(
    *,
    registry_service: ToolRegistryService,
    launcher_service: ToolLauncherService,
    tool_id: str,
    action_name: str,
    markdown_file: str | None,
    output_dir: str | None,
    diagram_id: str | None,
    request_id: str,
) -> int:
    manifest = registry_service.get_manifest(tool_id)
    invocation = launcher_service.run_action(
        manifest,
        action_name=action_name,
        markdown_file=markdown_file,
        output_dir=output_dir,
        diagram_id=diagram_id,
        request_id=request_id,
    )
    print(json.dumps(invocation.response or {}, indent=2, ensure_ascii=False))
    return EXIT_OK
