# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`。
- 本轮主推进明确记成 `功能开发 / 当前需求开发 / V5-R4 + V5-R1`；我把第二项目的 `member route` 首刀正式落成了代码与 probe。
- 这刀的核心不是再补一个文档字段，而是新增显式 `project_binding_mode=auto`：调用方明确选择 auto 时，assignment node 能按角色归属自动补 `project_id/project_ref`；默认模式继续保持空绑定，无路由时直接 fail-closed。

## 取舍
- 我没有重复上一轮的 `schedule_service` 拆分，也没有继续把第二项目 blocker 停在“project_id/project_ref 已有首刀”那一层。当前更值钱的是把 `member route` 从口头 blocker 推成真实入口。
- 我也没有把 auto 项目绑定做成默认行为。`workflow_devmate / workflow_testmate` 仍然会承接大量通用平台任务，若默认自动吸进 `project-comics-smoke`，副作用会大于收益；所以这轮只在显式 `project_binding_mode=auto` 时开启，并且对无路由场景 fail-closed。
- 当前我仍不把这轮误报成可发布批次。`pm-main` 已重新进入 `ahead_dirty`，而且 `Mandatory Gate` 仍是红灯；这轮没有 clean push 条件。

## 下一动作
- 先把当前 dirty batch 切清，把 `workflow_gate_probe_registry.py / graph_model_and_payloads.py / project_registry_service.py` 和新 probe 形成可解释的小批次，再决定是否存在可独立收口的小批次。
- 只要当前版本还不切，我下一步优先补两类 live 证据之一：`controller cadence closure` 的 finalize 后消费证据，或一条真实 `project-scoped member task`，证明这条 member route 已经从 probe 走到 live。
- 在 `Mandatory Gate` 没转绿之前，我不会把“member route 首刀已落地”误说成“第二项目已经可安全切版运营”。

## 本轮推进
- 更新 `.repository/pm-main/src/workflow_app/server/services/project_registry_service.py`：
  - 新增 `find_projects_by_member_role()`
  - 新增 `resolve_role_project_binding()`
  - 固化 `controller route -> non-builtin member route -> fail-closed` 的归属解析顺序
- 更新 `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/graph_model_and_payloads.py`：
  - 为 assignment node 新增显式 `project_binding_mode=auto`
  - auto 模式下按角色归属解析项目绑定
  - 默认模式保持显式 `project_id` 优先和空绑定行为
- 新增 `.repository/pm-main/scripts/acceptance/verify_assignment_project_binding_auto.py`
- 更新 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`

## 当前版本更新
- `V5-R1 = in_progress / 45% / 最近更新=2026-04-19T22:07:35+08:00 / eta=2026-04-21 / 未超时`
- `V5-R2 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R3 = in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`
- `V5-R4 = in_progress / 92% / 最近更新=2026-04-19T22:07:35+08:00 / eta=2026-04-21 / 未超时`
- `V5-R5 = in_progress / 60% / 最近更新=2026-04-19T21:41:32+08:00 / eta=2026-04-20 / 未超时`
- 本轮无超时需求，不新增 AAR。
- 当前切版 blocker 收口为：`member route` 已落地显式 auto 首刀，但 `controller cadence closure` 仍缺 live finalize 消费证据，真实 `project-scoped member task` 证据仍未形成，且 `V5-R5` 的 `Mandatory Gate` 仍为 false。

## 发布边界
- `root_sync_state=ahead_dirty`
- `ahead_count=0`
- `dirty_tracked_count=3 / untracked_count=1`
- `workspace_head=code_root_head=2d26364`
- `push_block_reason=workspace_dirty_changes_present + mandatory_gate_fail_closed`
- `next_push_batch=gate/acceptance 收口；先把本轮 member-route 代码切片和新 probe 形成可解释的小批次`

## 验证
- `.repository/pm-main/.test/20260419-220529-673/report.md`
- `.repository/pm-main/.test/20260419-220545-488/report.md`
- `.repository/pm-main/.test/20260419-220608-686/report.md`
- `.repository/pm-main/.test/20260419-220629-580/report.md`
- `.repository/pm-main/.test/20260419-220643-624/report.md`
- `.repository/pm-main/.test/20260419-221335-389/report.md`
- `verify_assignment_project_binding_auto.py`：通过，确认“默认不自动绑定 / auto 成员路由成功 / 无路由 fail-closed”
- `verify_project_bootstrap_summary.py`：通过
- `verify_assignment_status_detail_default_node.py`：通过
- `verify_v5_activation_gate.py`：通过，确认本轮把 member-route 首刀写回版本计划和矩阵后，没有破坏 `V5 active` 的 gate 口径
- `python scripts/quality/check_workspace_line_budget.py --root .`：失败；`blocking_offender_count=39`，Mandatory Gate 仍是 fail-closed

## Live
- 当前 live 继续成立：`running_task_count=1 / queued_task_count=2 / active_agent_count=1`。
- 当前 `workflow` mainline 仍在运行，下一条 mainline 已是 `ready`，patrol 也仍有下一棒 `ready/future` 出口。

## 证据
- `preference_ref: state/user-preferences.md`
- `memory_ref: .codex/memory/2026-04/2026-04-19.md`
