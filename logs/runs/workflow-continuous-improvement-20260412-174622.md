# workflow continuous improvement 2026-04-12 17:46:22

- generated_at: `2026-04-12T17:53:59+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260412-2ffb67bc`
- active_version: `V1`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- version_progress: `bug 探测`
- preference_ref: `state/user-preferences.md`
- delta_observation: 当前这轮最有价值的推进不是继续口头确认主线健康，而是把 `17:11 followup_dispatch_blocked + 17:25 delete_node 未持久化 + 17:36 mainline 正常 dispatch` 收成一条真并行的 bug probe，并盯到 `17:51` 新主线再次 materialize 为 `ready`。
- delta_validation: 下一轮先消费 `workflow_bugmate node-20260412-174422-ccc71c / arun-20260412-174500-cd5659` 的探测结论，再决定是否派给 `workflow_devmate / workflow_testmate`。

## live_truth
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=607a5ab / push_block_reason=- / next_push_batch=待切批`
- `current_version=candidate_version=20260412-151337 / candidate_is_newer=false / can_upgrade=false / blocking_reason=running_tasks_present`
- `running_task_count=2 / queued_task_count=2 / active_agent_count=2 / workflow_mainline_handoff_pending=false`
- 当前 `workflow` 真 running：
  - `node-sti-20260412-2ffb67bc / arun-20260412-173605-1d6150`
- 当前 helper 真 running：
  - `workflow_bugmate node-20260412-174422-ccc71c / arun-20260412-174500-cd5659`
- 当前排队出口：
  - `node-sti-20260412-2afb6640 / pm持续唤醒 - workflow 主线巡检 / 2026-04-12T17:40:00+08:00`
  - `node-sti-20260412-f8617c06 / [持续迭代] workflow / 2026-04-12T17:51:00+08:00`
- future 入口：
  - 保底 `2026-04-12T18:00:00+08:00`
- 当前不是 `0 running + ready 堆积` 的假健康；`17:40` 保底与 `17:51` 新主线当前都只是主线仍在运行时的正常串行等待。

## actions
- 复核 `healthz / status / schedules / runtime-upgrade/status`，确认 `17:25` 主线已真 `running`。
- 复核 `.repository/pm-main` 与 `../workflow_code` 的 `status --short --branch / --porcelain=v1 / rev-parse --short HEAD`，确认本地发布边界仍 clean。
- 先删除一条 `node_goal` 被 PowerShell 反引号污染的未派发 helper 节点：`node-20260412-174258-a11a60`。
- 用纯文本 `node_goal` 重建 `workflow_bugmate` 的 `P0` 探测节点：`node-20260412-174422-ccc71c`。
- 通过 `dispatch-next` 成功派发该 helper，拿到 `run_id=arun-20260412-174500-cd5659`。
- 复核 `/api/status` 后，顺手把 PM 当前快照里的“继续保持”文案改回 parser 兼容句式，避免 `pm_version_status.lane / baseline` 被解析成空值。
- 同步更新 `pm/PM当前版本计划.md`、`pm/versions/V1/版本计划.md`、`pm/versions/V1/history/2026-04/2026-04-12.md`、`.codex/memory/2026-04/2026-04-12.md` 与经验卡。

## evidence
- `aaud-20260412-173645-41dfae`: `17:25` 主线被 dispatch 成 `running`
- `aaud-20260412-174359-6c3e51`: 清理被污染的 helper 节点 `node-20260412-174258-a11a60`
- `aaud-20260412-174424-c15593`: 创建新的 `P0` bug probe `node-20260412-174422-ccc71c`
- `arun-20260412-174500-cd5659`: `workflow_bugmate` 探测 run 已于 `2026-04-12T17:44:59+08:00` 开始，`latest_event_at=2026-04-12T17:53:15+08:00`

## parallel
- `parallel_candidate_count=2`
- `parallel_dispatched_count=1`
- `active_helper_tasks=[workflow_bugmate node-20260412-174422-ccc71c / arun-20260412-174500-cd5659]`
- `parallel_block_reason=第二条开发或回归切片仍依赖 bugmate 对 handoff/delete 持久化根因的判断，暂不盲派 workflow_devmate 或 workflow_testmate`

## next
- 先消费 `workflow_bugmate` 的 `dispatch-handoff-bug-probe.md`，再决定这条问题是 closure、提交 defect，还是转给 `workflow_devmate`。
- 主线 next: `node-sti-20260412-f8617c06 / [持续迭代] workflow / 2026-04-12T17:51:00+08:00`
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-12T18:00:00+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-12.md`
