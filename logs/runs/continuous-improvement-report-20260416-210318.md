# Continuous Improvement Report

- generated_at: `2026-04-16T21:03:18+08:00`
- preference_ref: `state/user-preferences.md`
- delta_observation: `prod=20260416-194053` 上的 current-version smoke 已正式打出 `schedule_list_response_too_slow`；`/api/schedules` 实测 `44926ms`，而新的 `candidate=20260416-205559` 已完成 gate 并等待 idle watcher 空窗切版。
- delta_validation: 等 `20260416-205559` 切进 live 后，优先复跑 current-version smoke，确认 `/api/schedules` 已回到 `15000ms` 预算内，并继续检查 next mainline launch summary 是否随新基线滚动。

## Summary

我这轮把 failed mainline 留下的 staged 批次收成了正式发布批次：`pm-main` 已提交 `33d2310 fix(schedule): 让定时列表使用live结果预览并补当前版本smoke时延验收`，本机 `../workflow_code` 已 fast-forward 到同一提交，五个 helper developer workspace 也都 refresh 到 `clean_synced@33d2310`。随后我重发了 `test`，生成新的 `prod candidate=20260416-205559`。

这轮真正新增的推进性修改有三项：

1. `schedule_service.py`
   `/api/schedules` 的列表读链不再直接沿用慢的 assignment runtime 状态读取，而是改成 task-file runtime preview，优先把列表级 `last_result_status / last_result_summary` 从文件真相投影出来。
2. `collect_v2_r4_r5_current_version_smoke.ps1`
   current-version smoke 新增 `schedule_list_response_within_budget`，把 `/api/schedules` 的响应时延正式纳入验收。
3. `verify_schedule_live_result_summary.py`
   acceptance 现在不仅锁 detail/preview，也把 `list_schedules()` 的 live `running / 运行中 / 进行中` summary 一并锁住。

## Validation

- `.repository/pm-main/.test/20260416-204351-517/report.md`
  `python scripts/quality/check_workspace_line_budget.py --root .`
- `.repository/pm-main/.test/20260416-204404-779/report.md`
  `python scripts/acceptance/verify_schedule_live_result_summary.py`
- `.repository/pm-main/.test/20260416-204515-866/report.md`
  `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `.running/control/logs/test/deploy-20260416-205559.json`
  `test` 部署通过并生成 `candidate=20260416-205559`
- `.repository/pm-main/.test/20260416-205627-536/report.md`
  live current-version smoke 失败，明确冻结 `schedule_list_response_too_slow`
- live probe
  `prod(8090) /api/schedules = 42489ms`
  `test(8092) /api/schedules = 14ms (schedule_total=0)`

## Release Boundary

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=33d2310`
- `pm-main` 当前为 `main...origin/main [ahead 1]`
- 六个 developer workspace 当前都为 `clean_synced@33d2310`

## Version Status

- `active_version=V3`
- `lane=工程质量探测`
- `lifecycle_stage=开发实现`
- `version_transition_decision=stay(V3)`
- `baseline=document_baseline=prod=20260416-194053`
- `current_version=20260416-194053`
- `candidate_version=20260416-205559`
- `candidate_is_newer=true / drain_active=true / running_task_count=1`
- `ghost_running_detected=false / ghost_running_count=0`

当前 active 需求评估：

- `V3-R1=completed 100% / ETA 2026-04-16 / 未超时`
- `V3-R2=in_progress 99% / ETA 2026-04-16 / 未超时`
- `V3-R3=planned 35% / ETA 2026-04-18 / 未超时`
- `V3-R4=completed 100% / ETA 2026-04-16 / 未超时`
- `V3-R5=in_progress 99% / ETA 2026-04-16 / 未超时`

本轮没有需求点超时，不触发新的版本 AAR。

## Current Risk

当前 live 风险已经从“怀疑 `/api/schedules` 慢”变成了正式证据：`prod=20260416-194053` 上 current-version smoke 失败于 `schedule_list_response_too_slow`，实测 `/api/schedules=44926ms`，超过 `15000ms` 预算。风险已经被当前批次的 candidate 缓解到“待切版可验证”状态，但在 `205559` 进入 live 之前，`V3-R5` 还不能改判 completed。

## Next

1. 等 idle watcher 在空窗把 `candidate=20260416-205559` 切进 live。
2. 切版后优先复跑 current-version smoke，确认 `/api/schedules` 已回到预算内。
3. smoke 转绿后继续看 next mainline `node-sti-20260416-93d44977` 的 launch summary 是否跟随新基线滚动，用它收 `V3-R2` 的最后缺口。
