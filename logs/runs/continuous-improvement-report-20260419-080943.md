# [持续迭代] workflow / 2026-04-19 07:25:00

## 判断
- `version_transition_decision=stay(V4)`。我这轮不切 `V5`，因为 `next_activation_ready=false`，而 `V4-R5` 还缺 `prod=20260419-080601` 下的 live 连续对话抽样。
- 当前最高价值动作不是再重复修 prompt rebuild，而是把 workflow schedule 节点在 dispatch 时的 refreshed `node_goal` 正式写回 node snapshot；否则 provider prompt 虽然已经是新基线，`status-detail.selected_node.node_goal` 仍会继续显示旧的 baseline / release-boundary 真相。

## 取舍
- 我没有重复上一轮继续修 `get_schedule_detail()` 的嵌套 payload；那层已经让 provider prompt 吃到 live schedule detail。真正还会误导版本判断和人工排障的，是 node snapshot 仍停在旧 `node_goal`。
- 我没有补派新的 helper 实现任务；当前 blocker 直接依赖 `prod` 切到 `20260419-080601` 后由 `workflow(pm)` 自身完成下一条 mainline / patrol 的 live 抽样，机械补派只会增加并行噪音，不会更快完成验收。

## 本轮推进
- 代码批次：`.repository/pm-main@6be3642 / ../workflow_code@6be3642`
- 修改：新增 `_assignment_refresh_workflow_schedule_node()`，让 workflow schedule 节点在 dispatch 准备 execution run 时先统一刷新 `node_goal`，再把 refreshed goal 回写到 node snapshot，并让 `_build_assignment_execution_prompt()` 复用这份刷新后的节点 payload。
- 验证：`line budget`、`verify_assignment_self_iteration_plan_reference.py`、完整 `workflow gate` 全绿。
- 发布：`test / prod candidate=20260419-080601`。
- 工作区：`workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 已全部 refresh 到 `clean_synced@6be3642`。

## 当前版本
- `V4-R1` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R2` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R3` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R4` `completed / 100% / eta=2026-04-17 / 未超时`
- `V4-R5` `in_progress / 98% / eta=2026-04-20 / 未超时`
- AAR：本轮无新增

## 现场真相
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=6be3642`
- `prod current_version=20260419-073148 / candidate_version=20260419-080601 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`
- `test current_version=20260419-080601 / candidate_is_newer=false / ghost_running_detected=false`
- 当前 running mainline：`node-sti-20260419-65518069`
- 当前下一棒：mainline `node-sti-20260419-70c8289d`（ready） / patrol `node-sti-20260419-2143146b`（ready）
- 当前受控 warning：07:25 mainline 的 `selected_node.node_goal` 仍保留 `baseline=prod=20260419-065255 / root_sync_state=ahead_dirty`，因为它在 `6be3642 / 080601` 生效前就已 dispatch；手工 `create_assignment_node` 的 non-ASCII 风险继续作为次级 warning 保留。

## 下一步
- 等 `prod` 在空窗把 `candidate=20260419-080601` apply 到 live。
- 升级后用下一条 workflow mainline / patrol 做 `V4-R5` live 连续对话抽样，确认 `status-detail.selected_node.node_goal` 与 `run prompt` 已一起对齐到新 baseline。
- 若抽样转绿，我下一轮重检 `V4` 退出门槛；但在 `V5` 仍是 `activation_readiness=draft` 的前提下，我不会因为当前版本接近完成就机械切版。

## 留痕
- preference_ref: state/user-preferences.md
- delta_observation: 只让 workflow schedule 节点的 provider prompt 吃到 refreshed goal 还不够；如果 dispatch 时不把同一份 refreshed goal 回写到 node snapshot，`status-detail.selected_node.node_goal` 仍会继续停在旧 baseline / release-boundary 真相。
- delta_validation: 等 `prod` 切到 `20260419-080601` 后，用下一条 mainline / patrol 的真实执行确认 `selected_node.node_goal` 与 `run prompt` 已一起对齐到新 baseline。
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`
