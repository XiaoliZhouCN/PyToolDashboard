from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DashboardRuntimeContext:
    """Describe the key directories used by the dashboard runtime."""

    repo_root: Path
    dashboard_root: Path
    tools_root: Path
    project_root: Path


def build_runtime_context(
    project_root: Path,
    repo_root: Path | None = None,
) -> DashboardRuntimeContext:
    """Build a runtime context anchored on the subject project directory.

    Args:
        project_root: Subject project directory used as runtime context.
        repo_root: Optional repository root override for tests or development.

    Returns:
        A normalized dashboard runtime context.

    Raises:
        FileNotFoundError: The provided project root does not exist.
        NotADirectoryError: The provided project root is not a directory.
    """

    resolved_project_root = project_root.resolve()
    if not resolved_project_root.exists():
        raise FileNotFoundError(f"Project root does not exist: {resolved_project_root}")
    if not resolved_project_root.is_dir():
        raise NotADirectoryError(f"Project root must be a directory: {resolved_project_root}")

    resolved_repo_root = (
        repo_root.resolve() if repo_root is not None else Path(__file__).resolve().parents[4]
    )
    dashboard_root = resolved_repo_root / "dashboard"
    tools_root = resolved_repo_root / "tools"

    return DashboardRuntimeContext(
        repo_root=resolved_repo_root,
        dashboard_root=dashboard_root,
        tools_root=tools_root,
        project_root=resolved_project_root,
    )
