# 持续迭代报告

## 判断
- `version_transition_decision=stay(V5)`。当前更高价值的仍是 `工程质量探测 / 发布边界收口`，不是重复 prod live member-route proof，也不是切到 `V6`。
- 我这轮完成的推进性修改是把 `graph_model_and_payloads.py` 里的节点显示修复、workflow 主线/保底识别和 schedule goal live refresh 抽成 `assignment_node_surface_runtime.py`，并补了 dedicated split probe。`graph_model_and_payloads.py` 已从 `1429` 行降到 `1223` 行，退出当前 `Mandatory Gate` 首批冻结对象。
- 当前下一刀改成 `schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/assignment_service_parts/task_artifact_store_queries.py`。等 `line budget / workflow gate / runtime release gate` 再往前推进后，我再刷新 `test/prod candidate`，然后重跑同一条 supported live member-route proof。

## 取舍
- 这轮我没有重复上一轮的 `role creation planning split`，也没有再做一轮同质化 live API 试探；因为当前 prod `20260419-180446` 还没带上正向 `project_id/project_ref` 证据，继续重复 live proof 只会空转。
- 我也判断当前不新建 helper 主线任务：`parallel_candidate_count=1 / parallel_dispatched_count=0 / active_helper_tasks=-`。原因是这一刀仍是 `pm-main` 本地 Mandatory Gate blocker 的紧耦合收口，我先把已验证小批次 commit 并同步回本机根仓，再按新的 `schedule/env/query` 首批冻结对象重切 helper 批次更稳。

## 结果
- 代码修改：
  - 新增 `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/assignment_node_surface_runtime.py`
  - 新增 `.repository/pm-main/scripts/acceptance/verify_assignment_graph_node_surface_split.py`
  - 更新 `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/graph_model_and_payloads.py`
  - 更新 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`
- 验证结果：
  - split probe：`.repository/pm-main/.test/20260420-042426-763/report.md`
  - `py_compile`：`.repository/pm-main/.test/20260420-042436-687/report.md`
  - line budget：`.repository/pm-main/.test/20260420-042544-757/report.md`
- 发布边界：
  - `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
  - `workspace_head=code_root_head=2263472`
  - `push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/assignment_service_parts/task_artifact_store_queries.py split + gate/acceptance`
  - `pm-main@2263472` 已通过受支持的 `../workflow_code fetch pm-main + ff-only merge` 收口到本机根仓；直接 `git push origin main` 仍被 local root 的 working-tree 保护拒绝，我没有把这批已验证改动留成本地滞留。
- line budget 真相：
  - `blocking_offender_count=33`，仍是 fail-closed
  - 当前 `first_batch_targets` 已切换为 `schedule_service.py / workflow_env_common.ps1 / task_artifact_store_queries.py`
  - `graph_model_and_payloads.py` 仍是 refactor-trigger offender，但已经退出首批冻结对象
- live 真相：
  - `/healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status` 当前可用
  - `running_task_count=1 / queued_task_count=2 / active_agent_count=1`
  - `candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false`
  - 当前不是空窗，不需要兜底补链

## 需求更新
- `V5-R1`: `in_progress / 60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
- `V5-R2`: `in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R3`: `in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R4`: `in_progress / 96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
- `V5-R5`: `in_progress / 97% / 最近更新=2026-04-20T04:28:58+08:00 / eta=2026-04-21 / 未超时`
- 今天仍未补 `pm/daily-execution-history/2026-04-20.md`，因为每日学习任务与真实学习报告还没收口；我这轮继续明确记录原因，不伪造 completed 记录。

## 下一动作
- 继续正面打 `schedule_service.py / workflow_env_common.ps1 / task_artifact_store_queries.py` 这三块 Mandatory Gate blocker。
- 等当前 clean head 的 `line budget / workflow gate / runtime release gate` 再往前推进后，部署 `test`、刷新 `prod candidate`，再重跑 supported live member-route proof。
- `memory_ref: .codex/memory/2026-04/2026-04-20.md`
