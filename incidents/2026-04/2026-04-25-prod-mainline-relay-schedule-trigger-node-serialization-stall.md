# 生产事故记录 | 2026-04-25 | prod 主线接力卡在 schedule-trigger 建节点重序列化

- incident_id: `INC-20260425-prod-mainline-relay-schedule-trigger-node-serialization-stall`
- severity: `SEV-2`
- environment: `prod`
- detected_at: `2026-04-25T09:54:39+08:00`
- detected_by: `workflow(pm)`
- related_version:
  - `broken_on_prod=20260425-094450`
  - `fixed_in_workspace=2a80185`
  - `fixed_on_test=20260425-102705`
  - `fixed_on_prod=20260425-102814`
- related_requirement:
  - `V12-R5`
- status: `resolved`
- resolution_time: `2026-04-25T10:37:21+08:00`
- resolution_policy: `must_restore_before_close`
- aar_policy: `defer_until_version_close`
- aar_target_version: `V11`

## 1. 事故摘要
- live patrol 已删除后，`[持续迭代] workflow` 虽然还能 `trigger_hit`，但多次停在：
  - `trigger_hit`
  - `self_iter_guard_degraded`
  - `queued_for_processing`
- 用户面会看到：
  - 主线似乎还在续挂
  - 但新一轮迟迟不建节点、不派发
  - 7x24 看起来没彻底断，却也没有真实推进

## 2. 用户面影响
- 这不是“服务挂了”，而是更隐蔽的“主线还在命中，但接力慢到接近不可用”。
- 直接影响是：
  - 用户会误以为 schedule 已恢复，实际上主线仍在锁后排队
  - 删除 patrol 后，如果主线这条重路径不修，现网会重新变成只有 future/trigger 的半断链

## 3. 现场真相
- 旧版本 `prod=20260425-094450` 上可见：
  - `sch-20260405-56eee156` 多次写出 `trigger_hit`
  - 但 `create_assignment_node` 很晚才出现，甚至长期不出现
- 关键现场证据：
  - `logs/runs/mainline-relay-recovery-20260425-1040.md`
  - `.running/control/runtime/prod/logs/events/schedules.jsonl`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`

## 4. 根因判断
- 根因不是主线 schedule 没命中，也不是 patrol 删除本身。
- 真正的直接根因是：
  - schedule-trigger 在创建 assignment node 时，为了返回 created node，
  - 仍走了“整张全局主图完整 response snapshot + serialized_nodes materialize”的重路径
- 在主图节点较多时，这条路径会把同一条 schedule 的 processing lock 长时间占住。
- 结果就是：
  - 旧 trigger 的后半段处理迟迟跑不完
  - 新 trigger 只能继续排在这把锁后面
  - 表面上像“主线会命中，但总是不往下走”

## 5. 修复动作
- 代码修复：
  - `src/workflow_app/server/services/assignment_service_parts/task_artifact_store_actions.py`
    - 为 schedule-trigger node create 增加 `serialize_nodes=False` fast path
    - 只构造 node-only response，不再为单条 trigger 强制重建全量 `serialized_nodes`
  - `scripts/acceptance/verify_schedule_trigger_node_create_fast_path.py`
    - 新增 dedicated probe，锁住“schedule-trigger node create 不再请求 full response snapshot serialization”
  - `scripts/acceptance/workflow_gate_probe_registry.py`
    - 将新 probe 接入 gate registry
- 发布链：
  - `test=20260425-102705`
  - `prod=20260425-102814`

## 6. 恢复结果
- 当前 `prod=20260425-102814` 已恢复到：
  - `running_task_count=1`
  - `queued_task_count=1`
  - `ghost_running_detected=false`
- 当前 live 主线：
  - running: `node-sti-20260425-aca948f5`
  - ready: `node-sti-20260425-3322efce`
- 对应 live run：
  - `arun-20260425-103325-9e2fc5`
  - `provider_pid=47296`
  - `events.log` 已出现 `provider_start / thread.started / turn.started`

## 7. 事故证据
- 运行留痕：
  - `logs/runs/mainline-relay-recovery-20260425-1040.md`
- gate / probe：
  - `.repository/pm-main/.test/20260425-102445-158/report.md`
  - `.repository/pm-main/.test/20260425-102455-799/report.md`
- 发布：
  - `.running/control/logs/test/deploy-20260425-102705.json`
  - `.running/control/logs/prod/deploy-20260425-102814.json`
- live:
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260425-103325-9e2fc5/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260425-103325-9e2fc5/events.log`

## 8. 后续避免方向（供版本结束 AAR 展开）
- schedule-trigger 这类桥接路径不能再偷走“整图完整序列化”这种高成本能力。
- 单条 trigger 建节点、桥接 dispatch、trigger truth 回写，后续都要默认优先走 node-only / graph-metrics fast path。
- 只要 live 上命中过“trigger_hit 之后迟迟不 create_assignment_node”，后续必须优先怀疑 processing lock 被重路径拖住，而不是先怀疑 schedule 没命中。
- 当前接口/性能这条需求不能再长期停在 planned 文案层；这次事故已经证明“重路径导致分钟级卡顿”本身就是接口性能问题，而不是纯 runtime 偶发。

## 9. AAR 约束
- 这张事故卡已经建档，不再允许后续口头略过。
- `V11` 结束后，必须补完整 AAR：
  - `pm/versions/V11/aar/2026-04/2026-04-25-prod-mainline-relay-schedule-trigger-node-serialization-stall.md`
- AAR 至少要回答：
  - 为什么当时把接口目录/compare 基线完成，误当成“接口性能这条可以继续后放”
  - 为什么 schedule-trigger node create 还允许走整图重序列化
  - 为什么这类分钟级卡顿没有更早被显式归类为接口/性能问题，而是先在 live 值守里兜圈
