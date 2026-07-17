"""Validate candidate commit artifacts, sizes, and Git LFS boundaries."""

from __future__ import annotations

import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAX_NON_LFS_FILE_BYTES = 10 * 1024 * 1024
MAX_NON_LFS_TOTAL_BYTES = 50 * 1024 * 1024
MAX_LFS_FILE_BYTES = 100 * 1024 * 1024
MAX_LFS_TOTAL_BYTES = 512 * 1024 * 1024

FORBIDDEN_COMPONENTS = {
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "playwright-report",
    "test-results",
}
FORBIDDEN_NAMES = {".DS_Store", "Thumbs.db"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".vsix", ".whl"}
SHOWCASE_BINARY_SUFFIXES = {".pdf", ".png"}
SHOWCASE_PREFIX = "examples/saved-artifact-workflows/"
FORBIDDEN_PUBLIC_CONTENT = {
    b"prompting" + b" adventures": "confidential initiative name",
    b"/users/" + b"paulo" + b"salem": "personal POSIX home path",
    b"c:\\users\\" + b"paulo" + b"salem": "personal Windows home path",
    b"googledrive-" + b"paulo" + b"salem": "personal cloud-storage path",
}


@dataclass(frozen=True, slots=True)
class Inventory:
    """Candidate-commit size and artifact inventory."""

    candidate_files: int
    ordinary_files: int
    lfs_files: int
    ordinary_bytes: int
    lfs_bytes: int
    by_top_level: dict[str, int]


def candidate_paths(root: Path = ROOT) -> list[Path]:
    """List tracked and untracked non-ignored files considered for a commit."""

    completed = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=root,
        capture_output=True,
        check=True,
    )
    return [
        root / raw.decode("utf-8")
        for raw in completed.stdout.split(b"\0")
        if raw
    ]


def lfs_paths(paths: list[Path], root: Path = ROOT) -> set[Path]:
    """Return candidate paths whose effective Git filter is LFS."""

    if not paths:
        return set()
    relative = [str(path.relative_to(root)) for path in paths]
    completed = subprocess.run(
        ["git", "check-attr", "--stdin", "-z", "filter"],
        cwd=root,
        input=b"\0".join(item.encode("utf-8") for item in relative) + b"\0",
        capture_output=True,
        check=True,
    )
    fields = completed.stdout.split(b"\0")
    result: set[Path] = set()
    for index in range(0, len(fields) - 2, 3):
        raw_path, attribute, value = fields[index : index + 3]
        if attribute == b"filter" and value == b"lfs":
            result.add(root / raw_path.decode("utf-8"))
    return result


def inspect_repository(root: Path = ROOT) -> tuple[Inventory, list[str]]:
    """Build the inventory and return human-actionable policy violations."""

    paths = candidate_paths(root)
    lfs = lfs_paths(paths, root)
    errors: list[str] = []
    ordinary_bytes = 0
    lfs_bytes = 0
    ordinary_files = 0
    by_top_level: dict[str, int] = defaultdict(int)

    for path in paths:
        relative = path.relative_to(root)
        if not path.is_file():
            continue
        size = path.stat().st_size
        top_level = relative.parts[0] if relative.parts else "."
        by_top_level[top_level] += size

        if relative.name in FORBIDDEN_NAMES:
            errors.append(f"forbidden generated file: {relative}")
        forbidden_component = next(
            (part for part in relative.parts if part in FORBIDDEN_COMPONENTS),
            None,
        )
        if forbidden_component is not None:
            errors.append(
                f"forbidden generated directory {forbidden_component!r}: {relative}"
            )
        if relative.suffix.casefold() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden package/cache artifact: {relative}")
        if relative.name.endswith((".tar.gz", ".zip")):
            errors.append(f"forbidden archive artifact: {relative}")

        is_lfs = path in lfs
        is_showcase_binary = (
            str(relative).startswith(SHOWCASE_PREFIX)
            and (
                "/outputs/" in f"/{relative}"
                or "/inputs/" in f"/{relative}"
            )
            and relative.suffix.casefold() in SHOWCASE_BINARY_SUFFIXES
        )
        if is_showcase_binary and not is_lfs:
            errors.append(f"showcase binary must use Git LFS: {relative}")
        if is_lfs and not is_showcase_binary:
            errors.append(f"Git LFS is reserved for curated showcase outputs: {relative}")

        if is_lfs:
            lfs_bytes += size
            if size > MAX_LFS_FILE_BYTES:
                errors.append(
                    f"LFS file exceeds {MAX_LFS_FILE_BYTES} bytes: {relative} ({size})"
                )
        else:
            ordinary_files += 1
            ordinary_bytes += size
            lowered_content = path.read_bytes().lower()
            for marker, label in FORBIDDEN_PUBLIC_CONTENT.items():
                if marker in lowered_content:
                    errors.append(f"{label} leaked into candidate file: {relative}")
            if size > MAX_NON_LFS_FILE_BYTES:
                errors.append(
                    "ordinary Git file exceeds "
                    f"{MAX_NON_LFS_FILE_BYTES} bytes: {relative} ({size})"
                )

    if ordinary_bytes > MAX_NON_LFS_TOTAL_BYTES:
        errors.append(
            "ordinary Git candidate total exceeds "
            f"{MAX_NON_LFS_TOTAL_BYTES} bytes ({ordinary_bytes})"
        )
    if lfs_bytes > MAX_LFS_TOTAL_BYTES:
        errors.append(
            f"Git LFS candidate total exceeds {MAX_LFS_TOTAL_BYTES} bytes ({lfs_bytes})"
        )

    inventory = Inventory(
        candidate_files=len(paths),
        ordinary_files=ordinary_files,
        lfs_files=len(lfs),
        ordinary_bytes=ordinary_bytes,
        lfs_bytes=lfs_bytes,
        by_top_level=dict(sorted(by_top_level.items())),
    )
    return inventory, sorted(set(errors))


def _format_mib(value: int) -> str:
    return f"{value / (1024 * 1024):.2f} MiB"


def main() -> int:
    """Run the repository hygiene gate."""

    try:
        inventory, errors = inspect_repository()
    except subprocess.CalledProcessError as exc:
        print(f"repository hygiene check could not inspect Git metadata: {exc}", file=sys.stderr)
        return 2

    print(
        "Repository inventory: "
        f"{inventory.candidate_files} candidates; "
        f"{inventory.ordinary_files} ordinary files "
        f"({_format_mib(inventory.ordinary_bytes)}); "
        f"{inventory.lfs_files} LFS files "
        f"({_format_mib(inventory.lfs_bytes)})."
    )
    for name, size in sorted(
        inventory.by_top_level.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"  {_format_mib(size):>10}  {name}")
    if errors:
        print("Repository hygiene violations:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Repository hygiene OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
