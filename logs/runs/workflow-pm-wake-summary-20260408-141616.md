# workflow-pm-wake-summary

## 巡检结论
- 巡检时间：`2026-04-08T14:16:16+08:00`
- `prod` 当前版本：`20260408-131718`
- 升级判断：本轮不升级。`/api/runtime-upgrade/status` 返回 `current=candidate=20260408-131718`、`running_task_count=1`、`can_upgrade=false`；按当前巡检节点排除后复核，`running_task_count=0` 但 `candidate_is_newer=false`、`blocking_reason=no_candidate`、`can_upgrade=false`
- 主链判断：本轮不补链。`[持续迭代] workflow` 仍保留未来入口 `sch-20260407-20001ab4 -> 2026-04-08T14:19:00+08:00`
- 任务图判断：当前 active 图里只有本轮巡检节点 `node-sti-20260408-c9fc3c32=running`，没有 active `ready` 节点需要我接管
- 最近运行上下文：上一轮主线 `node-sti-20260408-5bb210b5` 对应 `run_id=arun-20260408-134215-7980fe` 已在 `2026-04-08T14:02:43+08:00` 因“检测到运行句柄缺失”被收成 `cancelled/failed`

## 关键证据
- `GET /healthz` => `ok=true`
- `GET /api/status` => `running_task_count=1`、`assignment_workboard_summary.running_task_count=1`、`schedule_total=1`、`schedule_workboard_preview[0].next_trigger_at=2026-04-08T14:19:00+08:00`
- `GET /api/runtime-upgrade/status` => `current_version=20260408-131718`、`candidate_version=20260408-131718`、`running_task_count=1`、`can_upgrade=false`
- `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-c9fc3c32` => `running_task_count=0`、`candidate_is_newer=false`、`blocking_reason=no_candidate`、`can_upgrade=false`
- `GET /api/schedules/sch-20260407-20001ab4` => `enabled=true`、`next_trigger_at=2026-04-08T14:19:00+08:00`
- `GET /api/schedules/sch-20260407-5ef5e5c8` => 当前 trigger `sti-20260408-c9fc3c32` 处于 `running`，`future_triggers=[]`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-c9fc3c32.json` => `status=running`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-141214-3a6a98/run.json` => `status=running`、`latest_event_at=2026-04-08T14:15:01+08:00`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-134215-7980fe/run.json` => `status=cancelled`、`latest_event=检测到运行句柄缺失，已自动结束当前批次，后台结果不再回写节点状态。`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl` 与 `.running/control/runtime/prod/logs/events/schedules.jsonl` => `13:42` 主线失败后已在 `14:03:27+08:00` 把下一次主线续挂到 `14:19`

## 风险与备注
- 当前没有更高 candidate，这轮就算把本巡检节点排除掉也不应该 apply；这次阻塞是真 `no_candidate`，不是假 running 空窗
- 近三轮主线 `12:37 / 13:10 / 13:42` 都因“运行句柄缺失或 workflow 已重启”失败，`V1-P0 / V1-P1` 的执行收尾稳定性仍是 live 风险
- 当前主链仍连续，风险不在“没有 future 入口”，而在 `14:19` 这轮能否按时建单并在失败后继续续挂下一次入口

## 下一次建议唤醒时间
- 主线 next: `2026-04-08T14:19:00+08:00`
- 建议保底 next: 如果 `2026-04-08T14:19:00+08:00` 的主线没有按时建单，或没有自动续挂新的 `future/ready` 入口，我建议在 `2026-04-08T14:24:00+08:00` 再做一次保底巡检

memory_ref: `.codex/memory/2026-04/2026-04-08.md`
