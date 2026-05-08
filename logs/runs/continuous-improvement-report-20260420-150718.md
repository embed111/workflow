# [持续迭代] workflow / 2026-04-20 14:34:00

**判断**
- `version_transition_decision=stay(V5)`。当前更高价值的仍是 `V5-R5 / 工程质量探测 / 发布边界收口`，不是重复 prod live proof，也不是提前切到 `V6`。
- 我这轮把 `scripts/acceptance/run_acceptance_schedule_center_browser.py` 从 Mandatory Gate 首批冻结对象里挪掉了；新的第三个 blocker 已换成 `src/workflow_app/server/presentation/templates/index_training_center_layout.css`。
- helper 这轮继续不派发：`workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 仍停在 `cec137`，相对 `code_root@9259c1a` 还是 `diverged_or_unknown`，先 refresh 再并行更稳。

**本轮推进**
- 我新增了 `.repository/pm-main/scripts/acceptance/schedule_center_browser_acceptance_support.py`，把 HTTP helper、Edge probe、runtime bootstrap、SQLite/event 取证和 markdown report 从 runner 里抽成独立 support module。
- 我把 `.repository/pm-main/scripts/acceptance/run_acceptance_schedule_center_browser.py` 压到 `488` 行，并补上 `.repository/pm-main/scripts/acceptance/verify_schedule_center_browser_acceptance_split.py`，同时把 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py` 追平到新的 split contract。
- 我按 `test-session-manager` 先跑 `HEAD` 红灯 `.repository/pm-main/.test/20260420-150436-272/report.md`，确认旧 runner 仍是 `1048` 行且缺 support import；随后把 working tree 的 dedicated split probe 收绿 `.repository/pm-main/.test/20260420-150443-677/report.md`，再补跑最新 line budget `.repository/pm-main/.test/20260420-150451-977/report.md`。
- 我把代码提交成 `pm-main@9259c1a refactor(schedule): 拆分 schedule center 浏览器验收 support 以压低门禁 blocker`，再用受支持的 `git -C ../workflow_code fetch D:/code/AI/J-Agents/workflow/.repository/pm-main main` + `git -C ../workflow_code merge --ff-only FETCH_HEAD` 把本机根仓追平到同一提交。

**版本评估**
- `V5-R1`：`in_progress / 60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
- `V5-R2`：`in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R3`：`in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R4`：`in_progress / 96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`
- `V5-R5`：`in_progress / 99% / 最近更新=2026-04-20T15:04:58+08:00 / eta=2026-04-21 / 未超时`
- 本轮没有超时需求，不新增 AAR。

**发布边界与验证**
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=9259c1a`
- `push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/presentation/templates/index_training_center_layout.css split + gate/acceptance`
- 最新 `line budget` 仍 fail-closed，但 `blocking_offender_count` 已从 `7` 降到 `6`；当前首批冻结对象是 `schedule_service.py / workflow_env_common.ps1 / index_training_center_layout.css`
- `/healthz` 正常；`/api/status` 当前是 `running_task_count=1 / active_agent_count=1 / queued_task_count=2`
- 当前 mainline 仍是 `node-sti-20260420-f4aff3ca / running@2026-04-20T14:34:00+08:00`；下一条 mainline 已变成 `node-sti-20260420-41330836 / ready@2026-04-20T14:54:00+08:00`；保底 patrol 也已经是 `node-sti-20260420-ece7368d / ready@2026-04-20T15:00:00+08:00`
- `/api/runtime-upgrade/status` 仍是 `current_version=candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / blocking_reason=running_tasks_present`

**下一步**
- 我下一步优先继续切 `schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/presentation/templates/index_training_center_layout.css`，把 Mandatory Gate 再往下压。
- 等 `line budget / workflow gate / runtime release gate` 再往前走后，我再部署 `test`、刷新 `prod candidate`，然后重跑 supported live member-route proof。
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；这不是遗忘，而是今天的每日学习任务与真实学习报告还没收口，我这轮不伪造 completed 记录。
- `memory_ref=.codex/memory/2026-04/2026-04-20.md`
