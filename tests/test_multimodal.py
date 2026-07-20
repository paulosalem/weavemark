"""Tests for WeaveMark multimodal support: image input + image output.

Covers the deterministic pieces (no LLM required):
- ``extract_image_refs`` lifting of Markdown/data-URI images
- ``ImageRef`` / ``OutputContract`` data model + serialization
- ``@compile images: on|off`` toggle
- ``@output type: text|image`` contract parsing and per-``@prompt`` scoping
- The ``SingleCallEngine`` multimodal input + image-generation paths
"""

from __future__ import annotations

import base64
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from weavemark.compilation.multimodal import (
    OutputContract,
    extract_image_refs,
)
from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.engines.single_call import SingleCallEngine

# A 1x1 transparent PNG.
_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAE"
    "hQGAhKmMIQAAAABJRU5ErkJggg=="
)
_DATA_URI = "data:image/png;base64," + base64.b64encode(_PNG_BYTES).decode("ascii")


@pytest.fixture()
def image_dir(tmp_path: Path) -> Path:
    (tmp_path / "chart.png").write_bytes(_PNG_BYTES)
    return tmp_path


async def _compose(spec: str, base_dir: Path, variables: dict[str, Any] | None = None):
    controller = WeaveMarkController(WeaveMarkConfig())
    return await controller.compose(spec, variables or {}, base_dir)


# ── extract_image_refs ────────────────────────────────────────────────


def test_extract_local_image(image_dir: Path) -> None:
    refs, warnings = extract_image_refs("See ![chart](chart.png).", image_dir)
    assert warnings == []
    assert len(refs) == 1
    ref = refs[0]
    assert ref.source == "path"
    assert ref.alt == "chart"
    assert ref.media_type == "image/png"
    assert ref.data is not None
    assert ref.data_uri is not None and ref.data_uri.startswith("data:image/png;base64,")


def test_extract_data_uri(tmp_path: Path) -> None:
    refs, warnings = extract_image_refs(f"![inline]({_DATA_URI})", tmp_path)
    assert warnings == []
    assert len(refs) == 1
    assert refs[0].source == "data"
    assert refs[0].media_type == "image/png"


def test_extract_remote_image_requires_extension(tmp_path: Path) -> None:
    refs, _ = extract_image_refs(
        "![a](https://example.com/pic.png) and ![b](https://example.com/page)",
        tmp_path,
    )
    assert [r.source for r in refs] == ["url"]
    assert refs[0].ref == "https://example.com/pic.png"


def test_extract_ignores_non_image_links(tmp_path: Path) -> None:
    refs, warnings = extract_image_refs("[a doc](notes.md) and [x](http://x.com)", tmp_path)
    assert refs == []
    assert warnings == []


def test_extract_missing_local_image_warns(tmp_path: Path) -> None:
    refs, warnings = extract_image_refs("![gone](nope.png)", tmp_path)
    assert refs == []
    assert warnings == ["Image reference not found: nope.png"]


# ── data model ────────────────────────────────────────────────────────


def test_image_ref_to_dict_elides_base64(image_dir: Path) -> None:
    refs, _ = extract_image_refs("![c](chart.png)", image_dir)
    payload = refs[0].to_dict()
    assert payload["data"].startswith("<base64:")
    full = refs[0].to_dict(include_data=True)
    assert full["data"] == refs[0].data


def test_output_contract_roundtrip() -> None:
    contract = OutputContract.from_dict({"type": "image", "size": "1024x1024"})
    assert contract.is_image
    assert contract.to_dict() == {"type": "image", "size": "1024x1024"}
    text = OutputContract.from_dict({"type": "bogus"})
    assert text.type == "text"


# ── controller integration ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_images_lifted_by_default(image_dir: Path) -> None:
    result = await _compose("Analyze ![chart](chart.png).", image_dir)
    assert result.errors == []
    assert "default" in result.prompt_images
    assert result.prompt_images["default"][0].source == "path"


@pytest.mark.asyncio
async def test_compile_images_off_disables_lifting(image_dir: Path) -> None:
    spec = "@compile images: off\n\nAnalyze ![chart](chart.png)."
    result = await _compose(spec, image_dir)
    assert result.errors == []
    assert result.prompt_images == {}
    assert result.compile.get("images") is False


