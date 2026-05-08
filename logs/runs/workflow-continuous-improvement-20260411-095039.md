# continuous-improvement-report

- report_time: `2026-04-11T09:51:24+08:00`
- ticket/node: `asg-20260327-223335-b79f27 / node-sti-20260411-4ae90e27`
- active_version: `V1 工程质量基线与运行稳态`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260411-093051`
- root_sync_snapshot: `root_sync_state=ahead_clean / ahead_count=1 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=unpushed_commits_present / next_push_batch=待切批 / workspace_head=9521c3b / code_root_head=9521c3b`

## 本轮结论

1. 这轮没有命中 dirty/ahead 失控的发布边界异常，但当前根仓同步快照也不该再写成 `clean_synced`。`pm-main` 与 `../workflow_code` 现在都在 `9521c3b` 且工作树 clean，不过两边相对 `origin/main` 都是 `ahead 1`；当前真相应是 `ahead_clean`，阻塞原因是 `unpushed_commits_present`，不是 `workspace_dirty_changes_present`。
2. 当前 `workflow` 主线是真 running，不是假健康。`node-sti-20260411-4ae90e27 / arun-20260411-094605-ee5452` 的 `run.json` 仍是 `status=running`，`latest_event_at=2026-04-11T09:50:17+08:00`；`events.log` 也已经落下 `provider_start -> thread.started -> turn.started` 与后续读链 / API 核对动作。`/api/status` 同时收口为 `running_task_count=1 / assignment_running_agent_count=1`，与 run 文件真相一致。
3. 这轮不存在可执行的无痛升级窗口。默认 `/api/runtime-upgrade/status` 为 `current=candidate=20260411-093051 / running_tasks_present / can_upgrade=false`；按任务要求排除当前主线节点后，门禁明确回落为 `excluded_running_task_count=1 / blocking_reason=no_candidate / can_upgrade=false`。这说明当前不是“只差把自己排除掉就能升级”，而是根本没有更高 candidate，所以这轮不执行 `/api/runtime-upgrade/apply`。
4. `V1-P3` 的现网回归已经收口，不需要在这一棒再挂新的 helper。`workflow_testmate` 的 `node-20260411-091255-d2a674 / arun-20260411-091332-d85386` 已在 `2026-04-11T09:26:24+08:00` 成功交付“training registry 运行态口径与 03:43 主线故障在当前版本未复现，未新开缺陷”；因此本轮不再额外续挂 `workflow_devmate / workflow_qualitymate / workflow_bugmate / workflow_testmate`，避免在没有新异常的前提下制造并行噪声。
5. 当前真正需要继续盯的是文本快照新鲜度，而不是连续性本身。当前 running 节点的 `node_goal` 仍保留创建时的旧快照 `7a54432 / ahead_dirty`，但 live `/api/schedules` 已经刷新成 `9521c3b / ahead_clean`，且 future 入口已经续挂为主线 `2026-04-11T10:01:00+08:00`、保底 `2026-04-11T10:31:00+08:00`。这说明 7x24 主链没有断，下一轮更该验证的是“新建节点是否继承最新快照”，而不是再把当前现场误判成 Git 边界异常。

## 验证证据

- Git 真相：
  - `git -C .repository/pm-main status --porcelain=v2 --branch`
  - `git -C ../workflow_code status --porcelain=v2 --branch`
  - `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
  - `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- 运行态：
  - `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-4ae90e27'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-4ae90e27'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260411-091255-d2a674'`
- 任务图与 run 文件：
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-094605-ee5452/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-094605-ee5452/events.log`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-091332-d85386/result.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`

## 下一步

- 当前泳道/阶段 next: `测试探测 / 基于基线测试`
- 主线 next: `[持续迭代] workflow -> 2026-04-11T10:01:00+08:00`
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T10:31:00+08:00`
- 验证 next: 继续复核 `10:01` 主线节点是否以 `ahead_clean / 9521c3b` 的最新快照建单，而不是继续沿用当前 running 节点创建时的旧 `ahead_dirty / 7a54432` 文本。
- 升级 next: 只有在 future 节点接棒后、`candidate_is_newer=true` 且 `running_task_count=0` 时，才重新评估 `/api/runtime-upgrade/apply`。

- preference_ref: `state/user-preferences.md`
- delta_observation: live 连续性已经稳在 `mainline running + future mainline + future patrol`，当前更滞后的是 running 节点内嵌的旧 launch_summary 文本，而不是 Git 或调度出口。
- delta_validation: 下一轮优先核对 `10:01` 新主线节点与对应 future 保底节点的 prompt/launch_summary 是否已继承 `ahead_clean / 9521c3b` 最新快照。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
