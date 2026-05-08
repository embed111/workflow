# workflow-pm-wake-summary-20260412-173120

- generated_at: `2026-04-12T17:31:20+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260412-953a20b6`
- conclusion: `继续推进`
- version_focus: `V1 / 工程质量探测 / 开发实现`
- daily_task_status: `pm/daily-execution-history/2026-04-12.md` 已存在，本轮不重复补做每日任务
- preference_ref: `state/user-preferences.md`
- delta_observation: `17:20` 保底巡检已进入真 `running`；`17:25` 主线 `node-sti-20260412-2ffb67bc` 已 materialize 为最新 `ready`；旧 `16:56` 主线 `node-sti-20260412-b42e4fd4` 虽然在 `17:25:02` 已被写入 `delete_node` 审计，但节点文件一度仍是 `record_state=active`，我已用受支持 API 补做删除收口，把 active `ready` 从 `2` 条收回到 `1` 条`
- delta_validation: 下一轮优先确认当前巡检收尾后，`node-sti-20260412-2ffb67bc` 是否会在 `17:40` 下一轮保底前被正常 dispatch；若仍被连续压后，再升级为 `V1-R2` 的调度优先级风险或缺陷链

## 当前现场
- `/healthz=ok`
- `/api/status`: `running_task_count=1 / queued_task_count=1 / truth_mismatch_count=0 / workflow_mainline_handoff_pending=true`
- 当前真 running: `node-sti-20260412-953a20b6 / arun-20260412-172404-1ea899`，`started_at=2026-04-12T17:24:04+08:00`，`latest_event_at=2026-04-12T17:31:20+08:00`
- 当前待执行主线: `node-sti-20260412-2ffb67bc / [持续迭代] workflow / 2026-04-12T17:25:00+08:00`，状态 `ready`
- 已治理收口的旧主线: `node-sti-20260412-b42e4fd4 / [持续迭代] workflow / 2026-04-12T16:56:00+08:00`，当前 `record_state=deleted / deleted_at=2026-04-12T17:30:25+08:00`
- 保底 future 仍在 `2026-04-12T17:40:00+08:00`
- `/api/runtime-upgrade/status`: `current_version=candidate_version=20260412-151337 / candidate_is_newer=false / can_upgrade=false / blocking_reason=running_tasks_present`

## 本轮新增进展
- 我确认 `17:20` 这条保底巡检已经在 `2026-04-12T17:24:04+08:00` 被 `schedule-worker` dispatch 成真 `running`，不是只停在 `ready/future`
- `17:25` 的新主线已经 materialize 为 `node-sti-20260412-2ffb67bc`，当前最新主线出口没有丢
- 我也确认旧 `16:56` 主线并不是简单“继续堆着不动”：`aaud-20260412-172507-e4f120` 先写了 `superseded by newer schedule trigger`，只是删除没有真正落到节点文件
- 针对这条删除未持久化的现场，我执行了受支持的 `DELETE /api/assignments/.../nodes/node-sti-20260412-b42e4fd4` 收口，得到 `aaud-20260412-173027-be09d5`，随后图上 `ready` 从 `2` 条收回到 `1` 条、`queued_task_count` 也回落到 `1`
- 当前因此不再是“旧 ready 积压扩大”的现场，但 `workflow_mainline_handoff_pending` 仍存在：保底还在跑，真正的主线仍在等当前窗口收尾后接棒

## 发布边界
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=607a5ab`
- `push_block_reason=-`
- `next_push_batch=待切批`
- `.repository/pm-main` 与 `../workflow_code` 仍各自显示 `origin/main [ahead 20]`，按当前治理口径仅作上游参考，不作为本地发布边界阻塞

## 验证
- `Get-Date -Format o`
- `Invoke-RestMethod http://127.0.0.1:8090/healthz`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/schedules`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260412-953a20b6&include_test_data=0'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260412-b42e4fd4&include_test_data=0'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260412-2ffb67bc&include_test_data=0'`
- `Get-Content -Raw C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260412-b42e4fd4.json`
- `Get-Content -Raw C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260412-2ffb67bc.json`
- `Get-Content -Raw C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260412-172404-1ea899/run.json`
- `rg -n "aaud-20260412-173027-be09d5|node-sti-20260412-b42e4fd4|node-sti-20260412-2ffb67bc|node-sti-20260412-953a20b6" C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- `Invoke-RestMethod -Method Delete http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/nodes/node-sti-20260412-b42e4fd4`
- `git -C .repository/pm-main status --short --branch`
- `git -C ../workflow_code status --short --branch`

## 结论与下一步
- 当前明确回答：`继续推进`，不暂停，不补新的主线 schedule，也不触发 `/api/runtime-upgrade/apply`
- 本轮版本推进归类：`工程质量探测`。我除了确认 `17:20 running + 17:25 ready` 的新现场，还对“superseded 删除审计已写但 active 节点未收口”执行了受支持治理动作
- 当前现场仍不是 `0 running + ready 堆积` 的假健康：我保留了真实 patrol run、单条最新 mainline ready 和 `17:40` 的保底 future
- 下一轮优先观察当前巡检收尾后，`node-sti-20260412-2ffb67bc` 是否会在 `17:40` 前被接走；若继续被连续保底压后，我就把它正式升级为 `V1-R2` 的调度优先级风险或缺陷链
- memory_ref: `.codex/memory/2026-04/2026-04-12.md`
