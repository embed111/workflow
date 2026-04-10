# continuous-improvement-report

- report_time: `2026-04-07T20:48:15+08:00`
- active_version: `V1`
- active_task_pack: `V1-P0 / V1-P1`
- preference_ref: `state/user-preferences.md`
- delta_observation: `runtime_upgrade` 的 running gate 已改成复用 dashboard/workboard fallback，`prod candidate` 已刷新到 `20260407-204710`，但 live `prod` 仍因 `running_task_count=1` 暂不可升级
- delta_validation: `2026-04-07T21:07:00+08:00` 保底巡检时继续检查 `/api/runtime-upgrade/status` 是否转为 `can_upgrade=true`，并确认 future 主线入口是否已续挂
- memory_ref: `.codex/memory/2026-04/2026-04-07.md`

## 本轮结论

- 我把 `V1-P0 / V1-P1` 里“正式升级前运行真相不一致”这条问题继续收口：`runtime_upgrade.py` 的 running gate 现在会复用 dashboard/workboard fallback，不再只盯原始 assignment runtime metrics。
- 我新增了 `scripts/acceptance/verify_runtime_upgrade_running_gate_fallback.py`，并把这条校验接进 `workflow gate`，让这轮修复不只是一条单次定向验证，而是进入主门禁回归。
- 我已完成 `check_workspace_line_budget`、`py_compile`、定向验收、`workflow gate`、`test` 部署，并把 `prod candidate` 刷新到 `20260407-204710`。
- 当前 live `prod` 仍在 `20260407-200414`，`/api/runtime-upgrade/status` 已显示 `candidate_is_newer=true`，但因为当前还有 1 条真实运行中任务，所以 `running_task_count=1`、`can_upgrade=false`，本轮不直接调用 `/api/runtime-upgrade/apply`。
- 7x24 连续性当前未断：`pm持续唤醒 - workflow 主线巡检` 的保底入口 `sch-20260407-5ef5e5c8` 仍保留 `2026-04-07T21:07:00+08:00` 的 future trigger。

## 代码与验证

- 代码改动：
  - `.repository/pm-main/src/workflow_app/server/api/runtime_upgrade.py`
  - `.repository/pm-main/scripts/acceptance/verify_runtime_upgrade_running_gate_fallback.py`
  - `.repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py`
- 治理与经验同步：
  - `docs/workflow/governance/PM版本推进计划.md`
  - `.codex/experience/runtime-upgrade-and-agent-monitoring.md`
  - `.codex/experience/index.md`
- 验证证据：
  - 行数门禁：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - 定向验收：直接执行 `python scripts/acceptance/verify_runtime_upgrade_running_gate_fallback.py`，返回 `running_task_count=1 / agent_call_count=1`
  - workflow gate：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260407-204604.md`
  - test 部署日志：`.running/control/logs/test/deploy-20260407-204710.json`
  - test gate 证据：`.running/control/reports/test-gate-20260407-204710.json`
  - prod candidate：`.running/control/prod-candidate.json`

## 运行态真相

- `prod` 当前版本：`20260407-200414`
- 最新 candidate：`20260407-204710`
- `candidate_is_newer`: `true`
- `running_task_count`: `1`
- `can_upgrade`: `false`
- 当前主线节点：`node-sti-20260407-b90fd5d1`
- 当前主线计划 future：尚未挂出新的 `[持续迭代] workflow` future trigger
- 当前保底计划 future：`2026-04-07T21:07:00+08:00`

## 下一步

- 下一次保底观察点：`2026-04-07T21:07:00+08:00`
- 下一次主线观察点：优先在当前 `node-sti-20260407-b90fd5d1` 完成后检查是否自动续挂；若仍无 future 主线入口，则由 `21:07` 保底巡检补链。
- 下一轮若 `/api/runtime-upgrade/status` 变为 `can_upgrade=true` 且 `running_task_count=0`，应直接把 `20260407-204710` 应用到 `prod`。
- 本轮未额外挂新的 helper 任务：当前问题已经在 `pm-main` 最小改动面内收口，原有 `V1-P1 / V1-P2 / V1-P3 / V1-P4` 图内节点继续保留历史证据。

## 风险与备注

- `workspace line budget` 的 hard gate 通过，但 advisory/refactor trigger 仍命中；当前属于已知长期债，不阻塞本轮 `test`/candidate 刷新。
- `run_acceptance_workflow_gate.py` 目前自身仍超过 1000 行，已继续触发行数重构提示；这不是本轮阻塞项，但后续仍应拆分。
