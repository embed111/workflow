**判断**
- `version_transition_decision=stay(V5)`。当前 `next_activation_candidate=- / next_activation_ready=false`，`V6` 仍只有 backlog 骨架；切版 blocker 仍是 `controller cadence closure` 缺 live finalize 消费证据、`prod/live member task` 仍没有正向 `project_id/project_ref` 证据，以及 `Mandatory Gate=false`。
- live 当前是 `running_task_count=1 / queued_task_count=2 / active_agent_count=1`；`[持续迭代] workflow` 与 `pm持续唤醒 - workflow 主线巡检` 都仍启用，所以我这轮不补链、不切保底接管，最高价值泳道继续保持在 `工程质量探测 / 发布边界收口`。
- 下一动作已经明确：先继续压 `schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/presentation/templates/index.html`，等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，再刷新 `test / prod candidate` 并重跑 supported live member-route proof。

**本轮推进**
- 我把 assignment center 的 probe/runtime 探针整块从 `assignment_center_events.js` 抽到新的 `assignment_center_probe_runtime.js`，让主文件只保留操作按钮、detail action 和 DOM 事件绑定。
- 我新增了 `verify_assignment_center_probe_runtime_split.py` 并挂进 `workflow_gate_probe_registry.py`，把 `manifest` 顺序、关键 probe 函数迁移和主文件行数回到阈值内这几个 contract 锁成 dedicated split probe。
- 这刀落完之后，`assignment_center_events.js` 从 `1240` 行降到 `559` 行，新 probe runtime part 是 `680` 行；最新 `line budget` 里，`blocking_offender_count` 从 `26` 降到了 `24`，`assignment_center_events.js` 已退出 `first_batch_targets`，新的第三个 blocker 已切到 `src/workflow_app/server/presentation/templates/index.html`。
- 我把代码提交成 `pm-main@94cdd1a refactor(assignment): 拆分 assignment center probe runtime 以压低门禁 blocker`，并用受支持的 `../workflow_code fetch + ff-only merge` 把本机根仓同步到同一提交。

**版本与边界**
- 当前 active 需求评估：`V5-R1=in_progress/60%/最近更新=2026-04-19T23:50:42+08:00/eta=2026-04-21/未超时`；`V5-R2=in_progress/35%/最近更新=2026-04-19T20:37:53+08:00/eta=2026-04-21/未超时`；`V5-R3=in_progress/35%/最近更新=2026-04-19T20:37:53+08:00/eta=2026-04-21/未超时`；`V5-R4=in_progress/96%/最近更新=2026-04-19T23:50:42+08:00/eta=2026-04-21/未超时`；`V5-R5=in_progress/99%/最近更新=2026-04-20T07:50:03+08:00/eta=2026-04-21/未超时`。本轮没有需求点超时，不新增 AAR。
- 发布边界真相：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=94cdd1a / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/presentation/templates/index.html split + gate/acceptance`。
- 当前 `pm-main` 已回到 `## main...origin/main`；代码根仓当前 `## main...origin/main [ahead 193]` 仍只反映外部 tracking ref，不构成本轮收口阻塞。
- 当前没有 active helper task，也不需要给 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 做 create / restore / rerun / adjust；`parallel_candidate_count=1 / parallel_dispatched_count=0 / active_helper_tasks=- / parallel_peak_count=0 / parallel_peak_duration=0 / parallel_total_active_duration=0 / parallel_block_reason=这轮最高价值切片是 pm-main 本地 assignment center probe runtime split + release boundary 收口，且 helper developer workspaces 仍停在 cec137、落后 code_root@94cdd1a / helper_dispatch_focus=none / helper_dispatch_effect=assignment_center_events.js 已退出 first batch targets，blocking_offender_count 已降到 24 / non_dispatch_reason=本轮不强行 dispatch 旧 commit helper；下一次若切 helper 先 refresh 目标工作区`。

**验证**
- `.repository/pm-main/.test/20260420-075040-408/report.md`：`verify_assignment_center_probe_runtime_split.py` 绿灯。
- `.repository/pm-main/.test/20260420-074940-005/report.md`：`check_web_client_bundle_syntax.js` 绿灯。
- `.repository/pm-main/.test/20260420-075048-249/report.md`：`py_compile` 绿灯。
- `.repository/pm-main/.test/20260420-074956-135/report.md` 与 `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`：最新 `line budget` 仍 fail-closed，但 `blocking_offender_count=24`，新的首批冻结对象已切成 `schedule_service.py / workflow_env_common.ps1 / index.html`。
- `python .repository/pm-main/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`

**Warnings**
- `candidate_version` 仍等于 `prod=20260419-180446`；这批改动还没进入新的 `test / prod candidate`。
- `pm/daily-execution-history/2026-04-20.md` 仍缺失，因为今日学习任务与真实学习报告尚未收口，我这轮没有伪造 completed 记录。
- 我一开始把 test-session wrapper 并行跑到了一次 `.test/reports/history.jsonl` 写锁；随后已经按经验卡改成串行重跑，最终验证结论以串行 session 为准，这不是产品回归。
- `memory_ref=.codex/memory/2026-04/2026-04-20.md`

**Snapshot Addendum**
- preference_ref: `state/user-preferences.md`
- delta_observation: 你这轮继续要求我先给判断、取舍和下一动作，再补必要证据；我保持把 live 状态压成最小引用，不回到状态墙播报。
- delta_validation: 下一轮继续先给 `version_transition_decision` 和当前最高价值切片，再补验证引用。
