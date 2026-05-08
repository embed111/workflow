# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`。
- 本轮主推进明确记成 `工程质量探测 / V5-R5`；我完成了 `schedule query/projection` 第三刀，不再只是重复上一拍的 status/query 拆分。
- 当前不切 `V6`。`next_activation_candidate=- / next_activation_ready=false`；阻塞点仍是 `V5-R4` 的 `project_id/project_ref` 首个代码批次尚未开始、controller cadence closure 与 member route 未收口，以及 `V5-R5` 的 `Mandatory Gate` 仍为 false。

## 取舍
- 我没有在 `pm-main` 当前 `ahead_dirty + mixed_batch_pending(V5-R5 + V6 bootstrap/PM治理)` 的脏批次上继续叠加 `V5-R4` 产品实现，而是先把 `schedule_service.py` 的 row/trigger/projection 真逻辑迁到 `schedule_query_runtime.py`，继续缩当前冻结对象。
- 迁移后我没有把测试回归炸点留到下一轮：`verify_schedule_live_result_summary.py` 首次失败后，我继续把 `schedule_query_runtime.py` 对 `_assignment_runtime_status*` 的访问改回 runtime-symbol 透传，避免 monkeypatch / live hook 在新模块里失效。
- 我同时消费了 `workflow_devmate` 回传的 `v5-r4-project-graph-field-impl-brief.md`。这让 `V5-R4` 不再停在“等 brief”，而是已经冻结出 `project_id/project_ref` 的 first write set、surface read path 和最小 acceptance probe。

## 本轮推进
- `schedule_service.py` 从 `2652` 行降到 `2381` 行；`schedule_query_runtime.py` 升到 `1278` 行。结构上前进了，但 `Mandatory Gate` 仍未转绿，而且 `blocking_offender_count` 从 `39` 回到 `40`，说明这刀把一部分债移动到了新模块，不能误报成发布边界好转。
- 定向回归已转绿：
- `.repository/pm-main/.test/20260419-211025-324/report.md`
- 其中覆盖了 `py_compile`、`verify_dashboard_schedule_preview.py`、`verify_schedule_live_result_summary.py`、`verify_schedule_runtime_status_file_fast_path.py`
- line budget 仍为红灯：
- `.repository/pm-main/.test/20260419-211038-055/report.md`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- `workflow_devmate` 的 `V5-R4` brief 已在 `2026-04-19T21:04:37+08:00` 完成交付：
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-20260419-203657-267dd1.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260419-203758-31c3a6/result.json`

## 当前版本更新
- `V5-R1 = in_progress / 35% / 最近更新=2026-04-19T21:11:12+08:00 / eta=2026-04-21 / 未超时`
- `V5-R2 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R3 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R4 = in_progress / 82% / 最近更新=2026-04-19T21:04:37+08:00 / eta=2026-04-21 / 未超时`
- `V5-R5 = in_progress / 55% / 最近更新=2026-04-19T21:10:47+08:00 / eta=2026-04-20 / 未超时`
- 本轮无超时需求，不新增 AAR。
- 当前发布边界：`root_sync_state=ahead_dirty / ahead_count=0 / dirty_tracked_count=5 / untracked_count=7`
- `push_block_reason=workspace_dirty + mandatory_gate_fail_closed + mixed_batch_pending(V5-R5 + next_version_bootstrap)`
- `next_push_batch=先切开 V5-R5 runtime/query split 批次与 V6 bootstrap/PM治理批次，再决定是否按 brief 打开 V5-R4 独立实现批次`
- live 当前是 `running_task_count=1 / queued_task_count=2 / active_agent_count=1`；主线 `node-sti-20260419-57294838` 正在 running，下一条 mainline `node-sti-20260419-b6b1e1f4` 和 patrol `node-sti-20260419-27dc6ad5` 都已经 ready，连续性成立。
- helper 当前不需要 create / restore / rerun / adjust；`workflow_devmate` 的 brief 已交付，当前 `active_helper_tasks=-`。

## 下一动作
- 先切干净当前 mixed batch，不再让 `V5-R5` 治理批次和 `V6 bootstrap/PM治理` 继续混写。
- 切批完成后，在两条路之间二选一，不再空转：
- 按 brief 打开 `V5-R4` 的 `project_id/project_ref` 独立实现批次。
- 或继续拆 `schedule_query_runtime.py`，把这轮新暴露出来的 blocker 先压回去。
- 在 `Mandatory Gate` 没转绿之前，我不会把这轮 helper brief 回流误说成发布边界已经收口。

## 证据
- live health/status：
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- preference_ref: `state/user-preferences.md`
- delta_observation: 迁移 schedule query/projection 真逻辑时，如果新 runtime 模块直接抓静态 alias，现有 monkeypatch/live hook 会失效；必须继续经由 runtime symbol 透传。
- delta_validation: 下一轮若继续拆 `schedule_*_runtime.py`，先跑 `verify_schedule_live_result_summary.py`，再判断是否继续扩拆范围。
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`
