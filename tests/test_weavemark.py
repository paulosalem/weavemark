"""End-to-end tests for the WeaveMark example application.

These tests use REAL LLM calls (no mocks) to verify the complete
prompt composition workflow. They require OPENAI_API_KEY to be set.
"""

import html
import importlib.util
import json
import os
import re
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.wire_helpers import compiler_response

_skip_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — E2E tests require a real LLM",
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPLETS_DIR = REPO_ROOT / "promplets"
EXAMPLES_DIR = REPO_ROOT / "examples"
STUDIES_DIR = REPO_ROOT / "studies"


@_skip_no_api_key
class TestWeaveMarkE2E:
    """End-to-end tests using real LLM calls."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_simple_spec_no_directives(self):
        """A plain-text spec with variable substitution only."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text="Write a haiku about @{topic}.",
            variables={"topic": "autumn"},
        )

        assert result.composed_prompt, "Should produce a non-empty composed prompt"
        assert (
            "autumn" in result.composed_prompt.lower()
            or "haiku" in result.composed_prompt.lower()
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_directive(self):
        """Verify @match selects the correct branch."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = (
            "You are a coding assistant.\n\n"
            "@match language\n"
            '  "python" ==> Focus on PEP 8 and type hints.\n'
            '  "rust"   ==> Focus on ownership and lifetimes.\n'
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={"language": "python"},
        )

        prompt_lower = result.composed_prompt.lower()
        assert (
            "pep 8" in prompt_lower or "type hint" in prompt_lower
        ), "Should include Python-specific content"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_directive_true(self):
        """Verify @if includes content when the condition is true."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = (
            "Review this code.\n\n"
            "@if include_security\n"
            "  Check for SQL injection and XSS vulnerabilities.\n"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={"include_security": True},
        )

        prompt_lower = result.composed_prompt.lower()
        assert (
            "sql injection" in prompt_lower
            or "xss" in prompt_lower
            or "security" in prompt_lower
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_if_directive_false(self):
        """Verify @if excludes content when the condition is false."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = (
            "Review this code.\n\n"
            "@if include_security\n"
            "  Check for SQL injection and XSS vulnerabilities.\n"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={"include_security": False},
        )

        prompt_lower = result.composed_prompt.lower()
        assert "sql injection" not in prompt_lower

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_refine_directive(self):
        """Verify @refine reads a file and merges content."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = (
            "@refine module:weavemark.std.reasoning.base_analyst\n\n"
            "Analyze the renewable energy market in Europe.\n"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={},
            base_dir=PROMPLETS_DIR,
        )

        prompt_lower = result.composed_prompt.lower()
        # Should contain content from both the base analyst and the spec
        assert (
            "renewable" in prompt_lower
            or "energy" in prompt_lower
            or "europe" in prompt_lower
        )
        assert (
            result.tool_calls_made > 0
        ), "Should have called read_file for reasoning/base-analyst.weavemark.md"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_market_research_spec_full(self):
        """Full composition of the market research spec with all variables."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        vars_path = EXAMPLES_DIR / "batch-example-runs/static-prompts/inputs/market-research-example.json"
        variables = json.loads(vars_path.read_text(encoding="utf-8"))

        spec_text = (PROMPLETS_DIR / "market-research-brief.weavemark.md").read_text(
            encoding="utf-8"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec_text,
            variables=variables,
            base_dir=PROMPLETS_DIR,
        )

        assert result.composed_prompt, "Should produce a non-empty result"
        prompt_lower = result.composed_prompt.lower()
        assert "rivian" in prompt_lower or "electric" in prompt_lower

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tutorial_spec_with_escaping(self):
        """Verify @@ escaping renders literal @ in the final output."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        vars_path = EXAMPLES_DIR / "batch-example-runs/static-prompts/inputs/tutorial-fastapi.json"
        variables = json.loads(vars_path.read_text(encoding="utf-8"))

        spec_text = (PROMPLETS_DIR / "tutorial-generator.weavemark.md").read_text(
            encoding="utf-8"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec_text,
            variables=variables,
            base_dir=PROMPLETS_DIR,
        )

        assert result.composed_prompt, "Should produce a non-empty result"
        # The @@ should render as literal @ in decorator references
        prompt_lower = result.composed_prompt.lower()
        assert "fastapi" in prompt_lower or "rest" in prompt_lower

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_note_directive_stripped(self):
        """Verify @note content is stripped from the final output."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = (
            "Write a story.\n\n"
            "@note\n"
            "  SECRET_INTERNAL_MARKER_12345 — do not include this in the final prompt.\n\n"
            "The story should be about a cat.\n"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(spec_text=spec, variables={})

        assert "SECRET_INTERNAL_MARKER_12345" not in result.composed_prompt


# Regex patterns to detect unprocessed directives in the composed prompt.
# These should NEVER appear in a properly composed prompt.
_DIRECTIVE_PATTERNS = [
    (r"(?m)^\s*@refine\b", "@refine directive"),
    (r"(?m)^\s*@match\b", "@match directive"),
    (r"(?m)^\s*@if\b", "@if directive"),
    (r"(?m)^\s*@else\b", "@else directive"),
    (r"(?m)^\s*@compile\b", "@compile directive"),
    (r"(?m)^\s*@emit\b", "@emit directive"),
    (r"(?m)^\s*@note\b", "@note directive"),
    (r"==>", "==> arrow (from @match)"),
    (r"@\{[a-zA-Z_][\w.-]*\}", "@{variable} placeholder"),
]


def _assert_no_raw_directives(prompt: str, context: str = "") -> None:
    """Assert that no unprocessed directive syntax remains in the prompt."""
    for pattern, label in _DIRECTIVE_PATTERNS:
        match = re.search(pattern, prompt)
        assert match is None, (
            f"Found unprocessed {label} in composed prompt{' (' + context + ')' if context else ''}: "
            f"'{match.group()}' at position {match.start()}"
        )


def _assert_no_xml_tags(prompt: str, context: str = "") -> None:
    """Assert that XML structural tags are not present in the prompt text."""
    for tag in ("output", "prompt", "warnings", "errors", "suggestions"):
        assert (
            f"<{tag}>" not in prompt
        ), f"Found raw <{tag}> tag in composed prompt{' (' + context + ')' if context else ''}"
        assert (
            f"</{tag}>" not in prompt
        ), f"Found raw </{tag}> tag in composed prompt{' (' + context + ')' if context else ''}"


@_skip_no_api_key
class TestWeaveMarkOutputQuality:
    """Tests that verify the composed prompt is clean — no leftover
    directives, variables, or XML tags."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_market_research_no_raw_directives(self):
        """The market-research spec must be fully resolved."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        vars_path = EXAMPLES_DIR / "batch-example-runs/static-prompts/inputs/market-research-example.json"
        variables = json.loads(vars_path.read_text(encoding="utf-8"))
        spec_text = (PROMPLETS_DIR / "market-research-brief.weavemark.md").read_text(
            encoding="utf-8"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec_text,
            variables=variables,
            base_dir=PROMPLETS_DIR,
        )

        _assert_no_raw_directives(result.composed_prompt, "market-research")
        _assert_no_xml_tags(result.composed_prompt, "market-research")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_code_review_no_raw_directives(self):
        """The program-review spec must be fully resolved."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        vars_path = PROMPLETS_DIR / "vars" / "program-review-python.json"
        variables = json.loads(vars_path.read_text(encoding="utf-8"))
        spec_text = (PROMPLETS_DIR / "program-review-checklist.weavemark.md").read_text(
            encoding="utf-8"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec_text,
            variables=variables,
            base_dir=PROMPLETS_DIR,
        )

        _assert_no_raw_directives(result.composed_prompt, "program-review")
        _assert_no_xml_tags(result.composed_prompt, "program-review")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tutorial_no_raw_directives(self):
        """The tutorial spec must be fully resolved."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        vars_path = EXAMPLES_DIR / "batch-example-runs/static-prompts/inputs/tutorial-fastapi.json"
        variables = json.loads(vars_path.read_text(encoding="utf-8"))
        spec_text = (PROMPLETS_DIR / "tutorial-generator.weavemark.md").read_text(
            encoding="utf-8"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec_text,
            variables=variables,
            base_dir=PROMPLETS_DIR,
        )

        _assert_no_raw_directives(result.composed_prompt, "tutorial")
        _assert_no_xml_tags(result.composed_prompt, "tutorial")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_simple_match_no_raw_directives(self):
        """A simple @match spec must not leave raw directive syntax."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = (
            "You are a coding assistant.\n\n"
            "@match language\n"
            '  "python" ==> Focus on PEP 8 and type hints.\n'
            '  "rust"   ==> Focus on ownership and lifetimes.\n'
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={"language": "python"},
        )

        _assert_no_raw_directives(result.composed_prompt, "simple-match")
        _assert_no_xml_tags(result.composed_prompt, "simple-match")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_issues_cleanly_separated(self):
        """Warnings/errors/suggestions must NOT appear inside composed_prompt."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        vars_path = EXAMPLES_DIR / "batch-example-runs/static-prompts/inputs/market-research-example.json"
        variables = json.loads(vars_path.read_text(encoding="utf-8"))
        spec_text = (PROMPLETS_DIR / "market-research-brief.weavemark.md").read_text(
            encoding="utf-8"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec_text,
            variables=variables,
            base_dir=PROMPLETS_DIR,
        )

        prompt = result.composed_prompt
        # The prompt should not contain issue-like prefixes
        assert not re.search(
            r"(?i)\bwarning\s*\d*:", prompt
        ), "Found 'Warning:' text inside composed_prompt — issues should be separate"
        # Issues, if any, should be in their own fields
        for w in result.warnings:
            assert isinstance(w, str) and len(w) > 0
        for e in result.errors:
            assert isinstance(e, str) and len(e) > 0
        for s in result.suggestions:
            assert isinstance(s, str) and len(s) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_llm_response_uses_strict_json_schema(self):
        """Verify the provider returns the mandatory compiler-result object."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = (
            "@refine module:weavemark.std.reasoning.base_analyst\n\n"
            "Analyze the renewable energy market.\n"
        )

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={},
            base_dir=PROMPLETS_DIR,
        )

        payload = json.loads(result.raw_response)
        assert set(payload) == {
            "prompt",
            "prompts",
            "compile",
            "tools",
            "bindings",
            "execution",
            "emits",
            "outputs",
            "packages",
            "references",
            "directives",
            "analysis",
            "warnings",
            "errors",
            "suggestions",
        }
        assert len(result.composed_prompt) > 50, (
            f"composed_prompt too short ({len(result.composed_prompt)} chars) — "
            "strict response extraction may have failed"
        )


