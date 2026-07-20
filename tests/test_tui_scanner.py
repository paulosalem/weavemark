"""Tests for weavemark.tui.scanner — spec metadata extraction."""

from pathlib import Path

import pytest

from weavemark.tui.scanner import SpecInput, SpecMetadata, scan_spec

# ═══════════════════════════════════════════════════════════════════
# Minimal spec fixtures
# ═══════════════════════════════════════════════════════════════════

SPEC_SIMPLE = """\
# My Spec

A simple spec for testing.

Hello @{name}, welcome to @{place}.
"""

SPEC_MULTILINE_VARS = """\
# Writer

Write about @{topic}.

Here is the @{description} of what we need.

The @{body} goes here.
"""

SPEC_MATCH = """\
# Matcher

@match language
  "python" ==> Use Python style.
  "typescript" ==> Use TypeScript style.
  "rust" ==> Use Rust style.
  _ ==> Use generic style.

Write @{topic} code.
"""

SPEC_IF = """\
# Conditional

@if include_tests
  Also generate unit tests.

@if verbose_output
  Include detailed explanations.

Analyze @{project_name}.
"""

SPEC_COMPILE = """\
# Compile Metadata

@compile format: .json

Build @{thing}.
"""

SPEC_EMBED_FILE_VAR = """\
# Embed Test

@embed file: @{input_file}

Process the text above.
"""

SPEC_EMBED_STATIC = """\
# Embed Static

@embed file: samples/data.txt

@embed file: docs/readme.md

Process both files.
"""

SPEC_EMIT = """\
# Emit Outputs

@emit file: prompts/system.md
System prompt content.

@emit file="prompts/user.md"
User prompt content.

@emit file: @{dynamic_output}
Dynamic output path.
"""

SPEC_MESSAGE = """\
# Message Outputs

@prompt intro role: system
System content.

@prompt request role: user
User content.

@prompt @{dynamic_name} role: assistant
Dynamic name should not become a static output path.
"""

SPEC_EXECUTE = """\
# Strategy Spec

@execute reflection
  max_iterations: 3
  temperature: 0.7

@prompt generate
Generate something about @{topic}.

@prompt critique
Critique the above.

@prompt revise
Revise based on critique.
"""

SPEC_TOOLS = """\
# Tool Spec

@tool web_search
@tool calculator

@if use_database
  @tool sql_query

Solve @{problem}.
"""

SPEC_ASSERT = """\
# Validated Spec

@assert contains: "citations" severity: error
@assert contains: "under 500 words" severity: warning

Write about @{topic}.
"""

SPEC_NOTE_NEAR_VAR = """\
# With Notes

@note
  The focus should describe what characteristics to look for.

What is the @{focus} of this analysis?

@note
  Choose a language from the supported list.

Code in @{language}.
"""

SPEC_REFINE = """\
# Refined Spec

@refine ./library/reasoning/base-analyst.weavemark.md

@refine @{custom_base}

Analyze @{topic}.
"""

SPEC_COLLABORATIVE = """\
# Collaborative Writer

@execute collaborative
  max_rounds: 5

@prompt generate
Write about @{topic} in @{tone} tone.

@prompt continue
The user edited the content.
Original: @{original_content}
Edited: @{edited_content}
Continue.
"""

SPEC_COMPLEX = """\
# Complex Spec

A real-world-like spec with many features.

@refine ./library/reasoning/base-analyst.weavemark.md

@execute reflection
  max_iterations: 2

@prompt generate
@prompt critique
@prompt revise

@tool web_search

@match output_format
  "json" ==> Produce JSON output.
  "markdown" ==> Produce Markdown output.
  _ ==> Produce plain text.

@if include_citations
  Always include citations.

@embed file: samples/data.txt

@note
  Describe what you want analyzed.

Analyze @{topic} with focus on @{description}.

@assert contains: "at least 3 examples" severity: error
"""

SPEC_BINDINGS = """\
# Tool Bindings

@tool web_search
  Search.

@bind web_search language: python from: "./tools/search.py" symbol: search
"""

SPEC_FUNCTIONAL = """\
@promplet version: 0.6

@define fetch_market_snapshot
  @phase execute
  @scope self
  @returns value

  @param ticker
    Ticker symbol.

  @effect market_data read

  @body
    Fetch market data for @{ticker}.

@bind market_data language: python from: "./tools/market.py" symbol: fetch

@execute functional scheduler: graph-strict
  allow_effects: [market_data]

@fetch_market_snapshot ticker: "@{ticker}" as: market_snapshot

Use @{market_snapshot} in the report.
"""

