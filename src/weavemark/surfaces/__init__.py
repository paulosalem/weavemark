"""WeaveMark surface adapters.

A *surface adapter* deterministically lowers host-specific authoring syntax
into canonical WeaveMark before macro expansion, scanning, and composition.

The canonical form is ordinary ``@directive``-based WeaveMark.  Surface
adapters are **entirely optional** and activated only by an explicit
``surface:`` key on the ``@promplet`` pragma::

    @promplet version: 0.8 surface: markdown

Pipeline::

    raw source
      → surface adapter (lowers host-specific sugar to canonical WeaveMark)
      → module/macro preprocessing
      → scanner / composer / runtime

New surfaces (HTML, Org-mode, …) implement :class:`SurfaceAdapter` and
register themselves via :func:`register_surface_adapter`.
"""

from __future__ import annotations

from weavemark.surfaces.base import (
    SurfaceAdapter,
    SurfaceLoweringResult,
    lower_weavemark_surface,
    parse_surface_pragma,
    register_surface_adapter,
)

__all__ = [
    "SurfaceAdapter",
    "SurfaceLoweringResult",
    "lower_weavemark_surface",
    "parse_surface_pragma",
    "register_surface_adapter",
]
