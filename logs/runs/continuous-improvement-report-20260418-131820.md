# Continuous Improvement Report

- generated_at: `2026-04-18T13:18:20+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-b4c6fc4c`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- preference_ref: `state/user-preferences.md`

## 本轮推进

- 我先用受支持的 developer workspace refresh，把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 从 `3188351` 收回到 `clean_synced@6290feb`，先把 helper drift 从 live 真相里移除。
- 我在 `.repository/pm-main@6e6839e` 修掉了 `assignment_probe=1` 下的浏览器 acceptance 挂死：`app_runtime_controls.js` 现在不会再启动 workflow poller、runtime-upgrade poller 和自动 policy analysis。
- 我把这批改动用 `line budget`、一次 red->green 的 `collect_v4_r1_r4_current_version_smoke.py` 复跑、完整 `workflow gate` 验证通过，再同步到 `../workflow_code@6e6839e`。
- 我随后再次把 5 个 helper developer workspace 刷到 `clean_synced@6e6839e`，并刷新出 `test / prod candidate=20260418-131806`；`deploy-20260418-131806.json` 自动记录了 `post_deploy_ghost_running.repaired_count=1`。

## 当前版本判断

- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 97% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision=stay(V4) / next_activation_candidate=- / next_activation_ready=false / switch_blockers=V5 仍保持 backlog activation_readiness=draft`

## 发布边界

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=6e6839e`
- `next_push_batch=等待 prod 空窗切到 20260418-131806 后复跑 live current-version smoke / running_detail browser contract`

## Live Truth

- `prod`: `current_version=20260418-123447 / candidate_version=20260418-131806 / candidate_is_newer=true / request_pending=false / running_task_count=1 / queued_task_count=2 / ghost_running_detected=false`
- `test`: `current_version=20260418-131806 / candidate_version=20260418-131806 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- `developer_workspaces`: `pm-main + 5 helper` 当前已全部回到 `clean_synced@6e6839e`

## 验证

- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-130655-914/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-130710-136/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-131031-638/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-131350.md`
- `D:/code/AI/J-Agents/workflow/.running/control/logs/test/deploy-20260418-131806.json`

## 风险与下一步

- `prod` 当前仍有 running mainline，idle watcher 还不能 apply `20260418-131806`。
- 下一步优先等待空窗切版后复跑 `collect_v4_r1_r4_current_version_smoke.py`，确认 live `running_detail` browser contract 与 helper workspace clean-synced 没有回退。
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`