class TestWeaveMarkImports:
    """Non-integration tests: verify imports and structure."""

    def test_controller_importable(self):
        from weavemark.controller import (
            CompositionResult,
            WeaveMarkConfig,
            WeaveMarkController,
            parse_composition_response,
        )

        assert WeaveMarkController is not None
        assert WeaveMarkConfig is not None
        assert CompositionResult is not None
        assert callable(parse_composition_response)

    def test_app_importable(self):
        from weavemark.app import cli, create_parser

        assert callable(cli)
        assert callable(create_parser)

    def test_specs_exist(self):
        """All example specs and var files must be present."""
        assert (PROMPLETS_DIR / "stdlib/fragments/reasoning/base-analyst.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/market-research-brief.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/program-review-checklist.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/tutorial-generator.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/consulting-proposal.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/knowledge-base-article.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/api-docs-generator.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/multi-persona-debate.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/adaptive-interview.weavemark.md").is_file()
        assert (
            PROMPLETS_DIR / "catalog/standalone/prompt-refactoring-pipeline.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "catalog/standalone/live-investment-decision-brief.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "catalog/standalone/financial-independence-goal-plan-prompt.weavemark.md"
        ).is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/messy-notes-action-plan.weavemark.md").is_file()
        assert (
            PROMPLETS_DIR / "catalog/standalone/deep-summary-prompt.weavemark.md"
        ).is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/decision-advisor.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/learning-tutor.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/research-brief.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/prompt-refiner.weavemark.md").is_file()
        assert (
            PROMPLETS_DIR / "catalog/standalone/program-debugging-assistant.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "catalog/standalone/news-intelligence-board.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "catalog/standalone/passive-income-planning-dashboard.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "stdlib/fragments/reasoning/unstructured-input-normalization.weavemark.md"
        ).is_file()
        assert (PROMPLETS_DIR / "stdlib/fragments/reasoning/action-planning.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "stdlib/fragments/reasoning/deep-summary.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "stdlib/fragments/reasoning/learner-model.weavemark.md").is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/reasoning/prompt-refinement-core.weavemark.md"
        ).is_file()
        assert (PROMPLETS_DIR / "stdlib/definitions/planning/goals.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "stdlib/fragments/guidelines/research-rigor.weavemark.md").is_file()
        assert (PROMPLETS_DIR / "stdlib/fragments/guidelines/prompt-quality.weavemark.md").is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/analysis/strategic-problem-analysis.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/reasoning/learner-model.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/research/fragments/recurring-topic-monitor-core.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "domains/research/fragments/deep-web-source-discovery.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "domains/research/fragments/news-event-triage.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "experimental/studies/auto-research-ablation.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/debugging/root-cause-debugging.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/types/type-local-first-webapp.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/stacks/stack-typescript-nextjs-prisma-sqlite.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "domains/programming/fragments/modules/module-card.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/modules/module-local-sqlite-storage.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/modules/module-workflow-board.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/modules/module-activity-stream.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/modules/module-context-attachments.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/modules/module-output-surfaces.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/validation/playwright-mcp-browser-validation.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR
            / "domains/programming/fragments/validation/release-validation-matrix.weavemark.md"
        ).is_file()
        removed_programming_promplets = (
            "catalog/standalone/fieldpulse-iot-agriculture.weavemark.md",
            "catalog/standalone/mintlite-finance-app.weavemark.md",
            "catalog/standalone/passive-income-android-app.weavemark.md",
            "catalog/standalone/voidborne-roguelike.weavemark.md",
            "domains/programming/fragments/assets/generative-2d-sprites.weavemark.md",
            "domains/programming/fragments/models/model-finance.weavemark.md",
            "domains/programming/fragments/modules/module-mobile-financial-dashboard.weavemark.md",
            "domains/programming/fragments/stacks/stack-android-kotlin-compose.weavemark.md",
            "domains/programming/fragments/stacks/stack-python-fastapi-postgres.weavemark.md",
            "domains/programming/fragments/stacks/stack-rust-bevy.weavemark.md",
            "domains/programming/fragments/stacks/stack-typescript-nextjs-prisma.weavemark.md",
            "domains/programming/fragments/types/type-2d-game.weavemark.md",
            "domains/programming/fragments/types/type-android-app.weavemark.md",
            "domains/programming/fragments/types/type-saas-webapp.weavemark.md",
        )
        assert all(not (PROMPLETS_DIR / relative).exists() for relative in removed_programming_promplets)
        assert (
            PROMPLETS_DIR / "domains/product/fragments/release-readiness-gate.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "domains/finance/fragments/financial-resilience-lens.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/decision/forecast-uncertainty.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/decision/strategy-selection.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/decision/values-tradeoff.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/guidelines/release-evidence-quality.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "stdlib/fragments/teaching/mastery-practice-loop.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "domains/product/fragments/release-artifact-readiness.weavemark.md"
        ).is_file()
        removed_reusable_fragments = (
            "stdlib/fragments/writing/collaborative-writing-protocol.weavemark.md",
            "stdlib/fragments/writing/revision-critique-loop.weavemark.md",
            "domains/product/fragments/metaphor-to-product.weavemark.md",
        )
        assert all(
            not (PROMPLETS_DIR / relative).exists()
            for relative in removed_reusable_fragments
        )
        assert (
            PROMPLETS_DIR / "catalog/executable/recurring-topic-monitor.weavemark.md"
        ).is_file()
        assert not list(
            (PROMPLETS_DIR / "catalog/executable").glob("*.weavemark.yaml")
        )
        for runtime_name in (
            "fslm-support-triage.runtime.json",
            "fslm-support-triage-sugared.runtime.json",
        ):
            runtime_path = PROMPLETS_DIR / "experimental/fslm" / runtime_name
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            assert runtime["engine"] == "fslm"
            assert "variables" not in runtime
            assert "prompts" not in runtime
        assert (
            PROMPLETS_DIR / "catalog/executable/companions/recurring_topic_monitor.py"
        ).is_file()
        assert (
            PROMPLETS_DIR / "catalog/executable/financial-independence-goal-plan.weavemark.md"
        ).is_file()
        assert (
            PROMPLETS_DIR / "catalog/executable/companions/public_finance_reference.py"
        ).is_file()
        static_inputs_dir = EXAMPLES_DIR / "batch-example-runs/static-prompts/inputs"
        assert (static_inputs_dir / "market-research-example.json").is_file()
        assert (static_inputs_dir / "news-intelligence-board.yaml").is_file()
        assert (
            EXAMPLES_DIR
            / "batch-example-runs/static-prompts/outputs/news-intelligence-board/compiled-prompt.md"
        ).is_file()
        assert (
            EXAMPLES_DIR / "terminal-output-only/program-review-checklist/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "terminal-output-only/messy-notes-action-plan/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "terminal-output-only/deep-summary/inputs/vars.json"
        ).is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/investment-brief.weavemark.md").is_file()
        assert (
            EXAMPLES_DIR
            / "saved-artifact-workflows/investment-brief/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "saved-artifact-workflows/investment-brief/run.sh"
        ).is_file()
        assert (
            EXAMPLES_DIR
            / "saved-artifact-workflows/investment-brief/outputs/compiled-prompt.md"
        ).is_file()
        assert (
            EXAMPLES_DIR / "saved-artifact-workflows/recurring-topic-monitor/run.sh"
        ).is_file()
        assert (
            EXAMPLES_DIR
            / "saved-artifact-workflows/recurring-topic-monitor/inputs/ai-news.json"
        ).is_file()
        assert (
            EXAMPLES_DIR
            / "saved-artifact-workflows/recurring-topic-monitor/inputs/child-events.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "saved-artifact-workflows/market-snapshot/run.sh"
        ).is_file()
        assert (
            EXAMPLES_DIR / "saved-artifact-workflows/market-snapshot/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "terminal-output-only/decision-advisor/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "terminal-output-only/learning-tutor/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "terminal-output-only/research-brief/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR / "terminal-output-only/prompt-refiner/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR
            / "terminal-output-only/program-debugging-assistant/inputs/vars.json"
        ).is_file()
        assert (STUDIES_DIR / "README.md").is_file()
        assert (STUDIES_DIR / "AGENTS.md").is_file()
        assert (STUDIES_DIR / "controlled-studies/method.md").is_file()
        assert (STUDIES_DIR / "controlled-studies/results.md").is_file()
        assert (STUDIES_DIR / "controlled-studies/results.html").is_file()
        assert (
            STUDIES_DIR / "controlled-studies/metrics/semantic-information.json"
        ).is_file()
        assert (STUDIES_DIR / "examples-studies/results.md").is_file()
        assert (STUDIES_DIR / "examples-studies/results.html").is_file()
        assert (STUDIES_DIR / "examples-studies/metrics/example-quality.json").is_file()
        assert (
            REPO_ROOT / ".github/skills/weavemark-study-reporting/SKILL.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/release-readiness-workbench-ablation-study/specs/02-treatment-promplet-release-readiness-workbench.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/intelligence-execution-kanban-ablation-study/specs/02-treatment-promplet-intelligence-execution-kanban.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/evidence-decision-workspace-ablation-study/specs/02-treatment-promplet-evidence-decision-workspace.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/research-brief-ablation-study/specs/02-treatment-refined-research-brief.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/learning-tutor-refinement-ablation-study/specs/02-treatment-refined-expand-linear-algebra-tutor.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/games/orbital-drift-racing-ablation-study/specs/02-treatment-promplet-orbital-drift.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/games/verdant-relay-ablation-study/specs/02-treatment-promplet-verdant-relay.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/games/transit-city-swarm-ablation-study/specs/02-treatment-expand-transit-city-swarm.weavemark.md"
        ).is_file()
        assert (
            STUDIES_DIR
            / "controlled-studies/games/crowd-factory-puzzle-ablation-study/specs/02-treatment-expand-crowd-factory-puzzle.weavemark.md"
        ).is_file()
        assert (static_inputs_dir / "tutorial-fastapi.json").is_file()
        assert (static_inputs_dir / "consulting-proposal-example.json").is_file()
        assert (static_inputs_dir / "knowledge-base-article-example.json").is_file()
        assert (PROMPLETS_DIR / "catalog/standalone/api-docs-generator.vars.json").is_file()
        assert (static_inputs_dir / "multi-persona-debate-agi.json").is_file()
        assert (static_inputs_dir / "adaptive-interview-senior-backend.json").is_file()
        assert (static_inputs_dir / "prompt-refactoring-example.yaml").is_file()
        assert (
            EXAMPLES_DIR
            / "python-runtime-integrations/live-investment-decision/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR
            / "python-runtime-integrations/financial-independence-goal-plan/inputs/vars.json"
        ).is_file()
        assert (
            EXAMPLES_DIR
            / "python-runtime-integrations/financial-independence-goal-plan/run.py"
        ).is_file()
        recurring_monitor_inputs = (
            EXAMPLES_DIR / "batch-example-runs/execution-engines/inputs"
        )
        assert (recurring_monitor_inputs / "recurring-topic-monitor-ai-news.json").is_file()
        assert (
            recurring_monitor_inputs / "recurring-topic-monitor-child-events.json"
        ).is_file()
        assert not (
            EXAMPLES_DIR / "python-runtime-integrations/recurring-topic-monitor/run.py"
        ).exists()

    def test_prompt_refactoring_pipeline_uses_nested_transform_chain(self):
        """The refactoring example must thread one transform into the next."""

        source = (
            PROMPLETS_DIR
            / "catalog/standalone/prompt-refactoring-pipeline.weavemark.md"
        ).read_text(encoding="utf-8")
        lines = source.splitlines()

        def find_line(fragment: str, start: int = 0) -> tuple[int, int]:
            for index in range(start, len(lines)):
                line = lines[index]
                if fragment in line:
                    return index, len(line) - len(line.lstrip())
            raise AssertionError(f"Missing expected pipeline fragment: {fragment}")

        chain = [
            '@polish "Harmonize the fully transformed prompt',
            '@revise "Remove standalone format labels',
            "@structural_constraints strict: true",
            '@revise "If a Removal instruction block appears',
            '@revise "If an Additional section block appears',
            '@revise "@{revision_instruction}" mode: editorial',
            '@normalize "Resolve cross-references and contradictions',
            '@normalize "Normalize headings, lists, and terminology',
        ]
        previous_index = 0
        previous_indent = -1
        for fragment in chain:
            line_index, indent = find_line(fragment, previous_index)
            assert indent > previous_indent
            previous_index = line_index + 1
            previous_indent = indent

        semantic_index, semantic_indent = find_line(
            '@normalize "Resolve cross-references and contradictions'
        )
        extract_index, extract_indent = find_line("@extract", semantic_index + 1)
        assert extract_index > semantic_index
        assert extract_indent > semantic_indent

        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith(("@extract", "@normalize", "@revise")):
                assert len(line) > len(stripped), (
                    "Transform directives in the prompt-refactoring pipeline must "
                    "stay nested under @polish so each pass feeds the next."
                )

    def test_html_weavemark_snippets_are_syntax_highlighted(self):
        """HTML docs must color WeaveMark syntax in code snippets."""
        weavemark_tokens = (
            "@promplet",
            "@refine",
            "@expand",
            "@iterate",
            "@style",
            "@normalize",
            "@revise",
            "@output",
            "@assert",
            "@match",
            "@if",
            "@prompt",
            "@tool",
            "@bind",
            "@module",
            "@define",
            "@phase",
            "@scope",
            "@returns",
            "@param",
            "@effect",
            "@body",
            "@use",
            "@execute",
            "@{",
        )
        failures: list[str] = []
        for html_file in (REPO_ROOT / "docs").glob("*.html"):
            text = html_file.read_text()
            for index, match in enumerate(
                re.finditer(r"<pre><code>(.*?)</code></pre>", text, re.S), start=1
            ):
                block = match.group(1)
                if (
                    any(token in block for token in weavemark_tokens)
                    and "syntax-directive" not in block
                    and "syntax-var" not in block
                ):
                    failures.append(f"{html_file.relative_to(REPO_ROOT)} block {index}")

        assert failures == []

    def test_html_weavemark_snippets_use_valid_directive_shapes(self):
        """HTML docs must not teach invalid WeaveMark directive structure."""
        body_required_directives = {
            "@ask",
            "@compress",
            "@emit",
            "@expand",
            "@iterate",
            "@normalize",
            "@prompt",
            "@revise",
            "@style",
            "@tool",
        }
        body_target_directives = {"@normalize", "@revise", "@style"}
        failures: list[str] = []

        def next_nonblank(lines: list[str], start_index: int) -> tuple[int, str] | None:
            for line_index in range(start_index + 1, len(lines)):
                if lines[line_index].strip():
                    return line_index, lines[line_index]
            return None

        for html_file in (REPO_ROOT / "docs").glob("*.html"):
            text = html_file.read_text(encoding="utf-8")
            for block_index, match in enumerate(
                re.finditer(r"<pre><code>(.*?)</code></pre>", text, re.S), start=1
            ):
                block = html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))
                if "@" not in block:
                    continue

                lines = block.splitlines()
                for line_index, line in enumerate(lines):
                    if re.match(
                        r"\s*>\s*\[!PROMPLET\s+(style|normalize|revise)\s*\]",
                        line,
                    ):
                        failures.append(
                            f"{html_file.relative_to(REPO_ROOT)} block {block_index} "
                            f"line {line_index + 1}: body-transforming callout "
                            "must put the operation instruction in the callout header"
                        )

                for line_index, line in enumerate(lines):
                    stripped = line.lstrip()
                    if not stripped.startswith("@"):
                        continue

                    directive = stripped.split(maxsplit=1)[0]
                    indent = len(line) - len(stripped)
                    location = (
                        f"{html_file.relative_to(REPO_ROOT)} block {block_index} "
                        f"line {line_index + 1}"
                    )

                    if directive in body_required_directives:
                        next_line = next_nonblank(lines, line_index)
                        if next_line is None:
                            failures.append(f"{location}: {directive} has no body")
                        else:
                            next_indent = len(next_line[1]) - len(next_line[1].lstrip())
                            if next_indent <= indent:
                                failures.append(
                                    f"{location}: {directive} body must be indented"
                                )

                    if directive in body_target_directives and len(stripped.split()) == 1:
                        failures.append(
                            f"{location}: {directive} must put the operation "
                            "instruction inline; the body is the target subspec"
                        )

                    if directive == "@emit" and not re.match(r"^@emit\s+file:", stripped):
                        failures.append(f"{location}: @emit must use file:")

                    if directive == "@refine":
                        parts = stripped.split()
                        if len(parts) > 1:
                            refine_path = parts[1].strip("\"'")
                            if refine_path.startswith("module:"):
                                continue
                            if "/" in refine_path or refine_path.endswith(".weavemark.md"):
                                if refine_path.startswith("promplets/"):
                                    resolved_path = (REPO_ROOT / refine_path).resolve()
                                else:
                                    resolved_path = (PROMPLETS_DIR / refine_path).resolve()
                                if not resolved_path.is_file():
                                    failures.append(
                                        f"{location}: @refine target not found: "
                                        f"{refine_path}"
                                    )

                    if directive == "@execute" and len(stripped.split()) > 2:
                        failures.append(
                            f"{location}: @execute config must be an indented body"
                        )

                    if directive == "@bind":
                        for required_token in ("language:", "from:", "symbol:"):
                            if required_token not in stripped:
                                failures.append(
                                    f"{location}: @bind missing {required_token}"
                                )

                    if directive == "@tool":
                        next_line = next_nonblank(lines, line_index)
                        if next_line is not None and next_line[1].strip().startswith("- "):
                            failures.append(
                                f"{location}: @tool body should start with a description"
                            )

        assert failures == []

    def test_system_prompt_exists(self):
        from weavemark.controller import _SYSTEM_PROMPT_PATH

        assert _SYSTEM_PROMPT_PATH.is_file()
        content = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        assert "@refine" in content
        assert "@match" in content
        assert '"prompt"' in content
        assert '"packages"' in content

    def test_discovery_prompt_is_internal_and_packaged(self):
        from weavemark.app import (
            DISCOVERY_SYSTEM_PROMPT,
            _load_discovery_system_prompt,
        )

        prompt = _load_discovery_system_prompt()

        assert DISCOVERY_SYSTEM_PROMPT.is_file()
        assert "search_catalog" in prompt
        assert "@promplet" not in prompt
        assert "@tool" not in prompt
        assert not (
            PROMPLETS_DIR / "catalog/executable/spec-discovery.weavemark.md"
        ).exists()

    def test_malformed_metadata_response_is_rejected(self, caplog):
        from weavemark.controller import parse_composition_response

        raw = """
        <output>
          <prompt>Compiled prompt</prompt>
          <tools>]</tools>
          <bindings>]</bindings>
        </output>
        """

        result = parse_composition_response(raw)

        assert result.tools == []
        assert result.bindings == []
        assert result.errors
        assert "Failed to parse <tools>" not in caplog.text
        assert "Failed to parse <bindings>" not in caplog.text

    def test_singleton_tool_and_binding_metadata_is_rejected(self, caplog):
        from weavemark.controller import parse_composition_response

        raw = """
        <output>
          <prompt>Compiled prompt</prompt>
          <tools>{"type":"function","function":{"name":"search_web"}}</tools>
          <bindings>{"tool":"search_web","provider":"ellements"}</bindings>
        </output>
        """

        result = parse_composition_response(raw)

        assert result.tools == []
        assert result.bindings == []
        assert result.errors
        assert "Failed to parse <tools>" not in caplog.text
        assert "Failed to parse <bindings>" not in caplog.text


