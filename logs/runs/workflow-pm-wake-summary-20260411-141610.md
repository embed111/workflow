# workflow-pm-wake-summary

- checked_at: `2026-04-11T14:16:10+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-d7823bfd`
- run_id: `arun-20260411-141221-9f5e23`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- experience_ref: `.codex/experience/runtime-upgrade-and-agent-monitoring.md`

## 巡检结论

这轮 `prod` 不是假健康。当前真实现场已经收口为：

- `running`: `node-sti-20260411-d7823bfd / arun-20260411-141221-9f5e23`
- `ready`: `none`
- `future`: 主线 `2026-04-11T14:25:00+08:00`

我直接核了当前巡检 run 的磁盘真相：`run.json` 仍是 `status=running / provider_pid=63708 / latest_event_at=2026-04-11T14:16:10+08:00`，`events.log` 也已经持续写到本轮的工具执行阶段。所以这轮不是“0 running + ready 堆积”的假健康，而是保底巡检自己仍在真实执行；在它收尾前，任务图里没有新的 `ready` 主线节点，但主线 future 已经保住到 `2026-04-11T14:25:00+08:00`。

当前 active 版本继续是 `V1`，当前最该推进的任务包仍是 `V1-P2`，泳道与生命周期阶段继续记为 `工程质量探测 / 变更控制`。这轮最高价值动作不是扩功能或顺手再挂 helper，而是把 live 运行真相、升级门禁和 release boundary 旧 metadata 的分叉一起钉实。

## 发布边界

这轮命中的旧快照仍然过期：

- 调度 prompt 与 `/api/schedules` launch summary 仍带着 `root_sync_state=ahead_clean / ahead_count=5 / push_block_reason=unpushed_commits_present`
- live 当前节点 `node_goal` 也沿用了同一组旧 metadata

我按 live Git 真相重算后，当前真正的 release boundary 是：

- `developer_id=pm-main`
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=待切批`
- `workspace_head=code_root_head=c55e357`
- 上游参考：`pm-main / workflow_code -> ## main...origin/main [ahead 5]`

也就是说，这轮没有新的 dirty/ahead 历史包袱，不需要再切发布边界收口动作；真正需要继续收口的是 schedule metadata 仍在引用旧快照，而不是本地工作区真的又脏了。

## 升级门禁

当前没有执行 `/api/runtime-upgrade/apply`。默认 `/api/runtime-upgrade/status` 为：

- `current_version=20260411-093051`
- `candidate_version=20260411-131835`
- `running_task_count=1`
- `blocking_reason=running_tasks_present`
- `can_upgrade=false`

按当前巡检节点排除 `node-sti-20260411-d7823bfd` 后，门禁回落为：

- `running_task_count=0`
- `candidate_is_newer=true`
- `can_upgrade=true`

所以这轮不存在“已经空窗却漏升”的判断问题；当前仍应继续由 `prod` supervisor 托管的 idle watcher 在真正空窗时发起升级，而不是由这条巡检节点自己 `apply`。

## Helper 判断

这轮我没有新挂 helper 任务，原因不是忽略泳道，而是当前没有新的 live 执行者缺口：

- 当前全局主图的 active 非 `workflow` 节点只剩历史 `pending/blocked` 链
- `workflow_qualitymate` 当前只剩旧 `rc-64b429-*` pending/blocked 链
- `workflow_testmate` 当前只剩旧 `rc-9675f0-*` pending/blocked 链
- `workflow_bugmate` 当前只剩旧 `dr-20260404-9ac9b604c9-*` pending/blocked 链

这类节点是历史 backlog，不是“现在缺个 live 执行者就会断链”的现场。当前关键路径仍是 `workflow(pm)` 先把这条保底巡检收好，并继续观察空窗升级与 metadata 真相分叉。

## Watchdog 观察

- `start_workflow_env.ps1 -Environment prod -SkipBackfill` 的 supervisor 进程还在
- `.running/control/prod-last-action.json` 仍显示最近一次成功升级停在 `20260411-093051`
- 工作区里 fresh `logs/runs/prod-idle-upgrade-watchdog-live.md` 仍缺失，只能看到历史 `logs/runs/prod-idle-upgrade-watcher-live-20260408-211647.md`

所以这轮最值得继续盯的不是“能不能升级”，而是空窗到来后 idle watcher 是否真的会留下 fresh single-check 证据并把 `candidate=20260411-131835` 接进 live `prod`。

## 下一次建议

- 主线下一观察点：`2026-04-11T14:25:00+08:00`
- 保底下一建议点：`2026-04-11T15:25:00+08:00`
  - 这是按当前机制从主线 future `14:25` 再加 `60` 分钟推断的建议时间；当前巡检节点还在 running，schedule 详情尚未回写新的保底 future
- 升级观察点：等这条巡检节点收尾后的空窗，核对 idle watcher 是否把 `candidate=20260411-131835` 切进 live `prod`
- 异常门槛：
  - 如果 `14:25` 主线到点后找不到新的 live run，就按主线 handoff 异常继续处理
  - 如果空窗后 `current_version` 仍停在 `20260411-093051`，或 fresh watchdog 日志仍缺失，就把它升级成下一条 `V1-P0 / V1-P2` 受支持治理批次

## 证据

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `docs/workflow/reports/7x24发布边界收口方案-20260409.md`
- `git -C .repository/pm-main status --short --branch`
- `git -C ../workflow_code status --short --branch`
- `git -C .repository/pm-main status --porcelain=v1`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-d7823bfd'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-d7823bfd'`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-141221-9f5e23/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-141221-9f5e23/events.log`
- `.running/control/prod-last-action.json`
- `logs/runs/prod-idle-upgrade-watchdog-live.md`（当前缺失）
- `logs/runs/prod-idle-upgrade-watcher-live-20260408-211647.md`
