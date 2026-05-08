# continuous improvement report

**判断**
- `version_transition_decision=stay(V5)`。
- 本轮阶段切到 `开发实现`；当前最高价值泳道是 `工程质量探测 / 发布边界收口`。
- 我这轮没有再重复 prod live probe，而是直接把 `schedule_service.py` 的 self-iteration smoke guard / backup schedule / smoke baseline 运行时职责抽到了新模块 `schedule_self_iter_runtime.py`，并把这批代码收口到 `pm-main@c33dee3 / workflow_code@c33dee3`。
- 这刀之后，`schedule_service.py` 已经退出 Mandatory Gate 的 first batch targets；新的首批冻结对象改成了 `assignment_center_render_runtime.js / workflow_env_common.ps1 / index_training_loop_panels.css`。

**取舍**
- 我没有继续做同一条 `prod/live member-route` 负向证据，因为上一轮已经把这个 blocker 钉成真相；这轮更值钱的是把 clean head 上的 Mandatory Gate 真往下压。
- 我按 `test-session-manager` 串行跑过了 `py_compile`、`verify_schedule_smoke_guard_scope.py`、`verify_schedule_smoke_guard_expired_fail_open.py`、`verify_self_iteration_backup_schedule_on_smoke_block.py`、`verify_smoke_baseline_guard_recovery.py` 和最新 `line budget`。
- 定向 probe 都过了，说明这次抽模块没有把 self-iteration smoke guard / backup schedule 合同打坏；最新 `line budget` 仍是红灯，但 `schedule_service.py` 已从 `2383` 行压到 `1871` 行，并退出 first batch targets。
- helper 这轮没有新派发：`parallel_candidate_count=1 / parallel_dispatched_count=0 / active_helper_tasks=- / non_dispatch_reason=当前最高价值切片是 pm-main 本地 Mandatory Gate 收口，先把已验证批次提交并同步根仓更值`。

**下一动作**
- 先继续打 `assignment_center_render_runtime.js` 或 `workflow_env_common.ps1`，把 Mandatory Gate 再往下压一刀。
- 等 `line budget / workflow gate` 转绿后，再部署 `test`、刷新 `prod candidate`，然后重跑 prod/live member-route proof，补齐正向项目字段证据。
- 当前 active 需求评估：`V5-R1=60%`，`V5-R2=35%`，`V5-R3=35%`，`V5-R4=96%`，`V5-R5=72%`；全部 `eta=2026-04-21`，本轮无超时，无 AAR。

**证据**
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=c33dee3 / push_block_reason=mandatory_gate_fail_closed / next_push_batch=assignment_center_render_runtime.js / workflow_env_common.ps1 / index_training_loop_panels.css split + gate/acceptance`
- live status：`running_task_count=1 / queued_task_count=2 / active_agent_count=1 / current_version=candidate_version=20260419-180446 / candidate_is_newer=false / ghost_running_detected=false / can_upgrade=false`
- current exits：`current_mainline=node-sti-20260419-a5935cd3(running) / next_mainline=node-sti-20260420-ef728491(ready) / patrol=node-sti-20260420-43edf2a2(ready)`
- 定向验证：`.repository/pm-main/.test/20260420-002455-757/report.md`、`.repository/pm-main/.test/20260420-002503-449/report.md`、`.repository/pm-main/.test/20260420-002515-269/report.md`、`.repository/pm-main/.test/20260420-002532-169/report.md`、`.repository/pm-main/.test/20260420-002539-685/report.md`
- 门禁真相：`.repository/pm-main/.test/20260420-002547-454/report.md`、`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- `memory_ref=.codex/memory/2026-04/2026-04-20.md`
- `preference_ref=state/user-preferences.md`

### Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: `schedule_service.py` 已经通过 self-iteration runtime 抽模块退出当前 first batch targets，但 Mandatory Gate 仍未转绿；当前阻塞集中到 `assignment_center_render_runtime.js / workflow_env_common.ps1 / index_training_loop_panels.css`
- delta_validation: 继续切剩余 first batch targets；待 gate 继续下降后刷新 `test/prod candidate`，并重跑 prod/live member-route 正向证据
