"""Unit tests for WeaveMark LLMClient.complete_with_tools() multi-turn tool calling.

These tests mock LiteLLM responses to verify the loop logic without
making real API calls.
"""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from ellements.core import (
    LLMClient,
    MaxToolIterationsError,
    ToolCallRecord,
    ToolCallResponse,
)

# ---------------------------------------------------------------------------
# Helpers to build mock LiteLLM responses
# ---------------------------------------------------------------------------

def _text_response(content: str):
    """Simulate a plain-text completion (no tool calls)."""
    msg = SimpleNamespace(content=content, tool_calls=None)
    choice = SimpleNamespace(message=msg)
    return SimpleNamespace(choices=[choice])


def _tool_call_response(calls: list[tuple[str, str, dict]]):
    """Simulate a response that requests one or more tool calls.

    *calls* is a list of ``(call_id, function_name, arguments_dict)``.
    """
    tool_calls = []
    for call_id, fn_name, fn_args in calls:
        tc = SimpleNamespace(
            id=call_id,
            type="function",
            function=SimpleNamespace(
                name=fn_name,
                arguments=json.dumps(fn_args),
            ),
        )
        tool_calls.append(tc)

    msg = SimpleNamespace(content=None, tool_calls=tool_calls)
    choice = SimpleNamespace(message=msg)
    return SimpleNamespace(choices=[choice])


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return LLMClient(model="gpt-4o-mini")


DUMMY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string"},
                },
                "required": ["file_name"],
            },
        },
    }
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCompleteWithTools:
    """Tests for the multi-turn tool-calling loop."""

    @pytest.mark.asyncio
    async def test_no_tool_calls_returns_immediately(self, client):
        """When the model responds with text only, return right away."""
        executor = AsyncMock()

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = _text_response("Hello!")
            result = await client.complete_with_tools(
                "Hi", tools=DUMMY_TOOLS, tool_executor=executor,
            )

        assert isinstance(result, ToolCallResponse)
        assert result.content == "Hello!"
        assert result.tool_calls == []
        executor.assert_not_called()

    @pytest.mark.asyncio
    async def test_single_tool_call_round_trip(self, client):
        """Model requests one tool call, then responds with text."""
        executor = AsyncMock(return_value="file contents here")

        responses = [
            _tool_call_response([("tc1", "read_file", {"file_name": "a.md"})]),
            _text_response("Composed prompt."),
        ]

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = responses
            result = await client.complete_with_tools(
                "Compose", tools=DUMMY_TOOLS, tool_executor=executor,
            )

        assert result.content == "Composed prompt."
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].name == "read_file"
        assert result.tool_calls[0].arguments == {"file_name": "a.md"}
        assert result.tool_calls[0].result == "file contents here"

        executor.assert_awaited_once_with("read_file", {"file_name": "a.md"})

    @pytest.mark.asyncio
    async def test_multiple_tool_calls_in_one_turn(self, client):
        """Model requests two parallel tool calls in a single response."""
        executor = AsyncMock(side_effect=["contents A", "contents B"])

        responses = [
            _tool_call_response([
                ("tc1", "read_file", {"file_name": "a.md"}),
                ("tc2", "read_file", {"file_name": "b.md"}),
            ]),
            _text_response("Done."),
        ]

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = responses
            result = await client.complete_with_tools(
                "Compose", tools=DUMMY_TOOLS, tool_executor=executor,
            )

        assert result.content == "Done."
        assert len(result.tool_calls) == 2

    @pytest.mark.asyncio
    async def test_multi_round_tool_calls(self, client):
        """Model makes tool calls across multiple rounds."""
        call_count = 0

        async def executor(name, args):
            nonlocal call_count
            call_count += 1
            return f"result-{call_count}"

        responses = [
            _tool_call_response([("tc1", "read_file", {"file_name": "a.md"})]),
            _tool_call_response([("tc2", "read_file", {"file_name": "b.md"})]),
            _text_response("Final answer."),
        ]

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = responses
            result = await client.complete_with_tools(
                "Compose", tools=DUMMY_TOOLS, tool_executor=executor,
            )

        assert result.content == "Final answer."
        assert len(result.tool_calls) == 2
        assert result.tool_calls[0].result == "result-1"
        assert result.tool_calls[1].result == "result-2"

    @pytest.mark.asyncio
    async def test_max_iterations_raises(self, client):
        """Loop hits ``max_iterations`` → ``MaxToolIterationsError`` is raised
        with the partial conversation and unresolved tool calls attached."""
        executor = AsyncMock(return_value="ok")

        infinite_calls = _tool_call_response(
            [("tc1", "read_file", {"file_name": "x.md"})]
        )

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = infinite_calls
            with pytest.raises(MaxToolIterationsError) as excinfo:
                await client.complete_with_tools(
                    "Go",
                    tools=DUMMY_TOOLS,
                    tool_executor=executor,
                    max_iterations=3,
                )

        assert excinfo.value.max_iterations == 3
        assert mock_comp.await_count == 3
        assert executor.await_count == 3

    @pytest.mark.asyncio
    async def test_conversation_input(self, client):
        """Accepts a Conversation object as input."""
        conv = client.create_conversation(system_prompt="You are helpful.")
        conv.user("Hello")

        executor = AsyncMock()

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = _text_response("Hi!")
            result = await client.complete_with_tools(
                conv, tools=DUMMY_TOOLS, tool_executor=executor,
            )

        assert result.content == "Hi!"
        # Verify the system prompt was included
        call_msgs = mock_comp.call_args[1]["messages"]
        assert call_msgs[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_tools_passed_to_litellm(self, client):
        """Verify that tool definitions are forwarded to litellm.acompletion."""
        executor = AsyncMock()

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = _text_response("ok")
            await client.complete_with_tools(
                "test", tools=DUMMY_TOOLS, tool_executor=executor,
            )

        assert mock_comp.call_args[1]["tools"] == DUMMY_TOOLS

    @pytest.mark.asyncio
    async def test_tool_results_appended_to_messages(self, client):
        """After a tool call, verify tool results are appended correctly."""
        executor = AsyncMock(return_value="file data")

        responses = [
            _tool_call_response([("tc1", "read_file", {"file_name": "f.md"})]),
            _text_response("Done"),
        ]

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = responses
            await client.complete_with_tools(
                "test", tools=DUMMY_TOOLS, tool_executor=executor,
            )

        # Second call should contain the tool result message
        second_call_msgs = mock_comp.call_args_list[1][1]["messages"]
        tool_msg = [m for m in second_call_msgs if m.get("role") == "tool"]
        assert len(tool_msg) == 1
        assert tool_msg[0]["content"] == "file data"
        assert tool_msg[0]["tool_call_id"] == "tc1"
