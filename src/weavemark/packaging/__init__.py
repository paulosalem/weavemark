"""Fully-in-language packaging of a pipeline's produced artifacts.

Turns ``@output file:`` artifacts and ``@package`` steps into deliverable files:
persist produced artifacts, apply packaging-instruction promplets (semantic
transformation), and convert markup deliverables to formats like PDF.
"""

from __future__ import annotations

from .convert import ConversionError, convert_file
from .persist import (
    has_persistable_artifacts,
    persist_artifact_record,
    persist_execution_artifacts,
)
from .runner import PackageResult, build_package_context, run_packages

__all__ = [
    "ConversionError",
    "PackageResult",
    "build_package_context",
    "convert_file",
    "has_persistable_artifacts",
    "persist_artifact_record",
    "persist_execution_artifacts",
    "run_packages",
]
