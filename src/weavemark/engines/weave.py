"""Weave execution-plan engine."""

from __future__ import annotations

from typing import Optional

from ellements.execution import OnStepCallback, StepRecord

from ..compilation.result import CompositionResult
from .base import ArtifactCallback, BaseEngine, ExecutionResult, RuntimeConfig


class WeaveEngine(BaseEngine):
    """Return the executable weave document and plan without running effects."""

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult:
        """Materialize the weave plan for a host runtime to execute."""

        metadata = {
            "status": "planned",
            "execution": result.execution,
            "bindings": result.bindings,
            "effect_execution": "host-runtime-required",
        }
        step = StepRecord(
            name="plan",
            prompt_key="default",
            response=result.composed_prompt,
            metadata=metadata,
        )
        if on_step is not None:
            on_step(step)
        return ExecutionResult(
            output=result.composed_prompt,
            steps=[step],
            metadata=metadata,
        )
