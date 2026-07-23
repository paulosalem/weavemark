"""Tutorial source, markup, command, and image fidelity checks."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shlex
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageStat

from weavemark.compilation.macros import preprocess_weavemark
from weavemark.compilation.structural import try_apply_structural_helpers
from weavemark.controller import WeaveMarkConfig, WeaveMarkController

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs"
TUTORIALS = sorted(DOCS.glob("tutorial*.html"))
PROMPLETS = ROOT / "promplets"

_PARAMETER_KEYS = {
    "allow_effects",
    "as",
    "contains",
    "count",
    "country",
    "detail_level",
    "done_when",
    "edit",
    "enforce",
    "file",
    "focus",
    "format",
    "from",
    "goal",
    "horizon",
    "language",
    "length",
    "max_iterations",
    "max_results",
    "max_tool_calls",
    "mingle",
    "mode",
    "model",
    "name",
    "purpose",
    "quality",
    "query",
    "references",
    "repeat",
    "rounds",
    "scheduler",
    "scope",
    "severity",
    "size",
    "starting_point",
    "story_format",
    "strict",
    "symbol",
    "template",
    "time_range",
    "type",
    "version",
}
_DIRECTIVE_BODY_KEYS = {
    "allow_effects",
    "count",
    "edit",
    "file",
    "max_iterations",
    "max_tool_calls",
    "model",
    "quality",
    "repeat",
    "references",
    "rounds",
    "scheduler",
    "size",
    "story_format",
}


class _CodeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._stack: list[tuple[str, frozenset[str]]] = []
        self._block: list[tuple[str, frozenset[str]]] | None = None
        self.blocks: list[list[tuple[str, frozenset[str]]]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        classes = frozenset(dict(attrs).get("class", "").split())
        self._stack.append((tag, classes))
        if tag == "code" and any(item[0] == "pre" for item in self._stack[:-1]):
            self._block = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "code" and self._block is not None:
            self.blocks.append(self._block)
            self._block = None
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index][0] == tag:
                del self._stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self._block is None:
            return
        classes = frozenset().union(*(item[1] for item in self._stack))
        self._block.extend((character, classes) for character in data)


def _parsed_blocks(path: Path) -> list[list[tuple[str, frozenset[str]]]]:
    parser = _CodeParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.blocks


def _block_text(block: list[tuple[str, frozenset[str]]]) -> str:
    return "".join(character for character, _classes in block)


def _tutorial(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


def _find_block(name: str, needle: str) -> str:
    matches = [
        _block_text(block)
        for block in _parsed_blocks(DOCS / name)
        if needle in _block_text(block)
    ]
    assert len(matches) == 1, (name, needle, len(matches))
    return matches[0]


def _normalized_lines(source: str) -> list[str]:
    lines: list[str] = []
    for raw_line in source.splitlines():
        line = re.sub(r"\s+", " ", raw_line.strip())
        if not line or line.startswith("<!--"):
            continue
        lines.append(line)
    return lines


def _assert_line_subsequence(snippet: str, source: str) -> None:
    source_lines = _normalized_lines(source)
    cursor = 0
    for line in _normalized_lines(snippet):
        try:
            cursor = source_lines.index(line, cursor) + 1
        except ValueError as exc:
            raise AssertionError(f"Untraced tutorial line: {line!r}") from exc


def _read_promplet(relative: str) -> str:
    return (PROMPLETS / relative).read_text(encoding="utf-8")


def test_docs_have_no_legacy_execute_mode_even_across_markup() -> None:
    for path in DOCS.rglob("*"):
        if path.suffix.lower() not in {".html", ".md", ".ebnf"}:
            continue
        source = path.read_text(encoding="utf-8")
        flattened = html.unescape(
            re.sub(r"<[^>]+>", "", source.replace("<!--", "").replace("-->", ""))
        )
        assert not re.search(r"@execute\s*weave\b", flattened, re.IGNORECASE), path


def test_every_tutorial_promplet_filename_has_a_checked_in_source() -> None:
    known_names = {path.name for path in PROMPLETS.rglob("*.weavemark.md")}
    for path in TUTORIALS:
        names = set(
            re.findall(r"[A-Za-z0-9_.-]+\.weavemark\.md", path.read_text())
        )
        assert names <= known_names, (path, sorted(names - known_names))


def test_saved_tutorial_snippets_trace_to_their_canonical_promplets() -> None:
    for path in TUTORIALS:
        for block in (_block_text(item) for item in _parsed_blocks(path)):
            first_line = block.splitlines()[0] if block.splitlines() else ""
            match = re.search(
                r"Save as [^>]*?([A-Za-z0-9_.-]+\.weavemark\.md)", first_line
            )
            if match is None:
                continue
            candidates = list(PROMPLETS.rglob(match.group(1)))
            assert len(candidates) == 1, (path, match.group(1), candidates)
            snippet = "\n".join(block.splitlines()[1:])
            _assert_line_subsequence(
                snippet, candidates[0].read_text(encoding="utf-8")
            )


def test_investment_tutorial_stages_reduce_the_canonical_source() -> None:
    source = _read_promplet("catalog/standalone/investment-brief.weavemark.md")
    blocks = [
        _block_text(block)
        for block in _parsed_blocks(DOCS / "tutorial.html")
        if re.search(r"(?m)^\s*@(?:promplet|refine|match)\b", _block_text(block))
    ]
    assert len(blocks) == 4
    for block in blocks:
        _assert_line_subsequence(block, source)
    assert "@style" not in "\n".join(blocks)
    assert "investment_decision" not in "\n".join(blocks)
    assert "@assert contains:" in blocks[0]


def test_advanced_tutorial_snippets_are_canonical() -> None:
    cases = (
        (
            "@module weavemark.std.planning.goals",
            "stdlib/definitions/planning/goals.weavemark.md",
        ),
        (
            "# Financial Independence Goal-to-Plan Prompt",
            "catalog/standalone/financial-independence-goal-plan-prompt.weavemark.md",
        ),
        (
            "@define lookup_public_goal_assumptions",
            "stdlib/definitions/planning/goals.weavemark.md",
        ),
        (
            "# Executable Financial Independence Goal Planner",
            "catalog/executable/financial-independence-goal-plan.weavemark.md",
        ),
        (
            "# Language-learning plan",
            "tutorials/language-learning-goal-plan.weavemark.md",
        ),
    )
    for needle, source_path in cases:
        _assert_line_subsequence(
            _find_block("tutorial-advanced.html", needle),
            _read_promplet(source_path),
        )


def test_illustrated_tutorial_uses_dynamic_sources_and_package_module() -> None:
    tutorial = _tutorial("tutorial-illustrated.html")
    comic = _read_promplet("catalog/executable/comic-strip.weavemark.md")
    book = _read_promplet("catalog/executable/childrens-book.weavemark.md")

    _assert_line_subsequence(
        _find_block("tutorial-illustrated.html", "@execute reflection"), comic
    )
    _assert_line_subsequence(
        _find_block("tutorial-illustrated.html", "Supplied `panels` beat sheet"),
        comic,
    )
    _assert_line_subsequence(
        _find_block("tutorial-illustrated.html", "@execute chain"), book
    )
    _assert_line_subsequence(
        _find_block(
            "tutorial-illustrated.html",
            "module:weavemark.domains.creative.picture_book_html",
        ),
        book,
    )
    assert "@{panels.1." not in tutorial
    assert "@{pages.1." not in tutorial
    assert (
        "@package</span> <span class=\"syntax-key\">instructions:</span> "
        "module:weavemark.domains.creative.picture_book_html"
    ) in tutorial
    package_source = _read_promplet(
        "domains/creative/fragments/picture-book-html.weavemark.md"
    )
    assert "@module weavemark.domains.creative.picture_book_html" in package_source


def test_mingle_tutorial_states_the_real_default_and_preservation_mode() -> None:
    tutorial = html.unescape(re.sub(r"<[^>]+>", "", _tutorial("tutorial-reuse.html")))
    collapsed = " ".join(tutorial.split()).lower()

    assert "mingle: true is the default" in collapsed
    assert "explicit mingle: false" in collapsed
    assert "preservation-oriented structural merge" in collapsed
    assert "plain @refine layers" not in collapsed
    assert "start without mingle" not in collapsed


def test_advanced_tutorial_uses_exact_example_output_paths() -> None:
    tutorial = _tutorial("tutorial-advanced.html")
    prefix = (
        "examples/python-runtime-integrations/"
        "financial-independence-goal-plan/outputs/"
    )
    for filename in (
        "compiled-prompt.md",
        "compiled-plan.json",
        "public-assumptions.json",
        "execution-output.md",
        "execution-trace.md",
    ):
        assert prefix + filename in tutorial
        assert f"<code>outputs/{filename}</code>" not in tutorial


def test_advanced_tutorial_treats_execution_output_as_completed_plan() -> None:
    tutorial = _tutorial("tutorial-advanced.html")
    use_output = tutorial[tutorial.index('id="use-output"') :]

    assert "open and review" in use_output
    assert "as the completed financial-independence plan" in use_output
    assert "paste" not in use_output


def test_functional_docs_describe_the_built_in_execution_runtime() -> None:
    usage = (DOCS / "usage-reference.md").read_text(encoding="utf-8")
    reference = (DOCS / "reference.html").read_text(encoding="utf-8")
    advanced = _tutorial("tutorial-advanced.html")
    combined = " ".join((usage + reference + advanced).split()).lower()

    assert "functionalengine" in combined
    assert "authorized python" in combined
    assert "composition alone never runs the companion" in combined
    assert "host runtimes are responsible for actually running" not in combined
    assert "@execute</span> functional" in advanced


def test_advanced_tutorial_explains_effect_access_modes() -> None:
    tutorial = _tutorial("tutorial-advanced.html")
    collapsed = " ".join(html.unescape(re.sub(r"<[^>]+>", "", tutorial)).split())

    assert "web_search names the host capability" in collapsed
    assert "read says this function retrieves information" in collapsed
    assert "other mode is write" in collapsed
    assert "omitting the mode defaults to read" in collapsed
    assert 'href="reference.html#macros"' in tutorial


def test_market_report_command_is_the_default_runner_transcript() -> None:
    runner = (
        ROOT / "examples/saved-artifact-workflows/market-snapshot/run.sh"
    ).read_text(encoding="utf-8")
    lines = runner.splitlines()
    start = next(
        index
        for index, line in enumerate(lines)
        if line.startswith(
            "weavemark promplets/catalog/executable/market-snapshot.weavemark.md"
        )
    )
    command_lines = [lines[start]]
    for line in lines[start + 1 :]:
        command_lines.append(line)
        if not line.rstrip().endswith("\\"):
            break
    command = "\n".join(command_lines)
    default_vars = re.search(r'^VARS_FILE="([^"]+)"', runner, re.MULTILINE)
    assert default_vars is not None
    output_dir_match = re.search(r'^OUTPUT_DIR="([^"]+)"', runner, re.MULTILINE)
    assert output_dir_match is not None
    output_dir = output_dir_match.group(1)
    command = command.replace("$VARS_FILE", default_vars.group(1))
    command = command.replace("$OUTPUT_DIR", output_dir)

    displayed = _find_block(
        "tutorial-executable.html",
        "weavemark promplets/catalog/executable/market-snapshot.weavemark.md",
    )

    def normalize(value: str) -> list[str]:
        return shlex.split(value.replace("\\\n", " "))

    assert normalize(displayed) == normalize(command)


def test_market_report_tutorial_uses_real_workflow_sources() -> None:
    market = _read_promplet("catalog/executable/market-snapshot.weavemark.md")
    definitions = _read_promplet("domains/finance/definitions/market-research.weavemark.md")
    package = _read_promplet(
        "stdlib/fragments/presentation/information-dashboard-html.weavemark.md"
    )

    _assert_line_subsequence(
        _find_block("tutorial-executable.html", "@define fetch_asset_snapshot"),
        definitions,
    )
    _assert_line_subsequence(
        _find_block("tutorial-executable.html", "@bind finance_data"),
        definitions,
    )
    _assert_line_subsequence(
        _find_block("tutorial-executable.html", "@execute functional"),
        market,
    )
    _assert_line_subsequence(
        _find_block("tutorial-executable.html", "@fetch_asset_snapshot"),
        market,
    )
    _assert_line_subsequence(
        _find_block("tutorial-executable.html", "@package instructions:"),
        market,
    )
    _assert_line_subsequence(
        _find_block("tutorial-executable.html", "<source-report>"),
        package,
    )


def test_implementation_tutorial_uses_real_ai_kanban_sources() -> None:
    source = _read_promplet("catalog/standalone/ai-kanban-board.weavemark.md")
    tutorial = _tutorial("tutorial-implement.html")

    _assert_line_subsequence(
        _find_block("tutorial-implement.html", "@promplet version: 0.7"),
        source,
    )
    assert "outputs/implementations/ai-kanban-browser/compiled-spec.md" in tutorial
    assert "outputs/implementations/ai-kanban-browser/" in tutorial
    assert (
        'href="../outputs/implementations/ai-kanban-browser/index.html" '
        'data-live-demo="ai-kanban"'
    ) in tutorial
    assert '<script src="local-demo-links.js"></script>' in tutorial
    assert 'id="kanban-flow-title"' in tutorial


def test_tutorial_images_are_deterministic_source_previews() -> None:
    pairs = (
        (
            ROOT
            / "examples/saved-artifact-workflows/comic-strip-en/outputs/"
            "comic-strip.png",
            DOCS / "tutorial-comic.jpg",
            (1280, 853),
            "4ae4ce37deda7c4c83855d07ff555fee6f20387f656cf1309e2b3ab39857a549",
            "e72d4e492e60e0dcdbc36e5db5ee06a66a90a31c7011f4ef2b8f122f7b308021",
        ),
        (
            ROOT
            / "examples/saved-artifact-workflows/childrens-book-orion-en/"
            "outputs/pages/page-9.png",
            DOCS / "tutorial-storybook-page.jpg",
            (1100, 733),
            "a3395bca5011107e7e1764257ec99a144e67b33dbc3a35b364de0a9ec242becd",
            "6aa917a1c0c37835c7fd2fac5e30b6c1fb70538e0f4d657cac52c739dd8afcc1",
        ),
    )
    for source_path, preview_path, size, source_hash, preview_hash in pairs:
        source_bytes = source_path.read_bytes()
        assert hashlib.sha256(preview_path.read_bytes()).hexdigest() == preview_hash
        with Image.open(preview_path) as preview_image:
            actual = preview_image.convert("RGB")
        assert actual.size == size
        if source_bytes.startswith(b"version https://git-lfs.github.com/spec/v1"):
            assert f"oid sha256:{source_hash}".encode() in source_bytes
        else:
            assert hashlib.sha256(source_bytes).hexdigest() == source_hash
            with Image.open(source_path) as source_image:
                expected = source_image.convert("RGB").resize(
                    size, Image.Resampling.LANCZOS
                )
            rms = ImageStat.Stat(ImageChops.difference(expected, actual)).rms
            normalized_rms = (
                (sum(value**2 for value in rms) / len(rms)) ** 0.5 / 255
            )
            assert normalized_rms < 0.03

    illustrated = _tutorial("tutorial-illustrated.html")
    assert 'src="tutorial-character-sheet.jpg"' in illustrated
    assert "outputs/pages/page-9.png" in illustrated
    assert "outputs/comic-strip.png" in illustrated


def test_all_tutorial_weavemark_tokens_have_syntax_spans() -> None:
    for path in TUTORIALS:
        assert "includes:" not in path.read_text(encoding="utf-8")
        for block in _parsed_blocks(path):
            text = _block_text(block)
            has_weavemark = bool(
                re.search(r"(?<![\w@])@[A-Za-z_][\w-]*|@\{[^}\n]+}", text)
            )
            if not has_weavemark:
                continue
            token_specs = (
                (r"@\{[^}\n]+}", "syntax-var"),
                (r"(?<![\w@])@[A-Za-z_][\w-]*", "syntax-directive"),
            )
            for pattern, expected_class in token_specs:
                for match in re.finditer(pattern, text):
                    classes = [
                        block[index][1]
                        for index in range(match.start(), match.end())
                    ]
                    if any("syntax-comment" in item for item in classes):
                        continue
                    assert all(expected_class in item for item in classes), (
                        path,
                        match.group(),
                        expected_class,
                    )

            for match in re.finditer(r'"(?:\\.|[^"\n])*"', text):
                classes = [
                    block[index][1] for index in range(match.start(), match.end())
                ]
                if any("syntax-comment" in item for item in classes):
                    continue
                assert all("syntax-string" in item for item in classes), (
                    path,
                    match.group(),
                )

            for match in re.finditer(r"\b([A-Za-z_][\w-]*):", text):
                key = match.group(1)
                if key not in _PARAMETER_KEYS:
                    continue
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.end())
                if line_end < 0:
                    line_end = len(text)
                line = text[line_start:line_end]
                is_directive_header = bool(
                    re.search(r"(?<![\w@])@[A-Za-z_][\w-]*", line)
                )
                is_tool_parameter = bool(
                    re.match(rf"\s*-\s*{re.escape(key)}:", line)
                )
                if (
                    not is_directive_header
                    and key not in _DIRECTIVE_BODY_KEYS
                    and not is_tool_parameter
                ):
                    continue
                classes = [
                    block[index][1] for index in range(match.start(), match.end())
                ]
                if any("syntax-comment" in item for item in classes):
                    continue
                assert all("syntax-key" in item for item in classes), (
                    path,
                    match.group(),
                )


def test_canonical_tutorial_promplets_scan() -> None:
    paths = sorted((PROMPLETS / "tutorials").glob("*.weavemark.md"))
    assert paths
    for path in paths:
        completed = subprocess.run(
            [sys.executable, "-m", "weavemark.app", str(path), "--scan"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, (path, completed.stdout, completed.stderr)
        payload = json.loads(completed.stdout)
        assert isinstance(payload, dict)
        assert "inputs" in payload


def test_language_learning_tutorial_promplet_compiles_offline() -> None:
    path = PROMPLETS / "tutorials/language-learning-goal-plan.weavemark.md"
    preprocessed = preprocess_weavemark(
        path.read_text(encoding="utf-8"),
        path.parent,
    )
    assert preprocessed.errors == []

    def read_file(reference: str, directory: Path) -> tuple[str, Path]:
        resolved = (directory / reference).resolve()
        return resolved.read_text(encoding="utf-8"), resolved

    result = try_apply_structural_helpers(
        preprocessed.text,
        {},
        path.parent,
        read_file,
        preprocessed.semantic_definitions,
    )
    assert result is not None
    assert result.errors == []
    assert result.composed_prompt
    assert "@goal_plan" not in result.composed_prompt


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Live tutorial compilation requires OPENAI_API_KEY.",
)
async def test_all_canonical_tutorial_promplets_compile_live() -> None:
    variables = {
        "adaptive-tutor-guided.weavemark.md": {
            "topic": "gradient descent",
            "learner_context": "a designer learning machine-learning basics",
            "learner_level": "beginner",
            "include_practice": True,
        },
        "adaptive-tutor.weavemark.md": {
            "topic": "Bayes' rule",
            "learner_context": "a product manager who knows basic percentages",
            "learning_goal": "update a belief after new evidence",
            "learner_level": "beginner",
            "include_practice": True,
        },
        "language-learning-goal-plan.weavemark.md": {},
        "metro-lines-pack.weavemark.md": {
            "game_fantasy": "A living city shaped by transit routes",
            "target_device": "desktop browser",
            "visual_mood": "clean transit maps and readable swarms",
            "session_length": "short",
            "include_touch_controls": False,
            "include_accessibility": True,
        },
        "metro-lines.weavemark.md": {
            "game_fantasy": "A living city shaped by transit routes",
            "target_device": "desktop browser",
            "visual_mood": "clean transit maps and readable swarms",
            "session_length": "short",
            "include_touch_controls": False,
            "include_accessibility": True,
        },
        "release-workbench-pack.weavemark.md": {
            "product_name": "LaunchDesk",
            "primary_users": "release managers and support leads",
            "release_risk": "shipping with unresolved validation gaps",
            "release_stage": "public",
            "include_ai_review": True,
            "include_audit_trail": True,
        },
        "release-workbench.weavemark.md": {
            "product_name": "LaunchDesk",
            "primary_users": "release managers and support leads",
            "release_risk": "shipping with unresolved validation gaps",
            "release_stage": "public",
            "include_ai_review": True,
            "include_audit_trail": True,
        },
    }

    async def answer_clarification(_prompt: object) -> str:
        return "Explain gradient descent and choose a safe learning rate."

    controller = WeaveMarkController(WeaveMarkConfig())
    for name, values in variables.items():
        path = PROMPLETS / "tutorials" / name
        result = await controller.compose(
            path.read_text(encoding="utf-8"),
            variables=values,
            base_dir=path.parent,
            source_path=path,
            ask_handler=answer_clarification,
        )
        assert result.errors == [], (path, result.errors)
        assert result.composed_prompt or result.emits, path
