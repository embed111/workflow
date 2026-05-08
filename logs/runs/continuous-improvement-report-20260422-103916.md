# Continuous Improvement Report

## 判断

- `version_transition_decision=stay(V8)`。
- 这轮真正推进的是 `当前需求开发 + 发布推进 + 版本执行约束调整`。
- 我没有重复上一轮的 `R1` 收口；这轮直接修了 `V8-R6` 的 stale ready projection，把 `V9` 补成合格的 planned 版本，并把修复送进 `candidate=20260422-103706`。

## 取舍

- 我保留了旧 `api_catalog_live_regression` artifact 在 `compare` 里的 stale blocker 角色，但不再允许它继续被 `latest_evidence / project summary` 误投成 ready。
- 我没有继续新派 helper；当前更高价值的是直接在 `pm-main` 把 `R6` stale path 和 `V9` mandatory-lane blocker 一次收掉，再推进发布链。
- `git push origin main` 对 checked-out 的本机 `workflow_code` 仍不稳，我改走受支持的 `fetch + ff-only merge` 收口，不把根仓保护当成延后提交的理由。

## 本轮推进

- 代码批次已经提交为 `dc8ed9c fix(api-catalog): 过滤 stale live artifact 的 ready 投影`，并同步到本机 `workflow_code@dc8ed9c`。
- `platform_interface_catalog_self_readback_runtime.py` 现在只把 version-matched live artifact 投到 `latest_evidence`；旧 artifact 只保留在 `compare.stale_per_probe_results` 里。
- `verify_api_catalog_self_readback_closure.py` 已补成红绿灯：stale fixture 必须退成 `partial`，refresh fixture 仍能回到 `ready`。
- `verify_assignment_role_contract_runtime.py` 的 fixture 已追平到新合同，role-contract runtime 仍保持 `ready`。
- line budget、`verify_api_catalog_self_readback_closure.py`、`verify_assignment_role_contract_runtime.py`、`verify_pm_version_board_view.py`、`verify_planned_version_activation_readiness.py` 和完整 `workflow gate@8101` 已全部通过。
- 发布边界当前为：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=-`。
- `pm-main=clean_synced@dc8ed9c`，`workflow_code=clean_synced@dc8ed9c`；`next_push_batch=无代码待推；下一批若继续推进 V8-R6，就切 current-baseline live regression evidence 或 coverage batch。`
- 我已刷新出 `test=current=candidate=20260422-103706`。`8092 /api/platform/interfaces/platform.interfaces.detail` 现在显示：
  - `latest_evidence.status=partial`
  - `compare.status=blocked`
  - 旧 live artifact 不再出现在 `latest_evidence.report_refs`
- `8092 /api/status.project_task_summary.interface_catalog_entry.status=partial`，不再把旧 live artifact 当成最近 ready 证据。
- `prod` 仍是 `current=20260422-094731 / candidate=20260422-103706 / candidate_is_newer=true / drain_active=true / running_task_count=4`，当前在等 idle watcher 空窗升级。
- `V9` 现在已经补齐最低配置泳道和 `V10` 前置排期，不再是自动初始化骨架。

## 当前版本状态

- `V8-R1=in_progress / 90% / updated=2026-04-22T10:39:16+08:00 / eta=2026-04-23 / overdue=no`
- `V8-R2=in_progress / 55% / updated=2026-04-22T08:48:30+08:00 / eta=2026-04-23 / overdue=no`
- `V8-R3=in_progress / 50% / updated=2026-04-22T09:17:56+08:00 / eta=2026-04-24 / overdue=no`
- `V8-R4=completed / 100% / updated=2026-04-22T10:30:53+08:00 / eta=已完成 / overdue=no`
- `V8-R5=in_progress / 70% / updated=2026-04-22T10:39:16+08:00 / eta=2026-04-24 / overdue=no`
- `V8-R6=in_progress / 45% / updated=2026-04-22T10:39:16+08:00 / eta=2026-04-24 / overdue=no`
- 本轮没有需求超时，所以没有新增 AAR。

## 下一步

- 我下一步先等 `prod candidate=20260422-103706` 的 idle watcher 空窗升级；如果 `candidate_newer_pending_idle_window` 挂太久，我就按升级读链继续查 drain/window 真相。
- 如果下一轮继续推进 `V8-R6`，我会优先决定是补一条与 `103706` 对齐的 live regression 证据，还是直接切 coverage batch；这两条不再和别的 defect 修复混批。
- `pm/daily-execution-history/2026-04-20.md`、`2026-04-21.md`、`2026-04-22.md` 与 `pm/daily-learning-reports/2026-04-22/` 仍未补齐；这轮继续保留 warning，不伪造 daily 完成态。
- `memory_ref=.codex/memory/2026-04/2026-04-22.md`
