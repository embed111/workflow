# workflow-pm-wake-summary

- checked_at: `2026-04-10T22:25:12+08:00`
- active_version: `V1`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260410-212042`
- memory_ref: `.codex/memory/2026-04/2026-04-10.md`

## 巡检结论

这轮 `prod` 不是假健康。`2026-04-10T22:22:00+08:00` 同时命中了保底巡检和主线 schedule，当前现场已经收口为：

- `running`: `node-sti-20260410-b3cd9eac / arun-20260410-222212-8064d4`
- `ready`: `node-sti-20260410-5200bbc9`

当前巡检 run 的 `run.json` 显示 `status=running / provider_pid=54284 / latest_event_at=2026-04-10T22:25:12+08:00`，`events.log` 已出现 `dispatch -> provider_start -> thread.started -> turn.started`，所以 `schedules` 里的 `assigned agent already has running node` 不是“没有 live run 的假健康”，而是当前 `workflow` 已被巡检节点占用，主线节点因此停在 `ready` 等接棒。

当前没有执行 `/api/runtime-upgrade/apply`。默认 `/api/runtime-upgrade/status` 为：

- `current_version=candidate_version=20260410-212042`
- `running_task_count=1`
- `blocking_reason=running_tasks_present`
- `can_upgrade=false`

按本轮节点排除 `node-sti-20260410-b3cd9eac` 后，门禁回落为：

- `running_task_count=0`
- `excluded_running_task_count=1`
- `blocking_reason=no_candidate`
- `can_upgrade=false`

所以这轮不存在“可无痛升级但没升”的遗漏，当前只是没有更高 candidate。

## 发布边界

这轮实际根仓同步快照应改判为：

- `developer_id=pm-main`
- `root_sync_state=diverged_or_unknown`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=code_root_local_repo_behind_origin_main_and_workspace_path_scope_blocks_root_repo_sync`
- `next_push_batch=待允许工作区外收口时先把 ../workflow_code 快进到 b2572be`
- `workspace_head=b2572be`
- `code_root_head=340413e`

也就是说，调度上下文里沿用的 `root_sync_state=clean_synced` 在 `2026-04-10 22:24 +08:00` 这个时点已经过期；`pm-main` 自己是 clean，但本机 `../workflow_code` 本地 `main` 仍落后 `origin/main` 1 个提交。

## 协作链判断

当前 helper 执行链没有完全恢复：

- `workflow_bugmate.runtime_status=idle`
- `workflow_devmate.runtime_status=idle`
- `workflow_testmate.runtime_status=creating`
- `workflow_qualitymate.runtime_status=creating`

`/api/agents` 还显示四个 helper 的开发工作区记录仍停在 `dev/<helper>` 和 `8343a2f...` 旧基线。因为这轮任务明确限制“只允许写当前 `workspace_path` 内的内容”，而通过 live API 续挂 helper 或修根仓同步都会把新记录写到 `C:/work/J-Agents/.output` 或工作区外路径，所以这轮我只把它记成明确阻塞，没有再越界补单。

## 当前出口与下一次建议

当前主线出口不是新的 `future` 时间，而是已经建好的 `ready` 主线节点：

- 主线接棒节点：`node-sti-20260410-5200bbc9`
- 当前保底巡检节点：`node-sti-20260410-b3cd9eac`

按现网机制，这轮巡检成功收尾后应由 finalize 释放 `workflow` 的 running 槽，并继续续挂新的主线/保底 future。若到 `2026-04-10T22:30:00+08:00` 仍然满足任一条件，应直接按断链处理：

- `node-sti-20260410-5200bbc9` 仍未从 `ready` 进入真实 `dispatch/provider_start`
- 两条 schedule 仍都没有新的 `next_trigger_at`

## 证据

- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260410-b3cd9eac'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260410-b3cd9eac'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/agents'`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260410-b3cd9eac.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260410-5200bbc9.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-222212-8064d4/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260410-222212-8064d4/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `.running/control/reports/test-gate-20260410-212042.json`
