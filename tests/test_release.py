"""Release-version contract tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parents[1]


def _load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "release_checker",
        ROOT / "scripts" / "check_release.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_release_tree(
    root: Path,
    *,
    version: str = "1.2.3",
    unreleased: str = "",
) -> None:
    (root / "src" / "weavemark").mkdir(parents=True)
    (root / "vscode-extension").mkdir()
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "weavemark"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (root / "src" / "weavemark" / "version.py").write_text(
        f'__version__ = "{version}"\n',
        encoding="utf-8",
    )
    (root / "vscode-extension" / "package.json").write_text(
        json.dumps({"version": version}),
        encoding="utf-8",
    )
    (root / ".github" / "workflows" / "ci.yml").write_text(
        f"assert weavemark.__version__ == '{version}'\n",
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## Unreleased\n\n{unreleased}"
        f"\n## {version} - 2026-07-19\n\n### Added\n\n- Release feature.\n",
        encoding="utf-8",
    )


def test_release_contract_accepts_synchronized_versions(tmp_path: Path) -> None:
    _write_release_tree(tmp_path)
    checker = _load_checker()

    release = checker.validate_release(tmp_path, "v1.2.3")

    assert release.version == "1.2.3"
    assert release.notes == "### Added\n\n- Release feature.\n"


def test_release_contract_rejects_version_drift(tmp_path: Path) -> None:
    _write_release_tree(tmp_path)
    checker = _load_checker()
    package = tmp_path / "vscode-extension" / "package.json"
    package.write_text(json.dumps({"version": "1.2.4"}), encoding="utf-8")

    with pytest.raises(checker.ReleaseValidationError, match="package.json=1.2.4"):
        checker.validate_release(tmp_path, "v1.2.3")


def test_release_contract_requires_empty_unreleased_section(tmp_path: Path) -> None:
    _write_release_tree(tmp_path, unreleased="### Added\n\n- Not finalized.\n")
    checker = _load_checker()

    with pytest.raises(
        checker.ReleaseValidationError,
        match="Unreleased.*must be empty",
    ):
        checker.validate_release(tmp_path, "v1.2.3")


@pytest.mark.parametrize("tag", ("1.2.3", "v1.2", "release-1.2.3"))
def test_release_contract_rejects_invalid_tags(tmp_path: Path, tag: str) -> None:
    _write_release_tree(tmp_path)
    checker = _load_checker()

    with pytest.raises(checker.ReleaseValidationError, match="vMAJOR.MINOR.PATCH"):
        checker.validate_release(tmp_path, tag)


def test_release_workflow_uses_oidc_and_immutable_pypi_versions() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )

    assert 'tags:\n      - "v*.*.*"' in workflow
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "password:" not in workflow
    assert "skip-existing:" not in workflow
    assert "GH_REPO: ${{ github.repository }}" in workflow
    assert 'gh release edit "$GITHUB_REF_NAME" --draft=false' in workflow
    assert 'python -m pip install -e ".[dev,convert,examples,ui]"' in workflow
