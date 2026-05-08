# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260419-f50eddd6`
- date: `2026-04-19`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`

## Summary
- 我修掉了 `refresh_pm_current_version_snapshot.py` 对 `candidate_version=... 已更高` 的 live 文案不兼容，避免主线继续炸在 `plan_prod_status_current_shape`。
- 我把补丁以 `pm-main@865bd46 / workflow_code@865bd46` 收口，跑通了定向 acceptance 和完整 `workflow gate`，并刷新出 `test / prod candidate=20260419-011939`。
- 我又把 prod live 里的 helper daily-learning finalize stall 连续 repair 到 `ghost_running_detected=false`，把当前阻塞收窄成“等空窗切新版 + 收齐剩余学习报告”。

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=865bd46`
- `code_root_head=865bd46`
- `push_block_reason=-`
- `next_push_batch=等待 prod 空窗切到 20260419-011939 后复跑 V4-R1 current-version smoke 与协作泳道 relation-based probe-only follow-up`

## Validation
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/verify_pm_current_version_snapshot_refresh.py`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_test_workflow_env.ps1`
- `/api/status`
- `/api/runtime-upgrade/status`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`

## Active Requirements
- `V4-R1`: `in_progress / 97% / eta=2026-04-20 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `V4-R5`: `in_progress / 20% / eta=2026-04-20 / 未超时`

## Learning & Daily
- 当前 `pm/daily-execution-history/2026-04-19.md` 仍是 `in_progress`。
- 已回流学习报告：`workflow / workflow_devmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate`
- 待回流学习报告：`workflow_testmate`

## Risks
- `prod` 当前仍有 `running_task_count=1`，所以 `candidate=20260419-011939` 还没切进正式环境。
- `workflow_testmate` 的今日学习报告仍未回流，今天的 daily 还不能收成 completed。
- `create_assignment_node` 的 non-ASCII decode 坑仍是受控 warning，下一轮如果影响 live prompt 理解，优先按 supported route 处理。

## Next
- 等 idle watcher 在空窗把 `candidate=20260419-011939` 切进 `prod`。
- 切版后补 `V4-R1` 的 relation-based current-version smoke / browser probe。
- 跟进 `workflow_testmate / workflow_ucdmate` 今日学习报告回流。
