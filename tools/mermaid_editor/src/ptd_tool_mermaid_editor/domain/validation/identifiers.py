from __future__ import annotations

import re


IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_]+$")


def is_valid_identifier(identifier: str) -> bool:
    """Return whether a Mermaid node or subgraph identifier is supported."""

    return bool(IDENTIFIER_RE.match(identifier))
