from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolInvocationResult:
    """Describe one tool process invocation from the dashboard host."""

    tool_id: str
    entrypoint_name: str
    command: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str
    response: dict[str, Any] | None
