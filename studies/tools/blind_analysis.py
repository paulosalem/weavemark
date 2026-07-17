"""Create, score, and reveal randomized blind WeaveMark study analyses."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import secrets
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from regenerate_reports import (  # noqa: E402
    BLIND_METRIC_DEFINITIONS,
    CRITERIA,
    SCORE_METRIC_DEFINITIONS,
    STUDIES,
    html_document,
    kpi_card,
    metric_definition_lines,
    metric_definitions_panel,
    score_heat_cell,
    score_text,
    section,
)
from semantic_information import (  # noqa: E402
    ROOT,
    VARIANTS,
    candidate_facts,
    variant_metrics,
)

ANONYMOUS_IDS = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
DEFAULT_OUTPUT_ROOT = ROOT / "outputs/studies/blind-analysis"
SCHEMA_VERSION = 1
DERIVED_METRIC_CRITERIA = ("Authoring leverage", "Information yield")
MASKED_REVIEW_CRITERIA = (
    "Grounded expressiveness",
    "Input readability",
    "Output readability",
    "Constraint integration",
    "Reusable abstraction quality",
)
CRITERION_METHODS = {
    "Authoring leverage": {
        "blindness": "derived-evidence",
        "method": "Ranked from local leverage without exposing variant identity.",
        "leakage_risk": "Low: uses automated counts and ratios only.",
    },
    "Information yield": {
        "blindness": "derived-evidence",
        "method": "Ranked from discounted fact units per local source word.",
        "leakage_risk": "Low-to-moderate: fact extraction reads artifacts, but scoring uses derived counts.",
    },
    "Grounded expressiveness": {
        "blindness": "masked-source-output review",
        "method": "Independent review reads masked source/output because richness and grounding are semantic judgments.",
        "leakage_risk": "Moderate: domain content and style may leak even after identity masking.",
    },
    "Input readability": {
        "blindness": "masked-source review",
        "method": "Independent review reads masked source text because readability is not reducible to source length.",
        "leakage_risk": "Moderate: source syntax/style may reveal the authoring approach.",
    },
    "Output readability": {
        "blindness": "masked-output review",
        "method": "Independent review reads masked output text because readability is not reducible to density or brevity.",
        "leakage_risk": "Moderate: output style/domain content may leak.",
    },
    "Constraint integration": {
        "blindness": "masked-source-output review",
        "method": "Independent review reads masked source/output to judge whether constraints are woven into the artifact.",
        "leakage_risk": "Moderate: domain content and artifact structure may leak.",
    },
    "Reusable abstraction quality": {
        "blindness": "masked-source review",
        "method": "Independent review reads masked source to judge abstraction clarity and reuse.",
        "leakage_risk": "Moderate-to-high: abstraction syntax can leak authoring style, but reading it is necessary for reliability.",
    },
}
METRIC_ONLY_METHODS = {
    criterion: {
        "blindness": "derived-evidence metric proxy",
        "method": (
            "Ranked from automated derived metrics only. This is useful for mechanical "
            "checks but is not reliable for subjective reading-dependent criteria."
        ),
        "leakage_risk": "Low-to-moderate: artifact text is processed automatically, but the score uses derived values.",
    }
    for criterion in CRITERIA
}
METRIC_ONLY_LEAK_RISK_NOTE = (
    "Metric-only derived-evidence scoring minimizes identity leakage, but subjective "
    "criteria such as readability, constraint integration, and abstraction quality are "
    "only proxies in this mode."
)
HYBRID_LEAK_RISK_NOTE = (
    "Hybrid blind* scoring uses derived metrics for mechanical criteria and masked "
    "source/output review for criteria that require actual reading. The masked review "
    "is less blind because domain content, source syntax, or style can leak, but this "
    "is necessary to avoid replacing readability and integration judgments with weak "
    "length/density proxies."
)

IDENTITY_REPLACEMENTS = (
    (re.compile(r"\[C1\]|\[C2\]|\[T\]", re.IGNORECASE), "[VARIANT]"),
    (re.compile(r"\b(?:WeaveMark|WeaveMark)\b", re.IGNORECASE), "Framework-X"),
    (re.compile(r"\b(?:promplet|weavemark)\b", re.IGNORECASE), "framework-x"),
    (re.compile(r"\bcontrols\b", re.IGNORECASE), "variants"),
    (re.compile(r"\bcontrol\b", re.IGNORECASE), "variant"),
    (re.compile(r"\btreatments\b", re.IGNORECASE), "variants"),
    (re.compile(r"\btreatment\b", re.IGNORECASE), "variant"),
    (re.compile(r"\bmatched[- ]template\b", re.IGNORECASE), "variant pattern"),
    (re.compile(r"\bmatched[- ]prose\b", re.IGNORECASE), "variant prose"),
    (re.compile(r"\bmanual\b", re.IGNORECASE), "compact"),
    (re.compile(r"@refine\b", re.IGNORECASE), "@directive-a"),
    (re.compile(r"@expand\b", re.IGNORECASE), "@directive-b"),
    (re.compile(r"@compress\b", re.IGNORECASE), "@directive-c"),
)

LEAK_PATTERNS = (
    re.compile(r"\[C1\]|\[C2\]|\[T\]", re.IGNORECASE),
    re.compile(r"\b(?:WeaveMark|WeaveMark)\b", re.IGNORECASE),
    re.compile(r"\bcontrol\b|\btreatment\b", re.IGNORECASE),
    re.compile(r"@refine\b|@expand\b|@compress\b", re.IGNORECASE),
)


def rel(path: Path, base: Path = ROOT) -> str:
    """Return a POSIX path relative to the repository root when possible."""
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def sha256_text(text: str) -> str:
    """Return the SHA-256 digest for text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    """Read a UTF-8 text file."""
    return path.read_text(encoding="utf-8")