@pytest.mark.asyncio
async def test_output_image_contract_no_text_injection(tmp_path: Path) -> None:
    spec = "Draw a fox.\n\n@output type: image\n  size: 1024x1024\n  quality: high\n"
    result = await _compose(spec, tmp_path)
    assert result.errors == []
    contract = result.prompt_outputs["default"]
    assert contract.is_image
    assert contract.params["size"] == "1024x1024"
    assert "Output format" not in result.composed_prompt


@pytest.mark.asyncio
async def test_output_text_injects_obligation(tmp_path: Path) -> None:
    result = await _compose('@output "Return JSON only."', tmp_path)
    assert result.errors == []
    assert result.prompt_outputs["default"].type == "text"
    assert "Return JSON only." in result.composed_prompt


@pytest.mark.asyncio
async def test_output_per_prompt_scope(tmp_path: Path) -> None:
    spec = (
        "@execute reflection\n\n"
        "@prompt generate\n  Draft it.\n\n"
        "@prompt critique\n  Critique it.\n\n"
        "@prompt revise\n  @output type: image\n    size: 512x512\n  Render it.\n"
    )
    result = await _compose(spec, tmp_path)
    assert result.errors == []
    assert "revise" in result.prompt_outputs
    assert result.prompt_outputs["revise"].is_image
    assert "default" not in result.prompt_outputs


@pytest.mark.asyncio
async def test_to_dict_serializes_multimodal(image_dir: Path) -> None:
    spec = "Analyze ![chart](chart.png).\n\n@output type: image\n  size: 256x256\n"
    result = await _compose(spec, image_dir)
    payload = result.to_dict()
    assert "prompt_images" in payload
    assert "prompt_outputs" in payload
    assert payload["prompt_outputs"]["default"]["type"] == "image"
    assert payload["prompt_images"]["default"][0]["data"].startswith("<base64:")


# ── engine execution (fake client) ────────────────────────────────────


class _FakeClient:
    def __init__(self) -> None:
        self.complete_messages: Any = None
        self.generate_call: dict[str, Any] | None = None
        self.edit_call: dict[str, Any] | None = None

    async def complete(self, messages, model=None, temperature=0.7, **kwargs):
        self.complete_messages = messages
        return "TEXT-ANSWER"

    async def generate_image(self, prompt, model=None, **kwargs):
        self.generate_call = {"prompt": prompt, "model": model, "kwargs": kwargs}
        image = SimpleNamespace(
            model_dump=lambda: {
                "url": "https://img/out.png",
                "b64_json": None,
                "revised_prompt": None,
            }
        )
        return SimpleNamespace(data=[image])

    async def edit_image(self, prompt, images, model=None, **kwargs):
        self.edit_call = {
            "prompt": prompt,
            "model": model,
            "reference_count": len(list(images)),
            "kwargs": kwargs,
        }
        image = SimpleNamespace(
            model_dump=lambda: {
                "url": None,
                "b64_json": "ZWRpdGVk",
                "revised_prompt": None,
            }
        )
        return SimpleNamespace(data=[image])


@pytest.mark.asyncio
async def test_engine_sends_image_input_as_multimodal(image_dir: Path) -> None:
    result = await _compose("Describe ![chart](chart.png).", image_dir)
    engine = SingleCallEngine(client=_FakeClient())
    execution = await engine.execute(result)
    assert execution.output == "TEXT-ANSWER"
    assert execution.metadata["image_inputs"] == 1
    parts = engine.client.complete_messages[-1]["content"]
    assert [p["type"] for p in parts] == ["text", "image_url"]


@pytest.mark.asyncio
async def test_engine_generates_image(tmp_path: Path) -> None:
    spec = "Draw a fox.\n\n@output type: image\n  size: 1024x1024\n  quality: high\n"
    result = await _compose(spec, tmp_path)
    engine = SingleCallEngine(client=_FakeClient())
    execution = await engine.execute(result)
    assert execution.metadata["output_type"] == "image"
    assert execution.metadata["method"] == "generate_image"
    assert execution.metadata["model"] == "gpt-image-2"
    assert engine.client.generate_call["kwargs"] == {
        "size": "1024x1024",
        "quality": "high",
    }
    assert engine.client.edit_call is None
    assert execution.output == "https://img/out.png"


