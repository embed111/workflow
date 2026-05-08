# workflow-pm-wake-summary

- checked_at: `2026-04-11T17:42:04+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-da973892`
- run_id: `arun-20260411-172634-057cab`
- active_version: `V1`
- task_package: `V1-P2A (V1-P2)`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- preference_ref: `state/user-preferences.md`
- delta_observation: `7x24` 这轮不仅要确认主链没断，还要把 future schedule 漂回旧 release-boundary 口径的现场当场收口；巡检过程中又并发落了一批 `7822016 / candidate 20260411-173655` 的新快照，不能继续沿用 `a6773f5 / 171743` 的旧上下文。
- delta_validation: 我已在 live prod 上把两条 active schedule 的 future `launch_summary` 重刷为 `clean_synced(7822016)`，补了一条 fresh idle-watcher single-check 证据，并把版本计划、月度现场总览和今日日记同步到最新快照。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- experience_refs:
  - `.codex/experience/runtime-upgrade-and-agent-monitoring.md`
  - `.codex/experience/schedule-trigger-closure.md`

## 巡检结论

这轮 `prod` 不是假健康。当前 live 现场已经收口为：

- `running`: 保底巡检 `node-sti-20260411-da973892 / arun-20260411-172634-057cab`
- `ready`: 主线 `node-sti-20260411-5d1c8181`
- `future`: 主线 `sch-20260405-56eee156 -> 2026-04-11T17:56:00+08:00`；保底 `sch-20260405-67a89536 -> 2026-04-11T18:26:00+08:00`

我直接核了当前巡检 run 的磁盘真相：`run.json` 仍是 `status=running / provider_pid=43904 / latest_event_at=2026-04-11T17:41:23+08:00`，同时 `Win32_Process(ProcessId=43904)` 也确认为真实 `node.exe -> codex.js exec` 链路。全局主图当前是 `1 running / 1 ready / 6 pending`，所以这轮既不是“0 running + ready 堆积”的假健康，也没有丢掉下一棒出口。

当前 active 版本继续是 `V1`，本轮最高价值泳道继续是 `工程质量探测`，生命周期阶段继续是 `变更控制`。这轮最该推进的动作不是再挂新 helper，也不是自己触发正式升级，而是把 future schedule 的 prompt 真相收住，并补齐 fresh watcher 证据。

## 发布边界

当前真正的 release boundary 是：

- `developer_id=pm-main`
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=待切批`
- `workspace_head=code_root_head=7822016`
- 上游参考：`pm-main / workflow_code -> ## main...origin/main [ahead 7]`

也就是说，本轮出现的 `ahead 7` 只代表本机 `pm-main / workflow_code` 相对 `origin/main` 已有 7 个未上推的本地提交；相对本机代码根仓本身仍是 `clean_synced`，不构成本轮 dirty/ahead 异常。

我这轮在 `2026-04-11T17:37:58+08:00` 首次、`2026-04-11T17:40:42+08:00 ~ 2026-04-11T17:40:43+08:00` 再次用当前工作区模板回写 `sch-20260405-56eee156 / sch-20260405-67a89536`，把它们的 future `launch_summary` 都重新刷回：

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `push_block_reason=-`
- `workspace_head=code_root_head=7822016`

当前正在运行的保底节点 `node-sti-20260411-da973892` 仍保留 `16:21` materialize 时的历史 snapshot；这属于已 materialize 的历史节点，我这轮没有回写它的当前 prompt，只修 future schedule 本身。

## 升级门禁

这轮没有执行 `/api/runtime-upgrade/apply`。当前 `/api/runtime-upgrade/status` 是：

- `current_version=20260411-093051`
- `candidate_version=20260411-173655`
- `running_task_count=1`
- `blocking_reason=存在运行中任务，暂不可升级`
- `can_upgrade=false`

`logs/runs/prod-idle-upgrade-watchdog-live.md` 已在 `2026-04-11T17:38:24+08:00` 写入 fresh 单次检查结果，明确这轮仍是：

- `candidate_is_newer=true`
- `running_task_count=1`
- `can_upgrade=false`
- `当前仍未到可升级空窗，单次检查跳过`

我还补核了托管链：

- `start_workflow_env.ps1 -Environment prod -SkipBackfill` supervisor 进程仍在：`PID=38948`
- 当前 `launch_workflow.ps1` 子进程：`PID=44208`
- 当前 web 进程：`PID=63136`

所以这轮不存在“supervisor 缺失导致 watcher 根本不在”的误判；当前仍应继续由 `prod` supervisor 托管的 idle watcher 在真正空窗时发起升级，而不是由这条巡检节点自己 `apply`。

## Helper 判断

这轮我没有新挂 helper 任务，因为当前并不存在“执行者缺位就会断链”的现场：

- `agent_registry.runtime_status` 中 `workflow_bugmate / workflow_devmate / workflow_qualitymate / workflow_testmate` 当前都是 `idle`
- 当前主链断点不在 helper 缺位，而在 old prod 仍会按 `20260411-093051` 的旧 release-boundary 语义回写 future schedule
- `role_creation_sessions` 里若仍能看到 `workflow_testmate / workflow_qualitymate=creating`，也只属于历史 residue，不再是 live 锁

因此当前最值得做的不是再补派一个 helper，而是继续盯 `17:56 / 18:26` 这一棒以及首个空窗里的正式升级。

## 下一次建议

- 主线下一观察点：`2026-04-11T17:56:00+08:00`
- 保底下一观察点：`2026-04-11T18:26:00+08:00`
- 升级观察点：当前巡检节点释放后、且没有新的 `workflow` live running 占住槽位的首个空窗，继续核对 idle watcher 是否把 `candidate=20260411-173655` 接入 live `prod`
- 异常门槛：
  - 如果 `17:56` 主线到点后没有新的 live run，就按 handoff 异常继续处理
  - 如果首个空窗后 `current_version` 仍停在 `20260411-093051`，或 active schedule 又把 `launch_summary` 漂回过期快照，就把 `prod supervisor / idle watcher` 验证或重启提升为下一条受支持治理批次

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
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-56eee156'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-67a89536'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-da973892'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-5d1c8181'`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-172634-057cab/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-172634-057cab/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- `logs/runs/prod-idle-upgrade-watchdog-live.md`
- `Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in 38948,44208,63136,43904 }`
