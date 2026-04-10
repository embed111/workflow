# Continuous Improvement Report

- inspected_at: `2026-04-10T11:45:37+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-10.md`
- active_version: `V1` 工程质量基线与运行稳态
- task_package: `V1-P2` 发布链与工作区防漂移收口
- lane: `工程质量探测`
- lifecycle_stage: `开发实现 -> 变更控制`
- baseline: `prod=20260410-103412`
- baseline_change: `none`
- root_sync: `developer_id=pm-main / root_sync_state=ahead_clean / ahead_count=1 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=workspace_path_write_scope_blocks_push_to_workflow_code_main / next_push_batch=V1-P2 assignment workspace state helper split / workspace_head=e945995 / code_root_head=5b78e82`

## 结论

这轮我先按发布边界收口模式处理，没有继续扩 `pm-main` 同工作区实现面。原因是 live git 真相已经从调度器摘要里的旧 `clean_synced` 漂到 `ahead_clean`：`.repository/pm-main` 当前 `## main...origin/main [ahead 1]`，本地唯一未回根仓的小批次是 `e945995 refactor(workflow): split assignment workspace state helpers`，内容为把 `workspace_state_and_metrics.py` 拆成 `assignment_workspace_agent_memory.py` 和 `assignment_graph_runtime_metrics.py`，对应 `git show --stat e945995` 为 `538 insertions(+), 534 deletions(-)`。

当前 active 版本仍是 `V1`，这轮最高价值泳道继续是 `工程质量探测`，生命周期仍在 `开发实现 -> 变更控制`。baseline 沿用 `prod=20260410-103412`，没有新增 baseline，也没有新的变更实现；这轮真正做的是确认“现有已验证批次必须先恢复根仓同步，才能继续切下一批”。由于任务边界明确只允许写 `workspace_path`，我不能把 `e945995` push 到 `../workflow_code/main`，所以这轮 release boundary 只能明确记为阻塞，而不能假装已经 clean。

已有验证证据仍可直接复用到这批未推提交：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md` 与 `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260410-112311.md` 对应的是同一批 `e945995` 之前完成的 line budget 与 gate 验收；这轮没有再改代码，所以我没有重复跑同一批验证，只补了 git 边界与 live 运行态复核。

live `prod` 在 `2026-04-10T11:45:37+08:00` 不是假健康。`/api/status` 与 `/api/dashboard` 收口为 `1 running + 2 ready`，真实 running 已切到当前节点 `workflow=node-sti-20260410-f9f3092c / arun-20260410-114054-0fcb01`；`status-detail` 显示其 `latest_event_at=2026-04-10T11:44:16+08:00`，说明这一轮真实 run 仍在推进。当前 ready 主线是 `node-sti-20260410-77fe0b29` 与 `node-sti-20260410-e516f16e`，同时两条 once schedule 仍保留 future 出口：主线 `sch-20260407-20001ab4 -> 2026-04-10T11:56:00+08:00`，保底 `sch-20260407-5ef5e5c8 -> 2026-04-10T11:55:00+08:00`。所以这轮既不补链，也不判成“ready 堆积但没有 live run”。

升级门禁这轮同样不 apply。默认 `/api/runtime-upgrade/status` 仍为 `current=candidate=20260410-103412 / running_task_count=1 / blocking_reason_code=running_tasks_present / can_upgrade=false`；按任务要求排除当前 running 节点 `node-sti-20260410-f9f3092c` 后，门禁回落为 `running_task_count=0 / excluded_running_task_count=1 / blocking_reason_code=no_candidate / can_upgrade=false`，说明当前没有更高 candidate，而不是因为主链卡死。

这轮我也评估了 helper 续挂，但没有新建 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 任务。原因是当前最优先事项仍是收口 `pm-main` 的历史 ahead 批次，而不是在 release boundary 未 clean 的时候继续往同一主线叠新并发任务；当前系统也已经保留了 `running + ready + future` 的连续推进出口。

## 证据

- git / release boundary:
  - `git -C .repository/pm-main status --short --branch`
  - `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
  - `git -C .repository/pm-main rev-parse HEAD`
  - `git -C ../workflow_code rev-parse HEAD`
  - `git -C .repository/pm-main show --stat --format=medium e945995`
  - `docs/workflow/reports/7x24发布边界收口方案-20260409.md`
- 已有代码验证:
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260410-112311.md`
- live 运行态:
  - `GET http://127.0.0.1:8090/healthz`
  - `GET http://127.0.0.1:8090/api/status`
  - `GET http://127.0.0.1:8090/api/dashboard`
  - `GET http://127.0.0.1:8090/api/schedules`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260410-f9f3092c`
  - `GET http://127.0.0.1:8090/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260410-f9f3092c`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260410-114054-0fcb01/run.json`

## 下一步

- 主线 next: 当前 ready queue 为 `node-sti-20260410-77fe0b29`、`node-sti-20260410-e516f16e`；下一次主线 once schedule 触发是 `sch-20260407-20001ab4 -> 2026-04-10T11:56:00+08:00`
- 保底 next: 下一次保底巡检触发是 `sch-20260407-5ef5e5c8 -> 2026-04-10T11:55:00+08:00`
- 发布边界 next: 若后续允许写出 `workspace_path` 之外，我先把 `e945995` 推回 `../workflow_code/main`，把 `ahead_clean` 收回 `clean_synced`
- 版本 next: 根仓同步收口后，继续沿 `V1-P2 / 工程质量探测 / 开发实现-变更控制` 评估下一批仍超线的 part；在此之前不继续扩 `pm-main` 同工作区功能面

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 调度器 prompt 内的 git 快照可能落后于 live 工作区真相，这轮实际现场是 `ahead_clean` 而不是摘要里的 `clean_synced`
- delta_validation: 后续每轮继续先用 live `git status/rev-list/HEAD` 与 `runtime-upgrade/status/status-detail` 重算边界，再决定是否继续开发或先收口
