# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`
- 当前最高价值泳道继续是 `工程质量探测 / 发布边界收口`
- 当前生命周期阶段继续是 `开发实现`
- 本轮实际推进项是 `V5-R5 / pm daily governance learning-report runtime split`
- 下一步优先动作是继续压 `schedule_service.py / workflow_env_common.ps1 / assignment_core.py`

## 取舍
- 我没有回去重复上一轮已经完成的 `training loop overview create css split`，也没有再做一轮同质化的 live member-route smoke。
- 我直接正面收口新的第三个 Mandatory Gate blocker `pm_daily_governance_service.py`：把学习报告发现、delivery/result_ref 回流和 projected markdown 写回 runtime 抽到新的 `pm_daily_governance_learning_reports.py`，让主 service 退回到 daily governance 编排壳。
- 我没有强行给 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 派新主任务；这些 helper 的 developer workspace 仍停在 `cec137`，相对 `code_root@6974e87` 是 `diverged_or_unknown`，现在切过去只会放大发布边界收口成本。

## 推进结果
- 新增 `src/workflow_app/server/services/pm_daily_governance_learning_reports.py`，承接学习报告发现、optional agent formalization 和 projected markdown 写回 runtime。
- `src/workflow_app/server/services/pm_daily_governance_service.py` 从 `1169` 行压到 `616` 行。
- 新增 `scripts/acceptance/verify_pm_daily_governance_learning_reports_split.py`，并挂进 `scripts/acceptance/workflow_gate_probe_registry.py`。
- 这批代码已经提交并同步到 `pm-main@6974e87 / workflow_code@6974e87`。

## 版本现场
- 当前 active 需求评估：
  - `V5-R1 = in_progress / 60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R2 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R3 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R4 = in_progress / 96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
  - `V5-R5 = in_progress / 99% / 最近更新=2026-04-20T10:39:59+08:00 / eta=2026-04-21 / 未超时`
- 当前没有需求点超时，本轮不新增 AAR。
- `next_activation_candidate=- / next_activation_ready=false`，`V6` 仍只有 backlog 骨架，不满足切版条件。
- 当前切版 blocker 仍是：`controller cadence closure` 缺 live finalize 消费证据、`prod/live member task` 仍没有正向 `project_id/project_ref` 证据、以及 `Mandatory Gate=false`。

## 发布边界与 Live
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `push_block_reason=mandatory_gate_fail_closed`
- `next_push_batch=schedule_service.py / workflow_env_common.ps1 / assignment_core.py split + gate/acceptance`
- 当前 `line budget` 仍 fail-closed，但 `blocking_offender_count` 已从 `17` 降到 `16`；新的首批冻结对象是 `schedule_service.py / workflow_env_common.ps1 / assignment_core.py`。
- `/healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status` 当前可用；live 仍是 `1 running + 1 queued + patrol ready`，不是空窗。
- 当前 `prod=20260419-180446 / candidate_version=20260419-180446 / candidate_is_newer=false / ghost_running_detected=false / can_upgrade=false`，这批能力还没进入新的 `test/prod candidate`。

## 验证
- `.repository/pm-main/.test/20260420-103504-658/report.md`
- `.repository/pm-main/.test/20260420-103922-335/report.md`
- `.repository/pm-main/.test/20260420-103929-272/report.md`
- `.repository/pm-main/.test/20260420-103941-079/report.md`
- `.repository/pm-main/.test/20260420-103952-317/report.md`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- `git -C .repository/pm-main log -1 --pretty=format:"%H %cI %s"`
- `git -C ../workflow_code log -1 --pretty=format:"%H %cI %s"`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`

## 后续动作
- 继续正面处理 `schedule_service.py / workflow_env_common.ps1 / assignment_core.py`，把 clean head 的 Mandatory Gate 再往下压。
- 等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，再部署 `test`、刷新 `prod candidate`，然后重跑 supported live member-route proof。
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；今天的每日学习任务与真实学习报告还没有收口，我这轮不伪造 completed 记录。

- preference_ref: `state/user-preferences.md`
- delta_observation: 你持续要求我先给判断、取舍和下一动作，再补必要证据；这轮我继续按这个顺序组织版本报告。
- delta_validation: 下一轮继续保持“先判断、再证据”的正文结构，并避免把 live 字段堆成状态墙。

- memory_ref: `.codex/memory/2026-04/2026-04-20.md`