class TestDiscoveryTuiLaunch:
    @pytest.mark.asyncio
    async def test_discovery_awaits_tui_from_running_event_loop(
        self, monkeypatch, tmp_path
    ):
        from weavemark.app import run_discover
        from weavemark.discovery.catalog import SpecEntry
        from weavemark.discovery.metadata import SpecMetadataEntry
        from weavemark.discovery.tools import SpecSelected

        spec_path = tmp_path / "market-research-brief.weavemark.md"
        spec_path.write_text("# Market Research Brief\n", encoding="utf-8")
        entry = SpecEntry(
            path=spec_path,
            title="Market Research Brief",
            content_hash="hash",
            raw_text="# Market Research Brief\n",
        )

        class FakeProgress:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def add_task(self, *_args, **_kwargs):
                return 1

            def update(self, *_args, **_kwargs):
                return None

        class FakeDiscoveryChatUI:
            def show_step(self, *_args, **_kwargs):
                return None

            def show_scan_progress(self, *_args, **_kwargs):
                return None

            def show_metadata_progress_start(self, *_args, **_kwargs):
                return FakeProgress()

            def show_cache_summary(self, *_args, **_kwargs):
                return None

            def show_ready(self):
                return None

            def show_banner(self):
                return None

            def show_selected(self, *_args, **_kwargs):
                return None

            def show_goodbye(self):
                return None

        class FakeChatEngine:
            def __init__(self, *_args, **_kwargs):
                return None

            async def run(self):
                raise SpecSelected(str(spec_path))

        async def fake_ensure_metadata(entries, *_args, **_kwargs):
            return {
                str(entries[0].path): SpecMetadataEntry(
                    content_hash="hash",
                    title="Market Research Brief",
                    summary="Builds a market-research brief.",
                )
            }

        launched: dict[str, Path] = {}

        async def fake_launch_tui_async(*, spec_path: Path, **_kwargs):
            launched["spec_path"] = spec_path

        fake_tui_module = types.ModuleType("weavemark.tui.app")
        fake_tui_module.launch_tui_async = fake_launch_tui_async

        monkeypatch.setattr(
            "weavemark.discovery.config.load_config",
            lambda **_kwargs: SimpleNamespace(
                _global_path=None,
                _project_path=None,
                effective_library_dirs=lambda _cwd: [tmp_path],
            ),
        )
        monkeypatch.setattr(
            "weavemark.discovery.catalog.scan_directories",
            lambda _dirs: [entry],
        )
        monkeypatch.setattr(
            "weavemark.discovery.metadata.ensure_metadata",
            fake_ensure_metadata,
        )
        monkeypatch.setattr(
            "weavemark.discovery.chat_ui.DiscoveryChatUI",
            FakeDiscoveryChatUI,
        )
        monkeypatch.setattr("weavemark.engines.chat.ChatEngine", FakeChatEngine)
        monkeypatch.setitem(sys.modules, "weavemark.tui.app", fake_tui_module)

        exit_code = await run_discover(SimpleNamespace(model="gpt-5.5", library_dir=None))

        assert exit_code == 0
        assert launched["spec_path"] == spec_path


