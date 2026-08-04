"""Prepare, blind, and report the audience-conditioned release study."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
SCENARIO_PATH = ROOT / "inputs/scenario.json"
MODEL = "gpt-5.6-terra"
RUN_DATE = "2026-08-04"
GENERATION_METHOD = "Copilot CLI general-purpose subagent"
GENERATION_EFFORT = "high"
SEED = 20260804
AUDIENCE_SLUGS = {
    "Implementation Team": "implementation-team",
    "Release Team": "release-team",
}
VARIANTS = ("control", "treatment")
EVIDENCE_CRITERIA = (
    "specific_facts",
    "facts_assumptions_unknowns",
    "counterevidence_tradeoffs",
    "unsupported_claims",
)
PROTOCOL_CRITERIA = (
    "explicit_scoped_decision",
    "gate_logic",
    "risks_mitigations_owners",
    "conditions_triggers_actions",
)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, value: Any) -> None:
    _write_text(path, json.dumps(value, indent=2, sort_keys=True))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scenario() -> dict[str, Any]:
    scenario = _read_json(SCENARIO_PATH)
    required = {"release", "audiences", "development_notes"}
    missing = required - scenario.keys()
    if missing:
        raise ValueError(f"Scenario missing keys: {sorted(missing)}")
    if scenario["audiences"] != list(AUDIENCE_SLUGS):
        raise ValueError("Scenario audiences must match the frozen study order.")
    return scenario


def _control_task(release: str, audience: str) -> str:
    sentence = f"Advise the {audience} on {release} using the notes below."
    word_count = len(sentence.rstrip(".").split())
    if word_count > 20:
        raise ValueError(f"Control task has {word_count} words: {sentence}")
    return sentence


def prepare() -> None:
    scenario = _scenario()
    prepared = ROOT / "outputs/prepared"
    prompts = ROOT / "outputs/prompts"
    provenance = ROOT / "outputs/provenance"
    for directory in (prepared, prompts, provenance):
        directory.mkdir(parents=True, exist_ok=True)

    manifest_files: list[Path] = [
        SCENARIO_PATH,
        ROOT / "promplets/treatment.weavemark.md",
    ]
    for audience in scenario["audiences"]:
        slug = AUDIENCE_SLUGS[audience]
        variables = {
            "release": scenario["release"],
            "audience": audience,
            "dev_notes": scenario["development_notes"],
        }
        variables_path = prepared / f"{slug}.json"
        _write_json(variables_path, variables)
        manifest_files.append(variables_path)

        control = (
            f"{_control_task(scenario['release'], audience)}\n\n"
            f"# Development notes\n\n{scenario['development_notes']}"
        )
        control_path = prompts / f"control-{slug}.md"
        _write_text(control_path, control)
        manifest_files.append(control_path)

    _write_json(
        provenance / "preparation-manifest.json",
        {
            "study": "audience-conditioned-release-decision",
            "model": MODEL,
            "control_task_max_words": 20,
            "files": {
                str(path.relative_to(ROOT)): _sha256(path) for path in manifest_files
            },
        },
    )


def _response_paths() -> list[tuple[str, str, Path]]:
    paths = []
    for audience, slug in AUDIENCE_SLUGS.items():
        for variant in VARIANTS:
            paths.append(
                (
                    audience,
                    variant,
                    ROOT / "outputs/responses" / f"{variant}-{slug}.md",
                )
            )
    return paths


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, str):
        prefix = f"{REPO_ROOT}/"
        return value.removeprefix(prefix)
    return value


def sanitize_provenance() -> None:
    provenance_dir = ROOT / "outputs/provenance"
    paths = sorted(provenance_dir.glob("treatment-*.json"))
    if len(paths) != 2:
        raise FileNotFoundError("Expected two treatment provenance files.")
    for path in paths:
        _write_json(path, _sanitize_value(_read_json(path)))


def write_generation_manifest() -> None:
    records = []
    for audience, variant, response_path in _response_paths():
        slug = AUDIENCE_SLUGS[audience]
        prompt_path = ROOT / "outputs/prompts" / f"{variant}-{slug}.md"
        if not prompt_path.is_file() or not response_path.is_file():
            raise FileNotFoundError(
                f"Missing prompt/response pair: {prompt_path}, {response_path}"
            )
        records.append(
            {
                "audience": audience,
                "variant": variant,
                "model": MODEL,
                "reasoning_effort": GENERATION_EFFORT,
                "prompt_path": str(prompt_path.relative_to(ROOT)),
                "prompt_sha256": _sha256(prompt_path),
                "response_path": str(response_path.relative_to(ROOT)),
                "response_sha256": _sha256(response_path),
            }
        )
    _write_json(
        ROOT / "outputs/provenance/generation-manifest.json",
        {
            "run_date": RUN_DATE,
            "method": GENERATION_METHOD,
            "model": MODEL,
            "wrapper_protocol": (
                "Answer only the supplied prompt; use no tools or external facts; "
                "do not discuss the study or prompt quality."
            ),
            "response_normalization": (
                "Markdown hard-break trailing spaces were converted to blank-line "
                "paragraph separators before publication; wording is unchanged."
            ),
            "independent_context_per_cell": True,
            "system_context_recorded": False,
            "records": records,
        },
    )


def blind() -> None:
    scenario = _scenario()
    response_paths = _response_paths()
    missing = [str(path) for _, _, path in response_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing responses: {missing}")

    records = [
        {
            "audience": audience,
            "variant": variant,
            "path": path,
        }
        for audience, variant, path in response_paths
    ]
    random.Random(SEED).shuffle(records)
    anonymous_ids = [f"R{index}" for index in range(1, len(records) + 1)]
    key = {}
    packet_sections = []
    for anonymous_id, record in zip(anonymous_ids, records, strict=True):
        key[anonymous_id] = {
            "audience": record["audience"],
            "variant": record["variant"],
            "response_path": str(record["path"].relative_to(ROOT)),
        }
        response = record["path"].read_text(encoding="utf-8").strip()
        packet_sections.append(
            f"## {anonymous_id}\n\n"
            f"Audience condition: {record['audience']}\n\n"
            f"{response}"
        )

    private_dir = ROOT / "outputs/private"
    blind_dir = ROOT / "outputs/blind"
    private_dir.mkdir(parents=True, exist_ok=True)
    blind_dir.mkdir(parents=True, exist_ok=True)
    _write_json(private_dir / "key.json", key)
    rubric = """Score every criterion from 0 to 4.

