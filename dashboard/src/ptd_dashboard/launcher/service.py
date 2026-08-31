from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from ptd_dashboard.launcher.models import ToolInvocationResult
from ptd_dashboard.registry.models import ToolManifest


class ToolInvocationError(RuntimeError):
    """Raised when dashboard cannot run a tool entrypoint successfully."""

    def __init__(self, message: str, result: ToolInvocationResult | None = None) -> None:
        super().__init__(message)
        self.result = result


class ToolLauncherService:
    """Run tool entrypoints while preserving the project-root runtime contract."""

    def __init__(self, *, repo_root: Path, project_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.project_root = project_root.resolve()

    def run_preview(
        self,
        manifest: ToolManifest,
        *,
        markdown_file: str | Path,
        request_id: str = "",
    ) -> ToolInvocationResult:
        """Run a tool preview entrypoint and parse its JSON response."""

        extra_args = ["--markdown-file", str(markdown_file)]
        if request_id:
            extra_args.extend(["--request-id", request_id])
        return self.run_entrypoint(manifest, "preview", extra_args=extra_args)

    def run_action(
        self,
        manifest: ToolManifest,
        *,
        action_name: str,
        markdown_file: str | Path | None = None,
        output_dir: str | Path | None = None,
        diagram_id: str | None = None,
        request_id: str = "",
    ) -> ToolInvocationResult:
        """Run a tool action entrypoint and parse its JSON response."""

        extra_args = ["--action-name", action_name]
        if markdown_file is not None:
            extra_args.extend(["--markdown-file", str(markdown_file)])
        if output_dir is not None:
            extra_args.extend(["--output-dir", str(output_dir)])
        if diagram_id:
            extra_args.extend(["--diagram-id", diagram_id])
        if request_id:
            extra_args.extend(["--request-id", request_id])
        return self.run_entrypoint(manifest, "action", extra_args=extra_args)

    def run_entrypoint(
        self,
        manifest: ToolManifest,
        entrypoint_name: str,
        *,
        extra_args: list[str] | None = None,
    ) -> ToolInvocationResult:
        """Run one declared tool entrypoint and parse its JSON output when present."""

        if entrypoint_name not in manifest.entrypoints:
            raise ToolInvocationError(
                f"Tool '{manifest.tool_id}' does not declare '{entrypoint_name}' entrypoint."
            )

        command = self._build_command(
            manifest=manifest,
            entrypoint_name=entrypoint_name,
            extra_args=extra_args or [],
        )
        completed = subprocess.run(
            command,
            cwd=self.project_root,
            env=self._build_env(manifest),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        response = _try_parse_json(completed.stdout)
        result = ToolInvocationResult(
            tool_id=manifest.tool_id,
            entrypoint_name=entrypoint_name,
            command=tuple(command),
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            response=response,
        )
        if completed.returncode != 0:
            raise ToolInvocationError(
                _build_process_error_message(manifest.tool_id, entrypoint_name, result),
                result=result,
            )
        return result

    def _build_command(
        self,
        *,
        manifest: ToolManifest,
        entrypoint_name: str,
        extra_args: list[str],
    ) -> list[str]:
        raw_command = manifest.entrypoints[entrypoint_name]
        command = _split_command(raw_command)
        if not command:
            raise ToolInvocationError(
                f"Tool '{manifest.tool_id}' declares an empty '{entrypoint_name}' entrypoint."
            )

        executable = self._normalize_executable(command[0])
        tail = self._normalize_command_tail(
            tool_root=manifest.tool_root,
            command=command[1:],
        )
        return [
            executable,
            *tail,
            *extra_args,
            "--project-root",
            str(self.project_root),
        ]

    def _normalize_executable(self, executable: str) -> str:
        normalized = executable.strip().strip("\"'")
        if normalized.lower() == "python":
            return sys.executable
        return normalized

    def _normalize_command_tail(
        self,
        *,
        tool_root: Path,
        command: list[str],
    ) -> list[str]:
        normalized = [item.strip().strip("\"'") for item in command]
        if not normalized:
            return []

        if normalized[0] == "-m":
            return normalized

        first_item = Path(normalized[0])
        if not first_item.is_absolute() and normalized[0].endswith(".py"):
            candidate = (tool_root / first_item).resolve()
            if candidate.exists():
                normalized[0] = str(candidate)
        return normalized

    def _build_env(self, manifest: ToolManifest) -> dict[str, str]:
        environment = dict(os.environ)
        python_path_entries = [
            str(manifest.tool_root / "src"),
            str(self.repo_root / "packages"),
            str(self.repo_root / "dashboard" / "src"),
        ]
        existing_python_path = environment.get("PYTHONPATH", "")
        if existing_python_path:
            python_path_entries.append(existing_python_path)
        environment["PYTHONPATH"] = os.pathsep.join(python_path_entries)
        return environment


def _split_command(command: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote_char = ""

    for char in command.strip():
        if quote_char:
            if char == quote_char:
                quote_char = ""
            else:
                current.append(char)
            continue

        if char in {'"', "'"}:
            quote_char = char
            continue

        if char.isspace():
            if current:
                parts.append("".join(current))
                current = []
            continue

        current.append(char)

    if current:
        parts.append("".join(current))
    return parts


def _try_parse_json(payload: str) -> dict[str, Any] | None:
    stripped = payload.strip()
    if not stripped:
        return None
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def _build_process_error_message(
    tool_id: str,
    entrypoint_name: str,
    result: ToolInvocationResult,
) -> str:
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    details = stderr or stdout or "Tool process returned a non-zero exit code."
    return (
        f"Tool '{tool_id}' entrypoint '{entrypoint_name}' failed with exit code "
        f"{result.return_code}: {details}"
    )