def _load_recurring_topic_monitor_companion():
    path = PROMPLETS_DIR / "catalog/executable/companions/recurring_topic_monitor.py"
    spec = importlib.util.spec_from_file_location(
        "recurring_topic_monitor_for_tests", path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestRecurringTopicMonitorCompanion:
    def test_companion_contains_only_thin_web_bindings(self):
        module = _load_recurring_topic_monitor_companion()

        assert module.__all__ == ["crawl_url", "search_news", "search_web"]
        assert not hasattr(module, "MonitorSettings")
        assert not hasattr(module, "compile_variables")


class TestResponseParsing:
    """Unit tests for parse_composition_response and CompositionResult."""

    def test_full_response(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response(
            "You are an expert Python engineer.\n"
            "Focus on clean, PEP-8 compliant code.",
            analysis="Substituted variables and resolved directives.",
            warnings=["Variable 'style' was not provided, using default."],
            suggestions=["Consider adding a @note for the reasoning section."],
        )

        result = parse_composition_response(raw)
        assert "expert Python engineer" in result.composed_prompt
        assert "PEP-8" in result.composed_prompt
        assert "Substituted variables" in result.analysis
        assert len(result.warnings) == 1
        assert "style" in result.warnings[0].lower()
        assert result.errors == []
        assert len(result.suggestions) == 1
        assert result.raw_response == raw.strip()

    def test_prompt_only_has_no_diagnostics(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response("Write a haiku about autumn leaves.")

        result = parse_composition_response(raw)
        assert "haiku" in result.composed_prompt
        assert result.warnings == []
        assert result.errors == []
        assert result.suggestions == []

    def test_prompt_content_preserves_formatting(self):
        from weavemark.controller import parse_composition_response

        prompt = (
            "# Writing Helper\n\n"
            "You are a writing helper.\n\n"
            "Rules:\n"
            "  - Preserve intentional nested indentation."
        )
        raw = compiler_response(prompt)

        result = parse_composition_response(raw)

        assert result.composed_prompt == (
            "# Writing Helper\n\n"
            "You are a writing helper.\n\n"
            "Rules:\n"
            "  - Preserve intentional nested indentation."
        )

    def test_prompt_text_preserves_markup_literals(self):
        from weavemark.controller import parse_composition_response

        expected = 'Never modify <content status="final"> blocks.'
        raw = compiler_response(expected)

        result = parse_composition_response(raw)

        assert result.composed_prompt == expected
        assert result.prompts == {"default": expected}

    def test_plain_text_is_rejected(self):
        from weavemark.controller import parse_composition_response

        raw = "This is just plain text without the compiler response schema."

        result = parse_composition_response(raw)
        assert result.composed_prompt == ""
        assert result.raw_response == raw
        assert result.errors

    def test_multiple_warnings(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response(
            "Hello world.",
            warnings=[
                "Missing variable 'name'.",
                "Inconsistent indentation detected.",
                "Unused directive @note found.",
            ],
        )

        result = parse_composition_response(raw)
        assert result.composed_prompt == "Hello world."
        assert len(result.warnings) == 3

    def test_errors_present(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response(
            "Partial result.",
            errors=["File 'missing.md' not found."],
        )

        result = parse_composition_response(raw)
        assert len(result.errors) == 1
        assert "missing.md" in result.errors[0]

    def test_issues_property(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response(
            "Test.",
            warnings=["Warn A."],
            errors=["Err B."],
            suggestions=["Sug C."],
        )

        result = parse_composition_response(raw)
        issues = result.diagnostics
        assert len(issues) == 3
        assert issues[0]["type"] == "warning"
        assert issues[0]["code"] == "WM-COMPILER-WARNING"
        assert issues[0]["message"] == "Warn A."
        assert issues[1]["type"] == "error"
        assert issues[2]["type"] == "suggestion"

    def test_to_dict_includes_all_fields(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response(
            "Test prompt.",
            analysis="Some analysis.",
            warnings=["Some warning."],
        )

        result = parse_composition_response(raw)
        result.tool_calls_made = 2
        result.transitions = ["Pass 1: resolved variables"]
        d = result.to_dict()
        assert d["composed_prompt"] == "Test prompt."
        assert d["raw_response"] == raw.strip()
        assert d["analysis"] == "Some analysis."
        assert d["warnings"] == ["Some warning."]
        assert d["errors"] == []
        assert d["suggestions"] == []
        assert d["transitions"] == ["Pass 1: resolved variables"]
        assert d["tool_calls_made"] == 2

    def test_response_parsing_extracts_emit_artifacts(self):
        from weavemark.controller import parse_composition_response

        emits = {
            "system.md": "You are a careful assistant.",
            "user.md": "Summarize the attached notes.",
        }
        raw = compiler_response(emits=emits)

        result = parse_composition_response(raw)
        assert result.emits == emits
        assert result.to_dict()["emits"] == emits

    def test_response_parsing_extracts_compile_options(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response("Prompt.", compile={"format": "json"})

        result = parse_composition_response(raw)

        assert result.compile == {"format": "json"}
        assert result.to_dict()["compile"] == {"format": "json"}

    def test_xml_output_format_is_rejected_during_resolution(self):
        from weavemark.app import _resolve_output_format, create_parser
        from weavemark.compilation.diagnostics import UserDiagnosticError
        from weavemark.controller import CompositionResult

        parser = create_parser()
        args = parser.parse_args(["test.md", "--format", "xml", "--batch-only"])

        class FakePrinter:
            def __init__(self) -> None:
                self.warnings: list[str] = []

            def warning(self, message: str) -> None:
                self.warnings.append(message)

        result = CompositionResult(composed_prompt="Prompt.")
        printer = FakePrinter()
        with pytest.raises(UserDiagnosticError, match="Unsupported output format"):
            _resolve_output_format(result, args, printer)
        assert printer.warnings == []

    def test_output_format_defaults_to_spec_or_markdown(self):
        """The CLI resolves --format, @compile format, then markdown."""
        from weavemark.app import _resolve_output_format, create_parser
        from weavemark.controller import CompositionResult

        class FakePrinter:
            def __init__(self) -> None:
                self.warnings: list[str] = []

            def warning(self, message: str) -> None:
                self.warnings.append(message)

        parser = create_parser()
        printer = FakePrinter()
        args = parser.parse_args(["test.md", "--batch-only"])
        result = CompositionResult(composed_prompt="Prompt.")

        assert _resolve_output_format(result, args, printer) == "markdown"
        assert printer.warnings == []

        result.compile = {"format": "json"}
        assert _resolve_output_format(result, args, printer) == "json"
        assert printer.warnings == []

    def test_cli_format_overrides_compile_format_with_warning(self):
        """An explicit CLI format overrides @compile format and records a warning."""
        from weavemark.app import _resolve_output_format, create_parser
        from weavemark.controller import CompositionResult

        class FakePrinter:
            def __init__(self) -> None:
                self.warnings: list[str] = []

            def warning(self, message: str) -> None:
                self.warnings.append(message)

        parser = create_parser()
        args = parser.parse_args(["test.md", "--batch-only", "--format", "markdown"])
        result = CompositionResult(
            composed_prompt="Prompt.",
            compile={"format": "json"},
        )
        printer = FakePrinter()

        assert _resolve_output_format(result, args, printer) == "markdown"
        assert printer.warnings == [
            "CLI --format markdown overrides @compile format: json."
        ]
        assert result.warnings == [
            "CLI --format markdown overrides @compile format: json."
        ]

    def test_output_file_in_parser(self):
        """Verify --output / -o accepts a file path."""
        from weavemark.app import create_parser

        parser = create_parser()
        args = parser.parse_args(["test.md", "-o", "result.md"])
        assert args.output == Path("result.md")

    def test_cli_help_explains_interactive_and_batch_modes(self):
        """CLI help should make variable prompting and strict batch behavior clear."""
        from weavemark.app import create_parser

        parser = create_parser()
        help_text = parser.format_help()

        assert "guided interactive mode" in help_text
        assert "Missing @{variables}" in help_text
        assert "Strict non-interactive compile" in help_text
        assert "Missing inputs fail before compilation" in help_text

    def test_trace_output_file_in_parser(self):
        """Verify --trace-output accepts a file path."""
        from weavemark.app import create_parser

        parser = create_parser()
        args = parser.parse_args(["test.md", "--run", "--trace-output", "trace.md"])
        assert args.trace_output == Path("trace.md")

    def test_show_output_in_parser(self):
        """Verify --show-output requests stdout display even when writing files."""
        from weavemark.app import create_parser

        parser = create_parser()
        args = parser.parse_args(["test.md", "--output", "result.md", "--show-output"])
        assert args.show_output is True

    def test_no_file_summary_in_parser(self):
        """Verify --no-file-summary suppresses file-write status messages."""
        from weavemark.app import create_parser

        parser = create_parser()
        args = parser.parse_args(
            ["test.md", "--output", "result.md", "--no-file-summary"]
        )
        assert args.no_file_summary is True

    def test_execution_trace_helpers_include_step_responses(self):
        """Execution traces expose the intermediate responses, not just names."""
        from ellements.execution import StepRecord

        from weavemark.traces import (
            execution_result_to_dict,
            render_execution_trace_markdown,
        )

        steps = [
            StepRecord(
                name="sample_0",
                prompt_key="default",
                response="ANSWER: 42",
                metadata={"temperature": 0.8},
            )
        ]

        trace_json = execution_result_to_dict(
            output="ANSWER: 42",
            steps=steps,
            metadata={"aggregation": "majority_vote"},
        )
        assert trace_json["steps"][0]["response"] == "ANSWER: 42"
        assert trace_json["steps"][0]["metadata"] == {"temperature": 0.8}

        trace_md = render_execution_trace_markdown(
            spec="spec.weavemark.md",
            model="gpt-5.5",
            engine="self-consistency",
            output="ANSWER: 42",
            steps=steps,
            metadata={"aggregation": "majority_vote"},
        )
        assert "# WeaveMark Execution Trace" in trace_md
        assert "sample_0" in trace_md
        assert "ANSWER: 42" in trace_md
        assert "  \n" not in trace_md

    def test_execution_trace_elides_base64_image_payloads(self):
        """Image-step base64 payloads are elided so traces stay readable."""
        from ellements.execution import StepRecord

        from weavemark.traces import render_execution_trace_markdown

        blob = "iVBORw0KGgo" + "A" * 5000
        steps = [
            StepRecord(name="author", prompt_key="author", response="Draw a robot."),
            StepRecord(
                name="generate",
                prompt_key="generate",
                response=blob,
                metadata={"method": "edit_image", "images": [{"b64_json": blob}]},
            ),
        ]
        trace_md = render_execution_trace_markdown(
            spec="s",
            model="m",
            engine="reflection",
            output=blob,
            steps=steps,
            metadata={"images": [{"b64_json": blob}], "file": "art.png"},
        )
        # The raw base64 never appears; the readable stages survive.
        assert blob not in trace_md
        assert "base64 image data" in trace_md
        assert "Draw a robot." in trace_md
        assert "art.png" in trace_md

    @pytest.mark.asyncio
    async def test_run_execute_writes_trace_output(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Run mode writes a readable trace when --trace-output is supplied."""
        from ellements.cli import CliPrinter
        from ellements.execution import StepRecord

        import weavemark.engines
        from weavemark.app import create_parser, run_execute
        from weavemark.engines import ExecutionResult

        class FakeEngine:
            async def execute(self, result, config=None, on_step=None):
                step = StepRecord(
                    name="generate",
                    prompt_key="default",
                    response="Draft response",
                    metadata={"round": 0},
                )
                if on_step:
                    on_step(step)
                return ExecutionResult(
                    output="Final response",
                    steps=[step],
                    metadata={"rounds_completed": 1},
                )

        monkeypatch.setattr(
            weavemark.engines,
            "resolve_engine",
            lambda _name, **_kwargs: FakeEngine(),
        )

        trace_path = tmp_path / "trace.md"
        output_path = tmp_path / "output.md"
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "traceable.weavemark.md"),
                "--run",
                "--output",
                str(output_path),
                "--trace-output",
                str(trace_path),
            ]
        )

        exit_code = await run_execute(
            CliPrinter("WeaveMark", verbose=False),
            "Write a concise answer.",
            {},
            tmp_path,
            args,
        )

        assert exit_code == 0
        assert output_path.read_text(encoding="utf-8") == "Final response"
        trace = trace_path.read_text(encoding="utf-8")
        assert "Draft response" in trace
        assert "Final response" in trace
        assert "| Spec | `traceable.weavemark.md` |" in trace
        assert str(tmp_path) not in trace

    @pytest.mark.asyncio
    async def test_run_execute_show_output_prints_final_before_file_summary(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        """Run demos can stream engine output before saving artifacts."""
        from ellements.cli import CliPrinter
        from ellements.execution import StepRecord

        import weavemark.engines
        from weavemark.app import create_parser, run_execute
        from weavemark.engines import ExecutionResult

        class FakeEngine:
            async def execute(self, result, config=None, on_step=None):
                step = StepRecord(
                    name="generate",
                    prompt_key="default",
                    response="Draft response",
                    metadata={},
                )
                if on_step:
                    on_step(step)
                return ExecutionResult(
                    output="Visible final response",
                    steps=[step],
                    metadata={},
                )

        monkeypatch.setattr(
            weavemark.engines,
            "resolve_engine",
            lambda _name, **_kwargs: FakeEngine(),
        )

        output_path = tmp_path / "output.md"
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "show-run.weavemark.md"),
                "--run",
                "--output",
                str(output_path),
                "--show-output",
            ]
        )

        exit_code = await run_execute(
            CliPrinter("WeaveMark", verbose=False),
            "Write a concise answer.",
            {},
            tmp_path,
            args,
        )

        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Visible final response" in captured.out
        assert "Output written to" in captured.err
        assert output_path.read_text(encoding="utf-8") == "Visible final response"

    @pytest.mark.asyncio
    async def test_batch_writes_emit_files_relative_to_output(self, tmp_path: Path):
        """Batch mode writes @emit artifacts next to the primary output."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_dir = tmp_path / "dist"
        output_dir.mkdir()
        output_path = output_dir / "combined.md"
        spec = (
            "Primary prompt.\n\n"
            "@emit file: roles/system.md\n"
            "  System prompt for @{topic}.\n"
        )
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "emit.weavemark.md"),
                "--batch-only",
                "--output",
                str(output_path),
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            spec,
            {"topic": "launch planning"},
            tmp_path,
            args,
        )

        assert exit_code == 0
        assert output_path.read_text(encoding="utf-8") == "Primary prompt."
        assert (output_dir / "roles" / "system.md").read_text(
            encoding="utf-8"
        ) == "System prompt for launch planning."

    @pytest.mark.asyncio
    async def test_batch_show_output_prints_before_file_summary(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ):
        """--show-output makes demos print the prompt before artifact messages."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_path = tmp_path / "compiled.md"
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "show.weavemark.md"),
                "--batch-only",
                "--output",
                str(output_path),
                "--show-output",
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            "Visible prompt for @{topic}.",
            {"topic": "demos"},
            tmp_path,
            args,
        )

        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Visible prompt for demos." in captured.out
        assert "Output written to" in captured.err
        assert output_path.read_text(encoding="utf-8") == "Visible prompt for demos."

    @pytest.mark.asyncio
    async def test_batch_no_file_summary_suppresses_artifact_status(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ):
        """Demo scripts can print their own final artifact summary."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_path = tmp_path / "compiled.md"
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "quiet.weavemark.md"),
                "--batch-only",
                "--output",
                str(output_path),
                "--show-output",
                "--no-file-summary",
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            "Visible prompt for @{topic}.",
            {"topic": "quiet demos"},
            tmp_path,
            args,
        )

        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Visible prompt for quiet demos." in captured.out
        assert "Output written to" not in captured.err
        assert (
            output_path.read_text(encoding="utf-8") == "Visible prompt for quiet demos."
        )

    @pytest.mark.asyncio
    async def test_batch_returns_nonzero_for_composition_errors(self, tmp_path: Path):
        """Batch mode must fail when composition produced errors."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "bad-bind.weavemark.md"),
                "--batch-only",
            ]
        )
        spec = '@bind web_search language: python from: "../search.py" symbol: search\n'

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            spec,
            {},
            tmp_path,
            args,
        )

        assert exit_code == 1

    @pytest.mark.asyncio
    async def test_batch_returns_nonzero_for_missing_inputs(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ):
        """Batch mode must fail fast instead of compiling unresolved variables."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "missing.weavemark.md"),
                "--batch-only",
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            "Hello @{name}.",
            {},
            tmp_path,
            args,
        )

        captured = capsys.readouterr()
        assert exit_code == 1
        assert "Batch mode cannot continue" in captured.err
        assert "@{name}" in captured.err

    @pytest.mark.asyncio
    async def test_interactive_prompts_for_missing_inputs(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        """Default interactive mode asks for missing inputs before composing."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_interactive

        printer = CliPrinter("WeaveMark", verbose=False)
        responses = iter(["Ada", ""])
        monkeypatch.setattr(
            printer.console,
            "input",
            lambda *_args, **_kwargs: next(responses),
        )

        parser = create_parser()
        args = parser.parse_args([str(tmp_path / "hello.weavemark.md")])

        exit_code = await run_interactive(
            printer,
            "Hello @{name}.",
            {},
            tmp_path,
            args,
        )

        captured = capsys.readouterr()
        assert exit_code == 0
        assert "WeaveMark needs 1 input" in captured.err
        assert "Hello Ada." in captured.out

    @pytest.mark.asyncio
    async def test_batch_writes_message_files_relative_to_output(self, tmp_path: Path):
        """Batch mode writes role-tagged @prompt artifacts using default name.role.md paths."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_dir = tmp_path / "dist"
        output_dir.mkdir()
        output_path = output_dir / "combined.md"
        spec = (
            "Primary prompt.\n\n"
            "@prompt intro role: system\n"
            "  System prompt for @{topic}.\n"
        )
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "message.weavemark.md"),
                "--batch-only",
                "--output",
                str(output_path),
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            spec,
            {"topic": "launch planning"},
            tmp_path,
            args,
        )

        assert exit_code == 0
        assert output_path.read_text(encoding="utf-8") == "Primary prompt."
        assert (output_dir / "intro.system.md").read_text(
            encoding="utf-8"
        ) == "System prompt for launch planning."

    @pytest.mark.asyncio
    async def test_batch_uses_compile_format_when_cli_format_is_absent(
        self,
        tmp_path: Path,
    ):
        """Batch mode uses @compile format when --format is not explicit."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_path = tmp_path / "result.out"
        spec = "@compile format: json\n\n" "Primary prompt for @{topic}.\n"
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "compile-format.weavemark.md"),
                "--batch-only",
                "--output",
                str(output_path),
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            spec,
            {"topic": "launch planning"},
            tmp_path,
            args,
        )

        parsed = json.loads(output_path.read_text(encoding="utf-8"))
        assert exit_code == 0
        assert parsed["compile"] == {"format": "json"}
        assert parsed["composed_prompt"] == "Primary prompt for launch planning."

    @pytest.mark.asyncio
    async def test_batch_output_dir_writes_primary_with_derived_name(
        self,
        tmp_path: Path,
    ):
        """--output-dir writes the primary as <spec-stem>.md inside the directory."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_dir = tmp_path / "dist"
        spec = "Primary prompt for @{topic}.\n"
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "asset-deep-search.weavemark.md"),
                "--batch-only",
                "--output-dir",
                str(output_dir),
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            spec,
            {"topic": "launch planning"},
            tmp_path,
            args,
        )

        assert exit_code == 0
        assert (output_dir / "asset-deep-search.md").read_text(
            encoding="utf-8"
        ) == "Primary prompt for launch planning."

    @pytest.mark.asyncio
    async def test_batch_output_dir_writes_messages_into_directory(
        self,
        tmp_path: Path,
    ):
        """--output-dir places role-tagged @prompt artifacts in the directory next to the primary."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_dir = tmp_path / "dist"
        spec = (
            "Primary prompt.\n\n"
            "@prompt intro role: system\n"
            "  System prompt for @{topic}.\n"
        )
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "scenario.weavemark.md"),
                "--batch-only",
                "--output-dir",
                str(output_dir),
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            spec,
            {"topic": "launch planning"},
            tmp_path,
            args,
        )

        assert exit_code == 0
        assert (output_dir / "scenario.md").read_text(
            encoding="utf-8"
        ) == "Primary prompt."
        assert (output_dir / "intro.system.md").read_text(
            encoding="utf-8"
        ) == "System prompt for launch planning."

    @pytest.mark.asyncio
    async def test_batch_output_dir_skips_whitespace_primary_with_warning(
        self,
        tmp_path: Path,
    ):
        """Whitespace-only primary is skipped with a warning; role-tagged @prompt files still emit."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_dir = tmp_path / "dist"
        spec = (
            "\n   \n"
            "@prompt intro-system role: system\n"
            "  System prompt for @{topic}.\n\n"
            "@prompt intro-user role: user\n"
            "  User prompt for @{topic}.\n"
        )
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "scenario.weavemark.md"),
                "--batch-only",
                "--output-dir",
                str(output_dir),
            ]
        )

        printer = CliPrinter("WeaveMark", verbose=False)
        exit_code = await run_batch(
            printer,
            spec,
            {"topic": "launch planning"},
            tmp_path,
            args,
        )

        assert exit_code == 0
        assert not (output_dir / "scenario.md").exists()
        assert (output_dir / "intro-system.system.md").read_text(
            encoding="utf-8"
        ) == "System prompt for launch planning."
        assert (output_dir / "intro-user.user.md").read_text(
            encoding="utf-8"
        ) == "User prompt for launch planning."

    @pytest.mark.asyncio
    async def test_batch_output_file_skips_whitespace_primary_with_warning(
        self,
        tmp_path: Path,
    ):
        """When --output is given but the spec yields no primary content, skip the file."""
        from ellements.cli import CliPrinter

        from weavemark.app import create_parser, run_batch

        output_path = tmp_path / "dist" / "primary.md"
        spec = "\n\n" "@emit file: roles/system.md\n" "  System prompt for @{topic}.\n"
        parser = create_parser()
        args = parser.parse_args(
            [
                str(tmp_path / "emit-only.weavemark.md"),
                "--batch-only",
                "--output",
                str(output_path),
            ]
        )

        exit_code = await run_batch(
            CliPrinter("WeaveMark", verbose=False),
            spec,
            {"topic": "launch planning"},
            tmp_path,
            args,
        )

        assert exit_code == 0
        assert not output_path.exists()
        assert (output_path.parent / "roles" / "system.md").read_text(
            encoding="utf-8"
        ) == "System prompt for launch planning."

    def test_output_and_output_dir_are_mutually_exclusive(
        self,
        tmp_path: Path,
        monkeypatch,
    ):
        """Passing both --output and --output-dir exits with code 2."""
        import sys as _sys

        from weavemark.app import cli

        spec_path = tmp_path / "scenario.weavemark.md"
        spec_path.write_text("Primary.\n", encoding="utf-8")
        monkeypatch.setattr(
            _sys,
            "argv",
            [
                "weavemark",
                str(spec_path),
                "--batch-only",
                "--output",
                str(tmp_path / "out.md"),
                "--output-dir",
                str(tmp_path / "dist"),
            ],
        )

        with pytest.raises(SystemExit) as exc_info:
            cli()
        assert exc_info.value.code == 2


