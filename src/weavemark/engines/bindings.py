"""Load explicit Python bindings for executable WeaveMark tools."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import sys
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Any, cast

from ellements.core.exceptions import LLMError

from ..compilation.result import CompositionResult

ToolExecutor = Callable[[str, dict[str, Any]], Awaitable[str]]


def load_tool_executor(
    result: CompositionResult,
    *,
    max_calls: int,
) -> ToolExecutor:
    """Load and return the executor for all declared bound tools."""

    source_path = result.source_path
    if source_path is None:
        raise ValueError("Bound tools require a source promplet path.")
    base_dir = Path(source_path).resolve().parent
    bindings = {
        _binding_name(binding): binding
        for binding in result.bindings
    }
    tool_names = {
        str(tool.get("function", {}).get("name", ""))
        for tool in result.tools
        if isinstance(tool, Mapping)
    }
    missing = sorted(name for name in tool_names if name not in bindings)
    if missing:
        raise ValueError(
            "Executable tools are missing @bind implementations: "
            + ", ".join(missing)
            + "."
        )

    callables = {
        name: _load_binding(binding, base_dir, result)
        for name, binding in bindings.items()
        if name in tool_names
    }
    calls_made = 0

    async def execute(name: str, arguments: dict[str, Any]) -> str:
        nonlocal calls_made
        if calls_made >= max_calls:
            return json.dumps(
                {
                    "error": f"Bound tool-call budget exhausted after {max_calls} calls.",
                    "tool": name,
                    "recoverable": True,
                    "budget_exhausted": True,
                },
                ensure_ascii=False,
            )
        calls_made += 1
        try:
            function = callables[name]
        except KeyError as exc:
            raise KeyError(f"No bound implementation for tool {name!r}.") from exc
        try:
            value = function(**arguments)
            if inspect.isawaitable(value):
                value = await value
        except LLMError as exc:
            return json.dumps(
                {
                    "error": str(exc),
                    "tool": name,
                    "arguments": arguments,
                    "recoverable": True,
                },
                ensure_ascii=False,
            )
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, default=str)

    return execute


def _load_binding(
    binding: dict[str, str],
    base_dir: Path,
    result: CompositionResult,
) -> Callable[..., Any]:
    language = binding.get("language", "").casefold()
    if language != "python":
        raise ValueError(
            f"Unsupported @bind language {binding.get('language')!r}; expected python."
        )
    source = binding.get("from", "")
    path = (base_dir / source).resolve()
    try:
        path.relative_to(base_dir)
    except ValueError as exc:
        raise ValueError(f"@bind source escapes the promplet directory: {source}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"@bind source not found: {source}")
    if result.protection is not None:
        result.protection.authorize_python(
            source,
            path=path,
            reason=f"Executing bound tool {_binding_name(binding)!r}",
        )

    module_name = (
        "_weavemark_binding_"
        + hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]
    )
    module = sys.modules.get(module_name)
    if module is None:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load @bind module: {source}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

    symbol = binding.get("symbol", "")
    function = getattr(module, symbol, None)
    if not callable(function):
        raise TypeError(f"@bind symbol is not callable: {source}:{symbol}")
    return cast(Callable[..., Any], function)


def _binding_name(binding: Mapping[str, str]) -> str:
    name = (
        binding.get("name")
        or binding.get("capability")
        or binding.get("capability_name")
        or binding.get("tool")
    )
    if not name:
        raise ValueError("Compiled @bind metadata is missing its capability name.")
    return name


__all__ = ["ToolExecutor", "load_tool_executor"]
