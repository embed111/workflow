# continuous-improvement-report 2026-04-15 04:03:50

- executed_at: `2026-04-15T04:03:50+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260415-1ad80957`
- graph_name: `任务中心全局主图`
- active_version: `V2`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay`
- next_activation_candidate: `V3`
- next_activation_ready: `true`
- switch_blockers: `R2 / R4 / R5 / R6 / R7 未全部收口；today daily 仍差 workflow_testmate 当日报告；document_baseline 仍停在 003013`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `待切批`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-15.md`

## Result Summary
- 我确认 live `prod` 已自动升到 `20260415-031506`，不是继续停在 `003013`
- 我把 `workflow_testmate` 的 `node-20260415-021148-2cb441` 从 retryable `stream_disconnected` failed 通过受支持 `rerun -> dispatch-next` 接回 `running`
- 我同步回写了 `pm/PM当前版本计划.md`、`pm/versions/V2/版本计划.md`、`pm/daily-execution-history/2026-04-15.md` 与 `pm/versions/V2/history/2026-04/2026-04-15.md`

## Live Truth
- `/api/status`: `running_task_count=2 / queued_task_count=0 / active_agent_count=2 / baseline=prod=20260415-031506 / document_baseline=prod=20260415-003013`
- `/api/runtime-upgrade/status`: `current_version=20260415-031506 / candidate_version=20260415-031506 / candidate_is_newer=false / drain_active=false / can_upgrade=false / blocking_reason=running_tasks_present`
- `/api/schedules`: `mainline=node-sti-20260415-1ad80957 / running`，`patrol=node-sti-20260415-a5aa4068 / queued`，`patrol_next=2026-04-15T04:20:00+08:00`
- `workflow_testmate`: `node-20260415-021148-2cb441 / running / artifact_delivery_status=pending`

## Requirement Evaluation
- `V2-R1=status=completed / progress=100% / eta=已于 2026-04-14 完成 / timeout=-`
- `V2-R2=status=in_progress / progress=95% / eta=2026-04-18 / timeout=未超时`
- `V2-R3=status=completed / progress=100% / eta=已于 2026-04-14 完成 / timeout=-`
- `V2-R4=status=in_progress / progress=99% / eta=2026-04-19 / timeout=未超时`
- `V2-R5=status=in_progress / progress=99% / eta=2026-04-15 / timeout=未超时`
- `V2-R6=status=in_progress / progress=80% / eta=2026-04-15 / timeout=未超时`
- `V2-R7=status=in_progress / progress=99% / eta=2026-04-16 / timeout=未超时`
- `V2-R8=status=completed / progress=100% / eta=已于 2026-04-13 完成 / timeout=-`
- 本轮无需求点超时；未触发新的 `AAR`

## Validation
- `Invoke-RestMethod http://127.0.0.1:8090/healthz`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/schedules`
- `Invoke-RestMethod http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260415-021148-2cb441&include_test_data=0`
- `Invoke-RestMethod -Method Post http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/nodes/node-20260415-021148-2cb441/rerun`
- `Invoke-RestMethod -Method Post http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/dispatch-next`

## Next
- 继续盯 `workflow_testmate` 的 2026-04-15 学习报告回流，并在交付后刷新 `pm/daily-learning-reports/2026-04-15/workflow_testmate.md`
- 补 1 拍 `031506` 的 current-version 文档 baseline 证据，避免 PM 文档继续停在 `003013`
- `today daily` 只有在 `workflow_testmate` 报告真实落盘后才转成 `completed`