def mask_identity_terms(text: str) -> str:
    """Mask direct labels that would reveal control/treatment identity."""
    masked = text
    for pattern, replacement in IDENTITY_REPLACEMENTS:
        masked = pattern.sub(replacement, masked)
    return masked


def leak_counts(text: str) -> dict[str, int]:
    """Count direct identity leaks still present in a packet."""
    return {
        f"pattern_{index + 1}": len(pattern.findall(text))
        for index, pattern in enumerate(LEAK_PATTERNS)
    }


def study_map() -> dict[str, Any]:
    """Return StudySpec records by study id."""
    return {study.study_id: study for study in STUDIES}


def variants_by_study() -> dict[str, list[Any]]:
    """Group semantic-information variants by study id."""
    grouped: dict[str, list[Any]] = {}
    for variant in VARIANTS:
        grouped.setdefault(variant.study, []).append(variant)
    return grouped


def write_json(path: Path, payload: object) -> None:
    """Write stable, readable JSON."""
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def clean_fact(text: str) -> str:
    """Mask identity terms and collapse whitespace in one extracted fact."""
    return " ".join(mask_identity_terms(text).split())


def derived_evidence(variant: Any) -> dict[str, Any]:
    """Extract derived evidence without exposing raw source or output text."""
    output_text = read_text(variant.output)
    metrics = variant_metrics(variant)
    facts = [clean_fact(fact) for fact in candidate_facts(output_text)]
    return {
        "metrics": metrics,
        "fact_candidates": facts,
        "fact_candidate_count": len(facts),
        "artifact_hashes": {
            "source_sha256": sha256_text(read_text(variant.source)),
            "variables_sha256": (
                sha256_text(read_text(variant.variables)) if variant.variables else None
            ),
            "output_sha256": sha256_text(output_text),
        },
    }


def derived_packet_text(
    study_title: str,
    anonymous_id: str,
    evidence: dict[str, Any],
    evidence_path: Path,
) -> str:
    """Build a blind packet from derived evidence only."""
    metrics = evidence["metrics"]
    facts = evidence["fact_candidates"]
    fact_lines = "\n".join(f"- {escape_markdown(fact)}" for fact in facts[:60])
    if len(facts) > 60:
        fact_lines += f"\n- ... {len(facts) - 60} additional facts in JSON evidence."
    return "\n".join(
        [
            "# Blind derived-evidence packet",
            "",
            f"Study: {study_title}",
            f"Variant: {anonymous_id}",
            "Mode: derived-evidence",
            "",
            (
                "Evaluate this anonymous variant from automated measurements and "
                "extracted fact candidates only. Do not open raw source/output files "
                "or the private derandomization key."
            ),
            "",
            "## Derived metric summary",
            "",
            f"- Local authored source words: {metrics['local_authored_source_words']}",
            f"- Variable payload words: {metrics['variable_payload_words']}",
            f"- Output words: {metrics['output_words']}",
            f"- Local leverage: {metrics['local_leverage']}x",
            f"- Candidate facts: {metrics['candidate_facts']}",
            f"- Counted facts: {metrics['counted_facts']}",
            f"- Discounted fact units: {metrics['discounted_fact_units']}",
            (
                "- Information density per 1k output words: "
                f"{metrics['information_density_per_1k_output_words']}"
            ),
            (
                "- Information yield per 1k source words: "
                f"{metrics['information_yield_per_1k_source_words']}"
            ),
            "",
            "## Extracted fact candidates",
            "",
            fact_lines,
            "",
            "## Evidence file",
            "",
            f"Full derived evidence JSON: `{rel(evidence_path)}`",
            "",
        ]
    )