@pytest.mark.asyncio
async def test_engine_ignores_references_without_edit_flag(image_dir: Path) -> None:
    spec = "Redraw ![ref](chart.png) as a neon poster.\n\n@output type: image\n"
    result = await _compose(spec, image_dir)
    engine = SingleCallEngine(client=_FakeClient())
    execution = await engine.execute(result)
    # Image inputs present, but editing is opt-in: default is text-to-image.
    assert execution.metadata["method"] == "generate_image"
    assert execution.metadata["reference_images"] == 0
    assert engine.client.edit_call is None


@pytest.mark.asyncio
async def test_engine_edits_image_when_edit_enabled(image_dir: Path) -> None:
    spec = (
        "Redraw ![ref](chart.png) as a neon poster.\n\n"
        "@output type: image\n  size: 1024x1024\n  edit: on\n"
    )
    result = await _compose(spec, image_dir)
    engine = SingleCallEngine(client=_FakeClient())
    execution = await engine.execute(result)
    assert execution.metadata["method"] == "edit_image"
    assert execution.metadata["reference_images"] == 1
    assert engine.client.edit_call is not None
    assert engine.client.edit_call["reference_count"] == 1
    assert engine.client.generate_call is None


# ── artifact-aware reflection engine ──────────────────────────────────


class _FakeReflectionClient:
    """Fake client for the image reflection loop: scripted vision critiques."""

    def __init__(self, critiques: list[str]) -> None:
        self._critiques = list(critiques)
        self.generate_calls = 0
        self.edit_calls = 0
        self.edit_reference_counts: list[int] = []
        self.complete_calls = 0

    async def generate_image(self, prompt, model=None, **kwargs):
        self.generate_calls += 1
        return self._image_response()

    async def edit_image(self, prompt, images, model=None, **kwargs):
        self.edit_calls += 1
        self.edit_reference_counts.append(len(list(images)))
        return self._image_response()

    def _image_response(self):
        encoded = base64.b64encode(_PNG_BYTES).decode("ascii")
        image = SimpleNamespace(
            model_dump=lambda b=encoded: {
                "url": None,
                "b64_json": b,
                "revised_prompt": None,
            }
        )
        return SimpleNamespace(data=[image])

    async def complete(self, messages, model=None, **kwargs):
        index = self.complete_calls
        self.complete_calls += 1
        return self._critiques[index] if index < len(self._critiques) else "OK"


_REFLECTION_SPEC = (
    "@execute reflection\n  rounds: 3\n\n"
    "@prompt generate\n  @output type: image\n    size: 1024x1024\n  Draw one robot.\n\n"
    "@prompt critique\n  Reply OK or list defects.\n\n"
    "@prompt revise\n  @output type: image\n    size: 1024x1024\n  Fix: @{critique}\n"
)


@pytest.mark.asyncio
async def test_reflection_image_loop_inspects_and_stops(tmp_path: Path) -> None:
    from weavemark.engines.reflection import ReflectionEngine

    result = await _compose(_REFLECTION_SPEC, tmp_path)
    assert result.prompt_outputs["generate"].is_image
    assert result.prompt_outputs["revise"].is_image

    client = _FakeReflectionClient(["Two robots visible in the frame.", "OK"])
    execution = await ReflectionEngine(client=client).execute(result)

    assert execution.metadata["output_type"] == "image"
    assert execution.metadata["satisfied"] is True
    names = [step.name for step in execution.steps]
    assert names[:3] == ["generate", "critique_0", "revise_0"]
    assert "stop" in names
    # generate + one revise render; two vision critiques.
    assert client.generate_calls == 2
    assert client.complete_calls == 2


@pytest.mark.asyncio
async def test_reflection_image_loop_exhausts_rounds(tmp_path: Path) -> None:
    from weavemark.engines.reflection import ReflectionEngine

    spec = _REFLECTION_SPEC.replace("rounds: 3", "rounds: 2")
    result = await _compose(spec, tmp_path)

    client = _FakeReflectionClient(["still two robots", "still off-model"])
    execution = await ReflectionEngine(client=client).execute(result)

    assert execution.metadata["satisfied"] is False
    # generate + two revises; two critiques (no early stop).
    assert client.generate_calls == 3
    assert client.complete_calls == 2


