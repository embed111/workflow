# mainline relay recovery 2026-04-25 10:40

- topic: 去掉 live patrol 后，收口 `workflow` 主线 schedule 建单卡顿，恢复 `7x24` 主线真 running + 下一棒 ready。
- operator: `workflow(pm)`
- preference_ref: `state/user-preferences.md`

## 变更范围
- 代码提交：
  - `.repository/pm-main@2a80185`
  - `../workflow_code@2a80185`
- 关键代码：
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_actions.py`
  - `.repository/pm-main/scripts/acceptance/verify_schedule_trigger_node_create_fast_path.py`
  - `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`
- 运行面：
  - 删除 live patrol schedule：`sch-20260405-67a89536`
  - prod 当前版本：`20260425-102814`

## 问题与修复
- 现场问题：
  - patrol 已删除后，`[持续迭代] workflow` 仍多次停在 `trigger_hit / self_iter_guard_degraded / queued_for_processing`，迟迟不进入 `create_assignment_node`。
  - 根因收窄到 schedule-trigger 节点创建路径仍在重建整张全局主图的完整 response snapshot，导致同一条 mainline schedule 的 processing lock 被长时间占用。
- 修复动作：
  - 给 schedule-trigger 节点创建补 `serialize_nodes=False` 的 fast path，只保留 node-only response 与 graph metrics，不再为单条 trigger 强制 materialize 全量 `serialized_nodes`。
  - 新增 probe：`scripts/acceptance/verify_schedule_trigger_node_create_fast_path.py`
  - 将 probe 注册进 `workflow_gate_probe_registry.py`

## 验证
- line budget:
  - `python .repository/pm-main/scripts/quality/check_workspace_line_budget.py --root .repository/pm-main`
  - `mandatory_gate_pass=true`
- test sessions:
  - `.repository/pm-main/.test/20260425-102445-158/report.md`
    - `python scripts/acceptance/verify_schedule_trigger_node_create_fast_path.py`
  - `.repository/pm-main/.test/20260425-102455-799/report.md`
    - `python -m py_compile src/workflow_app/server/services/assignment_service_parts/task_artifact_store_actions.py scripts/acceptance/verify_schedule_trigger_node_create_fast_path.py scripts/acceptance/workflow_gate_probe_registry.py`
- deploy:
  - test：`20260425-102705`
  - prod：`20260425-102814`

## live 真相
- 当前 `/api/runtime-upgrade/status`：
  - `current_version=20260425-102814`
  - `running_task_count=1`
  - `ghost_running_detected=false`
- 当前 `/api/status`：
  - `running_task_count=1`
  - `queued_task_count=1`
  - `workflow` 主线：
    - running: `node-sti-20260425-aca948f5`
    - queued: `node-sti-20260425-3322efce`
- 当前 live run：
  - `arun-20260425-103325-9e2fc5`
  - `provider_pid=47296`
  - `events.log` 已出现 `provider_start / thread.started / turn.started`

## 结论
- live patrol 已去掉，不再误导为“主线巡检也算推进”。
- `workflow` 主线已经恢复到：
  - 当前有一条真 running
  - 下一棒已有 ready 节点可接力
  - 当前没有 ghost running
- 这轮代码修掉的是“schedule-trigger 建节点阶段的重序列化卡顿”；当前仍要继续观察运行中的 `arun-20260425-103325-9e2fc5` 收尾是否平稳。

## 下一步
- 继续观察当前 `aca948f5` 收尾与 `3322efce` 接力，不再人工补 patrol。
- 后续把 `repair-ghost-running` 的慢响应与当前版本快照自动刷新继续纳入 `V12-R5` 收口。
