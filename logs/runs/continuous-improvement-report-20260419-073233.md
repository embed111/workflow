# [持续迭代] workflow / 2026-04-19 06:36:00

## 判断
- `version_transition_decision=stay(V4)`。我这轮不切 `V5`，因为 `next_activation_ready=false`，而 `V4-R5` 还缺 `prod=20260419-073148` 下的 live 连续对话抽样。
- 当前最高价值动作不是再重复观察，也不是先追次级 non-ASCII warning，而是把 workflow prompt rebuild 对 `get_schedule_detail()` 的真实返回结构兼容好；否则新版本即使已经把 schedule detail 刷成 live 真相，执行时仍会静默回退到旧 `node_goal`。

## 取舍
- 我没有继续重复上一轮的 dispatch materialize 调整，而是直接收掉更深一层的读链缺口：`get_schedule_detail()` 实际返回 `{schedule: {...}}`，旧逻辑却按平铺字段取值，导致 live detail 根本没被消费到。
- 我没有补派新的 helper 任务，因为当前剩余 blocker 直接依赖 `prod` 空窗升级后的 workflow 自身下一次真实 mainline / patrol 执行；机械补派只会增加并行噪声，不会更快完成验收。

## 本轮推进
- 代码批次：`.repository/pm-main@2475f7f -> ../workflow_code@2475f7f`
- 红灯转绿：`verify_assignment_self_iteration_plan_reference.py` 现在同时锁住 flat payload 和 `{schedule: {...}}` detail payload 两条路径
- 验证：`line budget`、定向 acceptance、完整 `workflow gate`
- 发布：`test / prod candidate=20260419-073148`
- 工作区：`developer_workspace_count=6 / clean_synced=6`

## 当前版本
- `V4-R1` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R2` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R3` `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R4` `completed / 100% / eta=2026-04-17 / 未超时`
- `V4-R5` `in_progress / 96% / eta=2026-04-20 / 未超时`
- AAR：本轮无新增

## 现场真相
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=2475f7f`
- `prod current_version=20260419-065255 / candidate_version=20260419-073148 / candidate_is_newer=true / drain_active=true / running_task_count=1`
- `test current_version=20260419-073148 / candidate_is_newer=false / ghost_running_detected=false`
- 当前 running mainline：`node-sti-20260419-2ed63b36`
- 当前下一棒：mainline `node-sti-20260419-65518069`（queued） / patrol `node-sti-20260419-77e9c78b`（future `2026-04-19T07:40:00+08:00`）
- 当前受控风险：`C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260419-071437-b949d7/prompt.txt` 仍带 `baseline=prod=20260419-060625`，因为这条 06:36 mainline 在修复和 `073148` candidate 生效前就已启动；手工 `create_assignment_node` 的 non-ASCII 风险仍保留为次级 warning

## 下一步
- 等 `prod` 在空窗把 `candidate=20260419-073148` apply 到 live
- 升级后用下一条 workflow mainline / patrol 做 `V4-R5` live 连续对话抽样
- 若抽样转绿，下一轮重检 `V4` 退出门槛；但在 `V5` 仍是 `activation_readiness=draft` 的前提下，我不会因为当前版本接近完成就机械切版

## 留痕
- preference_ref: state/user-preferences.md
- delta_observation: 只把 dispatch prompt 改成“读 live schedule detail”还不够；如果 prompt rebuild 没兼容 `get_schedule_detail()` 的嵌套 `schedule` payload，执行时仍会静默回退到旧 `node_goal`
- delta_validation: 等 `prod` 切到 `20260419-073148` 后，用下一条 mainline / patrol 的真实执行确认 prompt 已不再回落到旧 baseline
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`
