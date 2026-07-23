"""Assertions for WeaveMark's reference-authority hierarchy."""

from __future__ import annotations

import inspect
import re
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


def test_semantic_transform_authority_requires_explicit_targets() -> None:
    system_prompt = (
        ROOT / "src" / "weavemark" / "prompts" / "weavemark.system.md"
    ).read_text(encoding="utf-8")
    semantics = (
        ROOT / "promplets" / "stdlib" / "prelude" / "semantics.weavemark.md"
    ).read_text(encoding="utf-8")

    assert "each call MUST provide a non-empty indented body" in system_prompt
    for directive in ("revise", "normalize", "style", "polish", "compress"):
        definition = semantics.split(f"@define {directive}\n", 1)[1].split(
            "\n@define ", 1
        )[0]
        assert "Required non-empty" in definition
        assert "If omitted" not in definition
        assert "enclosing specification scope" not in definition


def test_editor_metadata_matches_execution_and_tool_contracts() -> None:
    directives = (ROOT / "vscode-extension" / "src" / "directives.js").read_text(
        encoding="utf-8"
    )
    hovers = (ROOT / "vscode-extension" / "src" / "hovers.js").read_text(
        encoding="utf-8"
    )
    usage_reference = (ROOT / "docs" / "usage-reference.md").read_text(
        encoding="utf-8"
    )
    reference_html = (ROOT / "docs" / "reference.html").read_text(encoding="utf-8")

    for key in ("thought_step", "evaluate_step", "synthesize"):
        assert key in hovers
        assert key in usage_reference
        assert key in reference_html
    assert "Render-only documents return directly" in directives
    assert "Render-only documents return directly" in hovers
    assert "Parameters are optional by default" in directives
    assert "`(optional)` is invalid" in directives
    assert "ASCII ` - `" in directives


def test_execution_authority_matches_implemented_engines() -> None:
    system_prompt = (
        ROOT / "src" / "weavemark" / "prompts" / "weavemark.system.md"
    ).read_text(encoding="utf-8")

    assert (
        "`tree-of-thought`: **`thought_step`**, **`evaluate_step`**, "
        "**`synthesize`**"
    ) in system_prompt
    assert (
        "`simplified-tree-of-thought`: **`generate`**, **`evaluate`**, "
        "**`synthesize`**"
    ) in system_prompt
    for contract in (
        "trusted Python",
        "exactly one bound effect",
        "native runtime values",
        "maps to its declared implicit",
        "host protection policy",
        "configured LLM completes that document",
    ):
        assert contract in system_prompt


def test_effect_mode_authority_matches_runtime_metadata_contract() -> None:
    system_prompt = (
        ROOT / "src" / "weavemark" / "prompts" / "weavemark.system.md"
    ).read_text(encoding="utf-8")
    usage = (ROOT / "docs" / "usage-reference.md").read_text(encoding="utf-8")

    for text in (system_prompt, usage):
        collapsed = re.sub(r"\s+", " ", text)
        assert "observation or retrieval" in collapsed
        assert "external-state change" in collapsed
        assert "defaults to `read`" in collapsed
        assert "`read` and `write` are the complete mode set" in collapsed
        assert "not a sandbox" in collapsed
        assert "same binding for either mode" in collapsed
