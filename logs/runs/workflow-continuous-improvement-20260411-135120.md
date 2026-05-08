# Continuous Improvement Report

- generated_at: `2026-04-11T13:51:20+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-cf74d996`
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
- 本轮没有新增代码改动，也没有新增 baseline；当前工作仍归入 `V1-P2` 的 live 真相收口。
- 本轮最高价值动作是把“本地 release boundary 已 clean_synced”与“live prod 仍在旧版本上执行旧 launch summary”拆开确认，并把 idle watcher 的证据缺口钉成明确阻塞。

## Actions
- 重新核对 `pm-main / ../workflow_code` 的 Git 真相，确认当前本地边界已是 `clean_synced / c55e357`，`ahead 5` 只存在于相对 `origin/main` 的上游参考层。
- 复核 `healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status`、当前节点 `status-detail` 与 live `run.json`，确认主链当前真实 running 为 `node-sti-20260411-cf74d996 / arun-20260411-134307-c775a1`，下一次主线/保底 future 仍保留在 `2026-04-11T13:58:00+08:00 / 2026-04-11T14:12:00+08:00`。
- 对当前主线节点做 exclusion 版升级门禁复核，确认排除 `node-sti-20260411-cf74d996` 后 `candidate=20260411-131835` 已满足 `candidate_is_newer=true / can_upgrade=true`，因此当前阻塞只剩“主线仍在 running 槽里”。
- 直接查看当前节点 `node_goal` 与 run prompt ref，确认 live prod 这轮仍携带 `root_sync_state=ahead_clean / ahead_count=5 / push_block_reason=unpushed_commits_present` 的旧 launch summary；这不是当前工作区回退，而是当前 `prod=20260411-093051` 仍在使用旧一轮 schedule metadata。
- 复核 `prod` supervisor 进程、`prod-last-action.json`、`envs/prod.json` 和 watcher 留痕，确认当前 watchdog 进程 `PID=38948` 自 `2026-04-10T20:43:24+08:00` 起存活，但工作区内缺少 fresh `logs/runs/prod-idle-upgrade-watchdog-live.md`；目前只剩历史 `logs/runs/prod-idle-upgrade-watcher-live-20260408-211647.md`，因此本轮无法证明 idle watcher 已对 `20260411-131835` 跑过单次检查。
- 同步回写 `PM版本推进计划.md`、月度现场总览、运行留痕与今日日记，把这轮 live 结论压回真相源。

## Validation
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-cf74d996'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-cf74d996'`
- `Get-CimInstance Win32_Process | Where-Object { ($_.CommandLine -like '*start_workflow_env.ps1*') -or ($_.CommandLine -like '*apply_prod_candidate_when_idle.py*') }`
- `Get-Process -Id 38948 | Select-Object Id, ProcessName, StartTime, CPU, Path`
- `Get-Content -Raw .running/control/prod-last-action.json`
- `Get-Content -Raw .running/control/envs/prod.json`
- `Test-Path logs/runs/prod-idle-upgrade-watchdog-live.md`
- `Get-Content logs/runs/prod-idle-upgrade-watcher-live-20260408-211647.md -Tail 80`
- `@'... '@ | python -` 读取 `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-134307-c775a1/run.json`

## Live Runtime
- `healthz`：`2026-04-11T13:45:21+08:00` 返回 `ok=true`
- 当前 running 节点：`node-sti-20260411-cf74d996 / arun-20260411-134307-c775a1`
- `run.json`：`status=running / provider_pid=45920 / latest_event_at=2026-04-11T13:51:20+08:00`
- 当前 `prod`：`current_version=20260411-093051`
- 当前 `candidate`：`20260411-131835`
- 默认升级门禁：`running_tasks_present / can_upgrade=false`
- 排除当前主线节点后：`candidate_is_newer=true / can_upgrade=true`
- 当前 future 出口：
  - 主线：`2026-04-11T13:58:00+08:00`
  - 保底：`2026-04-11T14:12:00+08:00`
- 当前 supervisor/watchdog：
  - `start_workflow_env.ps1` 进程：`PID=38948 / started_at=2026-04-10T20:43:24+08:00`
  - fresh watchdog log：`missing (logs/runs/prod-idle-upgrade-watchdog-live.md)`

## Warnings
- `/api/status` 仍返回 `active_version=disabled`，与版本计划中的 `V1 active` 存在语义分叉；这轮只先把它固定为 `V1-P2` 的后续真相收口项。
- 当前 running 节点 `node-sti-20260411-cf74d996` 的 `node_goal/prompt` 仍带旧 `root_sync_state=ahead_clean / ahead_count=5 / push_block_reason=unpushed_commits_present` 快照；这被明确视为 live `prod=20260411-093051` 的旧 schedule metadata，不是当前工作区 release boundary 回退。
- `logs/runs/prod-idle-upgrade-watchdog-live.md` 当前缺失，工作区内只看到历史 `prod-idle-upgrade-watcher-live-20260408-211647.md`；在“不由主线自行 apply”的约束下，本轮还不能证明 idle watcher 已对 `candidate=20260411-131835` 跑过 fresh single-check。
- 当前没有新增 helper 任务；理由是主线与保底 future 已经续挂，四个 helper 当前也都处于 `idle/ready` 协作态，而不是 live `creating` 锁。

## Next
- 继续沿用 `V1 / V1-P2 / 工程质量探测 / 变更控制`，等待当前 `node-sti-20260411-cf74d996` 收尾后的空窗。
- 下一次主线触发：`2026-04-11T13:58:00+08:00`
- 下一次保底巡检：`2026-04-11T14:12:00+08:00`
- 若空窗后 `current_version` 仍停在 `20260411-093051`，或 fresh `prod-idle-upgrade-watchdog-live.md` 仍未出现，就把“prod supervisor / idle watcher 单次检查未留痕”升级为下一条 `V1-P0 / V1-P2` 受支持治理批次，在安全窗口内优先验证或重启 supervisor。
- 待 `candidate=20260411-131835` 真正切入 live `prod` 后，继续复核新的主线/保底 launch summary 与新建节点 prompt 是否都继承 `clean_synced / c55e357`。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求我不要把调度 prompt 里的旧 release boundary 当成 live 真相，也不要在主线节点里自行触发正式升级；必须把 current node、candidate、watcher 证据和下一次绝对触发时间一起说清。
- delta_validation: 我已确认本地 `pm-main / workflow_code` 实际是 `clean_synced(c55e357)`，当前阻塞只剩 live `prod=20260411-093051` 仍在运行旧 launch summary 且 fresh watchdog 日志缺失；主线与保底下一次触发已分别明确到 `2026-04-11T13:58:00+08:00 / 2026-04-11T14:12:00+08:00`。
