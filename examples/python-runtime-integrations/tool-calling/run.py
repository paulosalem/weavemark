#!/usr/bin/env python3
# ruff: noqa: E402
"""Compile a WeaveMark tool schema and execute it with a local calculator."""

from __future__ import annotations

import ast
import asyncio
import json
import operator
import os
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "python-runtime-integrations" / "tool-calling"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "examples" / "_lib"))

from ellements.core import LLMClient, ToolRegistry, ToolSpec
from weavemark_example_progress import weavemark_verbose_event

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.defaults import DEFAULT_MODEL

SPEC_PATH = (
    REPO_ROOT
    / "promplets"
    / "catalog"
    / "executable"
    / "portfolio-calculator-agent.weavemark.md"
)
VARS_PATH = EXAMPLE_ROOT / "inputs" / "vars.json"
OUTPUT_DIR = EXAMPLE_ROOT / "outputs"

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def calculate(expression: str) -> str:
    """Evaluate a small arithmetic expression without executing Python code."""

    normalized = expression.replace("$", "").replace(",", "").replace("^", "**").strip()
    if len(normalized) > 300:
        raise ValueError("Expression is too long.")
    tree = ast.parse(normalized, mode="eval")
    value = _evaluate_expression_node(tree)
    if value.is_integer():
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _evaluate_expression_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_expression_node(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value)
    if isinstance(node, ast.UnaryOp):
        operator_fn = _UNARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return operator_fn(_evaluate_expression_node(node.operand))
    if isinstance(node, ast.BinOp):
        operator_fn = _BINARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
        left = _evaluate_expression_node(node.left)
        right = _evaluate_expression_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 500:
            raise ValueError("Exponent is too large.")
        return operator_fn(left, right)
    raise ValueError(f"Unsupported expression element: {type(node).__name__}")


async def _invoke_calculate(expression: str) -> str:
    return calculate(expression)


def _tool_spec_from_weavemark(
    tool_schema: dict[str, Any],
    invoke: Callable[..., Awaitable[Any]],
) -> ToolSpec:
    function = tool_schema.get("function")
    if not isinstance(function, dict):
        raise ValueError("WeaveMark did not produce an OpenAI-style function schema.")
    name = function.get("name")
    if not isinstance(name, str):
        raise ValueError("WeaveMark tool schema is missing a function name.")
    parameters = function.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError("WeaveMark tool schema parameters must be a JSON object.")
    return ToolSpec(
        name=name,
        description=str(function.get("description", "")),
        params_json_schema=parameters,
        invoke=invoke,
    )


def _render_tool_trace(
    *,
    prompt: str,
    tools: list[dict[str, Any]],
    tool_calls: list[Any],
    output: str,
) -> str:
    return "\n".join(
        [
            "# WeaveMark Tool-Calling Trace",
            "",
            f"- Model: `{DEFAULT_MODEL}`",
            f"- Spec: `{SPEC_PATH.relative_to(REPO_ROOT)}`",
            f"- Tool calls: {len(tool_calls)}",
            "",
            "## Compiled prompt",
            "",
            _fence(prompt, "markdown"),
            "",
            "## Tool schema emitted by WeaveMark",
            "",
            _fence(json.dumps(tools, indent=2, ensure_ascii=False), "json"),
            "",
            "## Tool calls",
            "",
            _fence(
                json.dumps(
                    [call.model_dump() for call in tool_calls],
                    indent=2,
                    ensure_ascii=False,
                ),
                "json",
            ),
            "",
            "## Final response",
            "",
            _fence(output, "markdown"),
            "",
        ]
    )


def _fence(content: str, language: str) -> str:
    fence = "```"
    while fence in content:
        fence += "`"
    return f"{fence}{language}\n{content}\n{fence}"


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required to run the tool-calling demo.")

    variables = json.loads(VARS_PATH.read_text(encoding="utf-8"))
    controller = WeaveMarkController(WeaveMarkConfig(model=DEFAULT_MODEL))
    result = await controller.compose(
        SPEC_PATH.read_text(encoding="utf-8"),
        variables=variables,
        base_dir=SPEC_PATH.parent,
        on_event=weavemark_verbose_event,
    )
    if result.errors:
        raise RuntimeError("\n".join(result.errors))
    if len(result.tools) != 1:
        raise RuntimeError(
            f"Expected exactly one WeaveMark tool, got {len(result.tools)}."
        )

    _section("WeaveMark compiled prompt")
    print(result.composed_prompt)

    _section("WeaveMark-emitted tool schema")
    print(json.dumps(result.tools, indent=2, ensure_ascii=False))

    tool = _tool_spec_from_weavemark(result.tools[0], _invoke_calculate)
    client = LLMClient(model=DEFAULT_MODEL)
    _section(f"Executing with {DEFAULT_MODEL} and the local Ellements ToolRegistry")
    response = await client.complete_with_tools(
        [{"role": "user", "content": result.composed_prompt}],
        tools=ToolRegistry([tool]),
        temperature=0.0,
    )
    if not response.tool_calls:
        raise RuntimeError("The model returned without calling the calculate tool.")

    _section("Tool calls made by the model")
    print(
        json.dumps(
            [call.model_dump() for call in response.tool_calls],
            indent=2,
            ensure_ascii=False,
        )
    )

    _section("Final response")
    print(response.content)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    compiled_path = OUTPUT_DIR / "compiled-prompt.json"
    compiled_path.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    output_path = OUTPUT_DIR / "execution-output.md"
    output_path.write_text(response.content, encoding="utf-8")
    calls_path = OUTPUT_DIR / "tool-calls.json"
    calls_path.write_text(
        json.dumps(
            [call.model_dump() for call in response.tool_calls],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    trace_path = OUTPUT_DIR / "execution-trace.md"
    trace_path.write_text(
        _render_tool_trace(
            prompt=result.composed_prompt,
            tools=result.tools,
            tool_calls=response.tool_calls,
            output=response.content,
        ),
        encoding="utf-8",
    )

    _section("Artifacts written")
    print(f"Wrote {compiled_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {calls_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {trace_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
