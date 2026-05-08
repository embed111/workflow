# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-29586320`
- generated_at: `2026-04-18T16:22:28+08:00`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260418-153421`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`
- preference_ref: `state/user-preferences.md`

## Result Summary
- 我把 `V4-R3` 的下一条 live 风险收成 `afd40f9`：watcher 命中 `running_finalize_stall` 时，`repair-ghost-running` 请求就算先超时，也会继续短窗口复核 `/api/runtime-upgrade/status`，不再把慢响应直接记成最终失败。
- 我先在 `verify_apply_prod_candidate_when_idle.py` 增加 slow-repair settle probe 打出红灯，再修 `scripts/apply_prod_candidate_when_idle.py`，随后跑通 line budget、定向 watcher 验收、PowerShell helper 入口和完整 `workflow gate`。
- 我把改动提交到 `.repository/pm-main@afd40f9`，同步 `../workflow_code@afd40f9`，刷新出 `test / prod candidate=20260418-161644`，并把 5 个 helper developer workspace 全部拉回 `clean_synced@afd40f9`。

## Live Truth
- `prod`: `current_version=20260418-153421 / candidate_version=20260418-161644 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / ghost_running_detected=false`
- `test`: `current_version=20260418-161644 / candidate_version=20260418-161644 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- `assignment workboard`: `running=1 / queued=1 / failed=51 / blocked=10 / workflow_mainline_starvation_state=mitigated`
- `developer workspaces`: `workflow / workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部 `ready + clean_synced@afd40f9`

## Requirement Status
- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 99% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision`: `stay(V4)`
- `next_activation_ready`: `false`
- `AAR`: `本轮无新增`

## Validation
- Red: `.repository/pm-main/.test/20260418-160556-441/report.md`
- Green: `.repository/pm-main/.test/20260418-160840-435/report.md`
- Line budget: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- Helper probe: `.repository/pm-main/.test/20260418-160939-691/report.md`
- Gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-161321.md`
- Deploy/test candidate: `.running/control/logs/test/deploy-20260418-161644.json`
- Live checks: `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=afd40f9`
- `push_block_reason=-`
- `next_push_batch=等待 prod 空窗切到 20260418-161644 后确认 slow-repair settle 读链不再把 ghost repair 误记成最终失败`

## Next
- 等 `prod` 空窗切到 `20260418-161644`
- 切版后复核 `logs/runs/prod-idle-upgrade-watchdog-live.md`，确认 watcher 不再把 ghost repair 的慢响应写成 `request_failed` 终态
- 若 live 仍有红点，下一轮继续沿 `V4-R3` formal route 收下一刀，而不是回到纯观察

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: live watcher 在 `running_finalize_stall` 上会先拿到 `repair-ghost-running` 的客户端超时，但状态真相已经可能翻成 `ghost_running_detected=false / can_upgrade=true`
- delta_validation: 观察 `20260418-161644` 切入 prod 后的 watcher 日志，确认 slow-repair settle 读链在 live 也能把这类慢响应按成功修复继续推进
