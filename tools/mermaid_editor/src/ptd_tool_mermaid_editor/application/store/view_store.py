from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ViewStore:
    """Ephemeral UI state that should never be persisted to Markdown or sidecar data."""

    selection_payload: dict[str, object] | None = None
    zoom_percent: float = 100.0
    pan_x: float = 0.0
    pan_y: float = 0.0
    toolbar_height: int = 0
