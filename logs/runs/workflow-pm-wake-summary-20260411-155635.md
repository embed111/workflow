# workflow-pm-wake-summary

- checked_at: `2026-04-11T15:56:35+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-9a930f56`
- run_id: `arun-20260411-154229-4891fb`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- experience_refs:
  - `.codex/experience/runtime-upgrade-and-agent-monitoring.md`
  - `.codex/experience/schedule-trigger-closure.md`

## 巡检结论

这轮 `prod` 不是假健康。当前 live 现场已经收口为：

- `running`: 保底巡检 `node-sti-20260411-9a930f56 / arun-20260411-154229-4891fb`
- `ready`: 主线 `node-sti-20260411-7fa4dfbe`
- `future`: 主线 `sch-20260405-56eee156 -> 2026-04-11T15:58:00+08:00`；保底 `sch-20260405-67a89536 -> 2026-04-11T16:21:00+08:00`

我直接核了当前巡检 run 的磁盘真相：`run.json` 仍是 `status=running / provider_pid=62944 / latest_event_at=2026-04-11T15:56:14+08:00`。同时全局主图当前是 `1 running / 1 ready / 6 pending`，所以这轮既不是“0 running + ready 堆积”的假健康，也没有丢掉下一棒出口。

当前 active 版本继续是 `V1`，本轮最高价值泳道继续是 `工程质量探测`，生命周期阶段继续是 `变更控制`。这轮最该推进的动作不是再挂新 helper，也不是自己触发正式升级，而是把 future schedule 再次漂回旧 `ahead_clean` 的 prompt 真相收住。

## 发布边界

当前真正的 release boundary 仍是：

- `developer_id=pm-main`
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=待切批`
- `workspace_head=code_root_head=c55e357`
- 上游参考：`pm-main / workflow_code -> ## main...origin/main [ahead 5]`

也就是说，这轮命中的 `ahead_clean / ahead_count=5 / push_block_reason=unpushed_commits_present` 只是 live `prod=20260411-093051` 仍在旧 release boundary 口径上的 prompt 残留，不是新的本地 dirty/ahead 现场。

我已在 `2026-04-11T15:54:00+08:00` 用当前工作区模板对 live prod runtime 再执行一次受支持的 `schedule_service.update_schedule(...)`，把两条 active schedule 的 `launch_summary` 都重新刷回：

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `push_block_reason=-`

复核 `/api/schedules/sch-20260405-56eee156` 与 `/api/schedules/sch-20260405-67a89536` 后，`15:58 / 16:21` 的下一棒已经会读取新的 `clean_synced(c55e357)` 文案。当前正在运行的保底节点 `node-sti-20260411-9a930f56` 仍保留旧 snapshot，这属于已 materialize 的历史节点，我这轮没有回写它的当前 prompt，只修 future schedule 本身。

## 升级门禁

这轮没有执行 `/api/runtime-upgrade/apply`。默认 `/api/runtime-upgrade/status` 仍是：

- `current_version=20260411-093051`
- `candidate_version=20260411-131835`
- `running_task_count=1`
- `blocking_reason=存在运行中任务，暂不可升级`
- `can_upgrade=false`

按当前巡检节点排除 `node-sti-20260411-9a930f56` 后，门禁回落为：

- `running_task_count=0`
- `candidate_version=20260411-131835`
- `can_upgrade=true`

所以这轮不存在“已经空窗却漏升”的判断错误；当前仍应继续由 `prod` supervisor 托管的 idle watcher 在真正空窗时发起升级，而不是由这条巡检节点自己 `apply`。

## Helper 判断

这轮我没有新挂 helper 任务，因为当前并不存在“执行者缺位就会断链”的现场：

- `agent_registry.runtime_status` 中 `workflow_bugmate / workflow_devmate / workflow_qualitymate / workflow_testmate` 当前都是 `idle`
- `state/developer-workspaces.json` 中四个 helper 开发工作区也都保持 `main@c55e357 / status=ready`
- `role_creation_sessions` 里 `workflow_testmate / workflow_qualitymate=creating` 仍存在，但已经只是历史 residue，不再对应 live 锁

因此当前最值得做的不是再补派一个 helper，而是继续把 `workflow(pm)` 这一棒巡检收尾好，并观察首个空窗里的正式升级与 schedule 文本是否再次漂移。

## 下一次建议

- 主线下一观察点：`2026-04-11T15:58:00+08:00`
- 保底下一观察点：`2026-04-11T16:21:00+08:00`
- 升级观察点：当前巡检节点释放 running 槽后的首个空窗，核对 idle watcher 是否把 `candidate=20260411-131835` 接入 live `prod`
- 异常门槛：
  - 如果 `15:58` 主线到点后没有新的 live run，就按 handoff 异常继续处理
  - 如果首个空窗后 `current_version` 仍停在 `20260411-093051`，或 active schedule 又把 `launch_summary` 漂回 `ahead_clean`，就把 `prod supervisor / idle watcher` 验证或重启提升为下一条受支持治理批次

## 证据

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `docs/workflow/reports/7x24发布边界收口方案-20260409.md`
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-9a930f56'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-56eee156'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-67a89536'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-9a930f56'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-7fa4dfbe'`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-154229-4891fb/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-154229-4891fb/events.log`
- `D:/code/AI/J-Agents/workflow/.running/control/runtime/prod/state/workflow.db`
- `logs/runs/prod-idle-upgrade-watchdog-live.md`
