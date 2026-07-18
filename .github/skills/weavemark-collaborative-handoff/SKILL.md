---
name: weavemark-collaborative-handoff
description: |
  Run, test, debug, or automate WeaveMark collaborative/human-in-the-loop
  specs using non-interactive smoke mode, filesystem agent handoff, or direct
  engine APIs.
when_to_use: |
  - Running a spec with `@execute collaborative`
  - Testing or regenerating collaborative example outputs
  - Debugging collaborative edit rounds, traces, or runtime config
  - Acting as the editor/human collaborator for a WeaveMark run
  - Building future automation around collaborative WeaveMark workflows
---

# WeaveMark Collaborative Handoff

Use this skill when a task involves WeaveMark's collaborative engine: specs
that ask a human/editor/agent to review an LLM draft, edit it, and let the
engine continue. The goal is to make interactive cases reproducible for tests
and debuggable for agents without pretending that a real human is present.

## Mental model

Collaborative execution has three moving parts:

1. A composed WeaveMark result with named prompts, usually `generate` and
   `continue`.
2. A runtime config with `engine: collaborative` and `engine_config` such as
   `max_rounds`.
3. An edit callback. For automation, prefer either:
   - non-interactive smoke approval, or
   - `AgentHandoffEditCallback`, which creates request/response files for an
     external AI agent to fill in.

Important files:

- `src/weavemark/engines/collaborative.py`
- `examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py`
- `examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run-agent-handoff.sh`
- `promplets/catalog/executable/collaborative-*.weavemark.md`
- `tests/test_engines.py::TestCollaborativeEngine`

## Always start with the cheap path

Before involving a live editor or handoff loop, smoke-test the spec:

```bash
source ~/.zshenv 2>/dev/null || true
source ~/.zshrc 2>/dev/null || true

python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py \
  --spec promplets/catalog/executable/collaborative-investment-strategy.weavemark.md \
  --vars examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/inputs/vars.json \
  --output-dir examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/outputs \
  --non-interactive
```

This proves composition, source-declared engine dispatch, trace writing, and
artifact paths without requiring a live editing turn.

## Acting as the AI collaborator

Use agent handoff mode when the example or test should show a real edit turn:

```bash
source ~/.zshenv 2>/dev/null || true
source ~/.zshrc 2>/dev/null || true

python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py \
  --spec promplets/catalog/executable/collaborative-writer.weavemark.md \
  --vars examples/interactive-ui-and-handoff-demos/collaborative-writer/inputs/vars.json \
  --output-dir examples/interactive-ui-and-handoff-demos/collaborative-writer/outputs \
  --agent-collaborator
```

During execution the engine prints a block like:

```text
WEAVEMARK_AGENT_TURN_REQUEST
request_path=examples/interactive-ui-and-handoff-demos/.../outputs/agent-turns/turn-001-request.md
response_path=examples/interactive-ui-and-handoff-demos/.../outputs/agent-turns/turn-001-response.md
Write the complete edited document to response_path.
WEAVEMARK_AGENT_TURN_WAITING
```

When you see this:

1. Open the `request_path`.
2. Read the context and current draft.
3. Write the complete edited document to `response_path`.
4. Do not write a diff, commentary, or Markdown fence unless the requested
   document itself needs those.
5. To finish the collaboration, add a final line containing only `DONE`.
6. To approve unchanged, copy the draft exactly.
7. To abort intentionally, create an empty response file.

The response file is the public contract. Do not rely on hidden chat context;
the engine only reads the file.

## Direct engine/API pattern for tests and automation

For programmatic automation, inject `agent_handoff_dir` through
`RuntimeConfig.engine_config`. The collaborative engine materializes it into an
`AgentHandoffEditCallback`.

```python
from pathlib import Path

from weavemark.engines.base import RuntimeConfig

runtime_config = RuntimeConfig(
    engine="collaborative",
    engine_config={
        "max_rounds": 1,
        "agent_handoff_dir": str(Path("outputs/run/agent-turns")),
        "agent_handoff_timeout_seconds": 300,
        "agent_handoff_poll_seconds": 0.25,
        "agent_handoff_announce": True,
    },
)
```

Supported handoff keys:

- `agent_handoff_dir`: directory for `turn-NNN-request.md` and
  `turn-NNN-response.md`.
- `agent_handoff_timeout_seconds`: fail explicitly if no response appears.
- `agent_handoff_poll_seconds`: polling interval.
- `agent_handoff_label`: human-readable run label in request files.
- `agent_handoff_announce`: print machine-readable request blocks to stderr.
- `done_signal`: final line marker, default `DONE`.

Invalid values should raise explicit errors. Do not silence timeouts or replace
them with success-shaped defaults.

## Configuration pattern

Keep collaborative semantics in the promplet:

```weavemark
@execute collaborative
  max_rounds: 4
```

Keep run inputs in the example's JSON/YAML vars file. The Python runner creates
an in-memory runtime config only to inject the selected edit callback; it does
not load a sidecar config. Use an explicit `.runtime.json` or `.runtime.yaml`
only when a host genuinely needs provider policy or model routing overrides.

## Artifacts to inspect

Collaborative runs should save plain, inspectable files:

```text
examples/interactive-ui-and-handoff-demos/<example>/outputs/
  compiled-prompt.md
  execution-output.md
  execution-steps.json
  execution-trace.md
  agent-turns/
    turn-001-request.md
    turn-001-response.md
```

Inspect both the final output and trace. A passing exit code is not enough for
release examples: the edit turn should visibly improve or constrain the draft.

## Debugging checklist

1. Load API keys before live runs:
   `source ~/.zshenv 2>/dev/null || true; source ~/.zshrc 2>/dev/null || true`.
2. Run the non-interactive smoke path first.
3. Confirm `@execute collaborative` and sidecar `engine: collaborative` agree.
4. Confirm named prompts include the stages the strategy expects.
5. If the run waits, look for `WEAVEMARK_AGENT_TURN_REQUEST` on stderr and
   create the exact `response_path`.
6. If it times out, inspect `agent-turns/` before rerunning; stale response files
   are removed per turn, but stale requests can explain what happened.
7. Inspect `execution-steps.json` and `execution-trace.md` for leakage,
   missing edits, or an unchanged approval where a substantive edit was needed.
8. Run focused tests after engine changes:

```bash
python -m pytest tests/test_engines.py::TestCollaborativeEngine -q
```

## Release-example rules

- Shell `run*.sh` scripts under `examples/interactive-ui-and-handoff-demos/*/` must remain readable command
  transcripts. Do not add wrapper usage functions or argument parsing there.
- Put orchestration in `examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py` or library code,
  not in the shell transcript.
- Save outputs under each example's local `outputs/` folder.
- For agent-authored turns, make the edit concrete enough that future readers
  can see why collaborative execution is useful.
