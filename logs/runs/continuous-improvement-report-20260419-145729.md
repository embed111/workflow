# continuous-improvement-report

## 判断
- version_transition_decision=`stay(V4)`
- 当前最高价值推进：把 `V5-R4` 的项目级 `next_handoff_interval` 接到 self-iteration `scheduler consumption`，并收口到 `pm-main/workflow_code@cec137b`、`test / prod candidate=20260419-144557`。
- 当前不切 `V5`：`V5-R1 / V5-R2 / V5-R3` 仍只有计划级 activation gate；`V5-R4` 虽已具备对象/API/UI/probe/candidate/scheduler-consumption 证据，但还缺 `second-project bootstrap smoke / starter route` 的真实 running 证据，以及切版前 `go-no-go` 复核。
- 下一动作：先等当前 running mainline 释放空窗，让 idle watcher 消费 `candidate=20260419-144557`；若下轮仍未升级，我优先在 live prod 补 `project handoff smoke`，再把 `second-project starter route` 切给 helper 或自己落最小实现。

## 推进结果
- 代码/验收：新增 `verify_assignment_self_iteration_project_handoff_interval.py`；更新 `project_registry_service.py` 和 `assignment_self_iteration_runtime.py`，让手工覆盖的项目级 `next_handoff_interval` 会改变下一轮 self-iteration `next_trigger_at`，并回写 `next_handoff_interval_effective_after_run`。
- 版本门禁：同步追平 `verify_v5_activation_gate.py`、`verify_v5_r4_project_bootstrap_activation_slice.py` 和 `workflow_gate_probe_registry.py`，让 `V5-R4` blocker 改成 `starter route/go-no-go`，不再停在 `scheduler consumption`。
- 发布边界：`pm-main` 已提交 `cec137b`，`../workflow_code` 已 fast-forward 到同一提交；`test` 已部署并刷新 `prod candidate=20260419-144557`；6 个 developer workspace 已回到 `clean_synced@cec137b`。
- 当前 active 需求状态：
- `V4-R1=completed / 100% / 最近更新=2026-04-19T03:56:33+08:00 / eta=2026-04-19 / 未超时`
- `V4-R2=completed / 100% / 最近更新=2026-04-19T04:46:32+08:00 / eta=2026-04-19 / 未超时`
- `V4-R3=completed / 100% / 最近更新=2026-04-19T01:26:30+08:00 / eta=2026-04-19 / 未超时`
- `V4-R4=completed / 100% / 最近更新=2026-04-17 / eta=2026-04-17 / 未超时`
- `V4-R5=completed / 100% / 最近更新=2026-04-19T10:20:10+08:00 / eta=2026-04-19 / 未超时`

## 验证与真相
- 验证通过：`WORKSPACE_LINE_BUDGET_REPORT.md`、`verify_assignment_self_iteration_success_delay.py`、`verify_assignment_self_iteration_project_handoff_interval.py`、`verify_v5_activation_gate.py`、`verify_v5_r4_project_bootstrap_activation_slice.py`、完整 `workflow gate`。
- 关键证据：
- `.repository/pm-main/.test/20260419-143959-466/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-144417.md`
- `.running/control/logs/test/deploy-20260419-144557.json`
- 快照写回：我尝试运行 `refresh_pm_current_version_snapshot.py` 追平 `PM当前版本计划.md / V4 版本计划.md`，但它这拍仍炸在 `plan_prod_status_current_shape`；本轮已手工把版本现场回写到 `prod=20260419-134702 / candidate=20260419-144557` 的 live 真相。
- 发布边界：
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=cec137b`
- `push_block_reason=-`
- `next_push_batch=等待当前 running mainline 释放空窗，让 idle watcher 消费 candidate=20260419-144557；若下轮仍未升级，则优先在 live prod 补 project handoff smoke，并把 second-project bootstrap smoke/starter route 切成下一刀实现或 helper 任务`
- live：
- `prod current_version=20260419-134702 / candidate_version=20260419-144557 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`
- `test current_version=20260419-144557 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- 当前出口：`node-sti-20260419-251eda98` 正在 `running`，`node-sti-20260419-e24e37e2` 与 `node-sti-20260419-3646dd50` 为 `ready`

## 留痕
- preference_ref: `state/user-preferences.md`
- delta_observation: 我这轮把 `V5-R4` 的项目级 handoff interval 从 UI/对象字段推进成了真实 self-iteration scheduler consumption，并把 `V5` blocker 从“缺 scheduler consumption”改写成“缺 second-project starter route/go-no-go”。
- delta_validation: 下一轮优先验证 `candidate=20260419-144557` 升到 live 后的 `project handoff smoke`，再把 `second-project bootstrap smoke / starter route` 推成第一条真实 running 证据。
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`