Evidence quality:
- specific_facts: uses concrete supplied facts and metrics;
- facts_assumptions_unknowns: separates facts, assumptions, and unknowns;
- counterevidence_tradeoffs: represents both supporting and opposing evidence;
- unsupported_claims: avoids invented or stronger-than-supported claims.

Decision protocol:
- explicit_scoped_decision: states a clear decision for the proposed beta scope;
- gate_logic: applies stated gates and criteria to evidence;
- risks_mitigations_owners: links risks to mitigations and named owners;
- conditions_triggers_actions: gives conditions, stop/reversal triggers, and next actions.

Secondary:
- audience_alignment: emphasizes the supplied audience condition without ignoring
  decision-critical contrary evidence.
"""
    anonymous_responses = "\n\n".join(packet_sections)
    packet = f"""# Anonymous evaluator packet

Evaluate each response independently. Do not infer or guess its prompt variant.
Use only the supplied synthetic facts. Return JSON matching the schema below.

## Synthetic facts

{scenario["development_notes"]}

## Rubric

{rubric}

## Required JSON shape

```json
{{
  "evaluator_model": "MODEL",
  "scores": [
    {{
      "anonymous_id": "R1",
      "audience": "Implementation Team",
      "evidence": {{
        "specific_facts": {{"score": 0, "rationale": "..."}},
        "facts_assumptions_unknowns": {{"score": 0, "rationale": "..."}},
        "counterevidence_tradeoffs": {{"score": 0, "rationale": "..."}},
        "unsupported_claims": {{"score": 0, "rationale": "..."}}
      }},
      "decision_protocol": {{
        "explicit_scoped_decision": {{"score": 0, "rationale": "..."}},
        "gate_logic": {{"score": 0, "rationale": "..."}},
        "risks_mitigations_owners": {{"score": 0, "rationale": "..."}},
        "conditions_triggers_actions": {{"score": 0, "rationale": "..."}}
      }},
      "audience_alignment": {{"score": 0, "rationale": "..."}},
      "overall_notes": "..."
    }}
  ]
}}
```

