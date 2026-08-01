"""Lightweight console dispatch before the full Processor runtime is imported."""

from __future__ import annotations

import os
import sys

from weavemark.version import LANGUAGE_VERSION, PROCESSOR_VERSION


def cli() -> None:
    """Dispatch informational and library commands without loading the LLM stack."""

    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print(
            f"weavemark {PROCESSOR_VERSION} "
            f"(WeaveMark language {LANGUAGE_VERSION})"
        )
        return

    if len(sys.argv) > 1 and sys.argv[1] == "library":
        from weavemark.library_cli import (
            LIBRARY_MANAGEMENT_COMMANDS,
            create_library_parser,
            parse_library_target,
            run_library_command,
        )

        library_argv = sys.argv[2:]
        if (
            not library_argv
            or library_argv[0] in LIBRARY_MANAGEMENT_COMMANDS
            or library_argv[0] in {"-h", "--help"}
        ):
            parser = create_library_parser()
            args = parser.parse_args(library_argv)
            try:
                exit_code = run_library_command(args)
            except KeyboardInterrupt:
                print("\nInterrupted.", file=sys.stderr)
                exit_code = 130
            raise SystemExit(exit_code)

        try:
            promplet_path, processor_args = parse_library_target(library_argv)
        except (FileNotFoundError, OSError, ValueError) as exc:
            print(f"weavemark library: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        sys.argv = [sys.argv[0], str(promplet_path), *processor_args]

    if any(
        argument in {"-h", "--help", "--scan", "--env", "--replay-run"}
        for argument in sys.argv[1:]
    ):
        # Informational, structural, and replay commands do not need a remote
        # pricing-map refresh. Live compilation retains LiteLLM's normal source.
        os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "true")

    from weavemark.app import cli as processor_cli

    processor_cli()


if __name__ == "__main__":
    cli()
