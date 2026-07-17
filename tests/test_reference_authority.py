"""Assertions for WeaveMark's reference-authority hierarchy."""

from __future__ import annotations

import inspect
from pathlib import Path

import weavemark
from weavemark import api
from weavemark.app import create_parser
from weavemark.version import LANGUAGE_VERSION

ROOT = Path(__file__).parents[1]


def test_language_authority_and_grammar_mirror_are_explicit() -> None:
    development = (ROOT / "docs" / "development.md").read_text(encoding="utf-8")
    grammar = (ROOT / "docs" / "weavemark.ebnf").read_text(encoding="utf-8")
    system_prompt = (
        ROOT / "src" / "weavemark" / "prompts" / "weavemark.system.md"
    ).read_text(encoding="utf-8")

    authority = "weavemark.system.md` is the canonical source of truth"
    assert authority in development
    assert "This file MIRRORS the canonical WeaveMark" in grammar
    assert f"@promplet version: {LANGUAGE_VERSION}" in system_prompt


def test_executable_surfaces_are_self_authoritative() -> None:
    parser = create_parser()
    option_strings = {
        option for action in parser._actions for option in action.option_strings
    }
    assert {
        "--version",
        "--provenance",
        "--record-run",
        "--replay-run",
    } <= option_strings
    assert "provenance" in inspect.signature(api.compile_text).parameters
    assert "provenance" in inspect.signature(api.compile_file).parameters
    assert "ProvenanceOptions" in weavemark.__all__


def test_downstream_reference_documents_cover_core_provenance_flags() -> None:
    usage = (ROOT / "docs" / "usage-reference.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for option in ("--provenance", "--record-run", "--replay-run"):
        assert option in usage
        assert option in readme
