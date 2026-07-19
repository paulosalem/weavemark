"""Validate a WeaveMark release tag and extract its changelog notes."""

from __future__ import annotations

import argparse
import json
import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_TAG_RE = re.compile(r"^v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)$")
_SOURCE_FALLBACK_RE = re.compile(
    r'^\s*__version__\s*=\s*"(?P<version>[0-9]+\.[0-9]+\.[0-9]+)"\s*$',
    re.MULTILINE,
)
_CI_ASSERTION_RE = re.compile(
    r"weavemark\.__version__\s*==\s*'(?P<version>[0-9]+\.[0-9]+\.[0-9]+)'"
)


class ReleaseValidationError(ValueError):
    """Raised when a tag does not match the repository release contract."""


@dataclass(frozen=True)
class ReleaseInfo:
    """Validated release version and rendered changelog notes."""

    tag: str
    version: str
    notes: str


def validate_release(root: Path, tag: str) -> ReleaseInfo:
    """Validate release authorities under *root* for *tag*."""

    match = _TAG_RE.fullmatch(tag)
    if match is None:
        raise ReleaseValidationError(
            f"Release tag must match vMAJOR.MINOR.PATCH; received {tag!r}."
        )
    version = match.group("version")
    authorities = _release_versions(root)
    mismatches = {
        source: found
        for source, found in authorities.items()
        if found != version
    }
    if mismatches:
        detail = ", ".join(
            f"{source}={found}" for source, found in sorted(mismatches.items())
        )
        raise ReleaseValidationError(
            f"Tag {tag} does not match every release version: {detail}."
        )

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased = _changelog_section(changelog, "Unreleased")
    if unreleased is None:
        raise ReleaseValidationError("CHANGELOG.md is missing '## Unreleased'.")
    if unreleased.strip():
        raise ReleaseValidationError(
            "CHANGELOG.md 'Unreleased' must be empty before publishing; move its "
            f"entries into the {version} section."
        )
    notes = _changelog_section(changelog, version)
    if notes is None:
        raise ReleaseValidationError(
            f"CHANGELOG.md is missing release section '## {version}'."
        )
    if not notes.strip():
        raise ReleaseValidationError(
            f"CHANGELOG.md release section '## {version}' is empty."
        )
    return ReleaseInfo(tag=tag, version=version, notes=notes.strip() + "\n")


def _release_versions(root: Path) -> dict[str, str]:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    package_version = str(pyproject["project"]["version"])

    extension = json.loads(
        (root / "vscode-extension" / "package.json").read_text(encoding="utf-8")
    )
    extension_version = str(extension["version"])

    source_text = (root / "src" / "weavemark" / "version.py").read_text(
        encoding="utf-8"
    )
    source_match = _SOURCE_FALLBACK_RE.search(source_text)
    if source_match is None:
        raise ReleaseValidationError(
            "Could not find the source-checkout __version__ fallback."
        )

    ci_text = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    ci_match = _CI_ASSERTION_RE.search(ci_text)
    if ci_match is None:
        raise ReleaseValidationError(
            "Could not find the CI wheel-version assertion."
        )
    return {
        "pyproject.toml": package_version,
        "src/weavemark/version.py": source_match.group("version"),
        "vscode-extension/package.json": extension_version,
        ".github/workflows/ci.yml": ci_match.group("version"),
    }


def _changelog_section(changelog: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}(?:\s+-\s+[^\n]+)?\s*$"
        rf"(?P<body>.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(changelog)
    return match.group("body") if match is not None else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate release-version authorities for a vX.Y.Z tag."
    )
    parser.add_argument(
        "--tag",
        default=os.environ.get("GITHUB_REF_NAME"),
        help="Release tag (defaults to GITHUB_REF_NAME).",
    )
    parser.add_argument(
        "--notes",
        type=Path,
        help="Optional file receiving the matching changelog section.",
    )
    args = parser.parse_args()
    if not args.tag:
        parser.error("--tag is required outside a tagged GitHub Actions run")

    try:
        release = validate_release(ROOT, args.tag)
    except ReleaseValidationError as exc:
        parser.error(str(exc))
    if args.notes is not None:
        args.notes.write_text(release.notes, encoding="utf-8")
    print(f"Release contract OK: {release.tag}")


if __name__ == "__main__":
    main()
