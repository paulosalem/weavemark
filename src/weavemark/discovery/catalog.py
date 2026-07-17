"""Promplet catalog — scans directories and indexes promplet files.

Each spec is represented as a ``SpecEntry`` with basic metadata extracted
from the file content (title, variables, execution strategy) and a content
hash for cache invalidation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from weavemark.defaults import SPEC_EXTENSIONS
from weavemark.tui.scanner import scan_spec


@dataclass
class SpecEntry:
    """Metadata for a single promplet file."""

    path: Path
    title: str
    content_hash: str
    variables: list[str] = field(default_factory=list)
    execution_strategy: str | None = None
    module_name: str | None = None
    has_tools: bool = False
    raw_text: str = ""

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def short_name(self) -> str:
        """Stem without the spec extension."""
        name = self.path.name
        for ext in SPEC_EXTENSIONS:
            if name.endswith(ext):
                return name[: -len(ext)]
        return self.path.stem


def _content_hash(text: str) -> str:
    """SHA-256 hex digest of the spec content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_title(text: str) -> str:
    """Extract the first markdown heading, or fall back to filename."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def index_spec(path: Path) -> SpecEntry:
    """Build a SpecEntry from a single promplet file."""
    text = path.read_text(encoding="utf-8")
    meta = scan_spec(text)

    title = _extract_title(text)
    if not title:
        name = path.name
        title = path.stem
        for ext in SPEC_EXTENSIONS:
            if name.endswith(ext):
                title = name[: -len(ext)]
                break
    variables = [inp.name for inp in meta.inputs]
    strategy = None
    if meta.execution:
        strategy = meta.execution.get("type")
    has_tools = bool(meta.tool_names)

    return SpecEntry(
        path=path.resolve(),
        title=title,
        content_hash=_content_hash(text),
        variables=variables,
        execution_strategy=strategy,
        module_name=meta.module_name,
        has_tools=has_tools,
        raw_text=text,
    )


def scan_directories(dirs: list[Path]) -> list[SpecEntry]:
    """Recursively scan directories for promplet files and index them.

    Recognizes every extension in :data:`SPEC_EXTENSIONS`. Skips files that
    cannot be read or parsed.
    """
    entries: list[SpecEntry] = []
    seen: set[Path] = set()

    for base_dir in dirs:
        if not base_dir.is_dir():
            continue
        matches: list[Path] = []
        for ext in SPEC_EXTENSIONS:
            matches.extend(base_dir.rglob(f"*{ext}"))
        for path in sorted(matches):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                entries.append(index_spec(path))
            except Exception:
                continue  # skip unparsable specs

    return entries
