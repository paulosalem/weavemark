"""Strict semantic compiler response-contract tests."""

from __future__ import annotations

import json

import pytest
from ellements.core import ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.compilation.result_schema import (
    CompilerProtocolError,
    compiler_response_format,
    parse_wire_result,
)
from weavemark.controller import (
    WeaveMarkConfig,
    WeaveMarkController,
    parse_composition_response,
)


@pytest.mark.parametrize(
    "literal",
    (
        '```python\nprint("</prompt>")\n```',
        "<literal attr=\"x\">& data</literal>",
        "<![CDATA[not transport markup]]>",
        'JSON example: {"nested": [1, 2, 3]}',
    ),
)
def test_prompt_literals_round_trip_exactly(literal: str) -> None:
    result = parse_composition_response(compiler_response(literal))

    assert result.errors == []
    assert result.composed_prompt == literal
    assert result.prompts == {"default": literal}


def test_complete_metadata_round_trip_includes_packages_and_outputs() -> None:
    raw = compiler_response(
        "Prompt",
        prompts={"stage": {"text": "Stage", "role": "system"}},
        compile={"format": "json", "context": "local", "images": "off"},
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search",
                    "parameters": {"type": "object"},
                },
            }
        ],
        bindings=[{"capability": "search", "language": "python"}],
        execution={"type": "chain"},
        emits={"artifact.md": "Artifact"},
        outputs={"stage": {"type": "text", "file": "stage.md"}},
        packages=[{"file": "book.html", "template": "template.weavemark.md"}],
        references={"R1": "Resolved reference."},
        analysis="Analysis",
        warnings=["Warning"],
        suggestions=["Suggestion"],
    )

    result = parse_composition_response(raw)

    assert result.errors == []
    assert result.prompts == {"stage": "Stage"}
    assert result.prompt_roles == {"stage": "system"}
    assert result.compile == {"format": "json", "context": "local", "images": "off"}
    assert result.bindings == [{"name": "search", "language": "python"}]
    assert result.execution == {"type": "chain"}
    assert result.emits == {"artifact.md": "Artifact"}
    assert result.prompt_outputs["stage"].params["file"] == "stage.md"
    assert result.packages == [
        {"file": "book.html", "template": "template.weavemark.md"}
    ]
    assert result.reference_contents == {"R1": "Resolved reference."}
    assert result.warnings == ["Warning"]
    assert result.suggestions == ["Suggestion"]


@pytest.mark.parametrize(
    "raw",
    (
        "",
        "plain text",
        "```json\n{}\n```",
        '{"prompt": "unclosed"',
    ),
)
def test_malformed_or_wrapped_response_is_rejected(raw: str) -> None:
    result = parse_composition_response(raw)

    assert result.composed_prompt == ""
    assert result.raw_response == raw
    assert result.errors
    assert "protocol error" in result.errors[0].lower()


def test_missing_required_field_is_rejected() -> None:
    data = json.loads(compiler_response("Prompt"))
    del data["packages"]

    with pytest.raises(CompilerProtocolError, match="packages"):
        parse_wire_result(json.dumps(data))


def test_extra_field_is_rejected() -> None:
    data = json.loads(compiler_response("Prompt"))
    data["unexpected"] = True

    with pytest.raises(CompilerProtocolError, match="unexpected"):
        parse_wire_result(json.dumps(data))


def test_duplicate_json_key_is_rejected() -> None:
    raw = compiler_response("Prompt")
    duplicate = raw[:-1] + ', "prompt": "Other"}'

    with pytest.raises(CompilerProtocolError, match="duplicate JSON key"):
        parse_wire_result(duplicate)


class _ProtocolRepairClient:
    def __init__(self) -> None:
        valid = compiler_response("Repaired prompt")
        self.responses = [
            valid[:-1] + ', "prompt": "Duplicate"}',
            valid,
        ]
        self.calls = 0

    async def complete_with_tools(self, *args: object, **kwargs: object) -> ToolCallResponse:
        response = self.responses[self.calls]
        self.calls += 1
        return ToolCallResponse(content=response)


@pytest.mark.asyncio
async def test_controller_repairs_one_invalid_compiler_response() -> None:
    client = _ProtocolRepairClient()
    controller = WeaveMarkController(
        WeaveMarkConfig(use_structural_helpers=False),
        client=client,
    )

    result = await controller.compose("Write a useful prompt.", variables={})

    assert result.errors == []
    assert result.composed_prompt == "Repaired prompt"
    assert client.calls == 2
    assert "protocol-repair retry" in " ".join(result.warnings)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("warnings", "warning"),
        ("prompts", {"default": "not-an-object"}),
        ("bindings", [{"capability": 42}]),
        ("emits", {"file.md": 42}),
    ),
)
def test_wrong_field_types_are_rejected(field: str, value: object) -> None:
    data = json.loads(compiler_response("Prompt"))
    data[field] = value

    with pytest.raises(CompilerProtocolError):
        parse_wire_result(json.dumps(data))


@pytest.mark.parametrize(
    "package",
    (
        {"file": "out.html"},
        {"file": "out.html", "template": "t.md", "from": "source.html"},
    ),
)
def test_package_requires_exactly_one_source(package: dict[str, str]) -> None:
    data = json.loads(compiler_response("Prompt"))
    data["packages"] = [package]

    with pytest.raises(CompilerProtocolError, match="exactly one"):
        parse_wire_result(json.dumps(data))


def test_default_prompt_must_match_primary_prompt() -> None:
    data = json.loads(compiler_response("Prompt"))
    data["prompts"]["default"]["text"] = "Different"

    with pytest.raises(CompilerProtocolError, match="must equal prompt"):
        parse_wire_result(json.dumps(data))


def test_provider_schema_is_guidance_while_local_validation_stays_strict() -> None:
    response_format = compiler_response_format()

    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is False
    assert set(response_format["json_schema"]["schema"]["required"]) == {
        "prompt",
        "prompts",
        "compile",
        "tools",
        "bindings",
        "execution",
        "emits",
        "outputs",
        "packages",
        "references",
        "directives",
        "analysis",
        "warnings",
        "errors",
        "suggestions",
    }
