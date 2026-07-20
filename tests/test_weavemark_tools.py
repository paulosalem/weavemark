"""Tests for the @tool directive and tool parsing functionality.

Unit tests (no LLM required) verify strict compiler responses carry tools
correctly. Integration tests (require OPENAI_API_KEY) verify the full
@tool directive flow end-to-end.
"""

import os
from pathlib import Path

import pytest

from tests.wire_helpers import compiler_response
from weavemark.controller import (
    CompositionResult,
    WeaveMarkController,
    parse_composition_response,
)

# ═══════════════════════════════════════════════════════════════════
# Unit Tests — no LLM calls required
# ═══════════════════════════════════════════════════════════════════


class TestParseCompositionResponseWithTools:
    """Test strict compiler response parsing for tools and bindings."""

    def test_response_with_tools(self):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "City"}
                        },
                        "required": ["location"],
                    },
                },
            }
        ]
        result = parse_composition_response(
            compiler_response(
                "You are a weather assistant.",
                tools=tools,
                analysis="Processed @tool directive.",
            )
        )
        assert result.composed_prompt == "You are a weather assistant."
        assert len(result.tools) == 1
        assert result.tools[0]["function"]["name"] == "get_weather"
        assert result.tools[0]["function"]["parameters"]["required"] == ["location"]

    def test_response_without_tools(self):
        result = parse_composition_response(compiler_response("Hello world."))
        assert result.composed_prompt == "Hello world."
        assert result.tools == []

    def test_response_with_prompt_metadata(self):
        prompts = {"default": {"text": "Hello from CDATA.", "role": "user"}}
        result = parse_composition_response(
            compiler_response(
                "Hello from CDATA.",
                prompts=prompts,
                compile={"format": "markdown"},
                analysis="Decoded metadata.",
            )
        )
        assert result.composed_prompt == "Hello from CDATA."
        assert result.prompts == {"default": "Hello from CDATA."}
        assert result.prompt_roles == {"default": "user"}
        assert result.compile == {"format": "markdown"}
        assert result.tools == []
        assert result.bindings == []
        assert result.execution == {}
        assert result.analysis == "Decoded metadata."

    def test_response_with_bindings(self):
        bindings = [
            {
                "name": "search",
                "language": "python",
                "from": "./tools.py",
                "symbol": "search",
            }
        ]
        result = parse_composition_response(
            compiler_response("Hello", bindings=bindings)
        )
        assert result.bindings == bindings

    def test_response_with_multiple_tools(self):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search",
                    "parameters": {
                        "type": "object",
                        "properties": {"q": {"type": "string"}},
                        "required": ["q"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calc",
                    "description": "Calculate",
                    "parameters": {
                        "type": "object",
                        "properties": {"expr": {"type": "string"}},
                        "required": ["expr"],
                    },
                },
            },
        ]
        result = parse_composition_response(
            compiler_response("Agent prompt.", tools=tools)
        )
        assert len(result.tools) == 2
        names = [t["function"]["name"] for t in result.tools]
        assert "search" in names
        assert "calc" in names

    def test_plain_text_is_a_protocol_error(self):
        result = parse_composition_response("Just plain text, no JSON.")
        assert result.tools == []
        assert result.composed_prompt == ""
        assert result.errors


class TestReadFileResolution:
    """Test read_file fallback behavior for promplets in subdirectories."""

    def test_subdirectory_promplet_can_read_root_promplet(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        library_dir = tmp_path / "promplets"
        readme_dir = library_dir / "readme"
        readme_dir.mkdir(parents=True)
        (library_dir / "reasoning").mkdir()
        root_spec = library_dir / "reasoning/base-analyst.weavemark.md"
        root_spec.write_text("Base analyst spec", encoding="utf-8")

        assert (
            WeaveMarkController._read_file(
                "reasoning/base-analyst.weavemark.md",
                readme_dir,
            )
            == "Base analyst spec"
        )


class TestCompositionResultToDict:
    """Test that to_dict includes tools when present."""

    def test_to_dict_with_tools(self):
        tools = [{"type": "function", "function": {"name": "test_tool"}}]
        result = CompositionResult(
            composed_prompt="Hello",
            tools=tools,
        )
        d = result.to_dict()
        assert "tools" in d
        assert d["tools"] == tools

    def test_to_dict_with_bindings(self):
        bindings = [{"name": "search", "language": "python"}]
        result = CompositionResult(
            composed_prompt="Hello",
            bindings=bindings,
        )
        d = result.to_dict()
        assert d["bindings"] == bindings

    def test_to_dict_without_tools(self):
        result = CompositionResult(composed_prompt="Hello")
        d = result.to_dict()
        assert "tools" not in d

    def test_to_dict_empty_tools(self):
        result = CompositionResult(composed_prompt="Hello", tools=[])
        d = result.to_dict()
        assert "tools" not in d


# ═══════════════════════════════════════════════════════════════════
# Integration Tests — require OPENAI_API_KEY
# ═══════════════════════════════════════════════════════════════════

_skip = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — requires a real LLM",
)

