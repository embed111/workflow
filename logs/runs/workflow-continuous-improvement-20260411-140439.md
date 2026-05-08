# Continuous Improvement Report

- generated_at: `2026-04-11T14:04:39+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-878e68d7`
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
- 本轮没有新增代码改动，也没有新增 baseline；当前仍属于 `V1-P2` 的 live 真相收口。
- 本轮锁定的下一批次关注点仍是运行态真相分叉，而不是继续扩新功能：
  - `/api/status.active_version=disabled`
  - `[持续迭代] workflow` schedule launch summary 与当前 node goal 继续沿用旧 `ahead_clean / ahead_count=5` 快照
  - `prod` idle watcher 缺 fresh 留痕

## Actions
- 重新核对 `pm-main / ../workflow_code` 的 Git 真相，确认当前本地 release boundary 仍是 `clean_synced / c55e357`，并且 `ahead 5` 只存在于相对 `origin/main` 的上游参考层。
- 复核 `healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status` 和任务图，确认主链当前真实 running 已切到 `node-sti-20260411-878e68d7 / arun-20260411-135848-4323d0`，没有 ready 堆积假健康。
- 直读 `run.json`，确认当前 run 仍在推进：`provider_pid=49224 / started_at=2026-04-11T13:58:47+08:00 / latest_event_at=2026-04-11T14:04:39+08:00`。
- 对当前主线节点做 exclusion 版升级门禁复核，确认排除 `node-sti-20260411-878e68d7` 后 `candidate=20260411-131835` 已满足 `candidate_is_newer=true / can_upgrade=true`，因此默认门禁还不放开的唯一原因就是当前主线仍在占用 running 槽。
- 重新核对当前 node goal、`/api/schedules` launch summary 和版本计划快照，确认 live `prod=20260411-093051` 仍在沿用旧一轮 `root_sync_state=ahead_clean / ahead_count=5 / push_block_reason=unpushed_commits_present` metadata；这不是当前工作区 release boundary 回退。
- 复核 `prod-last-action.json` 和 watcher 留痕，确认当前工作区仍缺 fresh `logs/runs/prod-idle-upgrade-watchdog-live.md`，只能看到历史 `logs/runs/prod-idle-upgrade-watcher-live-20260408-211647.md`。
- 同步回写 `PM版本推进计划.md`、月度现场总览、会话快照、运行留痕与今日日记，把这轮 live 结论压回当前真相源。

## Validation
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-878e68d7'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-878e68d7'`
- `Get-Content -Raw 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-135848-4323d0/run.json'`
- `Get-Content -Raw .running/control/prod-last-action.json`
- `if (Test-Path logs/runs/prod-idle-upgrade-watchdog-live.md) { Get-Content -Raw logs/runs/prod-idle-upgrade-watchdog-live.md } else { '__MISSING__' }`
- `Get-Content -Tail 120 logs/runs/prod-idle-upgrade-watcher-live-20260408-211647.md`

## Live Runtime
- `healthz`：`2026-04-11T14:01:45+08:00` 返回 `ok=true`
- `/api/status`：`running_task_count=1 / assignment_running_agent_count=1 / active_version=disabled`
- 当前 running 节点：`node-sti-20260411-878e68d7 / arun-20260411-135848-4323d0`
- 当前 run：`status=running / provider_pid=49224 / latest_event_at=2026-04-11T14:04:39+08:00`
- 当前 `prod`：`current_version=20260411-093051`
- 当前 `candidate`：`20260411-131835`
- 默认升级门禁：`running_tasks_present / can_upgrade=false`
- 排除当前主线节点后：`candidate_is_newer=true / can_upgrade=true`
- 当前 future 出口：
  - 保底：`2026-04-11T14:12:00+08:00`
  - 主线：`2026-04-11T14:14:00+08:00`
- 当前 watcher 留痕：`logs/runs/prod-idle-upgrade-watchdog-live.md -> missing`

## Warnings
- `/api/status` 仍返回 `active_version=disabled`，与版本计划中的 `V1 active` 存在语义分叉；这轮只先把它继续固定为 `V1-P2` 的 live 真相收口项。
- 当前 running 节点 `node-sti-20260411-878e68d7` 的 `node_goal` 与 `/api/schedules` launch summary 仍带旧 `root_sync_state=ahead_clean / ahead_count=5 / push_block_reason=unpushed_commits_present` 快照；这来自 live `prod=20260411-093051` 的旧 schedule metadata，不是当前工作区回退。
- `logs/runs/prod-idle-upgrade-watchdog-live.md` 仍缺失；在“不由主线自行 apply”的治理边界下，本轮依然无法证明 idle watcher 已对 `candidate=20260411-131835` 跑过 fresh single-check。
- 本轮没有新挂 helper 任务；当前理由是主线与保底 future 已经保留，四个 helper 也不存在 live `creating` 锁，继续并发挂单的价值低于先把运行态真相分叉钉实。

## Next
- 当前泳道/阶段 next: `工程质量探测 / 变更控制`
- 当前 release boundary next: 继续按 `developer_id=pm-main / clean_synced(c55e357)` 记录，不再复用调度 prompt 里的旧 `ahead_clean / ahead_count=5`
- 升级 next: 继续等待 `node-sti-20260411-878e68d7` 收尾后的空窗，观察 `candidate=20260411-131835` 是否被 idle watcher 接入 live `prod`
- 治理 next:
  - 若空窗后 `current_version` 仍停在 `20260411-093051`，或 fresh watchdog 日志仍缺失，则把 `prod supervisor / idle watcher single-check 未留痕` 升级成下一条 `V1-P0 / V1-P2` 受支持治理批次
  - 若 candidate 成功切入 live `prod`，则优先复核新建主线/保底节点的 launch summary、node goal 与 `/api/status.active_version` 是否已经继承 `clean_synced / c55e357 / V1`
- 主线 next: `[持续迭代] workflow -> 2026-04-11T14:14:00+08:00`
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T14:12:00+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求我不要把调度 prompt 和 schedule launch summary 里的旧 release boundary 当成 live 真相，也不要在主线节点里自己发起正式升级；必须把当前 run、排除当前节点后的升级门禁、以及下一次绝对触发时间一起写清楚。
- delta_validation: 我已确认本地 `pm-main / workflow_code` 实际仍是 `clean_synced(c55e357)`，当前 live run 为 `node-sti-20260411-878e68d7 / arun-20260411-135848-4323d0 / latest_event_at=2026-04-11T14:04:39+08:00`；排除当前主线节点后 `candidate=20260411-131835` 已满足 `can_upgrade=true`，下一次保底/主线触发分别为 `2026-04-11T14:12:00+08:00 / 2026-04-11T14:14:00+08:00`，但 fresh watchdog 日志仍缺失。
