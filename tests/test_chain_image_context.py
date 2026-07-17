"""Regression tests: chain image stages thread compact refs, not base64.

A chain's image stage returns a large base64 payload from the provider. If that
payload were threaded forward as the stage's text (``@{previous}`` / ``@{<stage>}``
and, via packaging, ``@{page}``), a multi-page book would balloon the packaging
prompt with tens of MB of base64 and blow the model's context window. The engine
instead threads the artifact's ``file:`` path forward; the real bytes travel only
in the artifact metadata. These tests lock that in.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import pytest

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.engines.chain import ChainEngine
from weavemark.packaging import build_package_context

_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAE"
    "hQGAhKmMIQAAAABJRU5ErkJggg=="
)
# A base64 payload big enough that leaking even one copy would be obvious.
_BIG_B64 = base64.b64encode(_PNG_BYTES).decode("ascii") + ("A" * 50_000)


class _BigImageClient:
    """Fake image client returning an intentionally large base64 payload."""

    async def generate_image(self, prompt: str, model: str | None = None, **kwargs: Any):
        from types import SimpleNamespace

        image = SimpleNamespace(
            model_dump=lambda: {"url": None, "b64_json": _BIG_B64, "revised_prompt": None}
        )
        return SimpleNamespace(data=[image])


def _image_chain(count: int) -> str:
    return (
        f"@execute chain\n  repeat: page\n  count: {count}\n\n"
        "@prompt page\n  @output type: image\n    file: pages/page-@{index}.png\n"
        "    size: 512x512\n  Render page @{index}.\n"
    )


async def _compose(spec: str, base_dir: Path):
    controller = WeaveMarkController(WeaveMarkConfig())
    return await controller.compose(spec, {}, base_dir)


@pytest.mark.asyncio
async def test_image_stage_threads_file_path_not_base64(tmp_path: Path) -> None:
    result = await _compose(_image_chain(3), tmp_path)
    execution = await ChainEngine(client=_BigImageClient()).execute(result)

    page_steps = [s for s in execution.steps if s.metadata.get("stage") == "page"]
    assert [s.response for s in page_steps] == [
        "pages/page-1.png",
        "pages/page-2.png",
        "pages/page-3.png",
    ]
    for step in page_steps:
        assert _BIG_B64 not in step.response
    # The artifact metadata still carries the real image bytes for persistence.
    assert execution.metadata["artifacts"][0]["images"][0]["b64_json"] == _BIG_B64


@pytest.mark.asyncio
async def test_packaging_context_has_no_base64_blob(tmp_path: Path) -> None:
    result = await _compose(_image_chain(5), tmp_path)
    execution = await ChainEngine(client=_BigImageClient()).execute(result)

    context = build_package_context(
        {"title": "Book"},
        execution,
        {"page": [f"pages/page-{i}.png" for i in range(1, 6)]},
    )
    # @{page} is the compact list of paths, not 5 copies of a base64 blob.
    assert _BIG_B64 not in context["page"]
    assert context["page"].splitlines() == [f"pages/page-{i}.png" for i in range(1, 6)]
    assert len(context["page"]) < 500


@pytest.mark.asyncio
async def test_image_stage_without_file_falls_back_to_payload(tmp_path: Path) -> None:
    # No `file:` target -> the image is surfaced via the payload so it is not lost.
    spec = (
        "@execute chain\n\n@prompt shot\n  @output type: image\n    size: 512x512\n"
        "  Render one image.\n"
    )
    result = await _compose(spec, tmp_path)
    execution = await ChainEngine(client=_BigImageClient()).execute(result)
    assert execution.output == _BIG_B64
