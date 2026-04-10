# 持续迭代报告

## 本轮结论
- 当前 active 版本仍是 `V1`，本轮继续推进 `V1-P0 / V1-P1`。
- 我把 `[持续迭代] workflow` 的 smoke guard 从“baseline 过期直接硬拦”收成“`degraded_expired_smoke` 降级放行”，并把自迭代/保底计划模板补成必须先核 `/api/runtime-upgrade/status`，且在记忆 `next` 明确写出下一次主线/保底触发时间。
- `pm-main` 已通过 `verify_schedule_smoke_guard_scope.py`、`verify_assignment_self_iteration_plan_reference.py`、`py_compile`、行数门禁和 `workflow gate`；`test` 与 `prod candidate` 已刷新到 `20260407-193228`。
- live `prod` 当前仍在 `20260407-192451`，节点 `node-sti-20260407-e17eaf89` 的 run `arun-20260407-192706-a88570` 仍在 `running`，所以我这轮没有升级 `prod`。

## 代码与验证
- 代码触达：
- `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`
- `.repository/pm-main/src/workflow_app/server/services/schedule_text_repair.py`
- `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/assignment_self_iteration_runtime.py`
- `.repository/pm-main/scripts/acceptance/verify_schedule_smoke_guard_scope.py`
- `.repository/pm-main/scripts/acceptance/verify_assignment_self_iteration_plan_reference.py`
- 关键验证：
- `python scripts/acceptance/verify_schedule_smoke_guard_scope.py`
- `python scripts/acceptance/verify_assignment_self_iteration_plan_reference.py`
- `python -m py_compile src/workflow_app/server/services/assignment_service_parts/assignment_self_iteration_runtime.py src/workflow_app/server/services/schedule_service.py src/workflow_app/server/services/schedule_text_repair.py scripts/acceptance/verify_assignment_self_iteration_plan_reference.py scripts/acceptance/verify_schedule_smoke_guard_scope.py`
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- 证据：
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260407-193112.md`
- `.running/control/logs/test/deploy-20260407-193228.json`
- `.running/control/prod-candidate.json`

## Live 真相
- `prod` 版本：`20260407-192451`
- `prod candidate`：`20260407-193228`
- 当前运行节点：`node-sti-20260407-e17eaf89`
- 当前运行批次：`arun-20260407-192706-a88570`
- 主线/保底下一次入口：`2026-04-07T19:57:00+08:00` / `2026-04-07T20:27:00+08:00`
- 需要继续盯的一条现场风险：`/api/runtime-upgrade/status` 当前给出 `can_upgrade=true`、`running_task_count=0`，但 `/api/status` 同时仍显示 `running_task_count=1`；这说明升级前真相源还没完全一致，本轮只刷新候选、不直接升级 `prod`。

## 下一步
- 等 `node-sti-20260407-e17eaf89` 收尾后，先双检 `/api/status` 与 `/api/runtime-upgrade/status` 的运行数是否一致；只有两边都确认空闲，再决定是否把 `prod` 升到 `20260407-193228`。
- 若 `19:57` 主线或 `20:27` 保底入口在此之前出现 handoff 异常，继续按 `V1-P0 / V1-P1` 优先级收口，不跳版。
- memory_ref: `.codex/memory/2026-04/2026-04-07.md`