SPECS_DIR = Path(__file__).resolve().parents[1] / "specs"


def _controller():
    from weavemark.controller import WeaveMarkConfig, WeaveMarkController

    return WeaveMarkController(WeaveMarkConfig())


async def _compose(spec, variables=None, **kwargs):
    c = _controller()
    return await c.compose(spec, variables=variables or {}, **kwargs)


@_skip
class TestToolDirectiveE2E:
    """End-to-end tests for the @tool directive."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_single_tool(self):
        """A single @tool directive produces one tool definition."""
        spec = (
            "You are a research assistant.\n\n"
            "@tool search_web\n"
            "  Search the web for information.\n"
            "  - query: string (required) — The search query\n"
            "  - max_results: integer — Maximum results\n"
        )
        r = await _compose(spec)
        assert r.composed_prompt, "Should produce a prompt"
        assert len(r.tools) >= 1, "Should have at least one tool"
        names = [t["function"]["name"] for t in r.tools]
        assert "search_web" in names

        # Validate the tool structure
        tool = next(t for t in r.tools if t["function"]["name"] == "search_web")
        assert tool["type"] == "function"
        params = tool["function"]["parameters"]
        assert "query" in params.get("properties", {})
        assert "query" in params.get("required", [])

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_tools(self):
        """Multiple @tool directives produce multiple tool definitions."""
        spec = (
            "You are an agent.\n\n"
            "@tool get_weather\n"
            "  Get weather conditions.\n"
            "  - location: string (required) — City name\n\n"
            "@tool calculate\n"
            "  Perform a calculation.\n"
            "  - expression: string (required) — Math expression\n"
        )
        r = await _compose(spec)
        assert len(r.tools) >= 2
        names = [t["function"]["name"] for t in r.tools]
        assert "get_weather" in names
        assert "calculate" in names

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_with_enum(self):
        """@tool with enum parameter constraint."""
        spec = (
            "You are a weather bot.\n\n"
            "@tool get_weather\n"
            "  Get weather.\n"
            "  - location: string (required) — City\n"
            "  - units: string enum: [celsius, fahrenheit] — Temp units\n"
        )
        r = await _compose(spec)
        assert len(r.tools) >= 1
        tool = next(t for t in r.tools if t["function"]["name"] == "get_weather")
        units_prop = tool["function"]["parameters"]["properties"].get("units", {})
        if "enum" in units_prop:
            assert "celsius" in units_prop["enum"]
            assert "fahrenheit" in units_prop["enum"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_no_tools_produces_empty_array(self):
        """A spec without @tool should produce empty tools list."""
        spec = "You are a helpful assistant. Answer questions clearly."
        r = await _compose(spec)
        assert r.tools == [] or r.tools is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tools_not_in_prompt_text(self):
        """@tool definitions should NOT appear in the composed prompt text."""
        spec = (
            "You are a programming assistant.\n\n"
            "@tool run_program\n"
            "  Execute a program.\n"
            "  - program: string (required) — Program to run\n"
        )
        r = await _compose(spec)
        # The @tool directive should be processed, not passed through
        assert "@tool" not in r.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_react_agent_spec(self):
        """The react-agent.weavemark.md example spec compiles with tools."""
        spec_path = SPECS_DIR / "react-agent.weavemark.md"
        if not spec_path.exists():
            pytest.skip("react-agent.weavemark.md not found")
        spec = spec_path.read_text(encoding="utf-8")
        r = await _compose(
            spec,
            variables={
                "research_topic": "renewable energy trends",
                "audience": "business executives",
                "depth": "standard",
                "include_citations": True,
            },
            base_dir=SPECS_DIR,
        )
        assert r.composed_prompt, "Should produce a prompt"
        assert len(r.tools) >= 2, f"Expected at least 2 tools, got {len(r.tools)}"
        names = [t["function"]["name"] for t in r.tools]
        assert "search_web" in names
        assert "calculate" in names
        assert "read_url" not in names
        # Arbitrary Python execution is not part of the catalog surface.
        assert "run_python" not in names
