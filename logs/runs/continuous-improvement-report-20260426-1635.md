# continuous-improvement-report 2026-04-26 16:42

- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-26.md`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260426-3412c63d`
- active_version: `V11`
- version_transition_decision: `stay(V11)`
- progressive_modification: `helper_rerun_and_dispatch_recovery`

## 判断
- 本轮不切 `V12`。`V11-R1/R3/R4/R6` 已满足退出口径，`V12-R2` 测试路线已交付，但 `V12-R1/R5` 仍没有红灯 probe 与最小实现绿灯。
- 最高价值泳道保持 `工程质量探测`，生命周期阶段从“recovery failed + regression blocked”修正为“recovery 已 rerun 并真实 running，testmate regression pending”。
- 下一动作不是再造同义 helper 节点，而是等待 `node-20260426-1441-v12r15-dev-recovery` 交付；若它再次失败，下一轮直接处理对应 blocker。

## 本轮推进
- 已消费 devmate recovery 的失败真相：`stream_disconnected`，只有“准备写 probe 文件”的结构化结果，未交付实现报告。
- 已确认 `workflow_devmate` 工作区存在 4 个未验证 probe 文件，不能提交，必须由 recovery 节点完成或清理。
- 已对同一节点执行 rerun；客户端超时后回读文件真相，`node-20260426-1441-v12r15-dev-recovery` 已从 `failed` 恢复并进入真实 `running`。
- 已触发 dispatch-next；客户端超时后先生成 `arun-20260426-163000-9b494b`，最终复核时该 run 已转为 `running/provider_pid=46500`，latest_event_at=`2026-04-26T16:41:35+08:00`。
- `workflow_testmate node-20260426-1516-v12r15-test-regression` 已从 `blocked` 恢复到 `pending`，等待 devmate 真正交付后执行 go/no-go。

## 需求逐项状态
- `V11-R1`: `completed / 100% / 最近更新=2026-04-26T16:42:00+08:00 / ETA=2026-04-26 / 已完成，无 AAR`
- `V11-R2`: `v12_gate_test_regression_pending / 64% / 最近更新=2026-04-26T16:42:00+08:00 / ETA=2026-04-27 / 未超时`
- `V11-R3`: `completed / 100% / 最近更新=2026-04-26T16:42:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`
- `V11-R4`: `completed / 100% / 最近更新=2026-04-26T16:42:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`
- `V11-R5`: `v12_gate_recovery_running_after_rerun / 64% / 最近更新=2026-04-26T16:42:00+08:00 / ETA=2026-04-29 / 未超时`
- `V11-R6`: `completed / 100% / 最近更新=2026-04-26T16:42:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`

## 发布边界
- `root_sync_state=clean_synced(pm-main/workflow_code)`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=workflow_devmate 有 4 个未验证 untracked probe 文件，来自失败 helper；必须等当前 running recovery 完成验证或清理后才能提交`
- `next_push_batch=等待 workflow_devmate recovery 完成或清理 4 个 probe 文件；若产生代码则在 workflow_devmate 工作区完成 TDD/验证后提交并同步 workflow_code/main，再交给 testmate regression`

## 证据
- `/healthz`: `ok / 103ms`
- `/api/status`: `running_task_count=2 / active_version=V11 / next_activation_candidate=V12 / next_activation_ready=false`
- `/api/schedules`: `[持续迭代] workflow` 当前 last_result=`running`，node=`node-sti-20260426-3412c63d`
- `/api/runtime-upgrade/status`: `current=20260426-140042 / candidate=20260426-140042 / candidate_is_newer=false / request_pending=false / running_task_count=2 / agent_call_count=2 / ghost_running_detected=false`
- `node-20260426-1441-v12r15-dev-recovery.json`: `status=running`
- `node-20260426-1516-v12r15-test-regression.json`: `status=pending`
- `arun-20260426-163000-9b494b/run.json`: `status=running / provider_pid=46500 / latest_event_at=2026-04-26T16:41:35+08:00`

## 风险与下一步
- 风险：helper 已真实运行，但尚未交付红灯/绿灯证据；`workflow_devmate` 工作区的 4 个 probe 文件仍是未验证状态。
- 下一步：等待 devmate recovery 交付；若失败，下一轮直接按失败报告决定由 devmate retry、bugmate 复现，还是 PM 接管最小红灯 probe。
- 切版条件：devmate recovery 交付红灯/绿灯证据，testmate regression 给出 go/no-go，且 `/api/status` 回读 `next_activation_ready=true`。