@pytest.mark.asyncio
async def test_reflection_edit_based_revise(tmp_path: Path) -> None:
    from weavemark.engines.reflection import ReflectionEngine

    # revise opts into edit: on -> corrections edit the PREVIOUS render in place.
    spec = _REFLECTION_SPEC.replace(
        "@prompt revise\n  @output type: image\n    size: 1024x1024\n",
        "@prompt revise\n  @output type: image\n    size: 1024x1024\n    edit: on\n",
    )
    result = await _compose(spec, tmp_path)
    assert result.prompt_outputs["revise"].params.get("edit") == "on"

    client = _FakeReflectionClient(["one defect", "OK"])
    execution = await ReflectionEngine(client=client).execute(result)

    assert execution.metadata["satisfied"] is True
    # generate uses generate_image; the single revise edits the previous render.
    assert client.generate_calls == 1
    assert client.edit_calls == 1
    # The previous render is passed as the base image to edit.
    assert client.edit_reference_counts == [1]
    revise_steps = [s for s in execution.steps if s.name.startswith("revise_")]
    assert revise_steps[0].metadata["method"] == "edit_image"


# ── chain engine (sequential prompt chaining) ─────────────────────────


class _FakeChainClient:
    """Fake client for the chain engine: records prompts, returns b64 images."""

    def __init__(self, text: str = "PREV") -> None:
        self._text = text
        self.complete_prompts: list[str] = []
        self.generate_prompts: list[str] = []
        self.edit_calls: list[int] = []

    async def complete(self, prompt, model=None, **kwargs):
        self.complete_prompts.append(prompt)
        return self._text

    async def generate_image(self, prompt, model=None, **kwargs):
        self.generate_prompts.append(prompt)
        return self._img()

    async def edit_image(self, prompt, images, model=None, **kwargs):
        self.edit_calls.append(len(list(images)))
        return self._img()

    def _img(self):
        encoded = base64.b64encode(_PNG_BYTES).decode("ascii")
        image = SimpleNamespace(
            model_dump=lambda b=encoded: {"url": None, "b64_json": b, "revised_prompt": None}
        )
        return SimpleNamespace(data=[image])


@pytest.mark.asyncio
async def test_chain_threads_previous_output(tmp_path: Path) -> None:
    from weavemark.engines.chain import ChainEngine

    spec = (
        "@execute chain\n\n"
        "@prompt concept\n  Invent a mascot.\n\n"
        "@prompt image\n  @output type: image\n    size: 1024x1024\n"
        "  Render: @{concept}\n"
    )
    result = await _compose(spec, tmp_path)
    assert list(result.prompts.keys()) == ["concept", "image"]

    client = _FakeChainClient(text="a sleepy owl")
    execution = await ChainEngine(client=client).execute(result)
    # the image stage prompt saw the prior stage's output via @{concept}.
    assert "a sleepy owl" in client.generate_prompts[0]
    assert [s.name for s in execution.steps] == ["concept", "image"]
    assert execution.metadata["engine"] == "chain"


@pytest.mark.asyncio
async def test_chain_repeat_produces_n_outputs(tmp_path: Path) -> None:
    from weavemark.engines.chain import ChainEngine

    spec = (
        "@execute chain\n  repeat: page\n  count: 3\n\n"
        "@prompt page\n  @output type: image\n    size: 512x512\n"
        "  Page @{index} of @{count}.\n"
    )
    result = await _compose(spec, tmp_path)
    client = _FakeChainClient()
    execution = await ChainEngine(client=client).execute(result)
    # one render per repeat iteration.
    assert len(client.generate_prompts) == 3
    assert [s.name for s in execution.steps] == ["page_1", "page_2", "page_3"]
    # each iteration saw its index.
    assert "Page 1 of 3" in client.generate_prompts[0]
    assert "Page 3 of 3" in client.generate_prompts[2]


