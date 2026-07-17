"""Surface adapter base classes, registry, and public entry point.

Design rules
------------
* The canonical surface (``surface: canonical`` or no ``surface:`` param) is
  a no-op identity adapter — the source text is returned unchanged.
* Every adapter receives only the raw spec text and returns a
  :class:`SurfaceLoweringResult` with canonical WeaveMark text plus any
  warnings or errors produced during lowering.
* Adapters MUST NOT call the LLM, import the macro/module system, or assume
  any runtime context — their job is purely textual transformation.
* Adapters are registered once at import time; the registry is a simple dict
  keyed by lowercase surface name.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

_SURFACE_PRAGMA_RE = re.compile(
    r"^@promplet\b(?P<rest>[^\n]*)$",
    re.MULTILINE,
)
_KV_RE = re.compile(r"(?P<key>[A-Za-z_][\w-]*)\s*:\s*(?P<value>\S+)")


@dataclass
class SurfaceLoweringResult:
    """Result of running a surface adapter over a raw spec.

    Attributes:
        text:     Canonical WeaveMark text (may equal the input when the
                  adapter is a no-op).
        surface:  The surface name that was detected and applied, or
                  ``"canonical"`` when no surface was declared.
        warnings: Non-fatal issues produced during lowering.
        errors:   Fatal issues that prevent further processing.  When
                  non-empty, ``text`` may be incomplete.
    """

    text: str
    surface: str = "canonical"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Adapter protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class SurfaceAdapter(Protocol):
    """Protocol for a WeaveMark surface adapter.

    Concrete adapters must implement :meth:`lower`.  They should be stateless
    and thread-safe.
    """

    @property
    def name(self) -> str:
        """Lowercase surface name (e.g. ``"markdown"``, ``"html"``)."""
        ...

    def lower(self, spec_text: str) -> SurfaceLoweringResult:
        """Deterministically lower *spec_text* to canonical WeaveMark.

        The returned :attr:`SurfaceLoweringResult.text` must be valid
        canonical WeaveMark.  Errors in ``result.errors`` prevent further
        processing; warnings in ``result.warnings`` are informational.
        """
        ...


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, SurfaceAdapter] = {}


def register_surface_adapter(adapter: SurfaceAdapter) -> None:
    """Register *adapter* under its :attr:`~SurfaceAdapter.name`.

    Calling this twice with the same name overwrites the previous adapter.
    """
    _REGISTRY[adapter.name.lower()] = adapter


def _get_adapter(surface: str) -> SurfaceAdapter | None:
    return _REGISTRY.get(surface.lower())


# ---------------------------------------------------------------------------
# Pragma parsing
# ---------------------------------------------------------------------------


def parse_surface_pragma(spec_text: str) -> str | None:
    """Return the declared surface name from the ``@promplet`` pragma, if any.

    Scans the first non-blank line only (as the grammar requires).  Returns
    the lowercased surface name (e.g. ``"markdown"``) or ``None`` when no
    ``surface:`` key is present or no ``@promplet`` pragma is found.
    """
    for line in spec_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("@promplet"):
            break
        # Found the pragma — extract surface: value if present
        rest = stripped[len("@promplet") :]
        for m in _KV_RE.finditer(rest):
            if m.group("key").lower() == "surface":
                return m.group("value").lower()
        return None
    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

_SUPPORTED_SURFACES = frozenset({"canonical", "markdown"})


def lower_weavemark_surface(spec_text: str) -> SurfaceLoweringResult:
    """Detect the declared surface and lower *spec_text* if needed.

    This is the single integration point for all runtime paths (controller,
    scanner, CLI).  It must be called *before* macro/module preprocessing.

    Behaviour:
    * No ``surface:`` param → return unchanged text with ``surface="canonical"``.
    * ``surface: canonical`` → identity, same result.
    * ``surface: markdown`` → run the Markdown adapter.
    * Unknown surface → return an error result without modifying the text.
    """
    surface = parse_surface_pragma(spec_text)
    if surface is None or surface == "canonical":
        return SurfaceLoweringResult(text=spec_text, surface="canonical")

    if surface not in _SUPPORTED_SURFACES:
        return SurfaceLoweringResult(
            text=spec_text,
            surface=surface,
            errors=[
                f"Unknown surface '{surface}'. "
                f"Supported surfaces: {sorted(_SUPPORTED_SURFACES)}."
            ],
        )

    adapter = _get_adapter(surface)
    if adapter is None:
        return SurfaceLoweringResult(
            text=spec_text,
            surface=surface,
            errors=[
                f"Surface adapter '{surface}' is declared but not registered. "
                "This is a WeaveMark installation issue."
            ],
        )

    return adapter.lower(spec_text)


# ---------------------------------------------------------------------------
# Auto-register built-in adapters on import
# ---------------------------------------------------------------------------


def _register_builtins() -> None:
    from weavemark.surfaces.markdown_adapter import MarkdownSurfaceAdapter

    register_surface_adapter(MarkdownSurfaceAdapter())


_register_builtins()
