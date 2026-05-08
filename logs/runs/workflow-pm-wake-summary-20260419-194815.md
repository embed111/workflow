# workflow-pm-wake-summary

- judgment: `继续推进`
- version_transition_decision: `stay(V4)`
- lane_stage: `工程质量探测 / 变更控制`
- next_action: 我下一步先把 `schedule_query_runtime.py` 再拆成 `status/query` 双模块，避免新增 `1220` 行 blocker；随后再重检是否把首批治理主重心切到 `assignment_center_render_runtime.js`
- choice: live 当前仍是 `1 running + 2 queued/future`，主线连续性成立，不需要兜底补链；`V5` 仍因 `next_activation_ready=false` 且 `V4-R6` 的 Mandatory Gate 未转绿而不能切版

## 推进修改

1. 我把 `schedule_service.py` 里的 assignment 状态解析、preview/list/detail/calendar 查询链抽到新的 `src/workflow_app/server/services/schedule_query_runtime.py`。
2. 我让 `schedule_service.py` 改成通过 live runtime symbol 绑定新查询模块，保住 acceptance 里对 `resolve_artifact_root_path`、`_assignment_runtime_status` 这类 runtime 符号的 monkeypatch 合同。
3. 我把这条“拆片模块不要把 runtime 符号静态快照化”的经验补进了 `.codex/experience/module-parts-runtime-binding-and-role-memory-scaffold.md`。

## 版本需求更新

| 需求点 | 状态 | 进度 | 最近更新 | ETA | 超时/AAR |
| --- | --- | --- | --- | --- | --- |
| `V4-R1` | `completed` | `100%` | `2026-04-19T03:56:33+08:00` | `2026-04-19` | `未超时 / 无 AAR` |
| `V4-R2` | `completed` | `100%` | `2026-04-19T04:46:32+08:00` | `2026-04-19` | `未超时 / 无 AAR` |
| `V4-R3` | `completed` | `100%` | `2026-04-19T01:26:30+08:00` | `2026-04-19` | `未超时 / 无 AAR` |
| `V4-R4` | `completed` | `100%` | `2026-04-17` | `2026-04-17` | `未超时 / 无 AAR` |
| `V4-R5` | `completed` | `100%` | `2026-04-19T10:20:10+08:00` | `2026-04-19` | `未超时 / 无 AAR` |
| `V4-R6` | `in_progress` | `40%` | `2026-04-19T19:48:15+08:00` | `2026-04-20` | `未超时 / 无 AAR` |

## 发布边界与现场

- `root_sync_state=ahead_dirty / ahead_count=0 / dirty_tracked_count=4 / untracked_count=4`
- `push_block_reason=workspace_dirty + mandatory_gate_fail_closed + schedule_query_runtime_second_slice_uncommitted`
- `next_push_batch=先把 schedule_query_runtime.py 再拆成 status/query 双模块，避免新增 1220 行 blocker；随后再重检是否把首批治理主重心切到 assignment_center_render_runtime.js；Mandatory Gate 未转绿前不继续 test/candidate`
- `workspace_head=code_root_head=54f6aa8`
- `/healthz.ok=true@2026-04-19T19:47:00+08:00`
- `/api/status: running_task_count=1 / queued_task_count=2 / active_agent_count=1 / next_activation_candidate=V5 / next_activation_ready=false`
- `/api/schedules: [持续迭代] workflow -> last_result_status=queued / last_result_node_id=node-sti-20260419-a48c38b0 ; pm持续唤醒 - workflow 主线巡检 -> next_trigger_at=2026-04-19T20:00:00+08:00 / last_result_node_id=node-sti-20260419-8b7282c0`
- `/api/runtime-upgrade/status: current_version=20260419-180446 / candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / ghost_running_detected=false`

## 验证

- `.repository/pm-main/.test/20260419-194624-755/report.md`
- 通过：`py_compile`、`verify_schedule_runtime_status_file_fast_path.py`、`verify_schedule_assignment_runtime_reconciliation.py`、`verify_dashboard_schedule_preview.py`、`verify_schedule_live_result_summary.py`、`verify_schedule_text_repair.py`
- 预期 fail-closed：`python scripts/quality/check_workspace_line_budget.py --root .`
- line budget 变化：`schedule_service.py 3563 -> 2650`；新增 `schedule_query_runtime.py=1220`
- gate 真相：`refactor_trigger_count=32 / guideline_trigger_count=8 / first_batch_targets=assignment_center_render_runtime.js、schedule_service.py、workflow_env_common.ps1`

## Warnings

- `workflow gate / runtime release gate` 仍会被 Mandatory Gate 拦住，所以我这轮没有刷新 `test / prod candidate`。
- 这轮虽然把 `schedule_service.py` 压到了 `2650` 行，但也把债的一部分平移成了 `schedule_query_runtime.py=1220`；下一轮如果不继续拆它，这批 schedule runtime 还不能算真正收口。

- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-19.md`
