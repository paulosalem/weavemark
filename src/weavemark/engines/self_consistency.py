"""Self-consistency engine — wraps WeaveMark SelfConsistencyStrategy."""

from __future__ import annotations

from typing import Optional

from ellements.execution import OnStepCallback, SelfConsistencyStrategy

from ..compilation.result import CompositionResult
from .base import ArtifactCallback, BaseEngine, ExecutionResult, RuntimeConfig


class SelfConsistencyEngine(BaseEngine):
    """Run prompt N times and aggregate via voting or LLM judge."""

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult:
        self._require_text_only(result, "self-consistency")
        strategy = SelfConsistencyStrategy()
        sr = await strategy.execute(
            result.prompts or {"default": result.composed_prompt},
            self.client,
            tools=result.tools or None,
            config=self._build_strategy_config(result, config, on_step),
        )
        return self._wrap_result(sr, result, config)
