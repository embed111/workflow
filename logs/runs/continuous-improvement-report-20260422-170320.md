# Continuous Improvement Report

- version_transition_decision: `stay(V8)`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `无代码待推；下一批先接 V8-R3 targeted regression，再补 V8-R2 / V8-R5 的剩余 contract/probe`
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`

## 判断

我继续保持 `stay(V8)`。这轮真正推进的是 `工程质量探测 + 发布推进`：我先在 `pm-main` 提交 `10289f4`，把 `assignment_cross_process_dispatch_claim` 的 gate 误伤从 `upgrade_drain_active` 里隔离出来，再用 parse-safe current-version judgment 跑通 `verify_pm_version_board_view.py` 和完整 `workflow gate`。随后我把 `test/current=candidate` 刷到 `20260422-165858`，再在 `8092` 用 exact `verify_api_catalog_live_regression.py` 把 `V8-R6` 的 live baseline 追平到当前版本。

## 本轮推进

- 代码修改：`pm-main@10289f4` 收掉 isolated dispatch claim probe 对 `prod` drain 的错误继承，让完整 gate 不再被不相关 probe 短路。
- 发布推进：`pm-main@10289f4` 与 `workflow_code@10289f4` 已 clean_synced，`test/current=candidate` 已刷新到 `20260422-165858`，`prod candidate` 也同步更新到同版本。
- live 结果：`/api/platform/interfaces/platform.interfaces.detail` 的 `latest_evidence.status=ready / compare.status=ready / baseline_version=20260422-165858`；`workflow` 项目的 `project_task_summary.interface_catalog_entry.status=ready`，`V8-R6` 已从 broad compare blocker 真推进成 `ready`。

## 版本更新

- `V8-R1=in_progress/90%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R2=in_progress/55%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R3=in_progress/80%/最近更新=2026-04-22T15:26:31+08:00/eta=2026-04-24/未超时`
- `V8-R4=completed/100%/最近更新=2026-04-22T12:45:44+08:00/eta=已完成/未超时`
- `V8-R5=in_progress/75%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-24/未超时`
- `V8-R6=completed/100%/最近更新=2026-04-22T17:00:39+08:00/eta=已完成/未超时`

## 切版判断

- `switch_blockers=V8-R2 / V8-R3 / V8-R5`
- `recheck_trigger=优先完成 V8-R3 targeted regression，并把 V8-R2 / V8-R5 的剩余 contract/probe 批次重新接进 gate 后再重检切版条件`
- `prod current=20260422-160549 / candidate=20260422-165858 / candidate_is_newer=true / drain_active=true / running_task_count=1 / blocking_reason=存在运行中任务，暂不可升级`

## 证据

- `python scripts/quality/check_workspace_line_budget.py --root .`
- `.repository/pm-main/.test/20260422-164147-985/report.md`
- `.repository/pm-main/.test/20260422-165216-175/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-165634.md`
- `.running/control/logs/test/deploy-20260422-165858.json`
- `.repository/pm-main/.test/20260422-170021-782/report.md`
- `.repository/pm-main/.test/20260422-170021-782/artifacts/api-catalog-live-regression/summary.json`

## Warnings

- `pm/daily-execution-history/2026-04-20.md` 仍缺失，`pm/daily-execution-history/2026-04-21.md` 与 `pm/daily-execution-history/2026-04-22.md` 仍未补齐。
- `pm/daily-learning-reports/2026-04-22/` 仍未补齐。
- `workflow_devmate` developer workspace 仍是 `ahead_dirty@52e2efb`。

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮我把 `V8-R6` 从“gate blocker + stale compare”推进成了 `test/current` 上的 live ready，但 `workflow_devmate ahead_dirty` 与当日 daily governance 缺口仍在。
- delta_validation: 下一轮优先消费 `V8-R3` targeted regression，并复查 `V8-R2 / V8-R5` 的下一批 gate；同时继续确认 `prod` 是否在空窗把 `20260422-165858` 接上。
