"""Run and report quality studies for public WeaveMark examples."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

sys.dont_write_bytecode = True

from regenerate_reports import (  # noqa: E402
    CORE_METRIC_DEFINITIONS,
    definition_cards,
    details_panel,
    html_document,
    html_link,
    html_path_for,
    kpi_card,
    metric_cell,
    metric_definition_lines,
    section,
)
from semantic_information import ROOT, Variant, variant_metrics  # noqa: E402

EXAMPLE_STUDIES_ROOT = ROOT / "studies/examples-studies"
EXAMPLE_METRICS_PATH = EXAMPLE_STUDIES_ROOT / "metrics/example-quality.json"
LEAK_PATTERNS = (
    re.compile(r"(?m)^\s*@(?:refine|expand|compress|iterate|ask|emit|match|if)\b"),
    re.compile(r"@\{[^}]+\}"),
    re.compile(r"\{\{[^}]+\}\}"),
    re.compile(r"/Users/"),
    re.compile(r"\b(?:WeaveMark|WeaveMark)\b"),
)
PATHOLOGY_PATTERNS = (
    re.compile(r"\bas an ai language model\b", re.IGNORECASE),
    re.compile(r"\blorem ipsum\b", re.IGNORECASE),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bundefined\b", re.IGNORECASE),
    re.compile(r"\bnull\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ExampleSpec:
    """One public example to run and evaluate."""

    example_id: str
    title: str
    spec_path: str
    vars_path: str
    output_path: str
    intention: str
    expected_terms: tuple[str, ...]


EXAMPLES: tuple[ExampleSpec, ...] = (
    ExampleSpec(
        "program-review-checklist",
        "Program Review Checklist",
        "promplets/catalog/standalone/program-review-checklist.weavemark.md",
        "examples/terminal-output-only/program-review-checklist/inputs/vars.json",
        "examples/terminal-output-only/program-review-checklist/outputs/compiled-prompt.md",
        "Produce a practical review checklist tailored to a programming project.",
        ("review", "checklist", "security", "correctness", "tests"),
    ),
    ExampleSpec(
        "program-debugging-assistant",
        "Program Debugging Assistant",
        "promplets/catalog/standalone/program-debugging-assistant.weavemark.md",
        "examples/terminal-output-only/program-debugging-assistant/inputs/vars.json",
        "examples/terminal-output-only/program-debugging-assistant/outputs/compiled-prompt.md",
        "Produce a debugging assistant prompt that diagnoses behavior from evidence.",
        ("debug", "expected", "observed", "evidence", "hypothesis"),
    ),
    ExampleSpec(
        "learning-tutor",
        "Learning Tutor",
        "promplets/catalog/standalone/learning-tutor.weavemark.md",
        "examples/terminal-output-only/learning-tutor/inputs/vars.json",
        "examples/terminal-output-only/learning-tutor/outputs/compiled-prompt.md",
        "Produce an adaptive tutor prompt grounded in learner context and practice.",
        ("learner", "misconception", "practice", "feedback", "review"),
    ),
    ExampleSpec(
        "research-brief",
        "Research Brief",
        "promplets/catalog/standalone/research-brief.weavemark.md",
        "examples/terminal-output-only/research-brief/inputs/vars.json",
        "examples/terminal-output-only/research-brief/outputs/compiled-prompt.md",
        "Produce a research brief prompt with source expectations and caveats.",
        ("source", "evidence", "contradiction", "caveat", "brief"),
    ),
    ExampleSpec(
        "decision-advisor",
        "Decision Advisor",
        "promplets/catalog/standalone/decision-advisor.weavemark.md",
        "examples/terminal-output-only/decision-advisor/inputs/vars.json",
        "examples/terminal-output-only/decision-advisor/outputs/compiled-prompt.md",
        "Produce a decision-advice prompt with options, tradeoffs, and uncertainty.",
        ("decision", "option", "tradeoff", "uncertainty", "recommendation"),
    ),
    ExampleSpec(
        "investment-brief",
        "Investment Brief",
        "promplets/catalog/standalone/investment-brief.weavemark.md",
        "examples/saved-artifact-workflows/investment-brief/inputs/vars.json",
        "examples/saved-artifact-workflows/investment-brief/outputs/compiled-prompt.md",
        "Produce an educational investment brief with evidence, risks, alternatives, and decision triggers.",
        ("investment", "evidence", "risks", "alternatives", "decision"),
    ),
    ExampleSpec(
        "deep-summary",
        "Deep Summary",
        "promplets/catalog/standalone/deep-summary-prompt.weavemark.md",
        "examples/terminal-output-only/deep-summary/inputs/vars.json",
        "examples/terminal-output-only/deep-summary/outputs/compiled-prompt.md",
        "Produce a deep-summary prompt that preserves structure and audience needs.",
        ("summary", "audience", "source", "structure", "insight"),
    ),
    ExampleSpec(
        "messy-notes-action-plan",
        "Messy Notes Action Plan",
        "promplets/catalog/standalone/messy-notes-action-plan.weavemark.md",
        "examples/terminal-output-only/messy-notes-action-plan/inputs/vars.json",
        "examples/terminal-output-only/messy-notes-action-plan/outputs/compiled-prompt.md",
        "Turn messy notes into an organized action plan.",
        ("notes", "action", "priority", "owner", "next"),
    ),
    ExampleSpec(
        "prompt-refiner",
        "Prompt Refiner",
        "promplets/catalog/standalone/prompt-refiner.weavemark.md",
        "examples/terminal-output-only/prompt-refiner/inputs/vars.json",
        "examples/terminal-output-only/prompt-refiner/outputs/compiled-prompt.md",
        "Produce a prompt-improvement prompt that preserves intent and improves clarity.",
        ("prompt", "preserve", "improve", "clarity", "output"),
    ),
)


def repo_path(path: str) -> Path:
    """Return an absolute repository path."""
    return ROOT / path


def rel_link(from_file: Path, target: Path) -> str:
    """Return a POSIX relative link."""
    return Path(target.resolve()).relative_to(from_file.parent.resolve()).as_posix()


def markdown_link(from_file: Path, label: str, target: Path) -> str:
    """Return a Markdown link from one generated report to a target."""
    href = Path(os.path.relpath(target, from_file.parent)).as_posix()
    return f"[{label}]({href})"


def word_count(path: Path) -> int:
    """Return whitespace-delimited word count for a file."""
    return len(path.read_text(encoding="utf-8").split())


def run_examples(examples: tuple[ExampleSpec, ...]) -> None:
    """Compile all examples into their own output folders."""
    for example in examples:
        output = repo_path(example.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "promplet",
                example.spec_path,
                "--vars-file",
                example.vars_path,
                "--batch-only",
                "--output",
                example.output_path,
                "--no-file-summary",
            ],
            cwd=ROOT,
            check=True,
        )


def score_from_thresholds(value: int, thresholds: tuple[int, int, int, int]) -> int:
    """Map a count to a 1-5 score."""
    return 1 + sum(value >= threshold for threshold in thresholds)


def rubric_scores(
    example: ExampleSpec, output_text: str
) -> dict[str, dict[str, object]]:
    """Evaluate one example output with deterministic quality checks."""
    lowered = output_text.lower()
    term_hits = sum(1 for term in example.expected_terms if term.lower() in lowered)
    leak_count = sum(len(pattern.findall(output_text)) for pattern in LEAK_PATTERNS)
    pathology_count = sum(
        len(pattern.findall(output_text)) for pattern in PATHOLOGY_PATTERNS
    )
    heading_count = output_text.count("\n#")
    bullet_count = len(re.findall(r"(?m)^\s*[-*]\s+", output_text))
    output_words = len(output_text.split())
    imperative_hits = sum(
        1
        for term in (
            "include",
            "explain",
            "provide",
            "identify",
            "recommend",
            "produce",
        )
        if term in lowered
    )
    scores = {
        "Intention fit": {
            "score": score_from_thresholds(term_hits, (2, 3, 4, 5)),
            "rationale": f"Matches {term_hits}/{len(example.expected_terms)} expected intent terms.",
        },
        "Completeness": {
            "score": min(
                5, max(1, score_from_thresholds(output_words, (200, 400, 700, 1000)))
            ),
            "rationale": f"Compiled output has {output_words} words.",
        },
        "Writing and structure": {
            "score": min(
                5,
                max(
                    1,
                    score_from_thresholds(heading_count + bullet_count, (4, 8, 14, 22)),
                ),
            ),
            "rationale": f"Uses {heading_count} headings and {bullet_count} bullet rows.",
        },
        "No leakage/pathologies": {
            "score": (
                5
                if leak_count == 0 and pathology_count == 0
                else 3 if leak_count + pathology_count <= 2 else 1
            ),
            "rationale": f"Detected {leak_count} internal leaks and {pathology_count} pathology markers.",
        },
        "Direct usefulness": {
            "score": min(
                5,
                max(
                    1,
                    score_from_thresholds(
                        imperative_hits + bullet_count, (4, 8, 14, 22)
                    ),
                ),
            ),
            "rationale": f"Instruction/action signal combines {imperative_hits} directive verbs and {bullet_count} bullets.",
        },
    }
    return scores


def example_metrics(example: ExampleSpec) -> dict[str, object]:
    """Return metric row and rubric scores for one example."""
    variant = Variant(
        example.example_id,
        "example",
        repo_path(example.spec_path),
        repo_path(example.vars_path),
        repo_path(example.output_path),
    )
    metrics = variant_metrics(variant)
    output_text = repo_path(example.output_path).read_text(encoding="utf-8")
    rubric = rubric_scores(example, output_text)
    return {
        "example_id": example.example_id,
        "title": example.title,
        "spec_path": example.spec_path,
        "vars_path": example.vars_path,
        "output_path": example.output_path,
        "intention": example.intention,
        "metrics": metrics,
        "rubric": rubric,
        "rubric_total": sum(int(item["score"]) for item in rubric.values()),
    }


def write_json(rows: list[dict[str, object]]) -> None:
    """Write example-study metrics."""
    EXAMPLE_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLE_METRICS_PATH.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def metric_table(rows: list[dict[str, object]], report_path: Path) -> list[str]:
    """Render the metrics table."""
    lines = [
        "| Example | Source words | Variable words | Output words | Leverage | Fact units | Density | Yield | Rubric |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        metrics = row["metrics"]
        assert isinstance(metrics, dict)
        output = repo_path(str(row["output_path"]))
        lines.append(
            "| "
            f"{markdown_link(report_path, str(row['title']), output)} | "
            f"{metrics['local_authored_source_words']} | "
            f"{metrics['variable_payload_words']} | "
            f"{metrics['output_words']} | "
            f"{metrics['local_leverage']}x | "
            f"{metrics['discounted_fact_units']} | "
            f"{metrics['information_density_per_1k_output_words']} | "
            f"{metrics['information_yield_per_1k_source_words']} | "
            f"{row['rubric_total']}/25 |"
        )
    return lines


def rubric_table(row: dict[str, object]) -> list[str]:
    """Render one example rubric table."""
    rubric = row["rubric"]
    assert isinstance(rubric, dict)
    lines = ["| Criterion | Score | Rationale |", "|---|---:|---|"]
    for criterion, result in rubric.items():
        assert isinstance(result, dict)
        lines.append(f"| {criterion} | {result['score']}/5 | {result['rationale']} |")
    return lines


def write_markdown(rows: list[dict[str, object]]) -> None:
    """Write consolidated and per-example Markdown reports."""
    EXAMPLE_STUDIES_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = EXAMPLE_STUDIES_ROOT / "results.md"
    average_rubric = sum(int(row["rubric_total"]) for row in rows) / len(rows)
    lines = [
        "# WeaveMark Example Studies",
        "",
        "[View as HTML](results.html)",
        "",
        "## Bottom line",
        "",
        (
            "These studies inspect public example outputs without contrastive controls. "
            "They check whether each example compiles into a useful final prompt, whether "
            "the output fits its stated intention, and whether it avoids leaked directives, "
            "placeholders, brittle meta-commentary, and other pathologies."
        ),
        "",
        "## At a glance",
        "",
        f"- Examples studied: **{len(rows)}**.",
        f"- Average rubric score: **{average_rubric:.1f}/25**.",
        "- Outputs live in their own `examples/.../outputs/` folders.",
        "",
        "## Metric definitions",
        "",
        *metric_definition_lines(CORE_METRIC_DEFINITIONS),
        "- **Rubric:** Sum of five 1-5 quality checks: intention fit, completeness, writing/structure, no leakage/pathologies, and direct usefulness.",
        "",
        "## Example metrics",
        "",
        *metric_table(rows, report_path),
        "",
        "## Detailed rubric",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['title']}",
                "",
                f"- **Intention:** {row['intention']}",
                f"- **Source:** {markdown_link(report_path, Path(str(row['spec_path'])).name, repo_path(str(row['spec_path'])))}",
                f"- **Output:** {markdown_link(report_path, Path(str(row['output_path'])).name, repo_path(str(row['output_path'])))}",
                "",
                *rubric_table(row),
                "",
            ]
        )
        example_dir = EXAMPLE_STUDIES_ROOT / str(row["example_id"])
        example_dir.mkdir(exist_ok=True)
        example_report = example_dir / "results.md"
        example_lines = [
            f"# {row['title']} Example Study",
            "",
            "[View as HTML](results.html)",
            "",
            f"## Intention\n\n{row['intention']}",
            "",
            "## Metrics",
            "",
            *metric_table([row], example_report),
            "",
            "## Rubric",
            "",
            *rubric_table(row),
            "",
        ]
        example_report.write_text(
            "\n".join(example_lines).rstrip() + "\n", encoding="utf-8"
        )
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def rubric_cards(row: dict[str, object]) -> str:
    """Render rubric cards for one example."""
    rubric = row["rubric"]
    assert isinstance(rubric, dict)
    return (
        '<div class="study-grid">'
        + "".join(
            '<article class="card">'
            f"<h3>{escape(criterion)}</h3>"
            f"<p><strong>{result['score']}/5</strong></p>"
            f"<p>{escape(str(result['rationale']))}</p>"
            "</article>"
            for criterion, result in rubric.items()
            if isinstance(result, dict)
        )
        + "</div>"
    )


def write_html(rows: list[dict[str, object]]) -> None:
    """Write consolidated and per-example HTML reports."""
    report_path = EXAMPLE_STUDIES_ROOT / "results.md"
    html_path = html_path_for(report_path)
    average_rubric = sum(int(row["rubric_total"]) for row in rows) / len(rows)
    metric_rows = "".join(
        "<tr>"
        f"<td>{html_link(html_path, str(row['title']), repo_path(str(row['output_path'])))}</td>"
        f"<td class=\"numeric\">{metric_cell(row['metrics']['local_authored_source_words'])}</td>"
        f"<td class=\"numeric\">{metric_cell(row['metrics']['variable_payload_words'])}</td>"
        f"<td class=\"numeric\">{metric_cell(row['metrics']['output_words'])}</td>"
        f"<td class=\"numeric\">{metric_cell(row['metrics']['local_leverage'], 'x')}</td>"
        f"<td class=\"numeric\">{metric_cell(row['metrics']['discounted_fact_units'])}</td>"
        f"<td class=\"numeric\">{metric_cell(row['metrics']['information_density_per_1k_output_words'])}</td>"
        f"<td class=\"numeric\">{metric_cell(row['metrics']['information_yield_per_1k_source_words'])}</td>"
        f"<td class=\"numeric\"><strong>{row['rubric_total']}/25</strong></td>"
        "</tr>"
        for row in rows
    )
    details = details_panel(
        "Metric and rubric definitions",
        definition_cards(CORE_METRIC_DEFINITIONS)
        + definition_cards(
            (
                (
                    "Rubric",
                    "Five 1-5 checks: intention fit, completeness, writing/structure, no leakage/pathologies, and direct usefulness.",
                ),
                (
                    "No leakage/pathologies",
                    "Scans for unresolved directives, placeholders, local paths, WeaveMark internals, TODOs, nulls, and brittle assistant meta-language.",
                ),
            )
        ),
    )
    body = "\n".join(
        [
            section(
                "At a glance",
                '<div class="kpi-grid">'
                + kpi_card("Examples", str(len(rows)), "Curated public plain examples.")
                + kpi_card(
                    "Average rubric",
                    f"{average_rubric:.1f}/25",
                    "Deterministic output-quality checks.",
                )
                + kpi_card(
                    "Controls", "None", "Example studies are absolute, not contrastive."
                )
                + "</div>",
            ),
            details,
            section(
                "Example metrics",
                '<div class="table-wrap"><table>'
                "<thead><tr><th>Example</th><th>Source</th><th>Vars</th><th>Output</th><th>Leverage</th><th>Facts</th><th>Density</th><th>Yield</th><th>Rubric</th></tr></thead>"
                f"<tbody>{metric_rows}</tbody></table></div>",
            ),
            section(
                "Rubric detail",
                '<div class="study-grid">'
                + "".join(
                    '<article class="card">'
                    f"<h3>{escape(str(row['title']))}</h3>"
                    f"<p>{escape(str(row['intention']))}</p>"
                    f"<p><strong>{row['rubric_total']}/25</strong> total rubric score.</p>"
                    f"{html_link(html_path, 'Open output', repo_path(str(row['output_path'])))}"
                    "</article>"
                    for row in rows
                )
                + "</div>",
            ),
        ]
    )
    html_path.write_text(
        html_document(
            "WeaveMark Example Studies",
            "WeaveMark example corpus",
            "Absolute quality checks for public example outputs.",
            body,
            html_path,
            report_path,
        ),
        encoding="utf-8",
    )

    for row in rows:
        example_report = EXAMPLE_STUDIES_ROOT / str(row["example_id"]) / "results.md"
        example_html = example_report.with_suffix(".html")
        example_body = "\n".join(
            [
                section("Intention", f"<p>{escape(str(row['intention']))}</p>"),
                section("Rubric", rubric_cards(row)),
            ]
        )
        example_html.write_text(
            html_document(
                f"{row['title']} Example Study",
                "WeaveMark example study",
                "Absolute quality check for one public example output.",
                example_body,
                example_html,
                example_report,
            ),
            encoding="utf-8",
        )


def clear_reports() -> None:
    """Clear generated example-study reports and metric snapshots."""
    for path in EXAMPLE_STUDIES_ROOT.glob("**/*.md"):
        if path.name == "README.md":
            continue
        path.unlink()
    for path in EXAMPLE_STUDIES_ROOT.glob("**/*.html"):
        path.unlink()
    if EXAMPLE_METRICS_PATH.exists():
        EXAMPLE_METRICS_PATH.unlink()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-examples", action="store_true", help="Compile examples before reporting."
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear generated reports first."
    )
    return parser


def main() -> None:
    """Run the example-study report generator."""
    args = build_parser().parse_args()
    if args.clear:
        clear_reports()
    if args.run_examples:
        run_examples(EXAMPLES)
    rows = [example_metrics(example) for example in EXAMPLES]
    write_json(rows)
    write_markdown(rows)
    write_html(rows)
    print(f"Updated {len(rows)} example-study rows and reports.")


if __name__ == "__main__":
    main()
