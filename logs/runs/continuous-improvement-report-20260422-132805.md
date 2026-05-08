# Continuous Improvement Report 2026-04-22 13:28 +08:00

- preference_ref: `state/user-preferences.md`
- delta_observation: `/api/assignments/.../status-detail.selected_node` 在 live running node 上只给节点收据，不给当前 `run_id / started_at / prompt/stdout/stderr refs`；同时 `workflow_testmate` 已把 `V8-R6` 缩成单条 stale live regression path，可以直接挂下一刀 helper，而不是继续 broad 观察。
- delta_validation: 待 `prod` 空窗升到 `20260422-132411` 后，先复核 live `selected_node` 的 run 投影，再消费 `workflow_devmate node-20260422-132645-f52731` 的 exact rebind fix。

## 判断

- `version_transition_decision=stay(V8)`
- 本轮推进类别：`工程质量探测 + 发布推进`
- 我把 `/api/assignments/.../status-detail.selected_node` 的当前 run 投影补进 `pm-main/workflow_code@673caaf`，并用 `verify_assignment_status_detail_default_node.py + workflow gate` 锁住；新版本已部署到 `test/current=candidate=20260422-132411`。
- `workflow_testmate node-20260422-124330-ee9d8f / arun-20260422-130950-3292bf` 已把 `V8-R6` 缩成单条 stale live regression path：`C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260422-031749-7a93d8/output/v6-r2-interface-center-live-regression.md`（baseline `20260422-020751`）。
- 我没有把这条 blocker 留给下一轮口头接力，而是新建 `workflow_devmate node-20260422-132645-f52731` 作为 exact rebind fix；当前因为 `prod current=20260422-124101 / candidate=20260422-132411 / drain_active=true`，它正常冻结在 `ready`。

## 取舍

- 当前不切版：`V8-R2 / V8-R3 / V8-R5 / V8-R6` 仍未完成，`next_activation_candidate=V9 / next_activation_ready=false`。
- 我这轮没有再开新的 broad perf 或 broad UI 切片，而是先修当前 workboard/status-detail 读面，再把 `V8-R6` 的 blocker 压成“单条 stale path + 单条 rebind next slice”。
- `workflow_devmate` 的 developer workspace 仍是 `ahead_dirty`，所以这轮代码直接在 `pm-main` 收口；helper 侧只保留 runtime task，不硬改它的脏工作树。

## 下一动作

- 等 `prod` 空窗把 `candidate=20260422-132411` 接上后，优先消费 `workflow_devmate node-20260422-132645-f52731` 的 rebind fix。
- 升级后第一拍复核两件事：
  1. `status-detail.selected_node` 在 live running node 上能直接回读 `run_id / started_at / prompt/stdout/stderr refs`
  2. `8092` 这轮 fresh `summary.json` 是否已替换旧 stale live regression path
- 如果 `running_task_count` 清零后 `prod` 仍不升，我就继续顺着 `/api/runtime-upgrade/status` 和 watcher 读链查 `drain/window`，不把它滚成口头 blocker。

## 证据

- 发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=-`
- 代码批次：`pm-main/workflow_code@673caaf`
- 验证：
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - `.repository/pm-main/.test/20260422-131814-625/report.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-132224.md`
  - `.running/control/logs/test/deploy-20260422-132411.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260422-124330-ee9d8f/output/v8-r6-current-baseline-live-regression.md`
- 受控 warning：
  - `pm/daily-execution-history/2026-04-20.md` 仍缺失
  - `pm/daily-execution-history/2026-04-21.md` 与 `pm/daily-execution-history/2026-04-22.md` 仍未补齐
  - `pm/daily-learning-reports/2026-04-22/` 仍未补齐
  - `workflow_devmate` developer workspace 仍是 `ahead_dirty`
- `memory_ref=.codex/memory/2026-04/2026-04-22.md`
