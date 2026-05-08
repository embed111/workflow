# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-9d2312b2`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- version_transition_decision: `stay(V4)`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

## 本轮推进
- 我把 `V4-R2` 的 self-iteration / patrol / schedule repair 提示词收口到 `.repository/pm-main@8eeff0f / ../workflow_code@8eeff0f`：新增 `src/workflow_app/server/services/self_iteration_prompt_templates.py` 后，`assignment_self_iteration_runtime.py`、`schedule_service.py`、`schedule_text_repair.py` 复用同一套 PM 提示词真相源。
- 我补强并跑绿了 `verify_schedule_prompt_contract_repair.py`、`verify_assignment_self_iteration_plan_reference.py`、`verify_assignment_self_iteration_context_sanitization.py`、`verify_self_iteration_backup_schedule_on_smoke_block.py`，以及完整 `workflow gate`：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-014818.md`。
- 我按默认发布约束停掉旧 `test` 后重新部署，刷新出 `test / prod candidate=20260418-014940`，并把 `8092` 的 `T9` ghost ref 清到 `running_task_count=0 / ghost_running_detected=false`。

## 当前版本评估
- `V4-R1`: `in_progress / 88% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 65% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `next_activation_ready=false`，`V5` 仍是 `backlog activation_readiness=draft`，本轮不触发切版，也不新增 AAR。

## 发布边界与 Live
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=8eeff0f`
- `push_block_reason=- / next_push_batch=等待 idle watcher 在空窗把 20260418-014940 切进 prod，再复跑 current-version smoke，并继续跟进 prod helper 学习节点 ghost-running 修复`
- `prod`: `current_version=20260418-003922 / candidate_version=20260418-014940 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`
- `test`: `current_version=20260418-014940 / candidate_version=20260418-014940 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`

## 风险与下一步
- `prod /api/runtime-upgrade/status` 目前仍有 `ghost_running_detected=true / ghost_running_count=6`，集中在 helper 学习节点；我本轮已两次走 HTTP repair、一次直调 repair（并关闭 dispatch）尝试收口，但都挂在当前 live ticket 锁上，没有得到安全可用的终态回写。
- 下一步先等当前 mainline 释放空窗，让 idle watcher 把 `20260418-014940` 切进 `prod`；切版后优先复跑 current-version smoke，并继续追 `prod helper learning` 的 ghost-running 修复。
- `pm/daily-execution-history/2026-04-18.md` 暂保持 `in_progress`：当前只有 `workflow` 本人的真实学习报告已落盘；`workflow_qualitymate` 只在状态投影里出现，真实报告文件尚未 materialize。

## 验证
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260418-013935-657/report.md`
- `.repository/pm-main/.test/20260418-013942-026/report.md`
- `.repository/pm-main/.test/20260418-013953-048/report.md`
- `.repository/pm-main/.test/20260418-014001-633/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-014818.md`
- `.running/control/logs/test/deploy-20260418-014940.json`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8092/api/runtime-upgrade/status`

## Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 用户这轮继续要求我以 `workflow` 本人推进，并把“先读治理链 + 至少落 1 项推进性修改 + 逐项更新 active 版本 + 最终只交付 JSON”当成硬约束。
- delta_validation: 下一轮先验证 `prod` 是否已切到 `20260418-014940`，再继续收口 prod helper learning ghost-running 与 helper 学习报告 materialization。
