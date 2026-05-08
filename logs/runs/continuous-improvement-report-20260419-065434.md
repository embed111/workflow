# [持续迭代] workflow / 2026-04-19 05:49:00

## 判断
- `version_transition_decision=stay(V4)`。我这轮先修 dispatch prompt materialize，不切 `V5`，因为 `next_activation_ready=false`，而 `V4-R5` 还缺 `prod=20260419-065255` 下的 live 连续对话抽样。
- 当前最高价值动作不是再重复观察，而是把 live 已暴露的旧 prompt 漏口真正收进候选版本。

## 取舍
- 我没有继续重复 `node_goal` / old ready rebuild 那一刀；我改了 workflow schedule 节点在 dispatch 时优先回读 live schedule detail，避免 `05:49` 这类延迟派发节点继续带着 `052046 / ahead_dirty` 旧快照启动。
- 我没有补派新的 helper 任务，因为当前剩余 blocker 直接依赖 `prod` 空窗升级后的 mainline / patrol 真实执行，机械补派不会更快。

## 本轮推进
- 代码批次：`.repository/pm-main@799b01b -> ../workflow_code@799b01b`
- 验证：`line budget`、增强后的 `verify_assignment_self_iteration_plan_reference.py`、完整 `workflow gate`
- 发布：`test / prod candidate=20260419-065255`
- 工作区：`developer_workspace_count=6 / clean_synced=6`

## 当前版本
- `V4-R1` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R2` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R3` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R4` `completed / 100% / eta=2026-04-17 / 未超时`
- `V4-R5` `in_progress / 92% / eta=2026-04-20 / 未超时`
- AAR：本轮无新增

## 现场真相
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=799b01b`
- `prod current_version=20260419-060625 / candidate_version=20260419-065255 / candidate_is_newer=true / drain_active=true / running_task_count=1`
- `test current_version=20260419-065255 / candidate_is_newer=false / ghost_running_detected=false`
- 当前出口：running `node-sti-20260419-067cc597`；next mainline `node-sti-20260419-2ed63b36`；patrol `node-sti-20260419-d9a4b773`
- 受控风险：当前 running 的 `05:49` 主线仍在旧 prompt 下执行；手工 `create_assignment_node` 的 non-ASCII 风险仍在

## 下一步
- 等 `prod` 在空窗切到 `20260419-065255`
- 升级后用 `node-sti-20260419-2ed63b36 / node-sti-20260419-d9a4b773` 做 `V4-R5` live 连续对话抽样
- 若抽样转绿，下一轮重检是否满足 `V4 -> V5` 切版条件

## 留痕
- preference_ref: state/user-preferences.md
- delta_observation: 仅修 `node_goal` 和旧 `ready` 节点的 execution-time rebuild 还不够，dispatch 生成 `prompt.txt` 时也必须优先回读 live schedule detail，否则延迟派发的 mainline 仍会吃到旧 baseline。
- delta_validation: 等 `prod` 切到 `20260419-065255` 后，用 next mainline / patrol 的真实执行确认 live prompt 已不再回落到 `052046 / ahead_dirty`。
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`
