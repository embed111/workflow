# continuous-improvement-report

## 本轮结论

- active_version: `V1`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260410-212042`
- root_sync_snapshot: `developer_id=pm-main / root_sync_state=diverged_or_unknown / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=code_root_local_repo_behind_origin_main_and_workspace_path_scope_blocks_root_repo_sync / next_push_batch=待在允许工作区外收口时先把 ../workflow_code 快进到 b2572be / workspace_head=b2572be / code_root_head=340413e`

这轮我没有继续在 `pm-main` 扩同工作区实现面，而是把重点放在 live baseline 的测试探测和协作链复位上。当前 `prod` 不是假健康：`/healthz` 正常，`/api/status` 与全局主图都收口为 `3 running + 0 ready`，真实 running 分别是：

- `workflow=node-sti-20260410-0a88cc5e / arun-20260410-215217-e70081`
- `workflow_bugmate=node-20260410-215834-9c63d3 / arun-20260410-215856-fdb8b7`
- `workflow_devmate=node-20260410-215845-3cd058 / arun-20260410-215917-77d9b2`

三条 run 的 `run.json` 和 `events.log` 都已经出现 `provider_start -> thread.started -> turn.started`，说明这轮不是只把节点状态推成 `running`。升级方面，默认 `/api/runtime-upgrade/status` 仍是 `running_tasks_present / can_upgrade=false`；按任务要求排除当前主线节点 `node-sti-20260410-0a88cc5e` 后，门禁明确回落为 `excluded_running_task_count=1 / blocking_reason=no_candidate / can_upgrade=false`，因此这轮不执行 `/api/runtime-upgrade/apply`。

## 协作链处理

我先尝试按当前 baseline 续挂 `workflow_testmate` 与 `workflow_qualitymate`，但 live API 直接返回 `assigned_agent_creating_locked`。随后我直接查询 `D:/code/AI/J-Agents/workflow/.running/control/runtime/prod/state/workflow.db`，确认：

- `workflow_testmate.runtime_status=creating`
- `workflow_qualitymate.runtime_status=creating`
- `workflow_bugmate.runtime_status=idle`
- `workflow_devmate.runtime_status=idle`

所以这轮没有继续在被锁住的测试/质量 agent 上盲目补单，而是把阻塞即时改派成两条可执行切片：

- `V1-P1 prod 212042 helper creating锁与注册真相复核 / 2026-04-10 22:00:00`
  - assigned_agent: `workflow_bugmate`
  - node_id/run_id: `node-20260410-215834-9c63d3 / arun-20260410-215856-fdb8b7`
- `V1-P2 helper工作区bootstrap与分支对齐 / 2026-04-10 22:00:00`
  - assigned_agent: `workflow_devmate`
  - node_id/run_id: `node-20260410-215845-3cd058 / arun-20260410-215917-77d9b2`

这两条都已经进入真实执行，因此这轮协作链没有继续闲置，只是测试/质量链被明确转成了 `V1-P1 / V1-P2` 的缺陷与工程治理切片。

## 证据

- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/dashboard'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260410-0a88cc5e'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260410-0a88cc5e'`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-215217-e70081/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-215217-e70081/events.log -Tail 120`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-215856-fdb8b7/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-215856-fdb8b7/events.log -Tail 80`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-215917-77d9b2/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-215917-77d9b2/events.log -Tail 80`
- `python - <<sqlite query>> D:/code/AI/J-Agents/workflow/.running/control/runtime/prod/state/workflow.db`

## 下一步

- 主线 next: 当前主线 `node-sti-20260410-0a88cc5e / arun-20260410-215217-e70081` 仍在运行；新的 mainline future 需等本轮 finalize 自续挂。
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-10T22:22:00+08:00`
- 协作 next: 等 `workflow_bugmate / workflow_devmate` 返回结论；如果 `workflow_testmate / workflow_qualitymate` 仍卡在 `creating`，就把这条锁定问题继续按 `V1-P1` 收成正式修复项。
- release boundary next: 若后续允许处理工作区外根仓，优先把 `../workflow_code` 本地 `main` 快进到 `b2572be`，再重新校准根仓同步快照。
- memory_ref: `.codex/memory/2026-04/2026-04-10.md`