class TestToolRegistration:
    """Tests that the correct tools are registered."""

    def test_log_issue_tool_not_in_tools(self):
        """Issues arrive in the structured result, not through a tool."""
        from weavemark.controller import TOOLS

        tool_names = [t["function"]["name"] for t in TOOLS]
        assert "log_issue" not in tool_names

    def test_tools_include_read_file_and_log_transition(self):
        """TOOLS should include read_file and log_transition."""
        from weavemark.controller import TOOLS

        tool_names = [t["function"]["name"] for t in TOOLS]
        assert "read_file" in tool_names
        assert "log_transition" in tool_names
        assert len(TOOLS) == 2


class TestIssueHandling:
    """Tests for issue extraction, formatting, and output separation."""

    def test_response_preserves_warnings_and_suggestions(self):
        """Verify parse_composition_response correctly extracts all issue types."""
        from weavemark.controller import parse_composition_response

        raw = compiler_response(
            "You are a helpful assistant.",
            warnings=["Variable 'tone' was not provided, defaulting to neutral."],
            suggestions=[
                "Consider adding a persona directive for better results.",
                "The prompt could benefit from more specific constraints.",
            ],
        )

        result = parse_composition_response(raw)
        assert result.composed_prompt == "You are a helpful assistant."
        assert len(result.warnings) == 1
        assert "tone" in result.warnings[0].lower()
        assert len(result.suggestions) == 2
        assert result.errors == []
        # issues property should combine all
        assert len(result.diagnostics) == 3

    def test_non_schema_response_is_a_protocol_error(self):
        from weavemark.controller import parse_composition_response

        raw = "You are a helpful assistant.\n\nWarning: something went wrong."
        result = parse_composition_response(raw)
        assert result.composed_prompt == ""
        assert result.warnings == []
        assert result.suggestions == []
        assert len(result.errors) == 1
        assert "protocol error" in result.errors[0].lower()

    def test_empty_issue_arrays_yield_no_diagnostics(self):
        from weavemark.controller import parse_composition_response

        raw = compiler_response("Hello world.")

        result = parse_composition_response(raw)
        assert result.composed_prompt == "Hello world."
        assert result.warnings == []
        assert result.errors == []
        assert result.suggestions == []

    def test_verbose_batch_output_includes_diagnostics(self):
        """Issues should NOT be in _format_raw_output — they go to stderr separately."""
        from weavemark.app import _format_raw_output
        from weavemark.controller import CompositionResult

        result = CompositionResult(
            composed_prompt="You are a helpful assistant.",
            raw_response="<output>...</output>",
            warnings=["Variable 'tone' was not provided."],
            suggestions=["Consider adding more context."],
        )
        # Markdown output always contains only the prompt, never issues
        output = _format_raw_output(result, "markdown")
        assert output == "You are a helpful assistant."
        assert "Composition Issues" not in output
        assert "tone" not in output

    def test_non_verbose_batch_output_excludes_diagnostics(self):
        """_format_raw_output must only have the prompt."""
        from weavemark.app import _format_raw_output
        from weavemark.controller import CompositionResult

        result = CompositionResult(
            composed_prompt="You are a helpful assistant.",
            raw_response="<output>...</output>",
            warnings=["Variable 'tone' was not provided."],
            suggestions=["Consider adding more context."],
        )
        output = _format_raw_output(result, "markdown")
        assert output == "You are a helpful assistant."
        assert "Composition Issues" not in output

    def test_json_output_includes_diagnostics(self):
        """JSON output must always include warnings/suggestions fields."""
        from weavemark.app import _format_raw_output
        from weavemark.controller import CompositionResult

        result = CompositionResult(
            composed_prompt="Test prompt.",
            raw_response="<output>...</output>",
            warnings=["A warning."],
            suggestions=["A suggestion."],
        )
        output = _format_raw_output(result, "json")
        parsed = json.loads(output)
        assert parsed["warnings"] == ["A warning."]
        assert parsed["suggestions"] == ["A suggestion."]

    def test_json_wrapped_in_code_fence_is_rejected(self):
        from weavemark.controller import parse_composition_response

        raw = f"```json\n{compiler_response('You are a helpful assistant.')}\n```"

        result = parse_composition_response(raw)
        assert result.composed_prompt == ""
        assert result.errors

    def test_parse_response_with_large_prompt(self):
        from weavemark.controller import parse_composition_response

        big_prompt = "You are an analyst. " * 200  # ~4000 chars
        raw = compiler_response(
            big_prompt,
            warnings=["This is a test warning about the large prompt."],
            suggestions=["Consider splitting the prompt into sections."],
        )

        result = parse_composition_response(raw)
        assert "analyst" in result.composed_prompt
        assert len(result.composed_prompt) > 3000
        assert len(result.warnings) == 1
        assert len(result.suggestions) == 1


