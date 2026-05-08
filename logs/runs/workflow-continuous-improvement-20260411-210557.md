# workflow 持续迭代报告

- updated_at: `2026-04-11T21:05:57+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-4fca706e`
- active_version: `V1`
- task_package: `V1-P5`
- lane: `架构优化`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- `pm-main / ../workflow_code` 仍然是 `clean_synced(806aef2)`，当前没有新的 release boundary 脏现场；`origin/main ahead 9` 继续只作上游参考。
- 当前 live 阻塞已经从“candidate 刷不出来”切成“upgrade idle window 拿不到”：`candidate=20260411-202044` 已就位，但 `19:51` 主线 `node-sti-20260411-4fca706e` 仍在 `running` 时，`20:48` future 又已经转成 `ready` 节点 `node-sti-20260411-f4bc26eb`。
- 我本轮把这条现场正式提升成 `V1-P5`，并把当前最高价值泳道切到 `架构优化 / 变更控制`。这轮没有新增代码实现，也没有新的 `commit / push / test / candidate` 动作；本轮交付是把下一优先级和 live 真相写清，而不是继续重复巡检。

## 根仓同步快照
- 当前 live 真相：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批`
- 当前工作区：`pm-main`
- `workspace_head=code_root_head=806aef2`
- 说明：`pm-main / workflow_code` 相对 `origin/main` 仍是 `ahead 9`，但这里继续只作为上游参考，不构成本轮阻塞。
- 旧 prompt 快照仍然漂在 live 节点里：
  - `node-sti-20260411-4fca706e` 仍带 `root_sync_state=ahead_clean / ahead_count=8 / workspace_head=1cd76c8 / push_block_reason=unpushed_commits_present`
  - `node-sti-20260411-f4bc26eb` 仍带 `root_sync_state=ahead_clean / ahead_count=9 / workspace_head=806aef2 / push_block_reason=unpushed_commits_present`
  - 这不是根仓回脏，而是 live `prod` 还没切到包含新真相口径的 candidate。

## live 现场
- `prod current_version=20260411-093051`
- `candidate_version=20260411-202044`
- `blocking_reason=running_tasks_present / can_upgrade=false`
- 当前真实 running：
  - `node_id=node-sti-20260411-4fca706e`
  - `run_id=arun-20260411-204415-58684e`
  - `run_status=running`
  - `latest_event_at=2026-04-11T20:49:26+08:00`
  - `provider_pid=61844`
- 当前 ready 出口：
  - `node_id=node-sti-20260411-f4bc26eb`
  - `planned_trigger_at=2026-04-11T20:48:00+08:00`
  - `status=ready`
  - `last_result_summary=assigned agent already has running node`
- 当前任务图真相：`1 running / 1 ready / 6 pending / 11 failed / 3 blocked`
- 当前 `/api/status` 真相：`running_task_count=1 / queued_task_count=1 / workflow_mainline_handoff_pending=false`
- 当前保底 future：`sch-20260405-67a89536 -> 2026-04-11T21:18:00+08:00`
- 当前不是假健康，也不缺下一棒；真正缺的是升级链拿不到 `running_task_count=0` 的空窗。

## 本轮动作
1. 我按工作区治理读链重读了 `AGENTS.md / 协作约定 / 7x24机制 / 经验卡 / SOUL / USER / MEMORY / 记忆总览 / 今日日记 / 版本计划 / 持续唤醒需求 / 发布边界方案`。
2. 我重跑了 `pm-main / ../workflow_code` 的 Git 边界、`/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、任务图、当前 node `status-detail`、`20:48` 新 node `status-detail`、run 文件和 audit。
3. 我确认 `20:48` 这条 future 已经命中并进入 `ready`，说明当前连续接力在工作；同时它也证明当前 watcher 继续只能看到 `running_task_count=1`，空窗不会靠多等几分钟自己出现。
4. 我把 `V1-P5` 正式提升为 `in_progress`，并把版本计划、月度 live 总览和升级经验卡同步到这条新判断。
5. 我补写了本轮报告和今日日记，明确下一优先级、下一条主线/保底出口，以及“什么时候才该怀疑 watcher 本身”。

## 验证证据
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-4fca706e'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-f4bc26eb'`
- `Get-Content -Raw C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-204415-58684e/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-204415-58684e/events.log -Tail 120`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl -Tail 30`
- `Get-Content -Raw .running/control/prod-last-action.json`
- `Get-Content logs/runs/prod-idle-upgrade-watchdog-live.md -Tail 80`

## baseline 与变更控制
- 本轮沿用 baseline：`prod=20260411-093051`
- 本轮变更控制更新：
  - `V1-P2` 的 candidate 刷新阻塞已不再是当前首要矛盾
  - 当前首要阻塞正式切换为 `V1-P5`：升级期间 drain / 新派发分流
  - 当前 change control 目标是“在不破坏 7x24 连续接力的前提下，给 idle watcher 真正的 upgrade 空窗”
- 本轮继续遵守：
  - 不调用 `/api/runtime-upgrade/apply`
  - 不对当前 running 节点做 exclusion
  - 不为了抢升级空窗而手工切掉当前主线

## 协作与下一步
- 这轮没有新挂 helper 任务；原因不是没人可接，而是当前最值钱的动作是先把 `V1-P5` 的 change control 和 live blocker 写清。当前主线和保底出口都已保留，不需要额外补链。
- 主线 next：
  - 当前 running：`node-sti-20260411-4fca706e / arun-20260411-204415-58684e`
  - 当前 ready：`node-sti-20260411-f4bc26eb / [持续迭代] workflow / 2026-04-11 20:48:00`
- 保底 next：`sch-20260405-67a89536 -> 2026-04-11T21:18:00+08:00`
- 若 `node-sti-20260411-4fca706e` 收尾后，`node-sti-20260411-f4bc26eb` 又立刻接棒并继续让 `running_task_count=1`，下一轮优先推进 `V1-P5` 的 drain / dispatch 分流实现。
- 只有当真正出现 `running_task_count=0` 的 idle 窗口，而 `candidate=20260411-202044` 仍未自动 apply 时，下一轮才优先验证 `prod supervisor / idle watcher` 是否需要重启或补单次检查。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 当前 live `prod` 的真正阻塞已经从 `candidate` 刷新失败切成 `19:51 running + 20:48 ready` 带来的 idle upgrade starvation。
- delta_validation: 下一轮先看当前 running 节点收尾后是否继续立刻被 `20:48` 节点接棒；若是，就直接按 `V1-P5` 落实现切片，而不是继续追加 manual single-check。
