"""Tests for incremental (streaming) artifact output.

The chain engine emits each ``@output file:`` artifact through an ``on_artifact``
callback the moment its stage produces it, so long multi-artifact runs (e.g. a
picture book, one page after another) persist page-by-page instead of only after
the whole run finishes. These tests cover the callback firing order, the
single-artifact ``persist_artifact_record`` atom, and that streaming writes each
file progressively while staying byte-identical to the end-of-run batch safety net.
"""

from __future__ import annotations

import base64
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.engines.chain import ChainEngine
from weavemark.packaging import persist_artifact_record, persist_execution_artifacts

# A 1x1 transparent PNG.
_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAE"
    "hQGAhKmMIQAAAABJRU5ErkJggg=="
)


def _image_chain(count: int) -> str:
    return (
        f"@execute chain\n  repeat: page\n  count: {count}\n\n"
        "@prompt page\n  @output type: image\n    file: page-@{index}.png\n"
        "    size: 512x512\n  Render page @{index}.\n"
    )


class _FakeChainClient:
    """Fake client for the chain engine: returns a tiny b64 PNG per stage."""

    async def generate_image(
        self, prompt: str, model: str | None = None, **kwargs: Any
    ) -> Any:
        encoded = base64.b64encode(_PNG_BYTES).decode("ascii")
        image = SimpleNamespace(
            model_dump=lambda b=encoded: {"url": None, "b64_json": b, "revised_prompt": None}
        )
        return SimpleNamespace(data=[image])


async def _compose(spec: str, base_dir: Path):
    controller = WeaveMarkController(WeaveMarkConfig())
    return await controller.compose(spec, {}, base_dir)


@pytest.mark.asyncio
async def test_chain_fires_on_artifact_per_stage_in_order(tmp_path: Path) -> None:
    result = await _compose(_image_chain(3), tmp_path)
    recorded: list[dict[str, Any]] = []

    execution = await ChainEngine(client=_FakeChainClient()).execute(
        result, on_artifact=lambda record: recorded.append(dict(record))
    )

    assert [r["file"] for r in recorded] == ["page-1.png", "page-2.png", "page-3.png"]
    assert [r["index"] for r in recorded] == [1, 2, 3]
    # The streamed records match the artifacts exposed at the end of the run.
    assert [a["file"] for a in execution.metadata["artifacts"]] == [
        "page-1.png",
        "page-2.png",
        "page-3.png",
    ]


@pytest.mark.asyncio
async def test_streaming_persists_each_artifact_progressively(tmp_path: Path) -> None:
    """Each artifact lands on disk as it is produced, not all at the very end."""
    result = await _compose(_image_chain(3), tmp_path)
    root = tmp_path / "out"
    snapshots: list[list[str]] = []

    def sink(record: dict[str, Any]) -> None:
        written = persist_artifact_record(record, root)
        assert written is not None
        # The file for THIS record exists the instant the callback runs.
        assert (root / written).is_file()
        snapshots.append(sorted(p.name for p in root.glob("*.png")))

    await ChainEngine(client=_FakeChainClient()).execute(result, on_artifact=sink)

    # Files accumulate one at a time — proof of progressive writing.
    assert snapshots == [
        ["page-1.png"],
        ["page-1.png", "page-2.png"],
        ["page-1.png", "page-2.png", "page-3.png"],
    ]
    assert (root / "page-2.png").read_bytes() == _PNG_BYTES


def test_persist_artifact_record_writes_one_and_guards(tmp_path: Path) -> None:
    root = tmp_path / "one"

    assert (
        persist_artifact_record(
            {"stage": "s", "index": 1, "file": "note.md", "text": "hi"}, root
        )
        == "note.md"
    )
    assert (root / "note.md").read_text(encoding="utf-8") == "hi"

    # Path escapes are rejected, and nothing is written.
    assert persist_artifact_record({"file": "../escape.md", "text": "no"}, root) is None
    assert not (tmp_path / "escape.md").exists()

    # No file target and no payload both yield None.
    assert persist_artifact_record({"text": "no target"}, root) is None
    assert persist_artifact_record({"file": "empty.md"}, root) is None
    assert not (root / "empty.md").exists()


@pytest.mark.asyncio
async def test_batch_safety_net_matches_streamed_output(tmp_path: Path) -> None:
    """The end-of-run batch writer produces the same files as streaming."""
    result = await _compose(_image_chain(3), tmp_path)

    streamed_root = tmp_path / "streamed"
    execution = await ChainEngine(client=_FakeChainClient()).execute(
        result, on_artifact=lambda record: persist_artifact_record(record, streamed_root)
    )

    batch_root = tmp_path / "batch"
    persist_execution_artifacts(execution, batch_root)

    streamed = {p.name: p.read_bytes() for p in streamed_root.iterdir()}
    batched = {p.name: p.read_bytes() for p in batch_root.iterdir()}
    assert streamed == batched
    assert sorted(streamed) == ["page-1.png", "page-2.png", "page-3.png"]
