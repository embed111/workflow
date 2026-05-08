# Continuous Improvement Report

- generated_at: `2026-04-19T04:46:32+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260419-50f6759f`
- active_version: `V4`
- lane_this_round: `工程质量探测 / 发布推进`
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`

## 本轮推进

- 我先消费了 `workflow_devmate` 的 `arun-20260419-040336-80a9fc` follow-up 结果，把 `V4-R2` 剩余的 2 处 release-boundary compact lines 从 `assignment_self_iteration_runtime.py` 和 `schedule_service.py` 里抽掉，统一改成复用 `format_release_boundary_prompt_lines(...)`。
- 我在 `pm-main` 正式新增了 `scripts/acceptance/verify_v4_r2_prompt_share_followup.py`，把 helper 先前给出的 `remaining_duplicate_count=2` 红灯收成了 `remaining_duplicate_count=0` 绿灯，不再只停在 runtime helper 的 probe-only 结论。
- 我随后跑通了 `line budget`、`verify_v4_r2_prompt_share_followup.py`、`verify_release_boundary_local_root_sync_policy.py`、`verify_assignment_self_iteration_plan_reference.py` 和完整 `workflow gate`，并把补丁提交为 `pm-main@69c0e14`，再 fast-forward 到 `workflow_code@69c0e14`。
- 根仓收口后，我先用受支持的 `stop_workflow_env.ps1 -Environment test` 清掉旧 `test` 的 `PID=31496`，再重跑 `deploy_test_workflow_env.ps1`，把 `test / prod candidate` 刷到 `20260419-044334`；deploy report 显示 `test gate passed`，post-deploy ghost repair 额外修复了 `1` 条历史 ghost。
- 我最后把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部 refresh 回 `clean_synced@69c0e14`，避免 developer workspace 真相继续停在旧 head。

## 当前版本评估

- `V4-R1`: `completed / 100% / last_updated=2026-04-19T03:56:33+08:00 / eta=2026-04-19 / 未超时`
- `V4-R2`: `completed / 100% / last_updated=2026-04-19T04:46:32+08:00 / eta=2026-04-19 / 未超时`
- `V4-R3`: `completed / 100% / last_updated=2026-04-19T01:26:30+08:00 / eta=2026-04-19 / 未超时`
- `V4-R4`: `completed / 100% / last_updated=2026-04-17 / eta=2026-04-17 / 未超时`
- `V4-R5`: `in_progress / 25% / last_updated=2026-04-19T04:46:32+08:00 / eta=2026-04-20 / 未超时`
- `version_transition_decision=stay(V4)`；`next_activation_candidate=- / next_activation_ready=false`
- 当前 `switch_blockers=V4-R5`；`V4-R2` 已不再占据退出 blocker
- 我已经把当前最高价值泳道从 `工程质量探测` 显式切到 `UCD/设计优化`，把生命周期阶段切到 `验收`，避免下一轮还机械沿着 prompt-share 工程治理空转
- 本轮没有需求点超时，不新增 `AAR`

## Live Truth

- `prod(8090)`：`current_version=20260419-031640 / candidate_version=20260419-044334 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / ghost_running_detected=false`
- `test(8092)`：`current_version=20260419-044334 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- 当前主线出口仍成立：`workflow` 主线 `node-sti-20260419-50f6759f` 正在 `running`，下一条 mainline `node-sti-20260419-d26a067e` 处于 `ready`，保底 patrol `node-sti-20260419-cb9d54df` 也处于 `ready`
- 当前保底下一次触发时间：`2026-04-19T05:00:00+08:00`
- 当前发布边界真相：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=69c0e14 / push_block_reason=-`

## Validation

- `python scripts/quality/check_workspace_line_budget.py --root .`
  - report: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - hard gate: `pass=true`
- `python scripts/acceptance/verify_v4_r2_prompt_share_followup.py`
  - session: `.repository/pm-main/.test/20260419-043752-102/report.md`
  - result: `remaining_duplicate_count=0`
- `python scripts/acceptance/verify_release_boundary_local_root_sync_policy.py`
  - session: `.repository/pm-main/.test/20260419-043758-814/report.md`
- `python scripts/acceptance/verify_assignment_self_iteration_plan_reference.py`
  - session: `.repository/pm-main/.test/20260419-043804-641/report.md`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - report: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-044207.md`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_test_workflow_env.ps1`
  - report: `.running/control/logs/test/deploy-20260419-044334.json`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
  - result: `developer_workspace_count=6 / clean_synced=6`

## Warnings

- `prod` 仍未切到 `candidate=20260419-044334`；当前是 `running_task_count=1` 挡住空窗升级，不需要也不允许当前主线自己调用 `/api/runtime-upgrade/apply`
- 手工 `create_assignment_node` 的 non-ASCII `node_name/node_goal` 仍可能在 live 节点里落成 `?`；若它开始影响 prompt 理解，下一轮优先按 supported route 收这条风险
- `pm-main` 的 `branch_status=## main...origin/main [ahead 4]` 只代表外部 tracking ref，不构成本机 `workspace -> ../workflow_code` 的阻塞；当前发布边界真相仍以 `workspace_head == code_root_head == 69c0e14` 为准

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: `V4-R2` 工程收口完成后，当前最高价值动作已经从 prompt-share 工程治理切换到 `V4-R5` 的体验验收；如果不显式更新版本快照，主线会继续沿着旧泳道空转
- delta_validation: 等 `prod` 在空窗切到 `20260419-044334` 后，优先用连续对话抽样和 live current-version 现场一起验收 `V4-R5`，确认 `V4` 是否满足退出门槛
