# continuous-improvement-report

- report_time: `2026-04-11T10:16:23+08:00`
- ticket/node: `asg-20260327-223335-b79f27 / node-sti-20260411-af0886d0`
- active_version: `V1 工程质量基线与运行稳态`
- priority_task_package: `V1-P2 发布链与工作区防漂移收口`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- change_control: `沿用既有 baseline；本轮不新增代码实现，只按发布边界方案冻结扩面并记录 ahead_clean 阻塞`
- root_sync_snapshot: `root_sync_state=ahead_clean / ahead_count=1 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=unpushed_commits_present / next_push_batch=待切批 / workspace_head=9521c3b / code_root_head=9521c3b`

## 本轮结论

1. 这轮已经命中 `V1-P2` 的发布边界收口模式，不再继续按普通 `测试探测` 扩写。触发条件不是 dirty，而是 `pm-main` 与 `../workflow_code` 相对 `origin/main` 仍然 `ahead 1`；根据 `7x24发布边界收口方案`，这足以把本轮泳道切回 `工程质量探测 / 变更控制`。
2. 当前根仓同步现场并没有进一步恶化。`pm-main` 与 `../workflow_code` 都在 `9521c3b`，工作树 clean、`dirty_tracked_count=0`、`untracked_count=0`；未收口的只剩 `push_block_reason=unpushed_commits_present`，而不是 root 仓 behind、dirty 或 workspace 漂移。
3. 当前 `workflow` 主线是真 running，不是假健康。`node-sti-20260411-af0886d0 / arun-20260411-101220-f95254` 的 `run.json` 仍是 `status=running`，`latest_event_at=2026-04-11T10:15:24+08:00`；`events.log` 也已落下 `dispatch -> provider_start -> thread.started -> turn.started` 和后续读链 / API 核对动作。`/api/status` 同时收口为 `running_task_count=1 / assignment_running_agent_count=1`，与 run 文件真相一致。
4. 这轮没有可执行的无痛升级窗口。默认 `/api/runtime-upgrade/status` 为 `current=candidate=20260411-093051 / running_tasks_present / can_upgrade=false`；按任务要求排除当前主线节点后，门禁明确回落为 `excluded_running_task_count=1 / blocking_reason=no_candidate / can_upgrade=false`。这说明当前不是“只差自排除就能升级”，而是根本没有更高 candidate，所以这轮继续不执行 `/api/runtime-upgrade/apply`。
5. `V1-P3` 的回归已经在上一轮收口，不需要在这一棒再挂 helper。`workflow_testmate` 的 `node-20260411-091255-d2a674 / arun-20260411-091332-d85386` 已成功交付“training registry 运行态口径与 03:43 主线故障在当前版本未复现，未新开缺陷”；因此本轮不新增 `workflow_devmate / workflow_qualitymate / workflow_bugmate / workflow_testmate`，避免在 release boundary 尚未清掉时再制造并行噪声。
6. 当前 release boundary 仍然 blocked，但阻塞原因已经被压缩成单一项，而且这轮没有越界动作空间。按本轮任务授权，我能做的例外动作仅限 non-destructive `git fetch / pull --ff-only`、workspace bootstrap/refresh，以及 helper/schedule/supervisor/runtime-upgrade 恢复；并没有新的外部 `git push origin main` 授权。因此这轮我只显式记录 `ahead_clean / unpushed_commits_present`，保持 `pm-main` 冻结扩面，不把未授权 push 混进当前收口动作。
7. 7x24 连续推进出口仍然成立。当前主线 schedule 因本轮正在 running 而暂时没有新的 `next_trigger_at`，但保底 `sch-20260405-67a89536` 仍保留 `2026-04-11T10:31:00+08:00` 的 future 出口；下一次 mainline once 由当前 `node-sti-20260411-af0886d0` finalize 自动续挂，下一轮继续以 finalize 后的 `/api/schedules` 真相为准。

## 验证证据

- Git 真相：
  - `git -C .repository/pm-main status --porcelain=v2 --branch`
  - `git -C ../workflow_code status --porcelain=v2 --branch`
  - `git -C .repository/pm-main rev-parse --short HEAD`
  - `git -C ../workflow_code rev-parse --short HEAD`
  - `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
  - `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- 运行态：
  - `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-af0886d0'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-af0886d0'`
  - `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- 任务图与 run 文件：
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-101220-f95254/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-101220-f95254/events.log`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-091332-d85386/result.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-091332-d85386/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`

## 下一步

- 当前泳道/阶段 next: `工程质量探测 / 变更控制`
- 主线 next: 当前 `[持续迭代] workflow / 2026-04-11 10:12:00` 仍在 running；下一次 mainline once 由 `node-sti-20260411-af0886d0` finalize 自动续挂，以 finalize 后 `/api/schedules` 真相为准。
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T10:31:00+08:00`
- 发布边界 next: 若后续轮次允许外部 Git 收口或你明确要求处理远端推送，就优先清掉 `origin/main` 的 `ahead 1`；在此之前继续按发布边界方案冻结 `pm-main` 扩面。
- 验证 next: 下一轮继续核对新建 mainline / patrol 节点是否继承 `ahead_clean / 9521c3b` 的最新快照，而不是回退到旧的 launch_summary 文本。

- preference_ref: `state/user-preferences.md`
- delta_observation: 当前 live 连续性已经稳定，真正未收口的是 `ahead_clean / unpushed_commits_present` 这条发布边界，而不是调度出口或 helper 缺位。
- delta_validation: 下一轮优先核对当前主线 finalize 后的 schedule 回写，并在授权允许时优先处理 `origin/main` 的未推提交。
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`
