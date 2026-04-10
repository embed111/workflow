# 持续迭代报告（2026-04-08 15:18）

## 本轮结论
- 当前 active 版本仍是 `V1`，最高优先任务包仍为 `V1-P0 / V1-P1`。
- 我已在 `.repository/pm-main` 为 assignment runtime 补上 `stream disconnected before completion` 的瞬时故障识别、`stdout/stderr` 错误提取与“无最终结构化结果时自动重试”收口，目标是把 `Codex` 流断开从直接失败收成可恢复重试。
- live `prod` 截至 `2026-04-08T15:18:00+08:00` 已在 `20260408-143350`；当前 `node-sti-20260408-fbd8c8bc` 仍占用 running 槽，`/api/runtime-upgrade/status` 与带 exclusion 的复核都显示 `candidate_is_newer=false`，排除本节点后进一步收口成 `blocking_reason=no_candidate / can_upgrade=false`，所以本轮不执行 `apply`。
- 7x24 接力当前未断，但主线还没有预排下一跳：`sch-20260407-20001ab4` 当前 `future_triggers=[]`，说明下一次主线接力仍待当前 `14:59` 节点 finalize 后自动续挂；已经明确保住的未来入口只剩保底 `sch-20260407-5ef5e5c8 -> 2026-04-08T15:29:00+08:00`。

## 本轮交付
- 代码修复已落在：
  - `.repository/pm-main/src/workflow_app/server/services/codex_failure_contract.py`
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_runtime.py`
  - `.repository/pm-main/scripts/acceptance/verify_assignment_transient_startup_retry.py`
  - `.repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py`
- 文档与记忆已同步到：
  - `docs/workflow/governance/PM版本推进计划.md`
  - `.codex/experience/runtime-upgrade-and-agent-monitoring.md`
  - `state/session-snapshot.md`
  - `.codex/memory/2026-04/2026-04-08.md`
- 本轮不刷新 `test/prod candidate`：`.repository/pm-main` 当前同时存在我未接管的并行脏改动 `graph_model_and_payloads.py`、`running_state_reconciliation.py`、`verify_assignment_provider_liveness_guard.py` 与 `logs/`，直接发候选会把不同来源改动混进同一版。

## 验证证据
- `python scripts/quality/check_workspace_line_budget.py --root .`
  - 证据：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `python -m py_compile src/workflow_app/server/services/codex_failure_contract.py src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_runtime.py scripts/acceptance/verify_assignment_transient_startup_retry.py scripts/acceptance/run_acceptance_workflow_gate.py`
  - 结果：通过
- `python scripts/acceptance/verify_assignment_transient_startup_retry.py`
  - 结果：`startup_only`、`interrupt`、`stream_disconnect` 均通过
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - 证据：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-151040.md`
- live 现场：
  - `GET /api/status`
  - `GET /api/runtime-upgrade/status`
  - `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-fbd8c8bc`
  - `GET /api/schedules/sch-20260407-20001ab4`
  - `GET /api/schedules/sch-20260407-5ef5e5c8`
  - 当前 run 证据：`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-145913-9021f1/run.json`

## 风险与下一步
- 当前修复还只在 `.repository/pm-main` 本地验证通过，尚未刷新成新的 `test/prod candidate`。
- 我这轮没有新挂 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 任务；当前最高优先仍是先把 transient stream disconnect retry 收进干净候选，再看是否需要拆分后续质量/回归协作。
- 主线 next: 当前没有预先排好的下一次主线时间；我需要盯 `node-sti-20260408-fbd8c8bc` 收尾后是否自动续挂下一次 `[持续迭代] workflow`。
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-08T15:29:00+08:00`。如果当前主线收尾后没有自动补回 future/ready，这条保底会负责补链。
- 候选 next: 等并行脏改动完成归属或收口后，我再基于干净工作树重跑 `workflow gate`，随后刷新 `test` 与 `prod candidate`。
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
