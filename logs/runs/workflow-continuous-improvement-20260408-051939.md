# Continuous Improvement Report

- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-59614e1a`
- generated_at: `2026-04-08T05:19:39+08:00`

## 本轮结论
- 我继续按 `V1` 活跃版本推进，优先收了 `V1-P1` 的 schedule 真相分叉：当 `once` 计划已经终态且没有未来触发时，现在会自动从 active preview/count 里退场，并同步修正 `schedule_plans.enabled / last_result_*`，避免旧计划继续混进 dashboard/schedules 的活跃视图。
- 代码已在 `pm-main` 提交为 `11f7da2 fix(workflow): retire exhausted once schedules` 并推回 `workflow_code/main`；`test` 与 `prod candidate` 已刷新到 `20260408-051809`。
- 当前 live `prod` 仍是 `20260407-200414`。截至 `2026-04-08T05:19:39+08:00`，`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`，当前 running 节点是 `node-sti-20260408-59614e1a`，所以本轮未执行 `apply`。

## 关键改动
- `src/workflow_app/server/services/schedule_service.py`
  - 新增 exhausted `once` plan repair：读取最新 trigger 已终态且 `next_trigger_at` 为空时，自动回写 `schedule_plans.enabled=0`，并同步修正 `last_trigger_at / last_result_status / last_result_ticket_id / last_result_node_id`。
  - `list_schedule_preview()` 改成基于修正后的 active 计划重新过滤和计数，避免已耗尽的旧计划继续占据 dashboard / schedule preview。
  - `get_schedule_detail()` 与 `list_schedules()` 现在共享同一份计划修正逻辑，避免 detail / list / preview 口径分叉。
- `scripts/acceptance/verify_schedule_exhausted_once_plan_repair.py`
  - 新增定向验收，覆盖“终态 `once` 计划自动退场 + preview/count 收口 + 数据库行回写”。
- `scripts/acceptance/run_acceptance_workflow_gate.py`
  - 把新 probe 接进 `workflow gate`，避免这个真相分叉日后回归。

## 验证
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python -m py_compile src/workflow_app/server/services/schedule_service.py scripts/acceptance/verify_schedule_exhausted_once_plan_repair.py scripts/acceptance/run_acceptance_workflow_gate.py`
- `python scripts/acceptance/verify_schedule_trigger_terminal_status_repair.py`
- `python scripts/acceptance/verify_schedule_exhausted_once_plan_repair.py`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `git -C .repository/pm-main push origin main`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`
- `GET /api/runtime-upgrade/status`
- `GET /api/status`
- `GET /api/schedules/sch-20260407-5ef5e5c8`

## 证据路径
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-051644.md`
- `.running/control/logs/test/deploy-20260408-051809.json`
- `.running/control/prod-candidate.json`
- `logs/runs/workflow-continuous-improvement-20260408-051939.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `.codex/memory/2026-04/2026-04-08.md`

## 下一步
- 主线 next: 当前运行节点 `node-sti-20260408-59614e1a` 收尾后，立即复核 `/api/runtime-upgrade/status`；若 `running_task_count=0` 且 `can_upgrade=true`，优先直接 `apply 20260408-051809`。
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-08T05:36:00+08:00`
- 升级后验证 next: 复核 live `schedule_workboard_preview / schedule_total` 是否从旧版的 `4` 收口到真实 active 的主线 + 保底 `2` 条，并确认旧 `sch-20260407-4c67199b / sch-20260407-d7b8f1d6` 不再混进 active 预览。
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
