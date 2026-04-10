# workflow-pm-wake-summary

## 巡检结论
- 巡检时间：`2026-04-08T05:38:48+08:00` 至 `2026-04-08T05:40:51+08:00`
- `prod` 当前版本仍为 `20260407-200414`，候选版本为 `20260408-051809`，`candidate_is_newer=true`。
- 截至 `2026-04-08T05:40:51+08:00`，live `prod` 仍有 `1` 条运行中任务，`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`；因此本轮未执行 `/api/runtime-upgrade/apply`。
- 当前唯一 active `running` 节点就是本轮保底巡检 `node-sti-20260408-a5675f74`，对应 run 为 `arun-20260408-053709-1f300b`；`/api/status`、任务图文件与 `run.json` 真相一致，说明当前升级门禁就是被我这轮巡检本身占住，而不是被隐藏运行槽误卡。
- `[持续迭代] workflow` 仍保留未来入口 `sch-20260407-20001ab4 -> 2026-04-08T05:58:00+08:00`。上一轮主线节点 `node-sti-20260408-59614e1a` 虽在 `2026-04-08T05:27:32+08:00` 以 `assignment execution timeout after 1200s` 失败收口，但失败收口已经自动续挂了新的主线触发，因此主链未断，本轮无需补链。
- 当前 live `schedule_workboard_preview` 仍显示 `4` 条 active 计划，说明 exhausted `once` plan repair 还没在现网接管；这正是候选版本 `20260408-051809` 准备收掉的真相分叉，但在当前运行槽释放前我不能误升。

## 关键真相
- `GET /api/status`：`environment=prod`、`running_task_count=1`、`assignment_running_task_count=1`、`queued_task_count=0`，当前运行节点即 `node-sti-20260408-a5675f74`。
- `GET /api/runtime-upgrade/status`：`current_version=20260407-200414`、`candidate_version=20260408-051809`、`running_task_count=1`、`can_upgrade=false`、`request_pending=false`。
- `GET /api/schedules/sch-20260407-20001ab4`：`next_trigger_at=2026-04-08T05:58:00+08:00`，`last_result_status=failed`，`last_result_node_id=node-sti-20260408-59614e1a`，说明上一轮主线虽然超时失败，但 future 入口已经续上。
- `GET /api/schedules`：当前保底巡检 `sch-20260407-5ef5e5c8` 为 `last_result_status=running`、`next_trigger_at=''`；done_definition 要求的“至少保留一条未来可执行的 workflow 主线入口”已经由 `[持续迭代] workflow` 的 `05:58` future 满足。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-a5675f74.json`：当前保底节点为 `record_state=active`、`status=running`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-053709-1f300b/run.json`：当前 run 仍为 `running`，`started_at=2026-04-08T05:36:32+08:00`，`latest_event_at=2026-04-08T05:40:51+08:00`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-59614e1a.json` 与 `run.json`：上一轮主线已在 `2026-04-08T05:27:32+08:00` 因 `execution_timeout` 失败，失败原因为 `assignment execution timeout after 1200s`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`：`aaud-20260408-052804-b757e1` 记录了上一轮主线失败后自动续挂 `next_trigger_at=2026-04-08T05:58:04+08:00`，并把保底入口保留到 `2026-04-08T05:36:00+08:00`；`aaud-20260408-053628-7b609d` 与 `aaud-20260408-053713-e0b734` 记录了当前保底节点的创建与派发。
- `.running/control/runtime/prod/logs/events/schedules.jsonl`：与 audit/HTTP 真相一致，最近一次 schedule 更新在 `2026-04-08T05:28:04+08:00`，当前保底 trigger 命中在 `2026-04-08T05:36:03+08:00`。

## 证据路径
- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-a5675f74.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-59614e1a.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-053709-1f300b/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-050701-a4f15d/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-050701-a4f15d/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-08.md`

## 下一次建议唤醒时间
- 主线 next：`sch-20260407-20001ab4 -> 2026-04-08T05:58:00+08:00`
- 保底建议：如果 `2026-04-08T05:58:00+08:00` 的主线没有按时建单，或当前保底巡检节点收尾后仍没有自动续挂新的保底入口，建议在 `2026-04-08T06:03:00+08:00` 再做一次保底巡检。
- 升级建议：等当前 `node-sti-20260408-a5675f74` 收尾，且 `/api/runtime-upgrade/status` 返回 `running_task_count=0` 与 `can_upgrade=true` 后，优先直接 `apply 20260408-051809`。

memory_ref=.codex/memory/2026-04/2026-04-08.md
