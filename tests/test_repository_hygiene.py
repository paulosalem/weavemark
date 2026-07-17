"""Release-artifact and dependency-boundary regression tests."""

from __future__ import annotations

import importlib.util
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _load_hygiene_module():
    spec = importlib.util.spec_from_file_location(
        "repository_hygiene",
        ROOT / "scripts" / "check_repository_hygiene.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_distribution_module():
    spec = importlib.util.spec_from_file_location(
        "distribution_hygiene",
        ROOT / "scripts" / "check_distribution_artifact.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_repository_candidate_inventory_passes() -> None:
    hygiene = _load_hygiene_module()

    inventory, errors = hygiene.inspect_repository(ROOT)

    assert errors == []
    assert inventory.lfs_files == 53
    assert inventory.lfs_bytes < hygiene.MAX_LFS_TOTAL_BYTES
    assert inventory.ordinary_bytes < hygiene.MAX_NON_LFS_TOTAL_BYTES


def test_core_and_optional_dependencies_have_upper_bounds() -> None:
    pyproject = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    dependency_groups = [
        pyproject["project"]["dependencies"],
        *pyproject["project"]["optional-dependencies"].values(),
    ]

    for group in dependency_groups:
        for requirement in group:
            if requirement.startswith("weavemark["):
                continue
            assert "<" in requirement, f"dependency has no upper bound: {requirement}"


def test_lfs_patterns_are_narrow_and_explicit() -> None:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()

    assert len(attributes) == 10
    assert all(line.startswith("examples/saved-artifact-workflows/") for line in attributes)
    assert all(" filter=lfs diff=lfs merge=lfs -text" in line for line in attributes)
    assert not any(line.startswith("*.") for line in attributes)


def test_distribution_gate_rejects_lfs_pointer_and_generated_members(
    tmp_path: Path,
) -> None:
    import zipfile

    distribution = _load_distribution_module()
    wheel = tmp_path / "weavemark-0.8.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "weavemark/promplets/example.weavemark.md",
            "version https://git-lfs.github.com/spec/v1\n",
        )
        archive.writestr("weavemark/__pycache__/bad.pyc", b"bad")

    errors = distribution.inspect_artifact(wheel)

    assert any("Git LFS pointer leaked" in error for error in errors)
    assert any("forbidden generated member" in error for error in errors)


def test_distribution_gate_accepts_minimal_wheel(tmp_path: Path) -> None:
    import zipfile

    distribution = _load_distribution_module()
    wheel = tmp_path / "weavemark-0.8.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("weavemark/__init__.py", "")
        archive.writestr(
            "weavemark/promplets/example.weavemark.md",
            "Example promplet.\n",
        )

    assert distribution.inspect_artifact(wheel) == []
