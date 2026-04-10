# 持续迭代报告

- 时间：`2026-04-07T21:40:29+08:00`
- ticket / node：`asg-20260407-103450-fb8ba8` / `node-sti-20260407-101db522`
- active 版本：`V1`
- 当前任务包：`V1-P0 / V1-P1`

## 本轮结论
- 本轮没有执行正式升级。`/api/runtime-upgrade/status` 显示 `prod=current_version=20260407-200414`、`candidate_version=20260407-213849`、`running_task_count=1`、`can_upgrade=false`，阻塞原因仍是“存在运行中任务，暂不可升级”。
- 本轮补上的稳定性修复是：当同一 ticket 已有别的 `running` 节点时，schedule trigger recovery worker 不再反复重拉另一个只是 `queued/ready` 的节点；同时 schedule -> assignment 桥接开始透传真实等待原因，不再统一刷成 `dispatch_requested`。
- 这条修复已经过定向验收并接进 `workflow gate`，随后 `test` 与 `prod candidate` 已刷新到 `20260407-213849`。
- 截至本轮收尾，现网主链未断：`node-sti-20260407-101db522` 仍在 `running`，`node-sti-20260407-a7fd93ea` 已由 `21:37` 保底巡检建成 `ready`，`sch-20260407-20001ab4` 仍保留 `2026-04-07T21:39:00+08:00` 的主线计划时间。

## 代码与验证
- 代码改动：
  - `src/workflow_app/server/services/schedule_service.py`
  - `src/workflow_app/server/services/schedule_assignment_bridge.py`
  - `scripts/acceptance/verify_schedule_trigger_recovery_worker.py`
  - `scripts/acceptance/run_acceptance_workflow_gate.py`
- 验证通过：
  - `python .repository/pm-main/scripts/quality/check_workspace_line_budget.py --root .repository/pm-main`
  - `python -m py_compile .repository/pm-main/src/workflow_app/server/services/schedule_assignment_bridge.py .repository/pm-main/src/workflow_app/server/services/schedule_service.py .repository/pm-main/scripts/acceptance/verify_schedule_trigger_recovery_worker.py .repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py`
  - `python .repository/pm-main/scripts/acceptance/verify_schedule_trigger_recovery_worker.py`
  - `python .repository/pm-main/scripts/acceptance/verify_runtime_upgrade_running_gate_fallback.py`
  - `python .repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py --root .repository/pm-main --host 127.0.0.1 --port 8098`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`

## 关键证据
- 定向验收：
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260407-213742.md`
- 发布证据：
  - `.running/control/logs/test/deploy-20260407-213849.json`
  - `.running/control/reports/test-gate-20260407-213849.json`
  - `.running/control/prod-candidate.json`
- 现网真相：
  - `GET /api/runtime-upgrade/status`：`candidate_version=20260407-213849`，`can_upgrade=false`
  - `GET /api/status`：`running_task_count=1`，`queued_task_count=1`
  - `GET /api/schedules`：`sch-20260407-5ef5e5c8` 已在 `2026-04-07T21:37:00+08:00` 建出 `ready` 节点 `node-sti-20260407-a7fd93ea`

## 下一步
- 主线 next：`sch-20260407-20001ab4` 当前仍记录 `2026-04-07T21:39:00+08:00`
- 保底 next：`node-sti-20260407-a7fd93ea` 已由 `2026-04-07T21:37:00+08:00` 保底唤醒建成 `ready`
- 升级 next：等待 `running_task_count=0` 且 `/api/runtime-upgrade/status.can_upgrade=true` 后，直接把 `20260407-213849` `apply` 到 `prod`
- memory_ref：`.codex/memory/2026-04/2026-04-07.md`
