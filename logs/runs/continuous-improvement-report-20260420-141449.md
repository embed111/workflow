# 连续改进报告 2026-04-20 14:14

## 判断
- 我继续保持 `V5`，当前仍处于 `开发实现 / 工程质量探测 / 发布边界收口`。
- `version_transition_decision=stay(V5)`；我现在不切版，因为 `V6` 仍只是 backlog 骨架，`prod/live member task` 的正向 `project_id/project_ref` 证据还没形成，`Mandatory Gate` 也还没转绿。
- 这轮我不重复上一轮的 `session_commands.py` 生命周期拆分，而是直接改打新的第三个 blocker `assignment_center_state_helpers.js`。

## 推进
- 我新增 `.repository/pm-main/src/workflow_app/web_client/assignment_center_graph_runtime.js`，把任务图排序、泳道计算、graph meta 和 graph render runtime 从 `assignment_center_state_helpers.js` 里抽到独立 bundle part，并把主文件压到 `481` 行。
- 我补上 `.repository/pm-main/scripts/acceptance/verify_assignment_center_graph_runtime_split.py`，再把它接进 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`，让 manifest 装配、函数迁移、单文件语法和整包语法都能被 dedicated probe 锁住。
- 我按 `test-session-manager` 跑过红灯 `.repository/pm-main/.test/20260420-140514-505/report.md`、绿灯 `.repository/pm-main/.test/20260420-141232-302/report.md`、现有 assignment 资产回归 `.repository/pm-main/.test/20260420-141232-329/report.md` 和最新 line budget `.repository/pm-main/.test/20260420-141232-323/report.md`，随后把代码收口到 `pm-main@619634c / workflow_code@619634c`。
- 最新 `line budget` 仍 fail-closed，但 `assignment_center_state_helpers.js` 已退出首批冻结对象，`blocking_offender_count` 也从 `9` 降到 `8`；新的第三个 blocker 已切换成 `src/workflow_app/server/services/role_creation_service_parts/session_queries_and_internal_tasks.py`。

## 证据
- 发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=619634c`
- 门禁报告：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- 当前 first batch targets：`schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/role_creation_service_parts/session_queries_and_internal_tasks.py`
- live 真相：`/healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status` 当前都可读；`running_task_count=1 / active_agent_count=1 / queued_task_count=2`，`candidate_version=current_version=20260419-180446 / can_upgrade=false / blocking_reason=running_tasks_present`
- `/api/schedules` 当前共有 `2` 条 enabled plan；`pm持续唤醒 - workflow 主线巡检` 的 `next_trigger_at=2026-04-20T14:20:00+08:00`，`[持续迭代] workflow` 仍是 enabled。当前 per-item `status` 字段为 `null`，所以这轮我不拿它硬推 ready/future 计数。
- helper 判断：当前没有 active helper task，也不需要给 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 做 create / restore / rerun / adjust；它们的 developer workspace 仍停在 `cec137`，相对 `code_root@619634c` 为 `diverged_or_unknown`，下一次若要并行，先 refresh 目标工作区。

## 下一动作
- 我下一刀优先继续压 `schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/role_creation_service_parts/session_queries_and_internal_tasks.py`，把 Mandatory Gate 再往下压。
- 等 `line budget / workflow gate / runtime release gate` 再往前走后，我再部署 `test`、刷新 `prod candidate`，并重跑 supported live member-route proof。

- preference_ref: state/user-preferences.md
- delta_observation: 这轮把 `assignment_center_state_helpers.js` 的 graph compare/lane/render runtime 抽成独立 bundle part 后，Mandatory Gate 的第三个 blocker 已从前端 state helper 切换成 `session_queries_and_internal_tasks.py`。
- delta_validation: 下一轮优先验证 `schedule_service.py / workflow_env_common.ps1 / session_queries_and_internal_tasks.py` 的拆分是否还能继续把 `blocking_offender_count` 往下压，并在 helper workspace refresh 后重评是否适合并行派发。
- memory_ref: `.codex/memory/2026-04/2026-04-20.md`
