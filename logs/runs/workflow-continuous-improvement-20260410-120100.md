# Continuous Improvement Report

- inspected_at: `2026-04-10T12:01:00+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-10.md`
- active_version: `V1` 工程质量基线与运行稳态
- task_package: `V1-P2` 发布链与工作区防漂移收口
- lane: `工程质量探测`
- lifecycle_stage: `开发实现 -> 变更控制`
- baseline: `prod=20260410-103412`
- baseline_change: `none`
- root_sync: `developer_id=pm-main / root_sync_state=ahead_clean / ahead_count=1 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=workspace_path_write_scope_blocks_push_to_workflow_code_main / next_push_batch=V1-P2 assignment workspace state helper split / workspace_head=e945995 / code_root_head=5b78e82`

## 结论

这轮我继续按 `V1-P2` 的发布边界收口模式执行，没有扩 `pm-main` 同工作区实现面。live git 真相仍是 `## main...origin/main [ahead 1]`，唯一未回根仓的小批次仍是 `e945995 refactor(workflow): split assignment workspace state helpers`；`git show --stat e945995` 对应 `538 insertions(+), 534 deletions(-)`，核心内容是把 `workspace_state_and_metrics.py` 拆成 `assignment_workspace_agent_memory.py` 与 `assignment_graph_runtime_metrics.py`。这批改动已经完成过命中面的验证，但在本轮“只允许写 `workspace_path`”的边界下，我不能把它 push 到 `../workflow_code/main`，所以 release boundary 继续明确记为阻塞，而不是假装已经回到 `clean_synced`。

当前 active 版本仍是 `V1`，本轮最高价值泳道继续是 `工程质量探测`，生命周期继续停在 `开发实现 -> 变更控制`。baseline 沿用 `prod=20260410-103412`，没有新增 baseline，也没有新的代码切片；这轮真正需要交付的是把 live 现场、版本计划和 release boundary 阻塞同步回治理真相源。

截至 `2026-04-10T12:01:00+08:00`，live `prod` 不是假健康。`/api/status` 与 `/api/dashboard` 一致显示 `1 running + 3 ready`，真实 running 为 `workflow=node-sti-20260410-77fe0b29 / arun-20260410-115206-2ebb70`；`run.json` 显示 `status=running / provider_pid=11272 / latest_event_at=2026-04-10T11:57:55+08:00`。当前 ready 队列为 `node-sti-20260410-07d67d0c`、`node-sti-20260410-92a0457c`、`node-sti-20260410-e516f16e`。需要特别写清的是：两条 once schedule 的 `next_trigger_at` 现在都为空，不是因为断链，而是主线 `sch-20260407-20001ab4` 已在 `2026-04-10T11:56:00+08:00` 命中并转成 ready `node-sti-20260410-07d67d0c`，保底 `sch-20260407-5ef5e5c8` 已在 `2026-04-10T11:55:00+08:00` 命中并转成 ready `node-sti-20260410-92a0457c`；当前连续推进出口来自 `running + ready`，而不是新的 future time。

升级门禁这轮仍然不 apply。默认 `/api/runtime-upgrade/status` 继续是 `running_task_count=1 / blocking_reason_code=running_tasks_present / can_upgrade=false`；按任务要求排除当前 running 节点 `node-sti-20260410-77fe0b29` 后，门禁回落为 `running_task_count=0 / excluded_running_task_count=1 / blocking_reason_code=no_candidate / can_upgrade=false`，说明当前没有更高 candidate，而不是主链卡死。

这轮我也没有续挂新的 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 任务。原因不是忽略协作链，而是当前最高优先级仍是收口 `pm-main` 的历史 ahead 批次；在根仓同步尚未恢复前，再往同一条主线叠新并发只会继续制造边界噪音。

## 证据

- git / release boundary:
  - `git -C .repository/pm-main status --short --branch`
  - `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
  - `git -C .repository/pm-main rev-parse HEAD`
  - `git -C ../workflow_code rev-parse HEAD`
  - `git -C .repository/pm-main show --stat --format=medium e945995`
  - `docs/workflow/reports/7x24发布边界收口方案-20260409.md`
- 已有验证证据:
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260410-112311.md`
- live 运行态:
  - `Get-Date -Format o`
  - `GET http://127.0.0.1:8090/healthz`
  - `GET http://127.0.0.1:8090/api/status`
  - `GET http://127.0.0.1:8090/api/dashboard`
  - `GET http://127.0.0.1:8090/api/schedules`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260410-77fe0b29`
  - `GET http://127.0.0.1:8090/api/assignments/asg-20260407-103450-fb8ba8/status-detail`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260410-115206-2ebb70/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260410-115206-2ebb70/events.log`

## 下一步

- 泳道 / 阶段 next: `工程质量探测 / 开发实现-变更控制`
- 主线触发 next: `无`；`sch-20260407-20001ab4` 已于 `2026-04-10T11:56:00+08:00` 命中并转成 ready `node-sti-20260410-07d67d0c`
- 保底触发 next: `无`；`sch-20260407-5ef5e5c8` 已于 `2026-04-10T11:55:00+08:00` 命中并转成 ready `node-sti-20260410-92a0457c`
- ready 接力 next: 当前 ready queue 为 `node-sti-20260410-07d67d0c`、`node-sti-20260410-92a0457c`、`node-sti-20260410-e516f16e`
- 发布边界 next: 若后续允许写出 `workspace_path` 之外，我先把 `e945995` 推回 `../workflow_code/main`，把 `ahead_clean` 收回 `clean_synced`
- 版本 next: 根仓同步收口后，再继续沿 `V1-P2` 评估下一批仍超线的 part；在此之前不继续扩 `pm-main` 同工作区实现面

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 当前两条 once schedule 都已消费成 ready 节点；没有 future time 不等于断链，必须结合 live run 和 ready queue 一起判断
- delta_validation: 后续每轮继续先核 `git status/rev-list`、`run.json/events.log`、ready queue 和 `next_trigger_at`，再决定是补链、升级还是仅记录 ready 接力
