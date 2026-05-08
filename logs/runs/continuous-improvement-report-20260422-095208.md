# Continuous Improvement Report

## 判断

- `version_transition_decision=stay(V8)`。
- 这轮真正推进的是 `当前需求开发 + 发布推进`，不是再复述一次 helper 已经起跑。
- 我已经把 `V8-R1` 从 `workflow_devmate` 的 `ahead_dirty` 批次，推进到 `workflow_code@52e2efb`、`workflow gate` 通过、`test/prod candidate=20260422-094731` 刷新，以及 `8092` host lifecycle readback 转绿。

## 取舍

- 我没有继续新派 helper。live 真相已经切到 release-boundary 收口；这时再扩并行，只会把 V8 推进停在“报告做完了，主线没追上”的假进展里。
- `git push origin HEAD:main` 对本机 `workflow_code` 继续回 `Working directory has unstaged changes`，我没有把它记成“等下一轮再看”，而是直接改走受支持的根仓 `ff-only` 收口。
- `workflow gate` 第一次失败不是产品回退，而是我误用了被 live listener 占住的 `8098`；我换到空闲端口后继续跑，并把真正的 gate blocker 收窄到 `V8` 需求矩阵里的重复文档映射，再同轮修掉。

## 本轮推进

- `V8-R1`
  - `workflow_devmate` 代码批次已经提交为 `52e2efb`，并 fast-forward 收口进 `workflow_code`。
  - `project_registry_service.py` 通过拆出 `project_registry_lifecycle_actions.py`，从 `1117` 行压回 `986` 行。
  - line budget、focused probes、完整 `workflow gate`、`test` 部署和 `8092` host readback 已全部通过。
  - 当前进度更新为 `85% / updated=2026-04-22T09:47:43+08:00 / eta=2026-04-23 / overdue=no`。
- `V8-R5`
  - current baseline refresh 已完成，`prod/test` 的 project-ops latency sample 已冻结。
  - compare 仍 blocked，但 blocker 已收窄成一条 exact stale path：`api_catalog_live_regression` 还指向 `node-20260422-031749-7a93d8`，baseline 仍是 `20260422-020751`。
  - 当前进度更新为 `55% / updated=2026-04-22T09:20:28+08:00 / eta=2026-04-24 / overdue=no`。
- `V8-R3`
  - `workflow_ucdmate` 的 phase2 brief 已 handoff-ready。
  - 当前进度更新为 `50% / updated=2026-04-22T09:17:56+08:00 / eta=2026-04-24 / overdue=no`。
- 发布边界
  - `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=-`
  - `next_push_batch=无；下一批如果要处理 V8-R6 的 stale api_catalog_live_regression path，再切新的 exact-fix code batch`
  - `pm-main` 已 refresh 到 `52e2efb`；`workflow_devmate` 也已 `clean_synced@52e2efb`
  - `workflow_bugmate / workflow_qualitymate / workflow_testmate / workflow_ucdmate` 仍停在 `185ccce`；当前是“落后但不脏”，不算这轮 release-boundary blocker

## 证据

- code batch
  - `workflow_devmate commit=52e2efb`
  - `workflow_code HEAD=52e2efb`
- tests
  - line budget session: `.repository/workflow_devmate/.test/20260422-093347-999`
  - focused probes session: `.repository/workflow_devmate/.test/20260422-093356-154`
  - active version matrix fast-check: `.repository/workflow_devmate/.test/20260422-094242-893`
  - full gate pass session: `.repository/workflow_devmate/.test/20260422-094251-414`
  - full gate report: `.repository/workflow_devmate/.test/runs/workflow-gate-acceptance-20260422-094650.md`
- deploy
  - test deploy report: `.running/control/logs/test/deploy-20260422-094731.json`
  - `8090 /api/runtime-upgrade/status`：`current=20260422-065617 / candidate=20260422-094731 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`
- host readback
  - `8092` lifecycle smoke 已确认：`bootstrap -> next_handoff_interval=42 -> archive -> active list hide -> archived list show -> dashboard hide -> recover -> active list show -> dashboard show -> delete cleanup`
- developer workspace truth
  - `8090 /api/config/developer-workspaces` 已回读 `pm-main=clean_synced@52e2efb`
  - `8090 /api/config/developer-workspaces` 已回读 `workflow_devmate=clean_synced@52e2efb`

## 当前版本状态

- `V8-R1=in_progress / 85% / updated=2026-04-22T09:47:43+08:00 / eta=2026-04-23 / overdue=no`
- `V8-R2=in_progress / 55% / updated=2026-04-22T08:48:30+08:00 / eta=2026-04-23 / overdue=no`
- `V8-R3=in_progress / 50% / updated=2026-04-22T09:17:56+08:00 / eta=2026-04-24 / overdue=no`
- `V8-R4=in_progress / 98% / updated=2026-04-22T09:47:43+08:00 / eta=2026-04-23 / overdue=no`
- `V8-R5=in_progress / 55% / updated=2026-04-22T09:20:28+08:00 / eta=2026-04-24 / overdue=no`
- `V8-R6=planned / 15% / updated=2026-04-22T09:20:28+08:00 / eta=2026-04-24 / overdue=no`
- 本轮没有需求超时，所以没有新增 AAR。

## 下一步

- 下一刀先对准 `V8-R6` 的 exact stale path：把 `api_catalog_live_regression` 从旧 artifact `node-20260422-031749-7a93d8` / baseline `20260422-020751` 追到新的 `20260422-094731`。
- `prod` 仍是 `running_task_count=1`，当前只是 `candidate newer pending idle window`，不是立即可升级窗口；下一轮继续看 idle watcher 是否自动 apply `20260422-094731`。
- 如果我要继续给 `workflow_bugmate / workflow_qualitymate / workflow_testmate / workflow_ucdmate` 派代码任务，先把这些 developer workspace refresh 到最新根仓。
- `pm/daily-execution-history/2026-04-20.md`、`2026-04-21.md`、`2026-04-22.md` 与 `pm/daily-learning-reports/2026-04-22/` 仍未补齐；这轮继续保留 warning，不伪造 daily 完成态。

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮最值钱的动作不是再派新 helper，而是把 `V8-R1` 从“helper 成功但 boundary 还开着”，推进到“workflow_code 已追平、gate 已通过、test/candidate 已刷新、host readback 已拿到”。
- delta_validation: 下一轮直接检查 `8090 /api/runtime-upgrade/status` 是否从 `candidate_newer_pending_idle_window` 往正式 apply 继续推进，同时切出 `V8-R6` 的 exact stale-compare 修复批次。
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`