@pytest.mark.asyncio
async def test_chain_image_visual_carry_via_edit(tmp_path: Path) -> None:
    from weavemark.engines.chain import ChainEngine

    spec = (
        "@execute chain\n  repeat: frame\n  count: 2\n\n"
        "@prompt frame\n  @output type: image\n    size: 512x512\n    edit: on\n"
        "  Frame @{index}.\n"
    )
    result = await _compose(spec, tmp_path)
    client = _FakeChainClient()
    await ChainEngine(client=client).execute(result)
    # first frame generates; second frame edits the previous frame (visual carry).
    assert len(client.generate_prompts) == 1
    assert client.edit_calls == [1]


# ── nested @match + @output variable substitution ─────────────────────


@pytest.mark.asyncio
async def test_nested_match_resolves_inner_branch(tmp_path: Path) -> None:
    """A @match nested inside a @match branch selects deterministically."""
    spec = (
        "@match story_format\n"
        '  "picture-book" ==>\n'
        "    A picture book.\n"
        "    @match text_in_image\n"
        '      "off" ==>\n'
        "        Narration printed separately.\n"
        "      _ ==>\n"
        "        Narration lettered into the image.\n"
        '  "comic-strip" ==>\n'
        "    A comic strip.\n"
    )
    # Default (missing text_in_image) -> wildcard -> baked into the image.
    baked = await _compose(spec, tmp_path, {"story_format": "picture-book"})
    assert "lettered into the image" in baked.composed_prompt
    assert "printed separately" not in baked.composed_prompt
    assert "comic strip" not in baked.composed_prompt.lower()

    # Explicit "off" -> the inner named branch wins.
    separate = await _compose(
        spec, tmp_path, {"story_format": "picture-book", "text_in_image": "off"}
    )
    assert "printed separately" in separate.composed_prompt
    assert "lettered into the image" not in separate.composed_prompt

    # The sibling outer branch is unaffected by the nested match.
    comic = await _compose(spec, tmp_path, {"story_format": "comic-strip"})
    assert "comic strip" in comic.composed_prompt.lower()
    assert "picture book" not in comic.composed_prompt.lower()


@pytest.mark.asyncio
async def test_output_image_params_variable_substituted(tmp_path: Path) -> None:
    """@output type: image params resolve @{var} from companion variables."""
    spec = (
        "@prompt page\n"
        "  @output type: image\n"
        "    size: @{image_size}\n"
        "    model: @{image_model}\n"
        "  Draw it.\n"
    )
    result = await _compose(
        spec,
        tmp_path,
        {"image_size": "1536x1024", "image_model": "gpt-image-2"},
    )
    contract = result.prompt_outputs["page"]
    assert contract.is_image
    assert contract.params["size"] == "1536x1024"
    assert contract.params["model"] == "gpt-image-2"


# ── children's book as an @execute chain ──────────────────────────────

_BOOK_VARS = {
    "title": "Orion",
    "audience": "children aged 3 to 5",
    "page_count": 4,
    "text_in_image": "on",
    "image_size": "1536x1024",
    "image_quality": "high",
    "image_model": "gpt-image-2",
    "tone": "warm",
    "art_style": "bright-storybook",
    "premise": "A small purple dragon learns new skills.",
    "characters": "- Orion: a small round purple dragon.",
    "setting": "A sunny valley.",
    "lessons": "trying again after a wobble.",
    "pages": [
        {"scene": "Orion tries to fly from a low hill.", "text": "Up, up... wobble!"},
        {"scene": "Orion asks a robin for help.", "text": "Show me how, please."},
        {"scene": "Orion practices one careful wingbeat.", "text": "Slow and steady."},
        {"scene": "Orion glides home beside the robin.", "text": "I did it!"},
    ],
}


async def _compose_book(base_dir: Path, overrides: dict[str, Any] | None = None):
    from weavemark.controller import WeaveMarkConfig, WeaveMarkController

    spec_path = (
        Path(__file__).resolve().parents[1]
        / "promplets/catalog/executable/childrens-book.weavemark.md"
    )
    variables = {**_BOOK_VARS, **(overrides or {})}
    controller = WeaveMarkController(WeaveMarkConfig())
    return await controller.compose(
        spec_path.read_text(encoding="utf-8"),
        variables,
        spec_path.parent,
    )


