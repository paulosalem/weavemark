"""Engine registry — resolve engine names to instances."""

from __future__ import annotations

import importlib
from collections.abc import Callable

from ellements.core import LLMClient

from ..protection import ProtectionContext
from .base import Engine

BUILTIN_ENGINES: dict[str, Callable[..., Engine]] = {}


def _lazy_load_builtins() -> None:
    """Lazily populate the built-in registry on first use."""
    if BUILTIN_ENGINES:
        return
    from .chain import ChainEngine
    from .collaborative import CollaborativeEngine
    from .fslm import FSLMEngine
    from .functional import FunctionalEngine
    from .reflection import ReflectionEngine
    from .self_consistency import SelfConsistencyEngine
    from .single_call import SingleCallEngine
    from .tree_of_thought import SimplifiedTreeOfThoughtEngine, TreeOfThoughtEngine

    BUILTIN_ENGINES.update(
        {
            "single-call": SingleCallEngine,
            "self-consistency": SelfConsistencyEngine,
            "tree-of-thought": TreeOfThoughtEngine,
            "simplified-tree-of-thought": SimplifiedTreeOfThoughtEngine,
            "reflection": ReflectionEngine,
            "chain": ChainEngine,
            "collaborative": CollaborativeEngine,
            "fslm": FSLMEngine,
            "functional": FunctionalEngine,
        }
    )


def resolve_engine(
    name_or_path: str,
    *,
    client: LLMClient | None = None,
    protection: ProtectionContext | None = None,
) -> Engine:
    """Resolve an engine by built-in name or dotted Python import path.

    Args:
        name_or_path: Either a built-in name (``"single-call"``,
            ``"self-consistency"``, ``"tree-of-thought"``,
            ``"simplified-tree-of-thought"``, ``"reflection"``,
            ``"collaborative"``, ``"fslm"``, ``"functional"``)
            or a fully-qualified Python class path
            (e.g. ``"my_package.engines.CustomEngine"``).

    Returns:
        An instantiated :class:`Engine`.

    Raises:
        ValueError: If the name cannot be resolved.
    """
    _lazy_load_builtins()

    if name_or_path in BUILTIN_ENGINES:
        return BUILTIN_ENGINES[name_or_path](client=client)

    # Try importing as a dotted path
    try:
        if protection is not None and "." in name_or_path:
            protection.authorize_python(
                name_or_path,
                reason="Loading a custom WeaveMark execution engine imports Python code.",
            )
        module_path, class_name = name_or_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        engine_cls = getattr(module, class_name)
        engine = engine_cls()
        if not isinstance(engine, Engine):
            raise TypeError(
                f"Custom engine {name_or_path!r} does not implement the Engine protocol."
            )
        return engine
    except (ValueError, ImportError, AttributeError) as exc:
        available = ", ".join(sorted(BUILTIN_ENGINES.keys()))
        raise ValueError(
            f"Unknown engine '{name_or_path}'. "
            f"Built-in engines: {available}. "
            f"Or provide a dotted Python import path."
        ) from exc
