# Workflow Tools

## Preferred Local Commands
- `.\run_workflow.bat`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/launch_workflow.ps1 -OpenBrowser`
- `python scripts/workflow_web_server.py --host 127.0.0.1 --port 8090`
- `python scripts/workflow_entry_cli.py --mode status`
- `python scripts/workflow_entry_cli.py --mode backfill`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`

## Memory and Skill Conventions
- `.codex/*` stores agent memory and internal workspace guidance.
- `.codex/skills/` is the local skill entry expected by existing docs and code.
- `state/*` remains product runtime state; `logs/*` remains audit and execution evidence.
