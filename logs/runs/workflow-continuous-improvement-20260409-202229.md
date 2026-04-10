# [持续迭代] workflow / 2026-04-09 19:44:00

## 本轮结论
- active 版本：`V1`
- 泳道 / 生命周期阶段：`工程质量探测 / 开发实现-变更控制`
- baseline：`prod=20260409-105430`
- 我这轮继续按 `V1-P2` 收口 release boundary，把 `snapshot/store/scheduler` 相关 helper 从 [`task_artifact_store_queries.py`](/C:/work/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_queries.py) 切到新的 [`task_artifact_store_snapshot_runtime.py`](/C:/work/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_snapshot_runtime.py)，并同步更新 [`manifest.json`](/C:/work/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/manifest.json)。
- 结果是 `task_artifact_store_queries.py` 从上一轮的 `1288` 行继续压到 `986` 行，新 part 为 `238` 行；这一刀没有改行为，只是把 `queries` 收回到“查询接口 + stale recovery”主体职责。

## 验证证据
- `python -m py_compile .repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_queries.py .repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_snapshot_runtime.py .repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_execution.py .repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_runtime.py`
- `python .repository/pm-main/scripts/quality/check_workspace_line_budget.py --root .repository/pm-main`
- `python .repository/pm-main/scripts/acceptance/verify_assignment_status_detail_default_node.py`
- `python .repository/pm-main/scripts/acceptance/verify_assignment_mainline_visibility.py`
- `python .repository/pm-main/scripts/acceptance/verify_assignment_dispatch_survives_stale_recovery.py`
- `python .repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py --root .repository/pm-main --host 127.0.0.1 --port 8098`
- 最新证据路径：
  - [`WORKSPACE_LINE_BUDGET_REPORT.md`](/C:/work/J-Agents/workflow/.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md)
  - [`workflow-gate-acceptance-20260409-202000.md`](/C:/work/J-Agents/workflow/.repository/pm-main/.test/runs/workflow-gate-acceptance-20260409-202000.md)

## Live 真相
- 复核时间：`2026-04-09T20:22:29+08:00`
- 当前 `prod` 仍是 `20260409-105430`，`candidate_is_newer=false`，所以这轮不执行 `/api/runtime-upgrade/apply`。
- 当前真实 running 仍是 `workflow=node-sti-20260409-6092b8ec / arun-20260409-200305-823006`；[`run.json`](/C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260409-200305-823006/run.json) 显示 `status=running / provider_pid=23052 / latest_event_at=2026-04-09T20:23:14+08:00`。
- 当前 ready 出口已经扩成三条：
  - 主线：`node-sti-20260409-1245d43b`
  - 主线：`node-sti-20260409-16af22f2`
  - 保底：`node-sti-20260409-fadf491e`
- 这表示 `20:02 / 20:14 / 20:18` 的 once schedule 已全部转成 ready 节点，当前没有 future 时间并不等于断链。
- 升级门禁复核：
  - 默认：`running_task_count=1 / can_upgrade=false / blocking_reason=running_tasks_present`
  - 排除当前主线节点后：`running_task_count=0 / excluded_running_task_count=1 / can_upgrade=false / blocking_reason=no_candidate`

## 发布边界
- 当前继续按 release boundary dirty 处理，而不是恢复 helper 并发或刷新 `test / prod candidate`。
- root sync：
  - `root_sync_state=dirty_local`
  - `ahead_count=0`
  - `dirty_tracked_count=13`
  - `untracked_count=11`
- `push_block_reason`：同批 release boundary 仍混有 `V1-P1 / V1-P2 / V1-P14 / V1-P16` 改动和 acceptance/helper 文件。
- `next_push_batch`：先切 `V1-P2` 的 snapshot-runtime split 与既有 gate/helper 批次，再恢复小步推根仓、`test` 与 `prod candidate`。
- 协作决策：这轮仍不续挂 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate`，避免在同批 dirty 工作区继续扩冲突面。

## 下一步
- 主线 next：`node-sti-20260409-1245d43b (ready)`，等当前 `node-sti-20260409-6092b8ec` 收尾后优先接棒。
- 主线 next 2：`node-sti-20260409-16af22f2 (ready)`。
- 保底 next：`node-sti-20260409-fadf491e (ready)`。
- 开发 next：继续压 `V1-P2` 的 release boundary，优先准备可推送最小批次。
- memory_ref：`.codex/memory/2026-04/2026-04-09.md`
