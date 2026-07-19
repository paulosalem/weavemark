"""Compiler context and deterministic artifact rendering for references."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol


class ReferenceResource(Protocol):
    """Reference fields required by context and appendix renderers."""

    id: str
    path: str
    content: str
    keep: bool
    scope: str
    parent_id: str | None
    sha256: str
    media_type: str

    @property
    def resolved_path(self) -> Path: ...


def format_reference_context(references: Sequence[ReferenceResource]) -> str:
    """Render compiler-only reference resources with explicit boundaries."""

    if not references:
        return "No referenced source files."
    sections: list[str] = []
    for reference in references:
        sections.append(
            "\n".join(
                (
                    f'<weavemark-reference id="{reference.id}" '
                    f'path="{_xml_escape(reference.path)}" '
                    f'keep="{str(reference.keep).lower()}" '
                    f'scope="{_xml_escape(reference.scope)}"'
                    + (
                        f' parent_id="{reference.parent_id}"'
                        if reference.parent_id is not None
                        else ""
                    )
                    + ">",
                    reference.content,
                    "</weavemark-reference>",
                )
            )
        )
    return "\n\n".join(sections)


def materialize_reference_appendices(
    composed_prompt: str,
    prompts: Mapping[str, str],
    references: Sequence[ReferenceResource],
    resolved_contents: Mapping[str, str],
) -> tuple[str, dict[str, str], list[str]]:
    """Append retained references deterministically to their prompt scopes."""

    errors: list[str] = []
    kept = [reference for reference in references if reference.keep]
    for reference in references:
        if reference.id not in resolved_contents:
            errors.append(
                f"Compiler response omitted resolved reference '{reference.id}' "
                f"for {reference.path!r}."
            )
    if errors:
        return composed_prompt, dict(prompts), errors

    default_refs = [reference for reference in kept if reference.scope == "default"]
    named_refs: dict[str, list[ReferenceResource]] = {}
    for reference in kept:
        if reference.scope != "default":
            named_refs.setdefault(reference.scope, []).append(reference)

    rendered_prompts = dict(prompts)
    rendered_composed = _append_reference_document(
        composed_prompt,
        default_refs,
        resolved_contents,
    )
    if "default" in rendered_prompts:
        rendered_prompts["default"] = _append_reference_document(
            rendered_prompts["default"],
            default_refs,
            resolved_contents,
        )
    for name, scoped in named_refs.items():
        if name in rendered_prompts:
            rendered_prompts[name] = _append_reference_document(
                rendered_prompts[name],
                scoped,
                resolved_contents,
            )
    return rendered_composed, rendered_prompts, []


def _append_reference_document(
    prompt: str,
    references: list[ReferenceResource],
    resolved_contents: Mapping[str, str],
) -> str:
    if not references:
        return prompt
    entries: list[str] = []
    for reference in references:
        content = resolved_contents[reference.id].rstrip()
        entries.append(
            "\n".join(
                (
                    f"## Reference {reference.id} — {reference.resolved_path.name}",
                    "",
                    f"- Source: `{reference.path}`",
                    f"- Media type: `{reference.media_type}`",
                    f"- SHA-256: `{reference.sha256}`",
                    "",
                    content,
                )
            )
        )
    appendix = "# Reference Appendix\n\n" + "\n\n".join(entries)
    if not prompt:
        return appendix
    return f"{prompt.rstrip()}\n\n***\n\n{appendix}"


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


__all__ = ["format_reference_context", "materialize_reference_appendices"]
