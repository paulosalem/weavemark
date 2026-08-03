"""Distribution contract for the WeaveMark FSLM engine."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_runtime_dependencies_require_httpx_compatible_releases() -> None:
    pyproject = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )
    dependencies = pyproject["project"]["dependencies"]

    assert "ellements[cli,execution,fslm]>=0.2.2,<0.3" in dependencies
    assert "litellm>=1.94.1,<2" in dependencies
    assert pyproject["project"]["optional-dependencies"]["examples"] == [
        "ellements[finance,web]>=0.2.2,<0.3"
    ]


def test_lm_eval_is_confined_to_the_benchmarking_extra() -> None:
    pyproject = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert not any(
        dependency.startswith("lm-eval")
        for dependency in pyproject["project"]["dependencies"]
    )
    assert pyproject["project"]["optional-dependencies"]["benchmarking"] == [
        "ellements[benchmarking]>=0.2.2,<0.3"
    ]
