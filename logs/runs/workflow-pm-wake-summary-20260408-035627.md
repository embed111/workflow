# workflow-pm-wake-summary

## 巡检结论
- 巡检时间：`2026-04-08T03:54:35+08:00` 至 `2026-04-08T03:56:27+08:00`
- `prod` 当前版本仍为 `20260407-200414`，候选版本为 `20260408-034009`，`candidate_is_newer=true`。
- 当前 live `prod` 仍有 `1` 条运行中任务，`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`；因此本轮未执行 `/api/runtime-upgrade/apply`。
- 当前唯一 active `running` 节点就是本轮保底巡检 `node-sti-20260408-085a854e`，对应 run 为 `arun-20260408-035301-edee73`；它已于 `2026-04-08T03:52:30+08:00` 进入 `running`，截至 `2026-04-08T03:55:33+08:00` 仍在持续输出。
- 上一轮主线 `[持续迭代] workflow` 节点 `node-sti-20260408-72896d73` 已于 `2026-04-08T03:43:36+08:00` 以 `assignment execution timeout after 1200s` 收口失败，但 audit 已自动把主线续挂到 `sch-20260407-20001ab4 -> 2026-04-08T04:14:00+08:00`；主链未断，本轮无需补链。

## 关键真相
- `GET /api/status`：`environment=prod`、`running_task_count=1`、`assignment_running_task_count=1`、`queued_task_count=0`，当前运行节点即 `node-sti-20260408-085a854e`。
- `GET /api/runtime-upgrade/status`：`current_version=20260407-200414`、`candidate_version=20260408-034009`、`running_task_count=1`、`can_upgrade=false`、`request_pending=false`。
- `GET /api/schedules/sch-20260407-20001ab4`：`next_trigger_at=2026-04-08T04:14:00+08:00`，说明主线 future 入口仍在。
- `GET /api/schedules/sch-20260407-5ef5e5c8`：本轮保底巡检 `last_trigger_at=2026-04-08T03:52:00+08:00`、`last_result_status=running`，当前没有新的 future 保底入口，但并不影响“至少保留一条未来可执行主线入口”的门槛。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-035301-edee73/run.json`：当前 run 仍为 `running`，`started_at=2026-04-08T03:52:30+08:00`、`latest_event_at=2026-04-08T03:55:33+08:00`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-032304-9c3f84/run.json` 与 `result.json`：上一轮主线 run 于 `2026-04-08T03:43:36+08:00` 因 `execution_timeout` 失败，`retryable=true`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`：记录了 `aaud-20260408-034404-e01b16` 在上一轮主线失败后自动续挂 `next_trigger_at=2026-04-08T04:14:04+08:00`，以及 `aaud-20260408-035226-d47445` / `aaud-20260408-035304-b14992` 在 `03:52:06~03:52:30+08:00` 创建并派发当前保底巡检节点。
- `.running/control/runtime/prod/logs/events/schedules.jsonl`：记录了 `2026-04-08T03:44:04+08:00` 的 schedule 更新、`2026-04-08T03:52:06+08:00` 的 `trigger_hit` 和 `2026-04-08T03:53:29+08:00` 的 `dispatch_requested`，与 HTTP 真相一致。
- 直接按 `record_state=active` 过滤任务图节点后，当前全局主图是 `1 running / 0 ready`；不存在需要现场补 dispatch 的 live `ready` 节点。

## 证据路径
- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-085a854e.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-72896d73.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-035301-edee73/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-032304-9c3f84/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-032304-9c3f84/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-08.md`

## 下一次建议唤醒时间
- 主线 next：`sch-20260407-20001ab4 -> 2026-04-08T04:14:00+08:00`
- 保底建议：如果 `2026-04-08T04:14:00+08:00` 的主线没有按时建单，或当前保底巡检节点收尾后仍未自动续挂新的保底入口，建议在 `2026-04-08T04:19:00+08:00` 再做一次保底巡检。
- 升级建议：等当前 `node-sti-20260408-085a854e` 收尾，且 `/api/runtime-upgrade/status` 返回 `running_task_count=0` 与 `can_upgrade=true` 后，优先直接 `apply 20260408-034009`。

memory_ref=.codex/memory/2026-04/2026-04-08.md
