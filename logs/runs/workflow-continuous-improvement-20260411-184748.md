# Continuous Improvement Report

- generated_at: `2026-04-11T18:47:48+08:00`
- active_version: `V1`
- task_package: `V1-P2B`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- preference_ref: `state/user-preferences.md`
- delta_observation: `18:32` 主线已从 `ready waiting handoff` 切成真实 `running`；当前阻塞继续是 live `prod=20260411-093051` 尚未切到 `candidate=20260411-173655`，不是 `pm-main / ../workflow_code` 未同步。
- delta_validation: 我重新核对了 `healthz / status / schedules / status-detail / run.json / events.log`、`pm-main / ../workflow_code` Git 真相、`runtime-upgrade/status`、release-boundary 口径文件与 `prod` supervisor 进程链。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- 当前根仓同步真相仍是 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批`，`pm-main` 与 `../workflow_code` 继续对齐在 `7822016`；两边相对 `origin/main` 都是 `ahead 7`，但只保留为上游参考，不构成本轮阻塞。
- live `prod` 当前仍停在 `20260411-093051`，更高 `candidate=20260411-173655` 已通过门禁但仍在等待空窗；这轮继续不自行调用 `/api/runtime-upgrade/apply`。
- 当前真实 running 已切到主线 `node-sti-20260411-9e003113 / arun-20260411-184035-9edeec`；`run.json` 显示 `status=running / provider_pid=14576 / latest_event_at=2026-04-11T18:45:25+08:00`。
- 当前任务图真相已经推进到 `1 running / 0 ready / 6 pending`；连续推进出口收口为当前主线 `running`、下一条主线 future `sch-20260405-56eee156 -> 2026-04-11T18:55:00+08:00`，以及保底 future `sch-20260405-67a89536 -> 2026-04-11T19:25:00+08:00`。
- 两条 live schedule prompt 仍带着 `root_sync_state=ahead_clean ; ahead_count=7 ; push_block_reason=unpushed_commits_present` 旧 snapshot；当前主线 schedule 已变成 `last_result_status=running / last_result_summary=dispatch_requested / updated_at=2026-04-11T18:41:01+08:00`，保底 schedule 则已是 `last_result_status=succeeded / updated_at=2026-04-11T18:40:41+08:00`。
- 当前工作区与本机代码根仓的 `release_boundary_service.py` 已收口成“只以本机 `../workflow_code` clean_synced 为准，GitHub / origin 默认只作参考”的新口径；live 部署副本同名文件仍保留旧的 `code_root_local_repo_ahead_origin_main` 逻辑，这正是 live schedule prompt 继续回漂的直接原因。
- `prod` 托管链当前仍在：`.running/control/prod-last-action.json` 显示最后一次成功升级停在 `2026-04-11T01:35:04Z -> 20260411-093051`，`start_workflow_env.ps1` supervisor 仍在（`PID=38948`），`launch_workflow.ps1` 子进程为 `PID=44208`，web 进程为 `PID=63136`。
- 当前真正阻塞已经进一步收口成“当前主线本身仍占着 running 槽，idle upgrade 还没机会把 `20260411-173655` 切进 live prod”，而不是“当前工作区未 clean_synced”或“helper 缺位”。
- `/api/status.active_version=disabled` 仍然和版本计划里的 `V1 active` 分叉，这条语义分叉本轮继续保留为显式风险。
- 本轮没有新增代码改动，也没有补挂 helper；当前最有价值的动作是把现场真相回写清楚，让下一棒把“当前主线结束后的首个 idle 窗口是否自动升级到 `20260411-173655`”当成受支持治理判断，而不是继续误读成工作区没收口。

## 现场判断
- 本轮沿用 baseline：`prod=20260411-093051`；没有 baseline 更新，也没有新增代码变更控制批次。
- 当前最高价值泳道继续记为 `工程质量探测`，生命周期阶段继续记为 `变更控制`；本轮聚焦的仍是 `V1-P2B 真相源统一`。
- 当前 release boundary 继续按 `clean_synced(7822016)` 记录；schedule prompt 里的 `ahead_clean` 已明确降级成“现网旧代码尚未升级”的症状，而不是新的 Git 边界异常。
- 这轮命中了 7x24 现场治理判断，但当前还没有真正出现可升级空窗，所以我只做受支持的观察动作：重核 live `runtime-upgrade/status`、比对 workspace/prod 两份 `release_boundary_service.py`、确认主线 live run 真相与 `prod` supervisor 进程链仍在。
- 当前 helper 不存在 live `creating` 锁，也没有 ready 节点断链；这轮不补挂 helper，避免在升级门禁尚未释放前继续扩现场噪声。
- 当前主线 run 仍在进行中，所以这轮还不需要直接升级到 `supervisor / idle watcher` 重启；更合理的门槛是等当前主线释放后的首个 idle 窗口。如果空窗后仍不自动升级，或 `18:55 / 19:25` 两条 live schedule prompt 继续回漂旧 snapshot，再把 `prod supervisor / idle watcher` 验证或重启提升为下一条受支持治理批次。

## 验证证据
- `Get-Date -Format o`
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-9e003113'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Get-Content -Raw 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-184035-9edeec/run.json'`
- `Get-Content 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-184035-9edeec/events.log' -Tail 120`
- `Get-Content 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl' -Tail 20`
- `Select-String -Path .repository/pm-main/src/workflow_app/server/services/release_boundary_service.py -Pattern 'code_root_local_repo_ahead_origin_main|origin/main|clean_synced'`
- `Select-String -Path .running/prod/src/workflow_app/server/services/release_boundary_service.py -Pattern 'code_root_local_repo_ahead_origin_main|origin/main|clean_synced'`
- `Get-Content .running/control/prod-last-action.json`
- `Get-Content .running/control/instances/prod.json`
- `Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in 38948,44208,63136 } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Depth 5`
- `Get-Content -Tail 12 logs/runs/prod-idle-upgrade-watchdog-live.md`

## 下一步
- 主线 next: 当前 live run=`node-sti-20260411-9e003113 / arun-20260411-184035-9edeec`；下一次主线 future=`sch-20260405-56eee156 -> 2026-04-11T18:55:00+08:00`
- 保底 next: `sch-20260405-67a89536 -> 2026-04-11T19:25:00+08:00`
- 升级 next: 等当前主线释放 running 槽后，继续看 idle watcher 是否把 `candidate=20260411-173655` 接入 live `prod`
- 治理 next: 若首个空窗后 `current_version` 仍停在 `20260411-093051`，或 `18:55 / 19:25` 两条 live schedule prompt 继续沿用旧 `ahead_clean / unpushed_commits_present` 文案，下一轮优先验证或重启 `prod supervisor / idle watcher`
