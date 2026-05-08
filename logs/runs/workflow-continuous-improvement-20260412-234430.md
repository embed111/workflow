# workflow continuous improvement 2026-04-12 23:44:30 +08:00

- preference_ref: state/user-preferences.md
- delta_observation: `23:31` 主线已经真 running，`workflow_mainline_handoff_pending=false`；这轮真正新增的异常不是 handoff 继续饥饿，而是 `manage_developer_workspace.py bootstrap` 会把 helper developer workspace 短暂对齐到 `origin/main=7a54432` 或停在旧 `607a5ab`，需要立刻按本机 `../workflow_code/main=a3e5eda` 做 `ff-only` 收口并同步修正注册表。
- delta_validation: 下一轮优先确认 `23:49` 主线节点是否继承最新快照，并把已经对齐到 `a3e5eda` 的 helper developer workspace 转成至少 `1` 条真实 helper 派单。

## Summary
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- version_progress: `工程质量探测`
- root_sync_snapshot: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批 / workspace_head=code_root_head=a3e5eda`

## What Changed
1. `/api/status` 已显示 `node-sti-20260412-d96e815d / [持续迭代] workflow / 2026-04-12 23:31:00` 真 `running`，`workflow_mainline_handoff_pending=false`，上一轮盯的主线接棒饥饿不再是当前第一风险。
2. 当前 live 出口已经变成 `23:31 mainline running + 23:40 patrol ready + 23:49 mainline future + 2026-04-13T00:00:00+08:00 patrol future`；`running_task_count=1 / queued_task_count=1 / active_agent_count=1`，不是 `0 running + ready` 的假健康。
3. `manage_developer_workspace.py bootstrap --developer-id workflow_devmate` 先把 `workflow_devmate` 对齐到了 `origin/main=7a54432`，与本机 `../workflow_code/main=a3e5eda` 产生漂移；我立即停止继续 bootstrap，先验证 `7a54432` 与 `607a5ab` 都是 `a3e5eda` 的祖先，再统一对四个 helper 执行 `git pull --ff-only D:/code/AI/J-Agents/workflow_code main` 收口。
4. 收口后 `workflow_devmate / workflow_bugmate / workflow_testmate / workflow_qualitymate` 全部回到 `a3e5eda`，并把 `state/developer-workspaces.json` 修正到当前真相，避免下一轮继续按 `7a54432 / 607a5ab` 的旧快照误派单。

## Validation
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8090/healthz`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260412-d96e815d&include_test_data=0'`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/workflow_devmate rev-parse --short HEAD`
- `git -C .repository/workflow_bugmate rev-parse --short HEAD`
- `git -C .repository/workflow_testmate rev-parse --short HEAD`
- `git -C .repository/workflow_qualitymate rev-parse --short HEAD`
- `git -C ../workflow_code merge-base --is-ancestor 7a54432 a3e5eda`
- `git -C ../workflow_code merge-base --is-ancestor 607a5ab a3e5eda`
- `git -C .repository/workflow_devmate pull --ff-only D:/code/AI/J-Agents/workflow_code main`
- `git -C .repository/workflow_bugmate pull --ff-only D:/code/AI/J-Agents/workflow_code main`
- `git -C .repository/workflow_testmate pull --ff-only D:/code/AI/J-Agents/workflow_code main`
- `git -C .repository/workflow_qualitymate pull --ff-only D:/code/AI/J-Agents/workflow_code main`

## Decisions
- 当前主判断继续保持 `V1 / 工程质量探测 / 基于基线测试`。
- 本轮推进项记为 `工程质量探测`，因为新增价值是确认主线 handoff 已恢复、并主动收口 helper developer workspace commit 漂移。
- `prod` 基线继续保持 `20260412-211849`，本轮不触发 `/api/runtime-upgrade/apply`。
- `parallel_candidate_count=1 / parallel_dispatched_count=0 / active_helper_tasks=[]`
- `parallel_block_reason=本轮先用受支持的 ff-only 本地根仓收口清掉 helper commit drift，避免继续基于 7a54432/607a5ab 派单；下一轮优先把 workflow_devmate 作为第一条 helper 工程治理切片派出。`

## Next
- mainline running: `node-sti-20260412-d96e815d / [持续迭代] workflow / 2026-04-12T23:31:00+08:00`
- patrol ready: `node-sti-20260412-6c4b2a6d / pm持续唤醒 - workflow 主线巡检 / 2026-04-12T23:40:00+08:00`
- mainline future: `[持续迭代] workflow -> 2026-04-12T23:49:00+08:00`
- patrol future: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-13T00:00:00+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-12.md`
