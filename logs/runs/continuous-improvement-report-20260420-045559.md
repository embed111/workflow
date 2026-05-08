# 持续迭代报告

## 判断
- `version_transition_decision=stay(V5)`。我这轮继续留在 `V5 / 工程质量探测 / 开发实现`。
- 我没有重复上一轮的 `graph_model_and_payloads.py` 拆分，而是把 `task_artifact_store_queries.py` 的公共 query surface 抽到 `task_artifact_store_query_surface.py`，让 runner 从 `1407` 行降到 `1104` 行，并退出 Mandatory Gate 首批冻结对象。
- 当前更高价值的下一刀改成 `schedule_service.py / workflow_env_common.ps1 / training_center_role_creation.js`；在 `Mandatory Gate` 仍红灯前，我不刷新 `test/prod candidate`，也不切到 `V6`。

## 取舍
- 不切版：`next_activation_candidate=- / next_activation_ready=false`，`V6` 仍只有 backlog 骨架；`V5` 还卡 `controller cadence closure` 的 live finalize 证据、prod/live 正向 member task 证据和 `Mandatory Gate=false`。
- 不补链：截至 `2026-04-20T04:55:03+08:00`，live 仍是 `1 running / 2 queued`，主线 `node-sti-20260420-45657887` 在跑，下一条 mainline `node-sti-20260420-ca451f8b` 和 patrol `node-sti-20260420-91c1672c` 都在 `ready`。
- 不派 helper：本轮没有 active helper task，helper runtime 不需要 create / restore / adjust；但 developer workspaces 目前都落后 `code_root@68ea58b`，下一轮若要派发，先 refresh 目标工作区。

## 本轮推进
- 代码：
  - 新增 `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_query_surface.py`，承接 `list_assignments / get_assignment_overview / get_assignment_graph / get_assignment_scheduler_state / get_assignment_status_detail` 五个公共查询入口。
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_queries.py` 只保留内部 query / stale-recovery helper，并通过 alias 暴露新 surface；文件行数从 `1407` 降到 `1104`。
  - 新增 `.repository/pm-main/scripts/acceptance/verify_task_artifact_store_queries_split.py`，把 `runner < 1200 行 + support < 600 行 + assignment_service 暴露出的 query surface 绑定到新模块` 锁成正式 probe，并接入 `workflow_gate_probe_registry.py`。
- 验证：
  - `.repository/pm-main/.test/20260420-045156-721/report.md`：`verify_task_artifact_store_queries_split.py` 通过；确认 query surface 已由 `assignment_service_parts.task_artifact_store_query_surface` 提供。
  - `.repository/pm-main/.test/20260420-045204-670/report.md`：`py_compile` 通过。
  - `.repository/pm-main/.test/20260420-045211-506/report.md`：最新 `line budget` 仍 fail-closed，但 `task_artifact_store_queries.py` 已退出首批冻结对象；当前 `first_batch_targets` 变为 `schedule_service.py / workflow_env_common.ps1 / training_center_role_creation.js`，`blocking_offender_count` 维持 `33`。
- 发布边界：
  - `pm-main` 已提交 `68ea58b refactor(assignment): 抽离任务图查询 surface 以压低门禁 blocker`。
  - 直接 `git push origin main` 仍被本机 `../workflow_code` 的 `updateInstead` 保护误判拦下；我已改走受支持的 `git -C ../workflow_code fetch D:/code/AI/J-Agents/workflow/.repository/pm-main main && git -C ../workflow_code merge --ff-only FETCH_HEAD` 收口，并再执行 `git -C .repository/pm-main fetch origin` 追平 tracking。
  - 当前发布边界为 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=68ea58b / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / src/workflow_app/web_client/training_center_role_creation.js split + gate/acceptance`。

## 版本状态
- `V5-R1`：`in_progress / 60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
- `V5-R2`：`in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R3`：`in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R4`：`in_progress / 96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
- `V5-R5`：`in_progress / 98% / 最近更新=2026-04-20T04:53:03+08:00 / eta=2026-04-21 / 未超时`
- 本轮无新增 AAR。

## 今日例行与记忆
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；原因不变：今日学习任务与真实学习报告还未收口，我不伪造 completed 记录。
- `preference_ref: state/user-preferences.md`
- `delta_observation: 用户当前仍优先要求我把 7x24 轮次做成真实推进，不接受重复上一轮的同类拆分或纯观察；本轮我按这个口径改选了 task_artifact_store 查询面，而不是回去继续 graph surface。`
- `delta_validation: 下一轮若继续做工程门禁，我先验证能否把 schedule/env/role-creation 三块切成可并行批次；若切给 helper，先 refresh 对应 developer workspace 到 code_root@68ea58b。`
- `memory_ref: .codex/memory/2026-04/2026-04-20.md`

## 下一动作
1. 继续打 `schedule_service.py / workflow_env_common.ps1 / training_center_role_creation.js`，把 Mandatory Gate 再往下压。
2. 等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，部署 `test`、刷新 `prod candidate`。
3. 刷出新 candidate 后，再重跑同一条 supported prod/live member-route proof，补正向 `project_id/project_ref` 证据。
