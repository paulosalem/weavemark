#!/usr/bin/env python3
"""Install the bundled WeaveMark extension into local VS Code variants."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "vscode-extension"
MARKER_NAME = ".weavemark-local-install.json"
INSTALL_DIRECTORY = "paulosalem.weavemark-local"
LEGACY_DIRECTORIES = ("weavemark",)
INSTALL_ENTRIES = (
    "package.json",
    "language-configuration.json",
    "LICENSE",
    "README.md",
    "src",
    "syntaxes",
    "themes",
)


@dataclass(frozen=True, slots=True)
class EditorTarget:
    """One supported editor and its local extension directory."""

    name: str
    label: str
    cli: str
    extension_dir: Path


def _targets(home: Path) -> dict[str, EditorTarget]:
    return {
        "code": EditorTarget(
            name="code",
            label="Visual Studio Code",
            cli="code",
            extension_dir=home / ".vscode" / "extensions",
        ),
        "code-insiders": EditorTarget(
            name="code-insiders",
            label="Visual Studio Code Insiders",
            cli="code-insiders",
            extension_dir=home / ".vscode-insiders" / "extensions",
        ),
        "codium": EditorTarget(
            name="codium",
            label="VSCodium",
            cli="codium",
            extension_dir=home / ".vscode-oss" / "extensions",
        ),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Install the bundled WeaveMark extension into local editor extension "
            "directories. The default copy mode is atomic and survives repo moves."
        )
    )
    parser.add_argument(
        "--target",
        choices=("auto", "code", "code-insiders", "codium", "all"),
        default="auto",
        help=(
            "Editor target. auto installs into detected variants; if none are "
            "detected it installs into Visual Studio Code."
        ),
    )
    parser.add_argument(
        "--extensions-dir",
        action="append",
        type=Path,
        default=[],
        help="Explicit extension directory; repeatable and overrides --target.",
    )
    parser.add_argument(
        "--mode",
        choices=("copy", "link"),
        default="copy",
        help="copy for a stable install (default), link for live development.",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove WeaveMark installs owned by this installer.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace/remove a conflicting destination not owned by this installer.",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip npm test/check before installation.",
    )
    return parser


def _read_manifest(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read extension manifest {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"Extension manifest must be a JSON object: {path}")
    expected = {"name": "weavemark", "publisher": "paulosalem"}
    for field, value in expected.items():
        if data.get(field) != value:
            raise RuntimeError(
                f"Extension manifest {field!r} must be {value!r}; "
                f"got {data.get(field)!r}."
            )
    return data


def _run_checks() -> None:
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is required for pre-install extension checks.")
    for command in ((npm, "test"), (npm, "run", "check")):
        subprocess.run(command, cwd=SOURCE, check=True)


def _resolve_targets(
    *,
    target_name: str,
    explicit_directories: list[Path],
    home: Path,
) -> list[EditorTarget]:
    if explicit_directories:
        return [
            EditorTarget(
                name=f"custom-{index}",
                label=f"custom directory {directory}",
                cli="",
                extension_dir=directory.expanduser().resolve(),
            )
            for index, directory in enumerate(explicit_directories, start=1)
        ]

    available = _targets(home)
    if target_name == "all":
        return list(available.values())
    if target_name != "auto":
        return [available[target_name]]
    detected = [
        target
        for target in available.values()
        if shutil.which(target.cli) is not None or target.extension_dir.is_dir()
    ]
    return detected or [available["code"]]


def _marker_payload(manifest: dict[str, object], mode: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "extension_id": "paulosalem.weavemark",
        "version": manifest.get("version"),
        "mode": mode,
        "source": str(SOURCE),
    }


def _is_owned(path: Path) -> bool:
    if path.is_symlink():
        return path.resolve() == SOURCE.resolve()
    marker = path / MARKER_NAME
    if not marker.is_file():
        return False
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(data, dict) and data.get("extension_id") == "paulosalem.weavemark"


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def _cleanup_legacy_links(extension_dir: Path) -> None:
    for name in LEGACY_DIRECTORIES:
        legacy = extension_dir / name
        if legacy.is_symlink() and legacy.resolve() == SOURCE.resolve():
            legacy.unlink()


def _prepare_copy(
    temporary: Path,
    manifest: dict[str, object],
) -> None:
    temporary.mkdir()
    for entry_name in INSTALL_ENTRIES:
        source = SOURCE / entry_name
        destination = temporary / entry_name
        if source.is_dir():
            shutil.copytree(source, destination)
        elif source.is_file():
            shutil.copy2(source, destination)
        else:
            raise RuntimeError(f"Required extension entry is missing: {source}")
    (temporary / MARKER_NAME).write_text(
        json.dumps(_marker_payload(manifest, "copy"), indent=2) + "\n",
        encoding="utf-8",
    )


def _replace_destination(destination: Path, prepared: Path, *, force: bool) -> None:
    if destination.exists() or destination.is_symlink():
        if not _is_owned(destination) and not force:
            raise RuntimeError(
                f"Refusing to replace unowned extension destination: {destination}. "
                "Use --force only after inspecting it."
            )
        backup = destination.with_name(
            f".{destination.name}.backup-{uuid.uuid4().hex}"
        )
        destination.rename(backup)
        try:
            prepared.rename(destination)
        except Exception:
            backup.rename(destination)
            raise
        _remove(backup)
    else:
        prepared.rename(destination)


def _install(
    target: EditorTarget,
    *,
    manifest: dict[str, object],
    mode: str,
    force: bool,
) -> Path:
    extension_dir = target.extension_dir
    extension_dir.mkdir(parents=True, exist_ok=True)
    _cleanup_legacy_links(extension_dir)
    destination = extension_dir / INSTALL_DIRECTORY
    temporary = extension_dir / f".{INSTALL_DIRECTORY}.tmp-{uuid.uuid4().hex}"
    try:
        if mode == "copy":
            _prepare_copy(temporary, manifest)
        else:
            temporary.symlink_to(SOURCE, target_is_directory=True)
        _replace_destination(destination, temporary, force=force)
    finally:
        if temporary.exists() or temporary.is_symlink():
            _remove(temporary)
    _verify_install(destination, manifest, mode)
    return destination


def _verify_install(
    destination: Path,
    manifest: dict[str, object],
    mode: str,
) -> None:
    if mode == "link":
        if not destination.is_symlink() or destination.resolve() != SOURCE.resolve():
            raise RuntimeError(f"Installed link does not resolve to source: {destination}")
    elif not _is_owned(destination):
        raise RuntimeError(f"Installed copy has no valid ownership marker: {destination}")
    installed = _read_manifest(destination / "package.json")
    if installed.get("version") != manifest.get("version"):
        raise RuntimeError(
            f"Installed version mismatch at {destination}: "
            f"{installed.get('version')} != {manifest.get('version')}"
        )
    for relative in ("src/extension.js", "syntaxes/weavemark.tmLanguage.json"):
        if not (destination / relative).is_file():
            raise RuntimeError(f"Installed extension is missing {relative}: {destination}")


def _uninstall(target: EditorTarget, *, force: bool) -> bool:
    extension_dir = target.extension_dir
    _cleanup_legacy_links(extension_dir)
    destination = extension_dir / INSTALL_DIRECTORY
    if not destination.exists() and not destination.is_symlink():
        return False
    if not _is_owned(destination) and not force:
        raise RuntimeError(
            f"Refusing to remove unowned extension destination: {destination}. "
            "Use --force only after inspecting it."
        )
    _remove(destination)
    return True


def main(arguments: list[str] | None = None) -> int:
    """Run the local extension installer."""

    args = _parser().parse_args(arguments)
    try:
        manifest = _read_manifest(SOURCE / "package.json")
        targets = _resolve_targets(
            target_name=args.target,
            explicit_directories=args.extensions_dir,
            home=Path.home(),
        )
        if not args.uninstall and not args.skip_checks:
            _run_checks()
        for target in targets:
            if args.uninstall:
                removed = _uninstall(target, force=args.force)
                action = "Removed" if removed else "Not installed"
                print(f"{action}: {target.label} ({target.extension_dir})")
            else:
                destination = _install(
                    target,
                    manifest=manifest,
                    mode=args.mode,
                    force=args.force,
                )
                print(
                    f"Installed WeaveMark {manifest.get('version')} for "
                    f"{target.label}: {destination}"
                )
        if not args.uninstall:
            print("Reload each target editor window to activate the extension.")
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
