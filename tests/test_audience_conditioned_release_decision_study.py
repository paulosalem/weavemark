from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies/runtime-studies/audience-conditioned-release-decision"


def _module():
    path = STUDY / "study.py"
    spec = importlib.util.spec_from_file_location("release_decision_study", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_control_tasks_are_single_short_sentences() -> None:
    module = _module()
    scenario = json.loads((STUDY / "inputs/scenario.json").read_text(encoding="utf-8"))

    for audience in scenario["audiences"]:
        task = module._control_task(scenario["release"], audience)
        assert task.endswith(".")
        assert ". " not in task
        assert len(task.rstrip(".").split()) <= 20


def test_prepare_preserves_fact_parity(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _module()
    study = tmp_path / "study"
    (study / "inputs").mkdir(parents=True)
    (study / "promplets").mkdir()
    scenario_path = study / "inputs/scenario.json"
    scenario_path.write_text(
        (STUDY / "inputs/scenario.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (study / "promplets/treatment.weavemark.md").write_text(
        (STUDY / "promplets/treatment.weavemark.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "ROOT", study)
    monkeypatch.setattr(module, "SCENARIO_PATH", scenario_path)
    module.prepare()
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))

    for audience, slug in module.AUDIENCE_SLUGS.items():
        variables = json.loads(
            (study / f"outputs/prepared/{slug}.json").read_text(encoding="utf-8")
        )
        control = (study / f"outputs/prompts/control-{slug}.md").read_text(
            encoding="utf-8"
        )
        assert variables["audience"] == audience
        assert variables["dev_notes"] == scenario["development_notes"]
        assert scenario["development_notes"] in control
        assert "@refine" not in control
        assert "@match" not in control


def test_treatment_is_exact_requested_program() -> None:
    text = (STUDY / "promplets/treatment.weavemark.md").read_text(encoding="utf-8")

    assert text.count("@refine module:") == 2
    assert "@match @{audience}" in text
    assert "Implementation Team" in text
    assert "Release Team" in text
    assert "@output enforce: strict" in text


def test_provenance_sanitizer_removes_repository_prefix(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _module()
    repository = tmp_path / "repository"
    study = repository / "studies/runtime-studies/audience-conditioned-release-decision"
    monkeypatch.setattr(module, "ROOT", study)
    monkeypatch.setattr(module, "REPO_ROOT", repository)
    provenance_dir = study / "outputs/provenance"
    provenance_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        provenance_dir / "treatment-implementation-team.json",
        provenance_dir / "treatment-release-team.json",
    ]
    for path in paths:
        path.write_text(
            json.dumps(
                {
                    "source": {
                        "path": str(
                            repository / "studies/runtime-studies/"
                            "audience-conditioned-release-decision/"
                            "promplets/treatment.weavemark.md"
                        )
                    }
                }
            ),
            encoding="utf-8",
        )

    module.sanitize_provenance()

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "/Users/" not in text
        assert text.endswith("\n")


def test_generation_manifest_matches_saved_prompts_and_responses() -> None:
    manifest = json.loads(
        (STUDY / "outputs/provenance/generation-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["model"] == "gpt-5.6-terra"
    assert manifest["independent_context_per_cell"] is True
    assert manifest["system_context_recorded"] is False
    assert "wording is unchanged" in manifest["response_normalization"]
    assert len(manifest["records"]) == 4
    for record in manifest["records"]:
        prompt = STUDY / record["prompt_path"]
        response = STUDY / record["response_path"]
        assert record["prompt_sha256"] == _module()._sha256(prompt)
        assert record["response_sha256"] == _module()._sha256(response)


def test_saved_compilation_provenance_matches_source_and_prompts() -> None:
    module = _module()
    source = STUDY / "promplets/treatment.weavemark.md"

    for slug in module.AUDIENCE_SLUGS.values():
        provenance_path = STUDY / f"outputs/provenance/treatment-{slug}.json"
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        prompt = STUDY / f"outputs/prompts/treatment-{slug}.md"
        artifact = next(
            item
            for item in provenance["artifacts"]
            if item["name"] == "composed_prompt"
        )

        assert provenance["source"]["path"] == str(source.relative_to(ROOT))
        assert provenance["source"]["sha256"] == module._sha256(source)
        assert artifact["sha256"] == module._sha256(prompt)
        assert artifact["bytes"] == len(prompt.read_bytes())
        assert "/Users/" not in provenance_path.read_text(encoding="utf-8")


def test_report_values_are_derived_from_blind_scores() -> None:
    module = _module()
    rows, evaluator_model = module._scored_rows()
    markdown = module._markdown_report(rows, evaluator_model)
    by_pair = {(row["audience"], row["variant"]): row for row in rows}

    implementation_delta = (
        by_pair[("Implementation Team", "treatment")]["evidence_quality"]
        - by_pair[("Implementation Team", "control")]["evidence_quality"]
    )
    release_delta = (
        by_pair[("Release Team", "treatment")]["evidence_quality"]
        - by_pair[("Release Team", "control")]["evidence_quality"]
    )

    assert f"evidence {implementation_delta:+d}" in markdown
    assert f"evidence {release_delta:+d}" in markdown
    assert "[Open the self-contained HTML report](results.html)." in markdown
    assert "## Metric definitions" in markdown
    assert "**blind\\*:**" in markdown
    assert "Reported labels are therefore descriptive transcripts" in markdown
    assert "does not score decision direction" in " ".join(markdown.split())


def test_saved_reports_match_the_generator() -> None:
    module = _module()
    rows, evaluator_model = module._scored_rows()

    assert (STUDY / "results/results.md").read_text(encoding="utf-8") == (
        module._markdown_report(rows, evaluator_model).rstrip() + "\n"
    )
    assert (STUDY / "results/results.html").read_text(encoding="utf-8") == (
        module._html_report(rows, evaluator_model).rstrip() + "\n"
    )


def test_score_validation_rejects_duplicate_ids(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _module()
    study = tmp_path / "study"
    private_dir = study / "outputs/private"
    blind_dir = study / "outputs/blind"
    private_dir.mkdir(parents=True)
    blind_dir.mkdir(parents=True)
    key = json.loads((STUDY / "outputs/private/key.json").read_text(encoding="utf-8"))
    scores = json.loads(
        (STUDY / "outputs/blind/scores.json").read_text(encoding="utf-8")
    )
    scores["scores"].append(scores["scores"][0])
    (private_dir / "key.json").write_text(
        json.dumps(key),
        encoding="utf-8",
    )
    (blind_dir / "scores.json").write_text(
        json.dumps(scores),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "ROOT", study)

    with pytest.raises(ValueError, match="duplicate anonymous IDs"):
        module._scored_rows()


def test_small_score_and_label_guards() -> None:
    module = _module()

    assert module._reported_gate_label("") == "not explicit"
    assert (
        module._reported_gate_label("**Proceed conditionally** with beta.")
        == "proceed conditionally"
    )
    with pytest.raises(ValueError, match="Missing integer score"):
        module._criterion_score({"criterion": {"score": True}}, "criterion")


def test_blind_packet_and_key_cover_every_response(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _module()
    study = tmp_path / "study"
    inputs = study / "inputs"
    responses = study / "outputs/responses"
    inputs.mkdir(parents=True)
    responses.mkdir(parents=True)
    scenario_path = inputs / "scenario.json"
    scenario_path.write_text(
        (STUDY / "inputs/scenario.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    expected = {}
    for audience, slug in module.AUDIENCE_SLUGS.items():
        for variant in module.VARIANTS:
            value = f"Unique response for {audience} and {variant}."
            path = responses / f"{variant}-{slug}.md"
            path.write_text(value + "\n", encoding="utf-8")
            expected[(audience, variant)] = value
    monkeypatch.setattr(module, "ROOT", study)
    monkeypatch.setattr(module, "SCENARIO_PATH", scenario_path)

    module.blind()

    key = json.loads((study / "outputs/private/key.json").read_text(encoding="utf-8"))
    packet = (study / "outputs/blind/packet.md").read_text(encoding="utf-8")
    assert set(key) == {"R1", "R2", "R3", "R4"}
    assert {
        (identity["audience"], identity["variant"]) for identity in key.values()
    } == set(expected)
    for value in expected.values():
        assert value in packet