## Anonymous responses

{anonymous_responses}
"""
    _write_text(blind_dir / "packet.md", packet)


def _criterion_score(block: dict[str, Any], key: str) -> int:
    item = block.get(key)
    if (
        not isinstance(item, dict)
        or isinstance(item.get("score"), bool)
        or not isinstance(item.get("score"), int)
    ):
        raise ValueError(f"Missing integer score for {key}")
    score = item["score"]
    if not 0 <= score <= 4:
        raise ValueError(f"Score outside 0-4 for {key}: {score}")
    return score


def _reported_gate_label(response: str) -> str:
    lines = response.splitlines()
    if not lines:
        return "not explicit"
    first_line = lines[0].casefold()
    bold_label = re.match(r"^\*\*(.+?)\*\*", first_line)
    if bold_label:
        return bold_label.group(1).strip()
    if first_line.startswith("gate:"):
        return first_line.removeprefix("gate:").strip()
    return first_line[:80].strip() or "not explicit"


def _word_count(value: str) -> int:
    return len(re.findall(r"\b[\w.-]+\b", value))


def _scored_rows() -> tuple[list[dict[str, Any]], str]:
    key = _read_json(ROOT / "outputs/private/key.json")
    scores = _read_json(ROOT / "outputs/blind/scores.json")
    evaluator_model = str(scores.get("evaluator_model", "unknown"))
    score_items = scores.get("scores")
    if not isinstance(score_items, list):
        raise ValueError("scores.json must contain a scores list.")
    score_ids = [
        item.get("anonymous_id") for item in score_items if isinstance(item, dict)
    ]
    if len(score_ids) != len(set(score_ids)):
        raise ValueError("scores.json contains duplicate anonymous IDs.")
    by_id = {
        item.get("anonymous_id"): item for item in score_items if isinstance(item, dict)
    }
    if set(by_id) != set(key):
        raise ValueError("Anonymous score coverage does not match the reveal key.")

    rows = []
    for anonymous_id, identity in key.items():
        item = by_id[anonymous_id]
        if item.get("audience") != identity["audience"]:
            raise ValueError(f"Audience mismatch for {anonymous_id}")
        evidence = item.get("evidence")
        protocol = item.get("decision_protocol")
        alignment = item.get("audience_alignment")
        if not isinstance(evidence, dict) or not isinstance(protocol, dict):
            raise ValueError(f"Missing rubric blocks for {anonymous_id}")
        if not isinstance(alignment, dict):
            raise ValueError(f"Missing audience alignment for {anonymous_id}")
        evidence_score = sum(
            _criterion_score(evidence, criterion) for criterion in EVIDENCE_CRITERIA
        )
        protocol_score = sum(
            _criterion_score(protocol, criterion) for criterion in PROTOCOL_CRITERIA
        )
        alignment_score = _criterion_score(
            {"audience_alignment": alignment},
            "audience_alignment",
        )
        response_path = ROOT / identity["response_path"]
        response = response_path.read_text(encoding="utf-8")
        rows.append(
            {
                "anonymous_id": anonymous_id,
                "audience": identity["audience"],
                "variant": identity["variant"],
                "evidence_quality": evidence_score,
                "decision_protocol": protocol_score,
                "audience_alignment": alignment_score,
                "total": evidence_score + protocol_score + alignment_score,
                "reported_gate_label": _reported_gate_label(response),
                "response_words": _word_count(response),
                "overall_notes": str(item.get("overall_notes", "")),
                "response_path": identity["response_path"],
            }
        )
    return (
        sorted(rows, key=lambda row: (row["audience"], row["variant"])),
        evaluator_model,
    )


def _markdown_report(
    rows: list[dict[str, Any]],
    evaluator_model: str,
) -> str:
    table = [
        "| Audience | Variant | Reported label* | Words | Evidence /16 | Protocol /16 | Alignment /4 | Total /36 |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        marker = "[T]" if row["variant"] == "treatment" else "[C]"
        table.append(
            f"| {row['audience']} | {marker} {row['variant'].title()} | "
            f"{row['reported_gate_label']} | {row['response_words']} | "
            f"{row['evidence_quality']} | {row['decision_protocol']} | "
            f"{row['audience_alignment']} | {row['total']} |"
        )

    deltas = []
    for audience in AUDIENCE_SLUGS:
        pair = {row["variant"]: row for row in rows if row["audience"] == audience}
        deltas.append(
            f"- **{audience}:** treatment-control evidence "
            f"{pair['treatment']['evidence_quality'] - pair['control']['evidence_quality']:+d}; "
            f"protocol "
            f"{pair['treatment']['decision_protocol'] - pair['control']['decision_protocol']:+d}; "
            f"total {pair['treatment']['total'] - pair['control']['total']:+d}."
        )

    notes = "\n".join(
        f"- **{row['audience']} / {row['variant']}:** {row['overall_notes']}"
        for row in rows
    )
    table_text = "\n".join(table)
    delta_text = "\n".join(deltas)
    decisions = "\n".join(
        f"- **{row['audience']} / {row['variant']}:** reported "
        f"`{row['reported_gate_label']}` "
        f"({row['response_words']} words; "
        f"[response](../{row['response_path']}))."
        for row in rows
    )
    by_audience = {
        audience: {row["variant"]: row for row in rows if row["audience"] == audience}
        for audience in AUDIENCE_SLUGS
    }
    evidence_deltas = {
        audience: pair["treatment"]["evidence_quality"]
        - pair["control"]["evidence_quality"]
        for audience, pair in by_audience.items()
    }
    protocol_deltas = {
        audience: pair["treatment"]["decision_protocol"]
        - pair["control"]["decision_protocol"]
        for audience, pair in by_audience.items()
    }
    return f"""# Audience-Conditioned Release Decision Results

[Open the self-contained HTML report](results.html).

## Design

One synthetic release case, two audience conditions, and one response per
control/treatment cell. Every downstream response used `{MODEL}`. Anonymous
blind* rubric scoring used `{evaluator_model}`.

## Metric definitions

- **Words:** lexical tokens in the saved response, used only to expose the
  treatment-control length difference.
- **Evidence /16:** sum of four 0-4 scores for specific facts, separation of
  facts/assumptions/unknowns, counterevidence/tradeoffs, and unsupported claims.
- **Protocol /16:** sum of four 0-4 scores for an explicit scoped decision, gate
  logic, risks/mitigations/owners, and conditions/triggers/actions.
- **Alignment /4:** secondary score for useful emphasis on the assigned audience
  without suppressing decision-critical contrary evidence.
- **Total /36:** evidence, protocol, and alignment scores added together.
- **blind\\*:** identities were randomized before scoring, but response length and
  formatting could still reveal the prompt condition.

## Scores

{table_text}

## Treatment-control differences

{delta_text}

## Decision behavior

{decisions}

*The treatment prompt mandated `Gate: go | no-go | wait | investigate`; the
control did not. Reported labels are therefore descriptive transcripts, not a
comparable outcome measure.*

The Release control and treatment converge more than their labels suggest: both
describe a conditioned one-tenant, 24-hour path. They differ mainly on whether
that path is approved now or requires separate approval; the control additionally
pre-authorizes expansion to four tenants, while the treatment does not. No common
behavioral decision outcome was pre-specified, so this study does not score
decision direction.

The two compiled treatment prompts differ beyond their explicit audience
branches because they were produced by separate semantic-compilation calls. The
Release Team prompt is about 22% longer and additionally mandates an explicit
five-tenant-versus-narrower adjudication and a risks-and-next-action section
corresponding to a scored rubric dimension. The Implementation prompt uniquely
frames the decision as bounded-beta-only, while Release asks whether the requested
five-tenant release may proceed. Both assess material claims, but Release expands
the criteria into a definitional table. Therefore, differences between treatment
audiences cannot be attributed solely to `@match`.

## Anonymous evaluator notes

{notes}

## Interpretation

Treatment-control evidence-quality differences were
{evidence_deltas["Implementation Team"]:+d} for the Implementation Team and
{evidence_deltas["Release Team"]:+d} for the Release Team; protocol differences
were {protocol_deltas["Implementation Team"]:+d} and
{protocol_deltas["Release Team"]:+d}. This is a four-response synthetic case
study. Several rubric dimensions directly correspond to sections mandated by the
treatment output contract, so scores partly measure format compliance. Response
format and length made variant identity inferable despite anonymous IDs.
Differences describe these saved outputs only; they do not estimate an average
causal effect, a length-independent effect, or general model-wide superiority.
One evaluator scored all four responses in one shared packet; there is no repeat
or inter-rater reliability estimate.

## Artifacts

- [Study protocol](../README.md)
- [Anonymous evaluator packet](../outputs/blind/packet.md)
- [Machine-readable results](results.json)
"""


def _html_report(rows: list[dict[str, Any]], evaluator_model: str) -> str:
    cards = []
    for row in rows:
        marker = "[T]" if row["variant"] == "treatment" else "[C]"
        cards.append(f"""<article class="{html.escape(row['variant'])}">
              <div class="marker">{marker} {html.escape(row['variant'].title())}</div>
              <h2>{html.escape(row['audience'])}</h2>
              <div class="scores">
                <span><b>{row['evidence_quality']}</b>/16 evidence</span>
                <span><b>{row['decision_protocol']}</b>/16 protocol</span>
                <span><b>{row['audience_alignment']}</b>/4 alignment</span>
              </div>
              <p><strong>Reported label*:</strong>
              {html.escape(row['reported_gate_label'])} ·
              {row['response_words']} words</p>
              <p>{html.escape(row['overall_notes'])}</p>
              <p><a href="../{html.escape(row['response_path'], quote=True)}">
              Inspect saved response</a></p>
            </article>""")
    by_audience = {
        audience: {row["variant"]: row for row in rows if row["audience"] == audience}
        for audience in AUDIENCE_SLUGS
    }
    implementation = by_audience["Implementation Team"]
    release = by_audience["Release Team"]
    implementation_evidence_delta = (
        implementation["treatment"]["evidence_quality"]
        - implementation["control"]["evidence_quality"]
    )
    release_evidence_delta = (
        release["treatment"]["evidence_quality"]
        - release["control"]["evidence_quality"]
    )
    implementation_protocol_delta = (
        implementation["treatment"]["decision_protocol"]
        - implementation["control"]["decision_protocol"]
    )
    release_protocol_delta = (
        release["treatment"]["decision_protocol"]
        - release["control"]["decision_protocol"]
    )
    implementation_total_delta = (
        implementation["treatment"]["total"] - implementation["control"]["total"]
    )
    release_total_delta = release["treatment"]["total"] - release["control"]["total"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Audience-Conditioned Release Decision Study</title>
  <style>
    :root {{ --ink:#182431; --muted:#627184; --paper:#f4f3ef; --card:#fff;
      --line:#d8e0e6; --blue:#315f78; --blue-soft:#edf3f5; --green:#39725d;
      --green-soft:#e7f2ed; --amber:#9a641b; --amber-soft:#fff4df;
      --red:#9d443f; --red-soft:#faecea; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--paper);
      font:16px/1.55 Inter,ui-sans-serif,system-ui,sans-serif; }}
    header {{ padding:26px max(5vw,24px); color:white;
      background:linear-gradient(135deg,#15222e,#315f78); }}
    header h1 {{ margin:.15rem 0 .35rem; max-width:980px;
      font-size:clamp(1.8rem,4vw,3rem); line-height:1.08; }}
    header p {{ max-width:900px; margin:.35rem 0; color:#d9e7eb; }}
    .eyebrow {{ font-size:.78rem; font-weight:800; letter-spacing:.1em;
      text-transform:uppercase; }}
    main {{ width:min(1100px,94vw); margin:18px auto 60px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr));
      gap:10px; margin-bottom:16px; }}
    .kpi {{ min-height:118px; padding:16px; background:var(--card);
      border:1px solid var(--line); border-radius:13px; }}
    .kpi b {{ display:block; margin-bottom:4px; font-size:1.65rem; line-height:1.1; }}
    .kpi span {{ color:var(--muted); font-size:.9rem; }}
    .insight-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
      gap:12px; }}
    .insight {{ margin:0; padding:15px; border-radius:11px; }}
    .gain {{ color:#244f40; background:var(--green-soft); }}
    .caveat {{ color:#70480f; background:var(--amber-soft); }}
    .grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
    article {{ padding:20px; background:var(--card); border:1px solid var(--line);
      border-radius:14px; border-top:5px solid var(--blue); }}
    article.treatment {{ border-top-color:var(--green); }}
    article h2 {{ margin:.3rem 0 .8rem; }}
    .marker {{ color:var(--muted); font-size:.8rem; font-weight:800;
      letter-spacing:.08em; text-transform:uppercase; }}
    .scores {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .scores span {{ padding:7px 9px; border-radius:9px; background:var(--blue-soft); }}
    .scores b {{ font-size:1.25rem; }}
    section {{ margin-top:20px; padding:22px; background:white;
      border:1px solid var(--line); border-radius:14px; }}
    section h2 {{ margin-top:0; }}
    details {{ margin-top:16px; padding:15px 17px; background:var(--card);
      border:1px solid var(--line); border-radius:12px; }}
    summary {{ cursor:pointer; font-weight:750; }}
    .glossary {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
      gap:8px 18px; margin-bottom:0; }}
    .glossary dt {{ font-weight:750; }}
    .glossary dd {{ margin:0 0 10px; color:var(--muted); }}
    .links {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:16px; }}
    a {{ color:var(--blue); }}
    @media(max-width:820px) {{
      .kpis {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
      .grid,.insight-grid {{ grid-template-columns:1fr; }}
    }}
    @media(max-width:480px) {{
      .kpis {{ grid-template-columns:1fr; }}
      .glossary {{ grid-template-columns:1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">Runtime study · one synthetic case · four responses</p>
    <h1>Do reusable refinements improve evidence use and decision protocol?</h1>
    <p>Same facts and downstream model. In this saved case, compiled treatments
    scored higher than one-sentence controls, but were substantially longer and
    do not establish an average causal effect.</p>
  </header>
  <main>
    <div class="kpis" aria-label="Study at a glance">
      <div class="kpi"><b>4</b><span>independently generated responses</span></div>
      <div class="kpi"><b>+{implementation_total_delta}</b>
        <span>Implementation treatment-control total</span></div>
      <div class="kpi"><b>+{release_total_delta}</b>
        <span>Release treatment-control total</span></div>
      <div class="kpi"><b>1</b><span>anonymous evaluator; no reliability estimate</span></div>
    </div>
    <section>
      <h2>Top insights</h2>
      <div class="insight-grid">
        <p class="insight gain"><strong>Observed gain.</strong> Treatment improved
        blind* evidence scores by {implementation_evidence_delta} and
        {release_evidence_delta} points, and protocol scores by
        {implementation_protocol_delta} and {release_protocol_delta}.</p>
        <p class="insight caveat"><strong>Honest boundary.</strong> Treatments
        were much longer, scoring partly rewards mandated sections, and separate
        semantic compilations confound the audience comparison.</p>
      </div>
    </section>
    <details>
      <summary>Metric glossary and blind* caveat</summary>
      <dl class="glossary">
        <div><dt>Words</dt><dd>Lexical response tokens; exposes length differences.</dd></div>
        <div><dt>Evidence /16</dt><dd>Four 0-4 evidence-quality criteria.</dd></div>
        <div><dt>Protocol /16</dt><dd>Four 0-4 decision-protocol criteria.</dd></div>
        <div><dt>Alignment /4</dt><dd>Useful audience emphasis without hiding contrary evidence.</dd></div>
        <div><dt>Total /36</dt><dd>Evidence, protocol, and alignment combined.</dd></div>
        <div><dt>blind*</dt><dd>IDs were randomized, but formatting and length could reveal condition.</dd></div>
      </dl>
    </details>
    <section>
      <h2>Saved comparisons</h2>
      <div class="grid">{"".join(cards)}</div>
    </section>
    <section>
      <h2>Decision-label boundary</h2>
      <p><strong>Reported gate labels are not comparable outcomes.</strong>
      Treatment mandated a gate enum while controls were free-form. The Release
      control and treatment both describe a conditioned one-tenant path despite
      different labels. Decision direction was not pre-specified as a scored
      outcome.</p>
    </section>
    <section>
      <h2>Evidence boundary</h2>
      <p>This is a manually inspectable four-response case study, not an average
      treatment-effect estimate. Read the <a href="results.md">Markdown report</a>
      and saved responses before generalizing.</p>
      <p>Generation model: <code>{MODEL}</code>. Anonymous evaluator:
      <code>{html.escape(evaluator_model)}</code>. Rubric dimensions overlap the
      treatment's required output sections; format and length also make variant
      identity inferable. Separate semantic compilations at temperature 0.3
      introduced non-audience differences between treatment prompts, including a
      Release-only risks/owners section tied to a scored dimension, so audience
      effects are not isolated. One evaluator scored all responses in one packet;
      repeat and inter-rater reliability are unknown.</p>
      <div class="links">
       <a href="results.md">Read the Markdown report</a>
       <a href="../README.md">Read the study protocol</a>
       <a href="../outputs/blind/packet.md">Inspect the anonymous packet</a>
      </div>
    </section>
  </main>
</body>
</html>
"""


def report() -> None:
    rows, evaluator_model = _scored_rows()
    results_dir = ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "study": "audience-conditioned-release-decision",
        "generation_model": MODEL,
        "evaluator_model": evaluator_model,
        "rows": rows,
        "limitations": [
            "One synthetic scenario.",
            "One response per experimental cell.",
            "No causal average treatment effect is identified.",
            "Rubric dimensions partly measure treatment-mandated format compliance.",
            "Response format and length make variant identity inferable.",
            "Separate treatment compilations confound audience with other prompt differences.",
            "Reported gate labels are prompt-format dependent and are not scored as a common outcome.",
            "Downstream system context was not captured in the generation manifest.",
            "One evaluator scored all responses in a shared packet; repeat and inter-rater reliability are unknown.",
        ],
    }
    _write_json(results_dir / "results.json", payload)
    markdown = _markdown_report(rows, evaluator_model)
    _write_text(results_dir / "results.md", markdown)
    _write_text(
        results_dir / "results.html",
        _html_report(rows, evaluator_model),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "prepare",
            "sanitize-provenance",
            "generation-manifest",
            "blind",
            "report",
        ),
    )
    return parser


def main() -> None:
    command = build_parser().parse_args().command
    {
        "prepare": prepare,
        "sanitize-provenance": sanitize_provenance,
        "generation-manifest": write_generation_manifest,
        "blind": blind,
        "report": report,
    }[command]()


if __name__ == "__main__":
    main()
