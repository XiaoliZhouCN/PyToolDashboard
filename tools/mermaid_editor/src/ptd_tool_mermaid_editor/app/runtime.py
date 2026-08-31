from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RuntimeContext:
    """Runtime paths required by the desktop shell and CLI entrypoints."""

    tool_root: Path
    project_root: Path
    initial_markdown_path: Path | None = None


def resolve_optional_path(path: Path | None, project_root: Path) -> Path | None:
    """Resolve an optional path against project_root when present."""

    if path is None:
        return None
    return resolve_existing_path(path=path, project_root=project_root)


def resolve_existing_path(path: Path, project_root: Path) -> Path:
    """Resolve a required path against project_root and validate existence."""

    resolved = path if path.is_absolute() else project_root / path
    resolved = resolved.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Input Markdown file does not exist: {resolved}")
    return resolved


def tool_root_from_path(path: Path) -> Path:
    """Resolve the Mermaid Editor tool root from a module file path."""

    return path.resolve().parents[3]
