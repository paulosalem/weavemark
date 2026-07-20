"""Comprehensive directive-level tests for the WeaveMark.

These tests treat the WeaveMark as a programming
language and test each construct in isolation, with parameter variants,
edge cases, and composition interactions.

Every test uses REAL LLM calls (no mocks). Requires OPENAI_API_KEY.

Test organization mirrors the core WeaveMark directive categories:
  1. Variable substitution (@{var})
  2. Control flow (@if/@else, @match)
  3. File inclusion (@refine)
  4. Assertions (@assert)
  5. Debug queries (@directives?, @vars?, @structure?)
  6. Meta-comments (@note)
  7. Escaping (@@)
  8. Nesting & composition order
"""

import os
from pathlib import Path

import pytest

from weavemark.protection import ProtectionError

_skip = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — requires a real LLM",
)

SPECS_DIR = Path(__file__).resolve().parents[1] / "specs"


def _controller():
    """Create a fresh controller for each test."""
    from weavemark.controller import (
        WeaveMarkConfig,
        WeaveMarkController,
    )
    return WeaveMarkController(WeaveMarkConfig())


async def _compose(spec: str, variables: dict | None = None, **kwargs):
    """Shorthand: compose a spec and return the result."""
    c = _controller()
    return await c.compose(spec, variables=variables or {}, **kwargs)


