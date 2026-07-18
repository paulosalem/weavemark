"""Strict JSON and YAML promplet-variable file behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from weavemark.variable_files import VariablesFileError, load_variables_file


@pytest.mark.parametrize("suffix", (".yaml", ".yml"))
def test_yaml_variables_preserve_multiline_and_structures(
    tmp_path: Path,
    suffix: str,
) -> None:
    path = tmp_path / f"variables{suffix}"
    path.write_text(
        """
topic: release readiness
source_notes: |-
  First paragraph.

  Second paragraph.
include_checks: true
tags: [alpha, public]
run_date: 2026-07-17
""".lstrip(),
        encoding="utf-8",
    )

    assert load_variables_file(path) == {
        "topic": "release readiness",
        "source_notes": "First paragraph.\n\nSecond paragraph.",
        "include_checks": True,
        "tags": ["alpha", "public"],
        "run_date": "2026-07-17",
    }


def test_json_variables_remain_supported(tmp_path: Path) -> None:
    path = tmp_path / "variables.json"
    path.write_text('{"topic": "release", "count": 3}', encoding="utf-8")

    assert load_variables_file(path) == {"topic": "release", "count": 3}


@pytest.mark.parametrize(
    ("name", "content"),
    (
        ("duplicate.json", '{"topic": "one", "topic": "two"}'),
        ("duplicate.yaml", "topic: one\ntopic: two\n"),
    ),
)
def test_variable_files_reject_duplicate_keys(
    tmp_path: Path,
    name: str,
    content: str,
) -> None:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")

    with pytest.raises(VariablesFileError, match="Duplicate variable key 'topic'"):
        load_variables_file(path)


def test_variable_files_require_object_with_string_keys(tmp_path: Path) -> None:
    sequence = tmp_path / "sequence.yaml"
    sequence.write_text("- one\n- two\n", encoding="utf-8")
    numeric_key = tmp_path / "numeric.yaml"
    numeric_key.write_text("1: one\n", encoding="utf-8")

    with pytest.raises(VariablesFileError, match="must contain one object"):
        load_variables_file(sequence)
    with pytest.raises(VariablesFileError, match="variable name must be a string"):
        load_variables_file(numeric_key)


def test_variable_files_require_supported_extension(tmp_path: Path) -> None:
    path = tmp_path / "variables.txt"
    path.write_text("topic: release\n", encoding="utf-8")

    with pytest.raises(VariablesFileError, match=r"\.json, \.yaml, or \.yml"):
        load_variables_file(path)
