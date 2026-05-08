# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-b825bdb1`
- generated_at: `2026-04-18T00:59:11+08:00`
- version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `等待 idle watcher 在空窗把 20260418-003922 切进 prod，再复跑 current-version smoke 并确认 failure pool recent-first 已在 live 生效`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

## Summary

这轮我把 `V4-R3` 剩余的 `task-center failure/detail drift` 从 inventory 变成了真实修复批次：先补了 `verify_assignment_workboard_recent_failure_pool.py` 红灯，用 5 条同 agent 失败节点锁死“失败池必须按最近失败取前四条”；随后把 `dashboard._workboard_payload()` 改成按 `updated_at / completed_at / created_at / node_id` 做 recent-first 排序后再截断，避免 workboard 继续被节点文件遍历顺序带偏。补丁以 `.repository/pm-main@c577cf3 / ../workflow_code@c577cf3` 收口后，定向 probe 转绿、完整 `workflow gate` 继续通过，并刷新出了 `test/prod candidate=20260418-003922`。

除了代码批次，我还把今天缺失的 helper 学习任务补成了真实节点：`workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 `2026-04-18` 学习任务都已落到全局主图，要求各自把报告写回 `pm/daily-learning-reports/2026-04-18/<agent_id>.md`。我自己的 `workflow(pm)` 学习报告也已先写回；今日 `daily-execution-history` 先记为 `in_progress`，等 helper 报告真实回流后再收成 `completed`。

## Validation

- `line budget`: `.repository/pm-main/.test/20260418-003213-197/report.md`
- `failure-pool red`: `.repository/pm-main/.test/20260418-003312-748/report.md`
- `failure-pool green`: `.repository/pm-main/.test/20260418-003412-385/report.md`
- `workflow gate`: `.repository/pm-main/.test/20260418-003422-275/report.md`
- `workflow gate evidence`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-003718.md`
- `test gate evidence`: `.running/control/reports/test-gate-20260418-003922.json`
- `test deploy`: `.running/control/logs/test/deploy-20260418-003922.json`
- `git -C .repository/pm-main rev-parse HEAD -> c577cf3`
- `git -C ../workflow_code rev-parse HEAD -> c577cf3`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8092/api/runtime-upgrade/status`
- `http://127.0.0.1:8092/api/assignments/asg-20260417-202951-ec981b/status-detail?node_id=T9`

## Version Status

- `V4-R1`: `in_progress / 88% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 45% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 65% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision`: `stay(V4)`
- `next_activation_candidate`: `-`
- `next_activation_ready`: `false`

## Parallel Dispatch

- `parallel_candidate_count=5`
- `parallel_dispatched_count=5`
- `active_helper_tasks=[node-20260418-004748-65d812, node-20260418-004909-6500e8, node-20260418-005133-acecb1, node-20260418-005326-c2ace7, node-20260418-005501-03335b]`
- `parallel_block_reason=mainline 仍在 running，且 prod 已存在更高 candidate=20260418-003922，helper 学习任务先以 ready 队列等待空窗`
- `helper_dispatch_focus=2026-04-18 helper 学习任务 + V4-R3 failure/detail drift follow-up`
- `helper_dispatch_effect=dev/test/quality/bug/ucd 今日学习节点均已创建，缺口从“未派发”降为“待各自回写真实报告”`

## Warnings

- `prod` 当前仍是 `20260417-235555`；新的 `candidate=20260418-003922` 已生成，`candidate_is_newer=true / drain_active=true / running_task_count=1`，需等待 idle watcher 创造升级空窗。
- `pm/daily-execution-history/2026-04-18.md` 当前是 `in_progress`，因为 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的真实学习报告尚未回流。
- `8092 /api/runtime-upgrade/status` 在本轮 `repair-ghost-running` 后仍滞留 `ghost_running_detected=true / T9`，但 `status-detail` 与测试图 `graph.metrics_summary.running=0` 已显示 `T9=failed`；这条读链滞后未在本轮代码批次内一并处理。

## Next

- 等待 idle watcher 在空窗把 `candidate=20260418-003922` 切进 `prod`。
- 切版后优先复跑 `collect_v4_r1_r4_current_version_smoke.py`，并核对 `workflow` 的 近期失败池 是否已经切成 recent-first。
- 等待 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 回写 `2026-04-18` 学习报告，再把 `pm/daily-execution-history/2026-04-18.md` 从 `in_progress` 收成 `completed`。