def escape_markdown(text: str) -> str:
    """Escape only Markdown list-breaking backslashes in extracted facts."""
    return text.replace("\\", "\\\\")


def packet_text(
    study_title: str,
    anonymous_id: str,
    variant: Any,
    mode: str,
) -> str:
    """Build one anonymized packet."""
    output = mask_identity_terms(read_text(variant.output))
    sections = [
        "# Blind evaluation packet",
        "",
        f"Study: {study_title}",
        f"Variant: {anonymous_id}",
        f"Mode: {mode}",
        "",
        (
            "Evaluate only the anonymous artifact content. Do not use filenames, "
            "marker guesses, known study history, or presumed authoring condition."
        ),
        "",
    ]
    if mode == "source-and-output":
        sections.extend(
            [
                "## Source material",
                "",
                mask_identity_terms(read_text(variant.source)),
                "",
            ]
        )
        if variant.variables is not None:
            sections.extend(
                [
                    "## Variable payload",
                    "",
                    mask_identity_terms(read_text(variant.variables)),
                    "",
                ]
            )
    sections.extend(["## Compiled output", "", output, ""])
    return "\n".join(sections)


def prepare_blind_run(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    run_id: str | None = None,
    seed: int | None = None,
    mode: str = "derived-evidence",
    force: bool = False,
) -> Path:
    """Create randomized packet files plus a private derandomization key."""
    valid_modes = {"derived-evidence", "compiled-output", "source-and-output"}
    if mode not in valid_modes:
        raise ValueError(f"mode must be one of: {', '.join(sorted(valid_modes))}.")

    created_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    resolved_seed = seed if seed is not None else secrets.randbits(64)
    resolved_run_id = run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / resolved_run_id
    if run_dir.exists():
        if not force:
            raise FileExistsError(f"Blind analysis run already exists: {run_dir}")
        shutil.rmtree(run_dir)

    packets_dir = run_dir / "packets"
    evidence_dir = run_dir / "derived-evidence"
    private_dir = run_dir / "private"
    packets_dir.mkdir(parents=True)
    evidence_dir.mkdir()
    private_dir.mkdir()

    rng = random.Random(resolved_seed)
    studies = study_map()
    grouped = variants_by_study()
    manifest_studies = []
    key_studies: dict[str, dict[str, dict[str, str | None]]] = {}
    template_studies = []

    for study_id in sorted(grouped):
        variants = list(grouped[study_id])
        if len(variants) > len(ANONYMOUS_IDS):
            raise ValueError(f"Too many variants to anonymize for study: {study_id}")
        anonymous_ids = list(ANONYMOUS_IDS[: len(variants)])
        rng.shuffle(anonymous_ids)
        study = studies[study_id]
        study_packet_dir = packets_dir / study_id
        study_evidence_dir = evidence_dir / study_id
        study_packet_dir.mkdir()
        study_evidence_dir.mkdir()
        manifest_packets = []
        key_studies[study_id] = {}
        template_variants = []

        for anonymous_id, variant in zip(anonymous_ids, variants, strict=True):
            evidence_path = study_evidence_dir / f"{anonymous_id}.json"
            if mode == "derived-evidence":
                evidence = derived_evidence(variant)
                write_json(evidence_path, evidence)
                packet = derived_packet_text(
                    study.title, anonymous_id, evidence, evidence_path
                )
            else:
                packet = packet_text(study.title, anonymous_id, variant, mode)
            packet_path = study_packet_dir / f"{anonymous_id}.md"
            packet_path.write_text(packet, encoding="utf-8")
            manifest_packet = {
                "anonymous_id": anonymous_id,
                "packet": rel(packet_path),
                "packet_sha256": sha256_text(packet),
                "leak_counts_after_masking": leak_counts(packet),
            }
            if mode == "derived-evidence":
                manifest_packet["derived_evidence"] = rel(evidence_path)
            manifest_packets.append(manifest_packet)
            key_studies[study_id][anonymous_id] = {
                "variant": variant.name,
                "source": rel(variant.source),
                "variables": rel(variant.variables) if variant.variables else None,
                "output": rel(variant.output),
            }
            template_variants.append(
                {
                    "anonymous_id": anonymous_id,
                    "scores": {criterion: None for criterion in CRITERIA},
                    "notes": "",
                }
            )

        manifest_studies.append(
            {
                "study_id": study_id,
                "title": study.title,
                "packets": sorted(
                    manifest_packets, key=lambda packet: str(packet["anonymous_id"])
                ),
            }
        )
        template_studies.append(
            {
                "study_id": study_id,
                "title": study.title,
                "variants": sorted(
                    template_variants, key=lambda item: str(item["anonymous_id"])
                ),
            }
        )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": resolved_run_id,
        "created_at": created_at,
        "mode": mode,
        "seed_sha256": hashlib.sha256(str(resolved_seed).encode()).hexdigest(),
        "criteria": list(CRITERIA),
        "score_scale": "Absolute 1..7 per criterion before derandomization.",
        "blindness_note": (
            "The manifest intentionally omits variant identities. Do not open "
            "private/key.json until blinded scoring is complete. The default "
            "derived-evidence mode avoids raw text review; raw-text modes are "
            "identity-blinded but can still reveal intrinsic authoring style."
        ),
        "score_template": rel(run_dir / "blinded_scores.template.json"),
        "studies": manifest_studies,
    }
    key = {
        "schema_version": SCHEMA_VERSION,
        "run_id": resolved_run_id,
        "seed": resolved_seed,
        "mode": mode,
        "studies": key_studies,
    }
    template = {
        "schema_version": SCHEMA_VERSION,
        "run_id": resolved_run_id,
        "mode": mode,
        "score_scale": "Absolute 1..7 per criterion; higher is better.",
        "criteria": list(CRITERIA),
        "studies": template_studies,
    }

    write_json(run_dir / "manifest.json", manifest)
    write_json(private_dir / "key.json", key)
    write_json(run_dir / "blinded_scores.template.json", template)
    validate_blind_run(run_dir)
    return run_dir


