"""Tree-of-thought engines.

Two engines are exposed for explicit spec wiring:

* :class:`TreeOfThoughtEngine`           — full search (default ``mode='beam'``)
* :class:`SimplifiedTreeOfThoughtEngine` — generate → evaluate → synthesize
  (``mode='simple'``)

Both engines delegate to the single ``ellements.execution.TreeOfThoughtStrategy``
configured with the appropriate ``mode``.
"""

from __future__ import annotations

from typing import Optional

from ellements.execution import OnStepCallback, TreeOfThoughtStrategy

from ..compilation.result import CompositionResult
from .base import ArtifactCallback, BaseEngine, ExecutionResult, RuntimeConfig


class TreeOfThoughtEngine(BaseEngine):
    """Full BFS/DFS tree-of-thought engine (canonical Yao et al. 2023)."""

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult:
        self._require_text_only(result, "tree-of-thought")
        strategy = TreeOfThoughtStrategy()
        sr = await strategy.execute(
            result.prompts or {"default": result.composed_prompt},
            self.client,
            tools=result.tools or None,
            config=self._build_strategy_config(result, config, on_step),
        )
        return self._wrap_result(sr, result, config)


class SimplifiedTreeOfThoughtEngine(BaseEngine):
    """Simplified generate → evaluate → synthesize engine.

    Uses the same :class:`TreeOfThoughtStrategy` but injects
    ``mode='simple'`` into the strategy config.
    """

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult:
        self._require_text_only(result, "simplified-tree-of-thought")
        strategy = TreeOfThoughtStrategy()
        strategy_config = self._build_strategy_config(result, config, on_step)
        strategy_config.setdefault("mode", "simple")
        sr = await strategy.execute(
            result.prompts or {"default": result.composed_prompt},
            self.client,
            tools=result.tools or None,
            config=strategy_config,
        )
        return self._wrap_result(sr, result, config)
