"""Tests for the public WeaveMark Python library API."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

import pytest

from weavemark import (
    CompileOptions,
    RuntimeConfig,
    WeaveMarkCompilationError,
    bundled_promplet,
    bundled_promplets,
    compile_file,
    compile_text,
    execute_file,
    execute_text,
    format_compiled_output,
    iter_bundled_promplets,
    load_runtime_config,
    read_bundled_promplet,
)
from weavemark.controller import CompositionResult
from weavemark.engines import ExecutionResult


def _write(path: Path, text: str) -> Path:
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")
    return path


def test_bundled_promplet_library_is_public() -> None:
    paths = list(iter_bundled_promplets())

    assert bundled_promplets().is_dir()
    assert bundled_promplet(paths[0]).is_file()
    assert read_bundled_promplet(paths[0])


class EchoEngine:
    async def execute(
        self,
        result: CompositionResult,
        config: RuntimeConfig | None = None,
        on_step: Any | None = None,
    ) -> ExecutionResult:
        return ExecutionResult(
            output=result.composed_prompt,
            metadata={"engine_config": config.engine_config if config else {}},
        )


@pytest.mark.asyncio
async def test_compile_text_compiles_in_memory_spec() -> None:
    result = await compile_text(
        "@promplet version: 0.7\nHello @{name}",
        {"name": "library"},
        options=CompileOptions(temperature=0.0),
    )

    assert result.errors == []
    assert result.composed_prompt == "Hello library"


@pytest.mark.asyncio
async def test_compile_file_uses_file_parent_for_relative_references(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "base.weavemark.md",
        """
        # Base

        Hello @{name}.
        """,
    )
    spec = _write(
        tmp_path / "main.weavemark.md",
        """
        @refine ./base.weavemark.md mingle: false
        """,
    )

    result = await compile_file(spec, {"name": "file API"})

    assert result.errors == []
    assert result.composed_prompt == "# Base\n\nHello file API."


@pytest.mark.asyncio
async def test_compile_file_uses_project_format_settings(tmp_path: Path) -> None:
    _write(
        tmp_path / "weavemark.json",
        """
        {
          "formats": {
            "liquid": {"extension": "liquid"}
          }
        }
        """,
    )
    spec = _write(
        tmp_path / "bundle.weavemark.md",
        """
        @compile format: markdown

        @prompt welcome role: system format: liquid
          Hello {{ user.name }}.
        """,
    )

    result = await compile_file(spec)

    assert result.errors == []
    assert result.composed_prompt == ""
    assert result.emits == {"welcome.system.liquid.md": "Hello {{ user.name }}."}


@pytest.mark.asyncio
async def test_execute_file_merges_runtime_variables_and_accepts_engine_object(
    tmp_path: Path,
) -> None:
    spec = _write(
        tmp_path / "hello.weavemark.md",
        """
        @promplet version: 0.7

        Hello @{name}.
        """,
    )
    runtime = RuntimeConfig(
        variables={"name": "runtime"},
        engine_config={"trace": True},
    )

    result = await execute_file(
        spec,
        {"name": "explicit"},
        runtime_config=runtime,
        engine=EchoEngine(),
    )

    assert result.engine == "EchoEngine"
    assert result.output == "Hello explicit."
    assert result.runtime_config is runtime
    assert result.execution.metadata == {"engine_config": {"trace": True}}


def test_format_compiled_output_renders_primary_formats() -> None:
    result = CompositionResult(composed_prompt="Hello", compile={"format": "markdown"})

    assert format_compiled_output(result) == "Hello"
    structured = json.loads(format_compiled_output(result, "json"))
    assert structured["composed_prompt"] == "Hello"


def test_load_runtime_config_from_mapping() -> None:
    runtime = load_runtime_config(
        {
            "engine": "reflection",
            "engine_config": {"max_iterations": 2},
            "prompts": {"generate": {"model": "gpt-5.5", "temperature": 0.8}},
            "variables": {"topic": "public API"},
        }
    )

    assert runtime is not None
    assert runtime.engine == "reflection"
    assert runtime.engine_config == {"max_iterations": 2}
    assert runtime.prompts["generate"].temperature == 0.8
    assert runtime.variables == {"topic": "public API"}


@pytest.mark.asyncio
async def test_execute_text_raises_for_compile_errors() -> None:
    with pytest.raises(WeaveMarkCompilationError) as exc:
        await execute_text(
            textwrap.dedent("""
            @prompt broken role: system format: missing-format
              This cannot be emitted because the format is unknown.
            """).strip(),
            engine=EchoEngine(),
        )

    assert exc.value.result.errors
