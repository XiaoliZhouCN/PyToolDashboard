from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class UndoHistory:
    """A lightweight placeholder for future structured undo and redo state."""

    undo_stack: list[Any] = field(default_factory=list)
    redo_stack: list[Any] = field(default_factory=list)