@pytest.mark.asyncio
async def test_childrens_book_compiles_as_chain(tmp_path: Path) -> None:
    result = await _compose_book(tmp_path)
    assert result.errors == []
    # author (text) then page (image) stages, in source order.
    assert list(result.prompts.keys()) == ["author", "page"]
    assert result.execution["type"] == "chain"
    assert result.execution["repeat"] == "page"
    # count: @{page_count} resolved to an int at compile time.
    assert result.execution["count"] == 4
    # the page stage carries a resolved image contract.
    page = result.prompt_outputs["page"]
    assert page.is_image
    assert page.params["size"] == "1536x1024"
    assert page.params["model"] == "gpt-image-2"
    assert "@{" not in str(page.params["size"])
    # the author stage refines the core with the baked-text default on.
    author = result.prompts["author"]
    assert "picture book" in author.lower()
    assert "drawn directly INTO the illustration" in author
    # the page stage threads the authored book + runtime index (left for runtime).
    assert "@{author}" in result.prompts["page"]
    assert "@{index}" in result.prompts["page"]


@pytest.mark.asyncio
async def test_childrens_book_off_mode_keeps_text_separate(tmp_path: Path) -> None:
    result = await _compose_book(tmp_path, {"text_in_image": "off"})
    author = result.prompts["author"]
    assert "NO text rendered in the image" in author
    assert "drawn directly INTO the illustration" not in author


@pytest.mark.asyncio
async def test_childrens_book_chain_runs_end_to_end(tmp_path: Path) -> None:
    """The chain authors once then renders one image per page."""
    from weavemark.engines.chain import ChainEngine

    result = await _compose_book(tmp_path)
    book = (
        '{"title": "Orion", "pages": ['
        '{"page": 1, "illustration": "p1", "text": ["a"]},'
        '{"page": 2, "illustration": "p2", "text": ["b"]},'
        '{"page": 3, "illustration": "p3", "text": ["c"]},'
        '{"page": 4, "illustration": "p4", "text": ["d"]}]}'
    )
    client = _FakeChainClient(text=book)
    execution = await ChainEngine(client=client).execute(result)

    # one authoring text call, four page renders (count == page_count).
    assert len(client.complete_prompts) == 1
    assert "picture book" in client.complete_prompts[0].lower()
    assert len(client.generate_prompts) == 4
    assert len(execution.metadata["artifacts"]) == 4
    # every page render saw the authored book via @{author}.
    assert all("p1" in prompt or "Orion" in prompt for prompt in client.generate_prompts)
    step_names = [s.name for s in execution.steps]
    assert step_names == ["author", "page_1", "page_2", "page_3", "page_4"]


# ── reflection as a production chain + critique/revise loop ────────────


class _FakeProductionReflectionClient:
    """Fake for generalized reflection: author (multimodal) + render + critiques.

    The first ``complete`` is the author production stage; later ``complete``
    calls are the vision critiques.
    """

    def __init__(self, author_text: str, critiques: list[str]) -> None:
        self._author_text = author_text
        self._critiques = list(critiques)
        self.complete_messages: list[Any] = []
        self.generate_prompts: list[str] = []
        self.edit_prompts: list[str] = []
        self.edit_reference_counts: list[int] = []

    async def complete(self, messages, model=None, **kwargs):
        self.complete_messages.append(messages)
        if len(self.complete_messages) == 1:
            return self._author_text
        idx = len(self.complete_messages) - 2
        return self._critiques[idx] if idx < len(self._critiques) else "OK"

    async def generate_image(self, prompt, model=None, **kwargs):
        self.generate_prompts.append(prompt)
        return self._img()

    async def edit_image(self, prompt, images, model=None, **kwargs):
        self.edit_prompts.append(prompt)
        self.edit_reference_counts.append(len(list(images)))
        return self._img()

    def _img(self):
        encoded = base64.b64encode(_PNG_BYTES).decode("ascii")
        image = SimpleNamespace(
            model_dump=lambda b=encoded: {"url": None, "b64_json": b, "revised_prompt": None}
        )
        return SimpleNamespace(data=[image])


