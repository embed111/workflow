# workflow-pm-wake-summary

## 巡检结论
- 巡检时间：`2026-04-08T06:30:46+08:00` 至 `2026-04-08T06:32:13+08:00`
- `prod` 当前版本仍为 `20260407-200414`，候选版本为 `20260408-061833`，`candidate_is_newer=true`。
- 截至 `2026-04-08T06:32:13+08:00`，live `prod` 仍有 `1` 条运行中任务，`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`；因此本轮未执行 `/api/runtime-upgrade/apply`。
- 当前唯一 active `running` 节点就是本轮保底巡检 `node-sti-20260408-6f7b2ae8`，对应 run 为 `arun-20260408-062903-a8215c`；`/api/status`、任务图文件、`audit.jsonl` 与 `run.json` 真相一致，当前升级门禁就是被我这轮巡检本身占住，而不是被隐藏运行槽误卡。
- `[持续迭代] workflow` 仍保留未来入口 `sch-20260407-20001ab4 -> 2026-04-08T06:50:00+08:00`。上一轮主线节点 `node-sti-20260408-b3f1572f` 虽在 `2026-04-08T06:19:36+08:00` 以 `assignment execution timeout after 1200s` 失败收口，但失败路径已经自动续挂新的主线触发并补回本轮保底巡检，因此主链未断，本轮无需补链。
- 当前全局主图 live 真相是 `1 running / 0 queued`，而 `done_definition` 要求的“至少保留一条未来可执行的 workflow 主线入口”已经由 `[持续迭代] workflow` 的 `06:50` future 满足。

## 关键真相
- `GET /api/status`：`environment=prod`、`running_task_count=1`、`assignment_running_task_count=1`、`queued_task_count=0`，当前运行节点即 `node-sti-20260408-6f7b2ae8`。
- `GET /api/runtime-upgrade/status`：`current_version=20260407-200414`、`candidate_version=20260408-061833`、`running_task_count=1`、`can_upgrade=false`、`request_pending=false`。
- `GET /api/schedules/sch-20260407-20001ab4`：`next_trigger_at=2026-04-08T06:50:00+08:00`，`last_result_status=failed`，`last_result_node_id=node-sti-20260408-b3f1572f`，说明上一轮主线虽然超时失败，但 future 入口已经续上。
- `GET /api/schedules/sch-20260407-5ef5e5c8`：当前保底巡检 `last_result_status=running`、`future_triggers=[]`，说明本轮 once 保底已经命中并在执行中；未来主线入口需要看 `[持续迭代] workflow`，而不是继续从当前保底计划上找。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-6f7b2ae8.json`：当前保底节点为 `record_state=active`、`status=running`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-062903-a8215c/run.json`：当前 run 仍为 `running`，`started_at=2026-04-08T06:28:30+08:00`，`latest_event_at=2026-04-08T06:31:41+08:00`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-b3f1572f.json` 与 `run.json`：上一轮主线已在 `2026-04-08T06:19:36+08:00` 因 `execution_timeout` 失败，失败原因为 `assignment execution timeout after 1200s`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`：`aaud-20260408-062012-bd6ffc` 记录了上一轮主线失败后自动续挂 `next_trigger_at=2026-04-08T06:50:12+08:00`，并保留本轮保底入口 `backup_next_trigger_at=2026-04-08T06:28:00+08:00`；`aaud-20260408-062825-40902a` 与 `aaud-20260408-062907-2cc3ad` 记录了当前保底节点的创建与派发。
- `.running/control/runtime/prod/logs/events/schedules.jsonl`：与 audit/HTTP 真相一致，最近一次主线更新发生在 `2026-04-08T06:20:12+08:00`，当前保底 trigger 命中在 `2026-04-08T06:28:01+08:00`。

## 证据路径
- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-6f7b2ae8.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-b3f1572f.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-062903-a8215c/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-055904-9891f0/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-055904-9891f0/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-08.md`

## 下一次建议唤醒时间
- 主线 next：`sch-20260407-20001ab4 -> 2026-04-08T06:50:00+08:00`
- 保底建议：如果 `2026-04-08T06:50:00+08:00` 的主线没有按时建单，或当前保底巡检节点收尾后仍没有自动续挂新的保底入口，建议在 `2026-04-08T06:55:00+08:00` 再做一次保底巡检。
- 升级建议：等当前 `node-sti-20260408-6f7b2ae8` 收尾，且 `/api/runtime-upgrade/status` 返回 `running_task_count=0` 与 `can_upgrade=true` 后，优先直接 `apply 20260408-061833`。

memory_ref=.codex/memory/2026-04/2026-04-08.md
