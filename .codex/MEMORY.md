# Workflow Memory Spec

## Purpose
- This file is the top-level memory spec for the current workspace.
- Keep concrete round summaries out of this file; write them into daily memory files only.
- Treat `.codex/` as agent memory and internal guidance, never as product runtime state.

## Required Read Order
1. `AGENTS.md`
2. `.codex/SOUL.md`
3. `.codex/USER.md`
4. `.codex/MEMORY.md`
5. `.codex/memory/全局记忆总览.md`
6. `.codex/memory/YYYY-MM/记忆总览.md`
7. `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

## Directory Model
- Global overview: `.codex/memory/全局记忆总览.md`
- Monthly overview: `.codex/memory/YYYY-MM/记忆总览.md`
- Daily memory: `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

## Write Rules
- Every work round ends with one timestamped summary appended to the current daily memory file.
- Each daily entry should prefer a structured recall format: `topic`, `context`, `actions`, `decisions`, `validation`, `artifacts`, `next`.
- The current day's summary stays only in the daily file until the next day starts.
- The current month's overview stores only archived daily summaries up to yesterday.
- The global overview stores only archived monthly summaries for closed months.

## Daily Entry Detail Standard
- `topic`: what this round was mainly about.
- `context`: why the round happened, including the trigger or detected gap.
- `actions`: what was changed, created, migrated, or checked.
- `decisions`: rules or conclusions that affect later work.
- `validation`: commands, checks, and observed outcomes.
- `artifacts`: the most important files or directories touched.
- `next`: follow-up work, deferred checks, or rollover conditions.
- Keep entries concise but complete enough that a later reader can reconstruct the round without reopening a large number of unrelated files.

## Rollover Checks
- Day rollover: before the first round of a new day, verify yesterday's daily memory is summarized in the matching monthly overview.
- Month rollover: before the first round of a new month, verify the previous month's overview is summarized in the global overview.
- If a required overview entry is missing, archive it first and then continue normal work.

## Validation Commands
- `python scripts/manage_codex_memory.py status --root .`
- `python scripts/manage_codex_memory.py verify-rollups --root .`
- `python scripts/manage_codex_memory.py append --root . --summary "<round summary>"`
- `python scripts/manage_codex_memory.py append --root . --topic "<topic>" --context "<context>" --actions "<action1|action2>" --decisions "<decision1|decision2>" --validation "<check1|check2>"`
