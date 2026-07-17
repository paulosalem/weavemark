"""Resolution helpers for WeaveMark fragment references."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from weavemark.defaults import SPEC_EXTENSIONS
from weavemark.settings import WeaveMarkSettings

_ALIAS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class FragmentResolution:
    """Resolved fragment path or a user-facing diagnostic."""

    path: Path | None
    error: str | None = None
    alias: str | None = None


def is_explicit_file_reference(reference: str) -> bool:
    """Return whether *reference* is an explicit filesystem path."""

    text = reference.strip()
    if not text:
        return False
    if text.startswith(("./", "../", ".\\", "..\\", "~/", "~\\")):
        return True
    if text in {".", "..", "~"}:
        return True
    if Path(text).expanduser().is_absolute():
        return True
    return bool(_WINDOWS_ABSOLUTE_RE.match(text))


def resolve_fragment_reference(
    reference: str,
    settings: WeaveMarkSettings,
) -> FragmentResolution:
    """Resolve an alias-backed fragment reference.

    Supported forms:

    - ``alias:path/to/fragment`` resolves through that fragment alias.
    - ``path/to/fragment`` resolves through the only configured alias.

    Explicit filesystem references such as ``./base.weavemark.md`` are not
    fragment references and are reported as such by the caller.
    """

    text = reference.strip()
    if not text:
        return FragmentResolution(None, "Fragment reference must not be empty.")
    if is_explicit_file_reference(text):
        return FragmentResolution(None)

    alias_reference = _split_alias_reference(text)
    if alias_reference is not None:
        alias, fragment_path = alias_reference
        root = settings.fragment_aliases.get(alias)
        if root is None:
            return FragmentResolution(
                None,
                f"Unknown fragment alias '{alias}' in reference '{text}'.",
            )
        return _resolve_with_alias(alias, root, fragment_path, text)

    aliases = settings.fragment_aliases
    if not aliases:
        return FragmentResolution(
            None,
            (
                f"Bare fragment reference '{text}' requires a configured "
                "fragment alias or an explicit path starting with ./, ../, /, or ~/."
            ),
        )
    if len(aliases) > 1:
        available = ", ".join(sorted(aliases))
        return FragmentResolution(
            None,
            (
                f"Bare fragment reference '{text}' is ambiguous; use alias:path. "
                f"Available fragment aliases: {available}."
            ),
        )

    alias, root = next(iter(aliases.items()))
    return _resolve_with_alias(alias, root, text, text)


def has_fragment_alias_prefix(reference: str) -> bool:
    """Return whether *reference* starts with a syntactic ``alias:`` prefix."""

    return _split_alias_reference(reference.strip()) is not None


def _split_alias_reference(reference: str) -> tuple[str, str] | None:
    if _WINDOWS_ABSOLUTE_RE.match(reference):
        return None
    colon_index = reference.find(":")
    if colon_index <= 0:
        return None
    slash_index = min(
        [index for index in (reference.find("/"), reference.find("\\")) if index >= 0],
        default=-1,
    )
    if slash_index >= 0 and slash_index < colon_index:
        return None

    alias = reference[:colon_index].strip()
    fragment_path = reference[colon_index + 1 :].strip()
    if not _ALIAS_RE.fullmatch(alias):
        return None
    return alias, fragment_path


def _resolve_with_alias(
    alias: str,
    root: Path,
    fragment_path: str,
    original_reference: str,
) -> FragmentResolution:
    if not fragment_path:
        return FragmentResolution(
            None,
            f"Fragment reference '{original_reference}' must include a path after '{alias}:'.",
        )

    relative_path = Path(fragment_path)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return FragmentResolution(
            None,
            (
                f"Fragment reference '{original_reference}' must stay inside "
                f"the '{alias}' fragment root."
            ),
        )

    resolved_root = root.expanduser().resolve()
    tried = _fragment_candidates(resolved_root, relative_path)
    for candidate in tried:
        try:
            candidate.relative_to(resolved_root)
        except ValueError:
            return FragmentResolution(
                None,
                (
                    f"Fragment reference '{original_reference}' must stay inside "
                    f"the '{alias}' fragment root."
                ),
            )
        if candidate.is_file():
            return FragmentResolution(candidate, alias=alias)

    tried_text = ", ".join(str(path) for path in tried)
    return FragmentResolution(
        None,
        (
            f"Fragment '{original_reference}' was not found in alias '{alias}' "
            f"root {resolved_root}. Tried: {tried_text}."
        ),
        alias=alias,
    )


def _fragment_candidates(root: Path, relative_path: Path) -> tuple[Path, ...]:
    primary = (root / relative_path).resolve()
    candidates = [primary]
    primary_text = str(primary)
    for ext in SPEC_EXTENSIONS:
        if not primary_text.endswith(ext):
            candidates.append(Path(f"{primary_text}{ext}"))
    if primary.suffix == "":
        candidates.append(Path(f"{primary_text}.md"))

    seen: set[Path] = set()
    deduped: list[Path] = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        deduped.append(candidate)
    return tuple(deduped)
