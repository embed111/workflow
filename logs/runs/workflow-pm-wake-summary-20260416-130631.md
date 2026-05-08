# workflow-pm-wake-summary

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260416-47909914`
- generated_at: `2026-04-16T13:06:31+08:00`
- active_version: `V3`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V3)`

## 现场结论
- 我确认 `prod` 当前健康，`/healthz=ok`，`/api/runtime-upgrade/status.current_version=20260416-120206`。
- 当前 `prod candidate=20260416-125712`，`candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`，所以正式升级仍需等 idle watcher 命中空窗。
- live 风险不再是“主链已断”，而是两条更具体的真问题：`/api/status.document_baseline` 此前落后于 live `120206`，以及 `[持续迭代] workflow` 主线 schedule 一度掉成 `failed + 无 next_trigger_at`。
- 我这轮已经把主线 future 恢复为 `2026-04-16T13:15:00+08:00`，保底 future 仍在 `2026-04-16T13:20:00+08:00`，当前出口回到 `1 running patrol + 1 future mainline + 1 future patrol`。

## 本轮推进修改
- 我修改了 `.repository/pm-main/scripts/deploy_workflow_env.ps1`，让 `prod` 直发路径也自动刷新 PM current-version snapshot，避免直发后 `PM当前版本计划.md` 和 `/api/status.document_baseline` 继续停在旧 baseline。
- 我扩了 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh.py`，把 prod 直发的 snapshot refresh hook 锁进验收。
- 我把 `.repository/pm-main/scripts/acceptance/run_acceptance_schedule_center_browser.py` 的 HTTP timeout 参数化，并把 `.repository/pm-main/scripts/acceptance/run_acceptance_assignment_self_iteration_schedule.py` 的 graph/schedules 慢轮询放宽到 `90s`，把 `verify_pm_awake_tc_pack.py` 和完整 `workflow gate` 重新拉回通过态。
- 我把代码提交为 `b75cbe6 fix(release): 补prod直发快照刷新并放宽自迭代验收慢链路`，并同步到本机 `../workflow_code`。
- 我停掉旧 `test` 后重新部署，把 `test/candidate` 刷到 `20260416-125712`。
- 我把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 五个 helper developer workspace 全量 refresh 到 `clean_synced@b75cbe6`。
- 我用受支持的 `/api/schedules/{id}` update，把 `[持续迭代] workflow` 主线 schedule 重新挂回 `2026-04-16T13:15:00+08:00` 的 future trigger。

## 版本评估
- `V3-R1`: `completed / 100% / ETA 2026-04-16 / 未超时`
- `V3-R2`: `in_progress / 96% / ETA 2026-04-16 / 未超时`
- `V3-R3`: `planned / 35% / ETA 2026-04-18 / 未超时`
- `V3-R4`: `completed / 100% / ETA 2026-04-16 / 未超时`
- `V3-R5`: `in_progress / 99% / ETA 2026-04-16 / 未超时`
- 当前不满足切到 `V4` 的条件，`next_activation_candidate=V4 / next_activation_ready=false`，所以这轮继续 `stay(V3)`。
- 当前 release boundary 真相是：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=b75cbe6 / push_block_reason=-`。

## 验证
- `.repository/pm-main/.test/20260416-122512-387/report.md`
- `.repository/pm-main/.test/20260416-122538-543/report.md`
- `.repository/pm-main/.test/20260416-122603-530/report.md`
- `.repository/pm-main/.test/20260416-123933-194/report.md`
- `.repository/pm-main/.test/20260416-124843-425/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260416-125430.md`
- `.running/control/logs/test/deploy-20260416-125712.json`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/config/developer-workspaces`

## 下一步
- 我先等 idle watcher 在空窗把 `prod` 切到 `20260416-125712`。
- 切版后优先让 `workflow_testmate` 重跑 current-version smoke，把 `V3-R5` 的结论追平到最新 live baseline。
- 然后我给 `workflow_devmate` 补一条 `workflow_focus_context` clean rerun，把 `V3-R2` 的剩余缺口继续压缩。
- 当前仍保留 `ghost_running_detected=true / ghost_running_count=4` 的历史 refs；这轮先不把它和主线出口、发布边界混成同一优先级，下一拍单独清债。