_PRODUCTION_REFLECTION_SPEC = (
    "@execute reflection\n  rounds: 2\n\n"
    "@prompt author\n  Write an image prompt about @{topic}.\n  ![ref](chart.png)\n\n"
    "@prompt generate\n  @output type: image\n    file: art.png\n    size: 1024x1024\n"
    "  @{author}\n\n"
    "@prompt critique\n  Judge @{author}. Reply OK or defects.\n\n"
    "@prompt revise\n  @output type: image\n    size: 1024x1024\n    edit: on\n"
    "  @{author}\n  {{critique}}\n"
)


def test_reflection_production_stages_excludes_loop_roles() -> None:
    from weavemark.controller import CompositionResult
    from weavemark.engines.reflection import ReflectionEngine

    result = CompositionResult(
        composed_prompt="",
        prompts={"author": "a", "generate": "g", "critique": "c", "revise": "r"},
    )
    assert ReflectionEngine._production_stages(result) == ["author", "generate"]


@pytest.mark.asyncio
async def test_reflection_production_chain_threads_and_sees_refs(image_dir: Path) -> None:
    from weavemark.engines.reflection import ReflectionEngine

    result = await _compose(_PRODUCTION_REFLECTION_SPEC, image_dir)
    assert list(result.prompts.keys()) == ["author", "generate", "critique", "revise"]
    # author is the reference-reading production stage; generate is the artifact.
    assert len(result.prompt_images["author"]) == 1
    assert result.prompt_outputs["generate"].params["file"] == "art.png"

    client = _FakeProductionReflectionClient("AUTHORED SCRIPT", ["OK"])
    execution = await ReflectionEngine(client=client).execute(result)

    # The author stage saw the reference image (multimodal message, not a string).
    assert isinstance(client.complete_messages[0], list)
    # Its output threaded into the render stage and the critique.
    assert "AUTHORED SCRIPT" in client.generate_prompts[0]
    assert "AUTHORED SCRIPT" in str(client.complete_messages[1])
    # Steps: production chain then the loop, stopping on the satisfied critique.
    assert [s.name for s in execution.steps] == [
        "author",
        "generate",
        "critique_0",
        "stop",
    ]
    assert execution.metadata["satisfied"] is True
    # The artifact stage's file: is recorded for persistence.
    assert execution.metadata["file"] == "art.png"


@pytest.mark.asyncio
async def test_reflection_generate_conditions_on_references(image_dir: Path) -> None:
    """A production image stage with edit: on sends its refs to the image model."""
    from weavemark.engines.reflection import ReflectionEngine

    spec = (
        "@execute reflection\n  rounds: 2\n\n"
        "@prompt author\n  Write a prompt.\n\n"
        "@prompt generate\n  @output type: image\n    file: art.png\n    size: 1024x1024\n"
        "    edit: on\n  @{author}\n  ![ref](chart.png)\n\n"
        "@prompt critique\n  Reply OK or defects.\n\n"
        "@prompt revise\n  @output type: image\n    size: 1024x1024\n    edit: on\n"
        "  @{author}\n  {{critique}}\n"
    )
    result = await _compose(spec, image_dir)
    assert len(result.prompt_images["generate"]) == 1

    client = _FakeProductionReflectionClient("SCRIPT", ["OK"])
    await ReflectionEngine(client=client).execute(result)

    # The render conditioned directly on the embedded reference (edit endpoint).
    assert client.edit_reference_counts == [1]
    assert "SCRIPT" in client.edit_prompts[0]


@pytest.mark.asyncio
async def test_reflection_artifact_persists_via_output_file(image_dir: Path) -> None:
    from weavemark.engines.reflection import ReflectionEngine
    from weavemark.packaging import (
        has_persistable_artifacts,
        persist_execution_artifacts,
    )

    result = await _compose(_PRODUCTION_REFLECTION_SPEC, image_dir)
    client = _FakeProductionReflectionClient("SCRIPT", ["OK"])
    execution = await ReflectionEngine(client=client).execute(result)

    assert has_persistable_artifacts(execution)
    root = image_dir / "out"
    stage_files = persist_execution_artifacts(execution, root)
    assert stage_files == {"default": ["art.png"]}
    assert (root / "art.png").read_bytes() == _PNG_BYTES
