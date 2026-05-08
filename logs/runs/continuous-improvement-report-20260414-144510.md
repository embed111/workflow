# [持续迭代] workflow / 2026-04-14 13:30:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-a4492c78`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- release_boundary: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=ba31b50 / push_block_reason=- / next_push_batch=待切批`

## 本轮推进
- 我更新了 `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`，新增 `_schedule_result_summary_for_display(...)`，让 `/api/schedules` full list/detail 在节点已 `running / queued / succeeded` 时优先显示 live `assignment_status_text / result_status_text`，不再把历史 `assigned agent already has running node` 文案误报成当前结果。
- 我新增 `.repository/pm-main/scripts/acceptance/verify_schedule_live_result_summary.py`，并把它接进 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`，把“trigger_message 仍是 busy-skip，但 live 节点已经 running”这条回归锁进门禁。
- 我在 `.repository/pm-main` 提交 `ba31b50 fix(schedule): 优先显示定时任务节点的 live 结果摘要`；由于 direct push 到本机 `workflow_code` 命中 `updateInstead` 拒绝，我改走受支持的本地 `fetch + ff-only merge` 完成根仓收口。
- 我按受支持路径先停掉 `test`，再重跑 `deploy_workflow_env.ps1 -Environment test`，把 `test/prod candidate` 刷到 `20260414-144235`。

## 验证
- line budget：`.repository/pm-main/.test/20260414-143201-126/report.md`
- 定向 probe：`.repository/pm-main/.test/20260414-143425-257/report.md`
- workflow gate：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-143630.md`
- test 部署：`.running/control/logs/test/deploy-20260414-144235.json`
- live 复核：`/healthz=ok`

## 版本评估
- `V2-R1=status=completed / progress=100% / eta=已于 2026-04-14 完成 / timeout=-`
- `V2-R2=status=in_progress / progress=93% / eta=2026-04-18 / timeout=未超时`
- `V2-R3=status=in_progress / progress=99% / eta=2026-04-19 / timeout=未超时`
- `V2-R4=status=in_progress / progress=79% / eta=2026-04-19 / timeout=未超时`
- `V2-R5=status=in_progress / progress=96% / eta=2026-04-15 / timeout=未超时`
- `V2-R6=status=in_progress / progress=80% / eta=2026-04-15 / timeout=未超时`
- `V2-R7=status=in_progress / progress=82% / eta=2026-04-16 / timeout=未超时`
- `V2-R8=status=completed / progress=100% / eta=已于 2026-04-13 完成 / timeout=-`
- 本轮无需求点超时，不触发新的版本 AAR。

## Live 真相
- `/api/status`：`active_version=V2 / lane=工程质量探测 / lifecycle_stage=开发实现 / baseline=prod=20260414-134341 / running_task_count=1 / queued_task_count=2`
- `/api/runtime-upgrade/status`：`current_version=20260414-134341 / candidate_version=20260414-144235 / candidate_is_newer=true / drain_active=true / can_upgrade=false / blocking_reason=running_tasks_present`
- `/api/schedules`：mainline `last=node-sti-20260414-62dfa2ba / queued`，patrol `last=node-sti-20260414-f7403343 / queued`，patrol `next=2026-04-14T15:00:00+08:00`
- 当前 workflow 直接出口是 `running + queued + patrol future`，`workflow_mainline_starvation_state=mitigated`

## 风险与下一步
- 当前更高 `candidate=20260414-144235` 正在 drain 等待 idle watcher 创造升级空窗。
- 在 `144235` 切进 `prod` 之前，live `prod(8090)` 仍会在 `/api/schedules` full list/detail 中保留旧的 busy-skip 摘要优先级。
- 下一步优先复核 `144235` 切版后的 `/api/schedules` full list/detail` 与 `/api/status` workboard preview 是否一致；这条 `R4` 风险收稳后，再把窗口切回 `R5 / R2` 的正式编号化证据与收尾。

- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-14.md`
