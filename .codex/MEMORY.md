# Workflow Long-Term Memory

## Stable Workspace Facts
- This workspace keeps product runtime state in `state/` and operational evidence in `logs/`.
- The OpenClaw memory layer lives under `.codex/` and is separate from product runtime state.
- Local skills, when present, belong under `.codex/skills/*/SKILL.md`.

## Current Governance Baseline
- `AGENTS.md` remains the top-level governance entry for the workspace.
- Startup memory recovery reads `.codex/SOUL.md`, `.codex/USER.md`, and the latest daily memory files.
- Main-session recovery may additionally read this file for longer-lived context.
