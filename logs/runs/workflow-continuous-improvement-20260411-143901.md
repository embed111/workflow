# Continuous Improvement Report

- generated_at: `2026-04-11T14:44:20+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-5ef83a73`
- graph_name: `任务中心全局主图`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`

## Root Sync
- launch_snapshot:
  - `root_sync_state=ahead_clean`
  - `ahead_count=5`
  - `dirty_tracked_count=0`
  - `untracked_count=0`
  - `push_block_reason=unpushed_commits_present`
  - `next_push_batch=待切批`
  - `workspace_head=c55e357 / code_root_head=c55e357`
- current_snapshot:
  - `developer_id=pm-main`
  - `root_sync_state=clean_synced`
  - `ahead_count=0`
  - `dirty_tracked_count=0`
  - `untracked_count=0`
  - `push_block_reason=-`
  - `next_push_batch=待切批`
  - `workspace_head=code_root_head=c55e357`
  - upstream_reference: `pm-main / workflow_code -> ## main...origin/main [ahead 5]`

## Change Control
- baseline 继续沿用 `prod=20260411-093051`。
- 本轮没有新增代码改动、没有新增 baseline，也没有触发 runtime upgrade；当前仍属于 `V1-P2` 的 live 真相收口。
- 本轮把“下一轮 prompt 继续沿用旧 release boundary 快照”的问题收成了受支持 runtime 修正，而不是继续只把它记成口头风险：
  - `sch-20260405-56eee156` 与 `sch-20260405-67a89536` 已在 `2026-04-11T14:39:01+08:00` 重写为 `clean_synced(c55e357)` 的最新计划文案。
  - 当前正在运行的 `node-sti-20260411-5ef83a73` 仍保留命中时刻的旧 `ahead_clean` snapshot；这只影响本轮 in-flight node，不再影响后续 future schedule。
- 当前仍保留两条后续治理关注点：
  - `/api/status.active_version=disabled` 仍与版本计划 `V1 active` 分叉。
  - `logs/runs/prod-idle-upgrade-watchdog-live.md` 仍缺失，idle watcher fresh single-check 证据未补齐。

## Actions
- 重新按工作区读链、版本计划、持续唤醒需求与发布边界方案复核当前 `V1 / V1-P2 / 工程质量探测 / 变更控制` 口径。
- 核对 `pm-main / ../workflow_code` 的 live Git 真相，确认当前 release boundary 仍是 `clean_synced / c55e357`，launch summary 里的 `ahead_clean / ahead_count=5` 已过期。
- 复核 `healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status`、全局主图与 `status-detail`，确认当前主链真实 running 为 `node-sti-20260411-5ef83a73 / arun-20260411-142534-ad3833`。
- 直读 `run.json`，确认当前 run 仍在推进：`status=running / provider_pid=54692 / latest_event_at=2026-04-11T14:37:55+08:00`。
- 对当前主线节点做 exclusion 版升级门禁复核，确认排除 `node-sti-20260411-5ef83a73` 后 `candidate=20260411-131835` 已满足 `candidate_is_newer=true / can_upgrade=true`；默认门禁仍被当前 running task 挡住。
- 通过当前工作区代码模板直接回写 live `prod` 的两条 future schedule，刷新：
  - `[持续迭代] workflow -> sch-20260405-56eee156`
  - `pm持续唤醒 - workflow 主线巡检 -> sch-20260405-67a89536`
- 确认两条 schedule 的 `launch_summary` 已改为 `root_sync_state=clean_synced ; ahead_count=0 ; push_block_reason=-`，并先保留 `next_trigger_at=2026-04-11T14:40:00+08:00 / 2026-04-11T15:10:00+08:00`。
- 在 `2026-04-11T14:40:04+08:00` 之后继续回读 live 图谱，确认新命中的主线节点 `node-sti-20260411-6536efb7` 已进入 `ready`，并且它的 `node_goal / launch_summary_snapshot` 已经读到刚刷新的 `clean_synced(c55e357)` 文案。
- 同步回写版本计划最新快照、月度现场总览、会话快照、运行留痕、经验卡与今日日记。

## Validation
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-56eee156'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-67a89536'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-5ef83a73'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-5ef83a73'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-56eee156'`（二次复核 `14:40` recent trigger snapshot）
- `Get-Content -Raw 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-142534-ad3833/run.json'`
- `Get-Content -Raw .running/control/prod-last-action.json`
- `if (Test-Path logs/runs/prod-idle-upgrade-watchdog-live.md) { Get-Content -Raw logs/runs/prod-idle-upgrade-watchdog-live.md } else { '__MISSING__' }`
- `@'... '@ | python -` 调用 `assignment_self_iteration_runtime` 与 `schedule_service.update_schedule(...)` 刷新两条 future schedule 文案

## Live Runtime
- `healthz`：`2026-04-11T14:37:55+08:00` 返回 `ok=true`
- `/api/status.assignment_workboard_summary`：`1 running / 0 queued / 10 failed / 9 blocked`
- `workflow` agent live workboard：`1 running + 1 ready`
- 当前 running 节点：`node-sti-20260411-5ef83a73 / arun-20260411-142534-ad3833`
- 当前 run：`status=running / provider_pid=54692 / latest_event_at=2026-04-11T14:37:55+08:00`
- 当前 `prod`：`current_version=20260411-093051`
- 当前 `candidate`：`20260411-131835`
- 默认升级门禁：`running_tasks_present / can_upgrade=false`
- 排除当前主线节点后：`candidate_is_newer=true / can_upgrade=true`
- 当前接力出口（截至 `2026-04-11T14:44:20+08:00`）：
  - 主线 ready：`node-sti-20260411-6536efb7 / 2026-04-11T14:40:00+08:00`
  - 保底 future：`sch-20260405-67a89536 -> 2026-04-11T15:10:00+08:00`
- future schedule 文案刷新时间：`2026-04-11T14:39:01+08:00`
- 修正生效验证：`node-sti-20260411-6536efb7.node_goal` 已读到 `root_sync_state=clean_synced ; ahead_count=0 ; push_block_reason=-`
- 当前 watcher 留痕：`logs/runs/prod-idle-upgrade-watchdog-live.md -> missing`

## Next
- 当前泳道/阶段继续记为：`工程质量探测 / 变更控制`
- 主线 next：`2026-04-11T14:40:00+08:00`
- 保底 next：`2026-04-11T15:10:00+08:00`
- 下一观察点：
  - 当前已确认 `14:40` 新命中的主线节点 `node_goal / launch_summary_snapshot` 已读到 `clean_synced(c55e357)` 的新文案；下一步改为观察它在 `14:25` 旧主线收尾后是否能自动从 `ready` 接成真实 `running`。
  - 若空窗后 `candidate=20260411-131835` 仍未被接入，且 `logs/runs/prod-idle-upgrade-watchdog-live.md` 仍缺失，则把 `prod supervisor / idle watcher` 的 fresh single-check 验证或重启提升为下一条受支持治理批次。
  - `/api/status.active_version=disabled` 仍作为 `V1-P2` 的下一个代码侧真相收口点。

## Memory
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
