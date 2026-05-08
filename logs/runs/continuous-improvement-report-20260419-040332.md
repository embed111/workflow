# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260419-c1d7b70c`
- date: `2026-04-19`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- preference_ref: `state/user-preferences.md`
- delta_observation: `prod=20260419-031640` 上的 `V4-R1` live smoke 已经转绿；`workflow_devmate` 的 `V4-R2` 实现切片已通过全局任务图真实 dispatch 到 `arun-20260419-040336-80a9fc`。`
- delta_validation: `下一轮优先消费 workflow_devmate 的 V4-R2 实现结果，并继续用 audit/run 真相校验手工 create_assignment_node / dispatch-next 的 live 超时是否需要沉为稳定经验。`

## Summary
- 我先在 `prod(8090)` 跑通了 `collect_v4_r1_r4_current_version_smoke.py`，确认 `V4-R1` 的 current-version smoke、browser regression、helper lane relation probe 和 developer workspace clean-synced 全部转绿。
- 我随后没有停在“R1 已验收”的观察态，而是通过受支持的全局任务图 API 派发了 `workflow_devmate` 的 `V4-R2` 切片：`node-20260419-040127-7900e4 -> arun-20260419-040336-80a9fc`。
- 当前 `V4` 不切版，blocker 已从 `V4-R1 / V4-R2 / V4-R5` 收窄为 `V4-R2 / V4-R5`。

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=7dbe7de`
- `code_root_head=7dbe7de`
- `push_block_reason=-`
- `next_push_batch=等待 workflow_devmate 完成 node-20260419-040127-7900e4 / arun-20260419-040336-80a9fc 的 V4-R2 实现批次后，再决定是否切新的验证/发布批次`

## Validation
- `powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\jmqj\.codex\skills\test-session-manager\scripts\run-test-in-session.ps1 -RootPath .repository\pm-main -TestCommand "python scripts/acceptance/collect_v4_r1_r4_current_version_smoke.py --base-url http://127.0.0.1:8090 --expected-version 20260419-031640 --expected-active-version V4 --expected-lane 工程质量探测 --expected-lifecycle-stage 基于基线测试 --ticket-id asg-20260327-223335-b79f27 --expected-workspace-head 7dbe7de"`
- `.repository/pm-main/.test/20260419-035633-457/report.md`
- `.repository/pm-main/.test/evidence/workflow-testmate-v4-r1-r4-current-version-smoke.md`
- `http://127.0.0.1:8090/api/status`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl#aaud-20260419-040136-2b86a5`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl#aaud-20260419-040523-7f69a4`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260419-040336-80a9fc/run.json`

## Active Requirements
- `V4-R1`: `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 62% / eta=2026-04-20 / 未超时`
- `V4-R3`: `completed / 100% / eta=2026-04-19 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `V4-R5`: `in_progress / 20% / eta=2026-04-20 / 未超时`

## Parallel
- `parallel_candidate_count=1`
- `parallel_dispatched_count=1`
- `active_helper_tasks=[workflow_devmate:node-20260419-040127-7900e4/run=arun-20260419-040336-80a9fc]`
- `parallel_peak_count=2`
- `parallel_peak_duration=自 2026-04-19T04:03:32+08:00 起持续中`
- `parallel_total_active_duration=自 2026-04-19T04:03:32+08:00 起累计中`
- `parallel_block_reason=-`
- `helper_dispatch_focus=V4-R2 prompt-share remaining duplicate assembly`
- `helper_dispatch_effect=workflow_devmate 已拿到真实 P0 节点与 dispatch 审计，不再只是 ready 学习节点`
- `non_dispatch_reason=-`

## Warnings
- 手工 `create_assignment_node / dispatch-next` 的同步 HTTP 调用在 caller 侧都超时，但 `audit.jsonl + run.json` 已证明 create/dispatch 成功生效；当前 live 排查要优先看审计和 run 文件真相。
- 手工 `create_assignment_node` 的 non-ASCII `node_name/node_goal` 仍可能在 live 节点里落成 `?`；本轮继续用 ASCII-safe 派单规避。

## Next
- 优先消费 `workflow_devmate` 的 `V4-R2` 实现结果，再决定是否切新的验证/发布批次。
- `V4-R1` 转入常态 regression watch，不再继续占当前 blocker。
- 若手工 create/dispatch 的同步超时再次出现，我下一轮优先把这条 supported route 经验沉成稳定卡片或探针，而不是只在 history 里提一句。
