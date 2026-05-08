# continuous-improvement-report-20260416-084017

- generated_at: `2026-04-16T08:40:17+08:00`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-16.md`
- active_version: `V3`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260416-e2139ae0`

## Delta

- delta_observation: developer workspace registry 在跨机器/跨工作根后会遗留旧 `workspace_path`；如果只继续 refresh 当前 canonical workspace，读链仍可能沿旧路径把 helper 算成 `diverged_or_unknown`。
- delta_validation: 已通过 `verify_developer_workspace_registry_reconcile.py` 固化 canonical path reconcile，并用完整 `workflow gate`、`test` 部署和 live `/api/config/developer-workspaces` 复核它没有回退。

## Summary

- 我补了 `developer_workspace_service.py` 的 canonical workspace path reconcile，并更新 `verify_developer_workspace_registry_reconcile.py` fixture 锁住“旧路径在 scope 外、当前 canonical workspace 在 scope 内”这类现场。
- 我串行跑过 `verify_developer_workspace_registry_reconcile.py` 与 `verify_assignment_terminal_result_recovery_without_finalize.py`，随后提交 `7772220 fix(workspace): 自动收口helper旧路径registry漂移`，并通过本机 `../workflow_code` 的 `fetch + ff-only merge` 完成根仓收口。
- 我用新的读链重扫 `state/developer-workspaces.json`，把旧 `C:/work/...` helper registry 回落到当前 `D:/code/.../.repository/<developer_id>`，再把五个 helper 全量 refresh 到 `7772220`。
- 我修平 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 学习报告缺失字段，以及 `PM当前版本计划.md` 的 baseline 句式，完整 `workflow gate` 已在 `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260416-083503.md` 通过。
- 我停掉旧 `test` 后重发部署，把 `test` 刷到 `20260416-083609`，新的 `prod candidate=20260416-083609` 已生成；当前 `prod` 仍为 `20260416-080120`，并处于 `candidate_newer_pending_idle_window` drain。

## Boundary

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=7772220`
- `push_block_reason=-`
- `next_push_batch=当前无待推代码批次；下一执行批次改为等待 prod idle watcher 在空窗切到 20260416-083609，再由 workflow_testmate 补 current-version smoke`