SPEC_MUSTACHE_LITERAL = """\
# Mustache Template

Render this literal template later:
{{name}} works on {{date}}.

WeaveMark topic: @{topic}
"""

SPEC_MODULE_MACROS = """\
@module company.review

@use company.presentation as presentation exposing concise

@define checklist(body: review material)
  Checklist:
  @{body}

@include presentation
"""


# ═══════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════


class TestScanSpec:
    """Core scan_spec() tests."""

    def test_simple_vars(self):
        meta = scan_spec(SPEC_SIMPLE)
        assert meta.title == "My Spec"
        names = [i.name for i in meta.inputs]
        assert "name" in names
        assert "place" in names
        assert all(i.input_type == "text" for i in meta.inputs)

    def test_multiline_heuristic(self):
        meta = scan_spec(SPEC_MULTILINE_VARS)
        types = {i.name: i.input_type for i in meta.inputs}
        assert types["topic"] == "text"
        assert types["description"] == "multiline"
        assert types["body"] == "multiline"

    def test_match_directive(self):
        meta = scan_spec(SPEC_MATCH)
        lang_input = next(i for i in meta.inputs if i.name == "language")
        assert lang_input.input_type == "select"
        assert "python" in lang_input.options
        assert "typescript" in lang_input.options
        assert "rust" in lang_input.options
        assert "_" not in lang_input.options
        assert lang_input.source_directive == "@match"

    def test_match_options_belong_only_to_their_selector(self):
        meta = scan_spec("""
@match language
  "python" ==> Python.
  _ ==> Other.

@match layout
  "grid" ==> Grid.
  "list" ==> List.
""")

        inputs = {item.name: item for item in meta.inputs}
        assert inputs["language"].options == ["python"]
        assert inputs["layout"].options == ["grid", "list"]

    def test_if_directive(self):
        meta = scan_spec(SPEC_IF)
        bools = [i for i in meta.inputs if i.input_type == "boolean"]
        names = {i.name for i in bools}
        assert "include_tests" in names
        assert "verbose_output" in names
        assert all(i.source_directive == "@if" for i in bools)

    def test_interpolated_if_variables_keep_text_types(self):
        meta = scan_spec("""
@if title
  Include the title.
@if language
  Localize the output.
@if layout
  Apply the layout.
@if output_path
  Mention the path.

Title: @{title}
Language: @{language}
Layout: @{layout}
Path: @{output_path}
""")

        inputs = {item.name: item for item in meta.inputs}
        assert {
            name: inputs[name].input_type
            for name in ("title", "language", "layout", "output_path")
        } == {
            "title": "text",
            "language": "text",
            "layout": "text",
            "output_path": "text",
        }

    def test_compile_metadata(self):
        meta = scan_spec(SPEC_COMPILE)
        assert meta.compile == {"format": "json"}

    def test_embed_file_variable(self):
        meta = scan_spec(SPEC_EMBED_FILE_VAR)
        file_input = next(i for i in meta.inputs if i.name == "input_file")
        assert file_input.input_type == "file"
        assert file_input.source_directive == "@embed"
        assert "Supports:" in file_input.file_hint

    def test_embed_static_files(self):
        meta = scan_spec(SPEC_EMBED_STATIC)
        assert "samples/data.txt" in meta.embed_files
        assert "docs/readme.md" in meta.embed_files
        # No file inputs should be created for static paths
        assert len(meta.inputs) == 0

    def test_emit_static_files(self):
        meta = scan_spec(SPEC_EMIT)
        assert meta.emit_files == ["prompts/system.md", "prompts/user.md"]

    def test_message_default_files(self):
        meta = scan_spec(SPEC_MESSAGE)
        assert meta.emit_files == ["intro.system.md", "request.user.md"]
        # Also picked up as named prompt entries.
        assert "intro" in meta.prompt_names
        assert "request" in meta.prompt_names

    def test_execute_metadata(self):
        meta = scan_spec(SPEC_EXECUTE)
        assert meta.execution is not None
        assert meta.execution["type"] == "reflection"
        assert meta.execution["max_iterations"] == 3
        assert meta.execution["temperature"] == 0.7

    def test_prompt_names(self):
        meta = scan_spec(SPEC_EXECUTE)
        assert "generate" in meta.prompt_names
        assert "critique" in meta.prompt_names
        assert "revise" in meta.prompt_names

    def test_tool_names(self):
        meta = scan_spec(SPEC_TOOLS)
        assert "web_search" in meta.tool_names
        assert "calculator" in meta.tool_names
        assert "sql_query" in meta.tool_names

    def test_binding_names(self):
        meta = scan_spec(SPEC_BINDINGS)
        assert meta.tool_names == ["web_search"]
        assert meta.binding_names == ["web_search"]

    def test_functional_generated_values_are_not_user_inputs(self):
        meta = scan_spec(SPEC_FUNCTIONAL)
        assert meta.execution == {
            "type": "functional",
            "scheduler": "graph-strict",
            "allow_effects": ["market_data"],
        }
        assert meta.binding_names == ["market_data"]
        assert meta.macro_names == ["fetch_market_snapshot"]
        assert [input.name for input in meta.inputs] == ["ticker"]

    def test_assertions(self):
        meta = scan_spec(SPEC_ASSERT)
        assert len(meta.assertions) == 2
        assert any("citations" in a for a in meta.assertions)

    def test_note_hints(self):
        meta = scan_spec(SPEC_NOTE_NEAR_VAR)
        focus_input = next(i for i in meta.inputs if i.name == "focus")
        assert focus_input.description is not None
        assert "characteristics" in focus_input.description

    def test_refine_static(self):
        meta = scan_spec(SPEC_REFINE)
        assert "./library/reasoning/base-analyst.weavemark.md" in meta.refine_files

    def test_refine_variable(self):
        meta = scan_spec(SPEC_REFINE)
        file_input = next(i for i in meta.inputs if i.name == "custom_base")
        assert file_input.input_type == "file"
        assert file_input.source_directive == "@refine"

    def test_collaborative_filters_internal_vars(self):
        """Internal strategy vars like edited_content/original_content are excluded."""
        meta = scan_spec(SPEC_COLLABORATIVE)
        names = {i.name for i in meta.inputs}
        assert "topic" in names
        assert "tone" in names
        assert "edited_content" not in names
        assert "original_content" not in names

    def test_reflection_filters_internal_vars(self):
        source = """
@execute reflection
  max_rounds: 3

Topic: @{topic}

@prompt generate
  Draft about @{topic}.

@prompt critique
  Review @{response}.

@prompt revise
  Revise @{response} using @{issues}.
"""

        meta = scan_spec(source)

        assert [item.name for item in meta.inputs] == ["topic"]

    @pytest.mark.parametrize(
        ("strategy", "internal_names"),
        [
            ("simplified-tree-of-thought", {"candidates", "best_approach"}),
            ("tree-of-thought", {"state", "best_path"}),
        ],
    )
    def test_tree_strategies_filter_runtime_variables(
        self, strategy, internal_names
    ):
        source = f"""
@execute {strategy}

Solve @{{problem}}.
Runtime: {' '.join(f'@{{{name}}}' for name in sorted(internal_names))}
"""

        meta = scan_spec(source)

        assert [item.name for item in meta.inputs] == ["problem"]

    def test_description_extraction(self):
        meta = scan_spec(SPEC_SIMPLE)
        assert "simple spec" in meta.description.lower()

    def test_title_and_description_follow_leading_note(self):
        meta = scan_spec("""\
@note
  # Internal note heading
  Context that is not the promplet description.

# Public Title

Public description.

@execute chain
""")

        assert meta.title == "Public Title"
        assert meta.description == "Public description."

    def test_title_inside_top_level_semantic_body_is_authored_title(self):
        meta = scan_spec("""\
@ask clarifying question detail_level: 35%
  @note
    # Private note heading

  # Wrapped public title

  Public body.
""")

        assert meta.title == "Wrapped public title"

    def test_wrapped_title_description_stops_at_sibling_directive_or_heading(self):
        directive = scan_spec("""\
@ask clarifying question detail_level: 35%
  # Wrapped title

  Public description.

  @style "Direct"
    Rest of semantic body.
""")
        heading = scan_spec("""\
@ask clarifying question detail_level: 35%
  # Wrapped title

  Public description.

  ## Next section
  Rest of semantic body.
""")

        assert directive.description == "Public description."
        assert heading.description == "Public description."

    def test_wrapped_title_description_does_not_leak_root_prose(self):
        meta = scan_spec("""\
@ask clarifying question detail_level: 35%
  # Wrapped title

  Public description.

Root prose owned by the outer document.
""")

        assert meta.description == "Public description."

    def test_canonical_tutorial_wrapped_titles_are_preserved(self):
        tutorials = Path(__file__).resolve().parents[1] / "promplets/tutorials"

        guided = scan_spec(
            (tutorials / "adaptive-tutor-guided.weavemark.md").read_text(
                encoding="utf-8"
            )
        )
        pack = scan_spec(
            (tutorials / "release-workbench-pack.weavemark.md").read_text(
                encoding="utf-8"
            )
        )

        assert guided.title == "Guided adaptive learning tutor"
        assert guided.description == ""
        assert pack.title == "@{product_name} product brief"

    def test_emit_body_heading_does_not_replace_primary_title(self):
        meta = scan_spec("""
@emit file: appendix.md
  # Appendix

# Main document

Primary prompt.
""")

        assert meta.title == "Main document"

    def test_nested_match_cases_do_not_leak_into_outer_options(self):
        meta = scan_spec("""\
@match outer_mode
  "first" ==>
    @match inner_mode
      "nested-a" ==> A
      "nested-b" ==> B
  "second" ==> Second
""")
        inputs = {item.name: item for item in meta.inputs}

        assert inputs["outer_mode"].options == ["first", "second"]
        assert inputs["inner_mode"].options == ["nested-a", "nested-b"]

    def test_has_notes(self):
        meta = scan_spec(SPEC_NOTE_NEAR_VAR)
        assert meta.has_notes is True
        meta2 = scan_spec(SPEC_SIMPLE)
        assert meta2.has_notes is False

    def test_no_duplicate_inputs(self):
        """Each variable name appears at most once in the inputs list."""
        meta = scan_spec(SPEC_COMPLEX)
        names = [i.name for i in meta.inputs]
        assert len(names) == len(set(names))

    def test_mustache_templates_are_not_weavemark_inputs(self):
        meta = scan_spec(SPEC_MUSTACHE_LITERAL)
        names = {i.name for i in meta.inputs}
        assert names == {"topic"}

    def test_module_macro_metadata(self):
        meta = scan_spec(SPEC_MODULE_MACROS)
        assert meta.module_name == "company.review"
        assert meta.use_modules == ["company.presentation"]
        assert meta.include_modules == ["presentation"]
        assert meta.macro_names == ["checklist"]

    def test_reference_metadata(self):
        meta = scan_spec(
            "@reference terminology.md keep:false\n"
            'See @reference("guide.md" keep:true) and @./facts.json.'
        )
        assert meta.reference_files == [
            "terminology.md",
            "guide.md",
            "./facts.json",
        ]

    def test_complex_spec_coverage(self):
        """A complex spec should discover all input types."""
        meta = scan_spec(SPEC_COMPLEX)
        types = {i.name: i.input_type for i in meta.inputs}
        assert types["output_format"] == "select"
        assert types["include_citations"] == "boolean"
        assert types["topic"] == "text"
        assert types["description"] == "multiline"
        # Metadata
        assert meta.execution["type"] == "reflection"
        assert "generate" in meta.prompt_names
        assert "web_search" in meta.tool_names
        assert "./library/reasoning/base-analyst.weavemark.md" in meta.refine_files
        assert "samples/data.txt" in meta.embed_files
        assert len(meta.assertions) == 1
        assert meta.has_notes

    def test_empty_spec(self):
        meta = scan_spec("")
        assert meta.title == ""
        assert meta.inputs == []
        assert meta.compile is None
        assert meta.execution is None

    def test_input_priority_order(self):
        """Directive and interpolation evidence merge without duplicate inputs."""
        spec = """\
# Priority

@match mode
  "fast" ==> speed
  "slow" ==> accuracy

@if debug

@{mode} @{debug} @{other}
"""
        meta = scan_spec(spec)
        mode_input = next(i for i in meta.inputs if i.name == "mode")
        debug_input = next(i for i in meta.inputs if i.name == "debug")
        assert mode_input.input_type == "select"
        assert debug_input.input_type == "text"
        assert len([i for i in meta.inputs if i.name == "mode"]) == 1
        assert len([i for i in meta.inputs if i.name == "debug"]) == 1


class TestSpecInputDataclass:
    """SpecInput dataclass basics."""

    def test_defaults(self):
        inp = SpecInput(name="x", input_type="text")
        assert inp.options is None
        assert inp.default is None
        assert inp.description is None
        assert inp.file_hint is None
        assert inp.source_directive is None

    def test_full_init(self):
        inp = SpecInput(
            name="lang",
            input_type="select",
            options=["python", "rust"],
            default="python",
            description="Pick a language",
            file_hint=None,
            source_directive="@match",
        )
        assert inp.options == ["python", "rust"]
        assert inp.default == "python"


class TestSpecMetadataDataclass:
    """SpecMetadata dataclass basics."""

    def test_defaults(self):
        meta = SpecMetadata()
        assert meta.title == ""
        assert meta.inputs == []
        assert meta.execution is None
        assert meta.prompt_names == []
        assert meta.tool_names == []
        assert meta.binding_names == []
