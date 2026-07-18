"""Strict JSON and YAML loaders for promplet input variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class VariablesFileError(ValueError):
    """Describe an invalid variables file with optional source location."""

    def __init__(self, message: str, *, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


_UniqueKeyLoader.yaml_implicit_resolvers = {
    character: [
        resolver
        for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:timestamp"
    ]
    for character, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _construct_unique_mapping(
    loader: _UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise VariablesFileError(
                "YAML mapping keys must be scalar values.",
                line=key_node.start_mark.line + 1,
            ) from exc
        if duplicate:
            raise VariablesFileError(
                f"Duplicate variable key {key!r}.",
                line=key_node.start_mark.line + 1,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_variables_file(path: Path) -> dict[str, Any]:
    """Load one strict JSON/YAML object from *path*."""

    suffix = path.suffix.casefold()
    if suffix not in {".json", ".yaml", ".yml"}:
        raise VariablesFileError(
            "Variables files must use a .json, .yaml, or .yml extension."
        )

    text = path.read_text(encoding="utf-8")
    try:
        if suffix == ".json":
            loaded = json.loads(text, object_pairs_hook=_unique_json_object)
        else:
            loaded = yaml.load(text, Loader=_UniqueKeyLoader)
    except json.JSONDecodeError as exc:
        raise VariablesFileError(exc.msg, line=exc.lineno) from exc
    except VariablesFileError:
        raise
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 1 if mark is not None else None
        message = getattr(exc, "problem", None) or str(exc)
        raise VariablesFileError(str(message), line=line) from exc

    if not isinstance(loaded, dict):
        raise VariablesFileError("Variables file must contain one object.")
    if not all(isinstance(key, str) for key in loaded):
        raise VariablesFileError("Every variable name must be a string.")
    return loaded


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VariablesFileError(f"Duplicate variable key {key!r}.")
        result[key] = value
    return result


__all__ = ["VariablesFileError", "load_variables_file"]
