# continuous improvement report

**判断**
- `version_transition_decision=stay(V5)`。
- 本轮阶段是 `基于基线测试`；当前最高价值泳道切到 `测试探测 / 发布边界收口`。
- 我用 supported live API 把 `prod/live member task` 这个 blocker 钉成了明确事实：在 `prod=20260419-180446` 上，`project_binding_mode=auto` 会真实建出 `workflow_testmate` 的 live member node，但 `project_id/project_ref` 仍为空。
- `pm-main` 与本机 `../workflow_code` 已经收口到 `clean_synced@a9b6b4d`，不再是开工时的 `ahead_dirty`；当前真正挡住发布推进的是 `Mandatory Gate=false`，不是 git 脏边界。

**取舍**
- 我没有继续重复隔离 runtime smoke，也没有把客户端超时误判成 API 失败。
- 我先在全局主图里用 supported API 建了两条 live probe node，再用 `node.json / status-detail / audit` 回读真相；确认当前 prod baseline 仍不产出项目字段后，再用 delete API 把两条 probe node 清掉，避免主图留下额外 `ready` 噪音。
- 我随后按 `test-session-manager` 在 clean head 上跑了一轮 `line budget`。结果仍是红灯：`blocking_offender_count=38`，首批冻结对象继续锁定 `assignment_center_render_runtime.js / schedule_service.py / workflow_env_common.ps1`，所以这轮不误报 `test/prod candidate` 可继续。

**下一动作**
- 先继续打 `V5-R5` 的首批冻结对象，优先 `assignment_center_render_runtime.js` 或 `schedule_service.py`，把 `Mandatory Gate` 从 `fail-closed` 往下压。
- 等 `a9b6b4d` 对应的 `line budget / workflow gate` 转绿后，再部署 `test`、刷新 `prod candidate`，然后重跑同一条 supported live member-route proof，补齐正向 prod/live 证据。
- 当前 active 需求评估：`V5-R1=60%`，`V5-R2=35%`，`V5-R3=35%`，`V5-R4=96%`，`V5-R5=65%`；全部 `eta=2026-04-21`，本轮无超时，无 AAR。

**证据**
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=a9b6b4d / push_block_reason=mandatory_gate_fail_closed / next_push_batch=first_batch_targets continuation + gate/acceptance after next split`
- live probe create refs：`aaud-20260419-234451-477bf5`、`aaud-20260419-234626-6616dd`
- live probe delete refs：`aaud-20260419-234920-7994d0`、`aaud-20260419-235053-4e8a48`
- `line budget` session：`.repository/pm-main/.test/20260419-235421-025/report.md`
- `line budget` truth：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- live status：`running_task_count=1 / queued_task_count=2 / active_agent_count=1 / current_version=candidate_version=20260419-180446 / ghost_running_detected=false / can_upgrade=false / next_activation_ready=false`
- `memory_ref=.codex/memory/2026-04/2026-04-19.md`
- `preference_ref=state/user-preferences.md`

### Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 当前 prod 已能真实写入 `workflow_testmate` 的 auto-bound live member node，但 `project_id/project_ref` 仍为空；同时 `pm-main / ../workflow_code` 已 clean_synced 到 `a9b6b4d`，当前阻塞已切换为 `Mandatory Gate=false`
- delta_validation: 先继续切 `assignment_center_render_runtime.js / schedule_service.py / workflow_env_common.ps1`，待 gate 转绿后部署 `test`、刷新 `prod candidate`，并重跑同一条 supported live member-route proof