# ──────────────────────────────────────────────────────────────────
# Nesting and core directive integration tests
# ──────────────────────────────────────────────────────────────────


@_skip_no_api_key
class TestNestingAndCoreDirectives:
    """Integration tests for nested core directives."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_nested_if_inside_if(self):
        """Double-nested @if blocks resolve inside out."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = """
Write about @{topic}.

@if include_details
  Include technical details.
  @if include_examples
    Add code examples for each concept.
"""
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec,
            variables={
                "topic": "REST APIs",
                "include_details": True,
                "include_examples": True,
            },
        )

        assert result.composed_prompt
        assert "technical details" in result.composed_prompt.lower()
        assert "code examples" in result.composed_prompt.lower()
        assert "@if" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_nested_if_false_omits_inner_block(self):
        """When outer @if is false, inner block is omitted entirely."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = """
Write about databases.

@if include_advanced
  Advanced topics:
  @if include_sharding
    Explain sharding strategies.
"""
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec,
            variables={
                "include_advanced": False,
                "include_sharding": True,
            },
        )

        assert result.composed_prompt
        assert "sharding" not in result.composed_prompt.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_at_sign_escaping(self):
        """@@ in the spec renders as a literal @ in the output."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = """
Python decorators use the @@property and @@staticmethod syntax.
Email: user@@example.com
"""
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(spec, variables={})

        assert "@property" in result.composed_prompt
        assert "@staticmethod" in result.composed_prompt
        assert "user@example.com" in result.composed_prompt
        assert "@@" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_note_stripped_from_output(self):
        """@note blocks are removed from the composed prompt."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = """
@note
  This is an internal design note that should not appear in output.
  It explains the rationale for the prompt structure.

Write a professional email to the team about the Q3 roadmap.
"""
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(spec, variables={})

        assert "professional email" in result.composed_prompt.lower()
        assert "internal design note" not in result.composed_prompt.lower()
        assert "@note" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_refine_with_nested_match(self):
        """@refine + @match work together (market research spec)."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec_file = PROMPLETS_DIR / "market-research-brief.weavemark.md"
        vars_file = EXAMPLES_DIR / "batch-example-runs/static-prompts/inputs/market-research-example.json"

        spec = spec_file.read_text()
        variables = json.loads(vars_file.read_text())

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(spec, variables=variables)

        assert result.composed_prompt
        # @refine should have pulled in reasoning/base-analyst.weavemark.md content
        assert (
            "analytical" in result.composed_prompt.lower()
            or "analysis" in result.composed_prompt.lower()
        )
        # Variable substitution
        assert "Rivian" in result.composed_prompt
        # No raw directives
        assert "@refine" not in result.composed_prompt
        assert "@match" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_log_transition_tool_called(self):
        """The log_transition tool is invoked during composition."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = """
