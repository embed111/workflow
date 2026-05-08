# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`。
- 当前最高价值泳道继续保持 `工程质量探测 / 发布边界收口`，生命周期阶段保持 `开发实现`。
- 现在不切版，因为 `next_activation_ready=false`，而且 `controller cadence closure` 仍缺 live finalize 消费证据、prod/live member-route 正向 `project_id/project_ref` 证据仍未形成、`Mandatory Gate` 也还没转绿。

## 本轮推进
- 我把 [`runtime_upgrade_service.py`](D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/runtime_upgrade_service.py) 里的运行时环境、manifest/instance、supervisor、process start-stop 上下文抽到新的 [`runtime_upgrade_runtime_context.py`](D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/runtime_upgrade_runtime_context.py)。
- 我新增了 [`verify_runtime_upgrade_service_context_split.py`](D:/code/AI/J-Agents/workflow/.repository/pm-main/scripts/acceptance/verify_runtime_upgrade_service_context_split.py)，并把它挂进 [`workflow_gate_probe_registry.py`](D:/code/AI/J-Agents/workflow/.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py)。
- `runtime_upgrade_service.py` 已从 `1122` 行降到 `700` 行，`blocking_offender_count` 从 `14` 降到 `13`，首批冻结对象切换为 `schedule_service.py / workflow_env_common.ps1 / policy_confirm_and_interactions.js`。
- 这批代码已提交并收口到 `pm-main / workflow_code @0e998d9`：`refactor(runtime): 拆分升级运行时上下文以压低门禁 blocker`。

## 版本与发布边界
- 当前需求评估保持为：`V5-R1=in_progress/60%/最近更新=2026-04-19T23:50:42+08:00/eta=2026-04-21/未超时`、`V5-R2=in_progress/35%/最近更新=2026-04-19T20:37:53+08:00/eta=2026-04-21/未超时`、`V5-R3=in_progress/35%/最近更新=2026-04-19T20:37:53+08:00/eta=2026-04-21/未超时`、`V5-R4=in_progress/96%/最近更新=2026-04-19T23:50:42+08:00/eta=2026-04-21/未超时`、`V5-R5=in_progress/99%/最近更新=2026-04-20T12:10:20+08:00/eta=2026-04-21/未超时`。
- 本轮无新增 AAR。
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`。
- `push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / src/workflow_app/web_client/policy_confirm_and_interactions.js split + gate/acceptance`。
- `pm-main` 与本机 `../workflow_code` 已同步到同一提交 `0e998d9`；相对外部 `origin` 的 `ahead` 只作为参考，不当成本轮阻塞。

## Live 真相
- `/healthz` 正常；`/api/status` 当前 `running_task_count=1 / queued_task_count=2 / active_agent_count=1`。
- `/api/schedules` 当前保持 `mainline running + next mainline ready + patrol ready/future`：当前运行主线是 `node-sti-20260420-c4ea7de0`，下一条 mainline ready 是 `node-sti-20260420-eb645f3a`，patrol ready 是 `node-sti-20260420-d933c6fb`，下一次 patrol 触发时间是 `2026-04-20T12:20:00+08:00`。
- `/api/runtime-upgrade/status` 当前仍是 `current_version=candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / ghost_running_detected=false`；也就是说这批收口还没进入新的 `test/prod candidate`。
- helper 当前不强派：`workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 仍停在 `cec137`、相对 `code_root@0e998d9` 显示 `diverged_or_unknown`，这轮不适合直接在旧 commit 上派新工程任务。

## 验证
- [`report.md`](D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260420-120819-029/report.md)
- [`report.md`](D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260420-120827-095/report.md)
- [`report.md`](D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260420-120833-922/report.md)
- [`WORKSPACE_LINE_BUDGET_REPORT.json`](D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json)
- `git -C .repository/pm-main log -1 --pretty=format:"%H %cI %s"`
- `git -C ../workflow_code log -1 --pretty=format:"%H %cI %s"`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`

## 下一步
- 我下一步优先继续切 `schedule_service.py / workflow_env_common.ps1 / policy_confirm_and_interactions.js`，先把 `Mandatory Gate` 再往下压。
- 等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，我再部署 `test`、刷新 `prod candidate`，然后重跑 supported live member-route proof。
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；原因不是遗忘，而是今天的每日学习任务与真实学习报告还没收口，我这轮不伪造 completed 记录。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮更高价值切片已经从 `runtime_upgrade_service.py` 切到了新的 `policy_confirm_and_interactions.js`，而 helper developer workspaces 仍停在旧 commit；当前继续强派只会把工程质量主任务扔进旧基线。
- delta_validation: 继续压 `schedule_service.py / workflow_env_common.ps1 / policy_confirm_and_interactions.js`，待 `Mandatory Gate` 再下压后补 `workflow gate / runtime release gate`，随后刷新 `test/prod candidate` 并重跑 supported live member-route proof。
- memory_ref: `.codex/memory/2026-04/2026-04-20.md`
