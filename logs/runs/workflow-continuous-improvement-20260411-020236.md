# continuous-improvement-report

- checked_at: `2026-04-11T02:12:06+08:00`
- active_version: `V1`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260411-014504`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
- preference_ref: `state/user-preferences.md`
- delta_observation: `launch_summary 里的根仓异常已经通过 non-destructive fetch 收口；当前 live 真相已经推进到 主线 + workflow_testmate + workflow_qualitymate 三条并行 running。`
- delta_validation: `下一轮优先等待 smoke baseline 和双 running 口径复核结论回传，并确认新一轮 schedule 继续写回 clean_synced / 4fd5c6d。`

## 本轮结论

这轮先按发布边界收口模式处理了 launch summary 里沿用的 `ahead_clean / 待外网恢复后推送 origin/main`，但现场已经继续推进到了 `V1 / 测试探测 / 基于基线测试`。我确认真正的根仓异常并不是新的代码分叉，而是 `../workflow_code` 的 `origin/main` remote-tracking ref 停在旧点位 `c7bbbc4`；随后在 7x24 允许的异常治理窗口内执行了受支持的 non-destructive `git -C ../workflow_code fetch origin`，把 `pm-main / ../workflow_code / origin/main` 一起校准到 `4fd5c6d`。截至本轮收尾，发布边界已经稳定回到 `workspace_head=code_root_head=4fd5c6d / root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待新批次`。

## 运行态真相

当前 `prod` 的 `/healthz` 正常，版本已经是 `current=candidate=20260411-014504`。这轮没有可执行的无痛升级窗口：默认 `/api/runtime-upgrade/status` 返回 `candidate_is_newer=false / running_tasks_present / can_upgrade=false`；按任务要求排除当前主线节点 `node-sti-20260411-8eddf3a3` 后，门禁仍是 `running_task_count=2 / excluded_running_task_count=1 / running_tasks_present / can_upgrade=false`，所以当前既没有更高 candidate，也不是“只剩当前主线占槽”的 apply 场景。

live 运行态已经从“主线 + 保底巡检双 running”的排查现场，推进成“主线 + 测试 + 质量”三条并行 running：主线 `workflow=node-sti-20260411-8eddf3a3 / arun-20260411-015731-2acefa` 仍在执行，同时 `workflow_testmate=node-20260411-020241-c3847e / arun-20260411-020254-dee9f2` 与 `workflow_qualitymate=node-20260411-020318-537595 / arun-20260411-020331-d9a01d` 已经被续挂成真实 helper run。此前并发中的保底巡检 `node-sti-20260411-9bbef3ff` 现在已经成功收尾，所以当前现场不再是 `workflow` 自己的双 running，而是主线继续推进、测试和质量链同时接棒。

## 主线与协作判断

主链目前没有断：`/api/schedules` 已经保留主线 future `2026-04-11T02:22:00+08:00`，保底 future `2026-04-11T02:52:00+08:00`，所以 done definition 里的“至少保留一条未来可执行入口”继续满足，本轮不需要手工补 future 主线。协作方面，这轮已经有 `workflow_testmate` 和 `workflow_qualitymate` 两条新 helper 在执行，最高价值的下一步不再是继续补单，而是等待它们回传 `smoke baseline` 与 `7x24 双 running 口径复核` 的结构化结论；`workflow_devmate / workflow_bugmate` 这轮无需额外续挂。

## 证据

- `git -C .repository/pm-main status --porcelain=v2 --branch`
- `git -C ../workflow_code status --porcelain=v2 --branch`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code fetch origin`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-8eddf3a3'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-8eddf3a3'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260411-020241-c3847e'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260411-020318-537595'`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-015731-2acefa/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-020254-dee9f2/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-020331-d9a01d/run.json`
- `Invoke-RestMethod -Method Post 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/nodes'`
- `Invoke-RestMethod -Method Post 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/dispatch-next'`

## 下一步

- 主线 next: `[持续迭代] workflow -> 2026-04-11T02:22:00+08:00`
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T02:52:00+08:00`
- helper next: 等 `workflow_testmate=node-20260411-020241-c3847e / arun-20260411-020254-dee9f2` 回传 smoke baseline 结论；等 `workflow_qualitymate=node-20260411-020318-537595 / arun-20260411-020331-d9a01d` 回传双 running 口径复核结论
- release boundary next: 下一轮先确认 schedule launch summary 已经把根仓快照写回 `clean_synced / 4fd5c6d`
