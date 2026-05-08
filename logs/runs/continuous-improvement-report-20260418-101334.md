# Continuous Improvement Report

- executed_at: `2026-04-18T10:13:34+08:00`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- version_transition_decision: `stay(V4)`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

## 本轮推进
- 我先对 `http://127.0.0.1:8092/api/runtime-upgrade/repair-ghost-running` 执行定向 repair，把 test 环境陈旧的 `ticket=asg-20260417-202951-ec981b / node=T9` 从 `running` 收口为 `failed`，让 `8092` 的 `/api/status` 与 `/api/runtime-upgrade/status` 重新对齐到 `running_task_count=0 / ghost_running_detected=false`。
- 随后我盘点到 `.repository/pm-main` 里存在与 `5e8636e fix(scripts): 拆分test与prod的停服部署入口` 同主题的 README 脏改，并将其切成 `549b1e2 docs(scripts): 补齐工作区目录与脚本入口说明`；再用受支持的 `git -C ../workflow_code merge --ff-only 549b1e2` 把本机根仓收口到同一 head。

## Live 真相
- `8090 /api/status`: `running_task_count=1 / queued_task_count=2 / active_version=V4 / baseline=prod=20260418-100054`
- `8090 /api/runtime-upgrade/status`: `current_version=candidate_version=20260418-100054 / candidate_is_newer=false / ghost_running_detected=false / can_upgrade=false / blocking_reason=存在运行中任务，暂不可升级`
- `8092 /api/status`: `running_task_count=0 / queued_task_count=0`
- `8092 /api/runtime-upgrade/status`: `current_version=candidate_version=20260418-100054 / running_task_count=0 / ghost_running_detected=false`
- 当前主线仍是 `node-sti-20260418-8ca435e9` 运行中；下一棒 mainline 已是 `node-sti-20260418-c6e5303f`，patrol 已是 `node-sti-20260418-64a7cde3`，连续性出口存在。

## 发布边界
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=549b1e2`
- `push_block_reason=-`
- `next_push_batch=待切批；当前先复跑 current-version smoke / recent-failure live contract`
- 说明：`git -C .repository/pm-main status --short --branch` 仍显示 `## main...origin/main [ahead 1]`，这是因为本轮通过本机根仓 `ff-only` 收口后，workspace 的本地 `origin/main` tracking ref 未刷新；`workspace -> code_root` 的真实 head 已对齐为 `549b1e2`。

## Active 需求状态
- `V4-R1`: `in_progress / 88% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 80% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- 本轮没有需求点超时，不新增 AAR。
- `next_activation_candidate=- / next_activation_ready=false / switch_blockers=V5 仍是 backlog activation_readiness=draft，且 V4 的 live current-version smoke / recent-failure 合同还要继续复核`

## 风险与下一步
- `repair-ghost-running` 在 test 侧同时回报了 `T17/T18/T19` 三个 `assignment_agent_workspace_missing` 跳过项；它们未再构成当前 baseline 的 running 阻塞，但后续需要按 formal route 清理旧 test 数据。
- 下一轮优先级继续保持 `工程质量探测`：先确认 live `recent-failure / current-version smoke` 合同继续成立，再决定是否把 `T17/T18/T19` 归入 `V4-R3` 的下一批低维护价值清理。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: `test runtime-upgrade gate 出现了“/api/status=0 running，但 /api/runtime-upgrade/status 仍被陈旧 ghost node 卡成 1 running”的 live 分叉；同时 .repository/pm-main 里存在与脚本入口拆分同主题的 README 脏批次`
- delta_validation: `下一轮继续复跑 live current-version smoke / recent-failure 合同，并确认 T17/T18/T19 这组 assignment_agent_workspace_missing 的旧 test 节点是否需要转成 V4-R3 formal route`
