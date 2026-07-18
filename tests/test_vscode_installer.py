"""Tests for the local VS Code extension installer."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = REPO_ROOT / "scripts" / "install_vscode_extension.py"


def _load_installer():
    spec = importlib.util.spec_from_file_location("vscode_installer_for_tests", INSTALLER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_copy_install_is_complete_and_idempotent(tmp_path: Path) -> None:
    installer = _load_installer()
    extensions = tmp_path / "extensions"
    arguments = [
        "--extensions-dir",
        str(extensions),
        "--skip-checks",
    ]

    assert installer.main(arguments) == 0
    destination = extensions / installer.INSTALL_DIRECTORY
    assert (destination / "package.json").is_file()
    assert (destination / "src/extension.js").is_file()
    marker = json.loads((destination / installer.MARKER_NAME).read_text())
    assert marker["extension_id"] == "paulosalem.weavemark"
    assert not (destination / "test").exists()

    (destination / "stale.txt").write_text("stale", encoding="utf-8")
    assert installer.main(arguments) == 0
    assert not (destination / "stale.txt").exists()


def test_link_install_and_uninstall_are_safe(tmp_path: Path) -> None:
    installer = _load_installer()
    extensions = tmp_path / "extensions"
    install_arguments = [
        "--extensions-dir",
        str(extensions),
        "--mode",
        "link",
        "--skip-checks",
    ]

    assert installer.main(install_arguments) == 0
    destination = extensions / installer.INSTALL_DIRECTORY
    assert destination.is_symlink()
    assert destination.resolve() == installer.SOURCE.resolve()

    assert installer.main(
        [
            "--extensions-dir",
            str(extensions),
            "--uninstall",
        ]
    ) == 0
    assert not destination.exists()
    assert installer.main(
        [
            "--extensions-dir",
            str(extensions),
            "--uninstall",
        ]
    ) == 0


def test_conflicting_destination_requires_force(tmp_path: Path) -> None:
    installer = _load_installer()
    extensions = tmp_path / "extensions"
    destination = extensions / installer.INSTALL_DIRECTORY
    destination.mkdir(parents=True)
    sentinel = destination / "keep.txt"
    sentinel.write_text("user data", encoding="utf-8")

    assert installer.main(
        [
            "--extensions-dir",
            str(extensions),
            "--skip-checks",
        ]
    ) == 1
    assert sentinel.read_text(encoding="utf-8") == "user data"

    assert installer.main(
        [
            "--extensions-dir",
            str(extensions),
            "--skip-checks",
            "--force",
        ]
    ) == 0
    assert not sentinel.exists()
    assert (destination / installer.MARKER_NAME).is_file()


def test_legacy_symlink_to_same_source_is_removed(tmp_path: Path) -> None:
    installer = _load_installer()
    extensions = tmp_path / "extensions"
    extensions.mkdir()
    legacy = extensions / "weavemark"
    legacy.symlink_to(installer.SOURCE, target_is_directory=True)

    assert installer.main(
        [
            "--extensions-dir",
            str(extensions),
            "--skip-checks",
        ]
    ) == 0
    assert not legacy.exists()
    assert (extensions / installer.INSTALL_DIRECTORY).is_dir()


def test_manifest_validation_rejects_wrong_identity(tmp_path: Path) -> None:
    installer = _load_installer()
    manifest = tmp_path / "package.json"
    manifest.write_text(
        json.dumps({"name": "other", "publisher": "paulosalem"}),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="manifest 'name'"):
        installer._read_manifest(manifest)
