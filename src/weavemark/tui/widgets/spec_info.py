"""Spec info widget — displays metadata about the loaded spec."""

from __future__ import annotations

from textual.widgets import Static

from weavemark.tui.scanner import SpecMetadata


class SpecInfoPanel(Static):
    """Displays promplet metadata: title, strategy, prompts, tools, etc."""

    DEFAULT_CSS = """
    SpecInfoPanel {
        height: auto;
        padding: 1;
        border: round $primary-darken-1;
        margin-bottom: 1;
    }
    """

    def __init__(self, metadata: SpecMetadata, **kwargs) -> None:
        super().__init__("", markup=True, **kwargs)
        self._metadata = metadata

    def on_mount(self) -> None:
        m = self._metadata
        lines: list[str] = []

        if m.title:
            lines.append(f"[bold]{m.title}[/bold]")
        if m.description:
            desc = m.description[:120] + ("…" if len(m.description) > 120 else "")
            lines.append(f"[dim]{desc}[/dim]")

        if m.execution:
            strategy = m.execution.get("type", "unknown")
            params = ", ".join(
                f"{k}={v}" for k, v in m.execution.items() if k != "type"
            )
            lines.append(
                f"⚡ Strategy: [bold]{strategy}[/bold]"
                + (f" ({params})" if params else "")
            )

        if m.compile:
            params = ", ".join(f"{k}={v}" for k, v in m.compile.items())
            lines.append(f"📦 Compile: {params}")

        if m.prompt_names:
            lines.append(f"📝 Prompts: {', '.join(m.prompt_names)}")

        if m.tool_names:
            lines.append(f"🔧 Tools: {', '.join(m.tool_names)}")

        if m.refine_files:
            lines.append(f"🔗 Deps: {', '.join(m.refine_files)}")

        if m.reference_files:
            unique = list(dict.fromkeys(m.reference_files))
            lines.append(f"📚 References: {', '.join(unique)}")

        if m.embed_files:
            unique = list(dict.fromkeys(m.embed_files))
            lines.append(f"📎 Embedded: {', '.join(unique)}")

        if m.emit_files:
            unique = list(dict.fromkeys(m.emit_files))
            lines.append(f"📤 Emits: {', '.join(unique)}")

        if m.assertions:
            lines.append(f"✅ Assertions: {len(m.assertions)}")

        n_inputs = len(m.inputs)
        lines.append(f"📋 Inputs: {n_inputs}")

        self.update("\n".join(lines))
