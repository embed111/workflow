# 持续迭代报告

- 时间：`2026-04-07T22:00:03+08:00`
- ticket / node：`asg-20260407-103450-fb8ba8` / `node-sti-20260407-cb9fc7de`
- active 版本：`V1`
- 当前任务包：`V1-P0 / V1-P1`

## 本轮结论
- 本轮没有执行正式升级。`/api/runtime-upgrade/status` 显示 `prod=current_version=20260407-200414`、`candidate_version=20260407-215842`、`running_task_count=1`、`can_upgrade=false`；当前运行节点仍是 `node-sti-20260407-cb9fc7de`，所以现在不满足 `apply` 条件。
- 我先把 live 现场钉实了：旧版 `prod` 在 `21:39:42~21:51:45` 之间，针对 `node-sti-20260407-cb9fc7de` 反复刷 `dispatch_requested -> trigger_resume_requested -> recover_assignment_node`，直到当前 running 槽释放后才真正 dispatch。这个现象和 `pm-main` 里的 busy-slot/recovery 修复完全对上。
- 这轮正式收口的补丁有两块：一是 `runtime_upgrade.py` 的 running gate 改成和 dashboard 共用 workboard fallback；二是 `schedule_service.py / schedule_assignment_bridge.py` 让 recovery worker 在同 ticket 已有别的 `running` 节点时安静等待，并把真实等待原因透传到 schedule dispatch 结果。
- 这组修复已经提交为 `a8015bd fix(workflow): quiet queued trigger recovery churn`，推回 `workflow_code/main`，并把 `test`/`prod candidate` 刷新到 `20260407-215842`。

## 代码与验证
- 代码改动：
  - `.repository/pm-main/src/workflow_app/server/api/runtime_upgrade.py`
  - `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`
  - `.repository/pm-main/src/workflow_app/server/services/schedule_assignment_bridge.py`
  - `.repository/pm-main/scripts/acceptance/verify_runtime_upgrade_running_gate_fallback.py`
  - `.repository/pm-main/scripts/acceptance/verify_schedule_trigger_recovery_worker.py`
  - `.repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py`
- 验证通过：
  - `python scripts/quality/check_workspace_line_budget.py --root .`
  - `python -m py_compile scripts/acceptance/run_acceptance_workflow_gate.py scripts/acceptance/verify_schedule_trigger_recovery_worker.py scripts/acceptance/verify_runtime_upgrade_running_gate_fallback.py src/workflow_app/server/api/runtime_upgrade.py src/workflow_app/server/services/schedule_assignment_bridge.py src/workflow_app/server/services/schedule_service.py`
  - `python scripts/acceptance/verify_runtime_upgrade_running_gate_fallback.py`
  - `python scripts/acceptance/verify_schedule_trigger_recovery_worker.py`
  - `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`
- 当前 `workflow gate` 总结果仍是 `passed`，但报告里保留了一个与本轮补丁无关的 `developer_workspace_bootstrap=workspace_not_git_repo` 非阻塞告警；这条残留更接近 `V1-P2` 的工作区 bootstrap 口径，不阻塞本轮 `V1-P0 / V1-P1` 候选刷新。

## 关键证据
- live 现场：
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-cb9fc7de.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-215225-c22486/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-215225-c22486/events.log`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
  - `.running/control/runtime/prod/logs/events/schedules.jsonl`
- 验收与发布：
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260407-215637.md`
  - `.running/control/logs/test/deploy-20260407-215842.json`
  - `.running/control/reports/test-gate-20260407-215842.json`
  - `.running/control/prod-candidate.json`
- 版本与升级真相：
  - `GET /api/runtime-upgrade/status`：`candidate_version=20260407-215842`、`running_task_count=1`、`can_upgrade=false`
  - `GET /api/status`：`node-sti-20260407-cb9fc7de` 当前仍在 `running`
  - `GET /api/schedules`：主线/保底 next 仍为 `2026-04-07T22:08:00+08:00 / 2026-04-07T22:38:00+08:00`

## 下一步
- 主线 next：`sch-20260407-20001ab4 -> 2026-04-07T22:08:00+08:00`
- 保底 next：`sch-20260407-5ef5e5c8 -> 2026-04-07T22:38:00+08:00`
- 升级 next：等 `running_task_count=0` 且 `/api/runtime-upgrade/status.can_upgrade=true` 后，直接把 `20260407-215842` `apply` 到 `prod`
- memory_ref：`.codex/memory/2026-04/2026-04-07.md`
