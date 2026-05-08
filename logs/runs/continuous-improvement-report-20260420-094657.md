# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`
- 当前最高价值泳道继续是 `工程质量探测 / 发布边界收口`
- 当前生命周期阶段继续是 `开发实现`
- 本轮实际推进项是 `V5-R5 / defect assignment runtime split`
- 下一步优先动作是继续压 `schedule_service.py / workflow_env_common.ps1 / index_training_loop_overview.css`

## 取舍
- 我没有回去重复上一轮已经完成的 `index_training_center_role_creation.css` split，也没有再做一轮同质化的 live member-route smoke。
- 我把 `defect_service_task_commands.py` 当成新的第三个 Mandatory Gate blocker 正面收口：把缺陷任务图绑定、task name base、task ref upsert 和 legacy graph repair runtime 抽到 `defect_service_assignment_runtime.py`，让 command entrypoint 回到薄壳。
- 我没有强行给 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 派新主任务；这些 helper 的 developer workspace 仍停在 `cec137`，相对 `code_root@4143bf6` 是 `diverged_or_unknown`，现在切过去只会放大收口成本。

## 推进结果
- 新增 `src/workflow_app/server/services/defect_service_assignment_runtime.py`，把 defect assignment runtime helper 从 `defect_service_task_commands.py` 拆出。
- `src/workflow_app/server/services/defect_service_task_commands.py` 从 `1187` 行压到 `269` 行；新 support runtime 为 `910` 行。
- 新增 `scripts/acceptance/verify_defect_service_assignment_runtime_split.py`，并挂进 `scripts/acceptance/workflow_gate_probe_registry.py`。
- 我顺手把 `scripts/acceptance/run_acceptance_defect_task_naming_and_global_graph_check.py` 的 schedule detail 断言改成短轮询，避免把 `queued_for_processing` 的正常异步回写误报成假红灯。
- 这批代码已经提交并同步到 `pm-main@4143bf6 / workflow_code@4143bf6`。

## 版本现场
- 当前 active 需求评估：
  - `V5-R1 = in_progress / 60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R2 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R3 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R4 = in_progress / 96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R5 = in_progress / 99% / 最近更新=2026-04-20T09:46:57+08:00 / eta=2026-04-21 / 未超时`
- 当前没有需求点超时，本轮不新增 AAR。
- `next_activation_candidate=- / next_activation_ready=false`，`V6` 仍只有 backlog 骨架，不满足切版条件。
- 当前切版 blocker 仍是：`controller cadence closure` 缺 live finalize 消费证据、`prod/live member task` 仍没有正向 `project_id/project_ref` 证据、以及 `Mandatory Gate=false`。

## 发布边界与 Live
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `push_block_reason=mandatory_gate_fail_closed`
- `next_push_batch=schedule_service.py / workflow_env_common.ps1 / index_training_loop_overview.css split + gate/acceptance`
- 当前 `line budget` 仍 fail-closed，但 `blocking_offender_count` 已从 `19` 降到 `18`；新的首批冻结对象是 `schedule_service.py / workflow_env_common.ps1 / index_training_loop_overview.css`。
- `/healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status` 当前可用；live 仍是 `1 running + 2 ready exits`，不是空窗。
- 当前 `prod=20260419-180446 / candidate_version=20260419-180446 / candidate_is_newer=false / ghost_running_detected=false / can_upgrade=false`，这批能力还没进入新的 `test/prod candidate`。

## 验证
- `.repository/pm-main/.test/20260420-094009-227/report.md`
- `.repository/pm-main/.test/20260420-094326-011/report.md`
- `.repository/pm-main/.test/20260420-094326-104/report.md`
- `.repository/pm-main/.test/20260420-094451-148/report.md`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- `git -C .repository/pm-main log -1 --pretty=format:"%H %cI %s"`
- `git -C ../workflow_code log -1 --pretty=format:"%H %cI %s"`
- `python .repository/pm-main/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`

## 后续动作
- 继续正面处理 `schedule_service.py / workflow_env_common.ps1 / index_training_loop_overview.css`，把 clean head 的 Mandatory Gate 再往下压。
- 等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，再部署 `test`、刷新 `prod candidate`，然后重跑 supported live member-route proof。
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；今天的每日学习任务与真实学习报告还没有收口，我这轮不伪造 completed 记录。

- preference_ref: `state/user-preferences.md`
- delta_observation: 你持续要求我先给判断、取舍和下一动作，再补必要证据；这轮我继续按这个顺序组织版本报告。
- delta_validation: 下一轮继续保持“先判断、再证据”的正文结构，并避免把 live 字段堆成状态墙。

- memory_ref: `.codex/memory/2026-04/2026-04-20.md`
