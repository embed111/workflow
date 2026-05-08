# 持续迭代报告

- generated_at: `2026-04-11T11:49:04+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-f264e03d`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- 我确认当前主线 `workflow=node-sti-20260411-f264e03d / arun-20260411-113923-44b556` 在 live `prod` 上真实 running，`run.json.latest_event_at=2026-04-11T11:45:30+08:00`，不是假健康。
- 当前主线 once schedule 因当前节点仍在 running 暂时没有新的 `next_trigger_at`；不过保底 schedule 仍保留 `2026-04-11T12:09:00+08:00` 的 future 入口，因此当前连续推进出口没有断。
- 我再次执行受支持的发布边界治理动作后，release boundary 已更新为 `ahead_clean(1bf2133) / ahead_count=2 / unpushed_commits_present`；本轮完成了 `fetch/pull --ff-only` 复核，但没有把相对 `origin/main` 的 `ahead 2` 收掉。
- 当前 `test` 已经产出更高的 `candidate=20260411-112732`，排除当前主线节点后 `/api/runtime-upgrade/status` 已明确给出 `candidate_is_newer=true / can_upgrade=true`；但正式升级仍应由 `prod` supervisor 托管的 idle watcher 在空窗时发起，本轮主线不自行调用 `/api/runtime-upgrade/apply`。

## 根仓同步快照
- `root_sync_state=ahead_clean`
- `ahead_count=2`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=unpushed_commits_present`
- `next_push_batch=待切批`
- `workspace_head=1bf2133`
- `code_root_head=1bf2133`
- 我已执行受支持的 non-destructive 动作：
- `git -C .repository/pm-main fetch origin`
- `git -C ../workflow_code fetch origin`
- `git -C .repository/pm-main pull --ff-only origin main`
- `git -C ../workflow_code pull --ff-only origin main`
- 结果说明：
- `pm-main` 的 `fetch/pull --ff-only` 正常完成
- `../workflow_code` 的 `fetch origin` 正常完成
- `../workflow_code` 的显式 `pull --ff-only origin main` 返回 `fatal: Cannot fast-forward to multiple branches`
- 但只读核对 `git remote show origin` 与 `git config --get-all branch.main.merge` 仍显示本地 `main` 只跟踪 `origin/main`，且仓库状态保持 clean / ahead 2，因此这轮把它记录为 Git pull 口径异常，不扩大解释成 behind/diverged

## 运行态证据
- `GET /healthz`：`ok=true`，时间戳 `2026-04-11T11:42:27+08:00`
- `GET /api/status`：`running_task_count=1 / queued_task_count=0 / active_agent_count=1 / failed_task_count=10 / blocked_task_count=9`
- `GET /api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-f264e03d`：
- 当前主图指标为 `total_nodes=75 / pending=6 / ready=0 / running=1 / succeeded=55 / failed=10 / blocked=3`
- 当前节点由 `schedule-worker` 在 `2026-04-11T11:39:22+08:00` 派发，run 引用为 `arun-20260411-113923-44b556`
- `run.json` 当前为 `status=running / latest_event_at=2026-04-11T11:45:30+08:00 / provider_pid=31560`
- `events.log` 已出现 `dispatch -> provider_start -> thread.started -> turn.started`，后续持续写入治理读链与 API/Git 复核动作
- `GET /api/schedules`：主线 once schedule 当前无新的 `next_trigger_at`，保底 `pm持续唤醒 - workflow 主线巡检` 仍保留 `2026-04-11T12:09:00+08:00` 的 future 入口

## 升级门禁
- 默认 `/api/runtime-upgrade/status`：`current=20260411-093051 / candidate=20260411-112732 / candidate_is_newer=true / running_task_count=1 / blocking_reason=running_tasks_present / can_upgrade=false`
- 排除当前主线节点后：`running_task_count=0 / excluded_running_task_count=1 / candidate_is_newer=true / can_upgrade=true`
- `prod-candidate` 证据：`.running/control/prod-candidate.json`
- `test gate` 证据：`.running/control/reports/test-gate-20260411-112732.json`
- 结论：当前只差空窗，不差 candidate；正式升级继续由 idle watcher 接管，本轮主线不自行 apply

## 协作决策
- 这轮不新增 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate`
- 当前最高优先级仍是 `V1-P2` 的发布边界阻塞收口与 idle upgrade 观察，而不是在 `pm-main` 上继续扩实现面
- 本轮没有新增 baseline，也没有新增代码实现；变更控制内容继续集中在 `ahead_clean` 发布边界和 `candidate=20260411-112732` 的升级门禁

## 下一步
- 当前泳道/阶段 next: `工程质量探测 / 变更控制`
- 主线 next: 当前 `node-sti-20260411-f264e03d` 仍在 running；下一次 mainline once 需以该节点 finalize 后的 `/api/schedules` 真相为准
- 保底 next: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T12:09:00+08:00`
- 升级 next: 当前主线收尾后，优先观察 idle watcher 是否把 `candidate=20260411-112732` 安全切进 `prod`
- 发布边界 next: 一旦允许外部 Git 收口，优先清掉 `origin/main` 的 `ahead 2`
