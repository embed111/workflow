# Continuous Improvement Report

- inspected_at: `2026-04-10T11:31:51+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-10.md`
- active_version: `V1` 工程质量基线与运行稳态
- task_package: `V1-P2` 发布链与工作区防漂移收口
- lane: `工程质量探测`
- lifecycle_stage: `开发实现 -> 变更控制`
- baseline: `prod=20260410-103412`
- root_sync: `developer_id=pm-main / root_sync_state=ahead_clean / ahead_count=1 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=workspace_path_write_scope_blocks_push_to_workflow_code_main / next_push_batch=V1-P2 assignment workspace state helper split / workspace_head=e945995 / code_root_head=5b78e82`

## 结论

这轮我继续推进 `V1-P2 / 工程质量探测 / 开发实现-变更控制`，把 `assignment_service_parts` 里仍超出 refactor trigger 的 `workspace_state_and_metrics.py` 再切成两个独立 part：`assignment_workspace_agent_memory.py` 负责 agent 工作区发现、`.codex/memory` scaffold 和 workspace 路径解析，`assignment_graph_runtime_metrics.py` 负责图状态重算、pause state 和 running counts。切完后 `workspace_state_and_metrics.py` 从 `1025` 行压到 `832` 行，这一轮不改行为，只收边界。

命中改动面的验证已完成：`python -m py_compile` 覆盖本轮 3 个 part 文件，`python scripts/quality/check_workspace_line_budget.py --root .` 已刷新报告，`python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098` 也重新通过；新的 gate 证据是 `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260410-112311.md`。line budget 侧，这轮已经把 `workspace_state_and_metrics.py` 从 refactor trigger 清单里移除。

live `prod` 在 `2026-04-10T11:31:51+08:00` 仍不是假健康。`/api/status` 收口为 `1 running + 3 ready`，真实 running 仍是 `workflow=node-sti-20260410-e903d220 / arun-20260410-110958-7e6dda`；其 `run.json` 在同一时间仍是 `status=running / provider_pid=18928 / latest_event_at=2026-04-10T11:24:18+08:00`。`11:25` 的主线 once schedule 已经命中并落成新的 ready 节点 `node-sti-20260410-e516f16e`，所以当前 ready 主线是 `node-sti-20260410-77fe0b29`、`node-sti-20260410-e516f16e` 与 `node-sti-20260410-f9f3092c`；future 入口则只剩保底 `sch-20260407-5ef5e5c8 -> 2026-04-10T11:55:00+08:00`。这说明系统已经把下一棒继续挂上，我没有补链，也没有触发 `/api/runtime-upgrade/apply`。

升级门禁这轮仍然不满足 apply 条件。默认 `/api/runtime-upgrade/status` 为 `current=candidate=20260410-103412 / running_task_count=1 / blocking_reason_code=running_tasks_present / can_upgrade=false`；排除当前主线节点 `node-sti-20260410-e903d220` 后，门禁回落为 `running_task_count=0 / excluded_running_task_count=1 / blocking_reason_code=no_candidate / can_upgrade=false`，说明当前不存在更高 candidate，可升级阻塞只是“没有新版本”，不是主线断链。

发布边界方面，这轮按当前任务边界只允许写 `workspace_path`，所以我把代码批次收成了工作区内本地提交 `e945995 refactor(workflow): split assignment workspace state helpers`，但没有 push 到 `../workflow_code/main`。因此这轮最终 root sync 真相是 `ahead_clean` 而不是 `clean_synced`；阻塞原因不是验证未完成，而是本轮写入范围不允许我回写工作区外的根仓。

这轮我没有续挂新的 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 任务。原因不是忽略协作，而是当前切片完全落在 `pm-main` 同一组 backend part 文件里，且已经有 live `running + ready + future` 接力出口；在不能 push 根仓的前提下，再扩 helper 并发只会制造新的边界噪音。

## 证据

- 代码:
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/workspace_state_and_metrics.py`
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/assignment_workspace_agent_memory.py`
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/assignment_graph_runtime_metrics.py`
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/manifest.json`
- 验证:
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260410-112311.md`
  - `python -m py_compile src/workflow_app/server/services/assignment_service_parts/workspace_state_and_metrics.py src/workflow_app/server/services/assignment_service_parts/assignment_workspace_agent_memory.py src/workflow_app/server/services/assignment_service_parts/assignment_graph_runtime_metrics.py`
  - `python scripts/quality/check_workspace_line_budget.py --root .`
  - `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- live 现场:
  - `GET http://127.0.0.1:8090/healthz`
  - `GET http://127.0.0.1:8090/api/status`
  - `GET http://127.0.0.1:8090/api/schedules`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260410-e903d220`
  - `GET http://127.0.0.1:8090/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260410-e903d220`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260410-110958-7e6dda/run.json`
- git:
  - `git -C .repository/pm-main status --porcelain=v1 --branch`
  - `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
  - `git -C .repository/pm-main rev-parse HEAD`
  - `git -C ../workflow_code rev-parse HEAD`

## 下一步

- 主线 next: 当前未来主线时间点已在 `2026-04-10T11:25:00+08:00` 命中并落成 ready `node-sti-20260410-e516f16e`；当前 ready queue 为 `node-sti-20260410-77fe0b29`、`node-sti-20260410-e516f16e`、`node-sti-20260410-f9f3092c`
- 保底 next: 下一次保底巡检触发是 `sch-20260407-5ef5e5c8 -> 2026-04-10T11:55:00+08:00`
- 发布边界 next: 如果后续允许写出 `workspace_path` 之外，我下一步先把 `e945995` 推回 `../workflow_code/main`，恢复 `clean_synced`
- 版本 next: 当前仍沿着 `V1-P2 / 工程质量探测 / 开发实现-变更控制` 继续推进；根仓同步收口后，再从当前干净基线切下一批超线 part
