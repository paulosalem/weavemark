"""Tests for the WeaveMark Markdown surface adapter and lowering pipeline."""

from __future__ import annotations

from weavemark.surfaces import (
    SurfaceLoweringResult,
    lower_weavemark_surface,
    parse_surface_pragma,
)
from weavemark.surfaces.markdown_adapter import MarkdownSurfaceAdapter

# ═══════════════════════════════════════════════════════════════════════
# parse_surface_pragma
# ═══════════════════════════════════════════════════════════════════════


class TestParseSurfacePragma:
    def test_returns_none_when_no_pragma(self):
        spec = "# Hello\n\n@prompt default\n  Do something.\n"
        assert parse_surface_pragma(spec) is None

    def test_returns_none_when_pragma_has_no_surface(self):
        spec = "@promplet version: 0.7\n\n@prompt default\n  Do something.\n"
        assert parse_surface_pragma(spec) is None

    def test_returns_surface_name_lowercase(self):
        spec = "@promplet version: 0.7 surface: markdown\n"
        assert parse_surface_pragma(spec) == "markdown"

    def test_canonical_surface_returned(self):
        spec = "@promplet version: 0.7 surface: canonical\n"
        assert parse_surface_pragma(spec) == "canonical"

    def test_ignores_leading_blank_lines(self):
        spec = "\n\n@promplet version: 0.7 surface: markdown\n"
        assert parse_surface_pragma(spec) == "markdown"

    def test_returns_none_when_non_pragma_first(self):
        spec = "# Heading\n@promplet version: 0.7 surface: markdown\n"
        assert parse_surface_pragma(spec) is None


# ═══════════════════════════════════════════════════════════════════════
# lower_weavemark_surface — canonical / no-op cases
# ═══════════════════════════════════════════════════════════════════════


class TestLowerPromptspecSurfaceCanonical:
    def test_no_pragma_returns_unchanged(self):
        spec = "@prompt default\n  Hello.\n"
        result = lower_weavemark_surface(spec)
        assert result.text == spec
        assert result.surface == "canonical"
        assert not result.errors

    def test_html_comments_are_stripped_before_surface_detection(self):
        spec = (
            "<!-- author note -->\n"
            "@promplet version: 0.8 surface: markdown\n\n"
            "# Prompt\n"
            "Hello.\n"
        )

        result = lower_weavemark_surface(spec)

        assert not result.errors
        assert result.surface == "markdown"
        assert "<!--" not in result.text
        assert "# Prompt" in result.text

    def test_unterminated_html_comment_is_an_error(self):
        result = lower_weavemark_surface("Hello.\n<!-- unfinished")

        assert result.errors == [
            "Unterminated HTML comment in WeaveMark source starting at line 2."
        ]

    def test_canonical_surface_returns_unchanged(self):
        spec = "@promplet version: 0.7 surface: canonical\n\n@prompt default\n  Hello.\n"
        result = lower_weavemark_surface(spec)
        assert result.text == spec
        assert result.surface == "canonical"
        assert not result.errors

    def test_unknown_surface_returns_error(self):
        spec = "@promplet version: 0.7 surface: html\n\n@prompt default\n  Hello.\n"
        result = lower_weavemark_surface(spec)
        assert result.errors
        assert "html" in result.errors[0]

    def test_result_type(self):
        spec = "@prompt default\n  Hello.\n"
        result = lower_weavemark_surface(spec)
        assert isinstance(result, SurfaceLoweringResult)


# ═══════════════════════════════════════════════════════════════════════
# MarkdownSurfaceAdapter — directive headings
# ═══════════════════════════════════════════════════════════════════════


class TestMarkdownDirectiveHeadings:
    def _lower(self, text: str) -> str:
        adapter = MarkdownSurfaceAdapter()
        result = adapter.lower(text)
        assert not result.errors, result.errors
        return result.text

    def test_simple_h2_directive(self):
        spec = "## @prompt extract\n\nExtract claims.\n"
        out = self._lower(spec)
        assert "@prompt extract" in out
        assert "Extract claims." in out
        # Should NOT have the ## prefix
        assert "## @prompt" not in out

    def test_h2_directive_with_params(self):
        spec = "## @prompt extract role: user\n\nExtract claims from @{passage}.\n"
        out = self._lower(spec)
        assert "@prompt extract role: user" in out
        assert "Extract claims from @{passage}." in out

    def test_body_is_indented(self):
        spec = "## @prompt default\n\nHello world.\n"
        out = self._lower(spec)
        lines = [l for l in out.splitlines() if "Hello world." in l]
        assert lines, "Body line not found"
        assert lines[0].startswith("  "), f"Expected indentation, got: {lines[0]!r}"

    def test_multiple_directive_headings(self):
        spec = (
            "## @prompt extract\n\nExtract claims.\n\n"
            "## @prompt critique\n\nCritique each claim.\n"
        )
        out = self._lower(spec)
        assert "@prompt extract" in out
        assert "@prompt critique" in out
        assert "Extract claims." in out
        assert "Critique each claim." in out

    def test_h1_directive(self):
        spec = "# @prompt main\n\nDo the thing.\n"
        out = self._lower(spec)
        assert "@prompt main" in out
        assert "## @prompt" not in out

    def test_heading_section_ends_at_same_level(self):
        spec = (
            "## @prompt first\n\nFirst body.\n\n"
            "## @prompt second\n\nSecond body.\n"
        )
        out = self._lower(spec)
        # First body should not contain second body
        idx_first = out.index("First body.")
        idx_second = out.index("Second body.")
        idx_second_dir = out.index("@prompt second")
        # second directive must come after first body
        assert idx_second_dir > idx_first
        assert idx_second > idx_second_dir

    def test_subheadings_preserved_in_body(self):
        spec = (
            "## @prompt document\n\n"
            "Intro text.\n\n"
            "### Subsection\n\n"
            "Sub content.\n\n"
            "## @prompt next\n\nNext body.\n"
        )
        out = self._lower(spec)
        assert "### Subsection" in out
        assert "Sub content." in out

    def test_non_directive_heading_preserved(self):
        spec = "## Regular Heading\n\nSome content.\n"
        out = self._lower(spec)
        assert "## Regular Heading" in out

    def test_pragma_line_preserved(self):
        spec = "@promplet version: 0.7 surface: markdown\n\n## @prompt default\n\nHello.\n"
        out = self._lower(spec)
        assert "@promplet version: 0.7 surface: markdown" in out


