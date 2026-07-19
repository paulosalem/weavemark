"""Functional execution-plan engine."""

from __future__ import annotations

from ellements.execution import OnStepCallback, StepRecord

from ..compilation.result import CompositionResult
from .base import ArtifactCallback, BaseEngine, ExecutionResult, RuntimeConfig


class FunctionalEngine(BaseEngine):
    """Return the executable functional document and plan without running effects."""

    async def execute(
        self,
        result: CompositionResult,
        config: RuntimeConfig | None = None,
        on_step: OnStepCallback | None = None,
        on_artifact: ArtifactCallback | None = None,
    ) -> ExecutionResult:
        """Materialize the functional plan for a host runtime to execute."""

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
