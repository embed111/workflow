# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-9e2f3228`
- generated_at: `2026-04-17T22:12:36+08:00`
- version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `等待 idle watcher 在空窗把 20260417-220802 切进 prod，再决定 V4-R3 formal route 批次或 V4-R2 下一刀跨文件抽取`
- preference_ref: `state/user-preferences.md`

## Summary

这轮我先消费了两条 helper 回流：把 `workflow_devmate` 的 `245f1c3` shared launch context 抽取收回 `pm-main / workflow_code`，再把 `workflow_qualitymate` 冻结的 `V4-R3` inventory 当成 live 风险输入。随后我确认新的主阻塞不是 prompt 回归，而是 `test` 发布链再次被旧 prototype 图 `running=0` 卡在 `run_acceptance_runtime_release_gate.py`。我因此补上 bootstrap 自恢复：旧测试图一旦 `total_nodes!=20` 或 `running<1`，就会在同 ticket 上自动重种 `20` 节点测试图，而不是直接复用旧残图。补丁以 `.repository/pm-main@bb1b646 / ../workflow_code@bb1b646` 收口后，`test gate` 与 `deploy_workflow_env.ps1 -Environment test` 都已转绿，`prod candidate` 刷新到 `20260417-220802`，我随后又把 `8092` 上新冒出来的 `T9` ghost running 收回终态。

## Validation

- `line budget`: `.repository/pm-main/.test/20260417-220718-752/report.md`
- `self-iteration context sanitization`: `.repository/pm-main/.test/20260417-215735-026/report.md`
- `self-iteration plan reference`: `.repository/pm-main/.test/20260417-215744-527/report.md`
- `schedule prompt contract`: `.repository/pm-main/.test/20260417-215756-357/report.md`
- `workflow gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-220050.md`
- `release gate evidence`: `.running/control/reports/test-gate-20260417-220802.json`
- `test deploy`: `.running/control/logs/test/deploy-20260417-220802.json`
- `ghost repair`: `POST http://127.0.0.1:8092/api/runtime-upgrade/repair-ghost-running -> repaired_count=1`

## Version Status

- `V4-R1`: `in_progress / 80% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 45% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 35% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision`: `stay(V4)`
- `next_activation_candidate`: `-`
- `next_activation_ready`: `false`

## Parallel Dispatch

- `parallel_candidate_count=2`
- `parallel_dispatched_count=2`
- `active_helper_tasks=[]`
- `parallel_block_reason=-`
- `helper_dispatch_focus=V4-R2 shared prompt refactor + V4-R3 inventory freeze`
- `helper_dispatch_effect=dev 切片已落到 bb1b646；质量切片已冻结 4 个高维护项并给出 2 条 formal route 建议`

## Warnings

- `prod` 当前仍是 `20260417-203210`；新的 `candidate=20260417-220802` 已生成，但仍受 `running_task_count=1` 约束，需等待 idle watcher 在空窗切版。
- `assignment_test_data_toggle_probe.py` 单独运行仍会命中既有 `unexpected prod hidden bootstrap error code`；本轮发布判断以 `run_acceptance_runtime_release_gate.py` 和 live `8092` API 真相为准。

## Next

- 等待 idle watcher 在空窗把 `candidate=20260417-220802` 切进 `prod`。
- 切版后优先复跑 `collect_v4_r1_r4_current_version_smoke.py` 与 `V4-R2` prompt contract 验证。
- 下一批按 `workflow_qualitymate` inventory，把 `snapshot/truth parser drift` 与 `task-center failure/detail drift` 转成正式路由。
