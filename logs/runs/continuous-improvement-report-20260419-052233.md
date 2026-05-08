# Continuous Improvement Report

- generated_at: `2026-04-19T05:22:33+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260419-d26a067e`
- active_version: `V4`
- lane_this_round: `UCD/设计优化`
- lifecycle_stage: `验收`
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`

## 本轮推进

- 我先在 `.repository/pm-main@b1ed184` 把 `self_iteration_prompt_templates.py` 的 mainline / patrol 提示词补进“交付默认先给判断、取舍和下一动作”“不要先铺长段状态播报”“少用继续观察 / 已记录 / 后续再看”这组三层约束。
- 我随后在 `schedule_text_repair.py` 把这些口径同步收成 required tokens，让旧 schedule snapshot 也会自动回修成新的 V4-R5 合同，而不是继续沿旧播报腔运行。
- 我新增了 `scripts/acceptance/verify_v4_r5_prompt_tone_contract.py`，并把它接进 `workflow_gate_probe_registry.py` 和 `verify_v4_activation_gate.py`；同时把 `pm/versions/V4/版本计划.md` 的 `V4-R5` probe / gate 口径同步追平。
- 我按 `test-session-manager` 跑通了 `line budget`、`verify_v4_r5_prompt_tone_contract.py`、`verify_schedule_prompt_contract_repair.py`、`verify_assignment_self_iteration_context_sanitization.py`、`verify_v4_activation_gate.py` 和完整 `workflow gate`。
- 我把补丁提交为 `pm-main@b1ed184 feat(v4-r5): 收口自迭代口径去播报腔约束`，再 fast-forward 到 `workflow_code@b1ed184`；之后先用受支持的 `stop_workflow_env.ps1 -Environment test` 清掉旧实例，再重跑 `deploy_test_workflow_env.ps1`，把 `test / prod candidate` 刷到 `20260419-052046`。
- 根仓前移后，我把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部 refresh 回 `clean_synced@b1ed184`，避免这条新合同只停在 `pm-main`。

## 当前版本评估

- `V4-R1`: `completed / 100% / last_updated=2026-04-19T03:56:33+08:00 / eta=2026-04-19 / 未超时`
- `V4-R2`: `completed / 100% / last_updated=2026-04-19T04:46:32+08:00 / eta=2026-04-19 / 未超时`
- `V4-R3`: `completed / 100% / last_updated=2026-04-19T01:26:30+08:00 / eta=2026-04-19 / 未超时`
- `V4-R4`: `completed / 100% / last_updated=2026-04-17 / eta=2026-04-17 / 未超时`
- `V4-R5`: `in_progress / 60% / last_updated=2026-04-19T05:22:33+08:00 / eta=2026-04-20 / 未超时`
- `version_transition_decision=stay(V4)`；`next_activation_candidate=- / next_activation_ready=false`
- 当前 `switch_blockers=V4-R5 尚未达到退出门槛；V5 仍保持 backlog activation_readiness=draft`
- 本轮没有需求点超时，不新增 `AAR`

## Live Truth

- `prod(8090)`：`current_version=20260419-044334 / candidate_version=20260419-052046 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / blocking_reason=存在运行中任务，暂不可升级 / ghost_running_detected=false`
- `test(8092)`：`current_version=20260419-052046 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- 当前主线出口仍成立：`workflow` 主线 `node-sti-20260419-d26a067e` 正在 `running`，下一条 mainline `node-sti-20260419-4325a160` 处于 `ready`，保底 patrol `node-sti-20260419-1b876a69` 也处于 `ready`
- 当前发布边界真相：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=b1ed184 / developer_workspace_count=6 / clean_synced=6 / push_block_reason=-`

## Validation

- `python scripts/quality/check_workspace_line_budget.py --root .`
  - report: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `python scripts/acceptance/verify_v4_r5_prompt_tone_contract.py`
  - session: `.repository/pm-main/.test/20260419-051406-285/report.md`
- `python scripts/acceptance/verify_schedule_prompt_contract_repair.py`
  - session: `.repository/pm-main/.test/20260419-051412-903/report.md`
- `python scripts/acceptance/verify_assignment_self_iteration_context_sanitization.py`
  - session: `.repository/pm-main/.test/20260419-051419-479/report.md`
- `python scripts/acceptance/verify_v4_activation_gate.py`
  - session: `.repository/pm-main/.test/20260419-051538-699/report.md`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - report: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-051910.md`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_test_workflow_env.ps1`
  - report: `.running/control/logs/test/deploy-20260419-052046.json`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
  - result: `developer_workspace_count=6 / clean_synced=6`

## Warnings

- `prod` 仍未切到 `candidate=20260419-052046`；当前是 `running_task_count=1` 挡住空窗升级，不需要也不允许当前主线自己调用 `/api/runtime-upgrade/apply`
- 手工 `create_assignment_node` 的 non-ASCII `node_name/node_goal` 仍可能在 live 节点里落成 `?`；若它开始影响 prompt 理解，下一轮优先按 supported route 收这条风险
- `pm-main` 的 `branch_status=## main...origin/main [ahead 5]` 只代表外部 tracking ref，不构成本机 `workspace -> ../workflow_code` 的阻塞；当前发布边界真相仍以 `workspace_head == code_root_head == b1ed184` 为准

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: `V4-R5` 这类“用户感受型口径”如果只留在偏好和 history 里，旧 schedule snapshot 仍会继续按旧播报腔运行；必须把它同步固化到 self-iteration prompt 模板、schedule repair 和正式 probe。
- delta_validation: `等 prod 在空窗切到 20260419-052046 后，优先用 live 多轮连续对话抽样确认新合同是否已经稳定生效，再判断 V4 是否满足退出门槛。`
