from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ToolManifest:
    """Represent a tool manifest discovered by the dashboard registry."""

    schema_version: str
    tool_id: str
    name: str
    version: str
    entrypoints: dict[str, str]
    capabilities: tuple[str, ...]
    launcher_policy: str
    manifest_path: Path
    tool_root: Path
    input_schema: str | None = None
    output_schema: str | None = None

    def to_summary_dict(self) -> dict[str, object]:
        """Convert the manifest into a JSON-friendly summary payload."""

        return {
            "schema_version": self.schema_version,
            "tool_id": self.tool_id,
            "name": self.name,
            "version": self.version,
            "entrypoints": dict(self.entrypoints),
            "capabilities": list(self.capabilities),
            "launcher_policy": self.launcher_policy,
            "manifest_path": str(self.manifest_path),
            "tool_root": str(self.tool_root),
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }
