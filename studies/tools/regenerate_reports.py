"""Update WeaveMark study metrics plus synchronized Markdown and HTML reports."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

sys.dont_write_bytecode = True

from semantic_information import (  # noqa: E402
    CONTROLLED_STUDIES_ROOT,
    ROOT,
    VARIANTS,
    variant_metrics,
)


@dataclass(frozen=True)
class VariantSpec:
    """A study variant to display in reports."""

    name: str
    label: str
    role: str
    source: str
    output: str
    variables: str | None = None


@dataclass(frozen=True)
class ScoreSpec:
    """A contrastive score for one evaluation criterion."""

    criterion: str
    score: int
    rationale: str


@dataclass(frozen=True)
class BlindCriterionSpec:
    """A revealed blind score for one criterion."""

    criterion: str
    control_absolute: int
    treatment_absolute: int
    delta: int


@dataclass(frozen=True)
class StudySpec:
    """Metadata needed to regenerate one study report."""

    study_id: str
    title: str
    path: str
    what_it_is: str
    evidence_class: str
    study_role: str
    semantic_trace: str
    strongest_control: str
    treatment: str
    variants: tuple[VariantSpec, ...]
    snippet_phrases: dict[str, tuple[str, ...]]
    strengths: tuple[str, ...]
    caveats: tuple[str, ...]
    conclusion: str
    headline: bool = False


CRITERIA = (
    "Authoring leverage",
    "Information yield",
    "Grounded expressiveness",
    "Input readability",
    "Output readability",
    "Constraint integration",
    "Reusable abstraction quality",
)

COMPACT_STUDY_TITLES = {
    "release-readiness": "Release Readiness",
    "work-intelligence-kanban": "Intel Kanban",
    "evidence-decision": "Evidence Workspace",
    "learning-tutor": "Learning Tutor",
    "research-brief": "Research Brief",
    "orbital-drift": "Orbital Drift",
    "verdant-relay": "Verdant Relay",
    "transit-city-swarm": "Transit City",
    "crowd-factory-puzzle": "Crowd Factory",
}

CORE_METRIC_DEFINITIONS = (
    (
        "Source words",
        "Words in the local study source for a variant; this is the local authoring burden.",
    ),
    (
        "Variable words",
        "Words in a variant's explicit input payload, when a template or refinement uses one.",
    ),
    ("Output words", "Words in the saved compiled final artifact."),
    (
        "Leverage",
        "Output words divided by local source words; larger means more final artifact per local word, not quality by itself.",
    ),
    (
        "Fact units",
        "Novelty-weighted semantic fact units extracted from the output by deterministic rules.",
    ),
    (
        "Density",
        "Discounted fact units per 1,000 output words; higher means a more information-dense output.",
    ),
    (
        "Yield",
        "Discounted fact units per 1,000 local source words; higher means more semantic material per local authoring word.",
    ),
)

SCORE_METRIC_DEFINITIONS = (
    (
        "Contrastive score",
        "A -3..+3 judgment comparing [T] against the strongest listed control for each criterion.",
    ),
    (
        "Total score",
        "The sum of the seven contrastive criterion scores for one study.",
    ),
    (
        "Score color",
        "Green means [T] is better, red means worse, amber means similar; intensity follows magnitude.",
    ),
)

BLIND_METRIC_DEFINITIONS = (
    (
        "Derived-evidence packet",
        "An anonymous packet containing automated metrics and extracted fact candidates instead of raw source/output text.",
    ),
    (
        "Blind absolute score",
        "An anonymous 1..7 criterion score assigned before applying the derandomization key; higher is better.",
    ),
    (
        "Blind delta",
        "Treatment absolute score minus control absolute score, mapped back to the -3..+3 contrastive scale after reveal.",
    ),
    (
        "Direct marker leaks",
        "Remaining direct labels such as [C1], [C2], [T], WeaveMark, control/treatment, or directives after masking.",
    ),
)

BLIND_ANALYSIS_ROOT = ROOT / "outputs/studies/blind-analysis"
BLIND_CURRENT_RUN_FILE = BLIND_ANALYSIS_ROOT / "current-run.txt"
BLIND_LEAK_RISK_NOTE = "Blind* scores may combine derived metrics and masked review; see criterion-specific notes."


def score_set(
    values: tuple[int, ...], rationales: tuple[str, ...]
) -> tuple[ScoreSpec, ...]:
    """Create a complete contrastive score set."""
    if len(values) != len(CRITERIA) or len(rationales) != len(CRITERIA):
        raise ValueError("Score sets must cover every criterion.")
    return tuple(
        ScoreSpec(criterion, score, rationale)
        for criterion, score, rationale in zip(
            CRITERIA, values, rationales, strict=True
        )
    )


STUDIES: tuple[StudySpec, ...] = (
    StudySpec(
        study_id="release-readiness",
        title="Release Readiness Workbench",
        path="studies/controlled-studies/release-readiness-workbench-ablation-study",
        what_it_is=(
            "A local-first release command center that turns release notes, docs, "
            "validation runs, screenshots, package artifacts, risks, waivers, and "
            "go/no-go decisions into one auditable workspace."
        ),
        evidence_class="Realistic workflow/product application",
        study_role="Headline structural-mingling evidence.",
        semantic_trace=(
            "release material -> readiness claim -> gate/evidence -> validation/failure "
            "-> action/waiver/decision -> launch/audit"
        ),
        strongest_control="matched-template",
        treatment="promplet",
        headline=True,
        variants=(
            VariantSpec(
                "manual",
                "[C1] Manual brief",
                "Compact hand-written release-workbench request.",
                "specs/00-control-manual-release-readiness-workbench.weavemark.md",
                "outputs/compiled-prompts/00-control-manual-release-readiness-workbench.md",
            ),
            VariantSpec(
                "matched-template",
                "[C2] Matched reusable-template control",
                "Template shell with study-local release, storage, workspace, and validation partials.",
                "specs/01-control-template-release-readiness-workbench.weavemark.md",
                "outputs/compiled-prompts/01-control-template-release-readiness-workbench.md",
                "inputs/template-vars.json",
            ),
            VariantSpec(
                "promplet",
                "[T] WeaveMark treatment",
                "Refines release, evidence, validation, decision, dashboard, notification, and programming layers.",
                "specs/02-treatment-promplet-release-readiness-workbench.weavemark.md",
                "outputs/compiled-prompts/02-treatment-promplet-release-readiness-workbench.md",
                "inputs/promplet-vars.json",
            ),
        ),
        snippet_phrases={
            "manual": ("collect release tasks",),
            "matched-template": ("Critical gates should block release",),
            "source": ("Mingle refinements into one release workspace",),
            "promplet": ("Build **Release Readiness Workbench**",),
        },
        strengths=(
            "Release gates, evidence quality, validation matrices, risks, waivers, actions, dashboards, and browser validation all shape one workflow.",
            "The treatment has higher source-only leverage than the matched reusable-template control.",
            "The final specification adds substantially more actionable release facts than the control.",
        ),
        caveats=(
            "The matched template is already strong and keeps higher information density.",
            "The treatment loses information yield versus the template because the WeaveMark source is longer while the template shell stays very compact.",
            "No downstream release-workbench implementation outcome has been measured.",
        ),
        conclusion="A strong headline study, with the honest caveat that the template remains denser and more source-efficient on the yield proxy.",
    ),
    StudySpec(
        study_id="work-intelligence-kanban",
        title="Intelligence-to-Execution Kanban",
        path="studies/controlled-studies/intelligence-execution-kanban-ablation-study",
        what_it_is=(
            "A local-first Kanban board for monitoring selected topics, turning signals "
            "into cards, deciding actions, delegating work, tracking status, and preserving output lineage."
        ),
        evidence_class="Realistic workflow/product application",
        study_role="Headline structural-mingling evidence.",
        semantic_trace="signal -> card -> board transition -> decision/action/delegation -> output",
        strongest_control="matched-template",
        treatment="promplet",
        headline=True,
        variants=(
            VariantSpec(
                "manual",
                "[C1] Manual brief",
                "Compact hand-written Kanban workspace request.",
                "specs/00-control-manual-intelligence-execution-kanban.weavemark.md",
                "outputs/compiled-prompts/00-control-manual-intelligence-execution-kanban.md",
            ),
            VariantSpec(
                "matched-template",
                "[C2] Matched reusable-template control",
                "Template shell with monitoring, local-first storage, workspace, and validation partials.",
                "specs/01-control-template-intelligence-execution-kanban.weavemark.md",
                "outputs/compiled-prompts/01-control-template-intelligence-execution-kanban.md",
                "inputs/template-vars.json",
            ),
            VariantSpec(
                "promplet",
                "[T] WeaveMark treatment",
                "Refines monitoring, signal-to-action workflow, Kanban state, decisions, alerts, and validation.",
                "specs/02-treatment-promplet-intelligence-execution-kanban.weavemark.md",
                "outputs/compiled-prompts/02-treatment-promplet-intelligence-execution-kanban.md",
                "inputs/promplet-vars.json",
            ),
        ),
        snippet_phrases={
            "manual": ("monitor selected topics",),
            "matched-template": ("what came in, why it mattered",),
            "source": ("monitored signals, ideas, decisions",),
            "promplet": (
                "Build **Intelligence-to-Execution Kanban**",
                "The application is a local-first",
            ),
        },
        strengths=(
            "The treatment propagates the signal-to-card trace through board states, delegation, notifications, APIs, activity history, and acceptance criteria.",
            "It produces much more total semantic content than the matched template while preserving a single implementation specification.",
            "The source keeps the domain abstract while reusable work-intelligence refinements define concrete responsibilities.",
        ),
        caveats=(
            "The matched template has higher information density.",
            "The treatment loses information yield against the template because the reusable-template shell is extremely compact.",
            "No generated Kanban implementation has been behaviorally compared yet.",
        ),
        conclusion="A strong realistic study for semantic propagation, with a measured density/yield loss that should stay visible.",
    ),
    StudySpec(
        study_id="evidence-decision",
        title="Evidence-to-Decision Workspace",
        path="studies/controlled-studies/evidence-decision-workspace-ablation-study",
        what_it_is=(
            "A local-first analyst workspace that turns documents, notes, links, news, claims, "
            "contradictions, options, decisions, and follow-up actions into an auditable decision surface."
        ),
        evidence_class="Realistic workflow/product application",
        study_role="Headline structural-mingling evidence.",
        semantic_trace="source -> claim -> evidence/contradiction -> ACH -> decision gate -> action/output",
        strongest_control="matched-template",
        treatment="promplet",
        headline=True,
        variants=(
            VariantSpec(
                "manual",
                "[C1] Manual brief",
                "Compact hand-written evidence-to-decision workspace request.",
                "specs/00-control-manual-evidence-decision-workspace.weavemark.md",
                "outputs/compiled-prompts/00-control-manual-evidence-decision-workspace.md",
            ),
            VariantSpec(
                "matched-template",
                "[C2] Matched reusable-template control",
                "Template shell with evidence, decision, local-first, workspace, and validation partials.",
                "specs/01-control-template-evidence-decision-workspace.weavemark.md",
                "outputs/compiled-prompts/01-control-template-evidence-decision-workspace.md",
                "inputs/template-vars.json",
            ),
            VariantSpec(
                "promplet",
                "[T] WeaveMark treatment",
                "Refines source fidelity, ACH, contradiction handling, decision gates, local-first architecture, and AI safety.",
                "specs/02-treatment-promplet-evidence-decision-workspace.weavemark.md",
                "outputs/compiled-prompts/02-treatment-promplet-evidence-decision-workspace.md",
                "inputs/promplet-vars.json",
            ),
        ),
        snippet_phrases={
            "manual": ("messy documents, notes, links",),
            "matched-template": ("Each source should preserve",),
            "source": ("source -> normalized fact", "source -> claim"),
            "promplet": (
                "Build **Evidence-to-Decision Workspace**",
                "source fidelity",
            ),
        },
        strengths=(
            "The treatment converts evidence quality, ACH, contradictions, decision gates, actions, storage, UI, APIs, and AI safety into one architecture.",
            "It wins leverage and information yield against the matched reusable-template control.",
            "The final specification has the largest fact-unit count in the study corpus.",
        ),
        caveats=(
            "The matched template remains denser.",
            "Output readability is mixed because the treatment is much longer and requires careful navigation.",
            "No analyst-task or implementation outcome has been measured.",
        ),
        conclusion="The strongest realistic application result on total semantic content and yield, though not on compactness.",
    ),
    StudySpec(
        study_id="learning-tutor",
        title="Learning Tutor",
        path="studies/controlled-studies/learning-tutor-refinement-ablation-study",
        what_it_is=(
            "A pasteable linear-algebra tutor prompt that teaches through geometric intuition, "
            "Socratic questions, misconception diagnosis, adaptive practice, and delayed review."
        ),
        evidence_class="Realistic non-programming assistant task",
        study_role="Supporting refinement evidence.",
        semantic_trace="learner profile -> concept explanation -> diagnosis -> practice ladder -> delayed review",
        strongest_control="matched-prose",
        treatment="promplet",
        variants=(
            VariantSpec(
                "manual",
                "[C1] Compact manual",
                "Short tutor request that leaves pedagogy mostly implicit.",
                "specs/00-control-compact-manual-linear-algebra-tutor.weavemark.md",
                "outputs/compiled-prompts/00-control-compact-manual-linear-algebra-tutor.md",
            ),
            VariantSpec(
                "matched-prose",
                "[C2] Matched prose control",
                "Manual prose version of the intended teaching method.",
                "specs/01-control-matched-prose-linear-algebra-tutor.weavemark.md",
                "outputs/compiled-prompts/01-control-matched-prose-linear-algebra-tutor.md",
            ),
            VariantSpec(
                "promplet",
                "[T] WeaveMark treatment",
                "Refines reusable teaching methods and expands the tutoring loop.",
                "specs/02-treatment-refined-expand-linear-algebra-tutor.weavemark.md",
                "outputs/compiled-prompts/02-treatment-refined-expand-linear-algebra-tutor.md",
                "inputs/treatment-vars.json",
            ),
        ),
        snippet_phrases={
            "manual": ("linear algebra",),
            "matched-prose": ("geometric intuition",),
            "source": (
                "learner profile",
                "The final prompt must be one coherent tutor prompt",
            ),
            "promplet": ("You are an adaptive", "linear algebra tutor"),
        },
        strengths=(
            "The treatment uses fewer local source words than the matched-prose control and produces far more semantic content.",
            "Pedagogy, diagnosis, practice, branching, and delayed review become one concrete tutor behavior.",
            "This is a strong non-programming demonstration of reusable refinement.",
        ),
        caveats=(
            "The artifact is still a prompt for a tutor, not a measured learner outcome.",
            "Because the control is matched prose rather than a reusable-template control, it is not apples-to-apples with headline software-specification studies.",
            "The final tutor prompt is much longer, so usability depends on whether the receiving model follows the structure.",
        ),
        conclusion="A strong supporting non-programming result, especially on leverage and yield versus matched prose.",
    ),
    StudySpec(
        study_id="research-brief",
        title="Research Brief",
        path="studies/controlled-studies/research-brief-ablation-study",
        what_it_is=(
            "A concise research-brief instruction for energy-storage strategy that requires source families, "
            "context limits, contradictions, alternatives, caveats, and explainable evidence handling."
        ),
        evidence_class="Realistic non-programming research workflow",
        study_role="Supporting refinement evidence.",
        semantic_trace="topic/context -> source quality -> contradiction -> alternatives -> explainable brief",
        strongest_control="matched-template",
        treatment="promplet",
        variants=(
            VariantSpec(
                "manual",
                "[C1] Manual request",
                "Compact hand-written research brief request.",
                "specs/00-control-manual-research-brief.weavemark.md",
                "outputs/compiled-prompts/00-control-manual-research-brief.md",
            ),
            VariantSpec(
                "matched-template",
                "[C2] Matched reusable-template control",
                "Template shell with study-local research-brief partial and variables.",
                "specs/01-control-template-research-brief.weavemark.md",
                "outputs/compiled-prompts/01-control-template-research-brief.md",
                "inputs/template-vars.json",
            ),
            VariantSpec(
                "promplet",
                "[T] WeaveMark treatment",
                "Refines context sufficiency, evidence quality, research rigor, news quality, alternatives, and explainability.",
                "specs/02-treatment-refined-research-brief.weavemark.md",
                "outputs/compiled-prompts/02-treatment-refined-research-brief.md",
                "inputs/energy-storage.json",
            ),
        ),
        snippet_phrases={
            "manual": ("energy storage",),
            "matched-template": ("source", "caveat"),
            "source": ("evidence quality", "research rigor"),
            "promplet": ("research brief", "contradictions"),
        },
        strengths=(
            "The treatment adds richer epistemic obligations: source families, contradictions, alternatives, evidence caveats, and explainability.",
            "It has a modest leverage and information-yield edge over the matched template.",
            "The comparison stays single-output after removing multi-artifact variants.",
        ),
        caveats=(
            "The measured leverage and yield wins are small.",
            "The matched template has nearly identical information density.",
            "No downstream researcher outcome, citation accuracy, or factuality result has been measured.",
        ),
        conclusion="A modest but realistic supporting win whose value is quality-lens integration more than raw metric dominance.",
    ),
    StudySpec(
        study_id="orbital-drift",
        title="Orbital Drift",
        path="studies/controlled-studies/games/orbital-drift-racing-ablation-study",
        what_it_is=(
            "A browser racing game about piloting a small craft through asteroid fields, gravity wells, "
            "orbital gates, lap routing, hazards, scoring, restart, and browser validation."
        ),
        evidence_class="Game implementation-specification study",
        study_role="Supporting game-programming specification evidence.",
        semantic_trace="ship control -> orbital hazards -> race loop -> browser implementation -> validation",
        strongest_control="matched-template",
        treatment="promplet",
        variants=(
            VariantSpec(
                "manual",
                "[C1] Manual brief",
                "Minimal hand-written Orbital Drift request.",
                "specs/00-control-manual-orbital-drift.weavemark.md",
                "outputs/compiled-prompts/00-control-manual-orbital-drift.md",
            ),
            VariantSpec(
                "matched-template",
                "[C2] Matched reusable-template control",
                "Template shell with game, browser implementation, asset, and validation partials.",
                "specs/01-control-template-orbital-drift.weavemark.md",
                "outputs/compiled-prompts/01-control-template-orbital-drift.md",
                "inputs/template-vars.json",
            ),
            VariantSpec(
                "promplet",
                "[T] WeaveMark treatment",
                "Refines software-spec, web-game, and Playwright MCP validation layers.",
                "specs/02-treatment-promplet-orbital-drift.weavemark.md",
                "outputs/compiled-prompts/02-treatment-promplet-orbital-drift.md",
            ),
        ),
        snippet_phrases={
            "manual": ("small craft", "asteroid fields"),
            "matched-template": (
                "Design Orbital Drift as a complete single-page browser racing game",
            ),
            "source": ("Orbital Drift",),
            "promplet": ("Orbital Drift", "browser racing"),
        },
        strengths=(
            "The treatment has a very large authoring-leverage and information-yield win over the matched template.",
            "Browser-game architecture, controls, states, hazards, restart, scoring, and validation are integrated rather than appended.",
            "The cleaned study is now a single named game instead of a broad multi-variant showcase.",
        ),
        caveats=(
            "The product theme is still synthetic compared with the real workflow/product studies.",
            "The matched template is shorter and denser.",
            "No actual browser game implementation has been generated and tested as behavioral proof.",
        ),
        conclusion="A strong game-specification result, best used as supporting implementation-spec evidence rather than the main claim.",
    ),
    StudySpec(
        study_id="verdant-relay",
        title="Verdant Relay",
        path="studies/controlled-studies/games/verdant-relay-ablation-study",
        what_it_is=(
            "A browser game about defending a living railway garden from blight by combining tower-defense "
            "route pressure, deckbuilder card choices, ecosystem feedback, original assets, and browser validation."
        ),
        evidence_class="Game implementation-specification study",
        study_role="Headline-compatible structural-mingling stress test.",
        semantic_trace="habitat -> route pressure -> defense/card choice -> ecosystem feedback -> browser validation",
        strongest_control="matched-template",
        treatment="promplet",
        headline=True,
        variants=(
            VariantSpec(
                "manual",
                "[C1] Manual brief",
                "Compact hand-written Verdant Relay request.",
                "specs/00-control-compact-manual-verdant-relay.weavemark.md",
                "outputs/compiled-prompts/00-control-compact-manual-verdant-relay.md",
            ),
            VariantSpec(
                "matched-template",
                "[C2] Matched reusable-template control",
                "Template shell with browser-game, tower-defense, deckbuilding, ecosystem, asset, and validation partials.",
                "specs/01-control-template-verdant-relay.weavemark.md",
                "outputs/compiled-prompts/01-control-template-verdant-relay.md",
                "inputs/template-vars.json",
            ),
            VariantSpec(
                "promplet",
                "[T] WeaveMark treatment",
                "Refines and expands mechanics, production requirements, assets, and validation into one playable first-build specification.",
                "specs/02-treatment-promplet-verdant-relay.weavemark.md",
                "outputs/compiled-prompts/02-treatment-promplet-verdant-relay.md",
                "inputs/promplet-vars.json",
            ),
        ),
        snippet_phrases={
            "manual": ("tower defense", "deckbuilding"),
            "matched-template": ("successful round should teach",),
            "source": ("route defense, deckbuilder choices",),
            "promplet": ("Player can understand the goal", "ecosystem state changes"),
        },
        strengths=(
            "The treatment integrates tower defense, deckbuilding, ecosystem simulation, assets, state, balance, UI, and validation into one playable trace.",
            "It wins leverage, information yield, and total fact units against the matched template.",
            "It is a useful stress test for whether several reusable mechanics can shape one final specification.",
        ),
        caveats=(
            "The treatment is much longer and less dense than the matched template.",
            "It is a synthetic game concept, so it should not carry the main real-work application claim.",
            "No generated browser game has been implemented and tested yet.",
        ),
        conclusion="A strong structural-mingling stress test, with length/density and synthetic-domain caveats.",
    ),
    StudySpec(
        study_id="transit-city-swarm",
        title="Transit City Swarm",
        path="studies/controlled-studies/games/transit-city-swarm-ablation-study",
        what_it_is=(
            "A browser strategy game that combines transit-network drawing, city growth, and ant-colony "
            "pathfinding through pheromone-style demand trails and congestion feedback."
        ),
        evidence_class="Game `@expand` study",
        study_role="Focused expansion evidence with a matched-prose comparison.",
        semantic_trace="transit network -> city growth -> swarm demand trails -> congestion -> player routing",
        strongest_control="matched-prose",
        treatment="promplet",
        variants=(
            VariantSpec(
                "compact-no-expand",
                "[C1] Compact no-expand control",
                "Compact source that names the inspirations without expansion.",
                "specs/00-control-compact-no-expand-transit-city-swarm.weavemark.md",
                "outputs/compiled-prompts/00-control-compact-no-expand-transit-city-swarm.md",
            ),
            VariantSpec(
                "matched-prose",
                "[C2] Matched-prose no-expand control",
                "Manual prose expansion without using `@expand`.",
                "specs/01-control-matched-prose-no-expand-transit-city-swarm.weavemark.md",
                "outputs/compiled-prompts/01-control-matched-prose-no-expand-transit-city-swarm.md",
            ),
            VariantSpec(
                "promplet",
                "[T] Expanded WeaveMark treatment",
                "Uses `@expand mode: intention` to unpack concept labels into mechanics.",
                "specs/02-treatment-expand-transit-city-swarm.weavemark.md",
                "outputs/compiled-prompts/02-treatment-expand-transit-city-swarm.md",
            ),
        ),
        snippet_phrases={
            "compact-no-expand": ("transit-network drawing",),
            "matched-prose": ("integrated mechanic",),
            "source": ("Mini Metro-style transit network drawing",),
            "promplet": (
                "The final design must not feel like three separate modules",
            ),
        },
        strengths=(
            "`@expand` makes compact concept labels readable and operational against the compact control.",
            "The treatment clearly states the integrated mechanic that connects network drawing, city growth, and demand trails.",
            "It now wins the matched-prose control on the deterministic leverage, fact-unit, density, and yield proxies.",
        ),
        caveats=(
            "The matched-prose control remains the fairness baseline because it spells out the same inspiration set without `@expand`.",
            "The treatment is a longer generated artifact, so this is not an output-brevity claim.",
            "This is saved-output semantic evidence; behavioral proof still requires downstream implementation/use.",
        ),
        conclusion="A useful `@expand` study where compact named inspirations now produce stronger deterministic proxy metrics than matched prose, while still needing behavioral proof.",
    ),
    StudySpec(
        study_id="crowd-factory-puzzle",
        title="Crowd Factory Puzzle",
        path="studies/controlled-studies/games/crowd-factory-puzzle-ablation-study",
        what_it_is=(
            "A browser puzzle game about steering autonomous crowds through factory automation, belts, machines, "
            "crates, spatial pushing rules, hazards, and readable level constraints."
        ),
        evidence_class="Game `@expand` study",
        study_role="Focused expansion evidence where source concepts are already concrete.",
        semantic_trace="workers -> belts/machines -> crate pushing -> hazards -> readable levels",
        strongest_control="matched-prose",
        treatment="promplet",
        variants=(
            VariantSpec(
                "compact-no-expand",
                "[C1] Compact no-expand control",
                "Compact source that names the puzzle inspirations without expansion.",
                "specs/00-control-compact-no-expand-crowd-factory-puzzle.weavemark.md",
                "outputs/compiled-prompts/00-control-compact-no-expand-crowd-factory-puzzle.md",
            ),
            VariantSpec(
                "matched-prose",
                "[C2] Matched-prose no-expand control",
                "Manual prose expansion without using `@expand`.",
                "specs/01-control-matched-prose-no-expand-crowd-factory-puzzle.weavemark.md",
                "outputs/compiled-prompts/01-control-matched-prose-no-expand-crowd-factory-puzzle.md",
            ),
            VariantSpec(
                "promplet",
                "[T] Expanded WeaveMark treatment",
                "Uses `@expand mode: intention` to unpack concept labels into mechanics.",
                "specs/02-treatment-expand-crowd-factory-puzzle.weavemark.md",
                "outputs/compiled-prompts/02-treatment-expand-crowd-factory-puzzle.md",
            ),
        ),
        snippet_phrases={
            "compact-no-expand": ("crowd-control puzzle", "factory automation"),
            "matched-prose": ("integrated mechanic",),
            "source": ("factory automation", "spatial puzzle"),
            "promplet": ("integrated mechanic", "workers"),
        },
        strengths=(
            "`@expand` keeps the source modular and still frames a coherent factory-crowd puzzle.",
            "The treatment wins the matched-prose control on the deterministic leverage, fact-unit, density, and yield proxies.",
            "It captures integration framing across autonomous workers, belts, machines, crates, hazards, and levels.",
        ),
        caveats=(
            "The source concepts are concrete enough that manual prose can unpack them very effectively.",
            "The matched-prose control remains an important fairness baseline even when the treatment wins the proxy metrics.",
            "This is saved-output semantic evidence; behavioral proof still requires downstream implementation/use.",
        ),
        conclusion="A positive `@expand` result: useful for clarity and framing, and currently ahead of matched prose on deterministic proxy metrics.",
    ),
)


SCORES: dict[str, tuple[ScoreSpec, ...]] = {
    "release-readiness": score_set(
        (1, -1, 3, 1, 0, 3, 2),
        (
            "[T] has higher source-only leverage than [C2], though the margin is moderate.",
            "[T] loses yield because [C2] is a very compact template shell.",
            "[T] is much richer across release gates, evidence, validation, risk, waivers, dashboards, and launch audit.",
            "[T] keeps the source readable through reusable release-readiness refinements.",
            "[T] is longer; readability is comparable rather than clearly better.",
            "[T] weaves release obligations through the whole workspace rather than appending a checklist.",
            "[T] uses reusable release, evidence, validation, decision, and programming abstractions.",
        ),
    ),
    "work-intelligence-kanban": score_set(
        (1, -1, 3, 1, 1, 3, 2),
        (
            "[T] has higher source-only leverage than [C2], but not dramatically.",
            "[T] loses yield because [C2] is extremely compact.",
            "[T] adds a fuller signal-to-card-to-output system.",
            "[T] keeps the source readable while moving detail into reusable refinements.",
            "[T] is longer but remains navigable and better structured around the workflow.",
            "[T] propagates monitoring, decisions, delegation, outputs, alerts, and validation through one model.",
            "[T] uses portable work-intelligence and workflow abstractions.",
        ),
    ),
    "evidence-decision": score_set(
        (1, 1, 2, 1, 0, 3, 2),
        (
            "[T] has materially higher source-only leverage than [C2].",
            "[T] wins information yield against [C2].",
            "[T] adds richer evidence, ACH, contradiction, decision-gate, action, API, and AI-safety detail.",
            "[T] source remains readable despite a larger refinement stack.",
            "[T] is much longer, so output readability is mixed.",
            "[T] strongly integrates the source-to-decision trace through storage, UI, automation, APIs, and validation.",
            "[T] uses portable evidence, decision, local-first, and safety abstractions.",
        ),
    ),
    "learning-tutor": score_set(
        (3, 3, 3, 2, 1, 3, 3),
        (
            "[T] uses fewer local source words than [C2] and produces much more output.",
            "[T] has far higher information yield than [C2].",
            "[T] adds concrete adaptive tutoring behavior, diagnosis, practice, and review structure.",
            "[T] source is clearer because pedagogy is named through reusable refinements.",
            "[T] is longer, but the tutor flow is more usable than the flat prose control.",
            "[T] integrates pedagogy through the tutor behavior rather than listing advice.",
            "[T] uses portable teaching and learning-method abstractions.",
        ),
    ),
    "research-brief": score_set(
        (1, 1, 2, 1, 0, 2, 2),
        (
            "[T] has a small leverage edge over [C2].",
            "[T] has a small information-yield edge over [C2].",
            "[T] adds richer epistemic obligations around evidence, alternatives, contradictions, and explainability.",
            "[T] source is readable because reusable research lenses are named directly.",
            "[T] and [C2] have similar output readability.",
            "[T] integrates multiple quality lenses into one research instruction.",
            "[T] uses reusable research-quality abstractions rather than one bespoke checklist.",
        ),
    ),
    "orbital-drift": score_set(
        (3, 3, 3, 2, 0, 2, 2),
        (
            "[T] has dramatically higher source-only leverage than [C2].",
            "[T] has dramatically higher information yield than [C2].",
            "[T] adds browser-game architecture, controls, states, hazards, scoring, restart, and validation.",
            "[T] source is compact and easy to read.",
            "[T] is much longer; output readability is organized but not clearly better.",
            "[T] integrates game mechanics and real-browser validation throughout the specification.",
            "[T] uses reusable web-game and validation abstractions.",
        ),
    ),
    "verdant-relay": score_set(
        (1, 1, 3, 1, 0, 3, 2),
        (
            "[T] has higher source-only leverage than [C2].",
            "[T] has higher information yield than [C2].",
            "[T] integrates tower defense, deckbuilding, ecosystem simulation, assets, balance, and validation.",
            "[T] source names composable mechanics clearly.",
            "[T] is longer; [C2] remains easier to scan.",
            "[T] strongly mingles multiple mechanics into one playable trace.",
            "[T] uses reusable mechanics and production abstractions.",
        ),
    ),
    "transit-city-swarm": score_set(
        (-1, -1, 1, 1, 1, 1, 1),
        (
            "[T] loses source-only leverage to [C2].",
            "[T] loses information yield to [C2].",
            "[T] improves integration framing, but [C2] already writes much of the expansion manually.",
            "[T] keeps the source modular and readable.",
            "[T] output is shorter and still coherent.",
            "[T] better states the combined transit/city/swarm mechanic than the compact control.",
            "[T] demonstrates reusable expansion behavior, though the matched prose control is strong.",
        ),
    ),
    "crowd-factory-puzzle": score_set(
        (1, -1, 0, 1, 0, 1, 1),
        (
            "[T] has a slight source-only leverage edge over [C2].",
            "[T] loses information yield to [C2].",
            "[T] and [C2] are similar because the source concepts are already concrete.",
            "[T] keeps the source modular and readable.",
            "[T] and [C2] have similar output readability.",
            "[T] modestly improves integration framing across workers, belts, machines, crates, hazards, and levels.",
            "[T] demonstrates reusable expansion behavior with a strong caveat.",
        ),
    ),
}


def repo_path(relative_path: str) -> Path:
    """Return a path relative to the repository root."""
    return ROOT / relative_path


def rel_link(from_file: Path, target: Path) -> str:
    """Return a POSIX relative Markdown link from one file to a target."""
    return Path(os.path.relpath(target, from_file.parent)).as_posix()


def markdown_link(from_file: Path, label: str, target: Path) -> str:
    """Create a Markdown link from one generated file to a target."""
    return f"[{label}]({rel_link(from_file, target)})"


def html_path_for(markdown_path: Path) -> Path:
    """Return the synchronized HTML path for a Markdown report."""
    return markdown_path.with_suffix(".html")


def html_link(from_file: Path, label: str, target: Path, css_class: str = "") -> str:
    """Create an HTML link from one generated file to a target."""
    class_attr = f' class="{escape(css_class, quote=True)}"' if css_class else ""
    return (
        f'<a href="{escape(rel_link(from_file, target), quote=True)}"{class_attr}>'
        f"{escape(label)}</a>"
    )


def variant_label(study: StudySpec, variant_name: str) -> str:
    """Return the display label for a study variant."""
    for variant in study.variants:
        if variant.name == variant_name:
            return variant.label
    return variant_name


def metric_rows() -> list[dict[str, float | int | str]]:
    """Compute all semantic-information rows from the registry."""
    return [variant_metrics(variant) for variant in VARIANTS]


def metric_map(
    rows: list[dict[str, float | int | str]],
) -> dict[tuple[str, str], dict[str, float | int | str]]:
    """Index metric rows by study and variant name."""
    return {(str(row["study"]), str(row["variant"])): row for row in rows}


def as_float(value: float | int | str) -> float:
    """Convert a metric value to float."""
    if isinstance(value, str):
        return float(value)
    return float(value)


def format_number(value: float | int | str) -> str:
    """Format metric numbers for Markdown tables."""
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return value


def latest_blind_report_path() -> Path | None:
    """Return the latest available derived blind report, if present."""
    if BLIND_CURRENT_RUN_FILE.exists():
        run_id = BLIND_CURRENT_RUN_FILE.read_text(encoding="utf-8").strip()
        if run_id:
            report = BLIND_ANALYSIS_ROOT / run_id / "derandomized-report.json"
            if report.exists():
                return report
    reports = sorted(BLIND_ANALYSIS_ROOT.glob("*/derandomized-report.json"))
    return reports[-1] if reports else None


def load_blind_summary() -> dict[str, object] | None:
    """Load the latest derandomized blind-analysis summary without private keys."""
    reveal_path = latest_blind_report_path()
    if reveal_path is None:
        return None

    payload = json.loads(reveal_path.read_text(encoding="utf-8"))
    criterion_methods = payload.get("criterion_methods", {})
    study_totals: list[tuple[str, int]] = []
    study_scores: dict[str, tuple[ScoreSpec, ...]] = {}
    study_score_details: dict[str, tuple[BlindCriterionSpec, ...]] = {}
    for study in payload["studies"]:
        study_id = str(study["study_id"])
        study_totals.append((str(study["title"]), int(study["total_delta"])))
        details = tuple(
            BlindCriterionSpec(
                str(row["criterion"]),
                int(row["control_score"]),
                int(row["treatment_score"]),
                int(row["delta"]),
            )
            for row in study["deltas"]
        )
        study_score_details[study_id] = details
        study_scores[study_id] = tuple(
            ScoreSpec(
                detail.criterion,
                detail.delta,
                (
                    f"{criterion_methods.get(detail.criterion, {}).get('blindness', 'blind')} method. "
                    "Blind* absolute scores: "
                    f"{detail.treatment_absolute} for [T] versus "
                    f"{detail.control_absolute} for the strongest control."
                ),
            )
            for detail in details
        )

    packet_count = 0
    leak_count = 0
    manifest_path = reveal_path.parent / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        packet_count = sum(len(study["packets"]) for study in manifest["studies"])
        leak_count = sum(
            sum(packet["leak_counts_after_masking"].values())
            for study in manifest["studies"]
            for packet in study["packets"]
        )

    return {
        "run_id": payload["run_id"],
        "mode": payload["mode"],
        "score_source": payload["score_source"],
        "aggregate_score": int(payload["aggregate_delta"]),
        "study_totals": study_totals,
        "study_scores": study_scores,
        "study_score_details": study_score_details,
        "criterion_methods": criterion_methods,
        "packet_count": packet_count,
        "leak_count": leak_count,
        "leak_risk_note": str(payload.get("leak_risk_note", BLIND_LEAK_RISK_NOTE)),
        "report_path": reveal_path.with_suffix(".md"),
        "html_report_path": reveal_path.with_suffix(".html"),
    }


def excerpt_lines(
    path: Path, phrases: tuple[str, ...], max_lines: int = 4
) -> list[str]:
    """Extract short quote lines from a source or output file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    lowered = [line.lower() for line in lines]
    start = 0
    for phrase in phrases:
        phrase_lower = phrase.lower()
        for index, line in enumerate(lowered):
            if phrase_lower in line:
                start = max(0, index - 1)
                break
        else:
            continue
        break
    else:
        for index, line in enumerate(lines):
            if line.strip() and not line.lstrip().startswith("#"):
                start = index
                break

    collected: list[str] = []
    for line in lines[start:]:
        if collected and not line.strip():
            break
        if not collected and not line.strip():
            continue
        collected.append(line.rstrip())
        if len(collected) >= max_lines:
            break
    if not collected:
        collected = ["(No excerpt available.)"]
    return collected


def excerpt(path: Path, phrases: tuple[str, ...], max_lines: int = 4) -> str:
    """Extract a short quote from a source or output file."""
    collected = excerpt_lines(path, phrases, max_lines)
    return "\n".join(f"> {line}" if line else ">" for line in collected)


def report_header(title: str, report_path: Path) -> str:
    """Return the standard report heading."""
    html_path = html_path_for(report_path)
    return f"# {title}\n\n[View as HTML]({rel_link(report_path, html_path)})\n"


def score_text(score: int) -> str:
    """Format a contrastive score with an explicit sign."""
    return f"{score:+d}"


def study_scores(
    study: StudySpec, blind_summary: dict[str, object] | None = None
) -> tuple[ScoreSpec, ...]:
    """Return the contrastive scores for one study."""
    summary = load_blind_summary() if blind_summary is None else blind_summary
    if summary is not None:
        blind_scores = summary["study_scores"]
        assert isinstance(blind_scores, dict)
        if study.study_id in blind_scores:
            return blind_scores[study.study_id]
    return SCORES[study.study_id]


def total_score(
    study: StudySpec, blind_summary: dict[str, object] | None = None
) -> int:
    """Return the summed contrastive score for one study."""
    return sum(score.score for score in study_scores(study, blind_summary))


def uses_blind_scores(
    study: StudySpec, blind_summary: dict[str, object] | None = None
) -> bool:
    """Return whether this study has primary blind scores available."""
    summary = load_blind_summary() if blind_summary is None else blind_summary
    if summary is None:
        return False
    blind_scores = summary["study_scores"]
    assert isinstance(blind_scores, dict)
    return study.study_id in blind_scores


def score_source_note(
    study: StudySpec, blind_summary: dict[str, object] | None = None
) -> str:
    """Return the score-source note shown near score tables."""
    if uses_blind_scores(study, blind_summary):
        summary = load_blind_summary() if blind_summary is None else blind_summary
        assert summary is not None
        return (
            f"Primary scores are **blind*** using `{summary['score_source']}`: anonymous absolute 1..7 scores "
            "were frozen before reveal, then converted to the -3..+3 treatment-control scale. "
            f"*{summary['leak_risk_note']}*"
        )
    return (
        "Scores are visible-review judgments because no compatible blind reveal artifact "
        "is available for this study."
    )


def score_source_note_html(
    study: StudySpec, blind_summary: dict[str, object] | None = None
) -> str:
    """Return the score-source note shown near HTML score tables."""
    if uses_blind_scores(study, blind_summary):
        summary = load_blind_summary() if blind_summary is None else blind_summary
        assert summary is not None
        return (
            '<p class="inline-note"><strong>Primary scores are blind*</strong> '
            f"using <code>{escape(str(summary['score_source']))}</code>: "
            "anonymous absolute 1..7 scores were frozen before reveal, then converted "
            "to the -3..+3 treatment-control scale. "
            f"<em>{escape(str(summary['leak_risk_note']))}</em></p>"
        )
    return (
        '<p class="inline-note">Scores are visible-review judgments because no compatible '
        "blind reveal artifact is available for this study.</p>"
    )


def score_tone(score: int) -> str:
    """Return a semantic tone for a contrastive score."""
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"


def score_magnitude_class(score: int) -> str:
    """Return the bounded magnitude class used by score visuals."""
    if score == 0:
        return "score-neutral-0"
    return f"score-{score_tone(score)}-{min(abs(score), 3)}"


def score_table_lines(study: StudySpec) -> list[str]:
    """Render the per-study contrastive score table."""
    score_column = "Blind* score" if uses_blind_scores(study) else "Score"
    lines = [
        (
            f"{score_source_note(study)}\n\nScores compare "
            f"{variant_label(study, study.treatment)} against "
            f"{variant_label(study, study.strongest_control)} on the -3..+3 scale "
            "(-3 = dramatically worse, 0 = similar, +3 = dramatically better).\n"
        ),
        f"| Criterion | {score_column} | Evidence |",
        "|---|---:|---|",
    ]
    for score in study_scores(study):
        lines.append(
            f"| {score.criterion} | {score_text(score.score)} | {score.rationale} |"
        )
    lines.append(
        f"| **Total** | **{score_text(total_score(study))}** | Net contrastive gain/loss. |"
    )
    return lines


def metric_definition_lines(
    definitions: tuple[tuple[str, str], ...] = CORE_METRIC_DEFINITIONS
    + SCORE_METRIC_DEFINITIONS,
) -> list[str]:
    """Render metric definitions as Markdown bullets."""
    return [f"- **{term}:** {definition}" for term, definition in definitions]


HTML_STYLE = """
:root {
  color-scheme: light;
  --ink: #142033;
  --muted: #65758f;
  --subtle: #eef3fb;
  --line: #dbe5f2;
  --paper: #ffffff;
  --paper-soft: #f7faff;
  --blue: #3157d5;
  --blue-soft: #e8edff;
  --purple: #6d4bdb;
  --green: #127a4a;
  --green-bg: #e8f7ef;
  --red: #b3261e;
  --red-bg: #fdebea;
  --amber: #a35b00;
  --amber-bg: #fff4d8;
  --shadow: 0 18px 60px rgba(21, 31, 52, 0.13);
  --radius-xl: 28px;
  --radius-lg: 20px;
  --radius-md: 14px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  color: var(--ink);
  background: #f6f8fc;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.55;
  overflow-x: hidden;
}

a { color: var(--blue); text-decoration: none; font-weight: 700; }
a:hover { text-decoration: underline; }

.page-shell { width: min(1360px, calc(100% - 40px)); margin: 0 auto; padding: 18px 0 48px; }

.report-header {
  display: grid;
  gap: 8px;
  padding: 4px 2px 14px;
  border-bottom: 1px solid var(--line);
}
.report-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 14px;
}
.eyebrow { margin: 0; color: var(--muted); font-size: 0.72rem; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(1.85rem, 3vw, 3rem); line-height: 1.04; letter-spacing: -0.035em; overflow-wrap: anywhere; }
.lede { max-width: 980px; margin: 0; color: var(--muted); font-size: clamp(0.98rem, 1.25vw, 1.1rem); }
.hero-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.button-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 11px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--blue);
  background: var(--paper);
  font-size: 0.86rem;
}

main { display: grid; grid-template-columns: minmax(0, 1fr); gap: 18px; margin-top: 18px; }
.section {
  min-width: 0;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  background: rgba(255,255,255,0.94);
  box-shadow: 0 8px 24px rgba(26, 39, 68, 0.06);
}
.section h2 { margin: 0 0 18px; font-size: 1.65rem; letter-spacing: -0.03em; overflow-wrap: anywhere; }
.section-kicker { margin: -8px 0 18px; color: var(--muted); }
.inline-note {
  margin: 0 0 12px;
  color: var(--muted);
  font-size: 0.9rem;
}
.inline-note strong { color: var(--ink); }
.inline-note em { color: #56657e; }

.kpi-grid, .study-grid, .two-column, .snippet-grid, .race-grid, .compact-alert-grid, .insight-grid {
  display: grid;
  gap: 16px;
}
.kpi-grid { grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
.study-grid { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.two-column { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.snippet-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.race-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.compact-alert-grid { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.insight-grid { grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }

.card, .kpi-card, .snippet-card, .race-card, .compact-alert, .insight-card {
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--paper);
}
.card { padding: 20px; }
.kpi-card { padding: 18px; }
.kpi-label { margin: 0; color: var(--muted); font-size: 0.76rem; font-weight: 900; letter-spacing: 0.11em; text-transform: uppercase; }
.kpi-value { margin: 4px 0; font-size: clamp(1.65rem, 4vw, 2rem); font-weight: 950; letter-spacing: -0.04em; overflow-wrap: anywhere; }
.kpi-detail { margin: 0; color: var(--muted); }
.card h3 { margin: 0 0 8px; font-size: 1.08rem; }
.card p { margin: 0 0 10px; color: var(--muted); }
.insight-card {
  padding: 17px 18px;
  border-left: 6px solid var(--blue);
  box-shadow: 0 8px 24px rgba(26, 39, 68, 0.05);
}
.insight-card.gain { border-left-color: var(--green); background: linear-gradient(90deg, rgba(4, 120, 87, 0.08), rgba(255,255,255,0.96)); }
.insight-card.loss { border-left-color: var(--red); background: linear-gradient(90deg, rgba(185, 28, 28, 0.08), rgba(255,255,255,0.96)); }
.insight-card.note { border-left-color: var(--amber); background: linear-gradient(90deg, rgba(180, 83, 9, 0.08), rgba(255,255,255,0.96)); }
.insight-card h3 { margin: 0 0 7px; font-size: 1rem; letter-spacing: -0.01em; }
.insight-card p { margin: 0; color: #52617a; line-height: 1.4; }
.insight-card strong { color: var(--ink); }
.insight-card em { color: #39465e; }
.details-panel {
  padding: 12px 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: rgba(255,255,255,0.76);
}
.details-panel summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  color: #25324a;
  font-weight: 950;
}
.details-panel summary small {
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 800;
}
.details-panel[open] { background: var(--paper); }
.details-panel[open] .definition-grid { margin-top: 14px; }
.definition-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 12px;
}
.definition-card {
  padding: 14px 15px;
  border: 1px solid var(--line);
  border-left: 4px solid var(--blue);
  border-radius: var(--radius-md);
  background: linear-gradient(90deg, rgba(49, 87, 213, 0.06), rgba(255,255,255,0.96));
}
.definition-card h3 {
  margin: 0 0 5px;
  color: #22304a;
  font-size: 0.82rem;
  font-weight: 950;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}
.definition-card p {
  margin: 0;
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.35;
}
.legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.legend-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--paper-soft);
  color: var(--muted);
  font-size: 0.9rem;
  font-weight: 800;
  flex: 0 1 auto;
  min-width: 0;
}
.legend-item span { overflow-wrap: anywhere; }

.race-card {
  padding: 16px;
  display: grid;
  gap: 12px;
  box-shadow: 0 8px 28px rgba(26, 39, 68, 0.07);
}
.race-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}
.race-card h3 { margin: 0; font-size: 1.05rem; line-height: 1.2; }
.race-meta { display: flex; flex-wrap: wrap; gap: 7px; }
.race-meta .badge { padding: 4px 7px; font-size: 0.72rem; }
.metric-race-grid { display: grid; gap: 8px; }
.metric-tile {
  display: grid;
  grid-template-columns: minmax(72px, 0.6fr) minmax(124px, 1.4fr) minmax(54px, auto);
  align-items: center;
  gap: 8px;
  padding: 7px 8px;
  border: 1px solid var(--line);
  border-left: 4px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--paper-soft);
}
.metric-tile.metric-win { border-left-color: var(--green); background: linear-gradient(90deg, rgba(4, 120, 87, 0.08), rgba(255,255,255,0.92)); }
.metric-tile.metric-loss { border-left-color: var(--red); background: linear-gradient(90deg, rgba(185, 28, 28, 0.08), rgba(255,255,255,0.92)); }
.metric-tile.metric-tie { border-left-color: var(--amber); background: linear-gradient(90deg, rgba(180, 83, 9, 0.08), rgba(255,255,255,0.92)); }
.metric-title {
  margin: 0;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}
.metric-values { display: grid; gap: 2px; }
.metric-line { display: grid; grid-template-columns: 1.9rem 1fr; gap: 6px; align-items: baseline; line-height: 1.05; }
.metric-variant { color: var(--muted); font-size: 0.68rem; font-weight: 900; line-height: 1.05; }
.metric-number {
  font-weight: 950;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.03em;
  text-align: right;
  line-height: 1.05;
}
.metric-number.winner { color: var(--green); }
.metric-number.loser { color: var(--red); }
.metric-number.tie { color: var(--amber); }
.metric-winner-label { margin: 0; font-size: 0.72rem; font-weight: 950; text-align: right; }
.metric-winner-label.winner { color: var(--green); }
.metric-winner-label.loser { color: var(--red); }
.metric-winner-label.tie { color: var(--amber); }
.compact-alert {
  padding: 14px 16px;
  border-left: 5px solid var(--amber);
}
.compact-alert strong { display: block; margin-bottom: 5px; }
.compact-alert p { margin: 0; color: var(--muted); }
.compact-alert.loss { border-left-color: var(--red); background: #fffafa; }
.compact-alert.gain { border-left-color: var(--green); background: #f8fffb; }

.table-wrap {
  max-width: 100%;
  min-width: 0;
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--paper);
}
table { width: 100%; border-collapse: collapse; min-width: 760px; }
table.score-matrix {
  table-layout: fixed;
  min-width: 980px;
}
table.blind-score-table {
  table-layout: fixed;
  min-width: 520px;
}
table.blind-score-table th:last-child,
table.blind-score-table td:last-child {
  width: 9rem;
  text-align: center;
}
th, td { padding: 13px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { color: #39465e; background: #f4f7fc; font-size: 0.78rem; font-weight: 900; letter-spacing: 0.07em; text-transform: uppercase; }
td.numeric, th.numeric { text-align: right; font-variant-numeric: tabular-nums; }
.group-start { border-left: 2px solid #b7c7ff; }
tr:last-child td { border-bottom: 0; }
.score-matrix th, .score-matrix td { padding: 10px 9px; vertical-align: middle; }
.score-matrix .study-col { width: 18%; }
.score-matrix .score-col { width: 10%; text-align: center; }
.score-matrix .total-col { width: 12%; text-align: center; }
.score-head {
  display: inline-block;
  max-width: 6.4rem;
  font-size: 0.72rem;
  line-height: 1.08;
}
.study-score-cell { display: grid; gap: 5px; }
.study-score-title { font-size: 0.9rem; line-height: 1.15; }
.study-score-context {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  color: var(--muted);
  font-size: 0.76rem;
  font-weight: 800;
}
.study-score-context .badge { padding: 3px 6px; font-size: 0.68rem; }
.score-matrix td.score-heat {
  font-weight: 950;
  font-variant-numeric: tabular-nums;
  text-align: center;
}
.score-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  font-size: 1rem;
  line-height: 1;
}
.score-matrix td.total-heat .score-mark { font-size: 1.08rem; }

.badge, .score-chip, .direction-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 26px;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 900;
  white-space: nowrap;
}
.badge.control { color: #31506f; background: #e8f0fb; }
.badge.treatment { color: #4d2789; background: #efe8ff; }
.score-chip {
  min-width: 42px;
  font-variant-numeric: tabular-nums;
  border: 1px solid transparent;
}
.score-positive, .direction-win { color: var(--green); background: var(--green-bg); }
.score-negative, .direction-loss { color: var(--red); background: var(--red-bg); }
.score-neutral, .direction-tie { color: #6c5200; background: var(--amber-bg); }
.score-positive-1 { color: #127a4a; background: #e9f8f0; border-color: #cceedd; }
.score-positive-2 { color: #086b42; background: #d6f3e2; border-color: #aee5c9; }
.score-positive-3 { color: #034f31; background: #b8e9cb; border-color: #83d9aa; box-shadow: inset 0 0 0 1px rgba(3, 79, 49, 0.08); }
.score-negative-1 { color: #b3261e; background: #fdebea; border-color: #f5c9c6; }
.score-negative-2 { color: #921b17; background: #f9d4d1; border-color: #efaaa5; }
.score-negative-3 { color: #6f120f; background: #efaaa5; border-color: #df7e77; box-shadow: inset 0 0 0 1px rgba(111, 18, 15, 0.08); }
.score-neutral-0 { color: #6c5200; background: var(--amber-bg); border-color: #eed38b; }
.score-matrix td.score-positive-1 { background: #f0fbf5; }
.score-matrix td.score-positive-2 { background: #dcf5e7; }
.score-matrix td.score-positive-3 { background: #bfeccd; }
.score-matrix td.score-negative-1 { background: #fdeeed; }
.score-matrix td.score-negative-2 { background: #fad9d6; }
.score-matrix td.score-negative-3 { background: #efb0aa; }
.score-matrix td.score-neutral-0 { background: #fff6de; }
.value-chip {
  display: inline-flex;
  justify-content: flex-end;
  min-width: 76px;
  padding: 4px 8px;
  border-radius: 10px;
  font-weight: 950;
}
.value-chip.winner { color: var(--green); background: var(--green-bg); }
.value-chip.loser { color: var(--red); background: var(--red-bg); }
.value-chip.tie { color: var(--amber); background: var(--amber-bg); }

.callout {
  padding: 18px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
}
.callout h3 { margin: 0 0 12px; }
.callout ul { margin: 0; padding-left: 1.15rem; }
.callout li + li { margin-top: 8px; }
.callout.gain { border-color: #b9e8cf; background: var(--green-bg); }
.callout.loss { border-color: #f4c2bf; background: var(--red-bg); }
.callout.note { border-color: #f2d58e; background: var(--amber-bg); }

.snippet-card { overflow: hidden; }
.snippet-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--line); background: var(--paper-soft); }
blockquote {
  margin: 0;
  padding: 16px;
  color: #233047;
  background: #fbfdff;
  border-left: 4px solid var(--blue);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.88rem;
  white-space: pre-wrap;
}

.total-row td { font-weight: 950; background: #f7faff; }
.footer-note { color: var(--muted); font-size: 0.92rem; }

@media (max-width: 720px) {
  .page-shell { width: min(100% - 20px, 1180px); padding-top: 12px; }
  .report-header, .section { padding: 20px; border-radius: 22px; }
  .report-meta { display: grid; grid-template-columns: minmax(0, 1fr); align-items: start; }
  .button-link { width: max-content; max-width: 100%; padding: 6px 10px; font-size: 0.82rem; }
  h1 { max-width: 100%; font-size: clamp(1.55rem, 8vw, 2rem); line-height: 1.08; }
  .lede { max-width: 100%; font-size: 0.96rem; line-height: 1.45; }
  .section h2 { font-size: 1.45rem; }
  .kpi-grid, .study-grid, .two-column, .snippet-grid, .race-grid, .compact-alert-grid, .insight-grid, .definition-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .kpi-grid { gap: 10px; }
  .kpi-card { padding: 14px; }
  .kpi-label { font-size: 0.68rem; letter-spacing: 0.08em; }
  .kpi-detail { font-size: 0.92rem; line-height: 1.35; }
  .legend-row { gap: 7px; }
  .legend-item { padding: 6px 8px; font-size: 0.8rem; gap: 6px; }
  table { min-width: 680px; }
  .metric-race-grid { grid-template-columns: 1fr; }
  .race-grid { grid-template-columns: 1fr; }
}
"""


def variant_badge(label: str) -> str:
    """Return an HTML badge for a study variant label."""
    css_class = "treatment" if label.startswith("[T]") else "control"
    return f'<span class="badge {css_class}">{escape(label)}</span>'


def score_chip(score: int) -> str:
    """Return a colored HTML chip for a score."""
    tone = score_tone(score)
    return (
        f'<span class="score-chip score-{tone} {score_magnitude_class(score)}">'
        f"{escape(score_text(score))}</span>"
    )


def score_heat_cell(score: int, extra_class: str = "score-col") -> str:
    """Return a contrastive score table cell with magnitude-aware fill."""
    tone = score_tone(score)
    classes = f"{extra_class} score-heat score-{tone} {score_magnitude_class(score)}"
    return f'<td class="{classes}"><span class="score-mark">{escape(score_text(score))}</span></td>'


def direction_chip(direction: str) -> str:
    """Return a colored HTML chip for a metric direction."""
    return (
        f'<span class="direction-chip direction-{escape(direction, quote=True)}">'
        f"{escape(direction)}</span>"
    )


def metric_cell(value: float | int | str, suffix: str = "") -> str:
    """Return an escaped metric table cell value."""
    return f"{escape(format_number(value))}{suffix}"


def winner_classes(
    control_value: float, treatment_value: float
) -> tuple[str, str, str]:
    """Return CSS classes and direction for a higher-is-better comparison."""
    if treatment_value > control_value:
        return "loser", "winner", "win"
    if treatment_value < control_value:
        return "winner", "loser", "loss"
    return "tie", "tie", "tie"


def value_chip(value: float | int | str, tone: str, suffix: str = "") -> str:
    """Return a compact emphasized value chip."""
    return f'<span class="value-chip {escape(tone, quote=True)}">{metric_cell(value, suffix)}</span>'


def metric_race_tile(
    title: str,
    control_value: float | int | str,
    treatment_value: float | int | str,
    suffix: str = "",
) -> str:
    """Render one compact control-versus-treatment metric tile."""
    control_numeric = as_float(control_value)
    treatment_numeric = as_float(treatment_value)
    control_class, treatment_class, direction = winner_classes(
        control_numeric, treatment_numeric
    )
    if direction == "win":
        label = "[T] wins"
        label_class = "winner"
    elif direction == "loss":
        label = "[C2] wins"
        label_class = "loser"
    else:
        label = "Tie"
        label_class = "tie"
    return (
        f'<article class="metric-tile metric-{direction}">'
        f'<p class="metric-title">{escape(title)}</p>'
        '<div class="metric-values">'
        '<div class="metric-line">'
        '<span class="metric-variant">[C2]</span>'
        f'<strong class="metric-number {control_class}">{metric_cell(control_value, suffix)}</strong>'
        "</div>"
        '<div class="metric-line">'
        '<span class="metric-variant">[T]</span>'
        f'<strong class="metric-number {treatment_class}">{metric_cell(treatment_value, suffix)}</strong>'
        "</div>"
        "</div>"
        f'<p class="metric-winner-label {label_class}">{escape(label)}</p>'
        "</article>"
    )


def comparison_value_cells(
    control_value: float, treatment_value: float
) -> tuple[str, str]:
    """Render paired table cells with the winner visually emphasized."""
    control_class, treatment_class, _direction = winner_classes(
        control_value, treatment_value
    )
    return (
        f'<td class="numeric group-start">{value_chip(control_value, control_class)}</td>',
        f'<td class="numeric">{value_chip(treatment_value, treatment_class)}</td>',
    )


def short_finding(text: str) -> str:
    """Return a compact label for a gain/failure sentence."""
    lowered = text.lower()
    if "information density" in lowered:
        return "Density loss"
    if "information yield" in lowered:
        return "Yield loss"
    if "source-only leverage" in lowered:
        return "Leverage loss"
    if "discounted fact units" in lowered:
        return "Fact-unit loss"
    if "much longer" in lowered:
        return "Longer output"
    if "matched prose" in lowered:
        return "Matched-prose caveat"
    return text.split(":", 1)[0][:48]


def section(title: str, body: str, kicker: str = "") -> str:
    """Render a report section."""
    kicker_html = f'<p class="section-kicker">{escape(kicker)}</p>' if kicker else ""
    return f'<section class="section"><h2>{escape(title)}</h2>{kicker_html}{body}</section>'


def kpi_card(label: str, value: str, detail: str = "") -> str:
    """Render a KPI card."""
    return (
        '<article class="kpi-card">'
        f'<p class="kpi-label">{escape(label)}</p>'
        f'<p class="kpi-value">{escape(value)}</p>'
        f'<p class="kpi-detail">{escape(detail)}</p>'
        "</article>"
    )


def definition_cards(definitions: tuple[tuple[str, str], ...]) -> str:
    """Render compact metric-definition cards."""
    return (
        '<div class="definition-grid">'
        + "".join(
            '<article class="definition-card">'
            f"<h3>{escape(term)}</h3>"
            f"<p>{escape(definition)}</p>"
            "</article>"
            for term, definition in definitions
        )
        + "</div>"
    )


def details_panel(title: str, body: str, note: str = "") -> str:
    """Render compact progressive disclosure for secondary report details."""
    note_html = f"<small>{escape(note)}</small>" if note else ""
    return (
        '<details class="details-panel">'
        f"<summary><span>{escape(title)}</span>{note_html}</summary>"
        f"{body}"
        "</details>"
    )


def metric_definitions_panel(definitions: tuple[tuple[str, str], ...]) -> str:
    """Render hidden-by-default metric definitions."""
    return details_panel(
        "Metric definitions and scoring legend",
        definition_cards(definitions),
        "Open for exact meanings.",
    )


def insight_card(tone: str, title: str, body_html: str) -> str:
    """Render one high-signal skimming insight."""
    return (
        f'<article class="insight-card {escape(tone, quote=True)}">'
        f"<h3>{escape(title)}</h3>"
        f"<p>{body_html}</p>"
        "</article>"
    )


def study_total_pairs(
    blind_summary: dict[str, object] | None,
) -> list[tuple[StudySpec, int]]:
    """Return study totals from the active primary score source."""
    return [(study, total_score(study, blind_summary)) for study in STUDIES]


def compact_score_list(pairs: list[tuple[StudySpec, int]], limit: int = 4) -> str:
    """Return a compact Markdown list of study-score pairs."""
    return ", ".join(
        f"{study.title} ({score_text(score)})" for study, score in pairs[:limit]
    )


def top_insight_lines(blind_summary: dict[str, object] | None) -> list[str]:
    """Return the most important reader-facing findings."""
    pairs = study_total_pairs(blind_summary)
    wins = sorted(
        (pair for pair in pairs if pair[1] > 0), key=lambda pair: pair[1], reverse=True
    )
    losses = sorted((pair for pair in pairs if pair[1] < 0), key=lambda pair: pair[1])
    neutral = [pair for pair in pairs if pair[1] == 0]
    aggregate_score = sum(score for _study, score in pairs)
    score_label = score_text(aggregate_score) + (
        "*" if blind_summary is not None else ""
    )
    lines = [
        (
            f"- **Exploratory score signal:** {score_label} aggregate across {len(STUDIES)} "
            "single-output studies in this corpus "
            f"({len(wins)} positive deltas, {len(neutral)} neutral, "
            f"{len(losses)} negative deltas)."
        ),
        (
            "- **Pattern in positive deltas:** within this corpus, reusable refinements "
            "score best when they create **semantic structure** mingled through one "
            "final artifact."
        ),
        (
            f"- **Largest positive blind deltas:** {compact_score_list(wins)}."
            if wins
            else "- **Largest positive deltas:** none in the active score source."
        ),
        (
            f"- **Negative deltas:** {compact_score_list(losses)}; these are cases where "
            "**matched prose was already concrete** or the treatment sacrificed density/yield."
            if losses
            else "- **Negative deltas:** none in the active score source."
        ),
        (
            "- **Best honest claim:** WeaveMark is evidence for **reusable specification "
            "refinement and structural mingling**, not a blanket claim that every output is "
            "shorter, denser, or behaviorally better."
        ),
    ]
    if blind_summary is not None:
        lines.append(f"- **Blindness caveat (*):** {blind_summary['leak_risk_note']}")
    return lines


def top_insights_html(blind_summary: dict[str, object] | None) -> str:
    """Render the opening insight cards for the consolidated HTML report."""
    pairs = study_total_pairs(blind_summary)
    wins = sorted(
        (pair for pair in pairs if pair[1] > 0), key=lambda pair: pair[1], reverse=True
    )
    losses = sorted((pair for pair in pairs if pair[1] < 0), key=lambda pair: pair[1])
    neutral = [pair for pair in pairs if pair[1] == 0]
    aggregate_score = sum(score for _study, score in pairs)
    score_label = escape(
        score_text(aggregate_score) + ("*" if blind_summary is not None else "")
    )
    win_text = escape(compact_score_list(wins)) if wins else "none"
    loss_text = escape(compact_score_list(losses)) if losses else "none"
    caveat = (
        insight_card(
            "note",
            "Blindness caveat*",
            f"<em>{escape(str(blind_summary['leak_risk_note']))}</em>",
        )
        if blind_summary is not None
        else ""
    )
    return (
        '<div class="insight-grid">'
        + insight_card(
            (
                "gain"
                if aggregate_score > 0
                else "loss" if aggregate_score < 0 else "note"
            ),
            "Primary score signal",
            (
                f"<strong>{score_label}</strong> aggregate across {len(STUDIES)} "
                "single-output studies in this corpus: "
                f"<strong>{len(wins)} positive deltas</strong>, {len(neutral)} neutral, "
                f"and <strong>{len(losses)} negative deltas</strong>."
            ),
        )
        + insight_card(
            "gain",
            "Pattern in positive deltas",
            (
                "Within this corpus, reusable refinements score best when they create "
                "<strong>semantic structure</strong> that is "
                "<em>mingled through one final artifact</em> rather than appended."
            ),
        )
        + insight_card(
            "gain",
            "Largest positive deltas",
            f"<strong>{win_text}</strong>.",
        )
        + insight_card(
            "loss",
            "Negative deltas",
            (
                f"<strong>{loss_text}</strong>. Negative deltas occur where "
                "<em>matched prose is already concrete</em> "
                "or where the treatment gives up density/yield."
            ),
        )
        + insight_card(
            "note",
            "Honest claim",
            (
                "The evidence supports <strong>reusable specification refinement</strong> and "
                "<strong>structural mingling</strong>, not a universal claim that every output is shorter, "
                "denser, or behaviorally better."
            ),
        )
        + caveat
        + "</div>"
    )


def blind_summary_markdown(report_path: Path, summary: dict[str, object]) -> list[str]:
    """Render the blind-analysis summary for the consolidated Markdown report."""
    blind_report = summary["report_path"]
    assert isinstance(blind_report, Path)
    criterion_methods = summary["criterion_methods"]
    assert isinstance(criterion_methods, dict)
    lines = [
        "\n## Primary blind* score source\n",
        (
            "The contrastive score tables above use this criterion-aware blind* result wherever "
            "a compatible revealed score exists. Mechanical criteria use derived evidence; criteria "
            "that require reading use masked source/output review. Identities are revealed only after "
            "scores are frozen.\n"
        ),
        f"- Run: {markdown_link(report_path, str(summary['run_id']), blind_report)}",
        f"- Mode: `{summary['mode']}`; score source: `{summary['score_source']}`.",
        f"- Anonymous packets checked for direct marker leaks: {summary['packet_count']}.",
        f"- Direct marker leaks after masking: {summary['leak_count']}.",
        f"- Aggregate blind contrastive delta*: **{score_text(int(summary['aggregate_score']))}**.",
        f"- **Leakage-risk note (*):** {summary['leak_risk_note']}",
        "",
        "| Study | Primary blind* delta |",
        "|---|---:|",
    ]
    for study_title, total in summary["study_totals"]:
        lines.append(f"| {study_title} | {score_text(int(total))} |")
    lines.extend(
        [
            "",
            "### Criterion-specific blindness",
            "",
            "| Criterion | Blindness level | Why this method is used | Leakage risk |",
            "|---|---|---|---|",
        ]
    )
    for criterion, details in criterion_methods.items():
        lines.append(
            f"| {criterion} | {details['blindness']} | {details['method']} | {details['leakage_risk']} |"
        )
    return lines


def blind_summary_html(html_path: Path, summary: dict[str, object]) -> str:
    """Render the blind-analysis summary for the consolidated HTML report."""
    blind_report = summary["html_report_path"]
    assert isinstance(blind_report, Path)
    if not blind_report.exists():
        blind_report = summary["report_path"]
        assert isinstance(blind_report, Path)
    rows = "".join(
        "<tr>"
        f"<td>{escape(str(study_title))}</td>"
        f"{score_heat_cell(int(total), 'total-col total-heat')}"
        "</tr>"
        for study_title, total in summary["study_totals"]
    )
    criterion_methods = summary["criterion_methods"]
    assert isinstance(criterion_methods, dict)
    method_rows = "".join(
        "<tr>"
        f"<td>{escape(str(criterion))}</td>"
        f"<td>{escape(str(details['blindness']))}</td>"
        f"<td>{escape(str(details['method']))}</td>"
        f"<td>{escape(str(details['leakage_risk']))}</td>"
        "</tr>"
        for criterion, details in criterion_methods.items()
    )
    return (
        '<div class="kpi-grid">'
        + kpi_card(
            "Primary blind* delta",
            score_text(int(summary["aggregate_score"])) + "*",
            "Used as the primary score source where available.",
        )
        + kpi_card(
            "Run",
            str(summary["run_id"]),
            f"{summary['mode']} / {summary['score_source']}",
        )
        + kpi_card(
            "Packets",
            str(summary["packet_count"]),
            f"{summary['leak_count']} direct marker leaks after masking.",
        )
        + "</div>"
        + '<div class="table-wrap"><table class="blind-score-table">'
        + '<thead><tr><th>Study</th><th class="total-col">Blind* delta</th></tr></thead>'
        + f"<tbody>{rows}</tbody></table></div>"
        + '<p class="inline-note"><strong>*Leakage risk note:</strong> '
        + escape(str(summary["leak_risk_note"]))
        + "</p>"
        + details_panel(
            "Criterion-specific blindness policy",
            '<div class="table-wrap"><table>'
            "<thead><tr><th>Criterion</th><th>Blindness level</th><th>Method</th><th>Leakage risk</th></tr></thead>"
            f"<tbody>{method_rows}</tbody></table></div>",
            "Open to inspect why some criteria require masked reading.",
        )
        + '<p class="footer-note">'
        + html_link(html_path, "Open derandomized blind report", blind_report)
        + "</p>"
    )


def html_document(
    title: str,
    eyebrow: str,
    lede: str,
    body: str,
    html_path: Path,
    markdown_path: Path,
) -> str:
    """Wrap HTML report content in the shared visual shell."""
    markdown = html_link(html_path, "Markdown report", markdown_path, "button-link")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{HTML_STYLE}</style>
</head>
<body>
  <div class="page-shell">
    <header class="report-header">
      <div class="report-meta">
        <p class="eyebrow">{escape(eyebrow)}</p>
        <div class="hero-actions">{markdown}</div>
      </div>
      <h1>{escape(title)}</h1>
      <p class="lede">{escape(lede)}</p>
    </header>
    <main>
      {body}
    </main>
  </div>
</body>
</html>
"""


def score_table_html(study: StudySpec) -> str:
    """Render the contrastive score table as HTML."""
    score_heading = "Blind* score" if uses_blind_scores(study) else "Score"
    source_note = score_source_note_html(study)
    rows = [
        "<tr>"
        f"<td>{escape(score.criterion)}</td>"
        f'<td class="numeric">{score_chip(score.score)}</td>'
        f"<td>{escape(score.rationale)}</td>"
        "</tr>"
        for score in study_scores(study)
    ]
    rows.append(
        '<tr class="total-row">'
        "<td>Total</td>"
        f'<td class="numeric">{score_chip(total_score(study))}</td>'
        "<td>Net contrastive gain/loss.</td>"
        "</tr>"
    )
    return (
        source_note + '<div class="table-wrap"><table>'
        f'<thead><tr><th>Criterion</th><th class="numeric">{escape(score_heading)}</th><th>Evidence</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def excerpt_html(path: Path, phrases: tuple[str, ...]) -> str:
    """Render an excerpt as an HTML blockquote."""
    lines = "\n".join(escape(line) for line in excerpt_lines(path, phrases))
    return f"<blockquote>{lines}</blockquote>"


def source_words(path: Path) -> int:
    """Count local source words."""
    return len(path.read_text(encoding="utf-8").split())


def output_lines(path: Path) -> int:
    """Count output lines."""
    return len(path.read_text(encoding="utf-8").splitlines())


def comparison_failures(
    control: dict[str, float | int | str],
    treatment: dict[str, float | int | str],
    study: StudySpec,
) -> list[str]:
    """Compute measured failures and append study-specific caveats."""
    failures: list[str] = []
    metrics = (
        ("local_leverage", "source-only leverage"),
        ("discounted_fact_units", "discounted fact units"),
        ("information_density_per_1k_output_words", "information density"),
        ("information_yield_per_1k_source_words", "information yield"),
    )
    for key, label in metrics:
        control_value = as_float(control[key])
        treatment_value = as_float(treatment[key])
        if treatment_value < control_value:
            failures.append(
                f"{variant_label(study, study.treatment)} loses {label}: "
                f"{format_number(treatment_value)} versus {format_number(control_value)} "
                f"for {variant_label(study, study.strongest_control)}."
            )
    control_output = as_float(control["output_words"])
    treatment_output = as_float(treatment["output_words"])
    if control_output and treatment_output / control_output >= 3:
        failures.append(
            f"{variant_label(study, study.treatment)} is much longer: "
            f"{format_number(treatment_output)} words versus {format_number(control_output)} "
            f"for {variant_label(study, study.strongest_control)}."
        )
    for caveat in study.caveats:
        if caveat not in failures:
            failures.append(caveat)
    return failures


def comparison_gains(
    control: dict[str, float | int | str],
    treatment: dict[str, float | int | str],
    study: StudySpec,
) -> list[str]:
    """Compute measured gains and append study-specific strengths."""
    gains: list[str] = []
    metrics = (
        ("local_leverage", "source-only leverage"),
        ("discounted_fact_units", "discounted fact units"),
        ("information_density_per_1k_output_words", "information density"),
        ("information_yield_per_1k_source_words", "information yield"),
    )
    for key, label in metrics:
        control_value = as_float(control[key])
        treatment_value = as_float(treatment[key])
        if treatment_value > control_value:
            gains.append(
                f"{variant_label(study, study.treatment)} wins {label}: "
                f"{format_number(treatment_value)} versus {format_number(control_value)} "
                f"for {variant_label(study, study.strongest_control)}."
            )
    for strength in study.strengths:
        if strength not in gains:
            gains.append(strength)
    return gains


def write_ablation_summary(
    study: StudySpec,
    metrics: dict[tuple[str, str], dict[str, float | int | str]],
) -> None:
    """Write one per-study ablation summary."""
    report_path = repo_path(study.path) / "results/ablation-summary.md"
    control = metrics[(study.study_id, study.strongest_control)]
    treatment = metrics[(study.study_id, study.treatment)]
    lines = [report_header(f"{study.title} Ablation Summary", report_path)]
    lines.extend(
        [
            "\n## What the example is\n",
            f"{study.what_it_is}\n",
            "\n## Study role\n",
            f"- **Evidence class:** {study.evidence_class}\n",
            f"- **Study role:** {study.study_role}\n",
            f"- **Semantic trace:** `{study.semantic_trace}`\n",
            "\n## Variant metrics\n",
            (
                "| Variant | Role | Source words | Variable words | Output words | "
                "Leverage | Fact units | Density | Yield |"
            ),
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for variant in study.variants:
        row = metrics[(study.study_id, variant.name)]
        source_link = markdown_link(
            report_path, variant.label, repo_path(study.path) / variant.source
        )
        lines.append(
            "| "
            f"{source_link} | {variant.role} | "
            f"{format_number(row['local_authored_source_words'])} | "
            f"{format_number(row['variable_payload_words'])} | "
            f"{format_number(row['output_words'])} | "
            f"{format_number(row['local_leverage'])}x | "
            f"{format_number(row['discounted_fact_units'])} | "
            f"{format_number(row['information_density_per_1k_output_words'])} | "
            f"{format_number(row['information_yield_per_1k_source_words'])} |"
        )

    lines.extend(["\n## Metric definitions\n"])
    lines.extend(metric_definition_lines(CORE_METRIC_DEFINITIONS))

    lines.extend(
        [
            "\n## Treatment-control comparison\n",
            (
                f"The strongest control is {variant_label(study, study.strongest_control)}. "
                f"The treatment is {variant_label(study, study.treatment)}.\n"
            ),
            (
                f"| Metric | {variant_label(study, study.strongest_control)} | "
                f"{variant_label(study, study.treatment)} | Direction |"
            ),
            "|---|---:|---:|---|",
        ]
    )
    for key, label in (
        ("local_leverage", "Source-only leverage"),
        ("discounted_fact_units", "Discounted fact units"),
        ("information_density_per_1k_output_words", "Information density"),
        ("information_yield_per_1k_source_words", "Information yield"),
    ):
        control_value = as_float(control[key])
        treatment_value = as_float(treatment[key])
        direction = (
            "win"
            if treatment_value > control_value
            else "loss" if treatment_value < control_value else "tie"
        )
        lines.append(
            f"| {label} | {format_number(control_value)} | {format_number(treatment_value)} | {direction} |"
        )

    lines.extend(["\n## Contrastive gain/loss scores\n"])
    lines.extend(score_table_lines(study))
    lines.extend(["\n## Score definitions\n"])
    lines.extend(metric_definition_lines(SCORE_METRIC_DEFINITIONS))
    lines.extend(["\n## Gains\n"])
    lines.extend(f"- {gain}" for gain in comparison_gains(control, treatment, study))
    lines.extend(["\n## Failures and caveats\n"])
    lines.extend(
        f"- {failure}" for failure in comparison_failures(control, treatment, study)
    )
    lines.extend(["\n## Conclusion\n", f"{study.conclusion}\n"])
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_quality_analysis(
    study: StudySpec,
    metrics: dict[tuple[str, str], dict[str, float | int | str]],
) -> None:
    """Write one per-study qualitative analysis."""
    report_path = repo_path(study.path) / "results/final-quality-analysis.md"
    control = metrics[(study.study_id, study.strongest_control)]
    treatment = metrics[(study.study_id, study.treatment)]
    lines = [report_header(f"{study.title} Final Quality Analysis", report_path)]
    lines.extend(
        [
            "\n## Outputs inspected\n",
            "| Variant | Output | Lines | Words |",
            "|---|---|---:|---:|",
        ]
    )
    for variant in study.variants:
        output = repo_path(study.path) / variant.output
        row = metrics[(study.study_id, variant.name)]
        lines.append(
            f"| {variant.label} | {markdown_link(report_path, Path(variant.output).name, output)} | "
            f"{format_number(output_lines(output))} | {format_number(row['output_words'])} |"
        )

    lines.extend(
        [
            "\n## Metric definitions\n",
            "- **Lines:** Saved output line count.",
            "- **Words:** Saved compiled output word count.",
        ]
    )

    lines.extend(["\n## Verbatim snippets\n"])
    for variant in study.variants:
        output = repo_path(study.path) / variant.output
        phrases = study.snippet_phrases.get(variant.name, ())
        lines.extend(
            [
                f"### {variant.label}",
                "",
                excerpt(output, phrases),
                "",
            ]
        )
    source_variant = next(
        variant for variant in study.variants if variant.name == study.treatment
    )
    source = repo_path(study.path) / source_variant.source
    lines.extend(
        [
            f"### {variant_label(study, study.treatment)} source seam",
            "",
            excerpt(source, study.snippet_phrases.get("source", ())),
            "",
        ]
    )

    lines.extend(["## Contrastive gain/loss scores\n"])
    lines.extend(score_table_lines(study))
    lines.extend(["\n## Score definitions\n"])
    lines.extend(metric_definition_lines(SCORE_METRIC_DEFINITIONS))
    lines.extend(["\n## What improved\n"])
    lines.extend(f"- {gain}" for gain in comparison_gains(control, treatment, study))
    lines.extend(["\n## What failed or did not improve\n"])
    lines.extend(
        f"- {failure}" for failure in comparison_failures(control, treatment, study)
    )
    lines.extend(
        [
            "\n## Interpretation\n",
            (
                f"{study.conclusion} The qualitative claim should therefore include both sides: "
                "WeaveMark improves semantic integration where listed above, but the measured failures "
                "and caveats are part of the result, not footnotes.\n"
            ),
        ]
    )
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_ablation_summary_html(
    study: StudySpec,
    metrics: dict[tuple[str, str], dict[str, float | int | str]],
) -> None:
    """Write one per-study HTML ablation summary."""
    markdown_path = repo_path(study.path) / "results/ablation-summary.md"
    html_path = html_path_for(markdown_path)
    control = metrics[(study.study_id, study.strongest_control)]
    treatment = metrics[(study.study_id, study.treatment)]

    variant_rows = []
    for variant in study.variants:
        row = metrics[(study.study_id, variant.name)]
        source = repo_path(study.path) / variant.source
        variant_rows.append(
            "<tr>"
            f"<td>{html_link(html_path, variant.label, source)}<br>{variant_badge(variant.label)}</td>"
            f"<td>{escape(variant.role)}</td>"
            f'<td class="numeric group-start">{metric_cell(row["local_authored_source_words"])}</td>'
            f'<td class="numeric">{metric_cell(row["variable_payload_words"])}</td>'
            f'<td class="numeric">{metric_cell(row["output_words"])}</td>'
            f'<td class="numeric group-start">{metric_cell(row["local_leverage"], "x")}</td>'
            f'<td class="numeric">{metric_cell(row["discounted_fact_units"])}</td>'
            f'<td class="numeric">{metric_cell(row["information_density_per_1k_output_words"])}</td>'
            f'<td class="numeric">{metric_cell(row["information_yield_per_1k_source_words"])}</td>'
            "</tr>"
        )

    comparison_rows = []
    for key, label in (
        ("local_leverage", "Source-only leverage"),
        ("discounted_fact_units", "Discounted fact units"),
        ("information_density_per_1k_output_words", "Information density"),
        ("information_yield_per_1k_source_words", "Information yield"),
    ):
        control_value = as_float(control[key])
        treatment_value = as_float(treatment[key])
        direction = (
            "win"
            if treatment_value > control_value
            else "loss" if treatment_value < control_value else "tie"
        )
        control_cell, treatment_cell = comparison_value_cells(
            control_value, treatment_value
        )
        comparison_rows.append(
            "<tr>"
            f"<td>{escape(label)}</td>"
            f"{control_cell}"
            f"{treatment_cell}"
            f"<td>{direction_chip(direction)}</td>"
            "</tr>"
        )

    gains = "".join(
        f"<li>{escape(gain)}</li>"
        for gain in comparison_gains(control, treatment, study)
    )
    failures = "".join(
        f"<li>{escape(failure)}</li>"
        for failure in comparison_failures(control, treatment, study)
    )
    body = "\n".join(
        [
            section(
                "At a glance",
                '<div class="kpi-grid">'
                + kpi_card(
                    "Net score",
                    score_text(total_score(study)),
                    "Sum of -3..+3 criteria.",
                )
                + kpi_card(
                    "Strongest control",
                    variant_label(study, study.strongest_control),
                    study.evidence_class,
                )
                + kpi_card(
                    "Treatment", variant_label(study, study.treatment), study.study_role
                )
                + kpi_card(
                    "Semantic trace",
                    study.semantic_trace,
                    "Propagation path inspected.",
                )
                + "</div>",
            ),
            section(
                "Variant metrics",
                '<div class="table-wrap"><table>'
                "<thead><tr><th>Variant</th><th>Role</th>"
                '<th class="numeric group-start">Source</th><th class="numeric">Variables</th>'
                '<th class="numeric">Output</th><th class="numeric group-start">Leverage</th>'
                '<th class="numeric">Fact units</th><th class="numeric">Density</th>'
                '<th class="numeric">Yield</th></tr></thead>'
                f"<tbody>{''.join(variant_rows)}</tbody></table></div>",
                "Columns are grouped into authoring size, final output size, and semantic-information proxies.",
            ),
            metric_definitions_panel(CORE_METRIC_DEFINITIONS),
            section(
                "Treatment-control comparison",
                '<div class="table-wrap"><table>'
                "<thead><tr><th>Metric</th>"
                f'<th class="numeric group-start">{escape(variant_label(study, study.strongest_control))}</th>'
                f'<th class="numeric">{escape(variant_label(study, study.treatment))}</th>'
                "<th>Direction</th></tr></thead>"
                f"<tbody>{''.join(comparison_rows)}</tbody></table></div>",
            ),
            section(
                "Contrastive gain/loss scores",
                score_table_html(study),
                (
                    f"Scores compare {variant_label(study, study.treatment)} against "
                    f"{variant_label(study, study.strongest_control)} on the -3..+3 scale."
                ),
            ),
            metric_definitions_panel(SCORE_METRIC_DEFINITIONS),
            section(
                "Gains and failures",
                '<div class="two-column">'
                f'<article class="callout gain"><h3>Gains</h3><ul>{gains}</ul></article>'
                f'<article class="callout loss"><h3>Failures and caveats</h3><ul>{failures}</ul></article>'
                "</div>",
            ),
            section(
                "Conclusion", f"<p><strong>{escape(study.conclusion)}</strong></p>"
            ),
        ]
    )
    html_path.write_text(
        html_document(
            f"{study.title} Ablation Summary",
            "WeaveMark study report",
            study.what_it_is,
            body,
            html_path,
            markdown_path,
        ),
        encoding="utf-8",
    )


def write_quality_analysis_html(
    study: StudySpec,
    metrics: dict[tuple[str, str], dict[str, float | int | str]],
) -> None:
    """Write one per-study HTML qualitative analysis."""
    markdown_path = repo_path(study.path) / "results/final-quality-analysis.md"
    html_path = html_path_for(markdown_path)
    control = metrics[(study.study_id, study.strongest_control)]
    treatment = metrics[(study.study_id, study.treatment)]

    output_rows = []
    snippet_cards = []
    for variant in study.variants:
        output = repo_path(study.path) / variant.output
        row = metrics[(study.study_id, variant.name)]
        output_rows.append(
            "<tr>"
            f"<td>{variant_badge(variant.label)}</td>"
            f"<td>{html_link(html_path, Path(variant.output).name, output)}</td>"
            f'<td class="numeric group-start">{format_number(output_lines(output))}</td>'
            f'<td class="numeric">{metric_cell(row["output_words"])}</td>'
            "</tr>"
        )
        snippet_cards.append(
            '<article class="snippet-card">'
            f'<div class="snippet-head">{variant_badge(variant.label)}'
            f"{html_link(html_path, 'Open output', output)}</div>"
            f"{excerpt_html(output, study.snippet_phrases.get(variant.name, ()))}</article>"
        )

    source_variant = next(
        variant for variant in study.variants if variant.name == study.treatment
    )
    source = repo_path(study.path) / source_variant.source
    snippet_cards.append(
        '<article class="snippet-card">'
        f'<div class="snippet-head">{variant_badge(variant_label(study, study.treatment))}'
        f"{html_link(html_path, 'Open source seam', source)}</div>"
        f"{excerpt_html(source, study.snippet_phrases.get('source', ()))}</article>"
    )
    gains = "".join(
        f"<li>{escape(gain)}</li>"
        for gain in comparison_gains(control, treatment, study)
    )
    failures = "".join(
        f"<li>{escape(failure)}</li>"
        for failure in comparison_failures(control, treatment, study)
    )
    body = "\n".join(
        [
            section(
                "Outputs inspected",
                '<div class="table-wrap"><table>'
                "<thead><tr><th>Variant</th><th>Output</th>"
                '<th class="numeric group-start">Lines</th><th class="numeric">Words</th>'
                "</tr></thead>"
                f"<tbody>{''.join(output_rows)}</tbody></table></div>",
            ),
            metric_definitions_panel(
                (
                    ("Lines", "Saved output line count."),
                    ("Words", "Saved compiled output word count."),
                )
            ),
            section(
                "Verbatim snippets",
                f'<div class="snippet-grid">{"".join(snippet_cards)}</div>',
                "Verbatim source/output material quoted from saved artifacts.",
            ),
            section(
                "Contrastive gain/loss scores",
                score_table_html(study),
                (
                    f"Scores compare {variant_label(study, study.treatment)} against "
                    f"{variant_label(study, study.strongest_control)} on the -3..+3 scale."
                ),
            ),
            metric_definitions_panel(SCORE_METRIC_DEFINITIONS),
            section(
                "What improved and what failed",
                '<div class="two-column">'
                f'<article class="callout gain"><h3>What improved</h3><ul>{gains}</ul></article>'
                f'<article class="callout loss"><h3>What failed or did not improve</h3><ul>{failures}</ul></article>'
                "</div>",
            ),
            section(
                "Interpretation",
                (
                    f"<p><strong>{escape(study.conclusion)}</strong> "
                    "The qualitative claim should include both sides: WeaveMark improves semantic "
                    "integration where shown, but the measured failures and caveats are part of the result.</p>"
                ),
            ),
        ]
    )
    html_path.write_text(
        html_document(
            f"{study.title} Final Quality Analysis",
            "WeaveMark qualitative report",
            study.what_it_is,
            body,
            html_path,
            markdown_path,
        ),
        encoding="utf-8",
    )


def aggregate(
    rows: list[dict[str, float | int | str]], study_ids: set[str], variants: set[str]
) -> dict[str, float]:
    """Aggregate key metrics across selected rows."""
    selected = [
        row for row in rows if row["study"] in study_ids and row["variant"] in variants
    ]
    return {
        "local_words": sum(
            as_float(row["local_authored_source_words"]) for row in selected
        ),
        "variable_words": sum(
            as_float(row["variable_payload_words"]) for row in selected
        ),
        "output_words": sum(as_float(row["output_words"]) for row in selected),
        "fact_units": sum(as_float(row["discounted_fact_units"]) for row in selected),
    }


def write_consolidated_results(rows: list[dict[str, float | int | str]]) -> None:
    """Write the top-level consolidated study result."""
    report_path = CONTROLLED_STUDIES_ROOT / "results.md"
    metrics = metric_map(rows)
    headline_ids = {study.study_id for study in STUDIES if study.headline}
    all_ids = {study.study_id for study in STUDIES}
    treatment_names = {study.treatment for study in STUDIES}
    control_names = {study.strongest_control for study in STUDIES}
    headline_treatment = aggregate(rows, headline_ids, treatment_names)
    headline_control = aggregate(rows, headline_ids, control_names)
    all_treatment = aggregate(rows, all_ids, treatment_names)
    all_control = aggregate(rows, all_ids, control_names)
    blind_summary = load_blind_summary()

    lines = [report_header("WeaveMark Studies Result", report_path)]
    lines.extend(
        [
            "\n## Bottom line\n",
            (
                "**Criterion-aware blind* scores are now the primary comparative signal wherever available.** "
                "WeaveMark's strongest result remains single-output semantic reuse with structural "
                "mingling: reusable specifications are adapted into one final artifact instead of appended as "
                "deterministic sections. The reports also show failures clearly: matched templates "
                "often remain denser, and matched prose can beat `@expand` on raw information yield.\n"
            ),
            (
                "Variant markers are preserved throughout the studies: [C1] is the compact/manual "
                "control, [C2] is the strongest matched control, and [T] is the WeaveMark treatment.\n"
            ),
            "\n## Key insights\n",
            *top_insight_lines(blind_summary),
            "\n## Study coverage\n",
            "| Study | What the example is | Study role |",
            "|---|---|---|",
        ]
    )
    for study in STUDIES:
        lines.append(
            f"| {markdown_link(report_path, study.title, repo_path(study.path))} | "
            f"{study.what_it_is} | {study.study_role} |"
        )

    lines.extend(["\n## Metric definitions\n"])
    lines.extend(
        metric_definition_lines(
            CORE_METRIC_DEFINITIONS
            + SCORE_METRIC_DEFINITIONS
            + BLIND_METRIC_DEFINITIONS
        )
    )

    lines.extend(
        [
            "\n## Post-reveal treatment-control metrics\n",
            (
                "| Study | Control | Treatment | Control leverage | Treatment leverage | "
                "Control fact units | Treatment fact units | Control yield | Treatment yield | Main failure |"
            ),
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for study in STUDIES:
        control = metrics[(study.study_id, study.strongest_control)]
        treatment = metrics[(study.study_id, study.treatment)]
        failures = comparison_failures(control, treatment, study)
        lines.append(
            f"| {markdown_link(report_path, study.title, repo_path(study.path))} | "
            f"{variant_label(study, study.strongest_control)} | "
            f"{variant_label(study, study.treatment)} | "
            f"{format_number(control['local_leverage'])}x | "
            f"{format_number(treatment['local_leverage'])}x | "
            f"{format_number(control['discounted_fact_units'])} | "
            f"{format_number(treatment['discounted_fact_units'])} | "
            f"{format_number(control['information_yield_per_1k_source_words'])} | "
            f"{format_number(treatment['information_yield_per_1k_source_words'])} | "
            f"{failures[0] if failures else 'No measured failure against strongest control.'} |"
        )

    lines.extend(
        [
            "\n## Contrastive gain/loss scores (primary blind*)\n",
            (
                "Scores compare each [T] WeaveMark treatment against the strongest listed control on "
                "the -3..+3 scale (-3 = dramatically worse, 0 = similar, +3 = dramatically better). "
                "Where a revealed blind run is available, these are criterion-aware blind* scores.\n"
            ),
            (
                "| Study | Control | Treatment | Authoring leverage | Information yield | Grounded expressiveness | "
                "Input readability | Output readability | Constraint integration | Reusable abstraction | Total |"
            ),
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for study in STUDIES:
        scores = study_scores(study)
        lines.append(
            f"| {markdown_link(report_path, study.title, repo_path(study.path))} | "
            f"{variant_label(study, study.strongest_control)} | "
            f"{variant_label(study, study.treatment)} | "
            f"{score_text(scores[0].score)} | "
            f"{score_text(scores[1].score)} | "
            f"{score_text(scores[2].score)} | "
            f"{score_text(scores[3].score)} | "
            f"{score_text(scores[4].score)} | "
            f"{score_text(scores[5].score)} | "
            f"{score_text(scores[6].score)} | "
            f"{score_text(total_score(study))} |"
        )

    lines.extend(
        [
            "\n## Aggregate signal\n",
            "### Headline subset\n",
            f"- Strongest controls: {format_number(headline_control['local_words'])} local source words, "
            f"{format_number(headline_control['output_words'])} output words, "
            f"{format_number(headline_control['fact_units'])} discounted fact units.",
            f"- Treatments: {format_number(headline_treatment['local_words'])} local source words, "
            f"{format_number(headline_treatment['output_words'])} output words, "
            f"{format_number(headline_treatment['fact_units'])} discounted fact units.",
            "\n### Full study corpus\n",
            f"- Strongest controls: {format_number(all_control['local_words'])} local source words, "
            f"{format_number(all_control['output_words'])} output words, "
            f"{format_number(all_control['fact_units'])} discounted fact units.",
            f"- Treatments: {format_number(all_treatment['local_words'])} local source words, "
            f"{format_number(all_treatment['output_words'])} output words, "
            f"{format_number(all_treatment['fact_units'])} discounted fact units.",
        ]
    )
    if blind_summary is not None:
        lines.extend(blind_summary_markdown(report_path, blind_summary))
    lines.append("\n## Post-reveal qualitative gains and failures\n")
    for study in STUDIES:
        control = metrics[(study.study_id, study.strongest_control)]
        treatment = metrics[(study.study_id, study.treatment)]
        lines.extend(
            [
                f"### {study.title}",
                "",
                f"- **What it is:** {study.what_it_is}",
                f"- **Best gain:** {comparison_gains(control, treatment, study)[0]}",
                f"- **Important failure/caveat:** {comparison_failures(control, treatment, study)[0]}",
                f"- **Conclusion:** {study.conclusion}",
                "",
            ]
        )

    lines.extend(
        [
            "## What not to claim yet\n",
            "- Do not claim downstream users or programming agents perform better; that has not been measured.",
            "- Do not treat contrastive scores or semantic-information proxies as behavioral proof.",
            "- Do not treat output length as quality unless added text introduces operational obligations.",
            "- Do not hide negative results: lower density, lower yield, weaker readability, and matched-prose wins are part of the study evidence.",
            "\n## Reproducibility\n",
            "Update this report, per-study reports, and the metric snapshot with:",
            "",
            "```bash",
            "python studies/tools/blind_analysis.py metric-pass",
            "python studies/tools/regenerate_reports.py --clear",
            "```",
            "",
            "Then run structural scans and link checks as described in [AGENTS.md](AGENTS.md).",
        ]
    )
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_consolidated_results_html(rows: list[dict[str, float | int | str]]) -> None:
    """Write the top-level consolidated HTML study result."""
    markdown_path = CONTROLLED_STUDIES_ROOT / "results.md"
    html_path = html_path_for(markdown_path)
    metrics = metric_map(rows)
    headline_ids = {study.study_id for study in STUDIES if study.headline}
    all_ids = {study.study_id for study in STUDIES}
    treatment_names = {study.treatment for study in STUDIES}
    control_names = {study.strongest_control for study in STUDIES}
    headline_treatment = aggregate(rows, headline_ids, treatment_names)
    headline_control = aggregate(rows, headline_ids, control_names)
    all_treatment = aggregate(rows, all_ids, treatment_names)
    all_control = aggregate(rows, all_ids, control_names)
    blind_summary = load_blind_summary()
    primary_totals = study_total_pairs(blind_summary)
    net_score = sum(score for _study, score in primary_totals)
    win_count = sum(1 for _study, score in primary_totals if score > 0)
    neutral_count = sum(1 for _study, score in primary_totals if score == 0)
    loss_count = sum(1 for _study, score in primary_totals if score < 0)
    score_source_detail = (
        "Primary blind* contrastive score."
        if blind_summary is not None
        else "Visible-review contrastive score."
    )
    legend_html = (
        '<div class="legend-row">'
        f'<div class="legend-item">{variant_badge("[C1]")}<span>Compact</span></div>'
        f'<div class="legend-item">{variant_badge("[C2]")}<span>Matched</span></div>'
        f'<div class="legend-item">{variant_badge("[T]")}<span>WeaveMark</span></div>'
        "</div>"
    )

    study_cards = []
    metric_race_cards = []
    caveat_cards = []
    score_rows_html = []
    qualitative_cards = []
    for study in STUDIES:
        control = metrics[(study.study_id, study.strongest_control)]
        treatment = metrics[(study.study_id, study.treatment)]
        failures = comparison_failures(control, treatment, study)
        gains = comparison_gains(control, treatment, study)
        ablation_html = html_path_for(
            repo_path(study.path) / "results/ablation-summary.md"
        )
        quality_html = html_path_for(
            repo_path(study.path) / "results/final-quality-analysis.md"
        )
        study_cards.append(
            '<article class="card">'
            f"<h3>{html_link(html_path, study.title, repo_path(study.path))}</h3>"
            f"<p>{escape(study.what_it_is)}</p>"
            f"<p>{score_chip(total_score(study))} Net contrastive score</p>"
            f'<p class="footer-note">{html_link(html_path, "Ablation HTML", ablation_html)} '
            f'&middot; {html_link(html_path, "Quality HTML", quality_html)}</p>'
            "</article>"
        )
        metric_race_cards.append(
            '<article class="race-card">'
            '<div class="race-card-head">'
            f"<h3>{html_link(html_path, study.title, repo_path(study.path))}</h3>"
            f"{score_chip(total_score(study))}"
            "</div>"
            '<div class="race-meta">'
            f'<span title="{escape(variant_label(study, study.strongest_control), quote=True)}">{variant_badge("[C2]")}</span>'
            f'<span title="{escape(variant_label(study, study.treatment), quote=True)}">{variant_badge("[T]")}</span>'
            "</div>"
            '<div class="metric-race-grid">'
            + metric_race_tile(
                "Leverage",
                control["local_leverage"],
                treatment["local_leverage"],
                "x",
            )
            + metric_race_tile(
                "Fact units",
                control["discounted_fact_units"],
                treatment["discounted_fact_units"],
            )
            + metric_race_tile(
                "Yield",
                control["information_yield_per_1k_source_words"],
                treatment["information_yield_per_1k_source_words"],
            )
            + "</div>"
            "</article>"
        )
        caveat_cards.append(
            '<article class="compact-alert loss">'
            f"<strong>{escape(study.title)} · {escape(short_finding(failures[0]))}</strong>"
            f"<p>{escape(failures[0])}</p>"
            "</article>"
        )
        scores = study_scores(study)
        control_label = variant_label(study, study.strongest_control)
        treatment_label = variant_label(study, study.treatment)
        control_marker = control_label.split(" ", 1)[0]
        treatment_marker = treatment_label.split(" ", 1)[0]
        comparison_title = f"{treatment_label} vs {control_label}"
        compact_title = COMPACT_STUDY_TITLES.get(study.study_id, study.title)
        score_rows_html.append(
            "<tr>"
            '<td class="study-col">'
            f'<div class="study-score-cell" title="{escape(comparison_title, quote=True)}">'
            f'<div class="study-score-title">{html_link(html_path, compact_title, repo_path(study.path))}</div>'
            '<div class="study-score-context">'
            f"{variant_badge(treatment_marker)}"
            "<span>vs</span>"
            f"{variant_badge(control_marker)}"
            "</div>"
            "</div>"
            "</td>"
            f"{score_heat_cell(scores[0].score, 'score-col group-start')}"
            f"{score_heat_cell(scores[1].score)}"
            f"{score_heat_cell(scores[2].score)}"
            f"{score_heat_cell(scores[3].score)}"
            f"{score_heat_cell(scores[4].score)}"
            f"{score_heat_cell(scores[5].score)}"
            f"{score_heat_cell(scores[6].score)}"
            f"{score_heat_cell(total_score(study), 'total-col group-start total-heat')}"
            "</tr>"
        )
        qualitative_cards.append(
            '<article class="card">'
            f"<h3>{escape(study.title)}</h3>"
            f"<p><strong>Best gain:</strong> {escape(gains[0])}</p>"
            f"<p><strong>Important failure/caveat:</strong> {escape(failures[0])}</p>"
            f"<p><strong>Conclusion:</strong> {escape(study.conclusion)}</p>"
            "</article>"
        )

    sections = [
        section(
            "At a glance",
            legend_html
            + '<div class="kpi-grid">'
            + kpi_card(
                "Exploratory outcome",
                f"{win_count}/9 positive",
                f"{neutral_count} neutral, {loss_count} negative deltas in this corpus.",
            )
            + kpi_card(
                "Net score",
                score_text(net_score) + ("*" if blind_summary is not None else ""),
                score_source_detail,
            )
            + kpi_card("Study count", str(len(STUDIES)), "Single-output study corpus.")
            + kpi_card(
                "Headline studies",
                str(len(headline_ids)),
                "Realistic/product and key stress-test cases.",
            )
            + kpi_card(
                "Metric rows", str(len(rows)), "Every [C1], [C2], and [T] variant."
            )
            + "</div>",
            "Markers and headline result.",
        ),
        section(
            "Key insights",
            top_insights_html(blind_summary),
            "What a reader should understand after skimming.",
        ),
        metric_definitions_panel(
            CORE_METRIC_DEFINITIONS
            + SCORE_METRIC_DEFINITIONS
            + BLIND_METRIC_DEFINITIONS
        ),
        section(
            "Post-reveal metric race",
            f'<div class="race-grid">{"".join(metric_race_cards)}</div>',
            (
                "Deterministic treatment-control metric context after reveal. Bold green numbers "
                "are the winner for each metric; red numbers show the losing side. Caveats are summarized separately below."
            ),
        ),
        section(
            "Key caveats to notice",
            f'<div class="compact-alert-grid">{"".join(caveat_cards)}</div>',
            "Long findings are kept out of the metric race so the numbers stay scannable.",
        ),
        section(
            "Contrastive gain/loss scores",
            '<div class="table-wrap"><table class="score-matrix">'
            '<thead><tr><th class="study-col">Study and comparison</th>'
            '<th class="score-col group-start" title="Authoring leverage"><span class="score-head">Authoring<br>leverage</span></th>'
            '<th class="score-col" title="Information yield"><span class="score-head">Information<br>yield</span></th>'
            '<th class="score-col" title="Grounded expressiveness"><span class="score-head">Grounded<br>expressiveness</span></th>'
            '<th class="score-col" title="Input readability"><span class="score-head">Input<br>readability</span></th>'
            '<th class="score-col" title="Output readability"><span class="score-head">Output<br>readability</span></th>'
            '<th class="score-col" title="Constraint integration"><span class="score-head">Constraint<br>integration</span></th>'
            '<th class="score-col" title="Reusable abstraction quality"><span class="score-head">Reusable<br>abstraction</span></th>'
            '<th class="total-col group-start" title="Total score"><span class="score-head">Total<br>score</span></th></tr></thead>'
            f"<tbody>{''.join(score_rows_html)}</tbody></table></div>",
            "Scores use the -3..+3 scale. Color intensity is proportional to magnitude; criterion-aware blind* values are primary where available.",
        ),
        section(
            "Aggregate signal",
            '<div class="kpi-grid">'
            + kpi_card(
                "Headline controls",
                format_number(headline_control["fact_units"]),
                f"{format_number(headline_control['local_words'])} local words.",
            )
            + kpi_card(
                "Headline treatments",
                format_number(headline_treatment["fact_units"]),
                f"{format_number(headline_treatment['local_words'])} local words.",
            )
            + kpi_card(
                "All controls",
                format_number(all_control["fact_units"]),
                f"{format_number(all_control['output_words'])} output words.",
            )
            + kpi_card(
                "All treatments",
                format_number(all_treatment["fact_units"]),
                f"{format_number(all_treatment['output_words'])} output words.",
            )
            + "</div>",
            "Fact-unit totals are deterministic semantic-information proxies, not behavioral proof.",
        ),
    ]
    if blind_summary is not None:
        sections.append(
            section(
                "Primary blind* score source",
                blind_summary_html(html_path, blind_summary),
                (
                    "Anonymous scores are frozen before reveal; the asterisk marks the remaining "
                    "criterion-specific leakage caveat."
                ),
            )
        )
    sections.extend(
        [
            section(
                "Study coverage",
                f'<div class="study-grid">{"".join(study_cards)}</div>',
            ),
            section(
                "Post-reveal qualitative gains and failures",
                f'<div class="study-grid">{"".join(qualitative_cards)}</div>',
            ),
            section(
                "What not to claim yet",
                '<article class="callout note"><ul>'
                "<li>Do not claim downstream users or programming agents perform better; that has not been measured.</li>"
                "<li>Do not treat contrastive scores or semantic-information proxies as behavioral proof.</li>"
                "<li>Do not treat output length as quality unless added text introduces operational obligations.</li>"
                "<li>Do not hide negative results: lower density, lower yield, weaker readability, and matched-prose wins are evidence.</li>"
                "</ul></article>",
            ),
        ]
    )
    body = "\n".join(sections)
    html_path.write_text(
        html_document(
            "WeaveMark Studies Result",
            "WeaveMark study corpus",
            (
                "Single-output semantic reuse with structural mingling is the strongest result; "
                "matched-template density and matched-prose @expand wins remain visible caveats."
            ),
            body,
            html_path,
            markdown_path,
        ),
        encoding="utf-8",
    )


def clear_reports() -> None:
    """Remove report artifacts before rewriting them."""
    for study in STUDIES:
        results_dir = repo_path(study.path) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        for report in (*results_dir.glob("*.md"), *results_dir.glob("*.html")):
            report.unlink()
    top_level_results = tuple(CONTROLLED_STUDIES_ROOT.glob("results*.md")) + tuple(
        CONTROLLED_STUDIES_ROOT.glob("results*.html")
    )
    for path in (
        *top_level_results,
        CONTROLLED_STUDIES_ROOT / "metrics/semantic-information.json",
    ):
        if path.exists():
            path.unlink()


def write_metrics(rows: list[dict[str, float | int | str]]) -> None:
    """Write the metric snapshot."""
    output = CONTROLLED_STUDIES_ROOT / "metrics/semantic-information.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def write_reports(rows: list[dict[str, float | int | str]]) -> None:
    """Write all synchronized report artifacts."""
    metrics = metric_map(rows)
    for study in STUDIES:
        write_ablation_summary(study, metrics)
        write_ablation_summary_html(study, metrics)
        write_quality_analysis(study, metrics)
        write_quality_analysis_html(study, metrics)
    write_consolidated_results(rows)
    write_consolidated_results_html(rows)


def main() -> None:
    """Entry point for the report generator."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete Markdown and HTML reports before rewriting them.",
    )
    args = parser.parse_args()

    if args.clear:
        clear_reports()
    rows = metric_rows()
    write_metrics(rows)
    write_reports(rows)
    print(f"Updated {len(rows)} metric rows and reports for {len(STUDIES)} studies.")


if __name__ == "__main__":
    main()
