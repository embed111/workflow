# Continuous Improvement Report

- generated_at: `2026-04-19T06:08:47+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260419-4325a160`
- active_version: `V4`
- lane_this_round: `UCD/设计优化`
- lifecycle_stage: `验收`
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`

## 本轮推进

- 我先在 `.repository/pm-main@80f7cfd / ../workflow_code@80f7cfd` 把 `schedule -> assignment` 的 `node_goal` 改成 compact schedule goal，不再把整套 mainline / patrol prompt 原样塞进去再硬截到 `3800`，避免 `V4-R5` 的 judgment-first、`version_transition` 和 `done_definition` 关键约束在 live 节点里丢失。
- 我同步把 `verify_assignment_self_iteration_plan_reference.py` 扩成红灯/绿灯，明确锁住 assignment node 的 `task_goal` 仍然保有 `交付默认先给判断、取舍和下一动作`、`version_transition_decision=stay|switch` 和 `done_definition`。
- 我随后在 `.repository/pm-main@e256779 / ../workflow_code@e256779` 给 `assignment_service_parts/graph_model_and_payloads.py` 增加 workflow schedule goal 的执行前重建：即使 `ready` 节点是在旧版本里建出来的，只要它在新版本里真正启动，也会先把 `task_goal` 重建成 compact prompt。
- 我重新跑通了 `line budget`、`verify_assignment_self_iteration_plan_reference.py`、`verify_v4_r5_prompt_tone_contract.py`、`verify_schedule_prompt_contract_repair.py` 和完整 `workflow gate`。
- 我把 `test / prod candidate` 刷到 `20260419-060625`，并把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部 refresh 回 `clean_synced@e256779`。

## 当前版本评估

- `V4-R1`: `completed / 100% / last_updated=2026-04-19T03:56:33+08:00 / eta=2026-04-19 / 未超时`
- `V4-R2`: `completed / 100% / last_updated=2026-04-19T04:46:32+08:00 / eta=2026-04-19 / 未超时`
- `V4-R3`: `completed / 100% / last_updated=2026-04-19T01:26:30+08:00 / eta=2026-04-19 / 未超时`
- `V4-R4`: `completed / 100% / last_updated=2026-04-17 / eta=2026-04-17 / 未超时`
- `V4-R5`: `in_progress / 85% / last_updated=2026-04-19T06:08:47+08:00 / eta=2026-04-20 / 未超时`
- `version_transition_decision=stay(V4)`；`next_activation_candidate=- / next_activation_ready=false`
- 当前 `switch_blockers=V4-R5 仍缺 prod=20260419-060625 下的 live 连续对话抽样；V5 仍保持 backlog activation_readiness=draft`
- 本轮没有需求点超时，不新增 `AAR`

## Live Truth

- `prod(8090)`：`current_version=20260419-052046 / candidate_version=20260419-060625 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false / blocking_reason=存在运行中任务，暂不可升级 / ghost_running_detected=false`
- `test(8092)`：`current_version=20260419-060625 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- 当前主线出口仍成立：`workflow` 主线 `node-sti-20260419-4325a160` 正在 `running`，下一条 mainline `node-sti-20260419-067cc597` 处于 `ready`，保底 patrol `node-sti-20260419-6e3a19ef` 也处于 `ready`
- 当前 `05:14` running 节点和 `05:49/05:40` ready 节点都诞生于 `052046`；但 `e256779` 已把 workflow schedule node 的执行前 `task_goal` 重建补上，所以这些旧 `ready` 节点在升级后真正启动时，也能补吃到新的 compact goal
- 当前发布边界真相：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=e256779 / developer_workspace_count=6 / clean_synced=6 / push_block_reason=-`

## Validation

- `python scripts/quality/check_workspace_line_budget.py --root .`
  - report: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `python scripts/acceptance/verify_assignment_self_iteration_plan_reference.py`
  - sessions: `.repository/pm-main/.test/20260419-055052-069/report.md`、`.repository/pm-main/.test/20260419-060141-209/report.md`
- `python scripts/acceptance/verify_v4_r5_prompt_tone_contract.py`
  - session: `.repository/pm-main/.test/20260419-055127-312/report.md`
- `python scripts/acceptance/verify_schedule_prompt_contract_repair.py`
  - session: `.repository/pm-main/.test/20260419-055134-226/report.md`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - reports: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-055510.md`、`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-060535.md`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_test_workflow_env.ps1`
  - report: `.running/control/logs/test/deploy-20260419-060625.json`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
  - result: `developer_workspace_count=6 / clean_synced=6`

## Warnings

- `prod` 仍未切到 `candidate=20260419-060625`；当前是 `running_task_count=1` 挡住空窗升级，不需要也不允许当前主线自己调用 `/api/runtime-upgrade/apply`
- 当前 running 的 `05:14` 节点已经在旧 prompt 下启动，所以这轮还不能把 `V4-R5` 的 live 连续对话抽样记成 completed
- 手工 `create_assignment_node` 的 non-ASCII `node_name/node_goal` 仍可能在 live 节点里落成 `?`；若它开始影响 prompt 理解，下一轮优先按 supported route 收这条风险

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: `schedule -> assignment` 如果把整套 prompt 直接塞给 `node_goal` 再硬截到 `3800`，`V4-R5` 的 judgment-first / version-transition / done_definition 关键约束会在 live 节点里一起丢失；而旧版本里遗留的 `ready` 节点，也不能只靠“等下一条新节点”被动恢复。
- delta_validation: `等 prod 在空窗切到 20260419-060625 后，优先用下一条 workflow mainline / patrol 的真实执行做 live 连续对话抽样，再判断 V4 是否满足退出门槛。`
