# workflow-pm-wake-summary

- checked_at: `2026-04-11T20:37:47+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-925e5ca2`
- run_id: `arun-20260411-203337-73dea5`
- active_version: `V1`
- task_package: `V1-P2 发布链与工作区防漂移收口`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260411-093051`
- launch_release_boundary_snapshot: `root_sync_state=ahead_clean / ahead_count=8 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=unpushed_commits_present / next_push_batch=待切批 / workspace_head=1cd76c8 / code_root_head=1cd76c8`
- live_release_boundary: `developer_id=pm-main / root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批 / workspace_head=code_root_head=806aef2 / upstream_ref=origin ahead 9`
- preference_ref: `state/user-preferences.md`
- delta_observation: 当前现场已经切到 `20:21` 保底巡检 live running、`19:51` 主线 ready，以及 `20:48 / 21:18` future；当前不是 `ready` 堆积但无 live run 的假健康，但 live `prod` 仍停在旧 release-boundary prompt 语义上。
- delta_validation: 我已重新核对 `pm-main / workflow_code` 的 git 真相、`prod` 的 status/runtime-upgrade/schedules、任务图、当前巡检 run 文件、assignment audit、`prod-last-action` 与 idle watcher 留痕，并把最新快照回写到版本计划、月度现场和今日日记。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- experience_refs:
  - `.codex/experience/runtime-upgrade-and-agent-monitoring.md`
  - `.codex/experience/schedule-trigger-closure.md`

## 巡检结论

这轮 `prod` 不是假健康。当前 live 现场已经收口为：

- `running`: 保底巡检 `node-sti-20260411-925e5ca2 / arun-20260411-203337-73dea5`
- `ready`: 主线 `node-sti-20260411-4fca706e / [持续迭代] workflow / 2026-04-11 19:51:00`
- `future`: 主线 `sch-20260405-56eee156 -> 2026-04-11T20:48:00+08:00`，保底 `sch-20260405-67a89536 -> 2026-04-11T21:18:00+08:00`

我直接核了当前巡检 run 的磁盘真相：`run.json` 仍是 `status=running / provider_pid=33900 / latest_event_at=2026-04-11T20:36:57+08:00`，当前 dispatch 审计是 `aaud-20260411-203347-cf5237 @ 2026-04-11T20:33:36+08:00`。当前全局主图也已经收口为 `1 running / 1 ready / 6 pending`，并且 `/api/status` 明确给出 `queued_task_count=1 / workflow_mainline_handoff_pending=true`，说明现在只是“保底巡检仍在运行，真正的 [持续迭代] workflow 还在待接棒”，不是 `0 running + ready` 堆积。

当前 active 版本继续是 `V1`，本轮最高价值泳道继续是 `工程质量探测`，生命周期阶段继续是 `基于基线测试`。这轮最该推进的动作仍不是再挂新 helper，也不是由当前节点自己触发正式升级，而是继续盯住 `20:21` 巡检释放后的主线 handoff 和首个 idle upgrade 空窗。

## 发布边界

本轮需要同时区分“当前节点自带的启动快照”和“live 真相”：

- 当前 `20:21` 巡检节点 prompt 里仍带着旧快照：`root_sync_state=ahead_clean / ahead_count=8 / workspace_head=1cd76c8 / push_block_reason=unpushed_commits_present`
- 当前 live 工作区真相已经是：`pm-main` 与 `../workflow_code` 都在 `806aef2`，相对本机代码根仓是 `clean_synced`，`origin/main ahead 9` 只作上游参考
- `/api/schedules` 当前 future 文本已经切到 `workspace_head=806aef2`，但仍按旧逻辑写成 `ahead_clean / ahead_count=9 / unpushed_commits_present`

也就是说，本轮看到的 `ahead_clean / unpushed_commits_present` 不是新的 dirty/ahead 异常，而是 live `prod=20260411-093051` 还没切到包含新 release-boundary 读链的 candidate，导致当前 running 节点和 future schedule 仍沿用旧语义回写。

## 升级门禁

这轮没有执行 `/api/runtime-upgrade/apply`。当前 `/api/runtime-upgrade/status` 是：

- `current_version=20260411-093051`
- `candidate_version=20260411-202044`
- `candidate_is_newer=true`
- `request_pending=false`
- `running_task_count=1`
- `blocking_reason=存在运行中任务，暂不可升级`
- `can_upgrade=false`

我还补核了托管链：

- `.running/control/prod-last-action.json` 仍显示最后一次成功升级完成于 `2026-04-11T01:35:04Z -> 20260411-093051`
- `logs/runs/prod-idle-upgrade-watchdog-live.md` 最近一次单次检查是 `2026-04-11T20:22:51+08:00`，当时因为 `running_task_count=1 / can_upgrade=false` 跳过
- 当前 `start_workflow_env.ps1` supervisor、`launch_workflow.ps1` 子进程和 web 进程仍都在

所以这轮并不存在“watcher 根本没在”或“当前巡检节点应该自己 apply”的结论；当前仍应继续由 `prod` supervisor 托管的 idle watcher 在真正空窗时发起升级。

## Helper 判断

这轮我没有新挂 helper 任务，因为当前并不存在“执行者缺位就会断链”的现场：

- `workflow_bugmate / workflow_devmate / workflow_testmate / workflow_qualitymate` 当前都在 `idle`
- 当前断点不在 helper 缺位，而在当前巡检占着 running 槽、主线仍待 handoff，以及 live `prod` 还没等到 idle upgrade 空窗

因此当前最值得做的不是再补派一个 helper，而是继续盯 `node-sti-20260411-925e5ca2 -> node-sti-20260411-4fca706e` 这一棒，以及首个 idle 窗口里的正式升级。

## 下一次建议

- 主线下一观察点：先等当前巡检 `node-sti-20260411-925e5ca2 / arun-20260411-203337-73dea5` 释放，再看 `node-sti-20260411-4fca706e` 是否自动 dispatch 成真实 run
- future 下一观察点：`sch-20260405-56eee156 -> 2026-04-11T20:48:00+08:00` 与 `sch-20260405-67a89536 -> 2026-04-11T21:18:00+08:00` 已经挂上；当前不需要额外补链
- 升级观察点：首个真正 idle 窗口里继续核对 idle watcher 是否把 `candidate=20260411-202044` 接入 live `prod`
- 异常门槛：
  - 如果 `node-sti-20260411-4fca706e` 在当前巡检收尾后仍长期停在 `ready`，或 `2026-04-11T20:48:00+08:00` 命中后仍没有新的 live mainline run，就按 handoff 异常继续处理
  - 如果首个真正 idle 窗口后 `current_version` 仍停在 `20260411-093051`，下一轮优先验证 `prod supervisor / idle watcher`

## 证据

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `docs/workflow/reports/7x24发布边界收口方案-20260409.md`
- `docs/workflow/governance/pm-version-live/2026-04/现场更新总览.md`
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-925e5ca2'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-4fca706e'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/agents'`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-203337-73dea5/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-203337-73dea5/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
- `.running/control/prod-last-action.json`
- `logs/runs/prod-idle-upgrade-watchdog-live.md`
