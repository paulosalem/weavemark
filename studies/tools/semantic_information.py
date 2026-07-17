"""Compute study-local semantic information metrics."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTROLLED_STUDIES_ROOT = ROOT / "studies/controlled-studies"
WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9'-]*")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "also",
    "and",
    "are",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "can",
    "could",
    "does",
    "each",
    "every",
    "for",
    "from",
    "has",
    "have",
    "into",
    "its",
    "must",
    "not",
    "only",
    "or",
    "other",
    "rather",
    "should",
    "than",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "this",
    "through",
    "use",
    "when",
    "where",
    "with",
    "without",
}


@dataclass(frozen=True)
class Variant:
    """A rendered output and its local authoring/input payload files."""

    study: str
    name: str
    source: Path
    variables: Path | None
    output: Path


VARIANTS = [
    Variant(
        "release-readiness",
        "manual",
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/specs/00-control-manual-release-readiness-workbench.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/outputs/compiled-prompts/00-control-manual-release-readiness-workbench.md",
    ),
    Variant(
        "release-readiness",
        "matched-template",
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/specs/01-control-template-release-readiness-workbench.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/inputs/template-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/outputs/compiled-prompts/01-control-template-release-readiness-workbench.md",
    ),
    Variant(
        "release-readiness",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/specs/02-treatment-promplet-release-readiness-workbench.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/inputs/promplet-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "release-readiness-workbench-ablation-study/outputs/compiled-prompts/02-treatment-promplet-release-readiness-workbench.md",
    ),
    Variant(
        "work-intelligence-kanban",
        "manual",
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/specs/00-control-manual-intelligence-execution-kanban.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/outputs/compiled-prompts/00-control-manual-intelligence-execution-kanban.md",
    ),
    Variant(
        "work-intelligence-kanban",
        "matched-template",
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/specs/01-control-template-intelligence-execution-kanban.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/inputs/template-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/outputs/compiled-prompts/01-control-template-intelligence-execution-kanban.md",
    ),
    Variant(
        "work-intelligence-kanban",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/specs/02-treatment-promplet-intelligence-execution-kanban.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/inputs/promplet-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "intelligence-execution-kanban-ablation-study/outputs/compiled-prompts/02-treatment-promplet-intelligence-execution-kanban.md",
    ),
    Variant(
        "evidence-decision",
        "manual",
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/specs/00-control-manual-evidence-decision-workspace.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/outputs/compiled-prompts/00-control-manual-evidence-decision-workspace.md",
    ),
    Variant(
        "evidence-decision",
        "matched-template",
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/specs/01-control-template-evidence-decision-workspace.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/inputs/template-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/outputs/compiled-prompts/01-control-template-evidence-decision-workspace.md",
    ),
    Variant(
        "evidence-decision",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/specs/02-treatment-promplet-evidence-decision-workspace.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/inputs/promplet-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "evidence-decision-workspace-ablation-study/outputs/compiled-prompts/02-treatment-promplet-evidence-decision-workspace.md",
    ),
    Variant(
        "verdant-relay",
        "manual",
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/specs/00-control-compact-manual-verdant-relay.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/outputs/compiled-prompts/00-control-compact-manual-verdant-relay.md",
    ),
    Variant(
        "verdant-relay",
        "matched-template",
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/specs/01-control-template-verdant-relay.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/inputs/template-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/outputs/compiled-prompts/01-control-template-verdant-relay.md",
    ),
    Variant(
        "verdant-relay",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/specs/02-treatment-promplet-verdant-relay.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/inputs/promplet-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "games/verdant-relay-ablation-study/outputs/compiled-prompts/02-treatment-promplet-verdant-relay.md",
    ),
    Variant(
        "orbital-drift",
        "manual",
        CONTROLLED_STUDIES_ROOT
        / "games/orbital-drift-racing-ablation-study/specs/00-control-manual-orbital-drift.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/orbital-drift-racing-ablation-study/outputs/compiled-prompts/00-control-manual-orbital-drift.md",
    ),
    Variant(
        "orbital-drift",
        "matched-template",
        CONTROLLED_STUDIES_ROOT
        / "games/orbital-drift-racing-ablation-study/specs/01-control-template-orbital-drift.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "games/orbital-drift-racing-ablation-study/inputs/template-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "games/orbital-drift-racing-ablation-study/outputs/compiled-prompts/01-control-template-orbital-drift.md",
    ),
    Variant(
        "orbital-drift",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "games/orbital-drift-racing-ablation-study/specs/02-treatment-promplet-orbital-drift.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/orbital-drift-racing-ablation-study/outputs/compiled-prompts/02-treatment-promplet-orbital-drift.md",
    ),
    Variant(
        "learning-tutor",
        "manual",
        CONTROLLED_STUDIES_ROOT
        / "learning-tutor-refinement-ablation-study/specs/00-control-compact-manual-linear-algebra-tutor.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "learning-tutor-refinement-ablation-study/outputs/compiled-prompts/00-control-compact-manual-linear-algebra-tutor.md",
    ),
    Variant(
        "learning-tutor",
        "matched-prose",
        CONTROLLED_STUDIES_ROOT
        / "learning-tutor-refinement-ablation-study/specs/01-control-matched-prose-linear-algebra-tutor.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "learning-tutor-refinement-ablation-study/outputs/compiled-prompts/01-control-matched-prose-linear-algebra-tutor.md",
    ),
    Variant(
        "learning-tutor",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "learning-tutor-refinement-ablation-study/specs/02-treatment-refined-expand-linear-algebra-tutor.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "learning-tutor-refinement-ablation-study/inputs/treatment-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "learning-tutor-refinement-ablation-study/outputs/compiled-prompts/02-treatment-refined-expand-linear-algebra-tutor.md",
    ),
    Variant(
        "transit-city-swarm",
        "compact-no-expand",
        CONTROLLED_STUDIES_ROOT
        / "games/transit-city-swarm-ablation-study/specs/00-control-compact-no-expand-transit-city-swarm.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/transit-city-swarm-ablation-study/outputs/compiled-prompts/00-control-compact-no-expand-transit-city-swarm.md",
    ),
    Variant(
        "transit-city-swarm",
        "matched-prose",
        CONTROLLED_STUDIES_ROOT
        / "games/transit-city-swarm-ablation-study/specs/01-control-matched-prose-no-expand-transit-city-swarm.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/transit-city-swarm-ablation-study/outputs/compiled-prompts/01-control-matched-prose-no-expand-transit-city-swarm.md",
    ),
    Variant(
        "transit-city-swarm",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "games/transit-city-swarm-ablation-study/specs/02-treatment-expand-transit-city-swarm.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/transit-city-swarm-ablation-study/outputs/compiled-prompts/02-treatment-expand-transit-city-swarm.md",
    ),
    Variant(
        "crowd-factory-puzzle",
        "compact-no-expand",
        CONTROLLED_STUDIES_ROOT
        / "games/crowd-factory-puzzle-ablation-study/specs/00-control-compact-no-expand-crowd-factory-puzzle.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/crowd-factory-puzzle-ablation-study/outputs/compiled-prompts/00-control-compact-no-expand-crowd-factory-puzzle.md",
    ),
    Variant(
        "crowd-factory-puzzle",
        "matched-prose",
        CONTROLLED_STUDIES_ROOT
        / "games/crowd-factory-puzzle-ablation-study/specs/01-control-matched-prose-no-expand-crowd-factory-puzzle.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/crowd-factory-puzzle-ablation-study/outputs/compiled-prompts/01-control-matched-prose-no-expand-crowd-factory-puzzle.md",
    ),
    Variant(
        "crowd-factory-puzzle",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "games/crowd-factory-puzzle-ablation-study/specs/02-treatment-expand-crowd-factory-puzzle.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "games/crowd-factory-puzzle-ablation-study/outputs/compiled-prompts/02-treatment-expand-crowd-factory-puzzle.md",
    ),
    Variant(
        "research-brief",
        "manual",
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/specs/00-control-manual-research-brief.weavemark.md",
        None,
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/outputs/compiled-prompts/00-control-manual-research-brief.md",
    ),
    Variant(
        "research-brief",
        "matched-template",
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/specs/01-control-template-research-brief.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/inputs/template-vars.json",
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/outputs/compiled-prompts/01-control-template-research-brief.md",
    ),
    Variant(
        "research-brief",
        "promplet",
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/specs/02-treatment-refined-research-brief.weavemark.md",
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/inputs/energy-storage.json",
        CONTROLLED_STUDIES_ROOT
        / "research-brief-ablation-study/outputs/compiled-prompts/02-treatment-refined-research-brief.md",
    ),
]


def words(text: str) -> list[str]:
    """Return word-like tokens."""
    return WORD_PATTERN.findall(text)


def word_count(path: Path | None) -> int:
    """Count whitespace-like words in a text file."""
    if path is None:
        return 0
    return len(path.read_text().split())


def chunks(text: str, max_words: int = 650) -> list[str]:
    """Split text into word-bounded chunks before fact extraction."""
    paragraphs = [
        paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()
    ]
    result: list[str] = []
    current: list[str] = []
    current_words = 0
    for paragraph in paragraphs:
        count = len(words(paragraph))
        if current and current_words + count > max_words:
            result.append("\n\n".join(current))
            current = []
            current_words = 0
        current.append(paragraph)
        current_words += count
    if current:
        result.append("\n\n".join(current))
    return result


def candidate_facts(text: str) -> list[str]:
    """Extract atomic fact candidates from chunks using deterministic rules."""
    facts: list[str] = []
    for chunk in chunks(text):
        for raw_line in chunk.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("|"):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if len(cells) > 2 and not all(
                    set(cell) <= {"-", ":"} for cell in cells
                ):
                    line = "; ".join(cell for cell in cells if cell)
                else:
                    continue
            if line.startswith(("-", "*")):
                facts.append(line.lstrip("-* ").strip())
                continue
            for sentence in SENTENCE_SPLIT.split(line):
                sentence = sentence.strip()
                if sentence:
                    facts.append(sentence)
    return [fact for fact in facts if len(normalize_tokens(fact)) >= 4]


def normalize_tokens(text: str) -> frozenset[str]:
    """Normalize a fact into a token set for similarity scoring."""
    return frozenset(
        token.lower().strip("'")
        for token in words(text)
        if len(token) > 2 and token.lower() not in STOPWORDS
    )


def similarity(left: frozenset[str], right: frozenset[str]) -> float:
    """Return Jaccard similarity for two normalized fact token sets."""
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def difference_score(max_similarity: float) -> int:
    """Map closest similarity to the 0-4 novelty score."""
    if max_similarity >= 0.92:
        return 0
    if max_similarity >= 0.78:
        return 1
    if max_similarity >= 0.58:
        return 2
    if max_similarity >= 0.32:
        return 3
    return 4


def discounted_fact_units(text: str) -> dict[str, float | int]:
    """Compute discounted semantic fact units for an output."""
    accepted: list[frozenset[str]] = []
    candidates = candidate_facts(text)
    total = 0.0
    counted = 0
    for fact in candidates:
        tokens = normalize_tokens(fact)
        closest = max((similarity(tokens, prior) for prior in accepted), default=0.0)
        score = difference_score(closest)
        if score:
            accepted.append(tokens)
            counted += 1
        total += score / 4
    return {
        "candidate_facts": len(candidates),
        "counted_facts": counted,
        "discounted_fact_units": round(total, 2),
    }


def variant_metrics(variant: Variant) -> dict[str, float | int | str]:
    """Compute metrics for one study variant."""
    output_text = variant.output.read_text()
    output_words = len(output_text.split())
    local_words = word_count(variant.source)
    variable_payload_words = word_count(variant.variables)
    facts = discounted_fact_units(output_text)
    fact_units = float(facts["discounted_fact_units"])
    return {
        "study": variant.study,
        "variant": variant.name,
        "local_authored_source_words": local_words,
        "variable_payload_words": variable_payload_words,
        "output_words": output_words,
        "local_leverage": round(output_words / local_words, 2) if local_words else 0,
        **facts,
        "information_density_per_1k_output_words": (
            round(fact_units / output_words * 1000, 1) if output_words else 0
        ),
        "information_yield_per_1k_source_words": (
            round(fact_units / local_words * 1000, 1) if local_words else 0
        ),
    }


def main() -> None:
    """Write the semantic information metric snapshot."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=CONTROLLED_STUDIES_ROOT / "metrics/semantic-information.json",
    )
    args = parser.parse_args()

    metrics = [variant_metrics(variant) for variant in VARIANTS]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
