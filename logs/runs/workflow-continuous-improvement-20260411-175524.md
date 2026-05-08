# Continuous Improvement Report

- generated_at: `2026-04-11T18:01:00+08:00`
- active_version: `V1`
- task_package: `V1-P2B`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- 当前根仓同步真相仍是 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批`，`pm-main` 与 `../workflow_code` 继续对齐在 `7822016`；`origin/main ahead 7` 只保留为上游参考，不构成本轮阻塞。
- live `prod` 当前仍停在 `20260411-093051`，更高 `candidate=20260411-173655` 已通过门禁但仍在等待空窗；这轮继续不自行调用 `/api/runtime-upgrade/apply`。
- 当前主链没有断：截至 `2026-04-11T18:01:00+08:00`，真实 running 仍是主线 `node-sti-20260411-5d1c8181 / arun-20260411-174923-f291b5`，`run.json` 显示 `provider_pid=23228 / latest_event_at=2026-04-11T17:56:15+08:00`。
- 当前任务图真相已经推进到 `1 running / 1 ready / 6 pending`：`17:56` 的下一棒主线已经 materialize 成 `ready` 节点 `node-sti-20260411-a65a76f9`，保底 future 仍保留在 `sch-20260405-67a89536 -> 2026-04-11T18:26:00+08:00`。
- 这轮钉住的根因是：`17:56` 新 materialize 的主线节点 `node-sti-20260411-a65a76f9` 又带上了 `root_sync_state=ahead_clean ; ahead_count=7 ; push_block_reason=unpushed_commits_present` 旧 snapshot，但这不是当前工作区重新 dirty，而是 live 部署副本 `D:/code/AI/J-Agents/workflow/.running/prod/src/workflow_app/server/services/release_boundary_service.py` 仍在使用旧的“上游 ahead 也算阻塞”口径；当前工作区与本机代码根仓同名文件已经切成“只以本机 `../workflow_code` clean_synced 为准，GitHub / origin 默认只作参考”的新口径。
- 我已在 `2026-04-11T17:54:16+08:00` 用受支持的 idle watcher single-check 再补了一次 fresh 证据，明确当前仍是 `candidate_is_newer=true / running_task_count=1 / can_upgrade=false`；所以当前真正阻塞的是“idle upgrade 尚未生效”，不是 release boundary 失控。
- `/api/status.active_version=disabled` 仍然和版本计划里的 `V1 active` 分叉，这条语义分叉本轮继续保留为显式风险。
- 本轮没有新增代码改动；当前最有价值的动作是把现场真相回写清楚，让下一棒把“首个空窗是否自动升级到 `20260411-173655`”当成受支持治理判断，而不是继续误读成工作区没收口。

## 现场判断
- 本轮沿用 baseline：`prod=20260411-093051`；没有 baseline 更新，也没有新增代码变更控制批次。
- 当前最高价值泳道继续记为 `工程质量探测`，生命周期阶段继续记为 `变更控制`；本轮聚焦的是 `V1-P2B 真相源统一`。
- 当前 release boundary 继续按 `clean_synced(7822016)` 记录；future schedule 里出现的 `ahead_clean` 已明确降级成“现网旧代码尚未升级”的症状，而不是新的 Git 边界异常。
- 当前主线节点 `node-sti-20260411-5d1c8181` 与新 ready 节点 `node-sti-20260411-a65a76f9` 都属于已 materialize 的历史 prompt snapshot；这轮不再对已落盘节点做热改写，只把它们当成现网尚未升级的证据。
- 若当前主线 run 释放 running 槽后的首个 idle 窗口里，live `prod` 仍没有从 `20260411-093051` 自动升级到 `20260411-173655`，或者 future schedule 文本继续反复漂回旧口径，就应把 `prod supervisor / idle watcher` 验证或重启提升为下一条受支持治理批次。

## 验证证据
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
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-5d1c8181'`
- `Get-Content -Raw 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-174923-f291b5/run.json'`
- `Get-Content 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-174923-f291b5/events.log' -Tail 30`
- `python .repository/pm-main/scripts/apply_prod_candidate_when_idle.py --base-url http://127.0.0.1:8090 --single-check --operator 'workflow(pm)-manual-single-check' --request-timeout-seconds 8 --timeout-seconds 30 --log-path logs/runs/prod-idle-upgrade-watchdog-live.md`
- `Get-Content -Tail 20 logs/runs/prod-idle-upgrade-watchdog-live.md`
- `Get-Content -Raw 'D:/code/AI/J-Agents/workflow/.running/prod/src/workflow_app/server/services/release_boundary_service.py'`
- `Get-Content -Raw 'D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/release_boundary_service.py'`

## 下一步
- 主线 next: `node-sti-20260411-a65a76f9` 已于 `2026-04-11T17:56:05+08:00` materialize 成 `ready`
- 保底 next: `sch-20260405-67a89536 -> 2026-04-11T18:26:00+08:00`
- 升级 next: 等当前主线 `node-sti-20260411-5d1c8181 / arun-20260411-174923-f291b5` 释放 running 槽后，继续看 idle watcher 是否把 `candidate=20260411-173655` 接入 live `prod`
- 治理 next: 若首个空窗过后 `current_version` 仍停在 `20260411-093051`，或 future schedule 文本继续回漂到 `ahead_clean / unpushed_commits_present`，下一轮优先验证或重启 `prod supervisor / idle watcher`
