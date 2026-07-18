"""Validate tracked Markdown fences, structure, transitions, and local links."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
FENCE_OPEN_PATTERN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
STRAY_LANGUAGE_SUFFIX_PATTERN = re.compile(
    r"\]\([^\n)]+\)\.(?:bash|sh|json|python|yaml|yml|md)\s*$"
)
VARIABLE_MARKERS = ("@{", "{{", "${")


def tracked_markdown_paths(root: Path = ROOT) -> list[Path]:
    """Return existing tracked Markdown files in stable lexical order."""

    completed = subprocess.run(
        ["git", "ls-files", "-z", "*.md"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    paths = (
        root / raw.decode("utf-8")
        for raw in completed.stdout.split(b"\0")
        if raw
    )
    return sorted(
        (path for path in paths if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def check_repository(root: Path = ROOT) -> list[str]:
    """Return Markdown hygiene violations for tracked repository files."""

    errors: list[str] = []
    parser = MarkdownIt("commonmark")
    for path in tracked_markdown_paths(root):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        errors.extend(_check_fences(relative, text, _is_documentation(relative)))
        errors.extend(_check_transitions(relative, text))
        tokens = parser.parse(text)
        if _is_documentation(relative):
            errors.extend(_check_heading_hierarchy(relative, tokens))
        errors.extend(_check_local_links(root, path, relative, tokens))
    return sorted(set(errors))


def _check_fences(relative: Path, text: str, require_info: bool) -> list[str]:
    errors: list[str] = []
    active: tuple[str, int, int, str] | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        if active is not None:
            character, length, opening_line, info = active
            if re.fullmatch(rf" {{0,3}}{re.escape(character)}{{{length},}}\s*", line):
                if require_info and not info:
                    errors.append(
                        f"{relative}:{opening_line}: fenced block needs a language"
                    )
                active = None
            continue
        match = FENCE_OPEN_PATTERN.match(line)
        if match:
            marker = match.group("fence")
            active = (
                marker[0],
                len(marker),
                line_number,
                match.group("info").strip(),
            )
    if active is not None:
        errors.append(f"{relative}:{active[2]}: unclosed fenced code block")
    return errors


def _check_transitions(relative: Path, text: str) -> list[str]:
    return [
        f"{relative}:{line_number}: stray language suffix after Markdown link"
        for line_number, line in enumerate(text.splitlines(), start=1)
        if STRAY_LANGUAGE_SUFFIX_PATTERN.search(line)
    ]


def _check_heading_hierarchy(relative: Path, tokens: list[object]) -> list[str]:
    errors: list[str] = []
    previous_level = 0
    for index, token in enumerate(tokens):
        if getattr(token, "type", None) != "heading_open":
            continue
        level = int(token.tag[1:])
        line_number = token.map[0] + 1 if token.map else 1
        heading = tokens[index + 1].content if index + 1 < len(tokens) else ""
        if previous_level and level > previous_level + 1:
            errors.append(
                f"{relative}:{line_number}: heading jumps from h{previous_level} "
                f"to h{level}: {heading}"
            )
        previous_level = level
    return errors


def _check_local_links(
    root: Path,
    path: Path,
    relative: Path,
    tokens: list[object],
) -> list[str]:
    errors: list[str] = []
    for token in tokens:
        if getattr(token, "type", None) != "inline" or not token.children:
            continue
        for child in token.children:
            if child.type not in {"link_open", "image"}:
                continue
            attribute = "href" if child.type == "link_open" else "src"
            value = child.attrGet(attribute)
            if not value or any(marker in unquote(value) for marker in VARIABLE_MARKERS):
                continue
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            line_number = token.map[0] + 1 if token.map else 1
            if not _within(target, root.resolve()):
                errors.append(
                    f"{relative}:{line_number}: local target escapes repository "
                    f"{value!r}"
                )
            elif not target.exists():
                errors.append(
                    f"{relative}:{line_number}: missing local target {value!r}"
                )
    return errors


def _is_documentation(relative: Path) -> bool:
    return (
        len(relative.parts) == 1
        or relative.parts[0] == "docs"
        or relative == Path("examples/README.md")
        or relative == Path("vscode-extension/README.md")
    )


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def main() -> int:
    """Run the repository Markdown check."""

    errors = check_repository()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Markdown hygiene OK: {len(tracked_markdown_paths())} tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
