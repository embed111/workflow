# PM当前版本计划

## 1. 文档定位
- 本文件是当前活跃版本的自动引用文件，不再单独承载当前版本的完整排期正文。
- 当前版本的完整计划统一维护在对应版本目录下的 `版本计划.md` 中。
- 当前版本的日级推进与现场更新统一维护在对应版本目录下的 `history/` 中。

## 2. 当前活跃版本
- active_version: `V13`
- active_version_title: `全仓逻辑边界与冗余实现根治`
- active_version_file: `pm/versions/V13/版本计划.md`
- version_history_root: `pm/versions/V13/history/`

## 3. 版本目录导航
- 全量版本目录、状态与路径索引统一看：`pm/PM版本目录导航.md`

## 4. 自动引用规则
1. 先读取本文件。
2. 再读取 `active_version_file` 指向的版本计划文件。
3. 再读取当前版本目录下的：
   - `需求台账.md`
   - `阶段看板.md`
   - `迭代甘特图.md`
4. 当前版本的具体需求点、责任人、进入前提、退出门槛，以该版本目录下的 `版本计划.md` 为准。
5. 当前版本的阶段、下一门禁、计划窗口和里程碑，以该版本目录下的 `需求台账.md / 阶段看板.md / 迭代甘特图.md` 为准。
6. 当前版本的日级推进、后移和排期判断，以该版本目录下的 `history/YYYY-MM/YYYY-MM-DD.md` 为准。
7. 当前活跃版本切换时，优先更新本文件中的：
   - `active_version`
   - `active_version_title`
   - `active_version_file`
   - `version_history_root`

## 5. 当前状态快照
1. snapshot_updated_at: `2026-05-08T20:50:17+08:00`
2. active 版本保持 `V13`
3. 当前版本标题为 `全仓逻辑边界与冗余实现根治`
4. 当前最高价值泳道为 `工程质量探测 / 架构优化 / 发布边界治理`
5. 生命周期阶段为 `active baseline=prod=20260504-041220；V13 的 R4/R5 已超时，当前继续处于治理恢复态；prod candidate 仍停在 20260504-012618，最近未形成更高 candidate；PM 主质量流水线 latest generated_at=2026-05-08T20:35:42+08:00 仍 fail(module_part_sprawl=warn(file_count=32))；workspace line budget 2026-05-08T20:35:18+08:00 pass；本轮已把 role_creation_message_runtime.py:12 / :354 / session_commands.py:699 三条旧 top debt 推出队列，并完成 pm-main@6dd23f9 / workflow_code@3bd69f3 本地根仓收口；当前 top debts 已切到 session_queries_and_internal_tasks.py:584 / training_workflow_execution_service.py:269 / pm_current_version_snapshot_refresh_support.py:0；isolated workflow gate session 20260508-170003-357 仍超出 wrapper window；/api/status 本轮仍 15 秒超时；切版判断继续由 version board readback 与 runtime-upgrade readback 回读 next_activation_ready=false`
6. baseline 已追到 live `prod=20260504-041220`；当前 `candidate=20260504-012618`，`candidate_is_newer=false / running_task_count=1 / can_upgrade=false / ghost_running_detected=false(count=0)`；`/api/schedules` 回读 `[持续迭代] workflow last_trigger_at=2026-05-08T20:08:00+08:00 / last_result_status=running / last_result_node_id=node-sti-20260508-ce995891 / next_trigger_at="" ; [持续迭代] novel_project_pm last_trigger_at=2026-05-08T19:50:00+08:00 / last_result_status=queued / last_result_node_id=node-sti-20260508-fc2878e0 / next_trigger_at=2026-05-09T06:35:00+08:00`；`/healthz ok=true @ 2026-05-08T20:42:06+08:00`
7. 当前版本判断: `version_transition_decision=stay / switch_blockers=governance recovery active; R4-R5 overdue; prod candidate stalled at 20260504-012618; isolated workflow gate session 20260508-170003-357 exceeded wrapper window; workflow gate last known still fails 12 probes; no newer candidate; verify_pm_version_board_view latest effective readback 仍为 next_activation_candidate="" / next_activation_ready=false / daily_governance_status=in_progress / mandatory_lane_guard_ready=true but summary still reports next version mandatory lanes missing; /api/status 本轮 15s timed out; V14 activation_readiness not_ready`
8. 当前发布边界真相：`root_sync_state=diverged_clean_patch_synced(本轮 role-creation 三债已相对本机 workflow_code 收口；developer workspace registry 仍停在上轮头部) / workspace_head=6dd23f9 / workflow_code_head=3bd69f3 / dirty_tracked_count=0(pm-main) / untracked_count=0(pm-main) / ahead_count=0(相对本轮已验证批次) / branch_status_pm_main=## main...origin/main [ahead 13, behind 3] / branch_status_workflow_code=## main...origin/main [ahead 446] / push_block_reason=workspace_and_code_root_diverged(commit history differs; content synced via supported git am pair)`
9. 当前治理约束：`本轮 role creation dialogue/batch/processing 三条参数面已通过 request-object 兼容层退出质量前三，并已完成 pm-main commit + workflow_code local git am 收口；/api/schedules 中 workflow launch_summary 仍残留开工前 ahead_dirty 快照，不作为当前 release boundary 真相；isolated workflow gate session 20260508-170003-357 仍超出 wrapper window，当前不能把 gate blocker 伪装成已通过；helper 现场仍以 workflow_devmate / workflow_bugmate ahead_dirty、workflow_testmate ahead、workflow_qualitymate diverged_or_unknown 为主，不适合把当前主债继续外派`
10. 当前恢复优先级：`先收口 session_queries_and_internal_tasks.py:584 -> training_workflow_execution_service.py:269 -> pm_current_version_snapshot_refresh_support.py:0 -> 再处理 isolated workflow gate session 20260508-170003-357 的 settle blocker 与 /api/status 超时 -> 复跑 workflow gate 与 PM quality pipeline -> 判断更高 candidate；若下一轮仍失败，则补 V13 version closeout AAR，并把版本判断改成 blocked 或 closeout_pending；next_push_batch=session_queries_and_internal_tasks request object -> training_workflow_execution waiting-context request object -> pm_current_version_snapshot_refresh_support split -> workflow gate rerun`
