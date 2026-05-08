# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`。
- 本轮主推进明确记成 `工程质量探测 / 发布边界收口 / V5-R5`；我新增了 `schedule_projection_runtime.py`，把 schedule 的 list/detail/calendar/read-side projection 从 `schedule_query_runtime.py` 正式拆出来。
- 这刀之后，`schedule_query_runtime.py` 已从 `1278` 行降到 `799` 行，并退出 Mandatory Gate offender 列表；但 `V6` 仍不切入，`next_activation_candidate=- / next_activation_ready=false`。

## 取舍
- 我没有顺着当前更脏的工作区继续叠新功能面。`pm-main` 这轮已经扩张到 `dirty_tracked_count=13 / untracked_count=9`，而且同时混着 `V5-R4` 首刀、`V5-R5` gate split 和 `V6 bootstrap`；这种现场不能硬推 `commit/push`。
- 我也没有重复上一轮“query/projection 第三刀”的同一路径，而是继续按职责边界往前做，把“底层查询/enrich”和“读面投影/公开读取入口”正式分层，避免新模块继续无限长大。
- 当前更高价值的不是再开一条 helper 编码切片，而是先把 mixed batch 切净，再决定给第二项目受控试运营争取第一条 clean push，还是继续拆 `schedule_service.py` 的首批冻结对象。

## 下一动作
- 先切开当前 mixed batch，把 `V5-R4` 首刀、`V5-R5` schedule split 和 `V6 bootstrap` 分离成可独立收口的小批次。
- 如果能形成第二项目受控试运营所需的第一条 clean push，我优先走 `V5-R4`；如果仍被首批冻结对象卡住，我就继续拆 `schedule_service.py`，而不是再把债平移到新文件上。
- 在 `Mandatory Gate` 没转绿之前，我不会把“本地已拆好”误说成“发布边界已收口”。

## 本轮推进
- 新增 `.repository/pm-main/src/workflow_app/server/services/schedule_projection_runtime.py`，承接 `_build_schedule_items / _build_schedule_list_items / _build_schedule_preview_items` 和 `list_schedule_preview / list_schedules / get_schedule_detail / get_schedule_calendar`。
- 更新 `.repository/pm-main/src/workflow_app/server/services/schedule_query_runtime.py`，把它退回到底层查询、文本修复和 trigger enrich 职责。
- 更新 `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`，让 service 改走新的 projection/runtime 绑定。
- `line budget` 最新结果仍为 fail-closed，但门禁真相已推进：`blocking_offender_count=39`，比上一拍的 `40` 少 `1`；`schedule_query_runtime.py` 已不再是 offender，`schedule_projection_runtime.py=522 / schedule_rule_runtime.py=426 / schedule_status_runtime.py=449` 都在阈值内。
- 当前仍未完成 `commit / push / 根仓同步`。阻塞原因不是“没做完功能”，而是 `workspace_dirty_expanded + mandatory_gate_fail_closed + mixed_batch_pending(V5-R4 + V5-R5 + next_version_bootstrap)`。

## 当前版本更新
- `V5-R1 = in_progress / 35% / 最近更新=2026-04-19T21:11:12+08:00 / eta=2026-04-21 / 未超时`
- `V5-R2 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R3 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R4 = in_progress / 88% / 最近更新=2026-04-19T21:36:58+08:00 / eta=2026-04-21 / 未超时`
- `V5-R5 = in_progress / 60% / 最近更新=2026-04-19T21:41:32+08:00 / eta=2026-04-20 / 未超时`
- 本轮无超时需求，不新增 AAR。
- 当前发布边界：`root_sync_state=ahead_dirty / ahead_count=0 / dirty_tracked_count=13 / untracked_count=9`
- `push_block_reason=workspace_dirty_expanded + mandatory_gate_fail_closed + mixed_batch_pending(V5-R4 + V5-R5 + next_version_bootstrap)`
- `next_push_batch=先切开当前 mixed batch，优先把 V5-R4 首刀和 V5-R5 schedule split 分离成可独立收口的小批次，再决定 clean push 还是继续拆首批冻结对象`
- live 当前是 `running_task_count=1 / queued_task_count=1 / active_agent_count=1`；`prod=current_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / ghost_running_detected=false`，主线连续性成立。

## 证据
- `.repository/pm-main/.test/20260419-213910-194/report.md`
- `.repository/pm-main/.test/20260419-213920-500/report.md`
- `.repository/pm-main/.test/20260419-213929-439/report.md`
- `.repository/pm-main/.test/20260419-213937-100/report.md`
- `.repository/pm-main/.test/20260419-213950-081/report.md`
- `.repository/pm-main/.test/20260419-213957-548/report.md`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `preference_ref: state/user-preferences.md`
- `memory_ref: .codex/memory/2026-04/2026-04-19.md`
