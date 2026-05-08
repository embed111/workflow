# workflow-pm-wake-summary 2026-04-17 15:39:18

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-7491bbbb`
- active_version: `V4`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- version_transition_decision: `stay(V4)`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `等待 workflow_testmate 先完成当前 running 的旧 smoke 节点 node-20260417-145552-3e7085，随后消费 corrected chain node-20260417-153558-d6139e -> node-20260417-153651-cfe43f`
- preference_ref: `state/user-preferences.md`
- delta_observation: `workflow_testmate` 当前 running 的 live smoke prompt 仍钉在旧 `expected_version=20260417-134734`；若不纠正，`workflow_ucdmate` 的下游 brief 会直接吃到旧 baseline。
- delta_validation: `继续跟踪 node-20260417-145552-3e7085 的终态，并优先验证 corrected chain node-20260417-153558-d6139e -> node-20260417-153651-cfe43f。`

## 巡检结论
- `prod` 服务健康，`/healthz=ok`。
- `/api/status` 当前为 `active_agent_count=2 / running_task_count=2 / queued_task_count=2 / workflow_mainline_handoff_pending=true`。
- `prod` 当前版本已经是 `20260417-145421`，`candidate_is_newer=false`，当前不是升级空窗问题。
- 当前主线未来入口仍在：保底 running=`node-sti-20260417-7491bbbb`，下一条主线 ready=`node-sti-20260417-f792cae7`，没有断链。

## 本轮推进性修改
- 我删除了依赖旧 smoke baseline 的 `workflow_ucdmate` pending 节点 `node-20260417-145653-922dce`。
- 我补挂了 corrected helper chain：
  - `node-20260417-153558-d6139e`：`workflow_testmate` current live smoke，明确要求 `expected_version=20260417-145421`
  - `node-20260417-153651-cfe43f`：`workflow_ucdmate` corrected route brief，只消费 corrected smoke 结果
- 这次修改属于 `当前需求开发` 下的 `helper dispatch 调整`，直接服务 `V4-R4 / V4-R1`。

## 版本评估
- `V4-R1`: `in_progress / 40% / eta=2026-04-19 / 未超时`
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`
- `V4-R4`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `next_activation_ready=false`，`V5` 仍是 `backlog activation_readiness=draft`，当前不切版。

## 证据
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260417-145552-3e7085`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260417-153558-d6139e`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260417-153651-cfe43f`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl#aaud-20260417-153504-b0f250`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl#aaud-20260417-153603-7841f9`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl#aaud-20260417-153702-99b638`

## Next
- 我先等 `node-20260417-145552-3e7085` 收尾，再观察 `node-20260417-153558-d6139e` 从 ready 转成 running。
- corrected smoke 一旦交付，我就优先让 `node-20260417-153651-cfe43f` 接上，只消费 `145421` 的 smoke 结果。
- 如果 corrected smoke 暴露的是产品问题而不是旧 prompt 漂移，我下一轮优先把最小实现批次路由给 `workflow_devmate`。
