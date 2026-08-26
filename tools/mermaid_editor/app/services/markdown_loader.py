from __future__ import annotations

import re
from pathlib import Path

from app.models.graph import MermaidDocument, MermaidDiagram
from app.services.mermaid_parser import MermaidParser


MERMAID_BLOCK_RE = re.compile(
    r"```mermaid\s*\r?\n(?P<content>.*?)\r?\n```",
    re.DOTALL | re.IGNORECASE,
)


class MarkdownLoader:
    def __init__(self, parser: MermaidParser | None = None) -> None:
        self._parser = parser or MermaidParser()

    def load(self, path: Path) -> MermaidDocument:
        markdown = path.read_text(encoding="utf-8")
        text_parts: list[str] = []
        diagrams: list[MermaidDiagram] = []
        cursor = 0

        for index, match in enumerate(MERMAID_BLOCK_RE.finditer(markdown)):
            text_parts.append(markdown[cursor : match.start()])
            source = match.group("content").strip("\n")
            diagrams.append(self._parser.parse(source=source, index=index))
            cursor = match.end()

        text_parts.append(markdown[cursor:])
        return MermaidDocument(
            source_path=str(path),
            text_parts=text_parts,
            diagrams=diagrams,
        )
