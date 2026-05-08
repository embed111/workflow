# Continuous Improvement Report

- generated_at: `2026-04-18T14:13:57+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-42fe512e`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- preference_ref: `state/user-preferences.md`

## 本轮推进

- 我先把 `.repository/pm-main@17e3556 / ../workflow_code@17e3556` 的 `collect_v4_r1_r4_current_version_smoke.py` 扩成新的 live smoke contract：显式校验 `status-detail` 默认选中节点是否回到当前 probe node，以及 `execution_chain.latest_run` 是否和显式 `node_id` 读取对齐。
- 我随后把 smoke 在 `.repository/pm-main@c4002b4 / ../workflow_code@c4002b4` 继续收口为稳定版本：对 live `status-detail` 读链补了超时重试，并把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部 refresh 到 `clean_synced@c4002b4`。
- 我按 `test-session-manager` 跑过 `line budget`、三次 red-light smoke 和最终 green 的 `collect_v4_r1_r4_current_version_smoke.py`，再跑通完整 `workflow gate`；新增合同 `status_detail_default_selected_probe_node=true / status_detail_default_latest_run_matches_explicit=true` 已转绿。
- 我最后执行 `stop_test_workflow_env.ps1` + `deploy_test_workflow_env.ps1`，刷新出 `test / prod candidate=20260418-141234`；`deploy-20260418-141234.json` 自动记录了 `post_deploy_ghost_running.repaired_count=1`。

## 当前版本判断

- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 99% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision=stay(V4) / next_activation_candidate=- / next_activation_ready=false / switch_blockers=V5 仍保持 backlog activation_readiness=draft`

## 发布边界

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=c4002b4`
- `next_push_batch=等待 prod 空窗切到 20260418-141234 后按新 status-detail default-node 合同复跑 live current-version smoke`

## Live Truth

- `prod`: `current_version=20260418-131806 / candidate_version=20260418-141234 / candidate_is_newer=true / request_pending=false / running_task_count=1 / queued_task_count=2 / ghost_running_detected=false`
- `test`: `current_version=20260418-141234 / candidate_version=20260418-141234 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- `developer_workspaces`: `pm-main + 5 helper` 当前已全部回到 `clean_synced@c4002b4`

## 验证

- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-135644-118/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-135657-646/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-140001-440/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-140306-240/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-140638-073/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-141217.md`
- `D:/code/AI/J-Agents/workflow/.running/control/logs/test/deploy-20260418-141234.json`

## 风险与下一步

- `prod` 当前仍有 running mainline，idle watcher 还不能 apply `20260418-141234`。
- 下一步优先等待空窗切版后复跑 `collect_v4_r1_r4_current_version_smoke.py --expected-version 20260418-141234`，确认新的 status-detail default-node / latest_run smoke 合同在 live `141234` 没有回退。
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`
