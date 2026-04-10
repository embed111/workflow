# workflow-pm-wake-summary

## 巡检结论
- 巡检时间：`2026-04-08T04:44:30+08:00` 至 `2026-04-08T04:48:38+08:00`
- `prod` 当前版本仍为 `20260407-200414`，候选版本为 `20260408-043244`，`candidate_is_newer=true`。
- 截至 `2026-04-08T04:48:38+08:00`，live `prod` 仍有 `1` 条运行中任务，`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`；因此本轮未执行 `/api/runtime-upgrade/apply`。
- 当前唯一 active `running` 节点就是本轮保底巡检 `node-sti-20260408-e1865eaa`，对应 run 为 `arun-20260408-044501-dab356`；`/api/status` 与任务图文件真相一致，当前没有额外 `ready/queued` 节点需要现场补 dispatch。
- 上一轮主线 `[持续迭代] workflow` 节点 `node-sti-20260408-a635881f` 已于 `2026-04-08T04:35:38+08:00` 以 `assignment execution timeout after 1200s` 收口失败，但失败收口已经自动把主线续挂到 `sch-20260407-20001ab4 -> 2026-04-08T05:06:00+08:00`；因此主链未断，本轮无需补链。

## 关键真相
- `GET /api/status`：`environment=prod`、`running_task_count=1`、`assignment_running_task_count=1`、`queued_task_count=0`，当前运行节点即 `node-sti-20260408-e1865eaa`。
- `GET /api/runtime-upgrade/status`：`current_version=20260407-200414`、`candidate_version=20260408-043244`、`running_task_count=1`、`can_upgrade=false`、`request_pending=false`。
- `GET /api/schedules/sch-20260407-20001ab4`：`next_trigger_at=2026-04-08T05:06:00+08:00`，`last_result_status=failed`，`last_result_node_id=node-sti-20260408-a635881f`，说明上一轮主线虽然超时失败，但 future 入口已经续上。
- `GET /api/schedules/sch-20260407-5ef5e5c8`：当前保底巡检 `last_trigger_at=2026-04-08T04:44:00+08:00`、`last_result_status=running`，本 schedule 当前没有新的 future trigger；但 done_definition 要求的是“至少保留一条未来可执行的 workflow 主线入口”，这条门槛已经由 `[持续迭代] workflow` 的 `05:06` future 满足。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-e1865eaa.json`：当前保底节点仍为 `record_state=active`、`status=running`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-044501-dab356/run.json`：当前 run 仍为 `running`，`started_at=2026-04-08T04:44:30+08:00`，`latest_event_at=2026-04-08T04:48:10+08:00`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-a635881f.json`、`run.json` 与 `result.json`：上一轮主线已在 `2026-04-08T04:35:38+08:00` 因 `execution_timeout` 失败，`retryable=true`。
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`：`aaud-20260408-043608-d384ba` 记录了上一轮主线失败后自动续挂 `next_trigger_at=2026-04-08T05:06:08+08:00`；`aaud-20260408-044426-5a7792` 与 `aaud-20260408-044505-d0e17d` 记录了当前保底节点的创建与派发。
- `.running/control/runtime/prod/logs/events/schedules.jsonl`：与 audit/HTTP 真相一致，最近一次主线 schedule 更新在 `2026-04-08T04:36:08+08:00`，当前保底 trigger 命中在 `2026-04-08T04:44:04+08:00`。

## 证据路径
- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-e1865eaa.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-a635881f.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-044501-dab356/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-041505-c691a2/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-041505-c691a2/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-08.md`

## 下一次建议唤醒时间
- 主线 next：`sch-20260407-20001ab4 -> 2026-04-08T05:06:00+08:00`
- 保底建议：如果 `2026-04-08T05:06:00+08:00` 的主线没有按时建单，或当前保底巡检节点收尾后仍没有自动续挂新的保底入口，建议在 `2026-04-08T05:11:00+08:00` 再做一次保底巡检。
- 升级建议：等当前 `node-sti-20260408-e1865eaa` 收尾，且 `/api/runtime-upgrade/status` 返回 `running_task_count=0` 与 `can_upgrade=true` 后，优先直接 `apply 20260408-043244`。

memory_ref=.codex/memory/2026-04/2026-04-08.md
