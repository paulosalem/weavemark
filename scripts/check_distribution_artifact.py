"""Validate WeaveMark wheel/sdist size and content boundaries."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MAX_WHEEL_BYTES = 5 * 1024 * 1024
MAX_SDIST_BYTES = 10 * 1024 * 1024
MAX_MEMBER_BYTES = 2 * 1024 * 1024

FORBIDDEN_COMPONENTS = {
    ".DS_Store",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".vsix", ".whl"}
FORBIDDEN_PUBLIC_CONTENT = {
    b"prompting" + b" adventures": "confidential initiative name",
    b"/users/" + b"paulo" + b"salem": "personal POSIX home path",
    b"c:\\users\\" + b"paulo" + b"salem": "personal Windows home path",
    b"googledrive-" + b"paulo" + b"salem": "personal cloud-storage path",
}


@dataclass(frozen=True, slots=True)
class ArchiveMember:
    """One normalized distribution member."""

    name: str
    size: int
    content: bytes


def inspect_artifact(path: Path) -> list[str]:
    """Return policy violations for one built wheel or sdist."""

    errors: list[str] = []
    suffixes = path.suffixes
    if path.suffix == ".whl":
        maximum = MAX_WHEEL_BYTES
        artifact_kind = "wheel"
    elif suffixes[-2:] == [".tar", ".gz"]:
        maximum = MAX_SDIST_BYTES
        artifact_kind = "sdist"
    else:
        return [f"unsupported distribution artifact: {path}"]

    size = path.stat().st_size
    if size > maximum:
        errors.append(
            f"{artifact_kind} exceeds {maximum} bytes: {path.name} ({size})"
        )
    members = _read_members(path)
    names = [member.name for member in members]
    if len(names) != len(set(names)):
        errors.append(f"{artifact_kind} contains duplicate member names")

    for member in members:
        pure = PurePosixPath(member.name)
        if any(part in FORBIDDEN_COMPONENTS for part in pure.parts):
            errors.append(f"forbidden generated member: {member.name}")
        if pure.suffix.casefold() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden packaged artifact: {member.name}")
        if member.size > MAX_MEMBER_BYTES:
            errors.append(
                f"archive member exceeds {MAX_MEMBER_BYTES} bytes: "
                f"{member.name} ({member.size})"
            )
        if member.content.startswith(b"version https://git-lfs.github.com/spec/v1"):
            errors.append(f"Git LFS pointer leaked into distribution: {member.name}")
        lowered_content = member.content.lower()
        for marker, label in FORBIDDEN_PUBLIC_CONTENT.items():
            if marker in lowered_content:
                errors.append(f"{label} leaked into distribution: {member.name}")

    if artifact_kind == "wheel":
        if not any(name.startswith("weavemark/promplets/") for name in names):
            errors.append("wheel does not contain bundled promplets")
        for forbidden_root in ("examples/", "outputs/", "studies/", "tests/"):
            if any(name.startswith(forbidden_root) for name in names):
                errors.append(f"wheel contains repository-only {forbidden_root}")
    else:
        root_names = [
            name.split("/", 1)[1] if "/" in name else ""
            for name in names
        ]
        for forbidden_root in ("examples/", "outputs/"):
            if any(name.startswith(forbidden_root) for name in root_names):
                errors.append(f"sdist contains generated {forbidden_root}")
    return sorted(set(errors))


def _read_members(path: Path) -> list[ArchiveMember]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return [
                ArchiveMember(
                    name=info.filename,
                    size=info.file_size,
                    content=archive.read(info),
                )
                for info in archive.infolist()
                if not info.is_dir()
            ]
    with tarfile.open(path, "r:gz") as archive:
        members: list[ArchiveMember] = []
        for info in archive.getmembers():
            if not info.isfile():
                continue
            extracted = archive.extractfile(info)
            content = extracted.read() if extracted is not None else b""
            members.append(
                ArchiveMember(name=info.name, size=info.size, content=content)
            )
        return members


def main(arguments: list[str] | None = None) -> int:
    """Validate command-line artifact paths."""

    values = arguments if arguments is not None else sys.argv[1:]
    if not values:
        print("usage: check_distribution_artifact.py ARTIFACT ...", file=sys.stderr)
        return 2
    failed = False
    for value in values:
        path = Path(value)
        errors = inspect_artifact(path)
        if errors:
            failed = True
            print(f"{path}:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"{path}: distribution artifact OK ({path.stat().st_size} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
