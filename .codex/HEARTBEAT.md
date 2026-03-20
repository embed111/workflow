# Workflow Heartbeat

## Startup Read Order
1. `AGENTS.md`
2. `.codex/SOUL.md`
3. `.codex/USER.md`
4. `.codex/MEMORY.md`
5. `.codex/memory/全局记忆总览.md`
6. `.codex/memory/YYYY-MM/记忆总览.md`
7. `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

## Memory Cycle
- Write each round summary into `.codex/memory/YYYY-MM/YYYY-MM-DD.md` with a timestamp and structured recall fields.
- Keep today's summary in the daily file only until day rollover.
- Archive yesterday into `.codex/memory/YYYY-MM/记忆总览.md` on the first round after a day switch.
- Archive a closed month into `.codex/memory/全局记忆总览.md` on the first round after a month switch.

## Verification
- `python scripts/manage_codex_memory.py status --root .`
- `python scripts/manage_codex_memory.py verify-rollups --root .`
- Do not write product runtime data into `.codex/`.
- Keep evidence for reads, writes, and regression validation in the current workspace.
