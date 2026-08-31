from __future__ import annotations

import json
from pathlib import Path

from ptd_dashboard.registry.models import ToolManifest


class ManifestValidationError(ValueError):
    """Raised when a tool manifest is missing required fields."""


class ToolRegistryService:
    """Load and validate tool manifests from the repository tools directory."""

    def __init__(self, tools_root: Path) -> None:
        self.tools_root = tools_root.resolve()

    def discover_manifests(self) -> list[ToolManifest]:
        """Discover all tool manifests under the tools directory."""

        if not self.tools_root.exists():
            return []

        manifests = [
            self.load_manifest(manifest_path)
            for manifest_path in sorted(self.tools_root.glob("*/tool.json"))
        ]
        return sorted(manifests, key=lambda manifest: manifest.tool_id)

    def get_manifest(self, tool_id: str) -> ToolManifest:
        """Load one manifest by tool identifier."""

        manifest_path = self.tools_root / tool_id / "tool.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Tool manifest does not exist: {manifest_path}")
        return self.load_manifest(manifest_path)

    def load_manifest(self, manifest_path: Path) -> ToolManifest:
        """Read and validate one tool manifest file."""

        resolved_manifest_path = manifest_path.resolve()
        payload = json.loads(resolved_manifest_path.read_text(encoding="utf-8"))
        required_fields = [
            "schema_version",
            "tool_id",
            "name",
            "version",
            "entrypoints",
            "capabilities",
            "launcher_policy",
        ]
        missing_fields = [field_name for field_name in required_fields if field_name not in payload]
        if missing_fields:
            raise ManifestValidationError(
                f"Manifest is missing required fields {missing_fields}: {resolved_manifest_path}"
            )

        entrypoints = payload["entrypoints"]
        capabilities = payload["capabilities"]

        if not isinstance(entrypoints, dict) or not entrypoints:
            raise ManifestValidationError(
                f"Manifest entrypoints must be a non-empty object: {resolved_manifest_path}"
            )
        if not isinstance(capabilities, list):
            raise ManifestValidationError(
                f"Manifest capabilities must be a list: {resolved_manifest_path}"
            )

        tool_root = resolved_manifest_path.parent
        return ToolManifest(
            schema_version=str(payload["schema_version"]),
            tool_id=str(payload["tool_id"]),
            name=str(payload["name"]),
            version=str(payload["version"]),
            entrypoints={str(key): str(value) for key, value in entrypoints.items()},
            capabilities=tuple(str(item) for item in capabilities),
            launcher_policy=str(payload["launcher_policy"]),
            manifest_path=resolved_manifest_path,
            tool_root=tool_root,
            input_schema=_optional_string(payload, "input_schema"),
            output_schema=_optional_string(payload, "output_schema"),
        )


def _optional_string(payload: dict[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    return str(value)
