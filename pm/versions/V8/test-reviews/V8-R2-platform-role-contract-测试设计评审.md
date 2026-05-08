# V8-R2 platform role contract 测试设计评审

- version: `V8`
- requirement_id: `V8-R2`
- reviewed_at: `2026-04-22T23:25:21+08:00`
- owner: `workflow(pm)`

## 1. 测试目标
- 证明项目级 `runtime-policy` 写回后，`project summary` 的关键字段会在 live `/api/dashboard` 与 `/api/status` 同步反映。
- 证明 `restore_default=true` 会把 `next_handoff_interval_minutes / next_handoff_interval_override_source / next_handoff_interval_effective_after_run` 一起恢复，不留下 stale cadence 痕迹。
- 保持 `controller cadence` 的消费验证继续由现有 self-iteration probe 覆盖，不把两条链路混成一个大而含糊的回归脚本。

## 2. 用例分层
- live targeted regression：
  - `verify_project_runtime_policy_live_regression.py --host 127.0.0.1 --port 8092 --expected-version 20260422-223441`
  - `verify_project_runtime_policy_live_regression.py --host 127.0.0.1 --port 8092 --expected-version 20260422-232042`
  - 证明当前 `test` 上 `project runtime-policy writeback -> summary readback` 在部署前后都成立。
- isolated gate：
  - `run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - 通过 `WORKFLOW_GATE_FORCE_PROJECT_FIXTURE_BOOTSTRAP=1` 在隔离 runtime 里 bootstrap 同一条 fixture project，并把 probe 正式接进 `workflow gate`。
- cadence consumption：
  - `verify_assignment_self_iteration_project_handoff_interval.py`
  - `verify_assignment_project_controller_self_iteration_schedule.py`
  - 继续覆盖“写入的 cadence 会不会被 self-iteration 真正消费”。

## 3. 关键断言
- `project_board_ref=projects/<project_id>/board`
- `runtime_policy_ref=projects/<project_id>/runtime-policy`
- bootstrap 后：`default=35 / next=35 / override=default / effective_after_run=''`
- 手动覆盖后：`next=42 / override=manual / effective_after_run=''`
- 恢复默认后：`next=35 / override=default / effective_after_run=''`
- 上述断言在 `/api/projects`、`/api/dashboard.project_task_summary`、`/api/status.project_task_summary` 三处都同时成立。

## 4. 不覆盖项
- 不在本轮对 `prod` 直接写 runtime-policy。
- 不把 `project ops` quiet-ready landing、版本信息页签、project output 摘要等 UI 语义混进这条 cadence read/write probe。
- 不把 controller cadence 的“下一轮实际消费”塞回这条 live regression；那部分继续交给 self-iteration probe。

## 5. 评审结论
- `pass`
- 当前测试设计足以支撑 `V8-R2` 的 read/write live evidence；后续只要继续补 controller cadence live chain 与 demo 准入，就可以把 R2 从 `developing` 继续推进到更接近退出门槛。