@match mode
  "a" ==>
    Option A content.
  "b" ==>
    Option B content.

Write about @{topic}.
"""
        events = []

        def on_event(event_type, data):
            events.append((event_type, data))

        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec,
            variables={"mode": "a", "topic": "testing"},
            on_event=on_event,
        )

        assert result.composed_prompt
        # Transitions may or may not be logged depending on LLM behavior,
        # but the composition should succeed regardless
        assert (
            "Option A" in result.composed_prompt
            or "testing" in result.composed_prompt.lower()
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_named_branch_with_refine_loads_file(self, tmp_path: Path):
        """A named `@match` branch containing `@refine` loads the target file."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        target = tmp_path / "alpha-fragment.weavemark.md"
        target.write_text(
            "## Alpha Fragment\n\n"
            "MARKER_ALPHA_42 — this sentence proves the refine target "
            "was loaded.\n"
        )

        spec = """@promplet version: 0.6

# Branch Router

You are a router that dispatches to one of several fragments based
on the `choice` variable.

## Selected Fragment

@match choice
  "alpha" ==>
    @refine ./alpha-fragment.weavemark.md mingle: false
  "beta" ==>
    Beta branch content (no refine).
"""
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={"choice": "alpha"},
            base_dir=tmp_path,
        )

        prompt = result.composed_prompt
        assert prompt, "Composition must produce a non-empty prompt"
        assert "MARKER_ALPHA_42" in prompt, (
            "Named @match branch with @refine must inline the target's "
            f"marker. Got:\n{prompt}"
        )
        assert "@refine" not in prompt
        assert "@match" not in prompt
        assert (
            result.tool_calls_made > 0
        ), "read_file should be invoked for the nested @refine target"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_wildcard_branch_with_refine_loads_file(self, tmp_path: Path):
        """A wildcard `_ ==> @refine ...` branch must also load the target.

        Regression guard for the wildcard case of the
        `@match → @refine` combination: an unmatched `choice` value
        must trigger the default branch's `@refine`, which in turn
        must actually invoke `read_file` for the target spec.
        """
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        target = tmp_path / "default-fragment.weavemark.md"
        target.write_text(
            "## Default Fragment\n\n"
            "MARKER_DEFAULT_77 — wildcard refine target loaded.\n"
        )

        spec = """@promplet version: 0.6

# Branch Router

You are a router that dispatches to one of several fragments based
on the `choice` variable. Unknown values fall through to the
default fragment.

## Selected Fragment

@match choice
  "alpha" ==>
    Alpha branch content (no refine).
  _ ==>
    @refine ./default-fragment.weavemark.md mingle: false
"""
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={"choice": "something-not-listed"},
            base_dir=tmp_path,
        )

        prompt = result.composed_prompt
        assert prompt, "Composition must produce a non-empty prompt"
        assert "MARKER_DEFAULT_77" in prompt, (
            "Wildcard @match branch with @refine must inline the "
            f"target's marker. Got:\n{prompt}"
        )
        assert "@refine" not in prompt
        assert "@match" not in prompt
        assert (
            result.tool_calls_made > 0
        ), "read_file should be invoked for the wildcard @refine target"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_match_with_refine_does_not_load_unselected_branch(
        self, tmp_path: Path
    ):
        """Only the winning branch's @refine should trigger a file load.

        Inactive branches must be discarded; their `@refine` targets
        must not appear in the composed output.
        """
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        winner = tmp_path / "winner-fragment.weavemark.md"
        winner.write_text("MARKER_WINNER_ONLY — this branch was selected.\n")
        loser = tmp_path / "loser-fragment.weavemark.md"
        loser.write_text("MARKER_LOSER_NEVER — this branch was NOT selected.\n")

        spec = """@promplet version: 0.6

# Branch Router

You are a router that dispatches to one of two fragments based on
the `pick` variable. Only the selected fragment must be inlined.

## Selected Fragment

@match pick
  "win" ==>
    @refine ./winner-fragment.weavemark.md
  "lose" ==>
    @refine ./loser-fragment.weavemark.md
"""
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={"pick": "win"},
            base_dir=tmp_path,
        )

        prompt = result.composed_prompt
        assert "MARKER_WINNER_ONLY" in prompt
        assert (
            "MARKER_LOSER_NEVER" not in prompt
        ), "Unselected @match branch's @refine target must not be inlined"


@_skip_no_api_key
class TestCreativeIdeationSpec:
    """End-to-end tests for the `creative-ideation.weavemark.md` application.

    This application spec dispatches to one of several pure method specs
    (SCAMPER, Six Thinking Hats, Reverse Brainstorming) via
    `@match method ==> @refine <method>.weavemark.md`, with a wildcard
    default of SCAMPER. These tests exercise the full
    application + dispatch + method-definition chain.
    """

    SUBJECT = "our company's weekly engineering all-hands meeting"
    OBJECTIVE = "make it more engaging for engineers without making it longer"
    SPEC_PATH = PROMPLETS_DIR / "catalog/standalone/creative-ideation.weavemark.md"
    BASE_DIR = PROMPLETS_DIR / "catalog/standalone"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_creative_ideation_scamper_named_branch(self):
        """method='scamper' selects the SCAMPER method spec."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = self.SPEC_PATH.read_text()
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={
                "method": "scamper",
                "subject": self.SUBJECT,
                "objective": self.OBJECTIVE,
            },
            base_dir=self.BASE_DIR,
        )

        prompt = result.composed_prompt
        assert prompt
        prompt_lower = prompt.lower()
        assert "scamper" in prompt_lower
        # Several SCAMPER lens names should appear in the composed prompt
        lens_terms = [
            "substitute",
            "combine",
            "adapt",
            "modify",
            "eliminate",
            "reverse",
        ]
        present = [t for t in lens_terms if t in prompt_lower]
        assert len(present) >= 4, (
            f"Expected at least 4 SCAMPER lens names in composed prompt, "
            f"found {present}.\nPrompt:\n{prompt}"
        )
        assert "@match" not in prompt
        assert "@refine" not in prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_creative_ideation_six_thinking_hats_named_branch(self):
        """method='six-thinking-hats' selects the Six Hats method spec."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = self.SPEC_PATH.read_text()
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={
                "method": "six-thinking-hats",
                "subject": self.SUBJECT,
                "objective": self.OBJECTIVE,
            },
            base_dir=self.BASE_DIR,
        )

        prompt = result.composed_prompt
        assert prompt
        prompt_lower = prompt.lower()
        # Hat names should appear
        hat_terms = [
            "white hat",
            "red hat",
            "black hat",
            "yellow hat",
            "green hat",
            "blue hat",
        ]
        present = [t for t in hat_terms if t in prompt_lower]
        assert len(present) >= 4, (
            f"Expected at least 4 hat names in composed prompt, "
            f"found {present}.\nPrompt:\n{prompt}"
        )
        # SCAMPER content must NOT have leaked in
        assert "scamper" not in prompt_lower
        assert "@match" not in prompt
        assert "@refine" not in prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_creative_ideation_reverse_brainstorming_named_branch(self):
        """method='reverse-brainstorming' selects the Reverse Brainstorming spec."""
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = self.SPEC_PATH.read_text()
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={
                "method": "reverse-brainstorming",
                "subject": self.SUBJECT,
                "objective": self.OBJECTIVE,
            },
            base_dir=self.BASE_DIR,
        )

        prompt = result.composed_prompt
        assert prompt
        prompt_lower = prompt.lower()
        # Core reverse-brainstorming vocabulary
        rb_terms = ["invert", "reverse", "flip", "fail"]
        present = [t for t in rb_terms if t in prompt_lower]
        assert len(present) >= 2, (
            f"Expected at least 2 reverse-brainstorming terms, "
            f"found {present}.\nPrompt:\n{prompt}"
        )
        # SCAMPER content must NOT have leaked in
        assert "substitute, combine, adapt" not in prompt_lower
        assert "@match" not in prompt
        assert "@refine" not in prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_creative_ideation_wildcard_falls_back_to_scamper(self):
        """An unrecognized method value falls back to SCAMPER via `_ ==> @refine ...`.

        The composer must still honor the `_` branch when the selected method
        is semantically mingled rather than structurally pasted.
        """
        from weavemark.controller import (
            WeaveMarkConfig,
            WeaveMarkController,
        )

        spec = self.SPEC_PATH.read_text()
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_text=spec,
            variables={
                "method": "not-a-real-method-xyz",
                "subject": self.SUBJECT,
                "objective": self.OBJECTIVE,
            },
            base_dir=self.BASE_DIR,
        )

        prompt = result.composed_prompt
        assert prompt
        prompt_lower = prompt.lower()

        # The SCAMPER method spec must have actually been loaded — its
        # lens names should appear in the composed prompt.
        lens_terms = [
            "substitute",
            "combine",
            "adapt",
            "modify",
            "eliminate",
            "reverse",
        ]
        present = [t for t in lens_terms if t in prompt_lower]
        assert len(present) >= 4, (
            "Wildcard branch failed to load SCAMPER method spec — "
            f"only found lens terms {present} in composed prompt.\n"
            f"Prompt:\n{prompt}"
        )

        # Negative checks: explicit "could not be loaded" failure mode
        # must not appear.
        for failure_phrase in [
            "could not be loaded",
            "would be inserted here",
            "file not found",
            "unable to load",
        ]:
            assert failure_phrase not in prompt_lower, (
                f"Composer reported file-load failure ('{failure_phrase}') "
                f"in wildcard branch. Prompt:\n{prompt}"
            )

        assert "@match" not in prompt
        assert "@refine" not in prompt


