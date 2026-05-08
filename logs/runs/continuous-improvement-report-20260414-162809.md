# continuous-improvement-report

- executed_at: `2026-04-14T16:28:09+08:00`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- active_version: `V2`
- baseline: `prod=20260414-144235`
- release_boundary: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=8c574f4 / push_block_reason=- / next_push_batch=待切批`
- memory_ref: `.codex/memory/2026-04/2026-04-14.md`

## Summary
- 我没有继续等 `workflow_testmate` 运行态里那份一次性 smoke 脚本，而是在 `.repository/workflow_testmate` 新增了正式的 `scripts/acceptance/collect_v2_r4_r5_current_version_smoke.ps1`，把 `R4/R5` 的 `144235` current-version smoke 收成可复用测试资产。
- 我同步把这条 smoke 纳入 `.repository/workflow_testmate/scripts/acceptance/verify_powershell_script_parse.py`，并完成了 line budget、parse 会话和 live smoke 会话验证。
- 我把 `workflow_testmate` 的提交 `8c574f4 test(smoke): 固化V2 R4 R5当前版回归脚本` 收口进 `../workflow_code`，再把 `pm-main` 与全部 helper developer workspace 统一 refresh 到 `8c574f4`。

## Validation
- `.repository/workflow_testmate/.test/20260414-161724-296/report.md`
- `.repository/workflow_testmate/.test/20260414-161942-148/report.md`
- `.repository/workflow_testmate/.test/20260414-161942-148/artifacts/workflow-testmate-v2-r4-r5-current-version-smoke.md`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/schedules`
- `Get-Content -Raw state/developer-workspaces.json`

## Active Requirements
- `V2-R1`: `completed / 100% / 已于 2026-04-14 完成 / 未超时`
- `V2-R2`: `in_progress / 95% / ETA 2026-04-18 / 未超时`
- `V2-R3`: `in_progress / 99% / ETA 2026-04-19 / 未超时`
- `V2-R4`: `in_progress / 86% / ETA 2026-04-19 / 未超时`
- `V2-R5`: `in_progress / 98% / ETA 2026-04-15 / 未超时`
- `V2-R6`: `in_progress / 80% / ETA 2026-04-15 / 未超时`
- `V2-R7`: `in_progress / 90% / ETA 2026-04-16 / 未超时`
- `V2-R8`: `completed / 100% / 已于 2026-04-13 完成 / 未超时`

## Live Truth
- `/api/status`: `running_task_count=1 / queued_task_count=2 / workflow_mainline_starvation_state=mitigated`
- `/api/runtime-upgrade/status`: `current_version=20260414-144235 / candidate_version=20260414-144235 / candidate_is_newer=false / drain_active=false / can_upgrade=false`
- `/api/schedules`: mainline 与 patrol 的 latest queued summary 都已是 `待开始`，不再回显旧的 `assigned agent already has running node`
- `rcs-20260414-004251-d716cd`: `creating / workspace_init_status=completed / stage=acceptance_confirmation`

## Retro Delta
- preference_ref: `state/user-preferences.md`
- delta_observation: 只把 current-version smoke 留在 helper 运行态里的临时 PowerShell 脚本会把类型处理错误误报成产品回归；把 smoke 正式沉到 developer workspace 更稳。
- delta_validation: 下一轮优先把这条 smoke 继续映射成 `R4/R7` 的 PM 侧专项编号，并继续补 `R5` 的正式编号化证据。
