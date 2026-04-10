# workflow-pm-wake-summary

## 巡检结论
- 巡检时间：`2026-04-08T03:02:12+08:00` 至 `2026-04-08T03:05:03+08:00`
- `prod` 当前版本仍为 `20260407-200414`，候选版本为 `20260408-024443`，`candidate_is_newer=true`。
- 当前 live `prod` 仍有 `1` 条运行中任务，`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`；因此本轮未执行 `/api/runtime-upgrade/apply`。
- 当前运行中的保底巡检节点是 `node-sti-20260408-c3cde83d`，对应 run 为 `arun-20260408-030057-23a1b5`；它已于 `2026-04-08T03:00:27+08:00` 进入 `running`，截至 `2026-04-08T03:03:10+08:00` 仍无 `result.json`。
- `[持续迭代] workflow` 仍保留未来可执行入口：`sch-20260407-20001ab4 -> 2026-04-08T03:22:00+08:00`；主链未断，本轮无需补链。

## 关键真相
- `GET /api/status`：`environment=prod`、`running_task_count=1`、`assignment_running_task_count=1`、`queued_task_count=0`，当前运行节点即 `node-sti-20260408-c3cde83d`。
- `GET /api/runtime-upgrade/status`：`current_version=20260407-200414`、`candidate_version=20260408-024443`、`running_task_count=1`、`can_upgrade=false`。
- `GET /api/schedules/sch-20260407-20001ab4`：`next_trigger_at=2026-04-08T03:22:00+08:00`，说明主线 future 入口还在。
- `GET /api/schedules/sch-20260407-5ef5e5c8`：`last_trigger_at=2026-04-08T03:00:00+08:00`、`last_result_status=running`，说明本轮保底巡检已真实建单并进入运行。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-030057-23a1b5/run.json`：当前 run 仍为 `running`，`started_at=2026-04-08T03:00:27+08:00`、`latest_event_at=2026-04-08T03:03:10+08:00`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`：记录了 `aaud-20260408-025211-da6425` 在上一轮主线失败后继续续挂 `[持续迭代] workflow`，以及 `aaud-20260408-030024-d49e2e` / `aaud-20260408-030101-c3f972` 在 `03:00:04~03:00:27+08:00` 创建并派发当前保底巡检节点。
- `.running/control/runtime/prod/logs/events/schedules.jsonl`：记录了 `2026-04-08T02:52:10+08:00` 的 `update_schedule`，以及 `2026-04-08T03:00:04+08:00` 的 `trigger_hit` 和 `2026-04-08T03:01:25+08:00` 的 `dispatch_requested`，与 HTTP 真相一致。
- 直接扫描节点目录时若不先过滤 `record_state=active`，会误把历史孤儿节点也算进 live 图；这次扫到的 `node-sti-20260407-8a302e24` 虽然 `status=ready`，但 `record_state=deleted`，不是当前待派发节点。按 `record_state=active` 过滤后，当前全局主图是 `1 running / 0 ready`。

## 证据路径
- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-c3cde83d.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-d8de4738.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-030057-23a1b5/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-08.md`

## 下一次建议唤醒时间
- 主线 next：`sch-20260407-20001ab4 -> 2026-04-08T03:22:00+08:00`
- 保底建议：如果 `2026-04-08T03:22:00+08:00` 的主线没有按时建单，或当前保底巡检节点收尾后没有自动续挂新的保底入口，建议在 `2026-04-08T03:27:00+08:00` 再做一次保底巡检。
- 升级建议：等当前 `node-sti-20260408-c3cde83d` 收尾，且 `/api/runtime-upgrade/status` 返回 `running_task_count=0` 与 `can_upgrade=true` 后，优先直接 `apply 20260408-024443`。

memory_ref=.codex/memory/2026-04/2026-04-08.md
experience_ref=.codex/experience/schedule-trigger-closure.md