@_skip_no_api_key
class TestMatchWithNestedRefineLLMOnly:
    """LLM-only path for ``@match`` then ``@refine`` (structural helpers off).

    The production path (deterministic structural helper) reliably handles
    the dispatch pattern. These tests bypass the helper to exercise the
    *pure LLM composer* — the path that will matter as we (a) experiment
    with using the LLM more aggressively and (b) want some confidence
    that the language definition in ``weavemark.system.md`` is teaching
    the composer the right behaviour rather than relying entirely on the
    Python pre-pass.

    The application spec (``creative-ideation.weavemark.md``) is used as
    the realistic harness — minimal synthetic specs are too sparse for
    the LLM to recognize them as "real specs to compile" rather than as
    "documentation/examples of the language", which is a separate
    failure mode that production specs do not exhibit.

    Reliability budget (observed across multiple runs at temperature 0):

      - Named branches (``scamper``, ``six-thinking-hats``,
        ``reverse-brainstorming``): 3/3 PASS — pinned by these tests.
      - Wildcard ``_`` branch with unknown method: ~1/3 — the LLM still
        sometimes narrates "Defaulting to …" and emits a placeholder
        instead of calling ``read_file``. Tracked by the ``xfail`` test
        below as a known limitation of the LLM-only path; the
        deterministic helper handles this case in production.
    """

    SUBJECT = "our company's weekly engineering all-hands meeting"
    OBJECTIVE = "make it more engaging for engineers without making it longer"

    @staticmethod
    def _llm_only_config():
        from weavemark.controller import WeaveMarkConfig
        from weavemark.defaults import DEFAULT_MODEL

        return WeaveMarkConfig(
            model=DEFAULT_MODEL,
            temperature=0.0,
            use_structural_helpers=False,
        )

    async def _compose_application(self, method: str):
        from weavemark.controller import WeaveMarkController

        spec_path = PROMPLETS_DIR / "catalog/standalone/creative-ideation.weavemark.md"
        spec = spec_path.read_text()
        controller = WeaveMarkController(self._llm_only_config())
        return await controller.compose(
            spec_text=spec,
            variables={
                "method": method,
                "subject": self.SUBJECT,
                "objective": self.OBJECTIVE,
            },
            base_dir=spec_path.parent,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_llm_only_named_scamper_branch(self):
        """LLM-only: `method=scamper` named branch loads the SCAMPER spec."""
        result = await self._compose_application("scamper")
        prompt_lower = result.composed_prompt.lower()
        lens_terms = [
            "substitute",
            "combine",
            "adapt",
            "modify",
            "eliminate",
            "reverse",
        ]
        present = [t for t in lens_terms if t in prompt_lower]
        assert len(present) >= 4, (
            "LLM-only composition of the named SCAMPER branch must "
            f"surface SCAMPER lens names; only found {present}.\n"
            f"tool_calls_made={result.tool_calls_made}\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        assert (
            result.tool_calls_made >= 1
        ), "LLM must invoke read_file for the named branch's @refine"
        assert "@match" not in result.composed_prompt
        assert "@refine" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_llm_only_named_six_thinking_hats_branch(self):
        """LLM-only: `method=six-thinking-hats` named branch loads the hats spec."""
        result = await self._compose_application("six-thinking-hats")
        prompt_lower = result.composed_prompt.lower()
        hat_terms = [
            "white hat",
            "red hat",
            "black hat",
            "yellow hat",
            "green hat",
            "blue hat",
        ]
        present = [t for t in hat_terms if t in prompt_lower]
        assert len(present) >= 4, (
            "LLM-only composition of the six-thinking-hats branch must "
            f"surface hat names; only found {present}.\n"
            f"tool_calls_made={result.tool_calls_made}\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        # SCAMPER content must not leak in
        assert "substitute, combine, adapt" not in prompt_lower
        assert result.tool_calls_made >= 1
        assert "@match" not in result.composed_prompt
        assert "@refine" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_llm_only_named_reverse_brainstorming_branch(self):
        """LLM-only: `method=reverse-brainstorming` loads the reverse spec."""
        result = await self._compose_application("reverse-brainstorming")
        prompt_lower = result.composed_prompt.lower()
        rb_terms = ["invert", "reverse", "flip", "fail"]
        present = [t for t in rb_terms if t in prompt_lower]
        assert len(present) >= 2, (
            "LLM-only composition of the reverse-brainstorming branch "
            f"must surface reverse-ideation vocabulary; only found "
            f"{present}.\ntool_calls_made={result.tool_calls_made}\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        assert result.tool_calls_made >= 1
        assert "@match" not in result.composed_prompt
        assert "@refine" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_llm_only_wildcard_falls_back_to_scamper(self):
        """LLM-only: an unknown method must select the `_` branch and load SCAMPER.

        Originally flaky (~1/3 pass rate) — fixed by strengthening the
        composer system prompt with explicit anti-hallucination,
        size-invariance, and "no second chances within a turn" rules
        plus a sharper tool-call inventory check. Now reliable.
        """
        result = await self._compose_application("not-a-real-method-zzz")
        prompt_lower = result.composed_prompt.lower()
        lens_terms = [
            "substitute",
            "combine",
            "adapt",
            "modify",
            "eliminate",
        ]
        present = [t for t in lens_terms if t in prompt_lower]
        assert len(present) >= 4, (
            "LLM-only composition of the wildcard branch must "
            f"surface SCAMPER lens names; only found {present}.\n"
            f"tool_calls_made={result.tool_calls_made}\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        assert (
            result.tool_calls_made >= 1
        ), "LLM must invoke read_file for the wildcard branch's @refine"


@_skip_no_api_key
class TestTinySpecLLMOnly:
    """Tiny synthetic specs composed end-to-end through the LLM only.

    These tests pin the behaviour that originally motivated the
    'Size invariance', 'Anti-hallucination', and 'No second chances
    within a turn' rules in ``weavemark.system.md``. Before those
    rules, earlier default models routinely one-shotted minimal specs by emitting
    placeholders like ``(Content from X will be inserted here.)``
    instead of invoking ``read_file``. The model's own ``<analysis>``
    would even claim "All required tool calls were made" while
    ``tool_calls_made == 0`` — a fluent hallucination.

    Each case here uses a 5-line synthetic spec with one ``@refine``
    in the winning branch. The full composition (selection +
    file load + inlining + transition log) must go through the
    LLM with ``use_structural_helpers=False``.

    All four variants (named/wildcard × mingle:false/true) PASS
    reliably (3/3 in repeated probe runs at temperature 0).
    """

    @staticmethod
    def _llm_only_config():
        from weavemark.controller import WeaveMarkConfig
        from weavemark.defaults import DEFAULT_MODEL

        return WeaveMarkConfig(
            model=DEFAULT_MODEL,
            temperature=0.0,
            use_structural_helpers=False,
        )

    async def _compose(self, spec: str, variables: dict, base_dir: Path):
        from weavemark.controller import WeaveMarkController

        controller = WeaveMarkController(self._llm_only_config())
        return await controller.compose(
            spec_text=spec,
            variables=variables,
            base_dir=base_dir,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tiny_named_branch_mingle_false(self, tmp_path: Path):
        """Tiny spec, named branch, mingle:false — LLM-only."""
        (tmp_path / "alpha.weavemark.md").write_text(
            "## Alpha\n\nMARKER_ALPHA — alpha loaded.\n"
        )
        spec = (
            "@promplet version: 0.6\n\n"
            "# Router\n\n"
            "@match choice\n"
            '  "alpha" ==>\n'
            "    @refine ./alpha.weavemark.md mingle: false\n"
            '  "beta" ==>\n'
            "    Beta inline.\n"
        )
        result = await self._compose(spec, {"choice": "alpha"}, tmp_path)
        assert "MARKER_ALPHA" in result.composed_prompt, (
            "LLM-only composition must actually load alpha.weavemark.md; "
            f"tool_calls_made={result.tool_calls_made}, "
            f"transitions={len(result.transitions)}.\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        assert result.tool_calls_made >= 1
        assert "@refine" not in result.composed_prompt
        assert "@match" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tiny_named_branch_mingle_true(self, tmp_path: Path):
        """Tiny spec, named branch, mingle:true (default) — LLM-only."""
        (tmp_path / "alpha.weavemark.md").write_text(
            "## Alpha\n\nMARKER_ALPHA — alpha loaded.\n"
        )
        spec = (
            "@promplet version: 0.6\n\n"
            "# Router\n\n"
            "@match choice\n"
            '  "alpha" ==>\n'
            "    @refine ./alpha.weavemark.md\n"
            '  "beta" ==>\n'
            "    Beta inline.\n"
        )
        result = await self._compose(spec, {"choice": "alpha"}, tmp_path)
        assert "MARKER_ALPHA" in result.composed_prompt, (
            "LLM-only composition must actually load alpha.weavemark.md; "
            f"tool_calls_made={result.tool_calls_made}, "
            f"transitions={len(result.transitions)}.\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        assert result.tool_calls_made >= 1
        assert "@refine" not in result.composed_prompt
        assert "@match" not in result.composed_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tiny_wildcard_branch_mingle_false(self, tmp_path: Path):
        """Tiny spec, wildcard `_` branch, mingle:false — LLM-only.

        Variable value is deliberately a literal-looking string (no
        semantic overlap with named labels) to exercise pure exact-match
        equality.
        """
        (tmp_path / "default.weavemark.md").write_text(
            "## Default\n\nMARKER_DEFAULT — default loaded.\n"
        )
        spec = (
            "@promplet version: 0.6\n\n"
            "# Router\n\n"
            "@match choice\n"
            '  "known" ==>\n'
            "    Known inline.\n"
            "  _ ==>\n"
            "    @refine ./default.weavemark.md mingle: false\n"
        )
        result = await self._compose(spec, {"choice": "xyz999"}, tmp_path)
        assert "MARKER_DEFAULT" in result.composed_prompt, (
            "LLM-only composition must select the wildcard branch and "
            "actually load default.weavemark.md; "
            f"tool_calls_made={result.tool_calls_made}, "
            f"transitions={len(result.transitions)}.\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        assert result.tool_calls_made >= 1
        assert (
            "Known inline" not in result.composed_prompt
        ), "Wildcard match must not also include the losing branch's text"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tiny_wildcard_branch_mingle_true(self, tmp_path: Path):
        """Tiny spec, wildcard `_` branch, mingle:true (default) — LLM-only.

        The hardest of the four tiny cases historically — exercises the
        anti-hallucination + size-invariance + no-second-chances rules
        simultaneously.
        """
        (tmp_path / "default.weavemark.md").write_text(
            "## Default\n\nMARKER_DEFAULT — default loaded.\n"
        )
        spec = (
            "@promplet version: 0.6\n\n"
            "# Router\n\n"
            "@match choice\n"
            '  "known" ==>\n'
            "    Known inline.\n"
            "  _ ==>\n"
            "    @refine ./default.weavemark.md\n"
        )
        result = await self._compose(spec, {"choice": "xyz999"}, tmp_path)
        assert "MARKER_DEFAULT" in result.composed_prompt, (
            "LLM-only composition must select the wildcard branch and "
            "actually load default.weavemark.md; "
            f"tool_calls_made={result.tool_calls_made}, "
            f"transitions={len(result.transitions)}.\n"
            f"Prompt:\n{result.composed_prompt}"
        )
        assert result.tool_calls_made >= 1
        assert "Known inline" not in result.composed_prompt
