# workflow-pm-wake-summary

- 巡检时间：`2026-04-11T08:45:13+08:00`
- ticket/node：`asg-20260327-223335-b79f27 / node-sti-20260411-bbaf62fa`
- active 版本：`V1 工程质量基线与运行稳态`
- 本轮泳道：`工程质量探测`
- 生命周期阶段：`基于基线测试`
- baseline：`prod=20260411-040421`
- 根仓同步快照：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批 / workspace_head=7a54432 / code_root_head=7a54432`

## 本轮结论

1. 当前 `prod` 不是假健康。`workflow` 现在只有 1 条真实 live run：`node-sti-20260411-bbaf62fa / arun-20260411-083922-11016f`；`events.log` 已出现 `dispatch -> provider_start -> thread.started -> turn.started`，而任务图当前没有已到时 `ready` 堆积。
2. 7x24 连续推进出口仍然完整。主线 schedule `sch-20260405-56eee156` 已续挂到 `2026-04-11T09:08:00+08:00`，保底 schedule `sch-20260405-67a89536` 已续挂到 `2026-04-11T09:38:00+08:00`，所以本轮无需补链。
3. 当前没有可执行的无痛升级窗口。`/api/runtime-upgrade/status` 显示 `current=candidate=20260411-040421 / running_task_count=1 / blocking_reason=running_tasks_present / can_upgrade=false`；排除当前巡检节点后回落为 `running_task_count=0 / excluded_running_task_count=1 / blocking_reason=no_candidate / can_upgrade=false`，说明不是被当前节点误挡住升级，而是根本没有更高 candidate。
4. 最新主线异常已经从“主链断了”收口为“工程质量信号待处理”。`[持续迭代] workflow / 2026-04-11 03:43:00` 对应节点 `node-sti-20260411-289d89af` 在 `2026-04-11T08:38:19+08:00` 被系统按 stale running 回收，但 failure context 已保存在 `arun-20260411-034321-33ca3c/stderr.txt`。证据里同时出现了三类问题：PowerShell 路径/命令误用、`verify_training_registry_assignment_runtime_status.py` 断言 `running_agents == set()`、以及 `training_registry_service_parts/registry_sync_and_overview.py` 的 `NameError: connect_db is not defined`。
5. 本轮没有新挂 `workflow_devmate / workflow_bugmate`。原因不是没人可接，而是当前最小稳态已经由 `workflow` 自己守住，下一条主线 `09:08` 仍会继续推进；相比现在盲派一条混合故障任务，更稳的顺序是先让下一棒把 `03:43` 主线失败压成单一问题定义，再决定路由给 `workflow_devmate` 还是 `workflow_bugmate`。

## 证据

- 版本与升级：`.running/control/prod-last-action.json`、`.running/control/prod-candidate.json`
- 调度与任务图：`http://127.0.0.1:8090/api/schedules`、`http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph`
- 当前 live run：`C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-083922-11016f/run.json`、`C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-083922-11016f/events.log`
- 03:43 主线失败：`http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-289d89af`、`C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-034321-33ca3c/stderr.txt`
- 审计回写：`C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`

## 下一次建议唤醒时间

- 主线：`2026-04-11T09:08:00+08:00`
- 保底：`2026-04-11T09:38:00+08:00`

