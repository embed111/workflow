# V8-R2 平台角色 contract 读写与 cadence 方案评审

- version: `V8`
- requirement_id: `V8-R2`
- reviewed_at: `2026-04-22T23:25:21+08:00`
- owner: `workflow(pm)`
- collaborators: `workflow_devmate / workflow_qualitymate / workflow_testmate`

## 1. 背景
- `409ae60` 已经把 `project_task_summary` 的 `project_type / project_goal / project_board_ref / runtime_policy_ref / member_role_ids` 补进读面，并让 `verify_project_task_summary.py` 与 `verify_project_ops_live_regression.py` 在 gate 和 live regression 上转绿。
- 当前真正还缺的一刀，不是再补一轮 quiet-ready 首页判断，而是把 `runtime-policy` 的 live writeback 做成 dedicated probe，证明“项目运维参数写入 -> `/api/dashboard` / `/api/status` 项目摘要读回 -> restore_default 清理”这条链路稳定成立。

## 2. 方案判断
- 继续复用现有 `POST /api/projects/{project_id}/runtime-policy/next-handoff-interval`，不新开第二套 cadence API。
- 单独新增 `verify_project_runtime_policy_live_regression.py`，而不是继续把这条读写链塞进 `verify_project_ops_live_regression.py`：
  - 先 bootstrap 固定 fixture `project-runtime-policy-live`；
  - 校验 `default_handoff_interval_minutes=35 / next_handoff_interval_minutes=35 / override_source=default / effective_after_run=''`；
  - 再把 `next_handoff_interval_minutes` 改成 `42`，验证 `project_board_ref / runtime_policy_ref / default/next interval / override/effective_after` 同时在 `/api/projects`、`/api/dashboard.project_task_summary`、`/api/status.project_task_summary` 三处读回；
  - 最后执行 `restore_default=true`，确认读面回到默认值且不残留 stale `effective_after_run`。
- `controller cadence` 的“写入后被下一轮 self-iteration 消费”继续由现有 `verify_assignment_self_iteration_project_handoff_interval.py` 与 `verify_assignment_project_controller_self_iteration_schedule.py` 负责，不把 live writeback probe 混成一条含糊大用例。

## 3. 备选方案取舍
- 否决：把 writeback 回归继续并进 `verify_project_ops_live_regression.py`
  - quiet-ready 首页判断与 runtime-policy 写回是两类不同合同，继续混在一条 live probe 里，失败后无法快速判断是 landing 读面坏了，还是 cadence 写回坏了。
- 否决：直接对 `prod` 做 live writeback
  - 当前 `prod` 仍有 running/queued 主线节点，本轮目标是最小扰动推进，不应该为了补 R2 probe 去改 live 底座 cadence。

## 4. 风险与护栏
- 风险：fixture project 若在非 test/gate 环境被误 bootstrap，会污染真实项目列表。
- 护栏：
  - 只有 `runtime environment=test` 或 `WORKFLOW_GATE_FORCE_PROJECT_FIXTURE_BOOTSTRAP=1` 时才自动 bootstrap fixture。
  - probe 固定使用稳定 `project_id`，不在 test runtime 里无限堆新项目。
- 风险：只验证 writeback，不验证下一轮 cadence 真消费，可能误把“写得进、但用不上”当成闭环。
- 护栏：
  - 方案明确把 live writeback 与 controller cadence 消费拆成两条 probe，同轮都保留在 `V8-R2` 的证据集里。

## 5. 验证口径
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/verify_project_runtime_policy_live_regression.py --host 127.0.0.1 --port 8092 --expected-version 20260422-223441`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_test_workflow_env.ps1`
- `python scripts/acceptance/verify_project_runtime_policy_live_regression.py --host 127.0.0.1 --port 8092 --expected-version 20260422-232042`

## 6. 评审结论
- `go`
- 这条方案允许我把 `V8-R2` 从“还缺 dedicated runtime-policy live writeback proof”的状态推进到“读写 probe 已成立，剩余缺口只剩 controller cadence live chain 与 demo 准入”。
