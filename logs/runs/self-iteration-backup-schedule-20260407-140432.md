# 自迭代补链验收 20260407-140432

- preference_ref: state/user-preferences.md
- memory_ref: .codex/memory/2026-04/2026-04-07.md
- delta_observation: 当前 `V1-P0 / V1-P1` 的最高优先缺口已经从“prod 端口漂移”收窄到“`[持续迭代] workflow` 被 `smoke guard` 或 stale running 收口时，7x24 主链是否还会自动保住下一轮入口”。
- delta_validation: 我已核对 prod 的 `/healthz`、`/api/status`、`/api/dashboard`、`/api/schedules/sch-20260407-4c67199b` 与 `.running/control/envs/prod.json` / `.running/control/instances/prod.json`，随后在 `.repository/pm-main` 里补跑 `verify_self_iteration_backup_schedule_on_smoke_block.py`、`verify_assignment_stale_running_self_iteration.py` 和 `workflow gate`。

## 结论

- 结果：通过
- 任务包：`V1-P0 / V1-P1`
- 收口点：当 `[持续迭代] workflow` 被 `smoke guard` 或“运行句柄缺失”收口时，系统仍会自动保留未来可执行入口，不再只靠已有的一次性计划碰运气。
- 当前 prod 事实：`20260407-121719`，`127.0.0.1:8090`，`healthz/status/dashboard` 正常返回；`sch-20260407-4c67199b` 仍保留 `2026-04-07T14:11:00+08:00` 的 future trigger。

## 验证

1. `python scripts/quality/check_workspace_line_budget.py --root .`
   - 输出：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
2. `python -m py_compile src/workflow_app/server/services/assignment_service_parts/assignment_self_iteration_runtime.py src/workflow_app/server/services/schedule_service.py scripts/acceptance/verify_assignment_stale_running_self_iteration.py scripts/acceptance/verify_self_iteration_backup_schedule_on_smoke_block.py`
   - 结果：通过
3. `python scripts/acceptance/verify_self_iteration_backup_schedule_on_smoke_block.py`
   - 结果：通过
   - 关键证据：`smoke baseline report missing` 时自动补出 `backup_schedule_id=sch-20260407-09009c68`，`backup_next_trigger_at=2026-04-07T14:29:00+08:00`
4. `python scripts/acceptance/verify_assignment_stale_running_self_iteration.py`
   - 结果：通过
   - 关键证据：stale running 节点被收成 `failed` 后，同时保留新的 `[持续迭代] workflow` 与 `pm持续唤醒 - workflow 主线巡检`
5. `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
   - 输出：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260407-140312.md`
   - 备注：脚本退出 `0`，但报告中仍保留一个与本轮补链无关的 `developer_workspace_bootstrap=workspace_dirty` 子项
6. `Invoke-RestMethod http://127.0.0.1:8090/healthz`
   - 结果：`ok=true`
7. `Invoke-RestMethod http://127.0.0.1:8090/api/status`
   - 结果：`environment=prod`，`running_task_count=1`，`assignment_running_task_count=1`
8. `Invoke-RestMethod http://127.0.0.1:8090/api/schedules/sch-20260407-4c67199b`
   - 结果：`last_result_status=running`，`future_triggers[0].planned_trigger_at=2026-04-07T14:11:00+08:00`

## 触达文件

- `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/assignment_self_iteration_runtime.py`
- `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`
- `.repository/pm-main/scripts/acceptance/verify_assignment_stale_running_self_iteration.py`
- `.repository/pm-main/scripts/acceptance/verify_self_iteration_backup_schedule_on_smoke_block.py`
- `docs/workflow/governance/PM版本推进计划.md`

## 风险与下一步

- 这组补链修复目前已在 `pm-main` 工作区通过定向验收和 `workflow gate`，但还没有继续走 `test / prod candidate` 链路。
- `workflow gate` 报告里仍有一个隔离 fixture 的 `workspace_dirty` 提示，它不影响这次自迭代补链逻辑，但后续如果把整轮门禁当发布依据，还需要单独清掉这项噪声。
- 当前 `prod` 虽然已经有未来入口，但页面与运行文件之间的多真相源一致性仍需继续回归，尤其是 `dashboard / status-detail / run.json` 的口径一致性。
