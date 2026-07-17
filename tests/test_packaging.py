"""Tests for fully-in-language artifact packaging.

Covers the deterministic pieces (no live LLM required):
- ``@package`` directive parsing (render / convert forms, validation)
- ``@output ... file:`` persistence targets (runtime ``@{index}`` preserved)
- ``persist_execution_artifacts`` writing produced artifacts to disk
- ``build_package_context`` exposing stage outputs + ``@{<stage>_files}``
- ``run_packages`` end to end with a fake client and a stubbed converter
"""

from __future__ import annotations

import base64
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.engines.base import ExecutionResult
from weavemark.packaging import (
    build_package_context,
    persist_execution_artifacts,
    run_packages,
)
from weavemark.packaging import runner as runner_module

_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAE"
    "hQGAhKmMIQAAAABJRU5ErkJggg=="
)


async def _compose(spec: str, base_dir: Path, variables: dict[str, Any] | None = None):
    controller = WeaveMarkController(WeaveMarkConfig())
    return await controller.compose(spec, variables or {}, base_dir)


def _image_meta() -> dict[str, Any]:
    encoded = base64.b64encode(_PNG_BYTES).decode("ascii")
    return {"url": None, "b64_json": encoded, "revised_prompt": None}


# ── @package parsing ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_package_render_and_convert_parse(tmp_path: Path) -> None:
    spec = (
        "Draw something.\n\n"
        "@package template: tmpl.weavemark.md file: out/book.html\n"
        "@package from: out/book.html file: out/book.pdf\n"
    )
    result = await _compose(spec, tmp_path)
    assert result.errors == []
    assert result.packages == [
        {"file": "out/book.html", "template": "tmpl.weavemark.md"},
        {"file": "out/book.pdf", "from": "out/book.html"},
    ]


@pytest.mark.asyncio
async def test_package_requires_exactly_one_source(tmp_path: Path) -> None:
    both = await _compose(
        "x\n\n@package template: t.md from: a.html file: b.html\n", tmp_path
    )
    assert any("exactly one" in e for e in both.errors)

    neither = await _compose("x\n\n@package file: b.html\n", tmp_path)
    assert any("exactly one" in e for e in neither.errors)


@pytest.mark.asyncio
async def test_package_rejects_unknown_param_and_escape(tmp_path: Path) -> None:
    bad_param = await _compose(
        "x\n\n@package template: t.md file: b.html mode: fancy\n", tmp_path
    )
    assert any("Unsupported parameter" in e for e in bad_param.errors)

    escape = await _compose(
        "x\n\n@package template: t.md file: ../evil.html\n", tmp_path
    )
    assert any("relative" in e for e in escape.errors)


@pytest.mark.asyncio
async def test_package_variable_substituted(tmp_path: Path) -> None:
    spec = "x\n\n@package template: t.md file: @{name}.html\n"
    result = await _compose(spec, tmp_path, {"name": "story"})
    assert result.packages == [{"file": "story.html", "template": "t.md"}]


# ── @output file: persistence target ──────────────────────────────────


@pytest.mark.asyncio
async def test_output_file_preserves_runtime_placeholder(tmp_path: Path) -> None:
    spec = (
        "@execute chain\n  repeat: page\n  count: 2\n\n"
        "@prompt page\n  @output type: image\n"
        "    file: pages/page-@{index}.png\n    size: 512x512\n  Render @{index}.\n"
    )
    result = await _compose(spec, tmp_path)
    params = result.prompt_outputs["page"].params
    # @{index} is a runtime value: preserved through compile for per-iteration use.
    assert params["file"] == "pages/page-@{index}.png"
    assert params["size"] == "512x512"


# ── persist_execution_artifacts ───────────────────────────────────────


def test_persist_writes_ordered_image_files(tmp_path: Path) -> None:
    execution = ExecutionResult(
        output="",
        steps=[],
        metadata={
            "engine": "chain",
            "artifacts": [
                {"stage": "page", "index": 1, "file": "pages/page-1.png",
                 "images": [_image_meta()]},
                {"stage": "page", "index": 2, "file": "pages/page-2.png",
                 "images": [_image_meta()]},
            ],
        },
    )
    stage_files = persist_execution_artifacts(execution, tmp_path)
    assert stage_files == {"page": ["pages/page-1.png", "pages/page-2.png"]}
    for name in ("pages/page-1.png", "pages/page-2.png"):
        written = tmp_path / name
        assert written.is_file()
        assert written.read_bytes() == _PNG_BYTES


def test_persist_writes_text_artifacts_and_rejects_escape(tmp_path: Path) -> None:
    execution = ExecutionResult(
        output="",
        steps=[],
        metadata={
            "artifacts": [
                {"stage": "note", "index": 1, "file": "n.txt", "text": "hello"},
                {"stage": "bad", "index": 1, "file": "../escape.txt", "text": "no"},
            ]
        },
    )
    stage_files = persist_execution_artifacts(execution, tmp_path)
    assert stage_files == {"note": ["n.txt"]}
    assert (tmp_path / "n.txt").read_text() == "hello"
    assert not (tmp_path.parent / "escape.txt").exists()


