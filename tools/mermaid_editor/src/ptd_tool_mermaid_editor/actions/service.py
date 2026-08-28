from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ptd_tool_mermaid_editor.actions.png_export import PngExporter
from ptd_tool_mermaid_editor.actions.svg_export import SvgExporter


def run_action(
    action_name: str,
    project_root: Path,
    request_id: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a supported Mermaid Editor action and return a standard response."""

    markdown_file = _resolve_required_path(kwargs.get("markdown_file"), project_root)
    output_dir = _resolve_output_dir(kwargs.get("output_dir"), project_root)
    diagram_id = kwargs.get("diagram_id")
    created_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    if action_name == "export_svg":
        results = SvgExporter().export_document(
            markdown_file=markdown_file,
            output_dir=output_dir,
            diagram_id=diagram_id,
        )
        artifact_type = "svg"
    elif action_name == "export_png":
        results = PngExporter().export_document(
            markdown_file=markdown_file,
            output_dir=output_dir,
            diagram_id=diagram_id,
        )
        artifact_type = "png"
    else:
        raise ValueError(f"Unsupported action: {action_name}")

    return _build_action_response(
        action_name=action_name,
        artifact_type=artifact_type,
        results=results,
        markdown_file=markdown_file,
        output_dir=output_dir,
        diagram_id=diagram_id,
        request_id=request_id,
        created_at=created_at,
    )


def _resolve_required_path(path_value: Any, project_root: Path) -> Path:
    if not path_value:
        raise ValueError("markdown_file is required for export_svg")

    path = Path(path_value)
    resolved = path if path.is_absolute() else project_root / path
    resolved = resolved.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Input Markdown file does not exist: {resolved}")
    return resolved


def _resolve_output_dir(path_value: Any, project_root: Path) -> Path:
    if not path_value:
        return (project_root / "artifacts" / "mermaid_editor").resolve()

    path = Path(path_value)
    return (path if path.is_absolute() else project_root / path).resolve()


def _build_action_response(
    action_name: str,
    artifact_type: str,
    results: list[Any],
    markdown_file: Path,
    output_dir: Path,
    diagram_id: str | None,
    request_id: str,
    created_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "request_id": request_id,
        "status": "ok",
        "message": f"Exported {len(results)} {artifact_type.upper()} file(s)",
        "payload": {
            "record_type": f"action.{action_name}",
            "created_at": created_at,
            "markdown_file": str(markdown_file),
            "output_dir": str(output_dir),
            "diagram_id": diagram_id or "",
        },
        "artifacts": [
            {
                "artifact_type": artifact_type,
                "diagram_id": result.diagram_id,
                "path": str(result.output_path),
            }
            for result in results
        ],
        "errors": [],
    }