# ═══════════════════════════════════════════════════════════════════
# 1. Variable Substitution
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestVariableSubstitution:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_weavemark_variable(self):
        """@{var} is replaced with its value."""
        r = await _compose(
            "Hello @{name}, welcome to @{place}.",
            {"name": "Alice", "place": "Wonderland"},
        )
        assert "Alice" in r.composed_prompt
        assert "Wonderland" in r.composed_prompt
        assert "@{name}" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_bare_at_variable_is_literal(self):
        """Bare @var text is not WeaveMark variable syntax."""
        r = await _compose(
            "Dear @name, your order @order_id is ready.",
            {"name": "Bob", "order_id": "ORD-42"},
        )
        assert "@name" in r.composed_prompt
        assert "@order_id" in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_inline_braced_variable(self):
        """@{var} syntax handles adjacent text."""
        r = await _compose("File: report_@{version}_final.pdf", {"version": "v3"})
        assert "report_v3_final.pdf" in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_missing_variable_warns(self):
        """Referencing an undefined variable emits a warning."""
        r = await _compose("Hello @{undefined_var}.", {})
        # Should warn about the missing variable
        assert (
            len(r.warnings) > 0
            or "undefined" in r.composed_prompt.lower()
            or "@{undefined_var}" in r.composed_prompt
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_occurrences_replaced(self):
        """Same variable used multiple times is replaced everywhere."""
        r = await _compose("@{x} plus @{x} equals two @{x}s.", {"x": "apple"})
        assert r.composed_prompt.lower().count("apple") >= 2
        assert "@{x}" not in r.composed_prompt


# ═══════════════════════════════════════════════════════════════════
# 2. Control Flow — @if / @else
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestIfElse:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_true_includes_block(self):
        r = await _compose(
            "Base text.\n\n@if show_extra\n  Extra content here.\n",
            {"show_extra": True},
        )
        assert "Extra content" in r.composed_prompt
        assert "@if" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_false_excludes_block(self):
        r = await _compose(
            "Base text.\n\n@if show_extra\n  Extra content here.\n",
            {"show_extra": False},
        )
        assert "Extra content" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_else_true_branch(self):
        """When condition is true, @if block included, @else excluded."""
        spec = (
            "Start.\n\n"
            "@if premium\n"
            "  Welcome, premium member!\n"
            "@else\n"
            "  Please upgrade.\n"
        )
        r = await _compose(spec, {"premium": True})
        assert "premium member" in r.composed_prompt.lower()
        assert "upgrade" not in r.composed_prompt.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_else_false_branch(self):
        """When condition is false, @else block included."""
        spec = (
            "Start.\n\n"
            "@if premium\n"
            "  Welcome, premium member!\n"
            "@else\n"
            "  Please upgrade.\n"
        )
        r = await _compose(spec, {"premium": False})
        assert "upgrade" in r.composed_prompt.lower()
        assert "premium member" not in r.composed_prompt.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_missing_variable_warns(self):
        """Missing condition variable should warn and treat as false."""
        spec = "Base.\n\n@if nonexistent_flag\n  Hidden.\n"
        r = await _compose(spec, {})
        # Should warn about missing variable
        assert len(r.warnings) > 0 or "Hidden" not in r.composed_prompt


# ═══════════════════════════════════════════════════════════════════
# 3. Control Flow — @match
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestMatch:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_selects_correct_branch(self):
        spec = (
            "@match color\n"
            '  "red" ==> You chose red.\n'
            '  "blue" ==> You chose blue.\n'
            '  "green" ==> You chose green.\n'
        )
        r = await _compose(spec, {"color": "blue"})
        assert "blue" in r.composed_prompt.lower()
        assert "red" not in r.composed_prompt.lower()
        assert "green" not in r.composed_prompt.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_wildcard_default(self):
        """_ wildcard matches when no other case does."""
        spec = (
            "@match tier\n"
            '  "enterprise" ==> Enterprise features.\n'
            "  _ ==> Standard features.\n"
        )
        r = await _compose(spec, {"tier": "free"})
        assert "standard" in r.composed_prompt.lower()
        assert "enterprise" not in r.composed_prompt.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_no_match_no_wildcard_warns(self):
        """No matching case and no wildcard: warn and remove block."""
        spec = (
            "Intro.\n\n"
            "@match size\n"
            '  "small" ==> Small.\n'
            '  "large" ==> Large.\n'
        )
        r = await _compose(spec, {"size": "medium"})
        assert "Small" not in r.composed_prompt
        assert "Large" not in r.composed_prompt
        assert len(r.warnings) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_multiline_block(self):
        """Multi-line block effect after ==>."""
        spec = (
            "@match mode\n"
            '  "detailed" ==>\n'
            "    Paragraph one of detailed mode.\n"
            "    Paragraph two of detailed mode.\n"
            '  "brief" ==> One liner.\n'
        )
        r = await _compose(spec, {"mode": "detailed"})
        assert "paragraph one" in r.composed_prompt.lower()
        assert "paragraph two" in r.composed_prompt.lower()


# ═══════════════════════════════════════════════════════════════════
# 4. File Inclusion — @refine
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestRefine:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_refine_merges_file_content(self):
        """@refine pulls in file and merges content."""
        spec = (
            "@refine ./library/reasoning/base-analyst.weavemark.md\n\n"
            "Analyze the housing market."
        )
        r = await _compose(spec, {}, base_dir=SPECS_DIR)
        # library/reasoning/base-analyst.weavemark.md content should be integrated
        p = r.composed_prompt.lower()
        assert "analytical" in p or "evidence" in p or "rigorous" in p
        assert "housing" in p
        assert "@refine" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_refine_mingle_false(self):
        """@refine mingle: false does minimal merge (preserves wording)."""
        spec = (
            "@refine ./library/reasoning/base-analyst.weavemark.md mingle: false\n\n"
            "Analyze the housing market."
        )
        r = await _compose(spec, {}, base_dir=SPECS_DIR)
        p = r.composed_prompt.lower()
        assert "housing" in p
        assert "@refine" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_refine_missing_file_errors(self):
        """Referencing a nonexistent file should emit an error."""
        spec = "@refine ./nonexistent_file_xyz.md\n\n" "Some text."
        r = await _compose(spec, {}, base_dir=SPECS_DIR)
        assert len(r.errors) > 0 or len(r.warnings) > 0


class TestRefineBinding:
    """@refine `with <name>: <value>` bindings resolve deterministically.

    These are structural (no LLM): a bound refine composes the child with the
    parent variables overlaid by the bindings, selecting branches at compile time.
    """

    @staticmethod
    def _write_core(tmp_path: Path) -> None:
        (tmp_path / "core.weavemark.md").write_text(
            "@match kind\n"
            '  "a" ==>\n'
            "    Branch A for @{shared}.\n"
            '  "b" ==>\n'
            "    Branch B for @{shared}.\n",
            encoding="utf-8",
        )

    @pytest.mark.asyncio
    async def test_binding_selects_branch_without_llm(self, tmp_path: Path):
        self._write_core(tmp_path)
        spec = '@refine ./core.weavemark.md\n  with kind: "b"\n'
        r = await _compose(spec, {"shared": "HELLO"}, base_dir=tmp_path)
        assert r.errors == []
        assert r.composed_prompt == "Branch B for HELLO."
        assert "@refine" not in r.composed_prompt

    @pytest.mark.asyncio
    async def test_binding_forwards_parent_variable(self, tmp_path: Path):
        (tmp_path / "core.weavemark.md").write_text(
            "@if fancy\n  FANCY for @{who}.\n@if plain\n  PLAIN for @{who}.\n",
            encoding="utf-8",
        )
        spec = "@refine ./core.weavemark.md\n  with fancy: @{use_fancy}\n"
        r = await _compose(spec, {"use_fancy": True, "who": "Orion"}, base_dir=tmp_path)
        assert r.errors == []
        assert r.composed_prompt == "FANCY for Orion."

    @pytest.mark.asyncio
    async def test_binding_overrides_runtime_variable(self, tmp_path: Path):
        self._write_core(tmp_path)
        spec = '@refine ./core.weavemark.md\n  with kind: "a"\n'
        # runtime says "b", but the in-spec binding pins "a".
        r = await _compose(spec, {"kind": "b", "shared": "X"}, base_dir=tmp_path)
        assert r.errors == []
        assert r.composed_prompt == "Branch A for X."

    @pytest.mark.asyncio
    async def test_unbound_variable_still_flows_from_runtime(self, tmp_path: Path):
        self._write_core(tmp_path)
        # bind the branch, leave @{shared} free -> supplied by runtime.
        spec = '@refine ./core.weavemark.md\n  with kind: "b"\n'
        r = await _compose(spec, {"shared": "RUNTIME"}, base_dir=tmp_path)
        assert r.errors == []
        assert r.composed_prompt == "Branch B for RUNTIME."


#
# 5.  @assertAssertions
#


@_skip
class TestAssert:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_assert_passes_silently(self):
        """@assert with satisfied condition is removed without error."""
        spec = (
            "## Output Format\nReturn JSON.\n\n"
            "Analyze sentiment.\n\n"
            '@assert section: "Output Format" severity: error\n'
        )
        r = await _compose(spec, {})
        assert "@assert" not in r.composed_prompt
        assert len(r.errors) == 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_assert_fails_with_error(self):
        """@assert with unsatisfied condition emits an error."""
        spec = (
            "Analyze sentiment.\n\n"
            '@assert section: "Output Format" severity: error\n'
        )
        r = await _compose(spec, {})
        # Should emit an error since there's no Output Format section
        assert len(r.errors) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_assert_warning_severity(self):
        """@assert severity: warning emits warning instead of error."""
        spec = (
            "Analyze sentiment.\n\n"
            '@assert contains: "max response length" severity: warning\n'
        )
        r = await _compose(spec, {})
        # Should emit a warning, not an error
        assert len(r.warnings) > 0 or len(r.suggestions) > 0


# ═══════════════════════════════════════════════════════════════════
# 10. Debug Queries — @directives?, @vars?, @structure?
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestDebugQueries:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_directives_query(self):
        """@directives? lists directives without appearing in output."""
        spec = (
            "@if show\n"
            "  Content.\n\n"
            "@match x\n"
            '  "a" ==> A.\n\n'
            "@directives?\n"
        )
        r = await _compose(spec, {"show": True, "x": "a"})
        assert "@directives?" not in r.composed_prompt
        # Should have analysis or suggestion listing the directives
        all_issues = " ".join(r.suggestions + r.warnings).lower()
        analysis = (r.analysis or "").lower()
        has_directive_info = (
            "@if" in all_issues
            or "@match" in all_issues
            or "@if" in analysis
            or "@match" in analysis
        )
        assert has_directive_info

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_vars_query(self):
        """@vars? lists referenced variables."""
        spec = "Hello @{name}, you are @{role}.\n\n" "@vars?\n"
        r = await _compose(spec, {"name": "Alice"})
        assert "@vars?" not in r.composed_prompt
        # Should mention the variables (especially the missing one)
        all_text = " ".join(r.suggestions + r.warnings).lower()
        analysis = (r.analysis or "").lower()
        has_var_info = "role" in all_text or "role" in analysis
        assert has_var_info

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_structure_query(self):
        """@structure? describes prompt structure."""
        spec = (
            "# Title\nIntro.\n\n"
            "## Section A\nContent A.\n\n"
            "## Section B\nContent B.\n\n"
            "@structure?\n"
        )
        r = await _compose(spec, {})
        assert "@structure?" not in r.composed_prompt
        all_text = " ".join(r.suggestions + r.warnings).lower()
        analysis = (r.analysis or "").lower()
        has_struct_info = (
            "section" in all_text
            or "heading" in all_text
            or "section" in analysis
            or "heading" in analysis
        )
        assert has_struct_info


# ═══════════════════════════════════════════════════════════════════
# 11. Meta-Comments & Escaping
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestNoteAndEscaping:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_note_stripped(self):
        """@note blocks are removed from final output."""
        spec = (
            "@note\n"
            "  Internal: this fixes bug #1234.\n"
            "  Do not remove the next instruction.\n\n"
            "Always validate user input.\n"
        )
        r = await _compose(spec, {})
        assert "bug #1234" not in r.composed_prompt
        assert "internal" not in r.composed_prompt.lower()
        assert "validate" in r.composed_prompt.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_double_at_escaping(self):
        """@@ renders as literal @ in the output."""
        spec = (
            "Use Python decorators: @@property, @@staticmethod.\n"
            "Contact: admin@@example.com\n"
        )
        r = await _compose(spec, {})
        assert "@property" in r.composed_prompt
        assert "@staticmethod" in r.composed_prompt
        assert "admin@example.com" in r.composed_prompt
        assert "@@" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_escaped_directive_not_executed(self):
        """@@if should render as @if text, not execute as directive."""
        spec = "The syntax is @@if condition for conditional blocks.\n"
        r = await _compose(spec, {})
        assert "@if" in r.composed_prompt
        assert "@@if" not in r.composed_prompt


# ═══════════════════════════════════════════════════════════════════
# 12. Nesting, Composition Order, and Interactions
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestNestingAndComposition:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_inside_match(self):
        """@if nested inside a @match branch."""
        spec = (
            "@match role\n"
            '  "engineer" ==>\n'
            "    You are a software engineer.\n"
            "    @if senior\n"
            "      Focus on architecture and mentoring.\n"
            '  "designer" ==> You are a designer.\n'
        )
        r = await _compose(spec, {"role": "engineer", "senior": True})
        p = r.composed_prompt.lower()
        assert "software engineer" in p or "engineer" in p
        assert "architecture" in p or "mentoring" in p
        assert "@match" not in r.composed_prompt
        assert "@if" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_inside_if(self):
        """@match nested inside an @if block."""
        spec = (
            "Base prompt.\n\n"
            "@if customize\n"
            "  @match tone\n"
            '    "formal" ==> Use formal language.\n'
            '    "casual" ==> Use casual language.\n'
        )
        r = await _compose(spec, {"customize": True, "tone": "formal"})
        p = r.composed_prompt.lower()
        assert "formal" in p
        assert "casual" not in p

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_asserts_all_checked(self):
        """Multiple @assert directives are all evaluated."""
        spec = (
            "## Role\nYou are an analyst.\n\n"
            "## Output Format\nReturn JSON.\n\n"
            '@assert section: "Role" severity: error\n'
            '@assert section: "Output Format" severity: error\n'
            '@assert contains: "example outputs" severity: warning\n'
        )
        r = await _compose(spec, {})
        # First two asserts should pass
        assert len(r.errors) == 0
        # Third assert should warn (no examples)
        assert len(r.warnings) > 0 or len(r.suggestions) > 0


# ═══════════════════════════════════════════════════════════════════
# 13. Edge Cases and Error Handling
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestEdgeCases:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_empty_spec(self):
        """Empty spec produces empty or minimal output."""
        r = await _compose("", {})
        # Should not error out
        assert r is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_no_directives_passthrough(self):
        """Plain text with no directives passes through unchanged."""
        text = "Write a poem about the sea."
        r = await _compose(text, {})
        # Core content should be preserved
        assert "poem" in r.composed_prompt.lower()
        assert "sea" in r.composed_prompt.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_unknown_directive_warns(self):
        """An unrecognized @directive should produce a warning."""
        spec = "Some text.\n\n@frobnicate\n  Do something weird.\n"
        r = await _compose(spec, {})
        # Should warn about unrecognized directive
        has_warning = len(r.warnings) > 0 or len(r.suggestions) > 0
        assert has_warning

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_deeply_nested_three_levels(self):
        """Three levels of nesting resolve correctly."""
        spec = (
            "@if level1\n"
            "  Level 1 active.\n"
            "  @if level2\n"
            "    Level 2 active.\n"
            "    @if level3\n"
            "      Level 3 active.\n"
        )
        r = await _compose(
            spec,
            {
                "level1": True,
                "level2": True,
                "level3": True,
            },
        )
        p = r.composed_prompt.lower()
        assert "level 1" in p
        assert "level 2" in p
        assert "level 3" in p
        assert "@if" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_variable_inside_directive_block(self):
        """Variables inside directive-owned blocks are substituted."""
        spec = (
            "@match choice_var\n"
            '  "alpha" ==> You chose alpha.\n'
            '  "beta" ==> You chose @{choice_var}.\n'
        )
        r = await _compose(spec, {"choice_var": "beta"})
        p = r.composed_prompt.lower()
        assert "beta" in p

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_variable_renders_readably(self):
        """List values can be injected through WeaveMark variables."""
        spec = "Review these files:\n" "@{files}\n"
        r = await _compose(spec, {"files": ["app.py", "utils.py", "tests.py"]})
        p = r.composed_prompt.lower()
        assert "app.py" in p
        assert "utils.py" in p
        assert "tests.py" in p


# ═══════════════════════════════════════════════════════════════════
# 13. @embed — Verbatim Injection (unit tests for _read_file / conversion)
# ═══════════════════════════════════════════════════════════════════


class TestReadFileRichConversion:
    """Unit tests for _read_file rich-format detection and conversion.

    These do NOT require an LLM or API key.
    """

    def _read_file(self, file_name: str, base_dir: Path) -> str:
        from weavemark.controller import WeaveMarkController

        return WeaveMarkController._read_file(file_name, base_dir)

    def test_plain_text_file_reads_normally(self, tmp_path):
        """Plain .txt files are read as-is."""
        f = tmp_path / "hello.txt"
        f.write_text("Hello, world!")
        result = self._read_file("hello.txt", tmp_path)
        assert result == "Hello, world!"

    def test_markdown_file_reads_normally(self, tmp_path):
        """Plain .md files are read as-is (not treated as rich)."""
        f = tmp_path / "doc.md"
        f.write_text("# Title\nSome text.")
        result = self._read_file("doc.md", tmp_path)
        assert result == "# Title\nSome text."

    def test_missing_file_returns_error(self, tmp_path):
        result = self._read_file("nonexistent.txt", tmp_path)
        assert "Error" in result
        assert "not found" in result

    def test_directory_traversal_blocked(self, tmp_path):
        with pytest.raises(ProtectionError, match="outside the entrypoint"):
            self._read_file("../../etc/passwd", tmp_path)

    def test_parent_ref_within_project_root_reads_normally(self, tmp_path):
        project = tmp_path / "project"
        source_dir = project / "prompts" / "scenario"
        shared_file = project / "prompts" / "shared.weavemark.md"
        source_dir.mkdir(parents=True)
        (project / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        shared_file.write_text("Shared prompt content")

        result = self._read_file("../shared.weavemark.md", source_dir)

        assert result == "Shared prompt content"

    def test_pdf_extension_triggers_conversion(self, tmp_path):
        """A .pdf file triggers the rich format conversion path."""
        from weavemark.controller import WeaveMarkController

        # We test that _convert_rich_file is called by checking it goes through
        # the conversion code path (it won't error out with "not found")
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"not a real PDF")
        result = self._read_file("doc.pdf", tmp_path)
        # Should not return a "file not found" error
        assert "not found" not in result
        # Verify the extension is in the rich set
        assert ".pdf" in WeaveMarkController._RICH_EXTENSIONS

    def test_docx_extension_triggers_conversion(self, tmp_path):
        from weavemark.controller import WeaveMarkController

        f = tmp_path / "doc.docx"
        f.write_bytes(b"PK\x03\x04not-a-real-docx")
        result = self._read_file("doc.docx", tmp_path)
        assert "not found" not in result
        assert ".docx" in WeaveMarkController._RICH_EXTENSIONS

    def test_rich_extensions_recognised(self):
        """All expected extensions are in the rich set."""
        from weavemark.controller import WeaveMarkController

        for ext in [
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".xls",
            ".doc",
            ".ppt",
            ".html",
            ".htm",
        ]:
            assert ext in WeaveMarkController._RICH_EXTENSIONS, f"{ext} not recognised"

    def test_missing_markitdown_gives_clear_error(self, tmp_path, monkeypatch):
        """If markitdown is not installed, a helpful error is returned."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "markitdown":
                raise ImportError("No module named 'markitdown'")
            return real_import(name, *args, **kwargs)

        f = tmp_path / "doc.pdf"
        f.write_bytes(b"%PDF-1.4 fake")

        monkeypatch.setattr(builtins, "__import__", mock_import)
        try:
            from weavemark.controller import WeaveMarkController

            result = WeaveMarkController._convert_rich_file(f, "doc.pdf")
            assert "pip install weavemark[convert]" in result
        finally:
            monkeypatch.setattr(builtins, "__import__", real_import)


# ═══════════════════════════════════════════════════════════════════
# 14. @embed — Integration tests (require LLM)
# ═══════════════════════════════════════════════════════════════════


@_skip
class TestEmbedDirective:
    """Integration tests for the @embed directive via LLM composition."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_embed_inline_produces_fenced_block(self):
        """@embed with inline block wraps content in a fenced code block."""
        spec = (
            "Analyze this data:\n\n"
            "@embed\n"
            "  line one\n"
            "  line two\n"
            "  line three\n"
        )
        r = await _compose(spec, {})
        p = r.composed_prompt
        # Should contain fenced code block markers
        assert "```" in p
        # The original content should be present verbatim
        assert "line one" in p
        assert "line two" in p

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_embed_with_lang_parameter(self):
        """@embed lang: json produces a json-fenced block."""
        spec = "Here is the config:\n\n" "@embed lang: json\n" '  {"key": "value"}\n'
        r = await _compose(spec, {})
        p = r.composed_prompt
        assert "```json" in p or "``` json" in p
        assert '"key"' in p

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_embed_with_label(self):
        """@embed with label: produces a caption before the block."""
        spec = "Review this:\n\n" '@embed label: "Sample Output"\n' "  result: ok\n"
        r = await _compose(spec, {})
        p = r.composed_prompt
        assert "Sample Output" in p
        assert "```" in p

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_embed_does_not_process_variables(self):
        """Variables inside @embed should NOT be substituted."""
        spec = (
            "Template reference:\n\n"
            "@embed\n"
            "  Hello @{name}, welcome to @{place}.\n"
        )
        r = await _compose(spec, {"name": "Alice", "place": "Wonderland"})
        p = r.composed_prompt
        # The @{name} should remain as-is inside the embed
        assert "@{name}" in p
        assert "@{place}" in p

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_embed_file(self):
        """@embed file: loads and wraps a file's content."""
        spec = (
            "Here is the reference spec:\n\n"
            "@embed file: reasoning/chain-of-thought.weavemark.md lang: markdown\n"
        )
        r = await _compose(spec, {}, base_dir=SPECS_DIR)
        p = r.composed_prompt
        assert "```" in p
        # The file content should be present
        assert "chain" in p.lower() or "thought" in p.lower()