def score_from_rank(
    value: float, values: list[float], higher_is_better: bool = True
) -> int:
    """Map a value to a 1..7 score by rank within one study."""
    ordered = sorted(set(values), reverse=not higher_is_better)
    if len(ordered) == 1:
        return 4
    position = ordered.index(value)
    return int(round(1 + (position / (len(ordered) - 1)) * 6))


def metric_score_payload(run_dir: Path) -> dict[str, Any]:
    """Create anonymous metric-only scores without exposing the key in output."""
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    key = json.loads((run_dir / "private/key.json").read_text(encoding="utf-8"))
    rows = {
        (variant.study, variant.name): variant_metrics(variant) for variant in VARIANTS
    }
    grouped = variants_by_study()
    studies_payload = []

    for study_entry in manifest["studies"]:
        study_id = study_entry["study_id"]
        study_variants = grouped[study_id]
        study_metrics = {
            variant.name: rows[(study_id, variant.name)] for variant in study_variants
        }
        metric_values = {
            metric: [float(metrics[metric]) for metrics in study_metrics.values()]
            for metric in (
                "local_leverage",
                "information_yield_per_1k_source_words",
                "discounted_fact_units",
                "local_authored_source_words",
                "information_density_per_1k_output_words",
                "counted_facts",
            )
        }

        variants_payload = []
        for packet in study_entry["packets"]:
            anonymous_id = packet["anonymous_id"]
            variant_name = key["studies"][study_id][anonymous_id]["variant"]
            metrics = study_metrics[variant_name]
            scores = {
                "Authoring leverage": score_from_rank(
                    float(metrics["local_leverage"]), metric_values["local_leverage"]
                ),
                "Information yield": score_from_rank(
                    float(metrics["information_yield_per_1k_source_words"]),
                    metric_values["information_yield_per_1k_source_words"],
                ),
                "Grounded expressiveness": score_from_rank(
                    float(metrics["discounted_fact_units"]),
                    metric_values["discounted_fact_units"],
                ),
                "Input readability": score_from_rank(
                    float(metrics["local_authored_source_words"]),
                    metric_values["local_authored_source_words"],
                    higher_is_better=False,
                ),
                "Output readability": score_from_rank(
                    float(metrics["information_density_per_1k_output_words"]),
                    metric_values["information_density_per_1k_output_words"],
                ),
                "Constraint integration": score_from_rank(
                    float(metrics["counted_facts"]), metric_values["counted_facts"]
                ),
                "Reusable abstraction quality": score_from_rank(
                    float(metrics["local_leverage"]), metric_values["local_leverage"]
                ),
            }
            variants_payload.append(
                {
                    "anonymous_id": anonymous_id,
                    "scores": scores,
                    "notes": (
                        "Metric-only blind score from saved source/output measurements; "
                        "use human or LLM blinded judging for qualitative claims."
                    ),
                }
            )
        studies_payload.append(
            {
                "study_id": study_id,
                "title": study_entry["title"],
                "variants": sorted(
                    variants_payload, key=lambda item: str(item["anonymous_id"])
                ),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "mode": manifest["mode"],
        "score_scale": "Absolute 1..7 per criterion; higher is better.",
        "score_source": "metric-only",
        "criterion_methods": METRIC_ONLY_METHODS,
        "leak_risk_note": METRIC_ONLY_LEAK_RISK_NOTE,
        "criteria": list(CRITERIA),
        "studies": studies_payload,
    }


def write_metric_scores(run_dir: Path) -> Path:
    """Write anonymous metric-only scores for a prepared run."""
    output_path = run_dir / "blinded_scores.metrics.json"
    payload = metric_score_payload(run_dir)
    validate_score_payload(run_dir, payload)
    write_json(output_path, payload)
    return output_path


def hybrid_score_payload(
    run_dir: Path, qualitative_scores_path: Path
) -> dict[str, Any]:
    """Combine derived metric criteria with masked-review qualitative scores."""
    metric_payload = metric_score_payload(run_dir)
    qualitative_payload = json.loads(
        qualitative_scores_path.read_text(encoding="utf-8")
    )
    validate_score_payload(
        run_dir, qualitative_payload, expected_criteria=MASKED_REVIEW_CRITERIA
    )
    qualitative = score_lookup(qualitative_payload)

    studies_payload = []
    for study in metric_payload["studies"]:
        variants_payload = []
        for variant in study["variants"]:
            key = (study["study_id"], variant["anonymous_id"])
            scores = {
                criterion: int(variant["scores"][criterion])
                for criterion in DERIVED_METRIC_CRITERIA
            }
            scores.update(
                {
                    criterion: qualitative[key][criterion]
                    for criterion in MASKED_REVIEW_CRITERIA
                }
            )
            variants_payload.append(
                {
                    "anonymous_id": variant["anonymous_id"],
                    "scores": scores,
                    "notes": (
                        "Hybrid blind* score: mechanical criteria from derived metrics; "
                        "semantic/readability criteria from independent masked source/output review."
                    ),
                }
            )
        studies_payload.append(
            {
                "study_id": study["study_id"],
                "title": study["title"],
                "variants": variants_payload,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": metric_payload["run_id"],
        "mode": metric_payload["mode"],
        "score_scale": "Absolute 1..7 per criterion; higher is better.",
        "score_source": "hybrid-derived-metrics-and-masked-review",
        "criteria": list(CRITERIA),
        "criterion_methods": CRITERION_METHODS,
        "leak_risk_note": HYBRID_LEAK_RISK_NOTE,
        "studies": studies_payload,
    }


def write_hybrid_scores(run_dir: Path, qualitative_scores_path: Path) -> Path:
    """Write hybrid anonymous scores for a prepared masked-review run."""
    output_path = run_dir / "blinded_scores.hybrid.json"
    payload = hybrid_score_payload(run_dir, qualitative_scores_path)
    validate_score_payload(run_dir, payload)
    write_json(output_path, payload)
    return output_path


def contrastive_delta(treatment_score: int, control_score: int) -> int:
    """Map two 1..7 absolute scores onto the -3..+3 contrastive scale."""
    difference = treatment_score - control_score
    if difference == 0:
        return 0
    magnitude = min(3, math.ceil(abs(difference) / 2))
    return magnitude if difference > 0 else -magnitude


def score_lookup(
    score_payload: dict[str, Any],
) -> dict[tuple[str, str], dict[str, int]]:
    """Return scores keyed by study and anonymous id."""
    lookup: dict[tuple[str, str], dict[str, int]] = {}
    for study in score_payload["studies"]:
        for variant in study["variants"]:
            lookup[(study["study_id"], variant["anonymous_id"])] = {
                criterion: int(score)
                for criterion, score in variant["scores"].items()
                if score is not None
            }
    return lookup


def validate_blind_run(run_dir: Path) -> None:
    """Validate that a prepared blind run is internally complete."""
    manifest_path = run_dir / "manifest.json"
    key_path = run_dir / "private/key.json"
    template_path = run_dir / "blinded_scores.template.json"
    for path in (manifest_path, key_path, template_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing blind-run artifact: {rel(path)}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    key = json.loads(key_path.read_text(encoding="utf-8"))
    template = json.loads(template_path.read_text(encoding="utf-8"))
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Blind manifest schema version does not match the tool.")
    if key["run_id"] != manifest["run_id"] or template["run_id"] != manifest["run_id"]:
        raise ValueError("Blind run artifacts disagree on run_id.")
    if template["criteria"] != list(CRITERIA):
        raise ValueError("Blind score template criteria are stale.")

    studies = study_map()
    for study_entry in manifest["studies"]:
        study_id = study_entry["study_id"]
        if study_id not in studies:
            raise ValueError(f"Unknown study in blind manifest: {study_id}")
        anonymous_ids = [packet["anonymous_id"] for packet in study_entry["packets"]]
        if len(anonymous_ids) != len(set(anonymous_ids)):
            raise ValueError(f"Duplicate anonymous IDs in {study_id}.")
        key_ids = set(key["studies"][study_id])
        if set(anonymous_ids) != key_ids:
            raise ValueError(f"Manifest/key anonymous IDs disagree in {study_id}.")
        for packet in study_entry["packets"]:
            packet_path = ROOT / packet["packet"]
            evidence_path = packet.get("derived_evidence")
            if not packet_path.exists():
                raise FileNotFoundError(f"Missing blind packet: {rel(packet_path)}")
            if evidence_path is not None and not (ROOT / evidence_path).exists():
                raise FileNotFoundError(f"Missing derived evidence: {evidence_path}")


def validate_score_payload(
    run_dir: Path,
    score_payload: dict[str, Any],
    expected_criteria: tuple[str, ...] = CRITERIA,
) -> None:
    """Validate anonymous scores before writing or revealing them."""
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if score_payload["run_id"] != manifest["run_id"]:
        raise ValueError("Score payload run_id does not match the blind run.")
    if score_payload["criteria"] != list(expected_criteria):
        raise ValueError("Score payload criteria are stale.")

    manifest_packets = {
        (study["study_id"], packet["anonymous_id"])
        for study in manifest["studies"]
        for packet in study["packets"]
    }
    score_packets = {
        (study["study_id"], variant["anonymous_id"])
        for study in score_payload["studies"]
        for variant in study["variants"]
    }
    if score_packets != manifest_packets:
        raise ValueError("Score payload does not cover exactly the manifest packets.")

    for study in score_payload["studies"]:
        for variant in study["variants"]:
            scores = variant["scores"]
            if set(scores) != set(expected_criteria):
                raise ValueError(
                    f"Scores for {study['study_id']} / {variant['anonymous_id']} do not cover every criterion."
                )
            for criterion, score in scores.items():
                if not isinstance(score, int) or not 1 <= score <= 7:
                    raise ValueError(
                        f"Invalid score for {study['study_id']} / {variant['anonymous_id']} / {criterion}: {score}"
                    )


def write_reveal_json(
    output_path: Path,
    manifest: dict[str, Any],
    score_source: str,
    caveat: str,
    criterion_methods: dict[str, Any],
    study_results: list[dict[str, Any]],
    total_delta: int,
) -> None:
    """Write the structured public reveal artifact used by report generation."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "mode": manifest["mode"],
        "score_source": score_source,
        "score_scale": "-3..+3 treatment-control contrastive delta after reveal.",
        "leak_risk_note": caveat.replace("Caveat: ", ""),
        "criterion_methods": criterion_methods,
        "aggregate_delta": total_delta,
        "studies": study_results,
    }
    write_json(output_path, payload)


def write_reveal_html(
    html_path: Path,
    markdown_path: Path,
    manifest: dict[str, Any],
    score_source: str,
    caveat: str,
    criterion_methods: dict[str, Any],
    study_results: list[dict[str, Any]],
    total_delta: int,
) -> None:
    """Write a polished HTML companion for the derandomized blind report."""
    method_rows = "".join(
        "<tr>"
        f"<td>{criterion}</td>"
        f"<td>{details['blindness']}</td>"
        f"<td>{details['method']}</td>"
        f"<td>{details['leakage_risk']}</td>"
        "</tr>"
        for criterion, details in criterion_methods.items()
    )
    study_cards = []
    for study in study_results:
        variants = "".join(
            "<tr>"
            f"<td>{variant['label']}</td>"
            f"<td><strong>{variant['anonymous_id']}</strong></td>"
            f"<td class=\"numeric\">{variant['mean_score']:.2f}</td>"
            "</tr>"
            for variant in study["variants"]
        )
        deltas = "".join(
            "<tr>"
            f"<td>{row['criterion']}</td>"
            f"<td class=\"numeric\">{row['control_score']}</td>"
            f"<td class=\"numeric\">{row['treatment_score']}</td>"
            f"{score_heat_cell(row['delta'], 'total-col total-heat')}"
            "</tr>"
            for row in study["deltas"]
        )
        study_cards.append(
            '<article class="card">'
            f"<h3>{study['title']}</h3>"
            '<div class="table-wrap"><table class="blind-score-table">'
            '<thead><tr><th>Variant</th><th>Anon.</th><th class="numeric">Mean</th></tr></thead>'
            f"<tbody>{variants}</tbody></table></div>"
            '<div class="table-wrap"><table class="blind-score-table">'
            '<thead><tr><th>Criterion</th><th class="numeric">Control</th>'
            '<th class="numeric">Treatment</th><th>Delta</th></tr></thead>'
            f"<tbody>{deltas}</tbody></table></div>"
            f"<p>{score_text(study['total'])} blind contrastive total.</p>"
            "</article>"
        )

    body = "\n".join(
        [
            section(
                "At a glance",
                '<div class="kpi-grid">'
                + kpi_card(
                    "Blind delta",
                    score_text(total_delta),
                    "Aggregate derandomized blind contrastive signal.",
                )
                + kpi_card("Mode", str(manifest["mode"]), str(score_source))
                + kpi_card(
                    "Run", str(manifest["run_id"]), "Derandomized after scoring."
                )
                + "</div>",
                caveat.replace("Caveat: ", ""),
            ),
            metric_definitions_panel(
                BLIND_METRIC_DEFINITIONS + SCORE_METRIC_DEFINITIONS
            ),
            section(
                "Criterion-specific blindness",
                '<div class="table-wrap"><table>'
                "<thead><tr><th>Criterion</th><th>Blindness level</th><th>Method</th><th>Leakage risk</th></tr></thead>"
                f"<tbody>{method_rows}</tbody></table></div>",
                "Some criteria require masked reading to avoid unreliable length/density proxies.",
            ),
            section(
                "Per-study blind results",
                f'<div class="study-grid">{"".join(study_cards)}</div>',
            ),
        ]
    )
    html_path.write_text(
        html_document(
            "Blind Study Analysis",
            "Derived-evidence blind check",
            "Anonymous derived metrics and extracted fact candidates are scored before revealing variant identities.",
            body,
            html_path,
            markdown_path,
        ),
        encoding="utf-8",
    )


def reveal_scores(run_dir: Path, scores_path: Path | None = None) -> Path:
    """Derandomize blinded scores and write a Markdown report."""
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    key = json.loads((run_dir / "private/key.json").read_text(encoding="utf-8"))
    resolved_scores_path = scores_path or run_dir / "blinded_scores.metrics.json"
    score_payload = json.loads(resolved_scores_path.read_text(encoding="utf-8"))
    validate_blind_run(run_dir)
    validate_score_payload(run_dir, score_payload)
    scores = score_lookup(score_payload)
    studies = study_map()
    score_source = str(score_payload.get("score_source", "external-blind-judge"))
    criterion_methods = dict(score_payload.get("criterion_methods", CRITERION_METHODS))
    total_delta = 0
    study_results: list[dict[str, Any]] = []
    if "leak_risk_note" in score_payload:
        caveat = f"Caveat: {score_payload['leak_risk_note']}"
    elif manifest["mode"] == "derived-evidence":
        caveat = (
            "Caveat: this pass is derived-evidence-blinded. Automated extraction "
            "reads raw artifacts first, then the evaluator sees anonymous counts, "
            "measurements, and fact candidates. The fact candidates may still carry "
            "domain content, but direct variant identity is masked."
        )
    else:
        caveat = (
            "Caveat: this pass is identity-blinded. Raw source/output text can still "
            "reveal intrinsic framework syntax or authoring style."
        )
    lines = [
        "# Blind Study Analysis",
        "",
        f"Run: `{manifest['run_id']}`",
        f"Mode: `{manifest['mode']}`",
        f"Score source: `{score_source}`",
        "",
        (
            "Procedure: variant identities were randomized into anonymous packets, "
            "scores were recorded on anonymous IDs, and the private key was applied "
            "only for this report."
        ),
        "",
        caveat,
        "",
        "## Metric definitions",
        "",
        *metric_definition_lines(BLIND_METRIC_DEFINITIONS + SCORE_METRIC_DEFINITIONS),
        "",
        "## Criterion-specific blindness",
        "",
        "| Criterion | Blindness level | Method | Leakage risk |",
        "|---|---|---|---|",
        *(
            f"| {criterion} | {details['blindness']} | {details['method']} | {details['leakage_risk']} |"
            for criterion, details in criterion_methods.items()
        ),
        "",
    ]

    for study_entry in manifest["studies"]:
        study_id = study_entry["study_id"]
        study = studies[study_id]
        variant_to_anon = {
            identity["variant"]: anonymous_id
            for anonymous_id, identity in key["studies"][study_id].items()
        }
        treatment_anon = variant_to_anon[study.treatment]
        control_anon = variant_to_anon[study.strongest_control]
        lines.extend(
            [
                f"## {study.title}",
                "",
                "| Variant | Anonymous ID | Mean absolute score |",
                "|---|---:|---:|",
            ]
        )
        variant_results = []
        for variant in study.variants:
            anonymous_id = variant_to_anon[variant.name]
            criterion_scores = scores[(study_id, anonymous_id)]
            mean_score = sum(criterion_scores.values()) / len(CRITERIA)
            variant_results.append(
                {
                    "label": variant.label,
                    "anonymous_id": anonymous_id,
                    "mean_score": mean_score,
                }
            )
            lines.append(f"| {variant.label} | `{anonymous_id}` | {mean_score:.2f} |")
        lines.extend(
            [
                "",
                "| Criterion | Control absolute | Treatment absolute | Blind contrastive delta |",
                "|---|---:|---:|---:|",
            ]
        )
        study_total = 0
        delta_results = []
        for criterion in CRITERIA:
            control_score = scores[(study_id, control_anon)][criterion]
            treatment_score = scores[(study_id, treatment_anon)][criterion]
            delta = contrastive_delta(treatment_score, control_score)
            study_total += delta
            delta_results.append(
                {
                    "criterion": criterion,
                    "control_score": control_score,
                    "treatment_score": treatment_score,
                    "delta": delta,
                }
            )
            lines.append(
                f"| {criterion} | {control_score} | {treatment_score} | {delta:+d} |"
            )
        total_delta += study_total
        study_results.append(
            {
                "study_id": study_id,
                "title": study.title,
                "variants": variant_results,
                "deltas": delta_results,
                "total": study_total,
                "total_delta": study_total,
            }
        )
        lines.append(f"| **Total** |  |  | **{study_total:+d}** |")
        lines.append("")

    lines.extend(
        [
            "## Aggregate blind contrastive signal",
            "",
            f"Total blind contrastive delta across studies: **{total_delta:+d}**.",
            "",
        ]
    )
    report_path = run_dir / "derandomized-report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    write_reveal_json(
        run_dir / "derandomized-report.json",
        manifest,
        score_source,
        caveat,
        criterion_methods,
        study_results,
        total_delta,
    )
    write_reveal_html(
        run_dir / "derandomized-report.html",
        report_path,
        manifest,
        score_source,
        caveat,
        criterion_methods,
        study_results,
        total_delta,
    )
    return report_path


def add_common_run_argument(parser: argparse.ArgumentParser) -> None:
    """Add the run directory argument to a subcommand."""
    parser.add_argument(
        "run_dir", type=Path, help="Prepared blind-analysis run directory."
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Create and reveal randomized blind study-analysis packets."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Create anonymized packets.")
    prepare.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    prepare.add_argument("--run-id")
    prepare.add_argument("--seed", type=int)
    prepare.add_argument(
        "--mode",
        choices=("derived-evidence", "compiled-output", "source-and-output"),
        default="derived-evidence",
        help=(
            "derived-evidence avoids raw text in packets; raw-text modes are "
            "available for explicit review."
        ),
    )
    prepare.add_argument("--force", action="store_true")

    metric_scores = subparsers.add_parser(
        "score-metrics", help="Write metric-only anonymous scores."
    )
    add_common_run_argument(metric_scores)

    hybrid_scores = subparsers.add_parser(
        "score-hybrid", help="Combine metric and masked-review anonymous scores."
    )
    add_common_run_argument(hybrid_scores)
    hybrid_scores.add_argument(
        "--qualitative-scores",
        type=Path,
        required=True,
        help="Partial masked-review score JSON for reading-dependent criteria.",
    )

    reveal = subparsers.add_parser("reveal", help="Apply the private key to scores.")
    add_common_run_argument(reveal)
    reveal.add_argument("--scores", type=Path)

    metric_pass = subparsers.add_parser(
        "metric-pass", help="Prepare, score, and reveal one metric-only blind run."
    )
    metric_pass.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    metric_pass.add_argument("--run-id")
    metric_pass.add_argument("--seed", type=int)
    metric_pass.add_argument(
        "--mode",
        choices=("derived-evidence", "compiled-output", "source-and-output"),
        default="derived-evidence",
        help=(
            "derived-evidence avoids raw text in packets; raw-text modes are "
            "available for explicit review."
        ),
    )
    metric_pass.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    """Run the CLI."""
    args = build_parser().parse_args()
    if args.command == "prepare":
        run_dir = prepare_blind_run(
            output_root=args.output_root,
            run_id=args.run_id,
            seed=args.seed,
            mode=args.mode,
            force=args.force,
        )
        print(rel(run_dir))
    elif args.command == "score-metrics":
        print(rel(write_metric_scores(args.run_dir)))
    elif args.command == "score-hybrid":
        print(rel(write_hybrid_scores(args.run_dir, args.qualitative_scores)))
    elif args.command == "reveal":
        print(rel(reveal_scores(args.run_dir, args.scores)))
    elif args.command == "metric-pass":
        run_dir = prepare_blind_run(
            output_root=args.output_root,
            run_id=args.run_id,
            seed=args.seed,
            mode=args.mode,
            force=args.force,
        )
        write_metric_scores(run_dir)
        print(rel(reveal_scores(run_dir)))


if __name__ == "__main__":
    main()