# ── build_package_context ─────────────────────────────────────────────


def test_build_context_exposes_stage_outputs_and_files() -> None:
    execution = ExecutionResult(
        output="",
        steps=[
            SimpleNamespace(name="author", response='{"title":"T"}',
                            metadata={"stage": "author"}),
            SimpleNamespace(name="page_1", response="<img1>",
                            metadata={"stage": "page", "index": 1}),
        ],
        metadata={},
    )
    context = build_package_context(
        {"title": "T", "n": 2}, execution, {"page": ["pages/page-1.png"]}
    )
    assert context["title"] == "T"
    assert context["author"] == '{"title":"T"}'
    assert context["page_files"] == ["pages/page-1.png"]


# ── run_packages end to end ───────────────────────────────────────────


class _FakePackClient:
    """Fake client whose completion is the assembled deliverable text."""

    def __init__(self, html: str) -> None:
        self._html = html
        self.prompts: list[str] = []

    async def complete(self, prompt, model=None, **kwargs):
        self.prompts.append(prompt)
        return self._html


@pytest.mark.asyncio
async def test_run_packages_renders_then_converts(tmp_path: Path, monkeypatch) -> None:
    # A tiny packaging-template promplet that receives the artifact list.
    template = tmp_path / "tmpl.weavemark.md"
    template.write_text(
        "Assemble a page for @{title} using these files:\n@{page_files}\n",
        encoding="utf-8",
    )

    execution = ExecutionResult(
        output="",
        steps=[
            SimpleNamespace(name="author", response='{"title":"Orion"}',
                            metadata={"stage": "author"}),
        ],
        metadata={
            "artifacts": [
                {"stage": "page", "index": 1, "file": "pages/page-1.png",
                 "images": [_image_meta()]},
            ]
        },
    )
    packages = [
        {"file": "book.html", "template": "tmpl.weavemark.md"},
        {"file": "book.pdf", "from": "book.html"},
    ]

    converted: list[tuple[Path, Path]] = []

    def _fake_convert(source: Path, target: Path) -> bool:
        converted.append((source, target))
        target.write_bytes(b"%PDF-1.4 fake")
        return True

    monkeypatch.setattr(runner_module, "convert_file", _fake_convert)

    client = _FakePackClient("<html><img src='pages/page-1.png'></html>")
    results = await run_packages(
        packages,
        {"title": "Orion"},
        execution,
        base_dir=tmp_path,
        root=tmp_path,
        model="fake",
        client=client,
    )

    # image artifact persisted
    assert (tmp_path / "pages/page-1.png").read_bytes() == _PNG_BYTES
    # render step wrote the HTML from the fake completion; template saw the files
    assert (tmp_path / "book.html").read_text().startswith("<html>")
    assert "pages/page-1.png" in str(client.prompts[0])
    assert "Orion" in str(client.prompts[0])
    # convert step invoked and wrote the PDF
    assert converted == [(tmp_path / "book.html", tmp_path / "book.pdf")]
    assert (tmp_path / "book.pdf").is_file()
    assert [r.ok for r in results] == [True, True]
    assert [r.kind for r in results] == ["render", "convert"]


@pytest.mark.asyncio
async def test_run_packages_resolves_module_template(tmp_path: Path) -> None:
    library = tmp_path / "promplets"
    library.mkdir()
    (library / "template.weavemark.md").write_text(
        "@promplet version: 0.7\n"
        "@module test.packaging.template\n\n"
        "Assemble @{title} from @{page_files}.\n",
        encoding="utf-8",
    )
    client = _FakePackClient("<!doctype html><title>Module template</title>")

    results = await run_packages(
        [
            {
                "file": "book.html",
                "template": "module:test.packaging.template",
            }
        ],
        {
            "title": "Module Template",
            "text_in_image": "on",
            "cover_image": "",
        },
        ExecutionResult(output="", steps=[], metadata={}),
        base_dir=tmp_path,
        root=tmp_path / "out",
        model="test-model",
        client=client,
        stage_files={"page": ["pages/page-1.png"]},
    )

    assert [result.ok for result in results] == [True]
    assert (tmp_path / "out" / "book.html").read_text(encoding="utf-8") == (
        "<!doctype html><title>Module template</title>"
    )
    assert client.prompts


@pytest.mark.asyncio
async def test_run_packages_convert_reports_missing_source(tmp_path: Path) -> None:
    results = await run_packages(
        [{"file": "book.pdf", "from": "book.html"}],
        {},
        ExecutionResult(output="", steps=[], metadata={}),
        base_dir=tmp_path,
        root=tmp_path,
        model="fake",
    )
    assert results[0].ok is False
    assert "source not found" in results[0].note
