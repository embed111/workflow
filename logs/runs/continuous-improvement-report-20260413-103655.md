# Continuous Improvement Report

- executed_at: `2026-04-13T10:36:55+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260413-ae7643c2`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- active_version: `V1`
- memory_ref: `.codex/memory/2026-04/2026-04-13.md`
- preference_ref: `state/user-preferences.md`

## Summary
这轮我把 workflow schedule 的 `launch_summary` 改成读出时自动覆盖 live PM baseline 与发布边界，因此 prod 自动升级后 `/api/schedules` 和后续新 trigger 不再依赖旧快照。我补了 `verify_schedule_text_repair.py` 的 live baseline 场景，跑过定向验收和 `workflow gate`，随后提交 `3afa675`、同步本机 `../workflow_code`、刷新 `test` 并生成 `prod candidate=20260413-103306`。另外我用受支持 API 把现网两条 workflow schedule 文本先追平到 `prod=20260413-094645 / workspace_head=3afa675`，先把当前 live 漂移压住。

## Code Changes
- `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`
  读取 workflow schedule 时，统一在返回前用 live PM version 和发布边界覆盖 `launch_summary` 的动态段落；`list/detail/calendar/scan` 都会走这条修复。
- `.repository/pm-main/scripts/acceptance/verify_schedule_text_repair.py`
  新增“schedule 文本自动跟随 live prod baseline / release boundary”断言，锁住 preview、list、detail、update 四条读写路径。

## Validation
- `python .repository/pm-main/scripts/quality/check_workspace_line_budget.py --root .`
- `.repository/pm-main/.test/20260413-102749-731/report.md`
  包含 `py_compile + verify_schedule_text_repair.py + verify_pm_version_truth_source.py + verify_assignment_self_iteration_plan_reference.py`
- `.repository/pm-main/.test/20260413-102749-793/report.md`
  包含 `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `.running/control/logs/test/deploy-20260413-103306.json`
  `test gate: passed`，`prod candidate=20260413-103306`

## Live Status
- `/api/runtime-upgrade/status`
  `current_version=20260413-094645`
  `candidate_version=20260413-103306`
  `candidate_is_newer=true`
  `drain_active=true`
  `blocking_reason=running_tasks_present`
- `/api/status`
  `running_task_count=1 / queued_task_count=2`
  当前仍是 `09:39 mainline running + 10:18 mainline ready(P1) + 10:20 patrol ready(P2)`
- `/api/schedules`
  两条 workflow schedule 的当前文本已手动刷新到 `baseline=prod=20260413-094645 / workspace_head=3afa675`

## Risks And Next
- `node-sti-20260413-57813f3e / 10:18 mainline` 与 `node-sti-20260413-728880ff / 10:20 patrol` 是 refresh 前 materialize 的 ready，触发快照仍是旧 baseline；我没有在 running 槽占用期间硬删现成 ready，避免引入更高扰动。
- 下一轮优先确认 `20260413-103306` 切进 prod 后，新 materialize 的 workflow 节点是否自动携带 `prod=20260413-103306 / workspace_head=3afa675`，届时再判断 `V1-R2 / V1-R8` 是否可以继续收口。
