# workflow-pm-wake-summary

## 本轮结论
- 巡检时间：`2026-04-10T11:03:19+08:00`
- Active 版本：`V1 工程质量基线与运行稳态`
- 当前任务包：`V1-P2 发布链与工作区防漂移收口`
- 当前泳道：`工程质量探测`
- 生命周期阶段：`开发实现 / 变更控制`
- 当前 baseline：`prod=20260410-103412`
- 根仓同步：`developer_id=pm-main / root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批 / workspace_head=5b78e82 / code_root_head=5b78e82`

- prod 当前不是假健康。唯一真实 running 为 `workflow=node-sti-20260410-b9ecfba1 / arun-20260410-105756-6a559b`；`run.json` 显示 `status=running / provider_pid=10048 / latest_event_at=2026-04-10T11:01:56+08:00`，`Get-Process 10048` 仍对得上 live `node.exe`，`events.log` 也持续记录本轮读取计划、live API、节点与 run 真相。
- 当前主链未断。ready 主线保留 `node-sti-20260410-77fe0b29`、`node-sti-20260410-e903d220`、`node-sti-20260410-f9f3092c`；future 入口保留为主线 `sch-20260407-20001ab4 -> 2026-04-10T11:27:00+08:00` 与保底 `sch-20260407-5ef5e5c8 -> 2026-04-10T11:57:00+08:00`。
- 需要额外说明的是，上一条主线 `node-sti-20260410-5014f088 / arun-20260410-102649-1fc0f7` 已在 `2026-04-10T10:56:26+08:00` 被 stale recovery 收口为 `failed/cancelled`，失败原因为“运行句柄缺失或 workflow 已重启，请手动重跑”；但系统同一时间已经续挂 `11:27 / 11:57` 两条 future，并立即派发当前保底巡检，所以现场仍是 `live running + ready + future`，不属于 `0 running + ready` 的假健康。
- 当前不执行 `/api/runtime-upgrade/apply`。默认门禁为 `current=candidate=20260410-103412 / running_task_count=1 / blocking_reason=running_tasks_present / can_upgrade=false`；排除当前巡检节点后回落为 `running_task_count=0 / excluded_running_task_count=1 / blocking_reason=no_candidate / can_upgrade=false`，说明当前没有更高 candidate。
- 本轮不续挂新的 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 任务。当前更高优先级是让已排上的 `workflow` 主线与保底继续自动接棒；本轮没有形成新的独立 helper 切片，后续在 `11:27` 主线节点收尾后再评估是否补挂。

## 关键证据
- API：
  - `GET /healthz` -> `ok=true` @ `2026-04-10T11:00:35+08:00`
  - `GET /api/status` -> `1 running + 3 queued`，running node=`node-sti-20260410-b9ecfba1`
  - `GET /api/schedules` -> mainline `next_trigger_at=2026-04-10T11:27:00+08:00`；patrol `next_trigger_at=2026-04-10T11:57:00+08:00`
  - `GET /api/runtime-upgrade/status` -> `current=candidate=20260410-103412 / can_upgrade=false / blocking_reason=running_tasks_present`
  - `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260410-b9ecfba1` -> `running_task_count=0 / excluded_running_task_count=1 / can_upgrade=false / blocking_reason=no_candidate`
  - `GET /api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260410-b9ecfba1` -> graph `status_counts=ready 3 / running 1 / succeeded 90 / failed 47`
- 文件真相：
  - `C:/work/J-Agents/workflow/.running/control/instances/prod.json`
  - `C:/work/J-Agents/workflow/.running/control/envs/prod.json`
  - `C:/work/J-Agents/workflow/.running/control/prod-last-action.json`
  - `C:/work/J-Agents/workflow/.running/control/prod-candidate.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260410-b9ecfba1.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260410-77fe0b29.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260410-e903d220.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260410-f9f3092c.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260410-5014f088.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260410-105756-6a559b/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260410-105756-6a559b/events.log`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260410-102649-1fc0f7/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- Git 真相：
  - `git -C .repository/pm-main status --porcelain=v1 --branch` -> `## main...origin/main`
  - `git -C .repository/pm-main rev-parse HEAD` -> `5b78e82435acaa28f75eb1f8d981d1ef2023beba`
  - `git -C ../workflow_code rev-parse HEAD` -> `5b78e82435acaa28f75eb1f8d981d1ef2023beba`

## 下一次建议唤醒
- 主线 next：`2026-04-10T11:27:00+08:00`
- 保底 next：`2026-04-10T11:57:00+08:00`
- 若 `11:27` 主线命中后出现 `0 running + ready 堆积`，或 recent trigger/message 继续只剩 `assigned agent already has running node` 且找不到 live `run.json/events.log`，应立即按假健康补链或重派发。
- memory_ref：`.codex/memory/2026-04/2026-04-10.md`
