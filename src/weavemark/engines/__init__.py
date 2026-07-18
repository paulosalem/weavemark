"""WeaveMark execution engines.

Thin wrappers that delegate to WeaveMark strategies, wiring
CompilationResult → strategy → ExecutionResult.
"""

from .base import (
    ArtifactCallback,
    BaseEngine,
    Engine,
    ExecutionResult,
    PromptConfig,
    RuntimeConfig,
    call_engine_execute,
    resolve_runtime_engine_name,
)
from .collaborative import (
    AgentHandoffEditCallback,
    AgentHandoffTurn,
    CollaborativeEngine,
)
from .fslm import FSLMEngine
from .reflection import ReflectionEngine
from .registry import resolve_engine
from .self_consistency import SelfConsistencyEngine
from .single_call import SingleCallEngine
from .tree_of_thought import SimplifiedTreeOfThoughtEngine, TreeOfThoughtEngine
from .weave import WeaveEngine

__all__ = [
    "ArtifactCallback",
    "BaseEngine",
    "CollaborativeEngine",
    "AgentHandoffEditCallback",
    "AgentHandoffTurn",
    "Engine",
    "ExecutionResult",
    "FSLMEngine",
    "PromptConfig",
    "ReflectionEngine",
    "RuntimeConfig",
    "SelfConsistencyEngine",
    "SimplifiedTreeOfThoughtEngine",
    "SingleCallEngine",
    "TreeOfThoughtEngine",
    "WeaveEngine",
    "call_engine_execute",
    "resolve_engine",
    "resolve_runtime_engine_name",
]
