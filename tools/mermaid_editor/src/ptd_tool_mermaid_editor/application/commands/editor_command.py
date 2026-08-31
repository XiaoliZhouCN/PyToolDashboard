from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EditorCommand:
    """A typed application command exchanged across editor layers."""

    command_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    request_id: str = ""