# ═══════════════════════════════════════════════════════════════════════
# MarkdownSurfaceAdapter — callouts
# ═══════════════════════════════════════════════════════════════════════


class TestMarkdownCallouts:
    def _lower(self, text: str) -> str:
        adapter = MarkdownSurfaceAdapter()
        result = adapter.lower(text)
        assert not result.errors, result.errors
        return result.text

    def test_simple_callout(self):
        spec = "> [!PROMPLET style]\n> Crisp and direct.\n"
        out = self._lower(spec)
        assert "@style" in out
        assert "Crisp and direct." in out
        # No blockquote marker in output
        assert "> [!PROMPLET" not in out

    def test_style_callout_body_becomes_positional_guidance(self):
        spec = "> [!PROMPLET style]\n> Crisp and direct.\n"
        out = self._lower(spec)
        assert out.strip() == '@style "Crisp and direct."'

    def test_callout_with_params(self):
        spec = "> [!PROMPLET output format: json]\n> JSON only.\n"
        out = self._lower(spec)
        assert "@output format: json" in out

    def test_callout_multiline_body(self):
        spec = "> [!PROMPLET style]\n> Line one.\n> Line two.\n"
        out = self._lower(spec)
        assert out.strip() == '@style "Line one. Line two."'

    def test_callout_with_blank_body_line(self):
        spec = "> [!PROMPLET note]\n> First.\n>\n> Second.\n"
        out = self._lower(spec)
        assert "First." in out
        assert "Second." in out

    def test_empty_callout_header_produces_error(self):
        spec = "> [!PROMPLET]\n> Body text.\n"
        adapter = MarkdownSurfaceAdapter()
        result = adapter.lower(spec)
        assert result.errors

    def test_ordinary_blockquote_preserved(self):
        spec = "> This is a regular quote.\n"
        out = self._lower(spec)
        assert "> This is a regular quote." in out


# ═══════════════════════════════════════════════════════════════════════
# Fenced code block preservation
# ═══════════════════════════════════════════════════════════════════════


class TestFencedBlockPreservation:
    def _lower(self, text: str) -> str:
        adapter = MarkdownSurfaceAdapter()
        result = adapter.lower(text)
        assert not result.errors, result.errors
        return result.text

    def test_directive_inside_fence_not_lowered(self):
        spec = (
            "```markdown\n"
            "## @prompt example\n"
            "\n"
            "This is example content.\n"
            "```\n"
        )
        out = self._lower(spec)
        assert "## @prompt example" in out

    def test_callout_inside_fence_not_lowered(self):
        spec = (
            "```\n"
            "> [!PROMPLET style]\n"
            "> Crisp.\n"
            "```\n"
        )
        out = self._lower(spec)
        assert "> [!PROMPLET style]" in out

    def test_directive_after_fence_is_lowered(self):
        spec = (
            "```\n"
            "some code\n"
            "```\n"
            "\n"
            "## @prompt after_fence\n"
            "\n"
            "Body after fence.\n"
        )
        out = self._lower(spec)
        assert "@prompt after_fence" in out
        assert "Body after fence." in out


# ═══════════════════════════════════════════════════════════════════════
# Full pipeline: lower_weavemark_surface with markdown surface
# ═══════════════════════════════════════════════════════════════════════


class TestFullPipelineMarkdown:
    def test_heading_lowered_by_pipeline(self):
        spec = (
            "@promplet version: 0.7 surface: markdown\n"
            "\n"
            "## @prompt extract\n"
            "\n"
            "Extract claims from the text.\n"
        )
        result = lower_weavemark_surface(spec)
        assert not result.errors
        assert result.surface == "markdown"
        assert "@prompt extract" in result.text
        assert "Extract claims" in result.text
        assert "## @prompt" not in result.text

    def test_callout_lowered_by_pipeline(self):
        spec = (
            "@promplet version: 0.7 surface: markdown\n"
            "\n"
            "> [!PROMPLET style]\n"
            "> Crisp and professional.\n"
        )
        result = lower_weavemark_surface(spec)
        assert not result.errors
        assert "@style" in result.text
        assert "Crisp and professional." in result.text

    def test_pragma_preserved_in_lowered_output(self):
        spec = (
            "@promplet version: 0.7 surface: markdown\n"
            "\n"
            "## @prompt default\n"
            "\n"
            "Hello.\n"
        )
        result = lower_weavemark_surface(spec)
        assert "@promplet version: 0.7 surface: markdown" in result.text

    def test_canonical_spec_unchanged_by_markdown_pipeline(self):
        """A spec without heading/callout sugar passes through unchanged (modulo whitespace normalization)."""
        spec = (
            "@promplet version: 0.7 surface: markdown\n"
            "\n"
            "@prompt default\n"
            "  Hello world.\n"
        )
        result = lower_weavemark_surface(spec)
        assert not result.errors
        assert "@prompt default" in result.text
        assert "Hello world." in result.text
